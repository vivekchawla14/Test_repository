from __future__ import annotations

import logging
import socket
import threading
import time
from collections.abc import Callable

from .exceptions import ConnectionError, ConnectionNotReadyError
from .models import RawPacket
from .states import ConnectionState


PacketCallback = Callable[[RawPacket], None]
ConnectionCallback = Callable[[tuple[str, int]], None]
DisconnectionCallback = Callable[[], None]


class TI990Connection:
    """
    Persistent TCP server for TriboScan.

    TriboScan is the TCP client. This server stays active and automatically
    accepts new TriboScan connections after a disconnect.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        receive_size: int = 4096,
        reconnect_delay: float = 1.0,
    ) -> None:
        if not 0 < port < 65536:
            raise ValueError("Port must be between 1 and 65535.")

        if receive_size <= 0:
            raise ValueError("receive_size must be positive.")

        self.host = host
        self.port = port
        self.receive_size = receive_size
        self.reconnect_delay = reconnect_delay

        self.state = ConnectionState.STOPPED
        self.client_address: tuple[str, int] | None = None

        self._server_socket: socket.socket | None = None
        self._client_socket: socket.socket | None = None
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._socket_lock = threading.Lock()

        self._packet_callbacks: list[PacketCallback] = []
        self._connection_callbacks: list[ConnectionCallback] = []
        self._disconnection_callbacks: list[DisconnectionCallback] = []

        self._logger = logging.getLogger(__name__)

    @property
    def is_connected(self) -> bool:
        return (
            self.state == ConnectionState.CONNECTED
            and self._client_socket is not None
        )

    @property
    def is_running(self) -> bool:
        return (
            self._worker_thread is not None
            and self._worker_thread.is_alive()
        )

    def add_packet_callback(self, callback: PacketCallback) -> None:
        if callback not in self._packet_callbacks:
            self._packet_callbacks.append(callback)

    def add_connection_callback(
        self,
        callback: ConnectionCallback,
    ) -> None:
        if callback not in self._connection_callbacks:
            self._connection_callbacks.append(callback)

    def add_disconnection_callback(
        self,
        callback: DisconnectionCallback,
    ) -> None:
        if callback not in self._disconnection_callbacks:
            self._disconnection_callbacks.append(callback)

    def start(self) -> None:
        """
        Start the persistent host in a background thread.

        This method returns immediately.
        """

        if self.is_running:
            return

        self._stop_event.clear()

        self._worker_thread = threading.Thread(
            target=self._serve_forever,
            name="ti990-connection-server",
            daemon=True,
        )
        self._worker_thread.start()

    def wait_until_connected(
        self,
        timeout: float | None = None,
    ) -> tuple[str, int]:
        """
        Wait until TriboScan connects.

        The persistent server continues running if this times out.
        """

        start_time = time.monotonic()

        while not self._stop_event.is_set():
            if self.is_connected and self.client_address is not None:
                return self.client_address

            if timeout is not None:
                elapsed = time.monotonic() - start_time

                if elapsed >= timeout:
                    raise TimeoutError(
                        "Timed out waiting for TriboScan to connect."
                    )

            time.sleep(0.1)

        raise ConnectionError("The TI 990 connection server was stopped.")

    def send_raw(self, data: bytes) -> None:
        """
        Send already-encoded bytes to TriboScan.

        Do not use this for commands until the packet encoder is verified.
        """

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes.")

        if not data:
            raise ValueError("Cannot send an empty byte string.")

        with self._socket_lock:
            client = self._client_socket

        if client is None or not self.is_connected:
            raise ConnectionNotReadyError(
                "TriboScan is not currently connected."
            )

        try:
            client.sendall(data)

        except OSError as exc:
            self._handle_client_disconnect()

            raise ConnectionError(
                f"Failed to send data to TriboScan: {exc}"
            ) from exc

    def close(self) -> None:
        """
        Stop the server and close all sockets.
        """

        self._stop_event.set()
        self._handle_client_disconnect(notify=False)

        server = self._server_socket

        if server is not None:
            try:
                server.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                server.close()
            except OSError:
                pass

        self._server_socket = None
        self.state = ConnectionState.STOPPED

        thread = self._worker_thread

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=2.0)

        self._worker_thread = None

    def _serve_forever(self) -> None:
        try:
            self._create_server_socket()

            while not self._stop_event.is_set():
                if not self.is_connected:
                    self._accept_client()

                if self.is_connected:
                    self._receive_from_client()

        except Exception:
            self.state = ConnectionState.ERROR
            self._logger.exception("TI 990 server failed.")

        finally:
            self._handle_client_disconnect(notify=False)

            if not self._stop_event.is_set():
                self.state = ConnectionState.ERROR

    def _create_server_socket(self) -> None:
        try:
            server = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server.bind((self.host, self.port))
            server.listen(1)

            # Lets the thread periodically check the stop event.
            server.settimeout(1.0)

            self._server_socket = server
            self.state = ConnectionState.LISTENING

            self._logger.info(
                "TI 990 host listening continuously at %s:%d",
                self.host,
                self.port,
            )

        except OSError as exc:
            raise ConnectionError(
                f"Could not listen at {self.host}:{self.port}: {exc}"
            ) from exc

    def _accept_client(self) -> None:
        server = self._server_socket

        if server is None:
            raise ConnectionError("Server socket is not available.")

        try:
            client, address = server.accept()

        except socket.timeout:
            return

        except OSError as exc:
            if self._stop_event.is_set():
                return

            raise ConnectionError(
                f"Failed while accepting TriboScan: {exc}"
            ) from exc

        # Allows periodic checks even when no packet arrives.
        client.settimeout(1.0)

        with self._socket_lock:
            self._client_socket = client

        self.client_address = address
        self.state = ConnectionState.CONNECTED

        self._logger.info(
            "TriboScan connected from %s:%d",
            address[0],
            address[1],
        )

        for callback in tuple(self._connection_callbacks):
            try:
                callback(address)
            except Exception:
                self._logger.exception(
                    "Connection callback failed."
                )

    def _receive_from_client(self) -> None:
        with self._socket_lock:
            client = self._client_socket

        if client is None:
            return

        try:
            data = client.recv(self.receive_size)

        except socket.timeout:
            return

        except OSError:
            self._handle_client_disconnect()
            time.sleep(self.reconnect_delay)
            return

        if not data:
            self._handle_client_disconnect()
            time.sleep(self.reconnect_delay)
            return

        packet = RawPacket.now(data)

        self._logger.debug(
            "Received %d bytes: %s",
            packet.size,
            packet.hex_string,
        )

        for callback in tuple(self._packet_callbacks):
            try:
                callback(packet)
            except Exception:
                self._logger.exception(
                    "Packet callback failed."
                )

    def _handle_client_disconnect(
        self,
        notify: bool = True,
    ) -> None:
        with self._socket_lock:
            client = self._client_socket
            self._client_socket = None

        was_connected = (
            client is not None
            or self.state == ConnectionState.CONNECTED
        )

        if client is not None:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                client.close()
            except OSError:
                pass

        self.client_address = None

        if not self._stop_event.is_set():
            self.state = ConnectionState.LISTENING

        if was_connected:
            self._logger.info(
                "TriboScan disconnected; waiting for reconnection."
            )

            if notify:
                for callback in tuple(
                    self._disconnection_callbacks
                ):
                    try:
                        callback()
                    except Exception:
                        self._logger.exception(
                            "Disconnection callback failed."
                        )

    def __enter__(self) -> "TI990Connection":
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

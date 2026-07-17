from __future__ import annotations

import logging
import socket
import threading
from collections.abc import Callable

from .exceptions import ConnectionError, ConnectionNotReadyError
from .models import RawPacket
from .states import ConnectionState


PacketCallback = Callable[[RawPacket], None]


class TI990Connection:
    """
    TCP server used by the external Python host.

    TriboScan is the TCP client and connects to this server.
    This class currently receives raw packets without attempting
    to decode the undocumented byte representation of the header.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        receive_size: int = 4096,
        timeout: float | None = None,
    ) -> None:
        if not 0 < port < 65536:
            raise ValueError("Port must be between 1 and 65535.")

        if receive_size <= 0:
            raise ValueError("receive_size must be positive.")

        self.host = host
        self.port = port
        self.receive_size = receive_size
        self.timeout = timeout

        self.state = ConnectionState.STOPPED
        self.client_address: tuple[str, int] | None = None

        self._server_socket: socket.socket | None = None
        self._client_socket: socket.socket | None = None
        self._receive_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._packet_callbacks: list[PacketCallback] = []

        self._logger = logging.getLogger(__name__)

    @property
    def is_connected(self) -> bool:
        return (
            self.state == ConnectionState.CONNECTED
            and self._client_socket is not None
        )

    def add_packet_callback(self, callback: PacketCallback) -> None:
        """
        Register a function that receives each incoming RawPacket.
        """

        if callback not in self._packet_callbacks:
            self._packet_callbacks.append(callback)

    def remove_packet_callback(self, callback: PacketCallback) -> None:
        if callback in self._packet_callbacks:
            self._packet_callbacks.remove(callback)

    def start(self) -> None:
        """
        Bind the TCP server and begin listening.

        This method does not block waiting for TriboScan.
        """

        if self.state in {
            ConnectionState.LISTENING,
            ConnectionState.CONNECTED,
        }:
            return

        self._stop_event.clear()

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(1)

            if self.timeout is not None:
                server.settimeout(self.timeout)

            self._server_socket = server
            self.state = ConnectionState.LISTENING

            self._logger.info(
                "TI 990 host listening at %s:%d",
                self.host,
                self.port,
            )

        except OSError as exc:
            self.state = ConnectionState.ERROR
            self.close()
            raise ConnectionError(
                f"Could not start TI 990 host at "
                f"{self.host}:{self.port}: {exc}"
            ) from exc

    def wait_for_triboscan(self) -> tuple[str, int]:
        """
        Block until TriboScan connects.
        """

        if self._server_socket is None:
            raise ConnectionNotReadyError(
                "Call start() before wait_for_triboscan()."
            )

        if self.is_connected and self.client_address is not None:
            return self.client_address

        try:
            client, address = self._server_socket.accept()

            if self.timeout is not None:
                client.settimeout(self.timeout)

            self._client_socket = client
            self.client_address = address
            self.state = ConnectionState.CONNECTED

            self._logger.info(
                "TriboScan connected from %s:%d",
                address[0],
                address[1],
            )

            return address

        except OSError as exc:
            self.state = ConnectionState.ERROR
            raise ConnectionError(
                f"Failed while waiting for TriboScan: {exc}"
            ) from exc

    def start_receiving(self) -> None:
        """
        Start a background thread that receives raw TriboScan packets.
        """

        if not self.is_connected:
            raise ConnectionNotReadyError(
                "TriboScan must be connected before receiving."
            )

        if self._receive_thread and self._receive_thread.is_alive():
            return

        self._receive_thread = threading.Thread(
            target=self._receive_loop,
            name="ti990-receiver",
            daemon=True,
        )
        self._receive_thread.start()

    def receive_once(self) -> RawPacket:
        """
        Receive one raw TCP chunk synchronously.
        """

        client = self._require_client()

        try:
            data = client.recv(self.receive_size)
        except socket.timeout as exc:
            raise ConnectionError(
                "Timed out while waiting for TriboScan data."
            ) from exc
        except OSError as exc:
            self.state = ConnectionState.ERROR
            raise ConnectionError(
                f"Failed to receive TriboScan data: {exc}"
            ) from exc

        if not data:
            self.state = ConnectionState.DISCONNECTED
            raise ConnectionError("TriboScan disconnected.")

        packet = RawPacket.now(data)
        self._notify_packet_callbacks(packet)

        return packet

    def send_raw(self, data: bytes) -> None:
        """
        Send exact bytes to TriboScan.

        Do not use this for instrument commands until protocol encoding
        has been verified.
        """

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes.")

        if not data:
            raise ValueError("Cannot send an empty byte string.")

        client = self._require_client()

        try:
            client.sendall(data)
        except OSError as exc:
            self.state = ConnectionState.ERROR
            raise ConnectionError(
                f"Failed to send data to TriboScan: {exc}"
            ) from exc

    def close(self) -> None:
        self._stop_event.set()

        for sock in (self._client_socket, self._server_socket):
            if sock is None:
                continue

            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                sock.close()
            except OSError:
                pass

        self._client_socket = None
        self._server_socket = None
        self.client_address = None

        if self.state != ConnectionState.ERROR:
            self.state = ConnectionState.STOPPED

    def _receive_loop(self) -> None:
        while not self._stop_event.is_set() and self.is_connected:
            try:
                packet = self.receive_once()
            except ConnectionError as exc:
                self._logger.warning("%s", exc)
                break

            self._logger.debug(
                "Received %d bytes: %s",
                packet.size,
                packet.hex_string,
            )

    def _notify_packet_callbacks(self, packet: RawPacket) -> None:
        for callback in tuple(self._packet_callbacks):
            try:
                callback(packet)
            except Exception:
                self._logger.exception(
                    "Incoming packet callback failed."
                )

    def _require_client(self) -> socket.socket:
        if not self.is_connected or self._client_socket is None:
            raise ConnectionNotReadyError(
                "There is no active TriboScan connection."
            )

        return self._client_socket

    def __enter__(self) -> "TI990Connection":
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
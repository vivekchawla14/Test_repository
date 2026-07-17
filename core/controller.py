from __future__ import annotations

from .core.connection import TI990Connection
from .core.models import RawPacket
from .core.states import AutomationState


class TI990:
    """
    Top-level interface to the TI 990 automation system.

    Hardware modules and managers will be attached here as they
    are implemented.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> None:
        self.connection = TI990Connection(
            host=host,
            port=port,
        )

        self.automation_state = AutomationState.UNKNOWN
        self.last_raw_packet: RawPacket | None = None

        self.connection.add_packet_callback(
            self._handle_raw_packet
        )

        # These will be added next:
        #
        # self.stage = Stage(self)
        # self.transducer = Transducer(self)
        # self.automation = Automation(self)
        #
        # self.safety = SafetyManager(self)
        # self.status = StatusManager(self)
        # self.data = DataManager(self)
        #
        # self.experiments = ExperimentManager(self)

    @property
    def is_connected(self) -> bool:
        return self.connection.is_connected

    
    
    def start(self) -> None:
        self.connection.start()

        print(
            f"TI 990 host is listening at "
            f"{self.connection.host}:{self.connection.port}"
        )

    def disconnect(self) -> None:
        self.connection.close()

    def _handle_raw_packet(self, packet: RawPacket) -> None:
        self.last_raw_packet = packet

        print()
        print("Received packet from TriboScan")
        print(f"Number of bytes: {packet.size}")
        print(f"Hex: {packet.hex_string}")
        print(f"Text guess: {packet.text_guess!r}")

    def __enter__(self) -> "TI990":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.disconnect()

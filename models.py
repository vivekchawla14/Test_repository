from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .messages import MessageDirection, get_message_name


@dataclass(frozen=True, slots=True)
class RawPacket:
    """
    Uninterpreted bytes received from or sent to TriboScan.

    We intentionally preserve the exact bytes while discovering and
    validating the packet encoding used by TriboScan 12.
    """

    data: bytes
    received_at: datetime

    @classmethod
    def now(cls, data: bytes) -> "RawPacket":
        return cls(
            data=bytes(data),
            received_at=datetime.now(timezone.utc),
        )

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def hex_string(self) -> str:
        return self.data.hex(" ")

    @property
    def text_guess(self) -> str:
        return self.data.decode("utf-8", errors="replace")


@dataclass(frozen=True, slots=True)
class TriboScanMessage:
    """
    Decoded protocol message.

    This model is ready now, but it will only be created after the exact
    byte-level packet format has been verified.
    """

    direction: MessageDirection
    message_id: int
    payload: str
    payload_length: int
    raw_data: bytes

    @property
    def name(self) -> str:
        return get_message_name(self.message_id)

    def __str__(self) -> str:
        return (
            f"TriboScanMessage("
            f"name={self.name}, "
            f"id={self.message_id}, "
            f"direction={self.direction.name}, "
            f"payload={self.payload!r})"
        )
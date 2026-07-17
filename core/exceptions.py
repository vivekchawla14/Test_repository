class TI990Error(Exception):
    """Base exception for the TI 990 automation library."""


class ConnectionError(TI990Error):
    """Raised when the TCP connection cannot be established or maintained."""


class ConnectionNotReadyError(ConnectionError):
    """Raised when an operation requires an active TriboScan connection."""


class ProtocolError(TI990Error):
    """Raised when a TCP message cannot be encoded or decoded safely."""


class IncompletePacketError(ProtocolError):
    """Raised when a complete protocol packet has not yet been received."""


class UnknownMessageError(ProtocolError):
    """Raised when strict parsing encounters an unknown message ID."""


class InvalidStateError(TI990Error):
    """Raised when a command is invalid in the current automation state."""


class SafetyError(TI990Error):
    """Raised when a requested operation fails a safety check."""


class TriboScanReportedError(TI990Error):
    """Raised when TriboScan sends a TS_ERROR message."""

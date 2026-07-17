from enum import IntEnum


class MessageDirection(IntEnum):
    """
    Direction field defined by the TriboScan TCP protocol.

    WRITE = message being written/sent
    READ  = message being read/requested
    """

    WRITE = 1
    READ = 2


class MessageID(IntEnum):
    """
    Message IDs documented in the Bruker Hysitron
    TCP Automation Interface manual.
    """

    # TriboScan -> host
    TS_READY_TO_LOAD_SAMPLE = 1

    # Host -> TriboScan
    HOST_SAMPLE_LOADED = 2
    HOST_HOME_Z_AXIS = 3

    # TriboScan -> host
    TS_BUSY = 4

    # Host -> TriboScan
    HOST_METHOD_ID = 5
    HOST_TRIBOSCAN_PAUSE = 6
    HOST_TRIBOSCAN_RESUME = 7
    HOST_EXIT_AUTOMATION = 8
    HOST_CHANGE_WORKSPACE = 9
    HOST_XY_COORDINATES = 10
    HOST_REQUEST_STATUS = 11

    # TriboScan -> host
    TS_ERROR = 12

    # TriboScan -> host
    TS_JOB_EXECUTION_STATUS = 22
    TS_SAMPLE_APPROACH_STATUS = 23

    # Host -> TriboScan
    HOST_SET_MOVEMENT_SPEED_XY = 24

    # TriboScan -> host
    TS_READY_TO_RUN_METHOD = 26

    # Host -> TriboScan
    HOST_OPERATION_COMPLETED = 27
    HOST_ERROR = 28
    HOST_SET_HEIGHT_OFFSET = 31
    HOST_SET_TRANSDUCER_SLOT = 32
    HOST_IMPORT_POSITIONS = 33


HOST_COMMAND_IDS: frozenset[MessageID] = frozenset(
    {
        MessageID.HOST_SAMPLE_LOADED,
        MessageID.HOST_HOME_Z_AXIS,
        MessageID.HOST_METHOD_ID,
        MessageID.HOST_TRIBOSCAN_PAUSE,
        MessageID.HOST_TRIBOSCAN_RESUME,
        MessageID.HOST_EXIT_AUTOMATION,
        MessageID.HOST_CHANGE_WORKSPACE,
        MessageID.HOST_XY_COORDINATES,
        MessageID.HOST_REQUEST_STATUS,
        MessageID.HOST_SET_MOVEMENT_SPEED_XY,
        MessageID.HOST_OPERATION_COMPLETED,
        MessageID.HOST_ERROR,
        MessageID.HOST_SET_HEIGHT_OFFSET,
        MessageID.HOST_SET_TRANSDUCER_SLOT,
        MessageID.HOST_IMPORT_POSITIONS,
    }
)


TRIBOSCAN_MESSAGE_IDS: frozenset[MessageID] = frozenset(
    {
        MessageID.TS_READY_TO_LOAD_SAMPLE,
        MessageID.TS_BUSY,
        MessageID.TS_ERROR,
        MessageID.TS_JOB_EXECUTION_STATUS,
        MessageID.TS_SAMPLE_APPROACH_STATUS,
        MessageID.TS_READY_TO_RUN_METHOD,
    }
)


def get_message_name(message_id: int) -> str:
    """
    Return the documented name for a message ID.

    Unknown values are preserved rather than raising an exception,
    because TriboScan may emit undocumented or version-specific IDs.
    """

    try:
        return MessageID(message_id).name
    except ValueError:
        return f"UNKNOWN_MESSAGE_{message_id}"

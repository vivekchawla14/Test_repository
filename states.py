from enum import Enum


class ConnectionState(str, Enum):
    STOPPED = "stopped"
    LISTENING = "listening"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class AutomationState(str, Enum):
    """
    TriboScan automation job states documented in the TCP manual.

    UNKNOWN is used until TriboScan reports enough information
    for us to determine its current state.
    """

    UNKNOWN = "unknown"
    MANUAL = "manual"

    INITIAL = "initial"
    LOADING_SAMPLE = "loading_sample"
    SET_ACTIVE_SLOT = "set_active_slot"
    SAMPLE_LOADED = "sample_loaded"
    WAIT_FOR_METHOD = "wait_for_method"
    START_AUTOMATIC_TEST = "start_automatic_test"
    TRIBOSCAN_PAUSED = "triboscan_paused"

    MOVE_STAGES = "move_stages"
    SET_MOVEMENT_SPEED = "set_movement_speed"
    SET_HEIGHT_OFFSET = "set_height_offset"
    HOME_Z_AXIS = "home_z_axis"
    CHANGE_WORKSPACE = "change_workspace"
    IMPORT_POSITIONS = "import_positions"

    ESTOP_TRIGGERED = "estop_triggered"
    EXIT_AUTOMATION = "exit_automation"
    END = "end"
from pywinauto import Desktop
import time

def enforce_window_function(WINDOW_TITLE="InView RunTest-inForce1000"):
    TARGET_X = -8
    TARGET_Y = -8
    TARGET_W = 1936
    TARGET_H = 1056

    desktop = Desktop(backend="win32")

    print(f"Looking for window: {WINDOW_TITLE!r}")

    dlg = desktop.window(title=WINDOW_TITLE)
    dlg.wait("exists enabled visible ready", timeout=5)

    # convert to actual wrapper
    dlg = dlg.wrapper_object()

    print("Found window:", dlg.window_text())
    print("Rectangle before:", dlg.rectangle())

    if dlg.is_minimized():
        dlg.restore()
        time.sleep(0.5)

    dlg.set_focus()
    time.sleep(0.2)

    dlg.move_window(
        x=TARGET_X,
        y=TARGET_Y,
        width=TARGET_W,
        height=TARGET_H,
        repaint=True
    )

    time.sleep(0.5)
    print("Rectangle after:", dlg.rectangle())
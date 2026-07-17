import logging
import time

from ti990 import TI990


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    instrument = TI990(
        host="127.0.0.1",
        port=5000,
    )

    try:
        instrument.connect()

        print()
        print("TI 990 host is running.")
        print("No hardware commands will be sent.")
        print("Press Ctrl+C to stop.")

        while instrument.is_connected:
            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nStopping TI 990 host...")

    finally:
        instrument.disconnect()


if __name__ == "__main__":
    main()
import logging

from ti990 import TI990
from ti990.core.exceptions import ConnectionError


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    instrument = TI990(
        host="127.0.0.1",
        port=5000,
    )

    try:
        instrument.connection.start()

        print("Waiting for TriboScan to connect...")

        address = instrument.connection.wait_for_triboscan()

        print(
            f"Connected successfully: "
            f"{address[0]}:{address[1]}"
        )

        print()
        print("Waiting synchronously for the first TriboScan message...")
        print("Now enter Automated Mode in TriboScan.")

        packet = instrument.connection.receive_once()

        print()
        print("Received packet from TriboScan")
        print(f"Number of bytes: {packet.size}")
        print(f"Hex: {packet.hex_string}")
        print(f"Text guess: {packet.text_guess!r}")

    except ConnectionError as exc:
        print(f"Connection error: {exc}")

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        instrument.disconnect()


if __name__ == "__main__":
    main()

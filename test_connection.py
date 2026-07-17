import socket

HOST = "127.0.0.1"
PORT = 5000

print(f"Starting TCP host at {HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print("Waiting for TriboScan to connect...")

    connection, address = server.accept()

    with connection:
        print(f"Connected successfully: {address}")

        while True:
            data = connection.recv(4096)

            if not data:
                print("TriboScan disconnected.")
                break

            print("Received raw bytes:", data)
            print("Received as hex:", data.hex(" "))
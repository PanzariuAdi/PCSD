import socket
import time
import sys

HOST = "127.0.0.1" 
PORT = 8080 
BUFFER_SIZE = 65000 
ONE_MB_MESSAGE = 1024 * 1024 * b"x"


def create_tcp_client(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print (f"Connected to {HOST}:{PORT}")
        print (f"Size of message in bytes: {sys.getsizeof(message):,}")
        print (f"Size of message in megabytes: {sys.getsizeof(message) / 1048576:.2f}")

        start_time = time.time()
        while message:
            chunk = message[:BUFFER_SIZE]
            message = message[BUFFER_SIZE:]
            s.sendall(chunk)

        end_time = time.time()
        total_time = end_time - start_time;

        print(f"Message sent succesfully !")
        print(f"Time taken : {total_time:.2f} seconds")
        return total_time


def create_udp_client(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print (f"Size of message in bytes: {sys.getsizeof(message):,}")
        print (f"Size of message in megabytes: {sys.getsizeof(message) / 1048576:.2f}")

        start_time = time.time()
        while message:
            chunk = message[:BUFFER_SIZE]
            message = message[BUFFER_SIZE:]
            s.sendto(chunk, (HOST, PORT))

        end_time = time.time()
        total_time = end_time - start_time;

        print(f"Message sent succesfully !")
        print(f"Time taken : {total_time:.2f} seconds")
        return total_time


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print ("You must specify the protocol !")
        sys.exit(0)

    protocol = sys.argv[1]

    if (protocol == "tcp"):
        create_tcp_client(ONE_MB_MESSAGE * 100)
    else:
        create_udp_client(ONE_MB_MESSAGE * 100)

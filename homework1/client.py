import socket
import time
import sys

TCP = 'tcp'
UDP = 'udp'
HOST = "127.0.0.1" 
PORT = 8080 
BUFFER_SIZE = 32768 
ONE_MB_MESSAGE = 1024 * 1024 * b"x"
STOP_AND_WAIT = "stop-and-wait"
STREAMING = "streaming"


def create_client(protocol, message_size, mechanism):
    message = ONE_MB_MESSAGE * int(message_size)

    if (protocol == TCP):
        create_tcp_client(message, mechanism)
    elif (protocol == UDP):
        create_udp_client(message, mechanism)


def create_tcp_client(message, mechanism):
    message_size = len(message) * 1024 * 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print (f"Connected to {HOST}:{PORT}")

        start_time = time.time()
        print (f"Size of message in bytes: {sys.getsizeof(message)}")
        print (f"Size of message in megabytes: {sys.getsizeof(message) / 1048576:.4f}")

        if (mechanism == STOP_AND_WAIT):
            data_sent = 0
            while message and data_sent < message_size:
                chunk = message[:BUFFER_SIZE]
                s.sendall(chunk)

                acknowledge = s.recv(1)
                if (acknowledge == b"1"):
                    data_sent += BUFFER_SIZE
                    message = message[BUFFER_SIZE:]
        elif (mechanism == STREAMING):
            while message:
                chunk = message[:BUFFER_SIZE]
                message = message[BUFFER_SIZE:]
                s.sendall(chunk)

        end_time = time.time()

        print(f"Message sent succesfully !")
        print(f"Time taken : {end_time - start_time:.2f} seconds")


def create_udp_client(message, mechanism):
    message_size = len(message) * 1024 * 1024

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((HOST, PORT))
        print (f"Connected to {HOST}:{PORT}")

        print (f"Size of message in bytes: {sys.getsizeof(message)}")
        print (f"Size of message in megabytes: {sys.getsizeof(message) / 1048576:.2f}")
    
        start_time = time.time()

        if (mechanism == STOP_AND_WAIT):
            data_sent = 0
            while message and data_sent < message_size:
                chunk = message[:BUFFER_SIZE]
                s.sendall(chunk)

                acknowledge = s.recv(1)
                if (acknowledge == b"1"):
                    data_sent += BUFFER_SIZE
                    message = message[BUFFER_SIZE:]
        elif (mechanism == STREAMING):
            while message:
                chunk = message[:BUFFER_SIZE]
                message = message[BUFFER_SIZE:] 
                s.sendall(chunk)
    
        end_time = time.time()
    
        print(f"Message sent succesfully !")
        print(f"Time taken : {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    no_of_arguments = len(sys.argv)

    if (no_of_arguments < 3):
        print ("You must specify the port and the message length in MB !")
        sys.exit(0)

    protocol = sys.argv[1]
    message_size = sys.argv[2]
    mechanism = sys.argv[3]

    if (mechanism == STOP_AND_WAIT):
        PORT = 8080
    elif (mechanism == STREAMING):
        PORT = 8081

    create_client(protocol, message_size, mechanism)

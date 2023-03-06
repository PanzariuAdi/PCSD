import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 8080 
BUFFER_SIZE = 32768 
MAX_CLIENTS = 5
TCP = 'tcp'
UDP = 'udp'
STOP_AND_WAIT = "stop-and-wait"
STREAMING = "streaming"


def create_server(protocol, mechanism):
    if (protocol == TCP):
        create_tcp_server(mechanism)
    elif (protocol == UDP):
        create_udp_server(mechanism);


def create_udp_server(mechanism):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"UDP Server listening on {HOST}:{PORT}")

        nr = 0
        data_received = 0
        if (mechanism == STOP_AND_WAIT):
            while True:
                data, addr = s.recvfrom(BUFFER_SIZE)
                s.sendto(b"1", addr)
                data_received += len(data)
                nr = nr + 1
                print_stats(nr, data, addr, data_received)
        elif (mechanism == STREAMING):
            while True:
                data, addr = s.recvfrom(BUFFER_SIZE)
                nr = nr + 1
                data_received += len(data)
                print_stats(nr, data, addr, data_received)


def create_tcp_server(mechanism):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP server listening on {HOST}:{PORT}")
    
        while True:
            conn, addr = s.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr, mechanism))
            client_thread.start()

            if threading.active_count() >= MAX_CLIENTS:
                print(f"Maximum number of clients reached ({MAX_CLIENTS}), waiting for a client to finish")
                client_thread.join()


def handle_client(conn, addr, mechanism):
    print(f"\nConnected by {addr}")
    data_received = 0

    if (mechanism == STREAMING):
        nr = 0
        while True:
            data = conn.recv(BUFFER_SIZE)

            if not data:
                break

            data_received += len(data)
            nr = nr + 1
            print_stats(nr, data, addr, data_received)
    elif (mechanism == STOP_AND_WAIT):
        nr = 0
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break;
            conn.sendto(b"1", addr)
            data_received += len(data)
            nr = nr + 1
            print_stats(nr, data, addr, data_received)

    conn.close()
    print (f"Connection with {addr} closed !\n")


def print_stats(nr, data, addr, data_received):
    print (f"Message no {nr} received {len(data)} bytes from {addr}")
    print (f"Current amount of data received : {data_received}\n\n")


if __name__ == "__main__":
    no_of_arguments = len(sys.argv)

    if (no_of_arguments < 3):
        print ("You must specify the protocol and the mechanism !")
        sys.exit(0)

    protocol = sys.argv[1]
    mechanism = sys.argv[2]

    if (mechanism == STOP_AND_WAIT):
        PORT = 8080
    elif (mechanism == STREAMING):
        PORT = 8081

    create_server(protocol, mechanism)

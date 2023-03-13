import threading
import socket
import sys


HOST = "127.0.0.1"
PORT = 8080 
BUFFER_SIZE = 65000 
MAX_CLIENTS = 5


def create_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

            if threading.active_count() >= MAX_CLIENTS:
                print(f"Maximum number of clients reached ({MAX_CLIENTS}), waiting for a client to finish")
                client_thread.join()


def create_udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print(f"UDP server listening on {HOST}:{PORT}")

        data_received = 0
        message_number = 0
        addr = ""

        try:
            while True:
                data, addr = s.recvfrom(BUFFER_SIZE)
                data_received += len(data)
                message_number += 1
        except Exception as e:
            print (f"Exception occured while receiving data from {addr}: {e}")



def handle_client(conn, addr):
    print (f"\nConnected by {addr}")
    print ("Receiving data ...\n")

    data_received = 0
    message_number = 0

    try:
        while True:
            data = conn.recv(BUFFER_SIZE) 

            if not data:
                break

            data_received += len(data)
            message_number += 1
    except Exception as e:
        print (f"Exception occured while receiving data from {addr}: {e}")
    finally:
        conn.close()

    print (f"Current amount of data received : {data_received:,}")
    print (f"Number of messages : {message_number:,}")
    print (f"Connection with {addr} closed !")


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print ("You must specify the protocol !")
        sys.exit(0)

    protocol = sys.argv[1]

    if (protocol == "tcp"):
        create_tcp_server()
    else:
        create_udp_server()

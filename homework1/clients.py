import client 
ONE_MB_MESSAGE = 1024 * 1024 * b"x"
MESSAGE = ONE_MB_MESSAGE * 100

def start_client(protocol):
    if (protocol == "tcp"):
        return client.create_tcp_client(MESSAGE)

    return client.create_udp_client(MESSAGE)


if __name__ == "__main__":
    total_time = 0
    for i in range (100):
        total_time += start_client("udp")

    print (f"\nAverage time : {total_time / 100} ")

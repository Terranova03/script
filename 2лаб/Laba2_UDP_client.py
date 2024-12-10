import socket


def udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "Привет, UDP сервер!"
    client_socket.sendto(message.encode(), ('localhost', 65432))

    data, addr = client_socket.recvfrom(1024)
    print(f"Ответ от сервера: {data.decode()}")

    client_socket.close()


if __name__ == "__main__":
    udp_client()

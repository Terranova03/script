import socket


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 65432))

    print("UDP сервер ожидает одного сообщения...")
    data, addr = server_socket.recvfrom(1024)
    print(f"Получено сообщение от {addr}: {data.decode()}")
    
    server_socket.sendto(data, addr)

    print("UDP сервер завершает работу.")
    server_socket.close()


if __name__ == "__main__":
    udp_server()

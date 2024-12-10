import socket


def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 65432))
    server_socket.listen(1)

    print("TCP сервер ожидает подключения...")
    conn, addr = server_socket.accept()
    print(f"Подключен клиент: {addr}")

    data = conn.recv(1024)
    print(f"Получено сообщение: {data.decode()}")

    conn.sendall(data)
    conn.close()


if __name__ == "__main__":
    tcp_server()

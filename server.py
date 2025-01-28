import os
import socket
import threading
from datetime import datetime, timezone

HOST = ''
PORT = 8080
WORKING_DIR = os.path.join(os.getcwd(), 'www')

# Убедимся, что рабочая директория существует
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)
    with open(os.path.join(WORKING_DIR, 'index.html'), 'w') as f:
        f.write("<h1>Добро пожаловать на мой веб-сервер!</h1>")

# Функция для обработки запросов клиента
def handle_client(conn, addr):
    try:
        print(f"Connected by {addr}")
        request = conn.recv(8192).decode()
        print(f"Request:\n{request}")

        # Разбираем запрос
        lines = request.splitlines()
        if not lines:
            return

        # Получаем первую строку запроса ("GET / HTTP/1.1")
        method, path, _ = lines[0].split()

        if method != "GET":
            send_response(conn, 405, "Method Not Allowed", "Метод не поддерживается.")
            return

        # Обрабатываем путь
        if path == "/":
            path = "/index.html"

        filepath = os.path.join(WORKING_DIR, path.lstrip("/"))

        # Проверяем существование файла
        if not os.path.exists(filepath):
            send_response(conn, 404, "Not Found", "Файл не найден.")
            return

        # Отправляем содержимое файла
        with open(filepath, 'rb') as f:
            content = f.read()
        send_response(conn, 200, "OK", content, content_type=get_content_type(filepath))

    except Exception as e:
        print(f"Error handling request from {addr}: {e}")
        send_response(conn, 500, "Internal Server Error", "Ошибка на сервере.")

    finally:
        conn.close()

# Функция для отправки ответа
def send_response(conn, status_code, status_text, body, content_type="text/plain"):
    if isinstance(body, str):
        body = body.encode('utf-8')

    headers = [
        f"HTTP/1.1 {status_code} {status_text}",
        f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        f"Server: SimplePythonServer/0.1",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        ""
    ]
    response = "\r\n".join(headers).encode('utf-8') + body
    conn.sendall(response)

# Функция для определения типа содержимого
def get_content_type(filepath):
    if filepath.endswith(".html"):
        return "text/html"
    elif filepath.endswith(".css"):
        return "text/css"
    elif filepath.endswith(".js"):
        return "application/javascript"
    elif filepath.endswith(".png"):
        return "image/png"
    elif filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server running on port {PORT}...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()

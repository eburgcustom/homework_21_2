from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import os

# Настройки сервера
hostName = "localhost"
serverPort = 8000


class MyServer(BaseHTTPRequestHandler):
    """
    Класс, который отвечает за обработку входящих запросов
    """

    def do_GET(self):
        """Обработка GET-запросов"""
        # Разбираем URL, чтобы извлечь путь без параметров запроса
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            path = "/contacts.html"

        # Безопасно формируем путь к файлу
        file_path = os.path.join(os.getcwd(), path.lstrip('/'))

        # Проверяем, что путь находится внутри текущей директории
        if not os.path.abspath(file_path).startswith(os.getcwd()):
            self.send_error(403, "Forbidden")
            return

        try:
            # Проверяем, что файл существует и это файл, а не директория
            if not os.path.isfile(file_path):
                self.send_error(404, "File Not Found: %s" % path)
                return

            # Открываем и отправляем файл
            with open(file_path, 'rb') as file:
                content = file.read()
                self.send_response(200)

                # Определяем Content-Type в зависимости от расширения файла
                if path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript")
                elif path.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    self.send_header("Content-type", "image/" + path.split('.')[-1])
                else:
                    self.send_header("Content-type", "text/html; charset=utf-8")

                self.end_headers()
                self.wfile.write(content)

        except Exception as e:
            print(f"Error processing {path}: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        """Обработка POST-запросов"""
        if self.path == "/submit_contact":
            try:
                # Получаем длину данных
                content_length = int(self.headers.get('Content-Length', 0))
                # Считываем данные
                post_data = self.rfile.read(content_length).decode('utf-8')
                # Парсим данные формы
                form_data = parse_qs(post_data)

                # Выводим данные в консоль
                print("\nПолучены данные формы:")
                for key, values in form_data.items():
                    print(f"{key}: {values[0]}")

                # Перенаправляем обратно на страницу контактов
                self.send_response(303)
                self.send_header('Location', '/contacts.html')
                self.end_headers()
            except Exception as e:
                print(f"Error processing POST request: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    # Создаем и запускаем сервер
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Сервер запущен по адресу http://%s:%s" % (hostName, serverPort))
    print("Нажмите Ctrl+C для остановки сервера")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Сервер остановлен.")

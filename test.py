from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Получаем строку query параметров из URL
        query_string = urllib.parse.urlparse(self.path).query

        # Парсим параметры из строки запроса
        params = urllib.parse.parse_qs(query_string)

        # Извлекаем значение info_hash из параметров
        if 'info_hash' in params:
            info_hash_encoded = params['info_hash'][0]

            # URL-декодируем строку в байты
            info_hash_bytes = urllib.parse.unquote_to_bytes(info_hash_encoded)

            # Преобразуем байты в строку хэша в hex-формате
            info_hash_hex = info_hash_bytes.hex()

            # Отправляем ответ с декодированным хэшем
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"Decoded info_hash: {info_hash_hex}".encode())
        else:
            # Если параметр info_hash отсутствует, отправляем ошибку
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Missing info_hash parameter")


def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
import mimetypes
import pathlib
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse
from jinja2 import Environment, FileSystemLoader


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("Path:", self.path)
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.__process_POST(self.path, data_dict)

        self.send_response(302)
        self.send_header("Location", self.path)
        self.end_headers()

    def __process_POST(self, path, data_dict):
        if path == "/message":
            self.__save_message(
                username=data_dict.get("username"),
                message=data_dict.get("message", ""),
            )

    def __save_message(self, username, message):
        timestamp = datetime.now().isoformat()
        storage_path = pathlib.Path("storage") / "data.json"

        try:
            with storage_path.open("r", encoding="utf-8") as f:
                storage = json.load(f)
                if not isinstance(storage, dict):
                    storage = {}
        except (FileNotFoundError, json.JSONDecodeError):
            storage = {}

        storage[timestamp] = {"username": username, "message": message}

        storage_path.parent.mkdir(parents=True, exist_ok=True)
        with storage_path.open("w", encoding="utf-8") as f:
            json.dump(storage, f, ensure_ascii=False, indent=2)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        env = Environment(loader=FileSystemLoader("."))

        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            template = env.get_template("read.html")
            try:
                with open("storage/data.json", "r", encoding="utf-8") as f:
                    storage = json.load(f)
                    if not isinstance(storage, dict):
                        storage = {}
            except (FileNotFoundError, json.JSONDecodeError):
                storage = {}

            messages = {}
            for ts, item in storage.items():
                item_copy = dict(item)
                try:
                    dt = datetime.fromisoformat(ts)
                    item_copy["ts_formatted"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    item_copy["ts_formatted"] = ts
                messages[ts] = item_copy

            rendered_page = template.render(messages=messages)
            body = rendered_page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    try:
        port = int(os.getenv("PORT", os.getenv("APP_PORT", "3000")))
    except ValueError:
        port = 3000

    server_address = ("", port)
    http = server_class(server_address, handler_class)
    try:
        print(f"Starting server on port {server_address[1]}")
        http.serve_forever()

    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()

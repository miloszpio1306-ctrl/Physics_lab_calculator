#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serwer HTTP obslugujacy interfejs webowy oraz API kalkulatora laboratoryjnego.
"""

import os
import io
import json
import socket
import zipfile
import mimetypes
import webbrowser
import threading
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

from calculations import compute_multi_targets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


def build_project_zip_bytes():
    """
    Tworzy archiwum ZIP ze wszystkimi plikami projektu.
    Umozliwia pobranie kompletnego kodu projektu z poziomu przegladarki.
    """
    files_to_pack = [
        "main.py",
        "calculations.py",
        "constants.py",
        "server.py",
        "kalkulator_fizyczny_laby.py",
        "index.html",
        "requirements.txt",
        "README.md",
        os.path.join("static", "style.css"),
        os.path.join("static", "app.js"),
    ]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path in files_to_pack:
            abs_path = os.path.join(BASE_DIR, rel_path)
            if os.path.isfile(abs_path):
                with open(abs_path, "rb") as f:
                    zf.writestr(rel_path, f.read())
    buf.seek(0)
    return buf.read()


class LabCalculatorHandler(BaseHTTPRequestHandler):
    """Obsluga zadan HTTP dla kalkulatora fizycznego."""

    def log_message(self, format, *args):
        # Wyciszenie standardowych logow konsoli BaseHTTPRequestHandler
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: str, content_type: str = None):
        if not os.path.isfile(file_path):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            index_path = os.path.join(BASE_DIR, "index.html")
            self._send_file(index_path, "text/html; charset=utf-8")

        elif path.startswith("/static/"):
            rel_file = path[len("/static/"):].lstrip("/")
            safe_path = os.path.abspath(os.path.join(STATIC_DIR, rel_file))
            # Zabezpieczenie przed wyjsciem poza katalog static (directory traversal)
            if safe_path.startswith(os.path.abspath(STATIC_DIR)) and os.path.isfile(safe_path):
                ct, _ = mimetypes.guess_type(safe_path)
                if path.endswith(".css"):
                    ct = "text/css; charset=utf-8"
                elif path.endswith(".js"):
                    ct = "application/javascript; charset=utf-8"
                self._send_file(safe_path, ct)
            else:
                self.send_response(404)
                self.end_headers()

        elif path == "/api/download_zip":
            zip_bytes = build_project_zip_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="kalkulator_fizyczny_v4.zip"')
            self.send_header("Content-Length", str(len(zip_bytes)))
            self.end_headers()
            self.wfile.write(zip_bytes)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8")

        try:
            payload = json.loads(raw_body)
            if parsed.path == "/api/calculate":
                result = compute_multi_targets(payload)
                self._send_json(result, 200)
            else:
                self._send_json({"error": "Nieznany endpoint"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 400)


def find_free_port(start_port: int = 8790) -> int:
    """Znajduje wolny port TCP w zadanym zakresie."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def run_server(port: int = None, open_browser: bool = True):
    """Uruchamia serwer HTTP i opcjonalnie otwiera przegladarke."""
    if port is None:
        port = find_free_port(8790)

    server = HTTPServer(("127.0.0.1", port), LabCalculatorHandler)
    url = f"http://127.0.0.1:{port}"
    print("=================================================================")
    print(f" Kalkulator Laboratoryjny Fizyki v4.0 uruchomiony:")
    print(f" Adres: {url}")
    print(" Aby zamknac serwer, nacisnij Ctrl+C w terminalu.")
    print("=================================================================")

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
        server.server_close()

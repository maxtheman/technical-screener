from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from datetime import datetime
from typing import List
import json
import os
from email.parser import BytesParser
from email.policy import default
import re

# Data models
@dataclass
class Todo:
    id: int
    title: str
    completed: bool
    created_at: str

@dataclass
class Document:
    id: int
    filename: str
    size: int
    uploaded_at: str

# In-memory storage
todos: List[Todo] = [
    Todo(1, "Learn Python", True, "2024-03-20T10:00:00"),
    Todo(2, "Build Web App", False, "2024-03-20T11:00:00")
]

documents: List[Document] = [
    Document(1, "example.txt", 1024, "2024-03-20T10:00:00")
]

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_cors_headers()
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self._serve_index()
        elif self.path == "/api/todos":
            self._handle_todos_get()
        elif self.path == "/api/documents":
            self._handle_documents_get()
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/todos":
            self._handle_todos_post()
        elif self.path == "/api/documents":
            self._handle_documents_post()
        else:
            self._send_error(404, "Not Found")

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _serve_index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
            self.wfile.write(f.read())

    def _handle_todos_get(self):
        self._send_json_response(todos)

    def _handle_documents_get(self):
        self._send_json_response(documents)

    def _handle_todos_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            todo_data = json.loads(post_data)
            if "title" not in todo_data:
                self._send_error(400, "Missing required field: title")
                return
            
            new_todo = Todo(
                id=len(todos) + 1,
                title=todo_data["title"],
                completed=False,
                created_at=datetime.now().isoformat()
            )
            todos.append(new_todo)
            self._send_json_response(new_todo)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON data")

    def _handle_documents_post(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self._send_error(400, "Expected multipart/form-data")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        parser = BytesParser(policy=default)
        message = parser.parsebytes(b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + body)

        file_part = None
        for part in message.iter_parts():
            if part.get_param('name', header='content-disposition') == 'file':
                file_part = part
                break

        if not file_part:
            self._send_error(400, "No file uploaded")
            return

        filename = file_part.get_filename()
        if not filename:
            self._send_error(400, "No filename")
            return

        # Get file content
        file_content = file_part.get_payload(decode=False)
        
        new_doc = Document(
            id=len(documents) + 1,
            filename=filename,
            size=len(file_content),
            uploaded_at=datetime.now().isoformat()
        )
        documents.append(new_doc)
        self._send_json_response(new_doc)

    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        
        # Handle dataclass serialization
        if isinstance(data, list):
            json_data = json.dumps([vars(item) for item in data])
        else:
            json_data = json.dumps(vars(data))
        
        self.wfile.write(json_data.encode())

    def _send_error(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

def run_server(port=8000):
    server = HTTPServer(("", port), RequestHandler)
    print(f"Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server() 
import unittest
import json
import threading
import urllib.request
import urllib.error
from urllib.parse import urlencode
import os
from app import run_server
from http.client import HTTPConnection
import time

class TestWebApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(target=run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        # Give the server a moment to start
        time.sleep(0.1)
        cls.base_url = "http://localhost:8000"
        cls.api_url = f"{cls.base_url}/api"

    def setUp(self):
        # Reset connection before each test
        self.conn = HTTPConnection("localhost", 8000)

    def test_index_page(self):
        """Test that the index page is served correctly"""
        with urllib.request.urlopen(self.base_url) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get('Content-type'), 'text/html')
            content = response.read().decode()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('Technical Screen Demo', content)

    def test_get_todos(self):
        """Test GET /api/todos endpoint"""
        with urllib.request.urlopen(f"{self.api_url}/todos") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read())
            self.assertIsInstance(data, list)
            self.assertTrue(len(data) > 0)
            # Verify todo structure
            todo = data[0]
            self.assertIn('id', todo)
            self.assertIn('title', todo)
            self.assertIn('completed', todo)
            self.assertIn('created_at', todo)

    def test_get_documents(self):
        """Test GET /api/documents endpoint"""
        with urllib.request.urlopen(f"{self.api_url}/documents") as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read())
            self.assertIsInstance(data, list)
            self.assertTrue(len(data) > 0)
            # Verify document structure
            doc = data[0]
            self.assertIn('id', doc)
            self.assertIn('filename', doc)
            self.assertIn('size', doc)
            self.assertIn('uploaded_at', doc)

    def test_create_todo(self):
        """Test POST /api/todos endpoint"""
        data = json.dumps({"title": "Test Todo"}).encode()
        headers = {
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(
            f"{self.api_url}/todos",
            data=data,
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 200)
            new_todo = json.loads(response.read())
            self.assertEqual(new_todo["title"], "Test Todo")
            self.assertFalse(new_todo["completed"])
            self.assertIn("created_at", new_todo)

    def test_upload_document(self):
        """Test POST /api/documents endpoint"""
        # Create a test file
        test_filename = "test_upload.txt"
        test_content = b"Hello, World!"
        
        # Prepare multipart form data
        boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = []
        body.append(b'--' + boundary)
        body.append(b'Content-Disposition: form-data; name="file"; filename="test_upload.txt"')
        body.append(b'Content-Type: text/plain')
        body.append(b'')
        body.append(test_content)
        body.append(b'--' + boundary + b'--')
        body.append(b'')
        body = b'\r\n'.join(body)

        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary.decode()}',
            'Content-Length': str(len(body))
        }

        request = urllib.request.Request(
            f"{self.api_url}/documents",
            data=body,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 200)
            new_doc = json.loads(response.read())
            self.assertEqual(new_doc["filename"], test_filename)
            self.assertEqual(new_doc["size"], len(test_content))
            self.assertIn("uploaded_at", new_doc)

    def test_404_handling(self):
        """Test handling of non-existent endpoints"""
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(f"{self.api_url}/nonexistent")
        self.assertEqual(context.exception.code, 404)

    def test_invalid_todo_data(self):
        """Test handling of invalid todo data"""
        data = json.dumps({"invalid": "data"}).encode()
        headers = {
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(
            f"{self.api_url}/todos",
            data=data,
            headers=headers,
            method="POST"
        )
        
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request)
        self.assertEqual(context.exception.code, 400)
        
        # Also test with invalid JSON
        request = urllib.request.Request(
            f"{self.api_url}/todos",
            data=b'invalid json',
            headers=headers,
            method="POST"
        )
        
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request)
        self.assertEqual(context.exception.code, 400)

    def test_invalid_document_upload(self):
        """Test handling of invalid document upload"""
        # Send request without multipart/form-data
        headers = {
            'Content-Type': 'application/json',
        }
        request = urllib.request.Request(
            f"{self.api_url}/documents",
            data=b'{}',
            headers=headers,
            method="POST"
        )
        
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request)
        self.assertEqual(context.exception.code, 400)

if __name__ == '__main__':
    unittest.main() 
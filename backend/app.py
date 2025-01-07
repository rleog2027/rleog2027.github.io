import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import sqlite3

# Replace DATABASE_URL with your Render PostgreSQL database connection details
DATABASE_URL = "postgresql://<user>:<password>@<host>:<port>/<database>"

class RequestHandler(BaseHTTPRequestHandler):
    # Handle GET requests
    def do_GET(self):
        if self.path == "/profiles":
            self.handle_get_profiles()

    # Handle POST requests
    def do_POST(self):
        if self.path == "/profiles":
            self.handle_create_profile()

    def handle_get_profiles(self):
        try:
            # Connect to the PostgreSQL database
            conn = sqlite3.connect(DATABASE_URL)
            cursor = conn.cursor()

            # Execute SQL query to retrieve all profiles
            cursor.execute("SELECT * FROM profiles")
            rows = cursor.fetchall()

            # Convert rows to JSON
            profiles = [
                {
                    "id": row[0],
                    "fullName": row[1],
                    "email": row[2],
                    "hebrewName": row[3],
                    "status": row[4],
                    "minhag": row[5],
                    "profilePic": row[6],
                }
                for row in rows
            ]

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(profiles).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_create_profile(self):
        try:
            # Read and parse request body
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Connect to the PostgreSQL database
            conn = sqlite3.connect(DATABASE_URL)
            cursor = conn.cursor()

            # Insert profile data into the database
            cursor.execute(
                """
                INSERT INTO profiles (full_name, email, hebrew_name, status, minhag, profile_pic)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    data["fullName"],
                    data["email"],
                    data["hebrewName"],
                    data["status"],
                    data["minhag"],
                    data["profilePic"],
                ),
            )
            conn.commit()

            # Send response
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Profile created successfully"}).encode())
        except Exception as e:
            self.send_error(500, str(e))


def run(server_class=HTTPServer, handler_class=RequestHandler, port=5000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()

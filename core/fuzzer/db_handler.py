import sqlite3
import os
from datetime import datetime


class DatabaseHandler:
    def __init__(self, db_dir, db_name=None):
        self.db_dir = db_dir
        self.curl_file = None
        if db_name is None:  # make new db
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = f'interactions_{timestamp}.db'
            self.curl_file = os.path.join(self.db_dir, f'curls_{timestamp}.txt')

        db_path = os.path.join(self.db_dir, db_name)

        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                payload TEXT,
                url TEXT,
                method TEXT,
                request_headers TEXT,
                request_body TEXT,
                status_code INTEGER,
                response_headers TEXT,
                response_body TEXT
            )
        ''')
        self.conn.commit()

    def save_interaction(self, payload_index, request, response, payload):
        cursor = self.conn.cursor()

        # httpx uses 'content' attribute, requests uses 'body'
        body_data = getattr(request, 'content', None) or getattr(request, 'body', None)

        if body_data is not None:
            if isinstance(body_data, bytes):
                request_body = body_data.decode('utf-8', errors='ignore') if body_data else ''
            elif isinstance(body_data, str):
                request_body = body_data if body_data else ''
            else:
                request_body = str(body_data)
        else:
            request_body = ''

        # httpx.URL is an object, need to convert to string
        url_str = str(request.url)

        cursor.execute('''
            INSERT INTO interactions (id, timestamp, payload, url, method, request_headers, request_body, status_code, response_headers, response_body)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payload_index,
            datetime.now().isoformat(),
            payload,
            url_str,
            request.method,
            str(dict(request.headers)),
            request_body,
            response.status_code,
            str(dict(response.headers)),
            response.text
        ))
        self.conn.commit()
        self.save_curl(payload_index, request, response, payload)

    def save_curl(self, payload_index, request, response, payload):
        if self.curl_file is None:
            return

        url_str = str(request.url)
        method = request.method

        # Build header flags
        header_flags = []
        for key, value in request.headers.items():
            escaped_value = str(value).replace('"', '\\"')
            header_flags.append(f'  -H "{key}: {escaped_value}"')

        # Build body flag
        body_data = getattr(request, 'content', None) or getattr(request, 'body', None)
        body_flag = ""
        if body_data:
            if isinstance(body_data, bytes):
                body_str = body_data.decode('utf-8', errors='ignore')
            elif isinstance(body_data, str):
                body_str = body_data
            else:
                body_str = str(body_data)
            if body_str:
                escaped_body = body_str.replace("'", "'\\''")
                body_flag = f"  -d '{escaped_body}'"

        # Assemble curl command
        parts = [f'curl -k -X {method}']
        parts.extend(header_flags)
        if body_flag:
            parts.append(body_flag)
        parts.append(f'  "{url_str}"')

        curl_cmd = ' \\\n'.join(parts)

        with open(self.curl_file, 'a') as f:
            f.write(f'# Bypass #{payload_index} - {payload}\n')
            f.write(f'# Status: {response.status_code} | Length: {len(response.text)}\n')
            f.write(curl_cmd + '\n\n')
            f.write('# ----------------------------------------\n\n')

    def load_interactions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM interactions')
        return cursor.fetchall()

    def close(self):
        self.conn.close()

    @staticmethod
    def get_latest_db(db_dir):
        db_files = [f for f in os.listdir(db_dir) if f.endswith('.db')]
        if not db_files:
            raise FileNotFoundError("No database files found in the interactions directory.")
        latest_db = max(db_files, key=lambda x: os.path.getctime(os.path.join(db_dir, x)))
        print(f"No db was specified, using the latest db: {latest_db}\n")

        return latest_db

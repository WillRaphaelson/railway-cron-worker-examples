import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/slow':
            time.sleep(11)
        self.send_response(503 if self.path == '/fail' else 200)
        self.end_headers()
    def log_message(self, *args):
        pass

class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
    def run_once(self, path):
        return subprocess.run([sys.executable, 'check_once.py'], cwd=ROOT,
            env={**os.environ, 'TARGET_URL': self.base + path},
            capture_output=True, text=True, timeout=15)
    def test_success_exits_zero(self):
        result = self.run_once('/ok')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Check succeeded: HTTP 200', result.stdout)
    def test_http_failure_exits_one(self):
        result = self.run_once('/fail')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Check failed: HTTP 503', result.stdout)
    def test_slow_response_exits_one(self):
        result = self.run_once('/slow')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Check failed', result.stdout)
    def test_worker_repeats_and_stops(self):
        worker = subprocess.Popen([sys.executable, 'worker.py'], cwd=ROOT,
            env={**os.environ, 'TARGET_URL': self.base + '/ok'},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            time.sleep(61)
            self.assertIsNone(worker.poll())
            worker.terminate()
            output, _ = worker.communicate(timeout=3)
            self.assertEqual(worker.returncode, 0)
            self.assertGreaterEqual(output.count('Check succeeded: HTTP 200'), 2)
            self.assertIn('Worker stopped', output)
        finally:
            if worker.poll() is None:
                worker.kill()
                worker.wait()

if __name__ == '__main__':
    unittest.main()

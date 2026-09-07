import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / '.venv' / 'Scripts' / 'python.exe'
if not PYTHON.exists():
    PYTHON = ROOT / '.venv' / 'bin' / 'python'
if not PYTHON.exists():
    PYTHON = Path(sys.executable)

APP = ROOT / 'app_server.py'
HOST = '127.0.0.1'
PORT = 8000


def server_is_running():
    try:
        with socket.create_connection((HOST, PORT), timeout=1):
            return True
    except OSError:
        return False


def start_app():
    proc = subprocess.Popen([
        str(PYTHON),
        str(APP),
    ], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc


if __name__ == '__main__':
    if server_is_running():
        print(f'Coverse is already running on http://{HOST}:{PORT}')
        raise SystemExit(0)

    proc = start_app()
    print(f'Started Coverse with PID {proc.pid}')
    try:
        while True:
            time.sleep(5)
            if proc.poll() is not None:
                if server_is_running():
                    print('Another Coverse process is already running; stopping watchdog.')
                    break
                print('App exited; restarting...')
                proc = start_app()
                print(f'Restarted Coverse with PID {proc.pid}')
    except KeyboardInterrupt:
        proc.terminate()
        raise

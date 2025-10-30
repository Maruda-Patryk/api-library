#!/bin/sh
set -e

# Default connection details if environment variables are absent
HOST=${POSTGRES_HOST:-db}
PORT=${POSTGRES_PORT:-5432}
TIMEOUT=${POSTGRES_WAIT_TIMEOUT:-60}

echo "Waiting for PostgreSQL at ${HOST}:${PORT} (timeout: ${TIMEOUT}s)..."
python - <<'PY'
import os
import socket
import sys
import time

host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', '5432'))
timeout = float(os.environ.get('POSTGRES_WAIT_TIMEOUT', '60'))

deadline = time.monotonic() + timeout

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        if time.monotonic() >= deadline:
            sys.exit(f"Timed out waiting for PostgreSQL at {host}:{port}")
        time.sleep(1)

print(f"PostgreSQL at {host}:{port} is available")
PY

python manage.py migrate --noinput
exec "$@"

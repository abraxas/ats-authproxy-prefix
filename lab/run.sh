#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ats-authproxy-prefix}"
export PYTHONUNBUFFERED=1

LABEL="ats-authproxy-prefix"
WITNESS="ATS-AUTHPROXY-PREFIX-WITNESS"
IMAGE="ats-10.2.0-lab:local"
LOCK="/tmp/ats-10.2.0-lab.lock"
export ATS_SRC="$(cd ../../client-reviews/trafficserver/src && pwd)"
READY_HOST="origin.lab"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  down
  exit 1
}

ensure_image() {
  echo "== wait/build ${IMAGE} lock=${LOCK} =="
  python3 - <<'PY'
import fcntl
import os
import subprocess
import sys
import time

IMAGE = "ats-10.2.0-lab:local"
LOCK = "/tmp/ats-10.2.0-lab.lock"
SRC = os.environ["ATS_SRC"]


def image_ok() -> bool:
    return (
        subprocess.call(
            ["docker", "image", "inspect", IMAGE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    )


def sibling_build() -> bool:
    proc = subprocess.run(["ps", "ax", "-o", "command="], capture_output=True, text=True, check=False)
    for line in proc.stdout.splitlines():
        if IMAGE in line and "docker" in line.lower() and "inspect" not in line:
            return True
    return False


for attempt in range(1, 181):
    if image_ok():
        print(f"image-present {IMAGE}", flush=True)
        sys.exit(0)
    if sibling_build():
        print(f"wait-sibling-build attempt={attempt}", flush=True)
        time.sleep(10)
        continue
    break

if image_ok():
    print(f"image-present {IMAGE}", flush=True)
    sys.exit(0)

os.makedirs(os.path.dirname(LOCK), exist_ok=True)
with open(LOCK, "a", encoding="utf-8") as handle:
    deadline = time.time() + 2400
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if image_ok():
                print(f"image-present-locked {IMAGE}", flush=True)
                sys.exit(0)
            if time.time() > deadline:
                print("lock-timeout", flush=True)
                sys.exit(2)
            time.sleep(5)
    if image_ok():
        print(f"image-present {IMAGE}", flush=True)
        sys.exit(0)
    print(f"docker-build {IMAGE}", flush=True)
    rc = subprocess.call(["docker", "build", "--pull=false", "-t", IMAGE, "-f", "./Dockerfile", SRC])
    sys.exit(rc)
PY
}

trap down EXIT

echo "== docker compose down (clean) =="
down

if ! ensure_image; then
  fail_setup "ats-image-build-failed"
fi

if ! docker run --rm --user 0 --entrypoint test "${IMAGE}" \
    -f /opt/ats/libexec/trafficserver/authproxy.so; then
  fail_setup "authproxy-so-missing"
fi

if ! docker image inspect python:3.12-slim >/dev/null 2>&1; then
  echo "== docker pull python:3.12-slim =="
  docker pull python:3.12-slim || fail_setup "python-image-pull-failed"
fi

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 8); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d; then
    up_ok=1
    break
  fi
  echo "compose-up-retry attempt=${attempt}"
  sleep 12
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait origin/auth/ats =="
ok=0
for i in $(seq 1 90); do
  if python3 - <<PY
import socket

def ping(host: str, port: int) -> None:
    with socket.create_connection((host, port), 2) as sock:
        sock.settimeout(3)
        sock.close()

ping("127.0.0.1", 18761)
ping("127.0.0.1", 18762)
req = (
    b"GET /ok-ready HTTP/1.1\r\n"
    b"Host: ${READY_HOST}\r\n"
    b"Connection: close\r\n"
    b"\r\n"
)
with socket.create_connection(("127.0.0.1", 18760), 3) as sock:
    sock.settimeout(5)
    sock.sendall(req)
    data = sock.recv(64)
if not data.startswith(b"HTTP/"):
    raise SystemExit(1)
PY
  then
    ok=1
    echo "stack-ready attempt=${i}"
    break
  fi
  echo "stack-wait attempt=${i}"
  sleep 2
done
if [[ "${ok}" != 1 ]]; then
  echo "== compose logs (not ready) =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=160 || true
  fail_setup "stack-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e

if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit=${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"

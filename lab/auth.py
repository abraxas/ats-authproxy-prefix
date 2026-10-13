#!/usr/bin/env python3
"""Auth helper: 200 + X-Auth-User: realuser, or 403 on /deny."""

from __future__ import annotations

import os
import socket
import threading

REALUSER = "realuser"
HOST = os.environ.get("AUTH_HOST", "0.0.0.0")
PORT = int(os.environ.get("AUTH_PORT", "9000"))
HEADER_LIMIT = 32_768


def _recv_headers(conn: socket.socket) -> bytes:
    buf = bytearray()
    while b"\r\n\r\n" not in buf and len(buf) < HEADER_LIMIT:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)


def _path_of(raw: bytes) -> str:
    header_blob, _sep, _rest = raw.partition(b"\r\n\r\n")
    first = header_blob.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
    parts = first.split(" ")
    if len(parts) < 2:
        return "/"
    return parts[1].split("?", 1)[0]


def _respond(conn: socket.socket, status: int, reason: str, extra: list[str]) -> None:
    body = f"{status} {reason}\n".encode("ascii")
    lines = [
        f"HTTP/1.1 {status} {reason}",
        "Content-Type: text/plain",
        f"Content-Length: {len(body)}",
        "Connection: close",
        *extra,
        "",
        "",
    ]
    conn.sendall("\r\n".join(lines).encode("ascii") + body)


def _handle(conn: socket.socket) -> None:
    try:
        raw = _recv_headers(conn)
        if not raw:
            return
        path = _path_of(raw)
        if path.startswith("/deny"):
            _respond(conn, 403, "Forbidden", [])
            return
        _respond(conn, 200, "OK", [f"X-Auth-User: {REALUSER}"])
    except OSError:
        return
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        conn.close()


def main() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(32)
        print(f"auth listen {HOST}:{PORT}", flush=True)
        while True:
            conn, _addr = server.accept()
            conn.settimeout(10)
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Origin that last-wins X-Auth-User and dumps every copy."""

from __future__ import annotations

import os
import socket
import threading
from dataclasses import dataclass, field

WITNESS = "ATS-AUTHPROXY-PREFIX-WITNESS"
REALUSER = "realuser"
ATTACKER = "attacker"
HOST = os.environ.get("ORIGIN_HOST", "0.0.0.0")
PORT = int(os.environ.get("ORIGIN_PORT", "8080"))
RECV_LIMIT = 65_536
HEADER_LIMIT = 32_768


@dataclass
class Hits:
    lock: threading.Lock = field(default_factory=threading.Lock)
    resource: int = 0

    def bump(self) -> int:
        with self.lock:
            self.resource += 1
            return self.resource

    def snapshot(self) -> int:
        with self.lock:
            return self.resource


HITS = Hits()


def _recv_headers(conn: socket.socket) -> bytes:
    buf = bytearray()
    while b"\r\n\r\n" not in buf and len(buf) < HEADER_LIMIT:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) >= RECV_LIMIT:
            break
    return bytes(buf)


def _parse_request(raw: bytes) -> tuple[str, str, list[tuple[str, str]]]:
    header_blob, _sep, _rest = raw.partition(b"\r\n\r\n")
    lines = header_blob.split(b"\r\n")
    if not lines:
        return "", "", []
    request_line = lines[0].decode("latin-1", errors="replace")
    parts = request_line.split(" ")
    method = parts[0] if parts else ""
    path = parts[1] if len(parts) > 1 else "/"
    headers: list[tuple[str, str]] = []
    for line in lines[1:]:
        if b":" not in line:
            continue
        name, _colon, value = line.partition(b":")
        headers.append(
            (
                name.decode("latin-1", errors="replace").strip(),
                value.decode("latin-1", errors="replace").strip(),
            )
        )
    return method, path, headers


def _header_values(headers: list[tuple[str, str]], name: str) -> list[str]:
    want = name.lower()
    return [value for key, value in headers if key.lower() == want]


def _http_response(status: int, reason: str, body: str) -> bytes:
    payload = body.encode("utf-8")
    header = (
        f"HTTP/1.1 {status} {reason}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return header.encode("ascii") + payload


def _identity_body(users: list[str]) -> tuple[int, str, str]:
    last = users[-1] if users else ""
    dump_lines = [
        f"X-Auth-User-Count: {len(users)}",
        f"X-Auth-User-Last: {last}",
        f"X-Auth-User-All: {' | '.join(users)}",
    ]
    for index, value in enumerate(users):
        dump_lines.append(f"X-Auth-User-{index}: {value}")
    leftover = last in {ATTACKER, WITNESS} or WITNESS in last
    if leftover:
        dump_lines.append(f"IDENTITY: {WITNESS}")
        dump_lines.append(WITNESS)
        return 200, "OK", "\n".join(dump_lines) + "\n"
    dump_lines.append(f"IDENTITY: {REALUSER}")
    dump_lines.append("REALUSER-ONLY")
    return 200, "OK", "\n".join(dump_lines) + "\n"


def _handle(conn: socket.socket) -> None:
    try:
        raw = _recv_headers(conn)
        if not raw:
            return
        _method, path, headers = _parse_request(raw)
        path_only = path.split("?", 1)[0]
        if path_only == "/_hits":
            body = f"hits={HITS.snapshot()}\n"
            conn.sendall(_http_response(200, "OK", body))
            return
        HITS.bump()
        users = _header_values(headers, "X-Auth-User")
        status, reason, body = _identity_body(users)
        conn.sendall(_http_response(status, reason, body))
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
        print(f"origin listen {HOST}:{PORT}", flush=True)
        while True:
            conn, _addr = server.accept()
            conn.settimeout(10)
            threading.Thread(target=_handle, args=(conn,), daemon=True).start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

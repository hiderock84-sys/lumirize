#!/usr/bin/env python3
"""Keep one Cloudflare quick tunnel for the local preview.

Account-less trycloudflare hostnames die with Error 1033 the moment their
cloudflared process exits, and that name can never be attached again.
This script therefore refuses to start a second tunnel while an existing
one still serves the site. Quick tunnels also ignore --ha-connections and
stay on a single connector, so replacing a live process only orphans the
URL already sent to someone.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ORIGIN = "http://127.0.0.1:4173/simple/index.html"
LOG_CANDIDATES = (
    Path("/tmp/cf-ha.log"),
    Path("/tmp/cf-preview.log"),
)
HOST_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def live_hosts_from_logs() -> list[str]:
    found: list[str] = []
    for path in LOG_CANDIDATES:
        if not path.is_file():
            continue
        text = path.read_text(errors="replace")
        for host in HOST_RE.findall(text):
            if host not in found:
                found.append(host)
    return found


def serves_site(host: str) -> bool:
    url = host + "/simple/index.html?v=1"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            body = response.read(800).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
    return response.status == 200 and "<title>" in body


def cloudflared_running() -> bool:
    result = subprocess.run(
        ["ps", "-eo", "args"],
        check=False,
        capture_output=True,
        text=True,
    )
    return any(
        "cloudflared" in line and "tunnel" in line and "grep" not in line
        for line in result.stdout.splitlines()
    )


def main() -> int:
    for host in reversed(live_hosts_from_logs()):
        if serves_site(host):
            print(host + "/simple/index.html?v=1")
            return 0
    if cloudflared_running():
        print(
            "cloudflared is running but its public hostname is not serving the site yet.",
            file=sys.stderr,
        )
        return 2
    if not os.environ.get("PREVIEW_TUNNEL_START"):
        print(
            "No healthy tunnel. Refusing to create a new hostname implicitly.",
            file=sys.stderr,
        )
        return 3
    print("start is intentionally not implemented here", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())

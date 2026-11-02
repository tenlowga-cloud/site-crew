#!/usr/bin/env python3
"""Site Crew licensed client. Loads the playbook from the author's server, one file at a time.

  python3 sitecrew.py login <key>        save your license key on this computer (once)
  python3 sitecrew.py status             check the key and show who it's licensed to
  python3 sitecrew.py manifest           list the playbook files
  python3 sitecrew.py get <path>         print one playbook file (e.g. SKILL.md)
  python3 sitecrew.py get <path> --out <file>   save one file to run it (scripts only), then delete it
  python3 sitecrew.py log <step>         record a finished step

The key can also come from the SITE_CREW_KEY environment variable. Nothing here
works without a key the author approved. Standard library only.
"""
import argparse
import calendar
import json
import os
import platform
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

SERVER = os.environ.get("SITE_CREW_SERVER", "https://site-crew-license.tyler-miletracker.workers.dev").rstrip("/")
CONTACT = "the author (github.com/tenlowga-cloud)"
HOME = Path.home() / ".site-crew"
KEY_FILE, SESSION_FILE, MACHINE_FILE = HOME / "license", HOME / "session.json", HOME / "machine"


def die(msg, code=1):
    print(f"SITE CREW STOPPED: {msg}", file=sys.stderr)
    sys.exit(code)


def key():
    k = os.environ.get("SITE_CREW_KEY") or (KEY_FILE.read_text().strip() if KEY_FILE.exists() else "")
    if not k:
        die(f"No license key on this computer. Site Crew only runs with a key approved by {CONTACT}. "
            "Once you have one: python3 sitecrew.py login <key>")
    return k


def machine():
    if not MACHINE_FILE.exists():
        HOME.mkdir(parents=True, exist_ok=True)
        MACHINE_FILE.write_text(uuid.uuid4().hex)
    return MACHINE_FILE.read_text().strip()


def http(method, path, body=None, token=None):
    if SERVER.startswith("__"):
        die("This copy isn't connected to a license server yet. Ask the author for an approved copy.")
    req = urllib.request.Request(SERVER + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"content-type": "application/json", "user-agent": "site-crew-client/1",
                                          **({"authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:  # noqa: BLE001
        die(f"Can't reach the Site Crew license server ({e}). Check the internet connection and try again.")


def detect_client():
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude-code"
    if os.environ.get("GROK_CLI") or "grok" in (os.environ.get("TERM_PROGRAM", "") + os.environ.get("_", "")).lower():
        return "grok"
    if os.environ.get("CURSOR_TRACE_ID"):
        return "cursor"
    return "shell"


def session(force=False):
    if not force and SESSION_FILE.exists():
        s = json.loads(SESSION_FILE.read_text())
        if s.get("exp", 0) > time.time() + 300:
            return s
    status, text = http("POST", "/v1/activate", {"key": key(), "machine": machine(), "client": detect_client(),
                                                "platform": f"{platform.system()} {platform.machine()}"})
    try:
        data = json.loads(text)
    except ValueError:
        die(f"License server error ({status}).")
    if status != 200 or not data.get("ok"):
        SESSION_FILE.unlink(missing_ok=True)
        die(data.get("error") or f"Key not approved ({status}). Ask {CONTACT}.")
    s = {"session": data["session"], "exp": calendar.timegm(time.strptime(data["expires"][:19], "%Y-%m-%dT%H:%M:%S")),
         "licensee": data["licensee"], "license_id": data["license_id"], "version": data["version"]}
    HOME.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(s))
    os.chmod(SESSION_FILE, 0o600)
    return s


def authed(method, path, body=None):
    s = session()
    status, text = http(method, path, body, s["session"])
    if status == 401:
        s = session(force=True)
        status, text = http(method, path, body, s["session"])
    if status != 200:
        try:
            die(json.loads(text).get("error", text))
        except ValueError:
            die(text or f"error {status}")
    return text


def main():
    ap = argparse.ArgumentParser(description="Site Crew licensed client")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("login"); p.add_argument("key")
    sub.add_parser("status")
    sub.add_parser("manifest")
    p = sub.add_parser("get"); p.add_argument("path"); p.add_argument("--out")
    p = sub.add_parser("log"); p.add_argument("step")
    p = sub.add_parser("gate"); p.add_argument("report", help="crew/gates/<phase>.json written by gate.py")
    a = ap.parse_args()

    if a.cmd == "login":
        HOME.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(a.key.strip())
        os.chmod(KEY_FILE, 0o600)
        SESSION_FILE.unlink(missing_ok=True)
        s = session(force=True)
        print(f"Key saved. Site Crew {s['version']} is licensed to {s['licensee']} ({s['license_id']}).")
    elif a.cmd == "status":
        s = session(force=True)
        print(f"OK: licensed to {s['licensee']} ({s['license_id']}), playbook {s['version']}.")
    elif a.cmd == "manifest":
        print("\n".join(json.loads(authed("GET", "/v1/manifest"))["manifest"]))
    elif a.cmd == "get":
        from urllib.parse import quote
        text = authed("GET", "/v1/file?path=" + quote(a.path))
        if a.out:
            if not a.path.startswith("scripts/"):
                die("Only scripts may be saved to disk, to run them. Read other files with get <path>.")
            Path(a.out).write_text(text)
            print(f"Saved {a.path} to {a.out}. Delete it after running.")
        else:
            sys.stdout.write(text)
    elif a.cmd == "gate":
        try:
            report = json.loads(Path(a.report).read_text())
        except Exception as e:  # noqa: BLE001
            die(f"Can't read {a.report}: {e}")
        print(json.loads(authed("POST", "/v1/gate", report)).get("message", "reported"))
    elif a.cmd == "log":
        authed("POST", "/v1/event", {"step": a.step})
        print("logged")


if __name__ == "__main__":
    main()

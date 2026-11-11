#!/usr/bin/env python3
"""Start and monitor one user-requested Coin Bag web-helper BLE attempt."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
import urllib.request

import dbus
import websocket

ADVERTISEMENT = "b6c3089a-7e4f-487d-b9f8-73a281dd718f"
DEFAULT_ROOT = pathlib.Path(os.environ.get("XDG_DATA_HOME", pathlib.Path.home() / ".local/share")) / "pokemon-go-coin-bag"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--port-file", type=pathlib.Path, default=DEFAULT_ROOT / "browser/DevToolsActivePort")
parser.add_argument("--timeout", type=int, default=300)
parser.add_argument("--select-single", action="store_true", help="select only when exactly one filtered phone is offered")
args = parser.parse_args()

port = args.port_file.read_text().splitlines()[0]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5) as response:
    pages = json.load(response)
allowed_origins = (
    "https://na-ji.github.io/pokemon-go-coin-bag/",
    "http://127.0.0.1:",
    "http://localhost:",
)
page = next(
    page for page in pages
    if page.get("type") == "page" and page.get("url", "").startswith(allowed_origins)
)
ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True, timeout=1)
sequence = 0


def send(method: str, params: dict | None = None) -> int:
    global sequence
    sequence += 1
    ws.send(json.dumps({"id": sequence, "method": method, "params": params or {}}))
    return sequence


def command(method: str, params: dict | None = None) -> dict:
    request_id = send(method, params)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            message = json.loads(ws.recv())
        except websocket.WebSocketTimeoutException:
            continue
        if message.get("id") == request_id:
            if "error" in message:
                raise RuntimeError(message["error"])
            return message.get("result", {})
    raise TimeoutError(method)


result = command(
    "Runtime.evaluate",
    {"expression": 'document.querySelector("#thing")?.dataset.state', "returnByValue": True},
)
state = result.get("result", {}).get("value")
if state not in ("ready", "success-pair", "success-exchange", "unconfirmed", "failure"):
    raise SystemExit(f"Helper is already busy ({state}); leaving it untouched.")

command("Runtime.enable")
command("DeviceAccess.enable")
bus = dbus.SystemBus()
objects = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
adapters = [path for path, interfaces in objects.items() if "org.bluez.Adapter1" in interfaces]
if len(adapters) != 1:
    raise SystemExit("Expected exactly one Bluetooth adapter; refusing to guess.")
adapter = dbus.Interface(bus.get_object("org.bluez", adapters[0]), "org.bluez.Adapter1")
adapter.SetDiscoveryFilter(
    dbus.Dictionary(
        {"UUIDs": dbus.Array([ADVERTISEMENT], signature="s"), "Transport": dbus.String("le"),
         "DuplicateData": dbus.Boolean(False)}, signature="sv"
    )
)
adapter.StartDiscovery()
prompt_id = None
selected = False
try:
    send(
        "Runtime.evaluate",
        {"expression": 'document.querySelector("#connect-new, #thing").click()', "userGesture": True},
    )
    print("Receiver waiting for the phone.", flush=True)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        try:
            message = json.loads(ws.recv())
        except websocket.WebSocketTimeoutException:
            continue
        method = message.get("method")
        params = message.get("params", {})
        if method == "DeviceAccess.deviceRequestPrompted":
            prompt_id = params["id"]
            devices = params.get("devices", [])
            print(f"Filtered GO devices offered: {len(devices)}", flush=True)
            if args.select_single and len(devices) == 1 and not selected:
                send("DeviceAccess.selectPrompt", {"id": prompt_id, "deviceId": devices[0]["id"]})
                selected = True
            elif len(devices) > 1:
                raise RuntimeError("Multiple matching phones are present; refusing to guess.")
        elif method == "Runtime.consoleAPICalled":
            values = " ".join(str(item.get("value", item.get("description", ""))) for item in params.get("args", []))
            if values.startswith(("→", "✓", "✗", "Mode:", "Closing BLE", "Thing completed.", "Thing probably failed.")):
                # Stage labels only. Do not emit nonces, IDs, player names, or transaction data.
                print(values[:500], flush=True)
            if values.startswith(("Thing completed.", "Thing probably failed.")):
                break
    status = command(
        "Runtime.evaluate",
        {"expression": 'JSON.stringify({state:document.querySelector("#thing-state")?.textContent,detail:document.querySelector("#thing-detail")?.textContent})',
         "returnByValue": True},
    )
    # Detail can include a trainer name, so report state only.
    raw = status.get("result", {}).get("value", "{}")
    print("Final state:", json.loads(raw).get("state", "unknown"), flush=True)
finally:
    if prompt_id and not selected:
        try:
            command("DeviceAccess.cancelPrompt", {"id": prompt_id})
        except RuntimeError:
            pass
    try:
        adapter.StopDiscovery()
    except dbus.DBusException:
        pass
    ws.close()

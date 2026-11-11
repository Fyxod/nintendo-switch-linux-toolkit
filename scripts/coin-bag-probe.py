#!/usr/bin/env python3
"""Read-only BlueZ probe for a Pokémon GO postcard-search advertisement."""
from __future__ import annotations

import argparse
import time

import dbus

ADVERTISEMENT = "b6c3089a-7e4f-487d-b9f8-73a281dd718f"
PROTOCOL = "291e0889-cb21-4add-a587-3bb494ca2acf"
MODE = "8f860fd8-51e4-497d-afed-94253dbe2e0a"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--timeout", type=int, default=180)
args = parser.parse_args()

bus = dbus.SystemBus()
manager = dbus.Interface(
    bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager"
)
objects = manager.GetManagedObjects()
adapters = [path for path, interfaces in objects.items() if "org.bluez.Adapter1" in interfaces]
if len(adapters) != 1:
    raise SystemExit("Expected exactly one Bluetooth adapter; refusing to guess.")
adapter_path = adapters[0]
adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter1")
device = None
connected_here = False
scanning = False

try:
    adapter.SetDiscoveryFilter(
        dbus.Dictionary(
            {
                "UUIDs": dbus.Array([ADVERTISEMENT], signature="s"),
                "Transport": dbus.String("le"),
                "DuplicateData": dbus.Boolean(False),
            },
            signature="sv",
        )
    )
    adapter.StartDiscovery()
    scanning = True
    print("Waiting for one GO postcard-search advertisement…", flush=True)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        objects = manager.GetManagedObjects()
        candidates = [
            (path, interfaces["org.bluez.Device1"])
            for path, interfaces in objects.items()
            if "org.bluez.Device1" in interfaces
            and ADVERTISEMENT in interfaces["org.bluez.Device1"].get("UUIDs", [])
            and "RSSI" in interfaces["org.bluez.Device1"]
        ]
        if len(candidates) > 1:
            raise RuntimeError("Multiple matching phones are present; refusing to guess.")
        if candidates:
            device_path, properties = candidates[0]
            if properties.get("Connected"):
                raise RuntimeError("A helper already owns this connection; leaving it untouched.")
            break
        time.sleep(0.3)
    else:
        raise TimeoutError("No matching phone advertised before the timeout.")

    adapter.StopDiscovery()
    scanning = False
    device = dbus.Interface(bus.get_object("org.bluez", device_path), "org.bluez.Device1")
    print(f"Connecting; RSSI {int(properties['RSSI'])} dBm", flush=True)
    device.Connect(timeout=35)
    connected_here = True

    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        objects = manager.GetManagedObjects()
        if objects.get(device_path, {}).get("org.bluez.Device1", {}).get("ServicesResolved"):
            break
        time.sleep(0.1)
    else:
        raise TimeoutError("GATT service discovery timed out.")
    time.sleep(1)

    for uuid, label in ((PROTOCOL, "protocol"), (MODE, "mode")):
        matches = [
            (path, interfaces["org.bluez.GattCharacteristic1"])
            for path, interfaces in objects.items()
            if str(path).startswith(str(device_path) + "/")
            and interfaces.get("org.bluez.GattCharacteristic1", {}).get("UUID") == uuid
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {label} characteristic, found {len(matches)}.")
        characteristic_path, characteristic_properties = matches[0]
        characteristic = dbus.Interface(
            bus.get_object("org.bluez", characteristic_path),
            "org.bluez.GattCharacteristic1",
        )
        started = time.monotonic()
        try:
            value = characteristic.ReadValue(
                dbus.Dictionary({"offset": dbus.UInt16(0)}, signature="sv"), timeout=40
            )
        except dbus.DBusException as error:
            elapsed = time.monotonic() - started
            print(f"{label} read failed after {elapsed:.1f}s: {error.get_dbus_name()}: {error.get_dbus_message()}")
            raise
        print(
            f"{label} read succeeded: {len(bytes(value))} byte(s) "
            f"(MTU {characteristic_properties.get('MTU', 'unknown')})",
            flush=True,
        )
    print("Read-only probe succeeded; no pairing or postcard data was written.", flush=True)
finally:
    if scanning:
        try:
            adapter.StopDiscovery()
        except dbus.DBusException:
            pass
    if connected_here and device is not None:
        try:
            device.Disconnect()
        except dbus.DBusException:
            pass

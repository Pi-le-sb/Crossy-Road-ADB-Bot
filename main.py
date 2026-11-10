#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time

import cv2
import numpy as np

import config


def adb_cmd(*args):
    cmd = ["adb"]
    if config.ADB_DEVICE_ID:
        cmd += ["-s", config.ADB_DEVICE_ID]
    return cmd + list(args)


def run(*args, timeout=10):
    try:
        return subprocess.run(adb_cmd(*args), capture_output=True, timeout=timeout)
    except FileNotFoundError:
        print("FEHLER: adb nicht gefunden. Platform-Tools in den PATH aufnehmen.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        return None


def check_adb():
    r = run("devices")
    if r is None:
        return False
    lines = r.stdout.decode(errors="ignore").splitlines()[1:]
    return any(l.strip().endswith("device") for l in lines)


def get_screen_size():
    r = run("shell", "wm", "size")
    if r is not None:
        out = r.stdout.decode(errors="ignore")
        if "size:" in out:
            w, h = out.strip().splitlines()[-1].split(":")[1].strip().split("x")
            return int(w), int(h)
    return None


def screenshot():
    r = run("exec-out", "screencap", "-p", timeout=15)
    if r is None or r.returncode != 0 or not r.stdout:
        return None
    return cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)


def tap(x, y):
    run("shell", "input", "tap", str(int(x)), str(int(y)))


def swipe(x1, y1, x2, y2, ms=60):
    run("shell", "input", "swipe", str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(ms))


def test_adb():
    if not check_adb():
        print("Kein Geraet gefunden. USB-Debugging an? 'adb devices' pruefen.")
        return False
    print("Geraet verbunden, Bildschirm:", get_screen_size())
    return True


def test_screen():
    if not check_adb():
        print("Kein Geraet gefunden.")
        return False
    img = screenshot()
    if img is None:
        print("Screenshot fehlgeschlagen.")
        return False
    h, w = img.shape[:2]
    cv2.imwrite("test_screenshot.png", img)
    x, y = config.GAME_AREA_X, config.GAME_AREA_Y
    cv2.rectangle(img, (x, y), (x + config.GAME_AREA_WIDTH, y + config.GAME_AREA_HEIGHT), (0, 255, 0), 4)
    cv2.imwrite("test_screenshot_area.png", img)
    print(f"OK: Screenshot {w}x{h} gespeichert.")
    print("test_screenshot.png = Original, test_screenshot_area.png = mit Spielbereich (gruen).")
    return True


def play():
    if not test_adb():
        return
    size = get_screen_size()
    if size:
        cx, cy = size[0] // 2, size[1] // 2
    else:
        cx = config.GAME_AREA_X + config.GAME_AREA_WIDTH // 2
        cy = config.GAME_AREA_Y + config.GAME_AREA_HEIGHT // 2
    input("Crossy Road oeffnen, Spiel starten, dann Enter. Abbruch mit Strg+C.")
    n = 0
    try:
        while True:
            tap(cx, cy)
            n += 1
            print(f"Schritt {n}")
            time.sleep(config.DELAY_BETWEEN_MOVES)
    except KeyboardInterrupt:
        print(f"Gestoppt nach {n} Schritten.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test-adb", action="store_true")
    p.add_argument("--test-screen", action="store_true")
    p.add_argument("--device", "-d")
    a = p.parse_args()
    if a.device:
        config.ADB_DEVICE_ID = a.device
    if a.test_adb:
        test_adb()
    elif a.test_screen:
        test_screen()
    else:
        play()


if __name__ == "__main__":
    main()

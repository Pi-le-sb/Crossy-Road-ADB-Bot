#!/usr/bin/env python3
"""
Crossy Road ADB Bot - Funktionierende Version
Einfach, getestet, ohne Komplikationen
"""

import subprocess
import time
import cv2
import numpy as np
import argparse
import config


def run_adb(command):
    """ADB-Befehl ausführen"""
    device_flag = f"-s {config.ADB_DEVICE_ID}" if config.ADB_DEVICE_ID else ""
    full_cmd = f"adb {device_flag} {command}"
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)


def check_adb():
    """ADB-Verbindung prüfen"""
    stdout, stderr = run_adb("devices")
    if "device" in stdout and len([l for l in stdout.split("\n")[1:] if l.strip() and "device" in l]) > 0:
        return True
    return False


def get_screen_size():
    """Bildschirmgröße ermitteln"""
    stdout, _ = run_adb("shell wm size")
    if "Physical size" in stdout:
        size_str = stdout.split(":")[1].strip()
        w, h = map(int, size_str.split("x"))
        return w, h
    return 1080, 1920


def tap(x, y):
    """Auf Bildschirm tippen"""
    run_adb(f"shell input tap {int(x)} {int(y)}")


def screenshot():
    """Screenshot machen und als numpy array zurückgeben"""
    run_adb("shell screencap -p /sdcard/crossy_bot.png")
    run_adb("pull /sdcard/crossy_bot.png /tmp/crossy_bot.png")
    img = cv2.imread("/tmp/crossy_bot.png")
    return img


def test_adb():
    """ADB-Test"""
    print("🔌 Teste ADB...")
    if not check_adb():
        print("❌ Kein Gerät gefunden!")
        print("\nTipps:")
        print("  1. USB-Debugging aktivieren")
        print("  2. Gerät anschließen")
        print("  3. 'adb devices' prüfen")
        return False
    
    w, h = get_screen_size()
    print(f"✓ Gerät verbunden: {w}x{h} Pixel")
    return True


def test_screen():
    """Screenshot-Test"""
    print("📸 Teste Screenshot...")
    
    if not check_adb():
        print("❌ Kein Gerät!")
        return False
    
    img = screenshot()
    if img is not None:
        cv2.imwrite("test_screenshot.png", img)
        print(f"✓ Screenshot: {img.shape}")
        print("  Gespeichert als test_screenshot.png")
        print(f"\nSpielbereich: X={config.GAME_AREA_X}, Y={config.GAME_AREA_Y}")
        print(f"              W={config.GAME_AREA_WIDTH}, H={config.GAME_AREA_HEIGHT}")
        return True
    else:
        print("❌ Screenshot fehlgeschlagen!")
        return False


def detect_player(screenshot):
    """Spieler-Position erkennen (einfache Farberkennung)"""
    if screenshot is None:
        return None, None
    
    # ROI für Spielbereich
    roi = screenshot[config.GAME_AREA_Y:config.GAME_AREA_Y+config.GAME_AREA_HEIGHT,
                    config.GAME_AREA_X:config.GAME_AREA_X+config.GAME_AREA_WIDTH]
    
    if roi is None or roi.size == 0:
        return None, None
    
    # HSV konvertieren
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Weiß/gelb für Spieler (Huhn)
    lower = np.array([0, 0, 200])
    upper = np.array([20, 50, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Konturen
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None
    
    # Größte Kontur
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    
    if w < 20 or h < 20:
        return None, None
    
    # Grid-Position (10x10 Grid angenommen)
    grid_x = int((x + w//2) / (config.GAME_AREA_WIDTH / 10))
    grid_y = int((y + h//2) / (config.GAME_AREA_HEIGHT / 10))
    
    return grid_x, grid_y


def decide_move(player_x, player_y):
    """Einfache AI-Entscheidung"""
    # Vorwärts ist gut!
    return "up"


def play():
    """Hauptspielschleife"""
    print("\n🐔 Starte Crossy Road Bot...")
    print(f"  Spielbereich: {config.GAME_AREA_X},{config.GAME_AREA_Y} +{config.GAME_AREA_WIDTH}x{config.GAME_AREA_HEIGHT}")
    
    if not check_adb():
        print("❌ Kein Gerät!")
        return
    
    print("\n⚠️  Crossy Road muss geöffnet sein!")
    input("Drücke Enter zum Starten...")
    
    score = 0
    moves = 0
    
    try:
        while True:
            # Screenshot
            img = screenshot()
            if img is None:
                print("⚠️  Screenshot-Fehler!")
                time.sleep(1)
                continue
            
            # Spieler erkennen
            px, py = detect_player(img)
            if px is not None:
                print(f"  Spieler: {px},{py}")
            
            # Bewegung
            move = decide_move(px, py)
            
            # Tap-Position
            cx = config.GAME_AREA_X + config.GAME_AREA_WIDTH // 2
            cy = config.GAME_AREA_Y + config.GAME_AREA_HEIGHT // 2
            offset = min(config.GAME_AREA_WIDTH, config.GAME_AREA_HEIGHT) // 6
            
            if move == "up":
                tap(cx, cy - offset)
                score += 1
                print(f"  ↑ UP (Score: {score})")
            
            moves += 1
            time.sleep(config.DELAY_BETWEEN_MOVES)
            
            if moves % 20 == 0:
                print(f"\n📊 Status: Score={score}, Züge={moves}\n")
                
    except KeyboardInterrupt:
        print(f"\n\n🛑 Gestoppt! Score: {score}, Züge: {moves}")


def main():
    parser = argparse.ArgumentParser(description="Crossy Road ADB Bot")
    parser.add_argument("--test-adb", action="store_true", help="ADB-Test")
    parser.add_argument("--test-screen", action="store_true", help="Screenshot-Test")
    parser.add_argument("--device", "-d", help="ADB Device ID")
    args = parser.parse_args()
    
    if args.device:
        config.ADB_DEVICE_ID = args.device
    
    if args.test_adb:
        test_adb()
    elif args.test_screen:
        test_screen()
    else:
        play()


if __name__ == "__main__":
    main()

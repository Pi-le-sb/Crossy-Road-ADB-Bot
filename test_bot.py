#!/usr/bin/env python3
"""
Test-Skript für Crossy Road ADB Bot
Überprüft alle Komponenten auf Funktionalität
"""

import sys
import time


def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_success(text):
    print(f"✓ {text}")


def print_error(text):
    print(f"✗ {text}")


def print_warning(text):
    print(f"⚠️  {text}")


def test_python_version():
    """Testet Python-Version"""
    print_header("Test 1: Python-Version")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success("Python-Version ist kompatibel (3.8+)")
        return True
    else:
        print_error("Python 3.8 oder höher erforderlich!")
        return False


def test_dependencies():
    """Testet Python-Abhängigkeiten"""
    print_header("Test 2: Python-Abhängigkeiten")
    
    required = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("Pillow", "PIL"),
    ]
    
    all_ok = True
    
    for package, import_name in required:
        try:
            __import__(import_name)
            print_success(f"{package} installiert")
        except ImportError:
            print_error(f"{package} NICHT installiert!")
            print(f"  Installation: pip install {package}")
            all_ok = False
    
    # Optionale Pakete
    try:
        import ultralytics
        print_success("ultralytics (YOLOv8) installiert (optional)")
    except ImportError:
        print_warning("ultralytics nicht installiert (optional, für YOLOv8)")
    
    try:
        import torch
        print_success("torch (PyTorch) installiert (optional)")
    except ImportError:
        print_warning("torch nicht installiert (optional, für ML)")
    
    return all_ok


def test_adb():
    """Testet ADB"""
    print_header("Test 3: ADB")
    
    import subprocess
    
    # ADB verfügbar?
    try:
        result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success("ADB installiert")
            print(f"  {result.stdout.split(chr(10))[0]}")
        else:
            print_error("ADB nicht verfügbar!")
            print("  Installation: siehe SETUP.md")
            return False
    except FileNotFoundError:
        print_error("ADB nicht gefunden!")
        print("  Ist ADB im PATH?")
        return False
    except subprocess.TimeoutExpired:
        print_error("ADB-Timeout - ADB hängt möglicherweise")
        return False
    
    # Geräte verbunden?
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
    devices = [l for l in result.stdout.split("\n")[1:] if l.strip() and "device" in l]
    
    if devices:
        print_success(f"{len(devices)} Gerät(e) verbunden")
        for device in devices:
            device_id = device.split()[0]
            print(f"  - {device_id}")
        return True
    else:
        print_error("Keine Geräte verbunden!")
        print("  1. USB-Debugging aktivieren")
        print("  2. Gerät anschließen")
        print("  3. 'adb devices' prüfen")
        return False


def test_adb_commands(device_id=None):
    """Testet ADB-Befehle am Gerät"""
    print_header("Test 4: ADB-Befehle")
    
    import subprocess
    
    device_flag = ["-s", device_id] if device_id else []
    
    # Bildschirmgröße
    try:
        result = subprocess.run(
            ["adb"] + device_flag + ["shell", "wm", "size"],
            capture_output=True, text=True, timeout=5
        )
        if "Physical size" in result.stdout:
            size = result.stdout.split(":")[1].strip()
            print_success(f"Bildschirmgröße: {size}")
        else:
            print_error("Konnte Bildschirmgröße nicht ermitteln")
    except Exception as e:
        print_error(f"Fehler: {e}")
    
    # Screenshot testen
    try:
        result = subprocess.run(
            ["adb"] + device_flag + ["shell", "screencap", "-p", "/sdcard/test.png"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print_success("Screenshot-Befehl erfolgreich")
        else:
            print_error("Screenshot fehlgeschlagen")
    except Exception as e:
        print_error(f"Screenshot-Fehler: {e}")
    
    # Input-Befehl testen
    try:
        result = subprocess.run(
            ["adb"] + device_flag + ["shell", "input", "tap", "100", "100"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print_success("Input-Befehl erfolgreich")
        else:
            print_error("Input-Befehl fehlgeschlagen")
    except Exception as e:
        print_error(f"Input-Fehler: {e}")


def test_src_modules():
    """Testet die src-Module"""
    print_header("Test 5: src-Module")
    
    modules = [
        "src.adb_controller",
        "src.screen_capture",
        "src.cv_detector",
        "src.ai_agent",
    ]
    
    all_ok = True
    
    for module_name in modules:
        try:
            __import__(module_name)
            print_success(f"{module_name} importierbar")
        except ImportError as e:
            print_error(f"{module_name} NICHT importierbar!")
            print(f"  Fehler: {e}")
            all_ok = False
    
    return all_ok


def test_config():
    """Testet die Konfiguration"""
    print_header("Test 6: Konfiguration")
    
    import config
    
    print(f"Spielbereich: {config.GAME_AREA_X},{config.GAME_AREA_Y} +{config.GAME_AREA_WIDTH}x{config.GAME_AREA_HEIGHT}")
    print(f"Grid: {config.GRID_COLUMNS}x{config.GRID_ROWS} Zellen")
    print(f"Computer Vision: {'Ja' if config.USE_CV else 'Nein'}")
    print(f"Machine Learning: {'Ja' if config.USE_ML else 'Nein'}")
    print(f"Verzögerung: {config.DELAY_BETWEEN_MOVES}s")
    
    # Plausibilitätsprüfung
    if config.GAME_AREA_WIDTH <= 0 or config.GAME_AREA_HEIGHT <= 0:
        print_error("Ungültige Spielbereichs-Größe!")
        return False
    
    if config.GAME_AREA_X < 0 or config.GAME_AREA_Y < 0:
        print_warning("Spielbereich startet außerhalb des Bildschirms?")
    
    print_success("Konfiguration sieht gültig aus")
    return True


def test_full_integration(device_id=None):
    """Vollständiger Integrationstest"""
    print_header("Test 7: Vollständiger Integrationstest")
    
    from src.adb_controller import ADBController
    from src.screen_capture import ScreenCapture
    from src.cv_detector import CVDetector
    
    # ADB Controller
    adb = ADBController(device_id)
    if not adb.check_connection():
        print_error("ADB-Verbindung fehlgeschlagen")
        return False
    
    print_success("ADB Controller initialisiert")
    
    # Screen Capture
    capture = ScreenCapture(adb)
    screenshot = capture.capture()
    
    if screenshot is not None:
        print_success(f"Screenshot erfolgreich: {screenshot.shape}")
    else:
        print_error("Screenshot fehlgeschlagen")
        return False
    
    # CV Detector
    detector = CVDetector()
    analysis = detector.analyze_frame(screenshot)
    
    print_success("CV-Analyse durchgeführt")
    print(f"  Spieler-Position: {analysis['player_position']}")
    print(f"  Hindernisse: {len(analysis['obstacles'])}")
    print(f"  Sichere Zellen: {len(analysis['safe_cells'])}")
    
    return True


def main():
    print("\n" + "🧪 " + "="*56)
    print("  Crossy Road ADB Bot - Test-Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Python
    results.append(("Python", test_python_version()))
    
    # Test 2: Dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test 3: ADB
    results.append(("ADB", test_adb()))
    
    # Test 4: ADB Commands (nur wenn ADB ok)
    if results[2][1]:
        test_adb_commands()
    
    # Test 5: src-Module
    results.append(("src-Module", test_src_modules()))
    
    # Test 6: Config
    results.append(("Config", test_config()))
    
    # Test 7: Integration (nur wenn alles andere ok)
    if all(r[1] for r in results):
        results.append(("Integration", test_full_integration()))
    
    # Zusammenfassung
    print_header("Zusammenfassung")
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✓ Bestanden" if ok else "✗ Fehlgeschlagen"
        print(f"  {name}: {status}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 Alle Tests erfolgreich! Der Bot ist bereit.")
        print("\nNächste Schritte:")
        print("  1. Crossy Road auf dem Gerät öffnen")
        print("  2. python main.py ausführen")
        print("  3. Enter drücken und zuschauen!")
    else:
        print("\n⚠️  Einige Tests fehlgeschlagen.")
        print("  Siehe SETUP.md für Fehlerbehebung.")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test-Suite für Crossy Road ADB Bot")
    parser.add_argument("--device", "-d", help="ADB Device ID")
    args = parser.parse_args()
    
    main()

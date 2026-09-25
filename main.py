#!/usr/bin/env python3
"""
Crossy Road ADB Bot - Hauptprogramm
Startet den Bot und koordiniert alle Komponenten
"""

import argparse
import time
import sys
from src.adb_controller import ADBController
from src.screen_capture import ScreenCapture
from src.cv_detector import CVDetector
from src.ai_agent import AIAgent
import config


def test_adb():
    """Testet die ADB-Verbindung"""
    print("🔌 Teste ADB-Verbindung...")
    adb = ADBController()
    
    if not adb.check_connection():
        print("❌ Kein Gerät gefunden!")
        print("\nTipps:")
        print("  1. USB-Debugging aktivieren")
        print("  2. Gerät per USB anschließen")
        print("  3. 'adb devices' in der Kommandozeile prüfen")
        return False
    
    width, height = adb.get_screen_size()
    print(f"✓ Gerät verbunden: {width}x{height} Pixel")
    return True


def test_screen():
    """Testet die Bildschirmaufnahme"""
    print("📸 Teste Bildschirmaufnahme...")
    adb = ADBController()
    
    if not adb.check_connection():
        print("❌ Kein Gerät gefunden!")
        return False
    
    capture = ScreenCapture(adb)
    screenshot = capture.capture()
    
    if screenshot is not None:
        print(f"✓ Screenshot erfolgreich: {screenshot.shape}")
        print("  Screenshot wurde unter 'test_screenshot.png' gespeichert")
        return True
    else:
        print("❌ Screenshot fehlgeschlagen!")
        return False


def run_bot():
    """Hauptspielschleife"""
    print("🐔 Starte Crossy Road Bot...")
    print(f"  Konfiguration: CV={config.USE_CV}, ML={config.USE_ML}")
    
    # Komponenten initialisieren
    adb = ADBController()
    
    if not adb.check_connection():
        print("❌ Kein Gerät gefunden!")
        return
    
    capture = ScreenCapture(adb)
    detector = CVDetector() if config.USE_CV else None
    agent = AIAgent(adb, detector)
    
    # Spielbereich anzeigen
    print(f"\n📐 Spielbereich:")
    print(f"   Position: ({config.GAME_AREA_X}, {config.GAME_AREA_Y})")
    print(f"   Größe: {config.GAME_AREA_WIDTH}x{config.GAME_AREA_HEIGHT}")
    
    # Bestätigung vor Start
    print("\n⚠️  Stelle sicher, dass:")
    print("   1. Crossy Road geöffnet ist")
    print("   2. Das Spiel im Hauptbildschirm ist (nicht Menü)")
    print("   3. Der Spieler bereit ist zu starten")
    
    input("\nDrücke Enter zum Starten (oder Strg+C zum Abbrechen)...")
    
    # Bot starten
    try:
        agent.play_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot gestoppt")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Crossy Road ADB Bot - Spiele Crossy Road automatisch"
    )
    parser.add_argument(
        "--device", "-d",
        help="ADB Device ID (standard: erstes verbundenes Gerät)"
    )
    parser.add_argument(
        "--test-adb",
        action="store_true",
        help="Nur ADB-Verbindung testen"
    )
    parser.add_argument(
        "--test-screen",
        action="store_true",
        help="Nur Bildschirmaufnahme testen"
    )
    parser.add_argument(
        "--config", "-c",
        action="store_true",
        help="Konfigurations-Assistent starten"
    )
    
    args = parser.parse_args()
    
    # Device ID setzen falls angegeben
    if args.device:
        import config
        config.ADB_DEVICE_ID = args.device
    
    # Tests ausführen
    if args.test_adb:
        test_adb()
        return
    
    if args.test_screen:
        test_screen()
        return
    
    if args.config:
        print("🔧 Konfigurations-Assistent:")
        print("\nÖffne config.py und passe folgende Werte an:")
        print("  - GAME_AREA_X, GAME_AREA_Y: Oben-links Ecke des Spielbereichs")
        print("  - GAME_AREA_WIDTH, GAME_AREA_HEIGHT: Größe des Spielbereichs")
        print("\nTipp: Mache einen Screenshot und messe die Koordinaten ab.")
        return
    
    # Normaler Bot-Modus
    run_bot()


if __name__ == "__main__":
    main()

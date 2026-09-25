# 🐔 Crossy Road ADB Bot

Ein funktionierender Bot der Crossy Road auf Android-Geräten spielt.

## 🚀 Quickstart (3 Schritte)

```bash
# 1. Dependencies
pip install opencv-python numpy pillow

# 2. ADB testen
python main.py --test-adb

# 3. Spielen!
python main.py
```

## 📋 Voraussetzungen

- Python 3.8+
- ADB installiert (`sudo apt install android-tools-adb` oder https://developer.android.com/studio/releases/platform-tools)
- Android-Gerät mit USB-Debugging
- Crossy Road App installiert

## 🎮 Verwendung

```bash
# ADB-Test
python main.py --test-adb

# Screenshot-Test (prüft Spielbereich)
python main.py --test-screen

# Bot starten
python main.py

# Mit Gerät
python main.py --device YOUR_DEVICE_ID
```

## ⚙️ Konfiguration

In `config.py` anpassen:

```python
GAME_AREA_X = 100      # Spielbereich X
GAME_AREA_Y = 300      # Spielbereich Y  
GAME_AREA_WIDTH = 800  # Breite
GAME_AREA_HEIGHT = 600 # Höhe
```

## 🔧 Fehlerbehebung

### "adb: command not found"
ADB installieren und zum PATH hinzufügen

### "no devices"
- USB-Debugging aktivieren
- Gerät anschließen
- `adb devices` prüfen

### Bot spielt nicht richtig
`--test-screen` ausführen und Spielbereich in `config.py` anpassen

## 📄 Lizenz

MIT License

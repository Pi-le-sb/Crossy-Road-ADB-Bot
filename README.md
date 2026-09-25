# 🐔 Crossy Road ADB Bot

Ein KI-Bot, der **Crossy Road auf echten Android-Geräten** über ADB spielt.

## 🎯 Features

- **ADB-Steuerung**: Tippt und swiped auf deinem Android-Gerät
- **Bildschirmaufnahme**: Macht Screenshots via ADB für die Analyse
- **Computer Vision**: Erkennt Spieler, Hindernisse und sichere Pfade
- **AI-Entscheidung**: Wählt optimale Bewegungen (regelbasiert oder ML)
- **Einfache Einrichtung**: Läuft auf Windows, macOS und Linux

## 📋 Voraussetzungen

- Python 3.8+
- ADB (Android Debug Bridge) installiert
- Android-Gerät mit USB-Debugging
- Crossy Road App installiert

## 🚀 Installation

### 1. ADB installieren

**Ubuntu/Debian:**
```bash
sudo apt install android-tools-adb
```

**macOS:**
```bash
brew install android-platform-tools
```

**Windows:**
- Download von [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- ZIP entpacken und `adb.exe` zum PATH hinzufügen

### 2. Python-Abhängigkeiten

```bash
pip install -r requirements.txt
```

### 3. Gerät vorbereiten

1. **Entwickleroptionen aktivieren**: 7x auf "Build-Nummer" in den Einstellungen tippen
2. **USB-Debugging aktivieren**: Einstellungen → Entwickleroptionen → USB-Debugging
3. **Gerät verbinden**: Per USB anschließen
4. **Verbindung prüfen**:
   ```bash
   adb devices
   ```
   Du solltest dein Gerät in der Liste sehen.

### 4. Crossy Road installieren

Installiere das Spiel aus dem Play Store oder als APK.

## 🎮 Verwendung

### Grundlegende Nutzung

```bash
python main.py
```

### Mit spezifischem Gerät

```bash
python main.py --device YOUR_DEVICE_ID
```

### Nur Bildschirm-Test

```bash
python main.py --test-screen
```

### Nur ADB-Test

```bash
python main.py --test-adb
```

## ⚙️ Konfiguration

Die wichtigsten Einstellungen in `config.py`:

```python
# Spielbereich auf dem Bildschirm
GAME_AREA_X = 100      # X-Startposition
GAME_AREA_Y = 300      # Y-Startposition
GAME_AREA_WIDTH = 800  # Breite des Spielbereichs
GAME_AREA_HEIGHT = 600 # Höhe des Spielbereichs

# KI-Einstellungen
USE_CV = True          # Computer Vision verwenden
USE_ML = False         # Machine Learning verwenden
DELAY_BETWEEN_MOVES = 0.3  # Sekunden zwischen Zügen
```

## 📁 Projektstruktur

```
Crossy-Road-ADB-Bot/
├── main.py              # Hauptprogramm
├── config.py            # Konfiguration
├── requirements.txt     # Python-Abhängigkeiten
├── src/
│   ├── __init__.py
│   ├── adb_controller.py    # ADB-Steuerung
│   ├── screen_capture.py    # Bildschirmaufnahme
│   ├── cv_detector.py       # Computer Vision
│   └── ai_agent.py          # KI-Entscheidungen
├── assets/
│   └── templates/           # Template-Bilder für CV
└── logs/                    # Log-Dateien
```

## 🔧 Fehlerbehebung

### "adb: command not found"
- ADB ist nicht im PATH. Füge den ADB-Ordner zum PATH hinzu.

### "no devices/emulators found"
- USB-Debugging ist nicht aktiviert
- Gerät ist nicht richtig verbunden
- USB-Treiber fehlen (Windows)

### Bot spielt nicht richtig
- Passe `GAME_AREA_*` Werte in `config.py` an
- Führe `--test-screen` aus, um die Koordinaten zu prüfen

### Screen Capture zu langsam
- Verwende `scrcpy` für schnelleres Screen-Streaming (optional)

## 🤝 Beitrag

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue eröffnen.

## 📄 Lizenz

MIT License

## 🙏 Danksagung

- Inspiriert von [alwyntan/Crossy-Road-AI](https://github.com/alwyntan/Crossy-Road-AI)
- ADB-Referenz: [AmroAbdoh/Crossy-Road](https://github.com/AmroAbdoh/Crossy-Road)

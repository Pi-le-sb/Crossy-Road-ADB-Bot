# 🛠️ Vollständige Setup-Anleitung

Diese Anleitung führt dich Schritt für Schritt durch die Installation und Konfiguration.

## Schritt 1: Repository klonen

```bash
git clone https://github.com/Pi-le-sb/Crossy-Road-ADB-Bot.git
cd Crossy-Road-ADB-Bot
```

## Schritt 2: Python installieren

### Windows
1. Python von https://python.org herunterladen
2. Installer ausführen und "Add Python to PATH" aktivieren

### macOS
```bash
brew install python3
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

## Schritt 3: ADB installieren

### Windows
1. [Platform Tools](https://developer.android.com/studio/releases/platform-tools) herunterladen
2. ZIP entpacken (z.B. nach `C:\platform-tools`)
3. PowerShell als Administrator öffnen:
   ```powershell
   setx PATH "%PATH%;C:\platform-tools"
   ```
4. Neues Terminal öffnen und `adb version` testen

### macOS
```bash
brew install android-platform-tools
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install android-tools-adb
```

## Schritt 4: Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Fehlerbehebung:**

### "pip: command not found"
- Python ist nicht im PATH. Installiere Python neu oder füge es manuell hinzu.

### "Permission denied" (Linux/macOS)
```bash
pip install --user -r requirements.txt
```

## Schritt 5: Android-Gerät vorbereiten

### Entwickleroptionen aktivieren

1. Einstellungen → "Über das Telefon"
2. 7x auf "Build-Nummer" tippen
3. Zurück zu Einstellungen → "Entwickleroptionen"

### USB-Debugging aktivieren

1. Entwickleroptionen öffnen
2. "USB-Debugging" aktivieren
3. Bestätigen

### Gerät verbinden

1. Per USB anschließen
2. Auf dem Gerät "USB-Debugging zulassen" bestätigen
3. Im Terminal testen:
   ```bash
   adb devices
   ```
   
   Erwartete Ausgabe:
   ```
   List of devices attached
   ABC123XYZ    device
   ```

### Fehlerbehebung

#### "no devices/emulators found"
- USB-Kabel prüfen (manche Kabel sind nur zum Laden)
- USB-Debugging aktivieren
- Gerät neu verbinden
- Windows: ADB-Treiber installieren (Google USB Driver)

#### "unauthorized"
- Auf dem Gerät erscheint ein Popup "USB-Debugging zulassen?"
- "Immer zulassen" + "OK" tippen

#### Gerät wird nicht erkannt (Windows)
1. Geräte-Manager öffnen
2. Nach "Android" oder "ADB" suchen
3. Rechtsklick → Treiber aktualisieren
4. [Google USB Driver](https://developer.android.com/studio/run/win-usb) installieren

## Schritt 6: Crossy Road installieren

### Option A: Play Store
1. Play Store auf dem Gerät öffnen
2. "Crossy Road" suchen
3. Installieren

### Option B: APK
1. APK von vertrauenswürdiger Quelle herunterladen
2. Auf Gerät installieren ("Unbekannte Quellen" erlauben)

## Schritt 7: Bot konfigurieren

### Spielbereich anpassen

1. Bot im Test-Modus starten:
   ```bash
   python main.py --test-screen
   ```

2. `test_screenshot.png` öffnen

3. Koordinaten des Spielbereichs messen:
   - Öffne das Bild in Paint, GIMP oder einem anderen Editor
   - Fahre mit der Maus in die obere linke Ecke des Spielbereichs
   - Notiere die X,Y-Koordinaten
   - Fahre in die untere rechte Ecke
   - Berechne: Breite = X2 - X1, Höhe = Y2 - Y1

4. `config.py` bearbeiten:
   ```python
   GAME_AREA_X = 100      # Dein gemessener X-Wert
   GAME_AREA_Y = 300      # Dein gemessener Y-Wert
   GAME_AREA_WIDTH = 800  # Deine gemessene Breite
   GAME_AREA_HEIGHT = 600 # Deine gemessene Höhe
   ```

### CV-Templates erstellen (optional, aber empfohlen)

1. `test_screenshot.png` öffnen
2. Spieler (Huhn) ausschneiden:
   - Ca. 30x30 Pixel um das Huhn
   - Speichern als `assets/templates/player.png`

3. Wiederhole für andere Objekte (Autos, Bäume, Wasser)

## Schritt 8: Bot testen

### ADB-Test
```bash
python main.py --test-adb
```

Erwartete Ausgabe:
```
🔌 Teste ADB-Verbindung...
✓ Gerät verbunden: 1080x2340 Pixel
```

### Screenshot-Test
```bash
python main.py --test-screen
```

Erwartete Ausgabe:
```
📸 Teste Bildschirmaufnahme...
✓ Screenshot erfolgreich: (2340, 1080, 3)
  Screenshot wurde unter 'test_screenshot.png' gespeichert
```

### Bot-Test

1. Crossy Road auf dem Gerät öffnen
2. Zum Hauptbildschirm navigieren (Spieler ist sichtbar)
3. Bot starten:
   ```bash
   python main.py
   ```

4. Enter drücken zum Starten

Der Bot sollte jetzt automatisch tippen und den Spieler bewegen!

## Schritt 9: Optimierung

### Bot ist zu langsam

In `config.py`:
```python
DELAY_BETWEEN_MOVES = 0.2  # Von 0.3 auf 0.2 reduzieren
```

### Bot macht schlechte Entscheidungen

1. CV-Templates verbessern
2. Template-Schwellenwert anpassen:
   ```python
   TEMPLATE_THRESHOLD = 0.8  # Höher = strengere Erkennung
   ```

### Screenshot dauert zu lange

- Verwende `scrcpy` für schnelleres Screen-Streaming
- Oder reduziere die Screenshot-Qualität

## Häufige Probleme

### Bot tippt an der falschen Stelle

- `GAME_AREA_*` Werte in `config.py` überprüfen
- Gerät hat andere Auflösung als erwartet

### CV erkennt nichts

- Templates sind falsch (falsche Größe, schlechte Qualität)
- `TEMPLATE_THRESHOLD` zu hoch (auf 0.5 testen)
- CV komplett deaktivieren zum Testen: `USE_CV = False`

### ADB-Befehle funktionieren nicht

- `adb kill-server` + `adb start-server`
- USB-Kabel wechseln
- Gerät neu starten

## Nächste Schritte

- Templates für bessere Erkennung erstellen
- Eigene AI-Logik in `src/ai_agent.py` implementieren
- YOLOv8-Modell trainieren für robustere Erkennung

Viel Erfolg! 🎮🐔

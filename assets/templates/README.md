# Template-Bilder für Computer Vision

Dieser Ordner enthält Template-Bilder für das Template Matching.

## Erforderliche Templates

Für die beste Erkennung solltest du folgende Templates aus Screenshots extrahieren:

### player.png
- Ein Screenshot-Ausschnitt des Spielers (Huhn/Fuchs/etc.)
- Größe: ca. 30x30 Pixel
- Tipp: Mache einen Screenshot und schneide das Huhn aus

### car_red.png, car_blue.png, etc.
- Verschiedene Auto-Farben
- Größe: ca. 40x20 Pixel

### tree.png
- Baum-Template
- Größe: ca. 30x40 Pixel

### water.png
- Wasser-Template (optional, wird auch via Farbe erkannt)
- Größe: ca. 50x50 Pixel

## Template erstellen

1. Starte den Bot mit `--test-screen`
2. Öffne `test_screenshot.png` in einem Bildbearbeitungsprogramm
3. Schneide die gewünschten Objekte aus
4. Speichere sie in diesem Ordner

## Alternative: YOLOv8

Für bessere Erkennung kannst du ein YOLOv8-Modell trainieren:

1. Mache viele Screenshots in verschiedenen Spielsituationen
2. Label die Objekte mit einem Tool wie LabelImg
3. Trainiere YOLOv8 mit den gelabelten Daten
4. Speichere das Modell als `assets/models/yolov8_crossy.pt`

## Template Matching vs. YOLOv8

| Methode | Vorteile | Nachteile |
|---------|----------|----------|
| Template Matching | Einfach, schnell | Nur exakte Übereinstimmungen |
| YOLOv8 | Robust, erkennt viele Varianten | Benötigt Training, langsamer |

Für den Start reicht Template Matching mit 2-3 Templates.

#!/usr/bin/env python3
"""
Crossy Road ADB Bot - Konfiguration
Passe hier die Einstellungen an dein Gerät und Spiel an
"""

# =============================================================================
# ADB-Einstellungen
# =============================================================================

# Device ID (optional, None = erstes verbundenes Gerät)
# Finde die ID mit: adb devices
ADB_DEVICE_ID = None

# =============================================================================
# Spielbereich auf dem Bildschirm
# =============================================================================
# Diese Werte müssen an dein Gerät und die Crossy Road Fensterposition angepasst werden!

# Oben-links Ecke des Spielbereichs (in Pixeln)
GAME_AREA_X = 100
GAME_AREA_Y = 300

# Größe des Spielbereichs (in Pixeln)
GAME_AREA_WIDTH = 800
GAME_AREA_HEIGHT = 600

# =============================================================================
# Grid-Einstellungen (für die Spielanalyse)
# =============================================================================

# Anzahl der Grid-Zellen im Spielbereich
# Crossy Road hat typischerweise ~10 Spalten und ~10 Reihen im sichtbaren Bereich
GRID_COLUMNS = 10
GRID_ROWS = 10

# Daraus berechnet sich die Größe einer Zelle:
# GRID_CELL_WIDTH = GAME_AREA_WIDTH / GRID_COLUMNS
# GRID_CELL_HEIGHT = GAME_AREA_HEIGHT / GRID_ROWS

# =============================================================================
# Computer Vision Einstellungen
# =============================================================================

# Computer Vision verwenden (erkennt Spieler und Hindernisse)
USE_CV = True

# CV-Modell-Einstellungen
CV_CONFIDENCE_THRESHOLD = 0.6  # Mindest-Konfidenz für Objekterkennung
CV_MODEL_PATH = "assets/models/yolov8_crossy.pt"  # YOLOv8 Modell (optional)

# Template Matching (Alternative zu YOLO)
USE_TEMPLATE_MATCHING = True
TEMPLATE_THRESHOLD = 0.7  # Ähnlichkeitsschwelle für Template Matching

# =============================================================================
# AI-Einstellungen
# =============================================================================

# Machine Learning verwenden (DQN-Agent statt regelbasierter AI)
USE_ML = False

# Regelbasierte AI Einstellungen
AI_PLAY_SAFE = True  # Vorsichtiges Spiel (wartet bei Unsicherheit)
AI_MAX_WAIT_TIME = 3.0  # Maximale Wartezeit in Sekunden

# DQN-Agent Einstellungen (falls USE_ML=True)
ML_MODEL_PATH = "assets/models/dqn_crossy.pth"
ML_TRAIN = False  # True = Training-Modus, False = Inferenz-Modus
ML_EPSILON = 0.1  # Exploration-Rate (0.0 = nur bekannte Züge)

# =============================================================================
# Timing-Einstellungen
# =============================================================================

# Verzögerung zwischen Zügen (in Sekunden)
DELAY_BETWEEN_MOVES = 0.3

# Timeout für Screenshot-Aufnahme (in Sekunden)
SCREENSHOT_TIMEOUT = 5.0

# Timeout für ADB-Befehle (in Sekunden)
ADB_TIMEOUT = 3.0

# =============================================================================
# Logging und Debugging
# =============================================================================

# Log-Level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Logs speichern
SAVE_LOGS = True
LOG_DIR = "logs"

# Screenshots speichern (für Debugging)
SAVE_SCREENSHOTS = False
SCREENSHOT_DIR = "screenshots"

# =============================================================================
# Hilfsfunktionen
# =============================================================================

def get_grid_cell_size():
    """Berechnet die Größe einer Grid-Zelle"""
    cell_width = GAME_AREA_WIDTH / GRID_COLUMNS
    cell_height = GAME_AREA_HEIGHT / GRID_ROWS
    return cell_width, cell_height


def get_grid_center(grid_x, grid_y):
    """Berechnet die Bildschirmkoordinaten für die Mitte einer Grid-Zelle"""
    cell_width, cell_height = get_grid_cell_size()
    
    screen_x = GAME_AREA_X + int(grid_x * cell_width + cell_width / 2)
    screen_y = GAME_AREA_Y + int(grid_y * cell_height + cell_height / 2)
    
    return screen_x, screen_y


def print_config():
    """Gibt die aktuelle Konfiguration aus"""
    print("\n" + "="*60)
    print("Crossy Road ADB Bot - Konfiguration")
    print("="*60)
    print(f"ADB Device: {ADB_DEVICE_ID or 'Auto-detect'}")
    print(f"Spielbereich: {GAME_AREA_X},{GAME_AREA_Y} +{GAME_AREA_WIDTH}x{GAME_AREA_HEIGHT}")
    print(f"Grid: {GRID_COLUMNS}x{GRID_ROWS} Zellen")
    print(f"Computer Vision: {'Ja' if USE_CV else 'Nein'}")
    print(f"Machine Learning: {'Ja' if USE_ML else 'Nein'}")
    print(f"Verzögerung: {DELAY_BETWEEN_MOVES}s")
    print("="*60 + "\n")


# Konfiguration beim Import anzeigen
if __name__ == "__main__":
    print_config()

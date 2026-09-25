#!/usr/bin/env python3
"""
AI Agent - Entscheidet die nächsten Züge
"""

import time
import random
import config
from .adb_controller import ADBController
from .screen_capture import ScreenCapture
from .cv_detector import CVDetector


class AIAgent:
    """KI-Agent für Crossy Road Entscheidungen"""
    
    def __init__(self, adb_controller, cv_detector=None):
        """
        Initialisiert den AI-Agent
        
        Args:
            adb_controller: ADBController-Instanz
            cv_detector: CVDetector-Instanz (optional)
        """
        self.adb = adb_controller
        self.capture = ScreenCapture(adb_controller)
        self.detector = cv_detector or CVDetector() if config.USE_CV else None
        
        # Spielzustand
        self.player_x = 5  # Startposition (Mitte)
        self.player_y = 5  # Unten
        self.score = 0
        self.is_alive = True
        
        # Grid-Informationen
        self.cell_width, self.cell_height = config.get_grid_cell_size()
    
    def decide_move(self, screenshot):
        """
        Entscheidet die nächste Bewegung
        
        Args:
            screenshot: Aktueller Screenshot
            
        Returns:
            "up", "left", "right" oder None (warten)
        """
        if config.USE_ML:
            return self._decide_ml(screenshot)
        else:
            return self._decide_rules(screenshot)
    
    def _decide_rules(self, screenshot):
        """
        Regelbasierte Entscheidung (einfache Heuristik)
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Bewegungsrichtung oder None
        """
        # Wenn CV aktiv ist, verwende echte Erkennung
        if self.detector:
            analysis = self.detector.analyze_frame(screenshot)
            
            if analysis["player_position"]:
                self.player_x, self.player_y = analysis["player_position"]
            
            obstacles = analysis["obstacles"]
            safe_cells = analysis["safe_cells"]
            
            # Prüfe ob vor uns sicher ist
            if self._is_safe(self.player_x, self.player_y + 1, obstacles):
                return "up"
            
            # Seitlich ausweichen
            if not self._is_safe(self.player_x, self.player_y, obstacles):
                if self._is_safe(self.player_x - 1, self.player_y, obstacles):
                    return "left"
                if self._is_safe(self.player_x + 1, self.player_y, obstacles):
                    return "right"
            
            # Warten
            if config.AI_PLAY_SAFE:
                return None
            else:
                # Trotzdem vorwärts versuchen
                return "up"
        
        else:
            # Ohne CV: Einfache zufällige Bewegung
            # (In Produktion sollte CV immer aktiv sein!)
            moves = ["up", "left", "right"]
            return random.choice(moves)
    
    def _decide_ml(self, screenshot):
        """
        ML-basierte Entscheidung (DQN-Agent)
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Bewegungsrichtung oder None
        """
        # Platzhalter für ML-Implementierung
        # Hier würde ein trainiertes PyTorch-Modell geladen werden
        
        # Fallback auf regelbasierte Entscheidung
        return self._decide_rules(screenshot)
    
    def _is_safe(self, grid_x, grid_y, obstacles):
        """
        Prüft ob eine Zelle sicher ist
        
        Args:
            grid_x, grid_y: Grid-Position
            obstacles: Liste von Hindernissen
            
        Returns:
            True wenn sicher, False sonst
        """
        # Außerhalb des Grid?
        if grid_x < 0 or grid_x >= config.GRID_COLUMNS:
            return False
        if grid_y < 0 or grid_y >= config.GRID_ROWS:
            return False
        
        # Kollision mit Hindernis?
        for obs_x, obs_y, obs_type in obstacles:
            if grid_x == obs_x and grid_y == obs_y:
                return False
            # Bei Wasser: auch benachbarte Zellen unsicher
            if obs_type == "water" and abs(grid_y - obs_y) <= 1:
                return False
        
        return True
    
    def execute_move(self, direction):
        """
        Führt eine Bewegung aus
        
        Args:
            direction: "up", "down", "left", "right" oder None
        """
        if direction is None:
            time.sleep(0.5)
            return
        
        # Tap-Position berechnen
        # Wir tippen in die Richtung, in die wir wollen
        center_x = config.GAME_AREA_X + config.GAME_AREA_WIDTH // 2
        center_y = config.GAME_AREA_Y + config.GAME_AREA_HEIGHT // 2
        
        offset = min(self.cell_width, self.cell_height) // 2
        
        taps = {
            "up": (center_x, center_y - offset),
            "down": (center_x, center_y + offset),
            "left": (center_x - offset, center_y),
            "right": (center_x + offset, center_y)
        }
        
        x, y = taps[direction]
        self.adb.tap(x, y)
        
        # Position aktualisieren
        if direction == "up":
            self.player_y += 1
            self.score += 1
        elif direction == "down":
            self.player_y -= 1
        elif direction == "left":
            self.player_x -= 1
        elif direction == "right":
            self.player_x += 1
        
        print(f"  → {direction} (Pos: {self.player_x},{self.player_y}, Score: {self.score})")
    
    def play_loop(self):
        """
        Hauptspielschleife
        """
        print("\n🎮 Bot läuft... (Strg+C zum Stoppen)")
        print(f"  Startposition: {self.player_x},{self.player_y}")
        print(f"  Verzögerung: {config.DELAY_BETWEEN_MOVES}s\n")
        
        move_count = 0
        wait_count = 0
        max_wait = int(config.AI_MAX_WAIT_TIME / config.DELAY_BETWEEN_MOVES)
        
        while self.is_alive:
            try:
                # Screenshot machen
                screenshot = self.capture.capture_game_area()
                
                if screenshot is None:
                    print("⚠️  Screenshot fehlgeschlagen, warte...")
                    time.sleep(1)
                    continue
                
                # Entscheidung treffen
                move = self.decide_move(screenshot)
                
                # Bewegung ausführen
                if move:
                    self.execute_move(move)
                    wait_count = 0
                else:
                    wait_count += 1
                    if wait_count >= max_wait:
                        # Zu lange gewartet, erzwinge Bewegung
                        print("  ⚠️  Zu lange gewartet, erzwinge Bewegung...")
                        move = "up"
                        self.execute_move(move)
                        wait_count = 0
                
                move_count += 1
                
                # Pause zwischen Zügen
                time.sleep(config.DELAY_BETWEEN_MOVES)
                
                # Status alle 50 Züge
                if move_count % 50 == 0:
                    print(f"\n📊 Status nach {move_count} Zügen: Score = {self.score}\n")
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Fehler in Spielschleife: {e}")
                time.sleep(1)
        
        print(f"\n🏁 Spiel beendet! Erreichter Score: {self.score}")
    
    def reset(self):
        """Setzt den Spielzustand zurück"""
        self.player_x = 5
        self.player_y = 5
        self.score = 0
        self.is_alive = True
        print("\n🔄 Spiel zurückgesetzt")

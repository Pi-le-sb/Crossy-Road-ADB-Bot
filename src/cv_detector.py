#!/usr/bin/env python3
"""
Computer Vision Detector - Erkennt Spieler, Hindernisse und Pfade
"""

import cv2
import numpy as np
import config


class CVDetector:
    """Erkennt Spielelemente in Screenshots"""
    
    def __init__(self):
        """Initialisiert den CV-Detektor"""
        self.confidence_threshold = config.CV_CONFIDENCE_THRESHOLD
        self.template_threshold = config.TEMPLATE_THRESHOLD
        
        # Grid-Informationen
        self.cell_width, self.cell_height = config.get_grid_cell_size()
        
        # Template-Bilder (werden bei Bedarf geladen)
        self.templates = {}
    
    def detect_player(self, screenshot):
        """
        Erkennt die Position des Spielers (Huhn)
        
        Args:
            screenshot: Vollständiger Screenshot oder Spielbereich
            
        Returns:
            Tuple (grid_x, grid_y) oder None wenn nicht gefunden
        """
        if config.USE_TEMPLATE_MATCHING:
            return self._detect_player_template(screenshot)
        else:
            return self._detect_player_color(screenshot)
    
    def _detect_player_template(self, screenshot):
        """
        Erkennt Spieler via Template Matching
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Tuple (grid_x, grid_y) oder None
        """
        # Template laden (muss im assets/templates Ordner sein)
        template = self._load_template("player")
        
        if template is None:
            # Fallback: Farberkennung
            return self._detect_player_color(screenshot)
        
        # Template Matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.template_threshold:
            # Position in Grid-Koordinaten umrechnen
            center_x = max_loc[0] + template.shape[1] // 2
            center_y = max_loc[1] + template.shape[0] // 2
            
            grid_x = int(center_x / self.cell_width)
            grid_y = int(center_y / self.cell_height)
            
            return grid_x, grid_y
        
        return None
    
    def _detect_player_color(self, screenshot):
        """
        Erkennt Spieler via Farberkennung (einfache Heuristik)
        Crossy Road Huhn ist typischerweise weiß/gelb
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Tuple (grid_x, grid_y) oder None
        """
        # In HSV konvertieren
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Weiß/Gelb Bereich definieren
        # Weiß: niedrige Sättigung, hohe Helligkeit
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([20, 50, 255])
        
        # Maske erstellen
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Konturen finden
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Größte Kontur als Spieler annehmen
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Bounding Box
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Größe prüfen (Player hat typische Größe)
        if w < 20 or h < 20:
            return None
        
        # Grid-Position berechnen
        center_x = x + w // 2
        center_y = y + h // 2
        
        grid_x = int(center_x / self.cell_width)
        grid_y = int(center_y / self.cell_height)
        
        return grid_x, grid_y
    
    def detect_obstacles(self, screenshot):
        """
        Erkennt Hindernisse (Autos, Züge, Wasser, Bäume)
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Liste von (grid_x, grid_y, obstacle_type) Tupeln
        """
        obstacles = []
        
        # Wasser erkennen (blaue Bereiche)
        water_obstacles = self._detect_water(screenshot)
        obstacles.extend(water_obstacles)
        
        # Autos erkennen (rote/bunte Bereiche)
        car_obstacles = self._detect_cars(screenshot)
        obstacles.extend(car_obstacles)
        
        # Bäume erkennen (grüne Bereiche)
        tree_obstacles = self._detect_trees(screenshot)
        obstacles.extend(tree_obstacles)
        
        return obstacles
    
    def _detect_water(self, screenshot):
        """Erkennt Wasser (blaue Bereiche)"""
        obstacles = []
        
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Blau für Wasser
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 200])
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Morphologische Operationen
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        eroded_mask = cv2.erode(dilated_mask, kernel, iterations=1)
        
        # Konturen
        contours, _ = cv2.findContours(eroded_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Mindestgröße
                x, y, w, h = cv2.boundingRect(contour)
                
                # Grid-Positionen für alle Zellen in diesem Bereich
                start_grid_x = int(x / self.cell_width)
                end_grid_x = int((x + w) / self.cell_width)
                start_grid_y = int(y / self.cell_height)
                end_grid_y = int((y + h) / self.cell_height)
                
                for gy in range(start_grid_y, end_grid_y + 1):
                    for gx in range(start_grid_x, end_grid_x + 1):
                        obstacles.append((gx, gy, "water"))
        
        return obstacles
    
    def _detect_cars(self, screenshot):
        """Erkennt Autos (rote/orange Bereiche)"""
        obstacles = []
        
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Rot/Orange für Autos
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([15, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Morphologische Operationen
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        eroded_mask = cv2.erode(dilated_mask, kernel, iterations=1)
        
        contours, _ = cv2.findContours(eroded_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 300:
                x, y, w, h = cv2.boundingRect(contour)
                
                grid_x = int((x + w // 2) / self.cell_width)
                grid_y = int((y + h // 2) / self.cell_height)
                
                obstacles.append((grid_x, grid_y, "car"))
        
        return obstacles
    
    def _detect_trees(self, screenshot):
        """Erkennt Bäume (grüne Bereiche)"""
        obstacles = []
        
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Grün für Bäume
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([70, 255, 200])
        
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Morphologische Operationen
        kernel = np.ones((5, 5), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        eroded_mask = cv2.erode(dilated_mask, kernel, iterations=1)
        
        contours, _ = cv2.findContours(eroded_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 400:
                x, y, w, h = cv2.boundingRect(contour)
                
                grid_x = int((x + w // 2) / self.cell_width)
                grid_y = int((y + h // 2) / self.cell_height)
                
                obstacles.append((grid_x, grid_y, "tree"))
        
        return obstacles
    
    def _load_template(self, name):
        """
        Lädt ein Template-Bild
        
        Args:
            name: Template-Name (ohne Erweiterung)
            
        Returns:
            numpy array oder None
        """
        if name in self.templates:
            return self.templates[name]
        
        try:
            import os
            template_path = f"assets/templates/{name}.png"
            
            if os.path.exists(template_path):
                template = cv2.imread(template_path)
                self.templates[name] = template
                return template
        except Exception as e:
            print(f"⚠️  Template nicht gefunden: {e}")
        
        return None
    
    def analyze_frame(self, screenshot):
        """
        Vollständige Frame-Analyse
        
        Args:
            screenshot: Screenshot
            
        Returns:
            Dict mit player_position, obstacles, safe_cells
        """
        player_pos = self.detect_player(screenshot)
        obstacles = self.detect_obstacles(screenshot)
        
        # Sichere Zellen berechnen
        safe_cells = []
        rows = config.GRID_ROWS
        cols = config.GRID_COLUMNS
        
        for y in range(rows):
            for x in range(cols):
                is_safe = True
                
                for obs_x, obs_y, obs_type in obstacles:
                    if x == obs_x and y == obs_y:
                        is_safe = False
                        break
                    # Bei Wasser: auch benachbarte Zellen unsicher
                    if obs_type == "water" and abs(y - obs_y) <= 1:
                        is_safe = False
                        break
                
                if is_safe:
                    safe_cells.append((x, y))
        
        return {
            "player_position": player_pos,
            "obstacles": obstacles,
            "safe_cells": safe_cells
        }

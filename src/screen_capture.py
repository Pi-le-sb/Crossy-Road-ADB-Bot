#!/usr/bin/env python3
"""
Screen Capture - Macht Screenshots vom Android-Gerät
"""

import cv2
import numpy as np
import time
import config
from .adb_controller import ADBController


class ScreenCapture:
    """Macht Screenshots vom Android-Gerät"""
    
    def __init__(self, adb_controller):
        """
        Initialisiert Screen Capture
        
        Args:
            adb_controller: ADBController-Instanz
        """
        self.adb = adb_controller
        self.temp_file = "/tmp/crossy_bot_screenshot.png"
        self.timeout = config.SCREENSHOT_TIMEOUT
    
    def capture(self, save_path=None):
        """
        Macht einen Screenshot
        
        Args:
            save_path: Optionaler Pfad zum Speichern (standard: temporäre Datei)
            
        Returns:
            numpy array mit Bilddaten oder None bei Fehler
        """
        filepath = save_path or self.temp_file
        
        start_time = time.time()
        
        # Screenshot machen
        if not self.adb.screenshot_to_file(filepath):
            print("❌ Screenshot fehlgeschlagen!")
            return None
        
        # Zeit messen
        capture_time = time.time() - start_time
        
        # Bild laden
        try:
            img = cv2.imread(filepath)
            
            if img is None:
                print(f"❌ Konnte Screenshot nicht laden: {filepath}")
                return None
            
            # Optional speichern
            if config.SAVE_SCREENSHOTS:
                import os
                os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                debug_path = f"{config.SCREENSHOT_DIR}/screenshot_{timestamp}.png"
                cv2.imwrite(debug_path, img)
            
            return img
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Screenshots: {e}")
            return None
    
    def capture_roi(self, x, y, width, height):
        """
        Macht einen Screenshot und schneidet einen Bereich aus
        
        Args:
            x, y: Oben-links Ecke des ROI
            width, height: Größe des ROI
            
        Returns:
            numpy array mit ROI-Bilddaten oder None
        """
        full_screenshot = self.capture()
        
        if full_screenshot is None:
            return None
        
        # ROI ausschneiden
        try:
            roi = full_screenshot[y:y+height, x:x+width]
            
            if roi.size == 0:
                print(f"⚠️  ROI außerhalb des Bildbereichs!")
                return None
            
            return roi
            
        except Exception as e:
            print(f"❌ ROI-Fehler: {e}")
            return None
    
    def capture_game_area(self):
        """
        Macht einen Screenshot nur des Spielbereichs
        
        Returns:
            numpy array mit Spielbereich oder None
        """
        return self.capture_roi(
            config.GAME_AREA_X,
            config.GAME_AREA_Y,
            config.GAME_AREA_WIDTH,
            config.GAME_AREA_HEIGHT
        )
    
    def benchmark(self, num_screenshots=5):
        """
        Misst die Screenshot-Geschwindigkeit
        
        Args:
            num_screenshots: Anzahl der Test-Screenshots
            
        Returns:
            Durchschnittliche Zeit pro Screenshot in Sekunden
        """
        print(f"📊 Benchmark: {num_screenshots} Screenshots...")
        
        times = []
        
        for i in range(num_screenshots):
            start = time.time()
            self.capture()
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Screenshot {i+1}/{num_screenshots}: {elapsed:.2f}s")
        
        avg_time = sum(times) / len(times)
        print(f"\n⏱️  Durchschnitt: {avg_time:.2f}s pro Screenshot")
        
        return avg_time

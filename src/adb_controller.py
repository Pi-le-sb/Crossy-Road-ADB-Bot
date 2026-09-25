#!/usr/bin/env python3
"""
ADB Controller - Steuert das Android-Gerät über ADB
"""

import subprocess
import time
import config


class ADBController:
    """Steuerung des Android-Geräts über ADB"""
    
    def __init__(self, device_id=None):
        """
        Initialisiert den ADB Controller
        
        Args:
            device_id: ADB Device ID (None = erstes verbundenes Gerät)
        """
        self.device_id = device_id or config.ADB_DEVICE_ID
        self.device_flag = f"-s {self.device_id}" if self.device_id else ""
        self.timeout = config.ADB_TIMEOUT
    
    def run_adb(self, command, capture_output=True):
        """
        Führt einen ADB-Befehl aus
        
        Args:
            command: ADB-Befehl (ohne 'adb' Prefix)
            capture_output: Ob stdout/stderr erfasst werden sollen
            
        Returns:
            Tuple (stdout, stderr) oder None bei Timeout
        """
        full_cmd = f"adb {self.device_flag} {command}"
        
        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout bei ADB-Befehl: {command}")
            return None, "Timeout"
        except Exception as e:
            print(f"❌ ADB-Fehler: {e}")
            return None, str(e)
    
    def check_connection(self):
        """
        Prüft ob ein Gerät verbunden ist
        
        Returns:
            True wenn Gerät verbunden, False sonst
        """
        stdout, stderr = self.run_adb("devices")
        
        if stdout and "device" in stdout:
            lines = stdout.split("\n")
            # Überspringe Header-Zeile
            devices = [l for l in lines[1:] if l.strip() and "device" in l]
            if devices:
                return True
        
        return False
    
    def get_screen_size(self):
        """
        Ermittelt die Bildschirmauflösung
        
        Returns:
            Tuple (width, height) in Pixeln
        """
        stdout, _ = self.run_adb("shell wm size")
        
        if stdout and "Physical size" in stdout:
            # Parse "Physical size: 1080x2340"
            try:
                size_str = stdout.split(":")[1].strip()
                width, height = map(int, size_str.split("x"))
                return width, height
            except (ValueError, IndexError):
                pass
        
        # Default-Werte
        return 1080, 1920
    
    def tap(self, x, y):
        """
        Tippt auf eine Bildschirmposition
        
        Args:
            x: X-Koordinate in Pixeln
            y: Y-Koordinate in Pixeln
        """
        self.run_adb(f"shell input tap {int(x)} {int(y)}")
    
    def swipe(self, x1, y1, x2, y2, duration=100):
        """
        Führt eine Swipe-Geste aus
        
        Args:
            x1, y1: Startposition
            x2, y2: Endposition
            duration: Dauer in Millisekunden
        """
        self.run_adb(f"shell input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(duration)}")
    
    def keyevent(self, keycode):
        """
        Sendet ein Tastenereignis
        
        Args:
            keycode: Android keycode (z.B. 66 = Enter)
        """
        self.run_adb(f"shell input keyevent {keycode}")
    
    def text(self, text):
        """
        Gibt Text ein
        
        Args:
            text: Eingabetext
        """
        # Leerzeichen und Sonderzeichen escapen
        escaped = text.replace(" ", "%s").replace("&", "\\&")
        self.run_adb(f"shell input text \"{escaped}\"")
    
    def screenshot_to_file(self, filepath):
        """
        Macht einen Screenshot und speichert ihn lokal
        
        Args:
            filepath: Lokaler Pfad zum Speichern
            
        Returns:
            True bei Erfolg, False sonst
        """
        # Auf Gerät speichern
        self.run_adb("shell screencap -p /sdcard/crossy_bot_temp.png")
        
        # Auf PC herunterladen
        stdout, stderr = self.run_adb(f"pull /sdcard/crossy_bot_temp.png {filepath}")
        
        if stderr:
            print(f"⚠️  Screenshot Warning: {stderr}")
            return False
        
        return True
    
    def get_package(self):
        """
        Ermittelt die aktuell fokussierte App
        
        Returns:
            Package-Name der App oder None
        """
        stdout, _ = self.run_adb("shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
        
        if stdout:
            # Parse "mCurrentFocus=Window{... u0 com.hyperhippo.crossyroad/com.unity3d.player.UnityPlayerActivity}"
            try:
                for line in stdout.split("\n"):
                    if "mCurrentFocus" in line:
                        package = line.split("/")[0].split()[-1]
                        return package
            except (IndexError, ValueError):
                pass
        
        return None
    
    def start_app(self, package):
        """
        Startet eine App
        
        Args:
            package: Package-Name (z.B. "com.hyperhippo.crossyroad")
        """
        self.run_adb(f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1")
    
    def list_devices(self):
        """
        Listet alle verbundenen Geräte
        
        Returns:
            Liste von Device-IDs
        """
        stdout, _ = self.run_adb("devices")
        devices = []
        
        if stdout:
            for line in stdout.split("\n")[1:]:  # Header überspringen
                if line.strip() and "device" in line:
                    device_id = line.split()[0]
                    devices.append(device_id)
        
        return devices

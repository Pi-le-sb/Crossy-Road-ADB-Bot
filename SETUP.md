# 🛠️ C++ Setup-Anleitung

## Schritt-für-Schritt Installation

### 1. System-Abhängigkeiten installieren

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y build-essential cmake git adb libopencv-dev
```

#### macOS

```bash
# Homebrew installieren (falls nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Abhängigkeiten
brew install cmake adb opencv
```

#### Windows

1. **Visual Studio 2019+** mit "Desktop Development with C++" Workload installieren
2. **CMake** von https://cmake.org/download/ herunterladen und installieren
3. **ADB Platform Tools** von https://developer.android.com/studio/releases/platform-tools
4. **OpenCV** von https://opencv.org/releases/ (oder vcpkg: `vcpkg install opencv`)

### 2. Repository klonen

```bash
git clone https://github.com/Pi-le-sb/Crossy-Road-ADB-Bot.git
cd Crossy-Road-ADB-Bot
```

### 3. Bauen

#### Linux/macOS

```bash
mkdir build
cd build
cmake ..
make -j$(nproc)  # oder: make -j$(sysctl -n hw.ncpu) auf macOS
```

#### Windows (Developer Command Prompt)

```cmd
mkdir build
cd build
cmake -G "Visual Studio 16 2019" ..
cmake --build . --config Release
```

### 4. Testen

```bash
# ADB-Test
./build/crossy_bot --test-adb

# Screenshot-Test
./build/crossy_bot --test-screen
```

### 5. Konfigurieren

Bearbeite `config.ini` und passe den Spielbereich an:

1. `--test-screen` ausführen
2. `test_screenshot.png` öffnen
3. Koordinaten messen
4. Werte in `config.ini` eintragen

### 6. Ausführen

```bash
./build/crossy_bot
```

## Fehlerbehebung

### CMake findet OpenCV nicht

**Linux:**
```bash
pkg-config --modversion opencv4
# Sollte Version anzeigen
```

**Windows (vcpkg):**
```cmd
vcpkg install opencv:x64-windows
set CMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
cmake ..
```

### Compiler-Fehler

- C++17 erforderlich: GCC 9+, Clang 10+, MSVC 2019+
- `cmake .. -DCMAKE_BUILD_TYPE=Release` für Release-Build

### ADB funktioniert nicht

- USB-Debugging aktivieren
- Gerät anschließen und "Immer zulassen" bestätigen
- `adb devices` prüfen

## Performance-Tipps

1. **Release-Build**: `cmake .. -DCMAKE_BUILD_TYPE=Release`
2. **AVX2**: `-march=native` (Linux)
3. **OpenCV mit TBB/IPP**: Schnellere CV-Operationen

Viel Erfolg! 🎮

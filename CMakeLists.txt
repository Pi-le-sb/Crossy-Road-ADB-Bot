cmake_minimum_required(VERSION 3.16)
project(CrossyRoadADBBot VERSION 1.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler-Flags
if(MSVC)
    add_compile_options(/W4 /O2 /std:c++17)
else()
    add_compile_options(-Wall -Wextra -O3 -std=c++17)
endif()

# OpenCV finden
find_package(OpenCV 4.5 REQUIRED)
if(OpenCV_FOUND)
    message(STATUS "OpenCV gefunden: ${OpenCV_VERSION}")
    include_directories(${OpenCV_INCLUDE_DIRS})
else()
    message(FATAL_ERROR "OpenCV nicht gefunden! Bitte installieren.")
endif()

# Threads finden
find_package(Threads REQUIRED)

# Include-Verzeichnis
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source-Dateien
set(SOURCES
    src/adb_controller.cpp
    src/screen_capture.cpp
    src/cv_detector.cpp
    src/minimax_ai.cpp
    src/game_state.cpp
    src/utils.cpp
    main.cpp
)

# Executable erstellen
add_executable(crossy_bot ${SOURCES})

# Libraries verlinken
target_link_libraries(crossy_bot
    ${OpenCV_LIBS}
    Threads::Threads
)

# Install-Target
install(TARGETS crossy_bot DESTINATION bin)

# Config-Datei installieren
configure_file(${PROJECT_SOURCE_DIR}/config.ini ${CMAKE_BINARY_DIR}/config.ini COPYONLY)

# Ausgabe
message(STATUS "Build-Konfiguration:")
message(STATUS "  C++ Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  Build-Typ: ${CMAKE_BUILD_TYPE}")
message(STATUS "  OpenCV: ${OpenCV_VERSION}")

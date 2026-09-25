#include "adb_controller.h"
#include "screen_capture.h"
#include "cv_detector.h"
#include "minimax_ai.h"
#include "config.h"
#include <iostream>
#include <chrono>
#include <thread>
#include <csignal>

volatile bool g_running = true;

void signalHandler(int) {
    g_running = false;
    std::cout << "\n[Bot] Stoppe..." << std::endl;
}

int main(int argc, char* argv[]) {
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    // Konfiguration laden
    BotConfig config;
    config.load("config.ini");

    // CLI-Parameter
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--device" && i + 1 < argc)
            config.deviceId = argv[++i];
        else if (arg == "--depth" && i + 1 < argc)
            config.minimaxDepth = std::stoi(argv[++i]);
        else if (arg == "--debug")
            config.debug = true;
        else if (arg == "--test-adb") {
            ADBController adb(config.deviceId);
            std::cout << "ADB verfügbar: " << (adb.isAvailable() ? "Ja" : "Nein") << std::endl;
            std::cout << "Verbindung: " << (adb.checkConnection() ? "OK" : "FEHLER") << std::endl;
            if (adb.checkConnection()) {
                auto size = adb.getScreenSize();
                std::cout << "Bildschirm: " << size.first << "x" << size.second << std::endl;
            }
            return 0;
        } else if (arg == "--test-screen") {
            ADBController adb(config.deviceId);
            if (!adb.checkConnection()) {
                std::cerr << "Kein Gerät verbunden!" << std::endl;
                return 1;
            }
            ScreenCapture capture(adb);
            auto img = capture.captureGameArea(config.gameX, config.gameY,
                                               config.gameWidth, config.gameHeight);
            if (!img.empty()) {
                cv::imwrite("test_screenshot.png", img);
                std::cout << "Screenshot gespeichert: test_screenshot.png" << std::endl;
                std::cout << "Größe: " << img.cols << "x" << img.rows << std::endl;
            } else {
                std::cerr << "Screenshot fehlgeschlagen!" << std::endl;
                return 1;
            }
            return 0;
        } else if (arg == "--help") {
            std::cout << "Crossy Road ADB Bot (C++ Minimax AI)\n"
                      << "Usage: " << argv[0] << " [OPTIONS]\n"
                      << "  --device ID     ADB Device ID\n"
                      << "  --depth N       Minimax-Tiefe (1-6)\n"
                      << "  --debug         Debug-Ausgaben\n"
                      << "  --test-adb      ADB-Test\n"
                      << "  --test-screen   Screenshot-Test\n"
                      << "  --help          Diese Hilfe" << std::endl;
            return 0;
        }
    }

    // Komponenten initialisieren
    ADBController adb(config.deviceId);

    if (!adb.checkConnection()) {
        std::cerr << "❌ Kein ADB-Gerät verbunden!" << std::endl;
        std::cerr << "  USB-Debugging aktivieren und Gerät anschließen." << std::endl;
        return 1;
    }

    ScreenCapture capture(adb);
    CVDetector detector(config.gridCols, config.gridRows);
    MinimaxAI ai(config.minimaxDepth, config.aiTimeLimitMs);

    ai.setDebug(config.debug);

    std::cout << "\n🐔 Crossy Road ADB Bot (C++ Minimax AI)\n";
    std::cout << "   AI-Tiefe: " << config.minimaxDepth << "\n";
    std::cout << "   Spielbereich: " << config.gameX << "," << config.gameY
              << " +" << config.gameWidth << "x" << config.gameHeight << "\n";
    std::cout << "\n⚠️  Crossy Road muss geöffnet sein!" << std::endl;
    std::cout << "   Drücke Enter zum Starten (oder Strg+C zum Abbrechen)..." << std::endl;
    std::cin.get();

    int score = 0;
    int moves = 0;
    auto startTime = std::chrono::steady_clock::now();

    while (g_running) {
        // Screenshot
        auto img = capture.captureGameArea(config.gameX, config.gameY,
                                           config.gameWidth, config.gameHeight);
        if (img.empty()) {
            std::cerr << "Screenshot-Fehler!" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            continue;
        }

        // CV-Analyse
        GameState state = detector.analyze(img);

        if (config.debug) {
            std::cout << "[CV] " << state.toString() << std::endl;
        }

        // Minimax-Entscheidung
        Direction move = ai.getBestMove(state);

        if (config.debug) {
            std::cout << "[AI] Zug: " << static_cast<int>(move)
                      << " (" << ai.getLastSearchTimeMs() << "ms, "
                      << ai.getNodesSearched() << " Knoten)" << std::endl;
        }

        // Bewegung ausführen
        if (move != Direction::NONE && move != Direction::WAIT) {
            int centerX = config.gameX + config.gameWidth / 2;
            int centerY = config.gameY + config.gameHeight / 2;
            int offset = std::min(config.gameWidth, config.gameHeight) / 6;

            int tapX = centerX, tapY = centerY;
            if (move == Direction::UP) tapY -= offset;
            else if (move == Direction::DOWN) tapY += offset;
            else if (move == Direction::LEFT) tapX -= offset;
            else if (move == Direction::RIGHT) tapX += offset;

            adb.tap(tapX, tapY);
            ++moves;

            if (move == Direction::UP)
                ++score;
        }

        // Warten
        std::this_thread::sleep_for(std::chrono::milliseconds(config.frameDelayMs));

        // Status
        if (moves > 0 && moves % 50 == 0) {
            auto elapsed = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - startTime).count();
            std::cout << "\n📊 Status: Score=" << score << " Züge=" << moves
                      << " Zeit=" << static_cast<int>(elapsed) << "s" << std::endl;
        }
    }

    auto elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - startTime).count();
    std::cout << "\n🏁 Beendet! Score=" << score << " Züge=" << moves
              << " Zeit=" << static_cast<int>(elapsed) << "s" << std::endl;

    return 0;
}

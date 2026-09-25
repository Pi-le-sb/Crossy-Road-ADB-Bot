#include "cv_detector.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <iostream>

CVDetector::CVDetector(int gridCols, int gridRows)
    : gridCols_(gridCols), gridRows_(gridRows) {}

GameState CVDetector::analyze(const cv::Mat& gameImage) const {
    GameState state;
    state.clearObstacles();

    if (gameImage.empty())
        return state;

    int cellWidth = gameImage.cols / gridCols_;
    int cellHeight = gameImage.rows / gridRows_;

    // Grid analysieren
    for (int y = 0; y < gridRows_; ++y) {
        for (int x = 0; x < gridCols_; ++x) {
            cv::Rect cellRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
            cv::Mat cell = gameImage(cellRect);

            CellType type = classifyCell(cell);
            state.setCell(x, y, type);

            // Hindernisse erkennen
            if (type == CellType::CAR || type == CellType::TREE) {
                Obstacle obs{{x, y}, type};
                state.addObstacle(obs);
            }

            // Spieler erkennen
            if (detectPlayer(cell)) {
                state.setPlayerPosition({x, y});
            }
        }
    }

    return state;
}

CellType CVDetector::classifyCell(const cv::Mat& cell) const {
    if (cell.empty())
        return CellType::UNKNOWN;

    cv::Mat hsv;
    cv::cvtColor(cell, hsv, cv::COLOR_BGR2HSV);

    // Durchschnittsfarbe berechnen
    cv::Scalar mean = cv::mean(hsv);
    float h = mean[0], s = mean[1], v = mean[2];

    // Wasser (blau, hohe Sättigung)
    if (h > 100 && h < 130 && s > 50)
        return CellType::WATER;

    // Gras (grün)
    if (h > 40 && h < 80 && s > 30)
        return CellType::GRASS;

    // Straße (grau, niedrige Sättigung)
    if (s < 30 && v > 100)
        return CellType::ROAD;

    // Baum (dunkelgrün)
    if (detectTree(cell))
        return CellType::TREE;

    // Auto (rot/orange)
    if (detectCar(cell))
        return CellType::CAR;

    return CellType::EMPTY;
}

bool CVDetector::detectPlayer(const cv::Mat& cell) const {
    if (cell.empty())
        return false;

    cv::Mat hsv;
    cv::cvtColor(cell, hsv, cv::COLOR_BGR2HSV);

    // Spieler ist typischerweise weiß/gelb (Huhn)
    cv::Scalar mean = cv::mean(hsv);
    float h = mean[0], s = mean[1], v = mean[2];

    // Weiß/gelb mit hoher Helligkeit
    return (v > 200 && s < 50) || (h > 20 && h < 35 && s > 50);
}

bool CVDetector::detectCar(const cv::Mat& cell) const {
    if (cell.empty())
        return false;

    cv::Mat hsv;
    cv::cvtColor(cell, hsv, cv::COLOR_BGR2HSV);

    cv::Scalar mean = cv::mean(hsv);
    float h = mean[0];

    // Rot/orange Autos
    return (h > 0 && h < 15) || (h > 160 && h < 180);
}

bool CVDetector::detectTree(const cv::Mat& cell) const {
    if (cell.empty())
        return false;

    cv::Mat hsv;
    cv::cvtColor(cell, hsv, cv::COLOR_BGR2HSV);

    cv::Scalar mean = cv::mean(hsv);
    float h = mean[0], s = mean[1], v = mean[2];

    // Dunkelgrüne Bäume
    return h > 50 && h < 70 && s > 80 && v < 150;
}

bool CVDetector::detectWater(const cv::Mat& cell) const {
    if (cell.empty())
        return false;

    cv::Mat hsv;
    cv::cvtColor(cell, hsv, cv::COLOR_BGR2HSV);

    cv::Scalar mean = cv::mean(hsv);
    float h = mean[0];

    // Blaues Wasser
    return h > 100 && h < 130;
}

cv::Mat CVDetector::drawDebug(const cv::Mat& image, const GameState& state) const {
    cv::Mat debug = image.clone();

    int cellWidth = debug.cols / gridCols_;
    int cellHeight = debug.rows / gridRows_;

    // Grid zeichnen
    for (int x = 0; x <= gridCols_; ++x) {
        cv::line(debug, {x * cellWidth, 0}, {x * cellWidth, debug.rows},
                 cv::Scalar(0, 255, 0), 1);
    }
    for (int y = 0; y <= gridRows_; ++y) {
        cv::line(debug, {0, y * cellHeight}, {debug.cols, y * cellHeight},
                 cv::Scalar(0, 255, 0), 1);
    }

    // Spieler markieren
    auto pos = state.getPlayerPosition();
    cv::rectangle(debug,
                  cv::Point(pos.x * cellWidth, pos.y * cellHeight),
                  cv::Point((pos.x + 1) * cellWidth, (pos.y + 1) * cellHeight),
                  cv::Scalar(255, 255, 0), 2);

    return debug;
}

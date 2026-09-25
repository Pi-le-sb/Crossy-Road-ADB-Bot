#pragma once

#include "game_state.h"
#include <opencv2/core.hpp>

/**
 * OpenCV-basierte Wahrnehmungsschicht.
 * Konvertiert den sichtbaren Spielbereich in einen GameState für MinimaxAI.
 */
class CVDetector {
public:
    CVDetector(int gridCols = GRID_COLS, int gridRows = GRID_ROWS);

    GameState analyze(const cv::Mat& gameImage) const;
    void setDebug(bool enabled) { debug_ = enabled; }

    cv::Mat drawDebug(const cv::Mat& image, const GameState& state) const;

private:
    int gridCols_;
    int gridRows_;
    bool debug_ = false;

    CellType classifyCell(const cv::Mat& cell) const;
    bool detectPlayer(const cv::Mat& cell) const;
    bool detectCar(const cv::Mat& cell) const;
    bool detectTree(const cv::Mat& cell) const;
    bool detectWater(const cv::Mat& cell) const;
};

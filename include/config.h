#pragma once

#include <string>

struct BotConfig {
    std::string deviceId;

    int gameX = 100;
    int gameY = 300;
    int gameWidth = 800;
    int gameHeight = 600;
    int gridCols = 10;
    int gridRows = 12;

    int minimaxDepth = 4;
    int aiTimeLimitMs = 80;
    int frameDelayMs = 180;
    bool debug = false;

    bool load(const std::string& filename);
};

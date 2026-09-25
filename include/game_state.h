#pragma once

#include <vector>
#include <array>
#include <string>
#include <cstdint>

/**
 * Spielzustand für Minimax AI
 * Basierend auf der Struktur von alwyntan/Crossy-Road-AI/Assets/Scripts/GameState.cs
 */

constexpr int GRID_COLS = 10;
constexpr int GRID_ROWS = 12;

enum class Direction : uint8_t {
    UP,
    DOWN,
    LEFT,
    RIGHT,
    WAIT,
    NONE
};

enum class CellType : uint8_t {
    EMPTY,
    ROAD,
    GRASS,
    WATER,
    TREE,
    CAR,
    LOG,
    TRAIN,
    PLAYER,
    UNKNOWN
};

struct Position {
    int x = 0;
    int y = 0;

    bool operator==(const Position& other) const {
        return x == other.x && y == other.y;
    }

    bool operator!=(const Position& other) const {
        return !(*this == other);
    }

    bool isValid() const {
        return x >= 0 && x < GRID_COLS && y >= 0 && y < GRID_ROWS;
    }
};

struct Obstacle {
    Position pos;
    CellType type;
    float velocityX = 0.0f;
    float velocityY = 0.0f;
    int width = 1;
    int height = 1;
};

/**
 * Repräsentiert den Zustand des sichtbaren Crossy-Road-Spielbereichs.
 * Der Zustand wird aus OpenCV-Erkennung erzeugt und von der Minimax-AI simuliert.
 */
class GameState {
public:
    GameState();

    // Grid-Zugriff
    CellType getCell(int x, int y) const;
    void setCell(int x, int y, CellType type);

    // Spieler
    Position getPlayerPosition() const { return playerPos_; }
    void setPlayerPosition(Position pos);
    bool isPlayerAlive() const { return playerAlive_; }
    void setPlayerAlive(bool alive) { playerAlive_ = alive; }

    // Spielzustand
    int getScore() const { return score_; }
    void setScore(int score) { score_ = score; }
    int getTurn() const { return turn_; }
    void setTurn(int turn) { turn_ = turn; }

    // Hindernisse
    const std::vector<Obstacle>& getObstacles() const { return obstacles_; }
    void addObstacle(const Obstacle& obstacle);
    void clearObstacles();

    // Bewegungen und Simulation (Kern von GameTreeAI)
    std::vector<Direction> getValidMoves() const;
    GameState applyMove(Direction direction) const;
    GameState simulateEnvironment() const;
    bool isSafe(Position pos) const;
    bool isTerminal() const;

    // Bewertung für AI
    double evaluate() const;
    double getDangerScore(Position pos) const;
    int countAvailableMoves() const;

    // Debugging
    std::string toString() const;

private:
    std::array<std::array<CellType, GRID_COLS>, GRID_ROWS> grid_;
    Position playerPos_;
    bool playerAlive_;
    int score_;
    int turn_;
    std::vector<Obstacle> obstacles_;

    bool isObstacleAt(Position pos) const;
    bool isWaterSafe(Position pos) const;
    Position directionToDelta(Direction direction) const;
};

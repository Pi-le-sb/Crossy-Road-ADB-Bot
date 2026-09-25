#include "game_state.h"
#include <algorithm>
#include <cmath>
#include <sstream>

GameState::GameState()
    : playerPos_{GRID_COLS / 2, 0}, playerAlive_{true}, score_{0}, turn_{0} {
    // Standard-Grid initialisieren
    for (int y = 0; y < GRID_ROWS; ++y) {
        for (int x = 0; x < GRID_COLS; ++x) {
            if (y % 3 == 0)
                grid_[y][x] = CellType::GRASS;
            else if (y % 3 == 1)
                grid_[y][x] = CellType::ROAD;
            else
                grid_[y][x] = CellType::WATER;
        }
    }
}

CellType GameState::getCell(int x, int y) const {
    if (x < 0 || x >= GRID_COLS || y < 0 || y >= GRID_ROWS)
        return CellType::UNKNOWN;
    return grid_[y][x];
}

void GameState::setCell(int x, int y, CellType type) {
    if (x >= 0 && x < GRID_COLS && y >= 0 && y < GRID_ROWS)
        grid_[y][x] = type;
}

void GameState::setPlayerPosition(Position pos) {
    playerPos_ = pos;
}

void GameState::addObstacle(const Obstacle& obstacle) {
    obstacles_.push_back(obstacle);
}

void GameState::clearObstacles() {
    obstacles_.clear();
}

std::vector<Direction> GameState::getValidMoves() const {
    std::vector<Direction> moves;

    if (!playerAlive_)
        return moves;

    // Vorwärts ist immer bevorzugt
    if (isSafe({playerPos_.x, playerPos_.y + 1}))
        moves.push_back(Direction::UP);

    if (isSafe({playerPos_.x - 1, playerPos_.y}))
        moves.push_back(Direction::LEFT);

    if (isSafe({playerPos_.x + 1, playerPos_.y}))
        moves.push_back(Direction::RIGHT);

    if (isSafe({playerPos_.x, playerPos_.y - 1}))
        moves.push_back(Direction::DOWN);

    moves.push_back(Direction::WAIT);

    return moves;
}

GameState GameState::applyMove(Direction direction) const {
    GameState next = *this;
    next.turn_ = turn_ + 1;

    if (!playerAlive_)
        return next;

    Position delta = directionToDelta(direction);
    Position newPos{playerPos_.x + delta.x, playerPos_.y + delta.y};

    if (newPos.isValid() && isSafe(newPos)) {
        next.playerPos_ = newPos;
        next.score_ = std::max(score_, newPos.y);
    }

    return next;
}

GameState GameState::simulateEnvironment() const {
    GameState next = *this;

    // Hindernisse bewegen (vereinfacht: nur X-Richtung)
    for (auto& obs : next.obstacles_) {
        if (obs.velocityX != 0.0f) {
            obs.pos.x += (obs.velocityX > 0) ? 1 : -1;
            if (obs.pos.x < 0) obs.pos.x = GRID_COLS - 1;
            if (obs.pos.x >= GRID_COLS) obs.pos.x = 0;
        }
    }

    // Spieler-Tod prüfen (von Hindernis getroffen)
    for (const auto& obs : next.obstacles_) {
        if (obs.pos == next.playerPos_ && (obs.type == CellType::CAR || obs.type == CellType::LOG)) {
            next.playerAlive_ = false;
            break;
        }
    }

    return next;
}

bool GameState::isSafe(Position pos) const {
    if (!pos.isValid())
        return false;

    if (isObstacleAt(pos))
        return false;

    // Wasser: Log benötigt, aber hier vereinfacht als unsicher
    if (getCell(pos.x, pos.y) == CellType::WATER)
        return false;

    return true;
}

bool GameState::isTerminal() const {
    return !playerAlive_ || playerPos_.y >= GRID_ROWS - 1;
}

double GameState::evaluate() const {
    if (!playerAlive_)
        return -1000.0;

    double score = 0.0;

    // Vorwärtsbewegung belohnen (wichtigster Faktor wie in GameTreeAI)
    score += playerPos_.y * 10.0;

    // Verfügbare Züge zählen (Flexibilität belohnen)
    score += countAvailableMoves() * 2.0;

    // Gefahr in der Nähe bestrafen
    score -= getDangerScore(playerPos_) * 5.0;

    // Wasser in der Nähe bestrafen
    for (int dy = -1; dy <= 1; ++dy) {
        int ny = playerPos_.y + dy;
        if (ny >= 0 && ny < GRID_ROWS && getCell(playerPos_.x, ny) == CellType::WATER) {
            score -= 3.0;
        }
    }

    return score;
}

double GameState::getDangerScore(Position pos) const {
    double danger = 0.0;

    for (const auto& obs : obstacles_) {
        if (obs.type == CellType::CAR || obs.type == CellType::LOG) {
            int dx = std::abs(obs.pos.x - pos.x);
            int dy = std::abs(obs.pos.y - pos.y);
            if (dx <= 1 && dy <= 1)
                danger += 1.0;
        }
    }

    return danger;
}

int GameState::countAvailableMoves() const {
    return static_cast<int>(getValidMoves().size());
}

std::string GameState::toString() const {
    std::ostringstream oss;
    oss << "Player: (" << playerPos_.x << "," << playerPos_.y << ")"
        << " Score: " << score_ << " Alive: " << (playerAlive_ ? "Y" : "N");
    return oss.str();
}

bool GameState::isObstacleAt(Position pos) const {
    for (const auto& obs : obstacles_) {
        if (obs.pos == pos && (obs.type == CellType::CAR || obs.type == CellType::TREE))
            return true;
    }
    return false;
}

bool GameState::isWaterSafe(Position pos) const {
    // Vereinfacht: Wasser ist nie sicher (kein Log-Transport implementiert)
    return false;
}

Position GameState::directionToDelta(Direction direction) const {
    switch (direction) {
        case Direction::UP:    return {0, 1};
        case Direction::DOWN:  return {0, -1};
        case Direction::LEFT:  return {-1, 0};
        case Direction::RIGHT: return {1, 0};
        default:               return {0, 0};
    }
}

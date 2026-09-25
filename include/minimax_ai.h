#pragma once

#include "game_state.h"
#include <chrono>
#include <unordered_map>

/**
 * Minimax AI mit Alpha-Beta-Pruning.
 *
 * Architektur und Bewertungsprinzip basieren auf GameTreeAI.cs aus
 * alwyntan/Crossy-Road-AI. Die C++-Variante ergänzt Alpha-Beta-Pruning,
 * iterative Tiefensuche und ein Zeitlimit für Echtzeitbetrieb über ADB.
 */
class MinimaxAI {
public:
    explicit MinimaxAI(int maxDepth = 4, int timeLimitMs = 80);

    // Beste Bewegung ermitteln
    Direction getBestMove(const GameState& state);

    // Konfiguration
    void setMaxDepth(int depth) { maxDepth_ = std::max(1, depth); }
    int getMaxDepth() const { return maxDepth_; }
    void setTimeLimitMs(int ms) { timeLimitMs_ = std::max(1, ms); }
    void setDebug(bool debug) { debug_ = debug; }

    // Statistik
    uint64_t getNodesSearched() const { return nodesSearched_; }
    double getLastEvaluation() const { return lastEvaluation_; }
    int getReachedDepth() const { return reachedDepth_; }
    double getLastSearchTimeMs() const { return lastSearchTimeMs_; }

private:
    int maxDepth_;
    int timeLimitMs_;
    bool debug_ = false;

    uint64_t nodesSearched_ = 0;
    double lastEvaluation_ = 0.0;
    int reachedDepth_ = 0;
    double lastSearchTimeMs_ = 0.0;
    std::chrono::steady_clock::time_point searchStart_;

    // Maximierender Spielerzug, dann deterministische Umweltbewegung
    double minimax(const GameState& state, int depth, double alpha, double beta);
    double evaluateMove(const GameState& state, Direction move, int depth,
                        double alpha, double beta);

    bool timeExpired() const;
    std::vector<Direction> orderMoves(const GameState& state,
                                      const std::vector<Direction>& moves) const;
};

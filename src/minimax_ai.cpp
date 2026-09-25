#include "minimax_ai.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>

MinimaxAI::MinimaxAI(int maxDepth, int timeLimitMs)
    : maxDepth_(maxDepth), timeLimitMs_(timeLimitMs) {}

Direction MinimaxAI::getBestMove(const GameState& state) {
    searchStart_ = std::chrono::steady_clock::now();
    nodesSearched_ = 0;
    reachedDepth_ = 0;

    auto moves = state.getValidMoves();
    if (moves.empty())
        return Direction::WAIT;

    // Iterative Tiefensuche: versuche tiefere Ebenen, solange Zeit bleibt
    Direction bestMove = Direction::WAIT;
    double bestValue = -std::numeric_limits<double>::infinity();

    for (int depth = 1; depth <= maxDepth_; ++depth) {
        if (timeExpired())
            break;

        reachedDepth_ = depth;

        for (const auto& move : orderMoves(state, moves)) {
            GameState nextState = state.applyMove(move);
            nextState = nextState.simulateEnvironment();

            double value = minimax(nextState, depth - 1,
                                   -std::numeric_limits<double>::infinity(),
                                   std::numeric_limits<double>::infinity());

            if (value > bestValue) {
                bestValue = value;
                bestMove = move;
            }
        }

        lastEvaluation_ = bestValue;

        if (debug_) {
            std::cout << "[AI] Tiefe " << depth << ": Wert=" << bestValue
                      << " Zug=" << static_cast<int>(bestMove) << std::endl;
        }
    }

    lastSearchTimeMs_ = std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now() - searchStart_).count();

    if (debug_) {
        std::cout << "[AI] Knoten=" << nodesSearched_
                  << " Zeit=" << lastSearchTimeMs_ << "ms" << std::endl;
    }

    return bestMove;
}

double MinimaxAI::minimax(const GameState& state, int depth, double alpha, double beta) {
    ++nodesSearched_;

    if (timeExpired() || state.isTerminal() || depth == 0)
        return state.evaluate();

    // Maximierer (Spieler)
    double maxEval = -std::numeric_limits<double>::infinity();

    for (const auto& move : state.getValidMoves()) {
        GameState nextState = state.applyMove(move);
        nextState = nextState.simulateEnvironment();

        double eval = minimax(nextState, depth - 1, alpha, beta);
        maxEval = std::max(maxEval, eval);
        alpha = std::max(alpha, eval);

        if (beta <= alpha)
            break; // Beta-Cutoff
    }

    return maxEval;
}

double MinimaxAI::evaluateMove(const GameState& state, Direction move, int depth,
                               double alpha, double beta) {
    GameState nextState = state.applyMove(move);
    nextState = nextState.simulateEnvironment();
    return minimax(nextState, depth - 1, alpha, beta);
}

bool MinimaxAI::timeExpired() const {
    auto elapsed = std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now() - searchStart_).count();
    return elapsed >= timeLimitMs_;
}

std::vector<Direction> MinimaxAI::orderMoves(const GameState& state,
                                              const std::vector<Direction>& moves) const {
    // Bewegungen priorisieren: Vorwärts > Seitwärts > Warten > Rückwärts
    std::vector<Direction> ordered;

    for (auto m : moves) {
        if (m == Direction::UP)
            ordered.insert(ordered.begin(), m);
        else if (m == Direction::LEFT || m == Direction::RIGHT)
            ordered.push_back(m);
        else
            ordered.insert(ordered.end(), m);
    }

    return ordered;
}

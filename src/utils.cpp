#include "utils.h"
#include <algorithm>
#include <sstream>

std::string trim(const std::string& value) {
    auto start = value.find_first_not_of(" \t\n\r");
    if (start == std::string::npos)
        return "";
    auto end = value.find_last_not_of(" \t\n\r");
    return value.substr(start, end - start + 1);
}

std::vector<std::string> split(const std::string& value, char delimiter) {
    std::vector<std::string> result;
    std::istringstream iss(value);
    std::string token;
    while (std::getline(iss, token, delimiter)) {
        result.push_back(trim(token));
    }
    return result;
}

std::string directionToString(int direction) {
    switch (direction) {
        case 0: return "UP";
        case 1: return "DOWN";
        case 2: return "LEFT";
        case 3: return "RIGHT";
        case 4: return "WAIT";
        default: return "NONE";
    }
}

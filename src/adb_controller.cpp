#include "adb_controller.h"
#include <cstdlib>
#include <iostream>
#include <sstream>

ADBController::ADBController(const std::string& deviceId) : deviceId_(deviceId) {}

bool ADBController::isAvailable() const {
    auto result = run("version");
    return !result.empty() && result.find("Android Debug Bridge") != std::string::npos;
}

bool ADBController::checkConnection() const {
    auto result = run("devices");
    if (result.empty())
        return false;

    std::istringstream iss(result);
    std::string line;
    std::getline(iss, line); // Header überspringen

    while (std::getline(iss, line)) {
        if (line.find("device") != std::string::npos && line.find("\t") != std::string::npos)
            return true;
    }
    return false;
}

std::vector<std::string> ADBController::listDevices() const {
    std::vector<std::string> devices;
    auto result = run("devices");

    std::istringstream iss(result);
    std::string line;
    std::getline(iss, line); // Header

    while (std::getline(iss, line)) {
        if (line.find("device") != std::string::npos) {
            size_t tab = line.find("\t");
            if (tab != std::string::npos)
                devices.push_back(line.substr(0, tab));
        }
    }
    return devices;
}

std::pair<int, int> ADBController::getScreenSize() const {
    auto result = run("shell wm size");
    if (result.find("Physical size:") != std::string::npos) {
        size_t pos = result.find(":") + 1;
        std::string sizeStr = result.substr(pos);
        size_t x = sizeStr.find("x");
        if (x != std::string::npos) {
            int width = std::stoi(sizeStr.substr(0, x));
            int height = std::stoi(sizeStr.substr(x + 1));
            return {width, height};
        }
    }
    return {1080, 1920};
}

bool ADBController::tap(int x, int y) const {
    return shell("input tap " + std::to_string(x) + " " + std::to_string(y));
}

bool ADBController::swipe(int x1, int y1, int x2, int y2, int durationMs) const {
    return shell("input swipe " + std::to_string(x1) + " " + std::to_string(y1) + " " +
                 std::to_string(x2) + " " + std::to_string(y2) + " " + std::to_string(durationMs));
}

bool ADBController::screenshot(const std::string& localPath) const {
    const std::string remotePath = "/sdcard/crossy_bot_temp.png";
    if (!shell("screencap -p " + remotePath))
        return false;
    return shell("pull " + remotePath + " " + quote(localPath));
}

bool ADBController::shell(const std::string& command) const {
    auto result = run("shell " + command);
    return result.empty() || result.find("error:") == std::string::npos;
}

std::string ADBController::prefix() const {
    if (deviceId_.empty())
        return "adb";
    return "adb -s " + deviceId_;
}

std::string ADBController::run(const std::string& command) const {
    std::string fullCmd = prefix() + " " + command;
    std::string result;

#ifdef _WIN32
    FILE* pipe = _popen(fullCmd.c_str(), "r");
#else
    FILE* pipe = popen(fullCmd.c_str(), "r");
#endif

    if (!pipe)
        return "";

    char buffer[256];
    while (fgets(buffer, sizeof(buffer), pipe)) {
        result += buffer;
    }

#ifdef _WIN32
    _pclose(pipe);
#else
    pclose(pipe);
#endif

    return result;
}

std::string ADBController::quote(const std::string& value) {
    std::string quoted;
    for (char c : value) {
        if (c == ' ' || c == '"' || c == '$')
            quoted += '\\';
        quoted += c;
    }
    return quoted;
}

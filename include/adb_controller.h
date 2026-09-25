#pragma once

#include <string>
#include <vector>
#include <optional>

/** ADB-Schnittstelle für echte Android-Geräte. */
class ADBController {
public:
    explicit ADBController(const std::string& deviceId = "");

    bool isAvailable() const;
    bool checkConnection() const;
    std::vector<std::string> listDevices() const;

    std::pair<int, int> getScreenSize() const;
    bool tap(int x, int y) const;
    bool swipe(int x1, int y1, int x2, int y2, int durationMs = 80) const;
    bool screenshot(const std::string& localPath) const;
    bool shell(const std::string& command) const;

    const std::string& getDeviceId() const { return deviceId_; }

private:
    std::string deviceId_;
    std::string prefix() const;
    std::string run(const std::string& command) const;
    static std::string quote(const std::string& value);
};

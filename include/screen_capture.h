#pragma once

#include "adb_controller.h"
#include <opencv2/core.hpp>
#include <string>

/** Bildschirmaufnahme und Ausschneiden des Spielbereichs. */
class ScreenCapture {
public:
    ScreenCapture(const ADBController& adb, const std::string& tempPath = "crossy_screen.png");

    cv::Mat capture() const;
    cv::Mat captureGameArea(int x, int y, int width, int height) const;

private:
    const ADBController& adb_;
    std::string tempPath_;
};

#include "screen_capture.h"
#include <opencv2/imgcodecs.hpp>
#include <iostream>

ScreenCapture::ScreenCapture(const ADBController& adb, const std::string& tempPath)
    : adb_(adb), tempPath_(tempPath) {}

cv::Mat ScreenCapture::capture() const {
    if (!adb_.screenshot(tempPath_)) {
        std::cerr << "[ScreenCapture] Screenshot fehlgeschlagen!" << std::endl;
        return cv::Mat();
    }

    cv::Mat img = cv::imread(tempPath_);
    if (img.empty()) {
        std::cerr << "[ScreenCapture] Konnte Bild nicht laden: " << tempPath_ << std::endl;
    }
    return img;
}

cv::Mat ScreenCapture::captureGameArea(int x, int y, int width, int height) const {
    cv::Mat full = capture();
    if (full.empty())
        return cv::Mat();

    if (x < 0 || y < 0 || x + width > full.cols || y + height > full.rows) {
        std::cerr << "[ScreenCapture] ROI außerhalb des Bildes!" << std::endl;
        return cv::Mat();
    }

    return full(cv::Rect(x, y, width, height));
}

# Read-only motion diagnostic

Run: python motion_preview.py
Tests: python -m unittest -v test_motion_preview
Requires the existing GUI opencv-python and numpy packages and calibration.py.

Start a round, select a static tree/rock region with many corners, then Enter. Avoid vehicles, duck, animated water, UI or areas that vehicles cross. R selects a fresh static reference; Q/Esc exits. Do not run the old main.py at the same time. No input events or file saves are performed by this diagnostic.

The camera estimate uses the median displacement of at least eight forward/backward-checked reference features, requiring at least 75 percent agreement within two preview pixels. Only translation is modeled, not rotation, zoom or perspective changes. A consistent but incorrect reference can still fool this check. The cyan outline follows the selected reference via estimated camera translation. If it leaves the frame or loses features, UNKNOWN is shown until R. If the camera moves while choosing the region, reselect it.

Orange arrows show residual feature velocity after subtracting camera translation. Their lengths represent 0.25 seconds of projected motion. CANDIDATES counts moving feature points, NOT vehicles. Stationary trees/cars and textureless or very fast vehicles may have no arrows. A duck hop, shadows, animation, transitions or UI can generate false candidates. No persistent object IDs, vehicle labels, bounding boxes or collision footprints exist yet.

--speed 12 sets the minimum speed in PREVIEW pixels/second. Displacement must also exceed 2.5 preview pixels. Speeds are approximate: frame time uses the midpoint of each ADB capture call, not a device-provided capture timestamp. Frame intervals outside .02..1.5 seconds invalidate the reference. This does not solve the existing slow ADB screenshot rate.

The existing combined player/game-over preview is not integrated here. The search core is not called. This diagnostic is not sufficient to enable autonomous movement.

Validation: syntax compilation and six tests of the extracted NumPy camera/velocity functions succeeded in the assistant environment. OpenCV could not import there because libGL.so.1 was missing. Optical flow, GUI, ADB, end-to-end module imports and real-device behavior were NOT executed there. Run the supplied tests and preview locally.

Technique references (not copied source):
https://docs.opencv.org/4.1.2/d4/dee/tutorial_optical_flow.html
https://github.com/opencv/opencv/blob/4.x/samples/python/lk_track.py

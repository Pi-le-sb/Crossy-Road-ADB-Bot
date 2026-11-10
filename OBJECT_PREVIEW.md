# Actual object detection, independent of motion

The previous optical-flow groups are not a complete obstacle detector: stationary scenery, textureless objects and fast vehicles can be absent. This optional preview runs a locally supplied YOLO detector on each full frame, with no motion gate and no guessed class IDs. It prints the actual model class names and draws its predicted labeled boxes, including stationary objects ONLY IF the model learned those classes. It does not guarantee complete detection.

## Optional installation

Use a separate virtual environment if you want to keep current package versions unchanged.
python -m pip install -r requirements-vision.txt

## Weights candidate, not audited or bundled

The repository AmroAbdoh/Crossy-Road contains models/crossy_yolo.pt (6,227,818 bytes) at commit f8a5f6c94e0eb9916d3dd5f3e95b6f85528a7b72. Its detector.py calls Ultralytics YOLO. The model file was located but not loaded, benchmarked, audited or tested against this user's images. Its class coverage and accuracy have NOT been established. Do not use crossy_dqn3.pt as a detection model.

Pinned source page:
https://github.com/AmroAbdoh/Crossy-Road/blob/f8a5f6c94e0eb9916d3dd5f3e95b6f85528a7b72/models/crossy_yolo.pt

If you trust that source and have reviewed applicable model/dependency licenses, download the file manually onto your PC. Example Windows CMD command (only download; this does not load the model):
curl.exe --fail -L -o crossy_yolo.pt https://raw.githubusercontent.com/AmroAbdoh/Crossy-Road/f8a5f6c94e0eb9916d3dd5f3e95b6f85528a7b72/models/crossy_yolo.pt

Recorded Git blob SHA-1: acff3f01fb95382ca38c074237e449f8774d844c. This is NOT a raw-file SHA-1 or a security certification. This repository does not redistribute the weights or claim rights to relicense them. Third-party model loading, especially PyTorch checkpoints, requires trust and can carry code-execution risk. Do not load unknown weights in an environment containing secrets. --trust-weights is explicit acknowledgment, not sandboxing.

## Run after selecting trusted, compatible local weights

python object_preview.py --weights crossy_yolo.pt --trust-weights

To inspect a local original screenshot first, without ADB:
python object_preview.py --weights crossy_yolo.pt --trust-weights --image test_screenshot.png

The existing local profile is reused for player/game-over status without re-selection. If no profile exists, object detection still runs but state is UNKNOWN. Keep calibration.py, combined_preview.py, persistent_preview.py, motion_preview.py, candidate_tracking.py and profile_store.py because helpers are imported. Do not run main.py or other capture loops alongside it.

Default --imgsz 960 and CPU inference are starting settings, not benchmarked real-time performance. --imgsz 640 reduces inference resolution; --conf 0.15 displays lower-confidence predictions and can add false positives. Missing training classes cannot be recovered by confidence tuning. --compute 0 requests GPU inference only if your PyTorch/device setup supports it. No external inference server is used by this code. Framework installation, configuration/cache creation and optional backend dependencies may still use PC storage or network. The script includes no weight downloader and requires an existing local model path.

Detection boxes are not ground-contact polygons or true collision geometry. There is no automatic movement, restart, planner connection or vehicle-velocity tracking in this preview. The alwyntan search core remains separate; this preview does not replace it with the reference project's DQN.

No screenshots are saved on the phone. This script sets prediction image/text/crop saving to False and includes no direct image-writing or phone-input calls. Your calibration profile is only read.

Validation: Python syntax and static checks of no direct tap/swipe/image-save calls and disabled prediction save flags passed. No Ultralytics/PyTorch inference, model-loading compatibility, class accuracy, latency, GUI or ADB tests were run by the assistant. If loading fails, retain the complete error message; do not work around it by disabling model-loader safety checks.

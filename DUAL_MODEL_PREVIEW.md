# Two-model read-only preview

No weight merging or training. Both trusted local models evaluate the SAME captured frame,
sequentially. Original non-tree/rock classes stay visible in green. The specialist supplies
orange OBSTACLE boxes from tree/rock/stone aliases, regardless of the model-local class ID.
Old tree/rock detections from the original model are deliberately ignored to avoid mixing
its static-obstacle predictions with the specialist. Other original classes are preserved;
they are NOT all assumed to be vehicles or moving objects.

## Run

Use the same virtual environment that successfully ran the individual preview.

```cmd
.venv-training\Scripts\python.exe -m unittest -v test_dual_model_fusion
set "OBSTACLE_WEIGHTS=C:\path-to-your-trained-run\weights\best.pt"
.venv-training\Scripts\python.exe dual_model_preview.py --weights crossy_yolo.pt --obstacle-weights "%OBSTACLE_WEIGHTS%" --trust-weights --conf 0.25 --obstacle-conf 0.10 --imgsz 640 --compute cpu
```

Replace the example checkpoint path with your actual local file. --trust-weights trusts BOTH
checkpoints. No automatic downloads. Existing optional dependencies are unchanged.
--image local.jpg tests an existing local image instead of ADB. --device selects ADB device.
The saved profile is reused; no new calibration dialogs. No profile means UNKNOWN state,
not a failure of detection. Q/Esc exits.

Overlapping specialist boxes use confidence-ranked class-agnostic suppression at
--obstacle-iou 0.5. This is a heuristic: neighboring objects with highly overlapping boxes
can be merged. No cross-model confidence averaging and no suppression against vehicles.
Thresholds and screen-space rectangles do not establish collision geometry or traversability.

No taps, swipes, automatic restarts, screenshot/label saves, model modifications or uploads.
No tracking, movement prediction, grid occupancy or automatic play. Runtime includes both
models and capture; CPU responsiveness must be measured on the actual device/computer.
The single-model object_preview.py is unchanged.

Tests cover synthetic fusion results, name mappings, same-frame inputs, confidence separation
and disabled prediction saves. They do NOT test actual checkpoints, ADB, GUI, profile state,
real-scene accuracy or end-to-end speed.

.gitignore additionally excludes local training data, new screenshots and checkpoints.
Ignore rules do not remove files already tracked in Git. Review explicit file lists before push.

# Warning-light stop intent (no train-body class)

Implemented in dual_model_preview.py: original-model train_light_on detection at
--warning-conf 0.10 requests HALT_WARNING_LATCHED. A single accepted detection latches
HALT for the life of the process. Blinking, missing detections, GAME_OVER, long elapsed
time or a missing train box do NOT automatically clear it. Restarting the preview starts
a new latch, but does NOT establish a clear crossing.

IMPORTANT: This is integrated stop-intent logic in a READ-ONLY preview, not a functioning
autonomous controller. It sends no taps/swipes and cannot stop a separate running process.
The legacy main.py blind tap loop is unchanged and NOT guarded by this module. Do not use
it expecting this preview to stop it. No automatic jumping or automatic restart is added.

There is no train-body class requirement. There is also NO positive LIGHT_OFF/clear-track
observation. No warning detection therefore means UNKNOWN_NO_WARNING_DETECTED, not GO.
RailDecision.crossing_clear is always False: movement permission must never be inferred
from stop_requested=False. Future control integration must block unknown crossing states
and provide independent, validated clearance evidence before release. No automatic
release timer or manual keyboard reset masquerading as verified clearance is included.
A warning in any visible part of the screen triggers the global stop intent; lane matching
is not implemented. This can over-stop for unrelated tracks.

The warning class has its own extraction threshold. The original model is evaluated at
min(--conf, --warning-conf), then all other original-model classes are filtered back to
--conf. The obstacle specialist is unchanged. Signal detections are processed before
player exclusion and shown in red. The startup and periodic reports state the limitations.

Run the existing dual-model command; --warning-conf is optional. A lower confidence can
produce false stops and does NOT improve training. Existing poor warning-light recognition
remains unresolved: a missed warning may never latch HALT. More appropriate labeled examples
and real-device validation are still needed. No extra train class, training, data upload,
video-source change or scrcpy support is part of this patch.

```cmd
.venv-training\Scripts\python.exe -m unittest -v test_dual_model_fusion test_player_obstacle_filter test_rail_warning
```

Ten new tests cover synthetic stop decisions, missed-frame persistence, unknown/no-clear,
threshold isolation, update ordering and absence of input executor calls. They do not test
actual warning detection, ADB, models, GUI, timing, latency or physical/game collision behavior.
Only text files are committed; pictures, labels and model weights remain local.

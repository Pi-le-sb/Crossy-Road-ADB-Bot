# Player exclusion in the two-model preview

The existing saved player template is matched on the SAME frame as both YOLO predictions.
State detection now runs BEFORE obstacle rendering. No training, new calibration, file
uploads, screenshot saves or input events are introduced.

By default, only in PLAYER_VISIBLE state and template similarity >=0.90, a static obstacle
is removed if at least 85% of its rectangle lies inside the player template rectangle,
its center is inside that rectangle and its area is 0.35-1.6 times the player rectangle.
The player rectangle is converted from preview coordinates to original frame coordinates.
Only obstacle-group entries are removed: original-model objects/vehicles are never filtered.
Large overlapping trees and adjacent obstacles are deliberately retained by these rules.

This is a conservative heuristic, NOT proof of player identity. Template similarity is
not a calibrated probability. A nearby real obstacle can still be hidden if its geometry
satisfies these rules and the player template matches incorrectly. Visual checking is
required. No profile, low similarity, UNKNOWN or GAME_OVER means no player exclusion.
Do not use this preview as collision/path-planning ground truth.

Run your existing dual_model_preview.py command unchanged. The second status line reports
player-score, excluded count and filter status. --no-player-filter disables exclusion for
comparison. --player-filter-score changes the minimum template similarity (default 0.90).
No fixed screen-center mask and no whole-player-neighborhood masking is used.

```cmd
.venv-training\Scripts\python.exe -m unittest -v test_dual_model_fusion test_player_obstacle_filter
```

New tests cover synthetic geometry, original-object preservation, low/missing/invalid player
matches, game-over behavior, coordinate scaling and filter-before-render ordering. They do
not validate real template matching, actual models, ADB, GUI, latency or real-scene accuracy.
Both model files and the original single-model preview remain unchanged.

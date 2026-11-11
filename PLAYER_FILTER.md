# Player selection and missing-class diagnostics

This revision replaces the previous strict 0.90/85%-containment filter. It does not prove
that the user's unresolved live failure has been reproduced or fixed.

Player evidence, on the same frame:
- One original-model prediction named player/chicken/duck/character, confidence >=0.65,
  is preferred. Model-local class IDs are never assumed to mean player.
- Otherwise the saved template can supply the position at similarity >=0.70. The same
  configurable threshold is used for visible-state classification and template exclusion.
- Multiple original-model player candidates need template fallback; non-overlapping strong
  model/template positions cause PLAYER_SOURCES_DISAGREE and no exclusion.
- A detected restart button blocks both sources, including before GAME_OVER confirmation.

Only obstacle-group boxes are removed, never original-model objects. A candidate must have
its center inside the selected player box, IoU >=0.45 and area 0.35-2.2 times the player box.
This accepts moderately larger player detections that failed the former containment rule.
These are heuristics: real nearby obstacles can be hidden if mistaken player evidence and
geometry meet the rules. Template similarity and YOLO confidence are not averaged or treated
as equivalent probabilities. No tracking or verified identity is claimed. Check visually;
--no-player-filter remains available for comparison.

Use the existing dual-model launch command unchanged. --player-filter-score now defaults to
0.70 (template), --player-model-score defaults to 0.65 (original-model class prediction).
The display shows player source, both scores, excluded count and a reason. Every two seconds
the console reports the same diagnostics plus observed original-model class counts.
NO_PLAYER_LOCATION, AMBIGUOUS_PRIMARY, PLAYER_SOURCES_DISAGREE and NO_MATCHING_OBSTACLE_BOX
explain why the filter leaves a frame unchanged instead of hiding every central object.

Startup prints checkpoint paths, all declared classes and a small known-alias inventory for
player/train/log/turtle/coin/road/water/rail. Inventory means declared name availability ONLY;
false may also mean an unrecognized alias. All raw names are printed for that reason. No new
classes are trained, no third model is downloaded, and no terrain/path planning is added.
Other original-model predictions remain unfiltered; tree/rock still come from the specialist.

```cmd
.venv-training\Scripts\python.exe -m unittest -v test_dual_model_fusion test_player_obstacle_filter
```

Tests use synthetic detections and source-code checks, not actual checkpoints, saved templates,
ADB, GUI, live accuracy or performance. The runtime uncertainty requires live checking.
No calibration dialogs, input events, screenshot saves, label changes or weight changes.
Only source/test/documentation files belong in Git; user images and weights stay local.

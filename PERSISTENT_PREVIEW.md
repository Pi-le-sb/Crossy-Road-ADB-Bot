# One-time local calibration

First run: python persistent_preview.py --calibrate
Later: python persistent_preview.py
Storage tests: python -m unittest -v test_profile_store

Calibration asks for the whole restart button on the result screen, then asks you to manually start a round and select the duck. The profile contains only those two crops, the button rectangle and screen dimensions. It is stored as one compressed NPZ file under your PC home directory: .crossy-road-adb-bot/profile.npz. Existing profiles require typing YES to replace. --profile selects a different local path/device profile. NumPy loads with allow_pickle=False. Invalid input does not replace the saved profile; completed writes replace it atomically.

Normal runs load the profile without selection dialogs. Dying, manually restarting and starting the program again do not require calibration. No images are saved on the phone; no new profile files are created per round. Recalibrate if you change character, resolution/orientation, rendering scale or UI/theme. Template matching can still lose animations or mistake similar objects; persistence does not improve recognition accuracy by itself.

This is the NEW entry point. Older calibration.py, combined_preview.py and motion_preview.py are unchanged and still ask for selections. The new preview imports their helpers, so keep those files. Do not run old main.py in parallel. Q/Esc exits.

The combined preview retains PLAYER_VISIBLE, GAME_OVER and UNKNOWN. A visible player does not prove gameplay is running. Game over requires three consecutive button matches. Thresholds are currently 0.70 for player, 0.90 for button.

No tree/rock selection is used. Each frame pair estimates camera translation from spatially spread green scenery feature matches, excluding the previous duck box and upper/lower UI bands. It retries automatically if references are insufficient or inconsistent. MOTION_UNKNOWN is separate from player/game-over state and can persist indefinitely when no suitable scenery exists.

The green mask is a heuristic, not semantic segmentation: green cars, moving shadows or vegetation animation may contaminate it. Translation only; no camera rotation/zoom compensation. Arrows remain candidate feature motions, not identified vehicles, reliable world velocities or collision footprints. Sparse ADB snapshots can miss fast traffic. Automatic retry does not guarantee recovery.

No taps, swipes, automatic restart, planner calls or safe-move decisions are implemented here. This is still read-only diagnostics, not autonomous play. It does not save the old manual field grid because no grid-based collision model is used in this preview.

Validation before proposal: all three Python files compiled; five real NumPy profile-storage tests passed in the assistant environment. Live OpenCV, GUI, automatic camera inference, ADB and real-device behavior were not executed there (OpenCV unavailable due to missing libGL.so.1).

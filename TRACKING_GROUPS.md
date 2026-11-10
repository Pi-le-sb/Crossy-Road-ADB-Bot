# Tentative motion group tracking

Run: python persistent_preview.py
Tests: python -m unittest -v test_candidate_tracking
No recalibration or profile migration is needed. Existing local profiles are unchanged.

Nearby moving feature points with similar residual velocity are connected into groups (24 preview pixel neighborhood, 40 preview px/s speed tolerance, minimum three points). Each group receives a tentative ID. Greedy matching uses predicted screen position including estimated camera translation and a velocity-change gate. Two consecutive observations display TRACK; otherwise NEW. Neither label means a verified vehicle.

Boxes cover only grouped feature points plus four pixels. They are NOT full object extents, ground-contact polygons or collision bounds. Speed labels are approximate camera-compensated preview pixels per second, not world cells per second. Arrow length projects 0.25 seconds of motion. An unobserved track is retained internally for at most two frame pairs but is never drawn as a current detection. Unknown camera motion or player/game-over uncertainty resets tracks; recovery can create new IDs. IDs are not saved to disk.

Close vehicles may merge; one vehicle may split into groups. Crossing tracks, repetitive textures, shadows, animations and incorrect camera estimation may switch IDs or create false groups. Stationary/textureless/fast objects may be absent entirely. The algorithm does not identify cars, trains, logs, lanes or terrain and cannot infer safe passage. There is no search-core connection, input injection or automatic restart.

No new files are written on the phone or per round. Close older preview processes and main.py before testing. Q/Esc exits.

Validation: eight NumPy-only synthetic grouping/tracking tests passed in the assistant environment, including camera-compensated matching, missed tracks, expiry, reset and invalid data. The updated preview passed Python syntax compilation. OpenCV live rendering, ADB capture, actual round transitions and phone behavior were not executed there. This is a diagnostic milestone, not a complete autonomous bot.

# Source-reviewed search adaptation, not a complete game bot

Upstream: https://github.com/alwyntan/Crossy-Road-AI
Authors credited by upstream: Alwyn Tan, Sajana Weerawardhena, Nick Rubin.
Upstream README declares MIT licensing. This implementation independently translates the search structure; it does not copy the Unity implementation or assets into this repository.

Reviewed Git blob identifiers (not commit identifiers):
- Assets/Scripts/GameTreeAI.cs: 0d0a0243a74da14e45c1631cc889ae712d6f6699
- Assets/Scripts/GameState.cs: c61acbc2fcc31eb66ae2ae1ed32d36358c1cee32
- Assets/Scripts/PlayerControl.cs: d91d5d97eca77a8d44dcf88b0631ed6e778e37a2

## Mapping

GameTreeAI.recurseFunction -> GameTreeSearch.choose/visit. Player branches maximize over actions, then a single deterministic environment update occurs. Depth decreases after that environment update. There is no adversarial choice of vehicle motion and no alpha-beta pruning.

The death penalty (-99999), no-action leaf penalty (-1000), root-position retreat fallback and truncated lateral-column weighting follow the reviewed code. Equal best actions are selected randomly (optional reproducible seed). GameState.SetNextState moves dynamic obstacles using velocity times interval; that operation must be supplied by the environment adapter.

## Deliberate differences and limits

- Python search core, not C++, and not yet wired into combined_preview.py.
- Independent adapter states replace Unity collider cloning/backtracking. Input states must remain unchanged.
- An empty action list at a non-leaf returns -1000/None instead of indexing an empty list as upstream does.
- Argument validation, node counts and optional seeded random selection are additions.
- Python arithmetic does not emulate Unity float32 edge-case rounding.
- Unity overlap boxes, clipping, log transport, moving-object spawning, retreat bounds and actual available-move logic are NOT implemented by this module.
- PlayerControl's actual/custom-transform coupling is not reproduced; the adapter must simulate the hypothetical state consistently.
- No screenshots are processed by the search. No ADB calls or input events are issued.
- No unmeasured performance or real-device score claims are made.

## Tests

Run: python -m unittest -v test_alwyntan_search

Eight tests were executed successfully in the assistant's Python environment before this patch was proposed. The tests use only a small synthetic adapter. They are not differential tests against Unity, and they do not validate real-world perception, movement timing or collision geometry.

## Next integration requirement

The screenshot-to-state adapter must provide calibrated world coordinates, static blocking, cars/trains/logs with sizes and measured velocities, terrain/support and timestamps. Camera motion must be separated from object motion. Unknown or stale observations must inhibit phone inputs; PLAYER_VISIBLE alone does not authorize movement. The interval default is only an example, not a measured phone timing.

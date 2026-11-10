"""Search adapted from alwyntan/Crossy-Road-AI GameTreeAI.cs.
Not a Unity physics port or an autonomous phone controller.
The adapter must return independent simulation states, never issue ADB input.
"""
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Decision:
    value: int
    action: object
    nodes: int


def leaf_score(score, x, start_z, has_actions):
    if not has_actions:
        return -1000
    if score < int(start_z):
        return int(start_z)
    column = abs(int(x))
    return int(score) if column == 0 else int(int(score) / column)


class GameTreeSearch:
    """Adapter API: dead, clip, actions, move, advance, score, position.

    position(state) -> (x, z); score(state) -> integer forward distance.
    clip/move/advance must not mutate their input, including nested objects.
    advance(state, interval) advances all dynamic obstacles once.
    dead must include water/log support, bounds and all lethal colliders.
    actions must enforce static blocking and retreat limits; may include STAY.
    This module does not implement those environment/vision operations.
    """
    def __init__(self, adapter, depth=4, interval=.1, seed=None):
        if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= 8:
            raise ValueError('depth must be an integer from 1 to 8')
        if not 0 < interval < float('inf'):
            raise ValueError('interval must be finite and positive')
        self.adapter = adapter
        self.depth = depth
        self.interval = interval
        self.rng = random.Random(seed)

    def choose(self, state):
        a = self.adapter
        start_z = a.position(state)[1]
        nodes = 0
        def visit(current, depth, player_turn):
            nonlocal nodes
            nodes += 1
            if a.dead(current):
                return -99999, None
            current = a.clip(current)
            if a.dead(current):
                return -99999, None
            if depth == 0:
                return leaf_score(a.score(current), a.position(current)[0], start_z,
                                  bool(tuple(a.actions(current)))), None
            if not player_turn:
                value, _ = visit(a.advance(current, self.interval), depth - 1, True)
                return value, None
            actions = tuple(a.actions(current))
            if not actions:
                return -1000, None
            best = None
            tied = []
            for action in actions:
                value, _ = visit(a.move(current, action), depth, False)
                if best is None or value > best:
                    best, tied = value, [action]
                elif value == best:
                    tied.append(action)
            return best, self.rng.choice(tied)
        value, action = visit(state, self.depth, True)
        return Decision(value, action, nodes)

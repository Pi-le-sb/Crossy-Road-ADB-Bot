import unittest
from dataclasses import dataclass, replace
from alwyntan_search import GameTreeSearch, leaf_score


@dataclass(frozen=True)
class State:
    x: int = 0
    z: int = 0
    tick: int = 0
    dead: bool = False


class ToyAdapter:
    def dead(self, s): return s.dead
    def clip(self, s): return s
    def position(self, s): return s.x, s.z
    def score(self, s): return s.z
    def actions(self, s): return ('FRONT', 'STAY')
    def move(self, s, action): return replace(s, z=s.z+(action == 'FRONT'))
    def advance(self, s, interval): return replace(s, tick=s.tick+1)


class SearchTests(unittest.TestCase):
    def test_forward_and_no_mutation(self):
        s = State()
        result = GameTreeSearch(ToyAdapter(), depth=4, seed=0).choose(s)
        self.assertEqual((result.action, result.value), ('FRONT', 4))
        self.assertEqual(s, State())

    def test_dynamic_collision(self):
        class Traffic(ToyAdapter):
            def advance(self, s, interval):
                return replace(s, tick=s.tick+1, dead=s.z == 1)
        result = GameTreeSearch(Traffic(), depth=1).choose(State())
        self.assertEqual(result.action, 'STAY')

    def test_dead(self):
        r = GameTreeSearch(ToyAdapter()).choose(State(dead=True))
        self.assertEqual((r.value, r.action), (-99999, None))

    def test_death_after_clip(self):
        class Clipped(ToyAdapter):
            def clip(self, s): return replace(s, dead=True)
        self.assertEqual(GameTreeSearch(Clipped()).choose(State()).value, -99999)

    def test_no_actions(self):
        class Blocked(ToyAdapter):
            def actions(self, s): return ()
        r = GameTreeSearch(Blocked()).choose(State())
        self.assertEqual((r.value,r.action), (-1000,None))

    def test_leaf_rules(self):
        self.assertEqual(leaf_score(12,0,0,True),12)
        self.assertEqual(leaf_score(12,3,0,True),4)
        self.assertEqual(leaf_score(12,-3,0,True),4)
        self.assertEqual(leaf_score(2,3,5,True),5)
        self.assertEqual(leaf_score(12,0,0,False),-1000)

    def test_ties_repeatable(self):
        class Tied(ToyAdapter):
            def move(self,s,action): return s
        self.assertEqual(GameTreeSearch(Tied(),seed=4).choose(State()).action,
                         GameTreeSearch(Tied(),seed=4).choose(State()).action)

    def test_validation(self):
        for depth in (0,9,True,1.5):
            with self.assertRaises(ValueError): GameTreeSearch(ToyAdapter(),depth=depth)
        for interval in (0,-1,float('inf'),float('nan')):
            with self.assertRaises(ValueError): GameTreeSearch(ToyAdapter(),interval=interval)


if __name__ == '__main__':
    unittest.main()

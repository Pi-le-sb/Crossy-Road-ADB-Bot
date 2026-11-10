import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from player_obstacle_filter import exclude_player,player_box_in_frame


def obj(box,group='obstacle'):
    return SimpleNamespace(box=box,group=group)


class PlayerFilterTests(unittest.TestCase):
    def test_player_sized_obstacle_removed(self):
        self.assertEqual(exclude_player([obj((10,10,30,50))],(10,10,30,50),.95,'PLAYER_VISIBLE'),([],1))
    def test_neighbor_kept(self):
        obstacle=obj((32,10,52,50))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),.95,'PLAYER_VISIBLE'),([obstacle],0))
    def test_large_overlapping_tree_kept(self):
        obstacle=obj((5,0,40,60))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),.95,'PLAYER_VISIBLE'),([obstacle],0))
    def test_original_vehicle_kept(self):
        vehicle=obj((10,10,30,50),'primary')
        self.assertEqual(exclude_player([vehicle],(10,10,30,50),.95,'PLAYER_VISIBLE'),([vehicle],0))
    def test_weak_player_match_kept(self):
        obstacle=obj((10,10,30,50))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),.75,'PLAYER_VISIBLE'),([obstacle],0))
    def test_gameover_kept(self):
        obstacle=obj((10,10,30,50))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),.95,'GAME_OVER'),([obstacle],0))
    def test_no_profile_kept(self):
        obstacle=obj((10,10,30,50))
        self.assertEqual(exclude_player([obstacle],None,.95,'UNKNOWN'),([obstacle],0))
    def test_invalid_match_kept(self):
        obstacle=obj((10,10,30,50))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),float('nan'),'PLAYER_VISIBLE'),([obstacle],0))
    def test_invalid_player_geometry_kept(self):
        obstacle=obj((10,10,30,50))
        self.assertEqual(exclude_player([obstacle],(10,10,10,50),.95,'PLAYER_VISIBLE'),([obstacle],0))
    def test_small_fragment_kept(self):
        obstacle=obj((12,12,15,15))
        self.assertEqual(exclude_player([obstacle],(10,10,30,50),.95,'PLAYER_VISIBLE'),([obstacle],0))
    def test_coordinate_conversion(self):
        self.assertEqual(player_box_in_frame((10,20),(40,20,3),(960,540,3),(1920,1080,3)),(20,40,60,120))
    def test_filter_before_render(self):
        tree=ast.parse(Path(__file__).with_name('dual_model_preview.py').read_text(encoding='utf-8'))
        calls=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='exclude_player']
        drawing=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='obj']
        self.assertTrue(calls and drawing and calls[0]<drawing[0])

if __name__=='__main__':unittest.main()

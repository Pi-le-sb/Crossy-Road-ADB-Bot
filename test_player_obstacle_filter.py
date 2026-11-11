import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from player_obstacle_filter import exclude_player,player_box_in_frame,select_player,class_inventory


def obj(box,group='obstacle',name='tree',score=.8,source='obstacles'):
    return SimpleNamespace(box=box,group=group,name=name,confidence=score,source=source)


class PlayerFilterTests(unittest.TestCase):
    def test_geometry_cases(self):
        player=(10,10,30,50)
        for box,group,removed in [((10,10,30,50),'obstacle',1),((6,7,34,55),'obstacle',1),
             ((32,10,52,50),'obstacle',0),((5,0,40,60),'obstacle',0),
             ((12,12,15,15),'obstacle',0),((10,10,30,50),'primary',0)]:
            with self.subTest(box=box,group=group):self.assertEqual(exclude_player([obj(box,group)],player,.75,'PLAYER_VISIBLE')[1],removed)
    def test_invalid_or_unconfirmed_player(self):
        obstacle=obj((10,10,30,50))
        for box,score,state in [(None,.95,'UNKNOWN'),((10,10,30,50),.65,'PLAYER_VISIBLE'),
             ((10,10,30,50),float('nan'),'PLAYER_VISIBLE'),((10,10,10,50),.95,'PLAYER_VISIBLE'),
             ((10,10,30,50),.95,'GAME_OVER')]:
            with self.subTest(box=box,score=score,state=state):self.assertEqual(exclude_player([obstacle],box,score,state),([obstacle],0))
    def test_coordinate_conversion(self):
        self.assertEqual(player_box_in_frame((10,20),(40,20,3),(960,540,3),(1920,1080,3)),(20,40,60,120))
    def test_primary_player_priority(self):
        player=obj((10,10,30,50),'primary','chicken',.8,'primary')
        self.assertEqual(select_player([player],None,-1)[2],'PRIMARY_PLAYER')
    def test_model_local_id_not_used_to_guess_player(self):
        car=obj((10,10,30,50),'primary','car',.99,'primary')
        self.assertIsNone(select_player([car],None,-1)[0])
    def test_multiple_players_without_template_are_ambiguous(self):
        players=[obj((10,10,30,50),'primary','player',.9,'primary'),obj((50,50,70,90),'primary','player',.9,'primary')]
        self.assertEqual(select_player(players,None,-1)[2],'AMBIGUOUS_PRIMARY')
    def test_disagreeing_sources_are_not_masked(self):
        player=obj((10,10,30,50),'primary','duck',.9,'primary')
        self.assertEqual(select_player([player],(60,60,80,100),.9)[2],'PLAYER_SOURCES_DISAGREE')
    def test_template_fallback_uses_same_threshold(self):
        box=(10,10,30,50)
        self.assertEqual(select_player([],box,.75)[2],'TEMPLATE_PLAYER')
        self.assertEqual(exclude_player([obj(box)],box,.75,'PLAYER_VISIBLE')[1],1)
    def test_button_blocks_model_and_template(self):
        player=obj((10,10,30,50),'primary','player',.99,'primary')
        self.assertIsNone(select_player([player],player.box,.99,True)[0])
    def test_inventory_does_not_invent_classes(self):
        inventory=class_inventory({0:'car',1:'truck'})
        self.assertFalse(inventory['player']);self.assertFalse(inventory['train']);self.assertFalse(inventory['water'])
        self.assertTrue(class_inventory({0:'Train',1:'Logs',2:'Player'})['train'])
    def test_filter_before_render_and_threshold_default(self):
        tree=ast.parse(Path(__file__).with_name('dual_model_preview.py').read_text(encoding='utf-8'))
        calls=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='exclude_player']
        drawing=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='obj']
        self.assertTrue(calls and drawing and calls[0]<drawing[0])
        options=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='--player-filter-score']
        default=next(k.value.value for k in options[0].keywords if k.arg=='default')
        self.assertEqual(default,.70)

if __name__=='__main__':unittest.main()

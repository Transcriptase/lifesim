from nose.tools import *
import lifesim as ls
from random import choice


def test_cell_loc():
    c = ls.Node()
    c.set_location(1,3)
    eq_(c.x, 1)
    eq_(c.y, 3)
    
def test_map_init():
    m = ls.Grid(2,3)
    eq_(len(m.nodes), 3)
    eq_(len(m.nodes[0]), 2)
    ok_(isinstance(m.nodes[0][0], ls.Node))
    eq_(m.nodes[1][0].x, 0)
    eq_(m.nodes[2][1].y, 2)
    
def build_small_map():
    map = ls.Grid(10,10)
    for row in map.nodes:
        for node in row:
            node.make_plain()
    return map
    
def test_sm_map():
    m = build_small_map()
    eq_(len(m.nodes), 10)
    eq_(len(m.nodes[0]), 10)
    ok_(isinstance(m.nodes[9][9], ls.Node))
    eq_(m.nodes[5][2].plants.amount, 10)
    
def test_place_org():
    m = build_small_map()
    o = ls.Organism()
    eq_(m.nodes[5][7].occupants, [])
    o.set_location(m.nodes[5][7])
    eq_(o.location.x, 7)
    eq_(o.location.y, 5)
    eq_(m.nodes[5][7].occupants, [o])
    
def test_plant_init():
    n = ls.Node()
    n.make_plain()
    eq_(n.plants.amount, 10)
    eq_(n.plants.energy_density, 1)
    
def test_graze():
    n = ls.Node()
    n.make_plain()
    o = ls.Organism()
    o.location = n
    o.graze()
    eq_(n.plants.amount, 9)
    eq_(o.energy, 101)
    
def test_neighbors():
    m = build_small_map()
    n1 = m.get_node(5,5)
    eq_(len(m.neighbors(n1)), 8)
    n2 = m.get_node(0,3)
    eq_(len(m.neighbors(n2)), 5)
    n3 = m.get_node(9,9)
    eq_(len(m.neighbors(n3)), 3)
    
def test_dist():
    m = build_small_map()
    n1 = m.get_node(3,3)
    n2 = m.get_node(6, 7)
    eq_(m.dist(n1, n2), 5)
    
def test_pf():
    o = ls.Organism()
    m = build_small_map()
    o.set_location(m.get_node(3,3))
    p = o.pathfind(m.get_node(5,6), m)
    ok_(p)
    ok_(isinstance(p.next(), ls.Node))
    

    
class TestVis(object):
    def setup(self):
        self.m = build_small_map()
        for row in self.m.nodes:
            for node in row:
                node.set_plants(choice(range(10)), 1, 10)
        self.v = ls.Visualizer(self.m)
        for i in range(30):
            new_o = ls.Organism()
            new_o.set_location(self.m.get_node(
                choice(range(10)),
                choice(range(10))
                )
            )
            
        
    def test_grid(self):
        self.v.draw_grid()
        
    def test_set_bg(self):
        n = ls.Node()
        n.set_plants(10, 1, 10)
        eq_(self.v.set_bg(n), self.v.YL_GN[7])
        n2 = ls.Node()
        n2.set_plants(0, 1, 10)
        eq_(self.v.set_bg(n2), self.v.YL_GN[0])
        n2.set_plants(4, 1, 10)
        eq_(self.v.set_bg(n2), self.v.YL_GN[2])
        
    def test_color(self):
        self.v.fill_grid()
        
#    def test_full(self):
#        self.v.run()
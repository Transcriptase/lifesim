from nose.tools import *
import lifesim as ls
from random import choice


class TestNode(object):
    def setup(self):
        self.n = ls.Node(1, 1)
        
    def test_plant_init(self):
        self.n.make_plain()
        eq_(self.n.plants.amount, 10)
        eq_(self.n.plants.energy_density, 1)
        
def build_small_map():
    map = ls.Grid(10,10)
    for row in map.nodes:
        for node in row:
            node.make_plain()
    return map
    
def build_desert():
    d = ls.Grid(10, 10)
    for row in d.nodes:
        for node in row:
            node.set_plants(0, 1, 10)
    return d
    
def build_rand_map():
    r = ls.Grid(10, 10)
    for row in r.nodes:
        for node in row:
            node.set_plants(choice(range(10)), 1, 10)
    return r
        
class TestGrid(object):
    def setup(self):
        self.m = build_small_map()
    
    def test_map_init(self):
        m1 = ls.Grid(2,3)
        eq_(len(m1.nodes), 3)
        eq_(len(m1.nodes[0]), 2)
        ok_(isinstance(m1.nodes[0][0], ls.Node))
        eq_(m1.nodes[1][0].x, 0)
        eq_(m1.nodes[2][1].y, 2)
    
    def test_sm_map(self):
        eq_(len(self.m.nodes), 10)
        eq_(len(self.m.nodes[0]), 10)
        ok_(isinstance(self.m.nodes[9][9], ls.Node))
        eq_(self.m.nodes[5][2].plants.amount, 10)
    

    def test_neighbors(self):
        n1 = self.m.get_node(5,5)
        eq_(len(self.m.neighbors(n1)), 8)
        n2 = self.m.get_node(0,3)
        eq_(len(self.m.neighbors(n2)), 5)
        n3 = self.m.get_node(9,9)
        eq_(len(self.m.neighbors(n3)), 3)
    
    def test_dist(self):
        n1 = self.m.get_node(3,3)
        n2 = self.m.get_node(6, 7)
        eq_(self.m.dist(n1, n2), 5)
    
    
class TestOrg(object):
    def setup(self):
        self.m = build_small_map()
        self.o = ls.Organism(self.m)
        
        #build an empty map with 1 plant in it
        self.d = build_desert()
        self.d.get_node(3, 3).set_plants(1, 1, 10)
        self.d_o = ls.Organism(self.d)
        
    def test_init(self):
        ok_(self.o in self.m.organisms)
        
    def test_graze(self):
        n = self.m.get_node(1, 1)
        self.o.location = n
        self.o.graze()
        eq_(n.plants.amount, 9)
        eq_(self.o.energy, 101)
        
    def test_place_org(self):
        eq_(self.m.nodes[5][7].occupants, [])
        self.o.set_location(self.m.nodes[5][7])
        eq_(self.o.location.x, 7)
        eq_(self.o.location.y, 5)
        eq_(self.m.nodes[5][7].occupants, [self.o])
    
    def test_pf(self):
        self.o.set_location(self.m.get_node(3,3))
        p = self.o.pathfind(self.m.get_node(5,6))
        ok_(p)
        ok_(isinstance(p.next(), ls.Node))
        
    def test_see(self):
        self.o.set_location(self.m.get_node(3, 3))
        eq_(len(self.o.can_see()), 25)
        for i in range(1, 5):
            for j in range(1, 5):
                ok_(self.m.get_node(i, j) in self.o.can_see())
        self.o.set_location(self.m.get_node(9, 9))
        eq_(len(self.o.can_see()), 9)
        
    def test_find_plants(self):
        self.d_o.set_location(self.d_o.grid.get_node(5, 5))
        ok_(self.d_o.find_plants())
        eq_(self.d_o.find_plants(), self.d.get_node(3, 3))
        self.d_o.set_location(self.d_o.grid.get_node(9, 9))
        ok_(not self.d_o.find_plants())
        
    def test_move(self):
        self.o.set_location(self.o.grid.get_node(3, 3))
        self.o.goal = self.o.grid.get_node(6, 6)
        self.o.path = self.o.pathfind(self.o.goal)
        energy = 100
        eq_(self.o.energy, energy)
        for i in range(3, 7):
            self.o.move()
            energy -= 1
            eq_(self.o.location, self.o.grid.get_node(i, i))
            eq_(self.o.energy, energy)
        self.o.move()
        ok_(not self.o.path, not self.o.goal)

    def test_decide(self):
        #TODO: It shouldn't take a whole tick to decide to start moving
        #or to realize it's at the goal. Move that check outside of move().
        self.d_o.energy = 20
        self.d_o.set_location(self.d_o.grid.get_node(5, 5))
        #no path yet
        ok_(not self.d_o.path)
        self.d_o.decide()
        #decides to forage, finds the food at 3, 3, gets a goal and a path
        ok_(self.d_o.path)
        eq_(self.d_o.goal, self.d_o.grid.get_node(3, 3))
        eq_(self.d_o.energy, 20)
        self.d_o.decide()
        #now has a path, calls move(), but first node in path is the current one
        #but energy cost is charged (this is a double charge, fix)
        eq_(self.d_o.location, self.d_o.grid.get_node(5, 5))
        eq_(self.d_o.energy, 19)
        self.d_o.decide()
        #moves to next node on path
        eq_(self.d_o.location, self.d_o.grid.get_node(4, 4))
        self.d_o.decide()
        #moves to next node on path, which is the goal
        eq_(self.d_o.location, self.d_o.grid.get_node(3, 3))
        eq_(self.d_o.energy, 17)
        eq_(self.d_o.location.plants.amount, 1)
        self.d_o.decide()
        #still calls move(), finds it's at the end
        eq_(self.d_o.location, self.d_o.grid.get_node(3, 3))
        self.d_o.decide()
        #grazes
        eq_(self.d_o.location, self.d_o.grid.get_node(3, 3))        
        eq_(self.d_o.energy, 18)
        eq_(self.d_o.location.plants.amount, 0)
        ok_(not self.d_o.path, not self.d_o.goal)
        
        

def rand_pop(grid, animals):
    for i in range(animals):
        new_o = ls.Organism(grid)
        new_o.set_location(choice(
            choice(grid.nodes)
            )
        )
    
class TestVis(object):
    def setup(self):
        self.m = build_rand_map()
        rand_pop(self.m, 30)
        self.v = ls.Visualizer(self.m)
        
        self.d = build_desert()
        rand_pop(self.d, 10)
        for org in self.d.organisms:
            org.energy = 20
        for i in range(20):
            choice(choice(self.d.nodes)).set_plants(10, 1, 10)
        self.v_d = ls.Visualizer(self.d)
            
        
    def test_grid(self):
        self.v.draw_grid()
        
    def test_set_bg(self):
        n = ls.Node(1, 1)
        n.set_plants(10, 1, 10)
        eq_(self.v.set_bg(n), self.v.YL_GN[7])
        n2 = ls.Node(2, 2)
        n2.set_plants(0, 1, 10)
        eq_(self.v.set_bg(n2), self.v.YL_GN[0])
        n2.set_plants(4, 1, 10)
        eq_(self.v.set_bg(n2), self.v.YL_GN[2])
        
    def test_color(self):
        self.v.fill_grid()
        
    def test_d(self):
        self.v_d.run()
        
#    def test_full(self):
 #      self.v.run()
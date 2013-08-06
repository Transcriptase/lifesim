from math import sqrt
import pathfinder
import pygame
import sys

class Node(object):
    '''
    A single location on a map grid.
    '''
    def __init__(self):
        self.occupants = []
        self.move_cost = 1
    
    def set_location(self, x, y):
        self.x = x
        self.y = y
        
    def set_plants(self, amount, energy_density, veg_max):
        self.plants = Vegetation(amount, energy_density, veg_max)
        
    def make_plain(self):
        self.set_plants(10, 1, 10)
        
        
class Grid(object):
        '''
        A cartesian grid of nodes, stored as a list of lists
        '''
        def __init__(self, x, y):
            '''
            Note that this construction method means that the
            y coordinate comes first when calling directly from
            the map matrix.
            
            To avoid confusion, use get_node(x, y) instead of
            raw indexing.
            '''
            self.nodes = []
            for j in range(y):
                self.nodes.append([])
                for i in range(x):
                    new_node = Node()
                    new_node.set_location(i, j)
                    self.nodes[j].append(new_node)
                    
        def get_node(self, x, y):
            return self.nodes[y][x]
            
        def dist(self, start, end):
            h = sqrt((abs(start.x - end.x) **2) + (abs(start.y - end.y) ** 2))
            return h
            
        def move_cost(self, start, end):
            return end.move_cost
            
        def neighbors(self, node):
            neighbors = []
            deltas = [-1, 0, 1]
            for delta in deltas:
                new_x = node.x + delta
                for delta in deltas:
                    new_y = node.y + delta
                    if (new_x in range(len(self.nodes)) and
                        new_y in range(len(self.nodes[0]))
                    ):
                        new_node = self.get_node(new_x, new_y)
                        if new_node != node:
                            neighbors.append(new_node)
            return neighbors
                    
class Vegetation(object):
    '''
    Hold information about plants in a node
    '''
    def __init__(self, amount, energy_density, veg_max):
        self.amount = amount
        self.energy_density = energy_density
        self.veg_max = veg_max
        
                    
class Organism(object):
    '''
    Base class for all organisms
    '''
    def __init__(self):
        self.energy = 100
        self.bitesize = 1
    
    def set_location(self, node):
        self.location = node
        node.occupants.append(self)
        
    def pathfind(self, goal, map):
        '''
        A* pathfinding to goal
        '''
        pf = pathfinder.PathFinder(map.neighbors,
                                    map.move_cost,
                                    map.dist)
        p = pf.compute_path(self.location, goal)
        return p
                
        
    def graze(self):
        self.location.plants.amount -= self.bitesize
        self.energy += self.location.plants.energy_density * self.bitesize

class Visualizer(object):
    '''
    Uses pygame to graphically represent a Grid.
    '''
    WINDOWWIDTH, WINDOWHEIGHT = 800, 800
    
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    DK_GREY = (40, 40, 40)
    YL_GN = [(255, 255, 229),
            (247, 252, 185),
            (217, 240, 163),
            (173, 221, 142),
            (120, 198, 121),
            (65, 171, 93),
            (35, 132, 67),
            (0, 90, 50)]

    def __init__(self, grid):
        '''
        Create a new visualization.
        
        grid:
            The Grid object to be visualized.
        '''
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WINDOWWIDTH, self.WINDOWHEIGHT))
        
        self.grid = grid        
        self.grid_width = self.WINDOWWIDTH / len(grid.nodes[0])
        self.grid_height = self.WINDOWHEIGHT / len(grid.nodes)
        
        self.font = pygame.font.Font(None, 36)
        
    def draw_grid(self):
        for x in range(0, self.WINDOWWIDTH, self.grid_width):
            pygame.draw.line(
                self.screen,
                self.DK_GREY,
                (x, 0),
                (x, self.WINDOWHEIGHT)
                )
        for y in range(0, self.WINDOWHEIGHT, self.grid_height):
            pygame.draw.line(
                self.screen,
                self.DK_GREY,
                (0,y),
                (self.WINDOWWIDTH, y))
                
    def fill_grid(self):
        for row in self.grid.nodes:
            for node in row:
                draw_x = node.x * self.grid_width
                draw_y = node.y * self.grid_height
                color = self.set_bg(node)
                draw_node = pygame.Rect(
                    (draw_x, draw_y, self.grid_width, self.grid_height))
                pygame.draw.rect(self.screen, color, draw_node)
                if node.occupants:
                    text = self.font.render(str(len(node.occupants)), 1, self.BLACK)
                    text_pos = text.get_rect()
                    text_pos.centerx = draw_node.centerx
                    text_pos.centery = draw_node.centery
                    self.screen.blit(text, text_pos)

    def set_bg(self, node):
        pct_veg = float(node.plants.amount)/float(node.plants.veg_max)
        scaled = int(pct_veg * (len(self.YL_GN) - 1))
        return self.YL_GN[scaled]
                            
    def draw(self):
        self.fill_grid()
        self.draw_grid()

            
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.draw()
            pygame.display.update()    
        
    
    
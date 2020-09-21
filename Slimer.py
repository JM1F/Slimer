import pygame as pg
import math
import random
from collections import *
import heapq
import sys
import os

# // Libary imports //

WIDTH = 1024   
HEIGHT = 768  
vector = pg.math.Vector2

TILESIZE = 64

GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

PLAYERVELOCITY = 5
# // Globals //


class PriorityQueue:
    # Priority queue initialize
    def __init__(self):
        self.nodes = []
    def put(self, node, cost):
        # Put an item into the Queue
        heapq.heappush(self.nodes, (cost, node))
    def get(self):
        # Return the item in slot one and pop it
        return heapq.heappop(self.nodes)[1]
    def empty(self):
        # Returns true of false 
        return len(self.nodes) == 0
    
class Wall(pg.sprite.Sprite):
    # Initialize wall with x and y coordinate and the image
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pg.Rect(x, y, 64, 64)
        self.x = x
        self.y = y
    
class Door(pg.sprite.Sprite):
    def __init__(self, x, y, image, doordirection):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        #  Makes sure that the door in placed on the
        #  outer edge with
        #  the right hitbox for the four different directions. 
        if doordirection == 1 or doordirection == 2:
            self.rect = pg.Rect(x, y, 32, 128)
        if doordirection == 3 or doordirection == 4:
            self.rect = pg.Rect(x, y, 128, 32)
        self.x = x
        self.y = y

class ClosedDoor(pg.sprite.Sprite):
    def __init__(self, x, y, image, doordirection):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        # Makes sure that the door in placed on the
        # outer edge with
        # the right hitbox for the four different directions. 
        if doordirection == 1 or doordirection == 2:
            self.rect = pg.Rect(x, y, 32, 128)
        if doordirection == 3 or doordirection == 4:
            self.rect = pg.Rect(x, y, 128, 16)
        self.x = x
        self.y = y


class Projectile(pg.sprite.Sprite):
    def __init__(self, startposx, startposy, endposx, endposy, velocity, screen, projtype):
        pg.sprite.Sprite.__init__(self)
        # Checks what type of projectile
        if projtype == 1:
            self.image = pg.image.load("Projectile.png")
        if projtype == 2:
            self.image = pg.image.load("orb_red.png")
        self.rect = self.image.get_rect()
        self.x = startposx
        self.y = startposy
        self.endx = endposx
        self.endy = endposy
        self.screen = screen
        # Create x and y vectors for projectiles
        self.difx = self.x - self.endx 
        self.dify = self.y - self.endy 
        self.vel = velocity
        
    def update(self):
        # Calls the off screen check which just checks if the hitbox of
        # the projectiles go off screen, if so, they are terminated
        if self.OffScreencheck() == True:
            self.kill()
            print("Killed")
        # Creating the hypotenuse vector equalling to the distance    
        self.dist = math.hypot(self.difx, self.dify)
        try:
            # Calculate the velocity
            self.vx = (self.difx / self.dist) * self.vel
            self.vy = (self.dify / self.dist) * self.vel
            # Move the projectile taking away the velocity each time
            self.x -= self.vx
            self.y -= self.vy
            self.rect.center = (self.x, self.y)
        except ZeroDivisionError:
            #Except statment to catch a zero
            #error in the case that
            #self.distance is equal to zero.
            self.kill()    
    def OffScreencheck(self):
        # Check to see if the projectile is off screen
        if (self.rect[0] + 16) < 0 or self.rect[0] > WIDTH or (self.rect[1] + 16) < 0 or self.rect[1] > HEIGHT:
            return True
        else:
            return

class Enemy(pg.sprite.Sprite):
    def __init__(self, map, startposx, startposy, health = 60):
        pg.sprite.Sprite.__init__(self)        
        self.imgindex = []
        # Initalizing all images
        self.imgindex.append(pg.image.load("emain1.png").convert_alpha())  
        self.imgindex.append(pg.image.load("emain2.png").convert_alpha())
        self.imgindex.append(pg.image.load("emain3.png").convert_alpha()) 
        self.imgindex.append(pg.image.load("emain4.png").convert_alpha())  
        self.imgindex.append(pg.image.load("emain5.png").convert_alpha())  
        self.imgindex.append(pg.image.load("emain6.png").convert_alpha())  
        self.imgindex.append(pg.image.load("emain7.png").convert_alpha())  
        self.imgindex.append(pg.image.load("emain8.png").convert_alpha())          
        
        self.vx, self.vy = 0, 0
        self.index = 0
        self.room = map
        self.image = self.imgindex[self.index]
        self.timer = 0
        self.rect = self.image.get_rect()
        self.rect.x = startposx
        self.health = health
        self.rect.y = startposy
        self.center = self.rect.center
        # Setting the speed of the enemy 
        self.enemy_speed = 4
        self.hitbox_rect = pg.Rect(startposx, startposy, 60,60)
        
    def getCenter(self):
        # Returns enemy sprites center
        self.center = self.rect.center
        return self.center
    
    def update(self, proj_group, playercenter, node, wall_group, itemnode, specialitem):
        self.goal = node
        # Checks to see if the enemies health is at zero, then
        # the object is deleted with the .kill() command
        if self.health == 0:
            self.kill()
            return True
        # Returns the node that the enemy is in
        self.currentnode = self.get_node()
        
        if itemnode == 1:
            # Breadth first search
            self.path = breadthfirst_search(self.room,specialitem, self.currentnode)   
        else:
            # A star search
            self.path = aStar(self.room,self.goal, self.currentnode)

        if self.currentnode != False:
            
            # Checks to see if the current node is on the goal node
            if self.currentnode != self.goal:
                try:
                    # Add the current node to the next node in the list.
                    self.current = self.currentnode + self.path[(self.currentnode)]
                except:
                    # Do nothing
                    pass
                # Pass the current node into a back-up node for other
                # iteratons
                self.backup = self.currentnode         
        else:
            # Checks to see if the current node is the goal node
            if self.currentnode != self.goal:
                try:      
                    self.current = self.backup + self.path[(self.backup)]
                except:
                    pass
                
        if self.currentnode == False:
            pass
        else:
            # Works out the directional vector
            self.dif = self.currentnode - self.current
            
        # Checking what direction the next path is      
        if self.dif == [1, 0]:
            self.rect.x -= self.enemy_speed
        elif self.dif == [-1, 0]:
            self.rect.x += self.enemy_speed
        elif self.dif == [0, 1]:
            self.rect.y -= self.enemy_speed
        elif self.dif == [0, -1]:
            self.rect.y += self.enemy_speed
        # Checks to see if the enemy gets hit by a projectile
        # and takes away 10 health
        if pg.sprite.spritecollide(self, proj_group, True):
            self.health = self.health - 10
        self.rect = self.hitbox_rect
        self.playercenter = playercenter
        # Rotate towards player procedure
        self.rotatetowardsPlayer()
        self.random_timer = random.randint(2, 5)
        self.timer += self.random_timer
        # This is where you a able to adjust the
        # animation time, for the cycles of the pictures.
        if (self.timer % 20) == 0:
            self.index += 1
            if self.index >= len(self.imgindex):
                self.index = 0
            self.image = self.imgindex[self.index]
        
    # Rotates the enemy to look towards the player                    
    def rotatetowardsPlayer(self):
        self.angle_vec = math.atan2((self.center[0] - self.playercenter[0]),(self.center[1] - self.playercenter[1]))
        # The angle is converted from radians to degrees
        self.angle = math.degrees(self.angle_vec)
        # Rotates the image about an angle
        self.newimage = pg.transform.rotate(self.image, self.angle - 180)
        oldcenter = self.rect.center
        self.newrect = self.newimage.get_rect()
        self.newrect.center = oldcenter
 
    def get_node(self):
        # Need to be set to False again for
        # when the procedure is called again in the update section
        self.iny = False 
        self.inx = False         
        self.playercenter = self.getCenter()
        for i in range(0, WIDTH, TILESIZE):
            # Checking if the player's center "x"
            # coordinate is between a tile's area coordinates
            if i == self.rect.x and (i + 64) == (self.rect.x + 64) :
                self.coordx = i
                self.inx = True
                
        for j in range(0, HEIGHT, TILESIZE):
            if j == self.rect.y and (j + 64) == (self.rect.y + 64) :
                self.coordy = j
                self.iny = True
        # Searching through the tile list and
        # mapping out what tile the player's center is in       
        if self.iny == True and self.inx == True: 
            # dividing the x and y coordinates
            # by 64 and minusing 1 to get into list form
            x = int(self.coordx / 64)
            y = int(self.coordy / 64)
            
            return (x, y)
        return False

    def draw(self):
        self.screen = maingame.returnGameScreen()
        if self.health == 0:
            return True
        # Only draws to the screen if the health is 0
        else:
            try:
                self.screen.blit(self.newimage, self.newrect)
            except:
                self.screen.blit(self.image, self.rect)
             
class Item(pg.sprite.Sprite):
    def __init__(self, startposx, startposy, item_number):
        # initalizing item sprite
        pg.sprite.Sprite.__init__(self)
        # Assigning items to the correct image
        if item_number == 1:
            self.image = pg.image.load("item1.png")
        if item_number == 2:
            self.image = pg.image.load("orb_green.png")  
        self.rect = pg.Rect((startposx + 16), (startposy + 16), 32, 32)
        self.x = startposx
        self.y = startposy
        
class PlayerSprite(pg.sprite.Sprite):
    def __init__(self, startposx, startposy, health = 100):
        pg.sprite.Sprite.__init__(self)
        
        self.imgindex = []
        # Loading all animation images
        self.imgindex.append(pg.image.load("main1.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main3.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main4.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main5.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main6.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main7.png").convert_alpha())  
        self.imgindex.append(pg.image.load("main8.png").convert_alpha())  
        self.index = 0
        self.health = health
        self.image = self.imgindex[self.index]
        self.timer = 0
        self.pos = vector(startposx, startposy) * TILESIZE
        self.rect = self.image.get_rect()
        self.center = self.rect.center
        self.hitbox_rect = pg.Rect(startposx, startposy, 60,60)
        self.original_image = self.image.copy()
        self.vx, self.vy = 0, 0
        self.rect.x = startposx
        self.rect.y = startposy
        self.hittimer = 0
        self.boss_hittimer = 0
        
    def keys(self):
        # Key logging what direction the player is moving
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.vy = -PLAYERVELOCITY
        if keys[pg.K_a]:
            self.vx = -PLAYERVELOCITY
        if keys[pg.K_s]:
            self.vy = PLAYERVELOCITY
        if keys[pg.K_d]:
            self.vx = PLAYERVELOCITY
  
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071
       
    def rotate(self):
        # The player rotates to face the mouse
        self.mousex, self.mousey = pg.mouse.get_pos()
        self.PLAYERCENTER = self.center
        self.angle_vec = math.atan2((self.mousex - self.PLAYERCENTER[0]),(self.mousey - self.PLAYERCENTER[1]))
        self.angle = math.degrees(self.angle_vec)
        # Rotate the image
        self.newimage = pg.transform.rotate(self.image, self.angle)
        oldcenter = self.rect.center
        self.newrect = self.newimage.get_rect()
        self.newrect.center = oldcenter
    
    def draw(self):
        self.screen = maingame.returnGameScreen()
        self.percentage = self.health / 100
        xcoord = self.percentage * 416
        # If the boss is not in that room draw the health bar at
        # the bottom
        if self.boss == None:
            if self.health >= 0:
                pg.draw.rect(self.screen,(0, 0, 0),[16, (HEIGHT -48), 416, 42])
                pg.draw.rect(self.screen,(95, 99, 88),[20,(HEIGHT -48), 416, 38])
                pg.draw.rect(self.screen,(227, 2, 43),[20,(HEIGHT -48), xcoord, 38])
        # If in the bossroom the health bar is raised up
        else:
            if self.health >= 0:
                pg.draw.rect(self.screen,(0, 0, 0),[70, (HEIGHT -112), 416, 42])
                pg.draw.rect(self.screen,(95, 99, 88),[74,(HEIGHT -112), 416, 38])
                pg.draw.rect(self.screen,(227, 2, 43),[74,(HEIGHT -112), xcoord, 38])
            
        self.screen.blit(self.newimage, self.newrect)
        
            
    def update(self, wall_group, closeddoor_group, closedEdoor_group, doors_group, Edoors_group, enemies, items, boss_projectiles,boss):
        self.rect = self.hitbox_rect
        self.boss = boss
        self.keys()
        self.rotate()
        # Move player in the x coordinate
        self.rect.x += self.vx
        # - Collisions -
        # Checks to see if the player can pick up a health pack
        if self.health != 100:
            # When collided +10 health is gained
            if pg.sprite.spritecollide(self, items, True):
                self.health += 10
        # Enemy collision between player
        collision =  pg.sprite.spritecollide(self, enemies, False)
        
        if collision:
            # If the hit timer MOD 100 is 0 then take off 10 health
            if (self.hittimer % 100) == 0 and self.hittimer != 0:
                self.health = self.health - 10
            # Takes off 10 health as soon as the hitboxes connect.    
            if self.hittimer == 0:    
                self.health = self.health - 10
                
            self.hittimer += 1 
        else:
            self.hittimer = 0
        # Checks to see if it's the boss room, by checking if the
        # boss object is created
        if boss != None:    
            boss_collision =  pg.sprite.spritecollide(self, boss, False)
            
            if boss_collision:
                # If the hit timer MOD 100 is 0 then take
                # off 25 health
                if (self.boss_hittimer % 100) == 0 and self.boss_hittimer != 0:
                    self.health = self.health - 25
                # Takes off 25 health as soon as the
                # hitboxes connect.     
                if self.boss_hittimer == 0:    
                    self.health = self.health - 25
                    
                self.boss_hittimer += 1 
            else:
                self.boss_hittimer = 0
            # Checks to see if the projectiles of the boss hits the
            # player and takes off 15 health 
            if pg.sprite.spritecollide(self, boss_projectiles, True):
                self.health = self.health - 15
        # Delete the object the player if the health falls below 0       
        if self.health <= 0:
            self.kill()
            return True
        # Collisions for the walls in the map
        self.collisionlist = pg.sprite.spritecollide(self, wall_group, False) 
        for collided in self.collisionlist:
            # Checks to see is the velocity is greather than 0
            # in the X plane
            if self.vx > 0:
                self.rect.right = collided.rect.left 
            else:
                self.rect.left = collided.rect.right
        # Colissions for the closed doors on the map
        self.collisionlist2 = pg.sprite.spritecollide(self, closeddoor_group, False)
        
        for collided in self.collisionlist2:
            if self.vx > 0:
                self.rect.right = collided.rect.left 
            else:
                self.rect.left = collided.rect.right 
        # Collision for the close Exit doors on the map
        self.collisionlist3 = pg.sprite.spritecollide(self, closedEdoor_group, False)
        for collided in self.collisionlist3:
            if self.vx > 0:
                self.rect.right = collided.rect.left 
            else:
                self.rect.left = collided.rect.right 
        # Move player in the y coordinate
        self.rect.y += self.vy
        # Collisions for the walls in the map
        self.collisionlist = pg.sprite.spritecollide(self, wall_group, False)
        for collided in self.collisionlist:
            # Checks to see is the velocity is greather than 0
            # in the Y plane
            if self.vy > 0:
                self.rect.bottom = collided.rect.top
            else:
                self.rect.top = collided.rect.bottom
        # Colissions for the closed doors on the map
        self.collisionlist2 = pg.sprite.spritecollide(self, closeddoor_group, False)
        for collided in self.collisionlist2:
            if self.vy > 0:
                self.rect.bottom = collided.rect.top
            else:
                self.rect.top = collided.rect.bottom
        # Collision for the close Exit doors on the map for the "y" axis        
        self.collisionlist3 = pg.sprite.spritecollide(self, closedEdoor_group, False)
        for collided in self.collisionlist3:
            if self.vy > 0:
                self.rect.bottom = collided.rect.top
            else:
                self.rect.top = collided.rect.bottom

        # Collision for the open doors on the map     
        self.doorcollisionlist = pg.sprite.spritecollide(self, doors_group, False)
        if len(self.doorcollisionlist) > 0:
            return 1
        # Collision for the Exit open doors on the map, returns 2 when collided
        self.doorlist = pg.sprite.spritecollide(self, Edoors_group, False)
        if len(self.doorlist) > 0:
            return 2
        
        
        self.timer += 4
        # This is where you a able to adjust the
        # animation time, for the cycles of the pictures.
        if (self.timer % 20) == 0:
        
            self.index += 1
            if self.index >= len(self.imgindex):
                self.index = 0
            self.image = self.imgindex[self.index]
         
    def LoadInto_OldMap(self, doordirection):
        # check to see the door direction the load
        # in to the coordinates 
        if doordirection == 1:
            self.rect.x = (WIDTH - 144)
            self.rect.y = (352)
        elif doordirection == 2:
            self.rect.x = (64)
            self.rect.y = (352)
        elif doordirection == 3:
            self.rect.x = (480)
            self.rect.y = (64)
        elif doordirection == 4:
            self.rect.x = (512 - 32)
            self.rect.y = (HEIGHT - 144)
   
    def LoadInto_NewMap(self, doordirection):
        # check to see the door direction the load
        # in to the coordinates 
        if doordirection == 1:
            self.rect.x = (64)
            self.rect.y = (352)
        elif doordirection == 2:
            self.rect.x = (WIDTH - 144)
            self.rect.y = (352)
        elif doordirection == 3:
            self.rect.x = (512 - 32)
            self.rect.y = (HEIGHT - 144)
        elif doordirection == 4:
            self.rect.x = (512 - 32)
            self.rect.y = (64)
        
    def getCenter(self):
        # Return the player center
        self.center = self.rect.center
        return self.center

class MapGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Node connections in all four directions
        self.node_connections = [vector(1, 0), vector(-1, 0), vector(0, 1), vector(0, -1)] 
        self.walls = []
        self.enemies = []
    def withinBoundary(self, node):
        # Check if node is within the screen boundary
        return 0 <= node.x < self.width and 0 <= node.y < self.height 
    def passable(self, node):
        # Return true or false if the node is a wall
        return node not in self.walls
    def node_neighbours(self, node): 
        neighbours = [node + connection for connection in self.node_connections]
        if (node[0] + node[1]) % 2:
            # Reverses objects in a list
            neighbours.reverse()
        # Filters out nodes that are walls or outside the boundary
        neighbours = filter(self.withinBoundary, neighbours)
        neighbours = filter(self.passable, neighbours)
        
        return neighbours
    
def aStar(graph, start, end):
    # Initialize a priority queue
    Pqueue = PriorityQueue()
    Pqueue.put((start), 0)
    # Initialzing path and cost dictionary
    path = {}
    cost = {}
    # Setting the starting node None and cost to 0 
    path[(start)] = None
    cost[(start)] = 0
    # Iterate while the priority queue is not empty 
    while not Pqueue.empty():
        current = Pqueue.get()
        if current == end:
            # Break used to stop the astar search when the
            # current node and goal node are the same
            break
        # Check the next neighbouring nodes of the
        # current node
        for next in graph.node_neighbours(vector(current)):
            next = vector_to_integer(next)
            # Get the next node cost 
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                # Get the priority by adding the next cost and
                # the hueristic value
                priority = next_cost + heuristicValue(vector(end), vector(next))
                cost[next] = next_cost
                # Puts the node into the priority queue
                Pqueue.put(next, priority)
                path[next] = vector(current) - vector(next)
    return path



def heuristicValue(a, b):
    # Return the hueristic value
    return (abs(a.x - b.x) + abs(a.y - b.y)) * 10

    
class WeightedGrid(MapGrid):
    def __init__(self, width, height):
        # Use of inheritance from the MapGrid
        super().__init__(width, height)
        self.weights = {}

    def cost(self, from_node, to_node):
        # Checks if the node distance is equal to 1, same as
        # all four directions of the node
        if (vector(to_node) - vector(from_node)).length_squared() == 1:
            return self.weights.get(to_node, 0) + 10
        
        
def breadthfirst_search(graph, start, end):
        queue = deque()
        queue.append(start)
        path = {}
        path[start] = None
        while len(queue) > 0:
            current = queue.popleft()
            if current == end:
                break
            if graph.node_neighbours(current) != None:
                for next in graph.node_neighbours(current):
                    if vector_to_integer(next) not in path:
                        queue.append(next)
                        path[vector_to_integer(next)] = current - next
        return path
               
def vector_to_integer(v):
    # Returns an integer from a vector input, v
    return (int(v.x), int(v.y))

class Room:
    def __init__(self, RoomNum, player, screen, direction, prevdirection):
        self.screen = screen
        self.RoomNum = RoomNum
        self.room = WeightedGrid(GRIDWIDTH, GRIDHEIGHT)
        self.walls = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.ExitDoors = pg.sprite.Group()
        self.closedExitDoors = pg.sprite.Group()
        self.closeddoors = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.specialitems = pg.sprite.Group()
        self.player = player
        self.doordirection = direction
        # Gives restrictions on where objects
        # can spawn in specific rooms
        if RoomNum == 0:
            self.roomLayout = [["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","B","B","B","","","","","","B"],["B","","","","","","","B","P","B","","","","","","B"],["B","","","","","","","B","B","B","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","B"]]
        else:
            self.roomLayout = [["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","P","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","","","","","","","","","","","","","","","B"],["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","B"]]
           
        self.prevdoordirection = prevdirection
        self.iny = False
        self.inx = False
    
        self.door_replaced = False
        # Wall vectors on the outside boundary
        self.w = [(0,0), (1,0), (2,0), (3,0), (4,0), (5,0), (6,0), (7,0), (8,0), (9,0), (10,0), (11,0), (12,0), (13,0), (14,0), (15,0), (15,1), (15,2), (15,3), (15,4), (15,5), (15,6), (15,7), (15,8), (15,9), (15,10), (15,11), (14,11), (13,11), (12,11), (11,11), (10,11), (9,11), (8,11), (7,11), (6,11), (5,11), (4,11), (3,11), (2,11), (1,11), (0,11), (0,10), (0,9), (0,8), (0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1)]
        
        for wall in self.w:
            self.room.walls.append(vector(wall))
            
        if RoomNum != 5:
            self.AddItems()
            self.CreateRoomWalls()
            self.AddEnemies()
        self.CreateBoundary()    
        #Checks for the last door direction so
        # it doesn't repeat and have two doors in one spot    
        self.CheckPrevDirection()   
        self.CheckCurrentDirection()
        
        pg.sprite.groupcollide(self.closeddoors, self.walls, False, True)
        pg.sprite.groupcollide(self.closedExitDoors, self.walls, False, True)
    
    def CheckCurrentDirection(self):
        if self.doordirection == 1:
            self.door = ClosedDoor(WIDTH - 64, 320, pg.image.load("closeddoorright.png").convert_alpha(), 1)
            self.closeddoors.add(self.door)
            
        elif self.doordirection == 2:
            self.door = ClosedDoor(32, 320, pg.image.load("closeddoorleft.png").convert_alpha(), 2)
            self.closeddoors.add(self.door)
            
        elif self.doordirection == 3:
            self.door = ClosedDoor(448, 48, pg.image.load("closeddoortop.png").convert_alpha(), 3)
            self.closeddoors.add(self.door)
            
        elif self.doordirection == 4:
            self.door = ClosedDoor(448, (HEIGHT - 64), pg.image.load("closeddoorbottom.png").convert_alpha(), 4)
            self.closeddoors.add(self.door)
            
        elif self.doordirection == 0:
            if self.prevdoordirection == 1:
                self.door = ClosedDoor(32, 320, pg.image.load("closeddoorleft.png").convert_alpha(), 2 )
                self.closeddoors.add(self.door)
            elif self.prevdoordirection == 2:
                self.door = ClosedDoor(WIDTH - 64, 320, pg.image.load("closeddoorright.png").convert_alpha(), 1)
                self.closeddoors.add(self.door)
            elif self.prevdoordirection == 3:
                self.door = ClosedDoor(448, (HEIGHT - 64), pg.image.load("closeddoorbottom.png").convert_alpha(), 4)
                self.closeddoors.add(self.door)
            elif self.prevdoordirection == 4:
                self.door = ClosedDoor(448, 48, pg.image.load("closeddoortop.png").convert_alpha(), 3)
                self.closeddoors.add(self.door)
        

    def CheckPrevDirection(self):
        if self.prevdoordirection == 1:
            self.door = ClosedDoor(32, 320, pg.image.load("closeddoorleft.png").convert_alpha(), 2 )
            self.closedExitDoors.add(self.door)
        elif self.prevdoordirection == 2:
            self.door = ClosedDoor(WIDTH - 64, 320, pg.image.load("closeddoorright.png").convert_alpha(), 1)
            self.closedExitDoors.add(self.door)
        elif self.prevdoordirection == 3:
            self.door = ClosedDoor(448, (HEIGHT - 64), pg.image.load("closeddoorbottom.png").convert_alpha(), 4)
            self.closedExitDoors.add(self.door)
        elif self.prevdoordirection == 4:
            self.door = ClosedDoor(448, 48, pg.image.load("closeddoortop.png").convert_alpha(), 3)
            self.closedExitDoors.add(self.door)
    
    def AddItems(self):
        # Add 0-2 items in a random spot in the room
        self.Item_Amount = random.randint(0, 2)
        self.itemnumber = 0
        if self.Item_Amount == 1:
            # Probability of gettng the item
            self.itemnumber = random.randint(1, 30)
        for i in range(self.Item_Amount):
            validSpot = False
            while validSpot == False:
                item_ynumber = random.randint(1, 11)
                item_xnumber = random.randint(1, 15)
                if self.roomLayout[item_ynumber][item_xnumber] == "":    
                    self.roomLayout[item_ynumber][item_xnumber] = "I"
                    
                    if self.itemnumber >= 5:
                        self.sitem = Item((item_xnumber * TILESIZE),(item_ynumber * TILESIZE), 2)
                        self.specitem = (item_xnumber, item_ynumber)
                        self.specialitems.add(self.sitem)
                    else:
                        self.item = Item((item_xnumber * TILESIZE),(item_ynumber * TILESIZE), 1)
                        self.items.add(self.item)       
                    validSpot = True

    def AddEnemies(self):
        self.enemylist = []
        # Add a random amount of enemies
        self.Enemy_Amount = random.randint(3 ,5)
        for i in range(self.Enemy_Amount):
            validSpot = False
            while validSpot == False:
                # Generating a random x and y coordinate
                ynumber = random.randint(3, 8)
                xnumber = random.randint(3, 12)
                if self.roomLayout[ynumber][xnumber] == "": 
                    self.roomLayout[ynumber][xnumber] = "E"
                    # Initializing the enemy(s) into the game
                    self.enemy = Enemy(self.room, xnumber * TILESIZE,ynumber * TILESIZE)
                    # Adding enemies to enemy group
                    self.enemies.add(self.enemy)
                    self.enemylist.append(self.enemy)
                    
                    validSpot = True
        # Minimum of 3 enemies
        self.enemy1 = self.enemylist[0]
        self.enemy2 = self.enemylist[1]
        self.enemy3 = self.enemylist[2]
        # If there are more than 3, enemies are added
        # to the group respectively

        if self.Enemy_Amount > 3:
            self.enemy4 = self.enemylist[3]
        if self.Enemy_Amount > 4:
            self.enemy5 = self.enemylist[4]
        
        
            
    def CreateRoomWalls(self):
        #Initilising the list layout of the map
        validSpot = False
        # the for loop gives the amount of objects
        # you want in each room, max 6 otherwise an error occurs
        # due to too many objects trying to fit in 
        for i in range(6):
            validSpot = False
            while validSpot == False:
                # Gives a random chance to ge the
                # different block types 
                blocktype = random.randint(1, 8)
                ynumber = random.randint(3, 8)
                xnumber = random.randint(3, 12)
                if blocktype == 1:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                            if  self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber + 1][xnumber + 2] == "" and self.roomLayout[ynumber ][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber -1  ] == "" and self.roomLayout[ynumber - 1 ][xnumber] == "" and self.roomLayout[ynumber - 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 2 ][xnumber] == "" and self.roomLayout[ynumber + 2 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber] == ""  and self.roomLayout[ynumber][xnumber + 1] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber+1))
                                self.room.walls.append(vector(xnumber, ynumber+1)) 
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                self.roomLayout[ynumber + 1][xnumber] = "W"
                                self.roomLayout[ynumber + 1 ][xnumber + 1] = "W"
                                # 2x2 block 
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,(ynumber+1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall(xnumber * TILESIZE,(ynumber+1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                            
                if blocktype == 2:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                            if self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber + 1][xnumber + 2] == "" and self.roomLayout[ynumber ][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber -1  ] == "" and self.roomLayout[ynumber - 1 ][xnumber] == "" and self.roomLayout[ynumber - 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 2 ][xnumber] == "" and self.roomLayout[ynumber + 2 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber] == ""  and self.roomLayout[ynumber][xnumber + 1] == "": 
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber))   
                                self.room.walls.append(vector(xnumber, ynumber+1))
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                self.roomLayout[ynumber + 1][xnumber] = "W"
                                # Right "L" 
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber) * TILESIZE,(ynumber+1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                if blocktype == 3:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                             if  self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber + 1][xnumber + 2] == "" and self.roomLayout[ynumber ][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber -1  ] == "" and self.roomLayout[ynumber - 1 ][xnumber] == "" and self.roomLayout[ynumber - 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 2 ][xnumber] == "" and self.roomLayout[ynumber + 2 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber] == ""  and self.roomLayout[ynumber][xnumber + 1] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber+1))
                                
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                self.roomLayout[ynumber + 1][xnumber + 1] = "W"
                                # Left "L"
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber + 1) * TILESIZE,(ynumber+1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                if blocktype == 4:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                            if self.roomLayout[ynumber][xnumber + 1] == "" and self.roomLayout[ynumber][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber] == "" and self.roomLayout[ynumber - 1][xnumber] == "":
                                # One Block
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False

                if blocktype == 5:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                             if  self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber + 1][xnumber + 1] == "" and self.roomLayout[ynumber ][xnumber - 1] == "" and self.roomLayout[ynumber - 1][xnumber -1  ] == "" and self.roomLayout[ynumber - 1 ][xnumber] == "" and self.roomLayout[ynumber - 2 ][xnumber + 1 ] == "" and self.roomLayout[ynumber - 2 ][xnumber] == "" and self.roomLayout[ynumber - 1 ][xnumber + 2 ] == "" and self.roomLayout[ynumber - 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber] == ""  and self.roomLayout[ynumber][xnumber + 1] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber -1))   
                                self.room.walls.append(vector(xnumber+1, ynumber))
                                
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                self.roomLayout[ynumber - 1][xnumber + 1] = "W"
                                # right up "L"
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber + 1) * TILESIZE,(ynumber-1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                if blocktype == 6:
                    
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                             if  self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber + 1][xnumber + 1] == "" and self.roomLayout[ynumber ][xnumber - 1] == "" and self.roomLayout[ynumber - 1][xnumber -1  ] == "" and self.roomLayout[ynumber - 1 ][xnumber] == "" and self.roomLayout[ynumber - 2 ][xnumber + 1 ] == "" and self.roomLayout[ynumber - 2 ][xnumber] == "" and self.roomLayout[ynumber -1 ][xnumber + 2 ] == "" and self.roomLayout[ynumber - 1 ][xnumber + 1 ] == "" and self.roomLayout[ynumber + 1 ][xnumber] == ""  and self.roomLayout[ynumber][xnumber + 1] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber))   
                                self.room.walls.append(vector(xnumber, ynumber -1))
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                self.roomLayout[ynumber - 1][xnumber] = "W"
                                # left up "L"
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber) * TILESIZE,(ynumber-1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                if blocktype == 7:
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                             if  self.roomLayout[ynumber][xnumber + 2] == "" and self.roomLayout[ynumber][xnumber + 1] == "" and self.roomLayout[ynumber][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber] == "" and self.roomLayout[ynumber - 1][xnumber] == "" and self.roomLayout[ynumber - 1][xnumber + 1] == "" and self.roomLayout[ynumber + 1][xnumber + 1] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber+1, ynumber))   
                        
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber][xnumber + 1] = "W"
                                # Horizontal 2x1 wall
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber+1) * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False
                if blocktype == 8:  
                    if self.roomLayout[ynumber][xnumber] == "":
                        try:
                             if  self.roomLayout[ynumber][xnumber + 1] == "" and self.roomLayout[ynumber][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber - 1] == "" and self.roomLayout[ynumber + 1][xnumber + 1] == "" and self.roomLayout[ynumber + 2][xnumber] == "" and self.roomLayout[ynumber - 1][xnumber] == "" and self.roomLayout[ynumber + 1][xnumber] == "":
                                self.room.walls.append(vector(xnumber, ynumber))   
                                self.room.walls.append(vector(xnumber, ynumber +1))   
                    
                                self.roomLayout[ynumber][xnumber] = "W"
                                self.roomLayout[ynumber + 1][xnumber ] = "W"
                                # Vertical block wall
                                self.wall = Wall(xnumber * TILESIZE,ynumber * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                self.wall = Wall((xnumber) * TILESIZE,(ynumber+1) * TILESIZE, pg.image.load("normwall.png"))
                                self.walls.add(self.wall)
                                validSpot = True
                        except:
                            print("error")
                            validSpot = False               
    def CreateBoundary(self):
        # Creates boundary of outer edge of the room
        for i in range(16):
            # Top boundary
            self.wall = Wall(i * TILESIZE,0, pg.image.load("topwall.png"))
            self.walls.add(self.wall)
        for k in range(16):
            # Bottom boundary
            self.wall = Wall(k * TILESIZE,(HEIGHT - 64), pg.image.load("bottomwall.png"))
            self.walls.add(self.wall)
        for u in range(1, 11):
            # Left boundary
            self.wall = Wall(0, u * TILESIZE, pg.image.load("leftwall.png"))
            self.walls.add(self.wall)
        for o in range(1, 11):
            # Right boundary
            self.wall = Wall((WIDTH - 64), o * TILESIZE, pg.image.load("rightwall.png"))
            self.walls.add(self.wall)
     
    def update(self, proj):
        # Checks to see if there is a special item in the room 
        if len(self.specialitems) > 0:
            self.specialtrue = 1
        else:
            self.specialtrue = 0
            self.specitem = None
        doorcheck = 0
        self.proj = proj
        if self.RoomNum < 5:
            # Update enemies in the room if the room is not number 5
            self.enemy1.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls, self.specialtrue, self.specitem)
            self.enemynode1 = self.enemy1.get_node()  
            self.enemy2.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls,self.specialtrue, self.specitem)
            self.enemynode2 = self.enemy2.get_node()
            self.enemy3.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls, self.specialtrue, self.specitem)
            self.enemynode3 = self.enemy3.get_node()
            if self.Enemy_Amount > 3:
                self.enemy4.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls, self.specialtrue, self.specitem)
                self.enemynode4 = self.enemy4.get_node()
            if self.Enemy_Amount > 4:
                self.enemy5.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls, self.specialtrue, self.specitem)
                self.enemynode5 = self.enemy5.get_node()
            if self.Enemy_Amount > 5:
                self.enemy6.update(self.proj, self.player.rect.center, self.PlayerNodeCheck(), self.walls, self.specialtrue, self.specitem)
                self.enemynode6 = self.enemy6.get_node()
        else:
            # Update the boss if it is room 5
            self.Boss.update(self.proj, self.walls)
        # Allows the projectiles to have collisions between the room objects 
        pg.sprite.groupcollide(self.proj, self.walls, True, False)
        pg.sprite.groupcollide(self.proj, self.closeddoors, True, False)
        pg.sprite.groupcollide(self.proj, self.closedExitDoors, True, False)
                                       
        if self.door_replaced == False:
            if len(self.enemies) == 0:
                if self.prevdoordirection == 1:
                    self.door = Door(32, 320, pg.image.load("opendoorright.png").convert_alpha(), 2 )
                    self.ExitDoors.add(self.door)
                elif self.prevdoordirection == 2:
                    self.door = Door(WIDTH - 64, 320, pg.image.load("opendoorright.png").convert_alpha(), 1)
                    self.ExitDoors.add(self.door)
                elif self.prevdoordirection == 3:
                    self.door = Door(448, (HEIGHT - 64), pg.image.load("opendoortop.png").convert_alpha(), 4)
                    self.ExitDoors.add(self.door)
                elif self.prevdoordirection == 4:
                    self.door = Door(448, 32, pg.image.load("opendoortop.png").convert_alpha(), 3)
                    self.ExitDoors.add(self.door)
                ##############   
                if self.doordirection == 1:
                    self.door = Door(WIDTH - 64, 320, pg.image.load("opendoorright.png").convert_alpha(), 1)
                    self.doors.add(self.door)      
                elif self.doordirection == 2:
                    self.door = Door(32, 320, pg.image.load("opendoorright.png").convert_alpha(), 2)
                    self.doors.add(self.door)                
                elif self.doordirection == 3:
                    self.door = Door(448, 32, pg.image.load("opendoortop.png").convert_alpha(), 3)
                    self.doors.add(self.door)    
                elif self.doordirection == 4:
                    self.door = Door(448, (HEIGHT - 64), pg.image.load("opendoortop.png").convert_alpha(), 4)
                    self.doors.add(self.door)
                pg.sprite.groupcollide(self.closeddoors, self.doors, True, False)
                pg.sprite.groupcollide(self.closedExitDoors, self.ExitDoors, True, False)
                self.door_replaced = True   
                
        if self.RoomNum != 5:
            
            self.collidedwithdoor = self.player.update(self.walls, self.closeddoors, self.closedExitDoors, self.doors, self.ExitDoors, self.enemies,self.items, None, None)
            if self.collidedwithdoor == 1:
                for projectile in self.proj:
                    projectile.kill()
                self.player.LoadInto_NewMap(self.doordirection)
                return 1
            if self.collidedwithdoor == 2:
                for projectile in self.proj:
                    projectile.kill()
                self.player.LoadInto_OldMap(self.prevdoordirection)
                return 2
        
    def PlayerNodeCheck(self):
        # Need to be set to False again for when
        # the procedure is called again in the update section
        self.iny = False
        self.inx = False 
        
        self.playercenter = self.player.getCenter()
        for i in range(0, WIDTH, TILESIZE):
            # Checking if the player's center "x"
            # coordinate is between a tile's area coordinates
            if i > self.playercenter[0] and (i - 64) < self.playercenter[0] :
                self.coordx = i
                self.inx = True
                
        for j in range(0, HEIGHT, TILESIZE):
            if j < self.playercenter[1] and (j + 64) > self.playercenter[1] :
                self.coordy = j
                self.iny = True
    
        # Searching through the tile list and
        # mapping out what tile the player's center is in       
        if self.iny == True and self.inx == True: 
            # Dividing the x and y coordinates
            # by 64 and minusing 1 to get into list form
            x = int(self.coordx / 64 - 1)
            y = int(self.coordy / 64)
            self.tempx = x
            self.tempy = y
            return (x, y)
        else:
            return (self.tempx, self.tempy)
    def draw(self):
        self.walls.draw(self.screen)
        self.specialitems.draw(self.screen)
        self.items.draw(self.screen)
        # Draw enemies when the room num is not 5
        if self.RoomNum < 5:
            self.enemy1.draw()
            self.enemy2.draw()
            self.enemy3.draw()
            if self.Enemy_Amount > 3:
                self.enemy4.draw()
            if self.Enemy_Amount > 4:
                self.enemy5.draw()
        self.closeddoors.draw(self.screen)
        self.closedExitDoors.draw(self.screen)
        if self.RoomNum != 5:
                
            if len(self.enemies) == 0:
                self.doors.draw(self.screen)
                self.ExitDoors.draw(self.screen)

class Boss(pg.sprite.Sprite):
    def __init__(self, startposx, startposy, player, health = 1200):
        pg.sprite.Sprite.__init__(self)
        self.boss_projectiles = pg.sprite.Group()
        self.imgindex = []
        # Initalizing all images
        self.imgindex.append(pg.image.load("boss.v2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("boss2.v2.png").convert_alpha())
        self.imgindex.append(pg.image.load("boss3.v2.png").convert_alpha()) 
        self.imgindex.append(pg.image.load("boss4.v2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("boss5.v2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("boss6.v2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("boss7.v2.png").convert_alpha())  
        self.imgindex.append(pg.image.load("boss8.v2.png").convert_alpha())          
        self.index = 0
        self.image = self.imgindex[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = startposx
        self.rect.y = startposy
        self.health = health
        self.player = player
        self.vx, self.vy = 0, 0
        self.first_movement = False
        self.direction = random.randint(1, 4)
        self.timer = 0
        self.stimer = 0
        self.wait = 0
        self.screen = maingame.returnGameScreen()
    def update(self, Group, wall_group):
        # Boss dies at 0 health
        if self.health == 0:
            self.kill()
            return True
        if pg.sprite.spritecollide(self, Group, True):
            self.health = self.health - 15
        # Setting the hit timer for boss
        if self.timer != 150:
            self.Boss_AttackCycle()
            self.rect.x += self.vx
            self.rect.y += self.vy
            # Directions to bounce
            if self.rect.x == 64 or self.rect.x == (WIDTH - 256):
                if self.direction == 1:
                    self.direction = 4
                elif self.direction == 2:
                    self.direction = 3
                elif self.direction == 3:
                    self.direction = 2
                elif self.direction == 4:
                    self.direction = 1
            if self.rect.y == 64 or self.rect.y == (HEIGHT - 256):
                if self.direction == 1:
                    self.direction = 3
                elif self.direction == 2:
                    self.direction = 4
                elif self.direction == 3:
                    self.direction = 1
                elif self.direction == 4:
                    self.direction = 2
            self.timer += 1
        else:   
            self.vx, self.vy = 0, 0
            if self.wait != 50:
                self.wait += 1
                if self.wait == 25:
                    self.shoot_projectiles()
                elif self.wait == 49:
                    self.shoot_projectiles() 
            else:
                self.wait = 0
                self.timer = 0 
        self.playercenter = self.player.getCenter()
        self.boss_projectiles.update()
        self.rotatetowardsPlayer()
        self.random_timer = random.randint(20, 25)        
        self.stimer += self.random_timer
        # This is where you a able to adjust the
        # animation time, for the cycles of the pictures.
        if (self.stimer % 5) == 0:
            self.index += 1
            if self.index >= len(self.imgindex):
                self.index = 0
            self.image = self.imgindex[self.index]
    def rotatetowardsPlayer(self):
        self.angle_vec = math.atan2((self.rect.center[0] - self.playercenter[0]),(self.rect.center[1] - self.playercenter[1]))
        # The angle is converted from radians to degrees
        self.angle = math.degrees(self.angle_vec)
        self.newimage = pg.transform.rotate(self.image, self.angle - 180)
        oldcenter = self.rect.center
        self.newrect = self.newimage.get_rect()
        self.newrect.center = oldcenter

    def shoot_projectiles(self):
        self.boss_center = self.rect.center
        self.newproj = Projectile(self.boss_center[0], self.boss_center[1], self.playercenter[0] + 128, self.playercenter[1] + 128, 10, self.screen, 2)  
        self.boss_projectiles.add(self.newproj)
        # Object added to a group
        self.newproj = Projectile(self.boss_center[0], self.boss_center[1], self.playercenter[0], self.playercenter[1], 10, self.screen, 2)  
        self.boss_projectiles.add(self.newproj)
        # Object added to a group
        self.newproj = Projectile(self.boss_center[0], self.boss_center[1], self.playercenter[0] - 128, self.playercenter[1] - 128, 10, self.screen, 2)  
        self.boss_projectiles.add(self.newproj)
        # Object added to a group
                                              
    def Boss_AttackCycle(self):
        if self.direction == 2:
            self.vx, self.vy = 4, 4
            self.vx *= -1 
            self.vy *= -1
        if self.direction == 1:
            self.vx, self.vy = -4, -4
            self.vx *= -1
            self.vy *= -1
        if self.direction == 3:
            self.vx, self.vy = -4, 4
            self.vx *= -1
            self.vy *= -1
        if self.direction == 4:
            self.vx, self.vy = 4, -4
            self.vx *= -1
            self.vy *= -1
                  
    def draw(self):
        self.percentage = self.health / 1200
        xcoord = self.percentage * 512
        if self.health != 0:
            self.boss_projectiles.draw(self.screen)
            pg.draw.rect(self.screen,(0, 0, 0),[253, 13, 518, 38])
            pg.draw.rect(self.screen,(95, 99, 88),[256, 16, 512, 32])
            pg.draw.rect(self.screen,(227, 2, 43),[256, 16, xcoord, 32])
            try:
                self.screen.blit(self.newimage, self.newrect)
            except:
                self.screen.blit(self.image, self.rect)
    
# Creating an object which inherits from the class Room       
class BossRoom(Room):
    def __init__(self, RoomNum, player, screen, direction, prevdirection):
        # Super allows the parameters to be
        # taken from the Room class while allowing to
        # have its own __init__ to add differnt
        # more specific parameters.
        super().__init__(RoomNum, player, screen, direction, prevdirection)
        self.boss_group = pg.sprite.Group()
        self.AddBoss()
        self.player = player
        self.boss_dead = False
        self.winimage = pg.image.load("winscreen.png").convert_alpha()
    def AddBoss(self):
        # Add the boss to the room
        self.Boss = Boss(448, 320, self.player)
        self.boss_group.add(self.Boss)
           
    def update(self, projectile):
        # Updating the bossroom and the projectile in it
        super(BossRoom, self).update(projectile)
        self.collidedwithdoor = self.player.update(self.walls, self.closeddoors, self.closedExitDoors, self.doors, self.ExitDoors, self.enemies, self.items, self.Boss.boss_projectiles, self.boss_group)
        if self.collidedwithdoor == 1:
            for projectile in self.proj:
                projectile.kill()
            self.player.LoadInto_NewMap(self.doordirection)
            return 1
        if self.collidedwithdoor == 2:
            for projectile in self.proj:
                projectile.kill()
            self.player.LoadInto_OldMap(self.prevdoordirection)
            return 2
        # Check to see if the boss is dead
        if len(self.boss_group) == 0:
            self.boss_dead = True        
    def draw(self):
        # Draw procedure for the boss room
        super(BossRoom, self).draw()
        self.screen = maingame.returnGameScreen()
        if self.boss_dead == True:
            # Draw the win screen once boss is beaten
            self.screen.blit(self.winimage, (0,0))
        else:
            self.walls.draw(self.screen)
            self.Boss.draw()
        
        self.screen = maingame.returnGameScreen()
        
class Game:
    def __init__(self):
        # initializing the main object
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Dungeon Game")
        self.clock = pg.time.Clock()
        self.bg = pg.image.load("back.png").convert_alpha()
        self.RoomNum = 0  
    
    
    def gameintro(self):
        # load intro screen
        self.image = pg.image.load("intropic.png")
        timer = 0
        intro_stage = True
        while intro_stage == True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quitGame()
                if event.type == pg.MOUSEBUTTONUP:
                    intro_stage = False
            if timer < 250:   
                self.screen.fill((255,255,255))
            if timer == 250:
                self.screen.fill((209, 209, 209))
            if timer == 500:
                self.screen.fill((161, 161, 161))
            if timer == 750:
                self.screen.fill((112, 112, 112))
            if timer >= 1000:
                self.screen.fill((89, 89, 89))
                self.screen.blit(self.image, (32,32))
            timer += 1
            pg.display.flip()
    def deathscreen(self):
        # load death screen 
        self.image = pg.image.load("deathscreen.png")
        timer = 0
        intro_stage = True
        while intro_stage == True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quitGame()
            if timer < 250:   
                self.screen.fill((255,255,255))
            if timer == 250:
                self.screen.fill((209, 209, 209))
            if timer == 500:
                self.screen.fill((161, 161, 161))
            if timer == 750:
                self.screen.fill((112, 112, 112))
            if timer >= 1000:
                self.screen.fill((89, 89, 89))
                self.screen.blit(self.image, (32,32))
            timer += 1
            pg.display.flip()

        
    def CheckforOppositeDoorDirection(self):
        # checking what the opposite door direction is
        if self.doordirection == 1:
            self.doordirection = random.randint(1, 4)
            if self.doordirection == 2:
                self.doordirection += 1           
        elif self.doordirection == 2:
            self.doordirection = random.randint(1, 4)
            if self.doordirection == 1:
                self.doordirection += 1
        elif self.doordirection == 3:
            self.doordirection = random.randint(1, 4)
            if self.doordirection == 4:
                self.doordirection -= 2
        elif self.doordirection == 4:
            self.doordirection = random.randint(1, 4)
            if self.doordirection == 3:
                self.doordirection -= 2
                      
    def CreateNewGame(self): 
        # Creating new sprite groups
        self.projectiles = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        #Initilizing the player into the game
        # with coordinates as parameters
        self.player = PlayerSprite(512, 384)  
        self.player_group.add(self.player)
        self.doordirection = random.randint(1, 4)
        
        self.exitdoor2 = self.doordirection
        # Initializing each room in the game
        self.Room_0 = Room(self.RoomNum, self.player, self.screen, self.doordirection, 0)        
        self.CheckforOppositeDoorDirection()
        self.exitdoor3 = self.doordirection
        
        self.Room_1 = Room(self.RoomNum + 1, self.player, self.screen,self.doordirection, self.exitdoor2)        
        self.CheckforOppositeDoorDirection()
        self.exitdoor4 = self.doordirection
        
        self.Room_2 = Room(self.RoomNum + 2, self.player, self.screen,self.doordirection, self.exitdoor3)
        self.CheckforOppositeDoorDirection()
        self.exitdoor5 = self.doordirection
        
        self.Room_3 = Room(self.RoomNum + 3, self.player, self.screen,self.doordirection, self.exitdoor4)
        self.CheckforOppositeDoorDirection()
        self.exitdoor6 = self.doordirection
        
        self.Room_4 = Room(self.RoomNum + 4, self.player, self.screen,self.doordirection, self.exitdoor5)
        self.CheckforOppositeDoorDirection()
        
        self.Room_5 = BossRoom(self.RoomNum +5, self.player, self.screen,0,self.exitdoor6 )
                
    def returnGameScreen(self):
        self.screen = self.screen
        return self.screen
        # Returns the game's screen
    def drawBackground(self):
        self.screen.blit(self.bg, (0,0))
        
    def MainGameLoop(self):
        self.gameRunning  = True
        # Main Game Loop
        while self.gameRunning:        
            # Setting the clock tick rate to 60 ticks
            self.clock.tick(60)
            self.getEvents()
            self.update()
            self.CreateImage()
        
                   
    def CreateImage(self):
        # Drawing sub-section of the main loop
        self.drawBackground()
        # Each room has a different object with
        # different data to keep the
        # data in that room's required 'data pack'
        self.projectiles.draw(self.screen)
        
        if self.RoomNum == 0:
            self.Room_0.draw()
        elif self.RoomNum == 1:    
            self.Room_1.draw()
        elif self.RoomNum == 2:    
            self.Room_2.draw()
        elif self.RoomNum == 3:    
            self.Room_3.draw()
        elif self.RoomNum == 4:    
            self.Room_4.draw()
        elif self.RoomNum == 5:
            self.player.draw()
            self.Room_5.draw() 
        if self.RoomNum != 5:
            self.player.draw()
        
        # Flips the display at the end to change the image
        pg.display.flip()
            
    def AimLine(self):
        # Testing attribute to visually see the vector
        # of the player's aim
        pg.draw.line(self.screen, (0, 0, 0), (self.mousex, self.mousey), (self.PLAYERCENTER))
        
    def DrawGrid(self):
        # Draws a grid with gives a reference for testing
        for i in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, (0, 0, 0), (i, 0), (i, HEIGHT))
        for j in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, (0, 0, 0), (0, j), (WIDTH, j))
    def getEvents(self):
        self.PLAYERCENTER = self.player.getCenter()
        self.mousex, self.mousey = pg.mouse.get_pos()  
        for event in pg.event.get():
            self.mouse = pg.mouse.get_pressed()
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    # Doesn't allow more than 5 projectiles on
                    # screen at once
                    if len(self.projectiles) < 5:
                        # Creates new projectile object 
                        self.newproj = Projectile(self.PLAYERCENTER[0], self.PLAYERCENTER[1], self.mousex, self.mousey, 15, self.screen, 1)
                        self.projectiles.add(self.newproj)
                        # Object added to a group
            # When the top right cross is clicked, the
            # program closes
            if event.type == pg.QUIT:
                self.quitGame() 
    def update(self):
        # Check to see if the player is dead
        if self.player.health <= 0:
            self.gameRunning  = False        
        self.projectiles.update()
        # Update section for all rooms
        if self.RoomNum == 0:
            if self.Room_0.update(self.projectiles) == 1:
                self.RoomNum = 1
        elif self.RoomNum == 1:
            door1 = self.Room_1.update(self.projectiles)
            if door1 == 1:
                self.RoomNum = 2
            if door1 == 2:
                self.RoomNum -= 1
        elif self.RoomNum == 2:
            door2 = self.Room_2.update(self.projectiles)
            if door2 == 1:
                self.RoomNum = 3
            if door2 == 2:
                self.RoomNum -= 1
        elif self.RoomNum == 3:
            door3 = self.Room_3.update(self.projectiles)
            if door3 == 1:
                self.RoomNum = 4
            if door3 == 2:
                self.RoomNum -= 1
        elif self.RoomNum == 4:
            door4 = self.Room_4.update(self.projectiles)
            if door4 == 1:
                self.RoomNum = 5
            if door4 == 2:
                self.RoomNum -= 1 
        elif self.RoomNum == 5:
            if self.Room_5.update(self.projectiles) == 2:
                self.RoomNum = 4
    # quit procedure                  
    def quitGame(self):
        pg.quit()
        sys.exit()


                
        

# Creates the main game object
maingame = Game()
while True:
    maingame.gameintro()
    maingame.CreateNewGame()
    maingame.MainGameLoop()
    maingame.deathscreen()
    
            

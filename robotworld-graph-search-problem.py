'''
Simulate a robot arm to lift a block using various algorithms like DFS BFS, A* & Best-First using different heuristics like manhattan eucledian chebyshev. 
Different robot worlds with easy medium hard placement and transfer of blocks
Cost - expanding vertices, actual time for execution, no of states created
'''
import time
from heapq import *
import functools
import copy
import math
import os.path
import subprocess

infinity = float("inf")
current_start = (0, 0, 0)
current_goal = ()

class RobotWorld:
    "The idea is that a RobotWorld is the datatype that goes in the queue."
    def __init__(self,width,length,height,initial,goal):
        self.hand = {'location' : (0,0,0), 'held' : None, 'closed?' : False}
        self.width, self.length, self.height = width, length, height
        self.blocks, self.goal = initial, goal
        self.cost, self.title = 0, ''
        assert(initial.keys() == goal.keys()) #there can't be blocks without a goal state, or goal states with a block that is not initialized.

    def __lt__(self,other):
        "Not meaningful, but necessary for RobotWorld to interact with a heapq"
        return True

    # The actions return the change in cost
    def moveUp(self):
        (x,y,z) = self.hand['location']
        if z < (self.height - 1):
            self.hand['location'] = (x,y,z+1)
            if self.hand['held']:
                self.blocks[self.hand['held']] = (x,y,z+1)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveUp' action occuring? The hand is as far up as it can go.")
            return 0
    def moveDown(self):
        (x,y,z) = self.hand['location']
        if z > 0:
            self.hand['location'] = (x,y,z-1)
            if self.hand['held']:
                self.blocks[self.hand['held']] = (x,y,z-1)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveDown' action occuring? The hand is on the floor.")
            return 0
    def moveLeft(self):
        (x,y,z) = self.hand['location']
        if y > 0:
            self.hand['location'] = (x,y-1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y-1,z)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveLeft' action occuring? The hand is on the left edge.")
            return 0
    def moveRight(self):
        (x,y,z) = self.hand['location']
        if y < (self.length - 1):
            self.hand['location'] = (x,y+1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y+1,z)
            self.cost += 1.0
            return 1.0
        else:
            print("Why is the 'moveRight' action occuring? The hand is on the right edge.")
            return 0
    def moveForward(self):
        (x,y,z) = self.hand['location']
        if x < (self.width - 1):
            self.hand['location'] = (x+1,y,z)
            if self.hand['held']:
                self.blocks[self.hand['held']] = (x+1,y,z)
            self.cost += 1
            return 1.0
        else:
            print("Why is the 'moveForward' action occuring? The hand is on the front edge.")
            return 0
    def moveBackward(self):
        (x,y,z) = self.hand['location']
        if x > 0:
            self.hand['location'] = (x-1,y,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x-1,y,z)
            self.cost += 1
            return 1.0
        else:
            print("Why is the 'moveBackward' action occuring? The hand is on the back edge.")
            return 0
    # the reason for the handOpen and handClose actions to have non-zero costs is to prevent the search from considering the
    # "I'll close my hand on this block" and "I'll open and close my hand on this block 20 million times" as equivalent.
    def handOpen(self):
        if not self.hand['closed?']: #if hand is open
            print("Why is the 'handOpen' action occuring? The hand is already open.")
            return 0
        self.hand['closed?'] = False
        if self.hand['held']:
            self.hand['held'] = None
            self.cost += 0.1
            return 0.1
    def handClose(self):
        if self.hand['closed?']:
            print("Why is the 'handClose' action occuring? The hand is already closed.")
            return 0
        else:   #if hand is open
            for (name,location) in self.blocks.iteritems():
                if location == self.hand['location'] and location != self.goal[name]:
                    self.hand['held'] = name
                    self.hand['closed?'] = True
                    self.cost += 0.1
                    return 0.1
            print("Why did the 'handClose' action occur? There is no block here at {}".format(str(self.hand['location'])))
            return 0

    def isGoal(self):
        return self.blocks == self.goal

    def allowedActions(self):
        def alreadyThere(coord):
            for (block_name, block_coord) in self.blocks.iteritems():
                if (block_coord == coord) and (block_coord == self.goal[block_name]):
                    #print "Already there is true: block",block_name," at coordinates: ", coord
                    if (self.blocks.values()).count(coord) == 1:
                        return True
            return False
        possibilities = ['close','forward','backward','left','right','up','down']
        if self.hand['closed?'] and alreadyThere(self.hand['location']): #try to open first if its a good idea
            possibilities = ['open'] + possibilities
        # Removing the close action if 'alreadyThere' is True could lead to problems in a 3D world, or even rare scenarios in a 2D world.
        # This is not relevant to the worlds here, but this should be removed if we re-use this for planning.
        if self.hand['closed?'] or (self.hand['location'] not in self.blocks.values()) or (alreadyThere(self.hand['location'])):
            possibilities.remove('close')
        (x,y,z) = self.hand['location']
        if x == 0: possibilities.remove('backward')
        if x == (self.length - 1): possibilities.remove('forward')
        if y == 0: possibilities.remove('left')
        if y == (self.width - 1): possibilities.remove('right')
        if z == 0: possibilities.remove('down')
        if z == (self.height - 1): possibilities.remove('up')
        if self.hand['closed?'] and ('open' not in possibilities): #try to put 'open' at the end, so moving around happens before
            possibilities = possibilities + ['open']               #pointless opening and closing.
        return possibilities

    def do(self,action):
        '''action is a string indicating an action for the RobotWorld to do. These strings come from the 'allowedActions' method, and are part of the process of
           iterating over neighboring nodes in the graph.'''
        if (action == 'up'): return self.moveUp()
        elif (action == 'down'): return self.moveDown()
        elif (action == 'left'): return self.moveLeft()
        elif (action == 'right'): return self.moveRight()
        elif (action == 'forward'): return self.moveForward()
        elif (action == 'backward'): return self.moveBackward()
        elif (action == 'open'): return self.handOpen()
        elif (action == 'close'): return self.handClose()
        else: print("Unexpected action {}".format(action))

def graphsearch(queue,queue_modification,timeout):
    t0 = time.time()
    visited, history = [], []
    while len(queue) > 0:
        if timeout == 0:
            print("Ran out of time for thinking")
            print("The queue is of size: {}".format(len(queue)))
            return float("inf")
        queue, expanded = queue_modification(queue,visited)
        if expanded!= []:
            visited.append(expanded)
            if expanded.isGoal():
                tf = time.time()
                print("The solution's cost is: {0}, and involved expanding {1} vertices".format(str(expanded.cost), str(len(history))))
                print("Finding the solution involved {0} seconds of walltime".format(str(tf - t0)))
                print("----------------------------------------------------------------------------------")
                history.append(expanded)
                return expanded
            else:
                timeout -= 1
                history.append(expanded)
    print("No possible actions left")
    return float("inf")

def duplicateWorld(world,worlds):
    #You may want to test if a world is in some visited set.
    #Worlds with different accumulated costs are considered equivalent.
    for w in worlds:
        #print "w.hand['location']= ",w.hand['location']," and world.hand['location']=",world.hand['location']
        if (w.hand == world.hand) and (w.blocks == world.blocks):
            return True
    return False

# Input: Takes an input array of possible actions , set of visited worlds and a node to be expanded
# Function: Checks if on taking actions in the array, the world generated is a duplicate of the visited world. returns "invalid" if no more state left to expand
# Output: Returns a possible action according to priority which does not create a duplicate world
def decide_action_state(allowedStatesArray,nodetoCheck,visitedStates):
    if "forward" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("forward")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            return "forward"
    if "right" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("right")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            return "right"
    if "backward" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("backward")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            return "backward"
    if "left" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("left")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            return "left"
    else: return "invalid"

# Input: Takes an input array of possible actions , set of visited worlds and a node to be expanded
# Function: Checks if on taking actions in the array, the world generated is a duplicate of the visited world. returns "invalid" if no more state left to expand
# Output: Returns a possible action according to priority which does not create a duplicate world
def decide_action_state_BFS(allowedStatesArray,nodetoCheck,visitedStates):
    if "forward" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("forward")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            print "copyOfTopNode not in visited : can do action: forward"
            return "forward"
    if "right" in allowedStatesArray:
        copyofNodeToCheck = copy.deepcopy(nodetoCheck)
        copyofNodeToCheck.do("right")
        if not duplicateWorld(copyofNodeToCheck,visitedStates):
            print "copyOfTopNode not in visited : can do action: right"
            return "right"
    return "invalid"

#Input: Priority Queue of all worlds, array of visited worlds
#Function: Pops the last visited world, and generates the world which is not visited and is closed from popped world
#Output: Priority Queue of all worlds sorted by last visited world, array of visited worlds
def depthFirst(queue,visited):
    queueCopy = copy.deepcopy(queue)
    topNode=[]
    if visited==[]:
         key,topWorld= queueCopy[len(queueCopy)-1]
         return (queue,topWorld)
    else:
        key,topNode= queueCopy[len(queueCopy)-1]
        allAllowedStates= topNode.allowedActions()
        copyOfTopNode = copy.deepcopy(topNode)
        action= decide_action_state(allAllowedStates,copyOfTopNode,visited)
        if action != "invalid" and (action != None) :
            topNode.do(action)
            #print "expanding topNode -- hand['location'] ",topNode.hand['location'], "cost until now: ",topNode.cost
            if (topNode.hand['location'] == topNode.blocks['A'] and (topNode.hand['held'] is None)) or (topNode.hand['location'] == topNode.blocks['B'] and (topNode.hand['held'] is None) ) : #do not open-close if u have block
                topNode.do("close")
                print "Close hand to pick up block ",topNode.hand['held']," at location: ",topNode.hand['location']
            if (topNode.hand['location'] == topNode.goal['A'] and topNode.hand['held']=='A') or (topNode.hand['location'] == topNode.goal['B'] and topNode.hand['held']=='B'):
                print "hand with block at goal"
                topNode.do("open")
                print "Open hand to drop block ",topNode.hand['held']," at location: ",topNode.hand['location']
                if topNode.isGoal():
                    print("You've found the solution")
            heappush(queue,(key+1,topNode))
            return (queue,topNode)
        else:
            heappop(queue)
            return [],topNode

#Input: Priority Queue of all worlds, array of visited worlds
#Function: Pops child of node visited in previous iteration , generates all child nodes for this one and pushes it into queue
#Output: Priority Queue of all worlds sorted by last visited world, array of visited worlds
def breadthFirst(queue,visited):
    key,topNode = heappop(queue)
    heappush(queue,(key,topNode))
    #print "expanding topNode -- hand['location'] ",topNode.hand['location'], "cost until now: ",topNode.cost
    actionArr=[]
    var = topNode.allowedActions()
    if "close" in var:
        if topNode.hand['held'] is None:
            topNode.do("close")
    if "forward" in var:
        actionArr.append("forward")
    if "right" in var:
        actionArr.append("right")
    if "backward" in var:
        actionArr.append("backward")
    if "left" in var:
        actionArr.append("left")
    if "open" in var:
        topNode.do("open")
        if topNode.isGoal():
            print("You've found the solution")
    for action in actionArr:
        if action != None:
            copyOfTopNode = copy.deepcopy(topNode)
            copyOfTopNode.do(action)
            if not duplicateWorld(copyOfTopNode,visited):
                heappush(queue, (key+len(queue),copyOfTopNode))
        else:
         return queue,[]
    heappop(queue)
    return queue, topNode

# calculates manhattan distance
def heuristic_manhattan(a,b):
    (x1, y1,z1) = a
    (x2, y2, z2) = b
    return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)

# calculates chebyshev distance
def heuristic_chebyshev(a,b):
    (x1, y1,z1) = a
    (x2, y2, z2) = b
    return max(abs(x1 - x2),abs(y1 - y2), abs(z1 - z2))

# Function:
# Used to generate a goal based on current position of Hand in World. If Hand hold a block, it generates goal for current held block,
# if node has dropped block on goal, decides which block to pick up depending on distance from current position
# in hard world,if the block is already on its goal and another block is also placed on the goal it decides which block to pick up
def choose_next_goal(currWorldState,distanceFunction):
    curr_pos = currWorldState.hand["location"]
    min_dist = 9999
    min_dist_goal = 'B'
    for blk in currWorldState.blocks:
        if currWorldState.blocks[blk] != currWorldState.goal[blk]:
            tempMinDist = distanceFunction(curr_pos, currWorldState.blocks[blk])
            if tempMinDist < min_dist:
                min_dist = tempMinDist
                min_dist_goal = blk
    return min_dist_goal

#Function: Calculates path to goal depending on 1. distance of world from origin 2. Distance of world from goal
# once a block is dropped on goal, recalculates path to goal taking current state as origin and destination as block closest from current state
# once hand is on location of block, decides which block to pick up for hard world
def aStar(queue,visited,heuristic):
    global current_start
    global current_goal
    key,topNode = heappop(queue)
    #print "expanding topNode -- hand['location'] ",topNode.hand['location'], "cost until now: ",topNode.cost

    if visited == []:
        current_goal=topNode.blocks[choose_next_goal(topNode, heuristic)]
    allAllowedActions = topNode.allowedActions()
    filteredActions = []
    if "close" in allAllowedActions:
        topNode.do("close")
        print "Close hand to pick up block ",topNode.hand["held"]," at location: ",topNode.hand["location"]
        current_start = topNode.hand["location"]
        current_goal = topNode.goal[topNode.hand["held"]]
        queue2 = []
        heappush(queue2, (0, topNode))
        return queue2, topNode
    if "forward" in allAllowedActions:
        filteredActions.append("forward")
    if "backward" in allAllowedActions:
        filteredActions.append("backward")
    if "right" in allAllowedActions:
        filteredActions.append("right")
    if "left" in allAllowedActions:
        filteredActions.append("left")
    if "open" in allAllowedActions:
        for (name,location) in topNode.blocks.iteritems():
            if (topNode.hand["held"] == name) and (topNode.blocks[name] == topNode.goal[name] == topNode.hand['location']):
                topNode.do("open")
                print "Open hand to drop block ",name," at location: ",location
                if topNode.isGoal(): print("You've found the solution")
                current_start = topNode.hand["location"]
                current_goal = topNode.blocks[choose_next_goal(topNode, heuristic)]
                queue2 = []
                heappush(queue2, (0, topNode))
                return queue2, topNode
    for action in filteredActions:
        if action != None:
            copyOfTopNode = copy.deepcopy(topNode)
            copyOfTopNode.do(action)
            if not duplicateWorld(copyOfTopNode, visited):
                cost = int(heuristic(copyOfTopNode.hand["location"], current_goal) + heuristic(current_start, copyOfTopNode.hand["location"]))
                heappush(queue, (cost, copyOfTopNode))
    return queue, topNode

#Function: Calculates path to goal depending on : Distance of world from goal
# once a block is dropped on goal, recalculates path to goal taking current state as origin and destination as block closest from current state
# once hand is on location of block, decides which block to pick up for hard world
def bestFirst(queue,visited,heuristic):
    global current_start
    global current_goal
    key,topNode = heappop(queue)
    #print "expanding topNode -- hand['location'] ",topNode.hand['location'], "cost until now: ",topNode.cost

    if visited == []:
        current_goal=topNode.blocks[choose_next_goal(topNode, heuristic)]
    allAllowedActions = topNode.allowedActions()
    filteredActions = []
    if "close" in allAllowedActions:
        topNode.do("close")
        print "Close hand to pick up block ",topNode.hand["held"]," at location: ",topNode.hand["location"]
        current_start = topNode.hand["location"]
        current_goal = topNode.goal[topNode.hand["held"]]
        queue2 = []
        heappush(queue2, (0, topNode))
        return queue2, topNode
    if "forward" in allAllowedActions:
        filteredActions.append("forward")
    if "backward" in allAllowedActions:
        filteredActions.append("backward")
    if "right" in allAllowedActions:
        filteredActions.append("right")
    if "left" in allAllowedActions:
        filteredActions.append("left")
    if "open" in allAllowedActions:
        for (name,location) in topNode.blocks.iteritems():
            if (topNode.hand["held"] == name) and (topNode.blocks[name] == topNode.goal[name] == topNode.hand['location']):
                topNode.do("open")
                print "Open hand to drop block ",name," at location: ",location
                if topNode.isGoal(): print("You've found the solution")
                current_start = topNode.hand["location"]
                current_goal = topNode.blocks[choose_next_goal(topNode, heuristic)]
                queue2 = []
                heappush(queue2, (0, topNode))
                return queue2, topNode
    for action in filteredActions:
        if action != None:
            copyOfTopNode = copy.deepcopy(topNode)
            copyOfTopNode.do(action)
            if not duplicateWorld(copyOfTopNode, visited):
                cost = int(heuristic(copyOfTopNode.hand["location"], current_goal))
                heappush(queue, (cost, copyOfTopNode))
    return queue, topNode

def run(world,title,heuristics,timeout=7000):
    solutions = []

    for h in heuristics:
        queue, hname = [], str(h)
        world2 = copy.deepcopy(world)
        world2.title=(title + hname + '_BestFirst')
        heappush(queue,(0,world2))
        bestFirst_h = functools.partial(bestFirst,heuristic=h)
        print("Doing Best First with heuristic {0} on {1}:".format(hname,title))
        solutions.append(graphsearch(queue, bestFirst_h, timeout))

        queue = []
        world4 = copy.deepcopy(world)
        world4.title=(title + hname + '_Astar')
        heappush(queue,(0,world4))
        aStar_h = functools.partial(aStar,heuristic=h)
        print("Doing A* with heuristic {0} on {1}:".format(hname,title))
        solutions.append(graphsearch(queue, aStar_h, timeout))
        queue = []
    world0 = copy.deepcopy(world)
    world0.title=(title + '_DFS')
    heappush(queue,(0,world0))
    print "Doing Depth First Search  on {0}:".format(title)
    solutions.append(graphsearch(queue, depthFirst, timeout))

    queue = []
    world1 = copy.deepcopy(world)
    world1.title=(title + '_BFS')
    heappush(queue,(0,world1))
    print("Doing Breadth First Search on {0}:".format(title))
    solutions.append(graphsearch(queue, breadthFirst, timeout))

hs = [heuristic_manhattan,heuristic_chebyshev] #this is a set, put your heuristic functions in here.
presolved = RobotWorld(4,4,1,{'A' : (3,3,0), 'B' : (3,1,0)}, {'A' : (3,3,0), 'B' : (3,1,0)})
run(presolved,'presolved',hs)
easy = RobotWorld(5,5,1,{'A' : (1,0,0), 'B' : (3,1,0)}, {'A' : (1,1,0), 'B' : (3,1,0)})
run(easy,'easy',hs)
medium = RobotWorld(6,6,1,{'A' : (1,1,0), 'B' : (3,1,0)}, {'A' : (4,4,0), 'B' : (4,5,0)})
run(medium,'medium',hs)
hard = RobotWorld(10,10,1,{'A' : (1,0,0), 'B' : (9,9,0), 'C' : (4,4,0)}, {'A' : (4,4,0), 'B' : (1,0,0), 'C' : (9,9,0)})
run(hard,'hard',hs)

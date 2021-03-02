import random
import math
from itertools import chain, combinations

ids = ['310246897','313769952']


#----------------------------------------------#
##################### NODE #####################
#----------------------------------------------#
##CLASS Node: Defines a Node in the Game Tree we search
class Node:
    def __init__(self, parent, action, state, zone_of_control, agent_zone_of_control, total_score):
        self.parent = parent
        self.creator = action
        self.state = state
        self.zone_of_control = zone_of_control
        self.agent_zone_of_control = agent_zone_of_control
        self.rows = len(state)
        self.columns = len(state[0])
        self.total_score = total_score + self.score_calc(self.zone_of_control) - self.score_calc(self.agent_zone_of_control) # Total score takes into account the cumulative score and the rival's score
        self.selected_action = None
        if parent:
            self.depth = parent.depth + 1
        else:
            self.depth = 0
            

#~~~~~~~~~~ NODE FUNCTIONS ~~~~~~~~~~#            

#   expand_node: Creates all possible following nodes for next actions
    def expand_node(self, my_agent, mid_round):
        if mid_round:
            curr_zone = self.zone_of_control
        else:
            curr_zone = self.agent_zone_of_control
        return [self.generate_following_node(my_agent, action, mid_round)
                for action in my_agent.actions(self.state, curr_zone)]
    
    
#   generate_following_node: Creates a following node based on given action
    def generate_following_node(self, my_agent, action, mid_round):
        next_state = my_agent.new_state_generator(self.state, action, mid_round)
        next_node = Node(self, action, next_state, self.zone_of_control, self.agent_zone_of_control, self.total_score)
        return next_node
    

#   score_calc: Calculates the current score of a player in its zone of control based on the states on the board
    def score_calc(self, zone_of_control):
        curr_score = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if (i, j) in zone_of_control:
                    if self.state[i][j][0] == "Q":
                        curr_score = curr_score - 5
                    elif self.state[i][j][0] == "S":
                        curr_score = curr_score - 1
                    elif self.state[i][j][0] == "I":
                        curr_score = curr_score + 1
                    elif self.state[i][j][0] == "H":
                        curr_score = curr_score + 1
        return curr_score

#-----------------------------------------------------#
##################### END OF NODE #####################
#-----------------------------------------------------#


###############################################################
###############################################################
###############################################################


#-----------------------------------------------#
##################### AGENT #####################
#-----------------------------------------------#
##CLASS Agent: Defines the agent competing against the AI
class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zone_of_control = zone_of_control
        self.order = order
        self.rows = len(initial_state)
        self.columns = len(initial_state[0])
        self.agent_zone_of_control = self.get_agent_zone_of_control()
        # 2 lists keeping track of last and before last steps
        self.last_state = [[0 for i in range(self.columns)] for j in range(self.rows)]
        self.before_last_state = [[0 for i in range(self.columns)] for j in range(self.rows)]


#~~~~~~~~~~ AGENT FUNCTIONS ~~~~~~~~~~#
#   act(self, state): Takes an action based on the order of playing to establish minmax attitude for the agent, including empty action in which a tile is vaccinated
    def act(self, state):
        my_state = self.personal_state(self.last_state, self.before_last_state, state)
        self.before_last_state = self.last_state
        self.last_state = state
        node = Node(None, None, my_state, self.zone_of_control, self.agent_zone_of_control, 0)
        if self.order == "first":
            self.max_value(node, -math.inf, math.inf, True)
        else:
            self.min_value(node, -math.inf, math.inf, True)
        if node.selected_action is None:
            return self.vax_rand(state, self.zone_of_control)
        return node.selected_action
    

#   personal_state maps out the current state by priority in the map based on the given state and previous states
    def personal_state(self, last, before_last, state):
        my_state = [[(0, 0) for i in range(self.columns)] for j in range(self.rows)] # blank 2d list
        for i in range(self.rows):
            for j in range(self.columns):
                if state[i][j] == 'S':
                    if last[i][j] == 'S' and before_last[i][j] == 'S':
                        my_state[i][j] = ('S', 1)
                    elif last[i][j] == 'S' and before_last[i][j] != 'S':
                        my_state[i][j] = ('S', 2)
                    else:
                        my_state[i][j] = ('S', 3)
                elif state[i][j] == 'Q':
                    if last[i][j] == 'Q':
                        my_state[i][j] = ('Q', 1)
                    else:
                        my_state[i][j] = ('Q', 2)
                else:
                    my_state[i][j] = (state[i][j], 0)
        my_state = tuple(tuple(row) for row in my_state)
        return my_state
    

#   get_agent_zone_of_control(self): Determines the AI's zone of control by choosing the tiles not in my agent's zone of control
    def get_agent_zone_of_control(self):
        agent_zone_of_control = []
        for i in range(self.rows):
            for j in range(self.columns):
                if (i, j) not in self.zone_of_control:
                    agent_zone_of_control.append((i, j))
        return agent_zone_of_control


#   min_value and max_value find the minimum and maximum values possible in the game
    def min_value(self, node, a, b, mid_round):
        if node.depth >= 4 or self.goal_test(node.state):
            return node.total_score
        val = math.inf
        for succ_node in node.expand_node(self, mid_round):
            if mid_round:
                mid_round = False
            else:
                mid_round = True
            max_val = self.max_value(succ_node, a, b, mid_round)
            if val <= a:
                return val
            b = min(b, val)
            if max_val <= val:
                val = max_val
                node.selected_action = succ_node.creator
        return val
    
    def max_value(self, node, a, b, mid_round):
        if node.depth >= 4 or self.goal_test(node.state):
            return node.total_score
        val = -math.inf
        for succ_node in node.expand_node(self, mid_round):
            if mid_round:
                mid_round = False
            else:
                mid_round = True
            min_val = self.min_value(succ_node, a, b, mid_round)
            if val >= b:
                return val
            a = max(a, val)
            if min_val >= val:
                val = min_val
                node.selected_action = succ_node.creator
        return val


#   goal_test indicates if we reached a goal state where there are no sick tiles on the board
    def goal_test(self, state):
        for i in range(self.rows):
            for j in range(self.columns):
                if state[i][j][0] == "S":
                    return False
        return True


#   actions maps out all possible actions in the current state inside the agent's zone of control
    def actions(self, state, zone):
        possible_actions = []
        v_actions = []
        q_actions = []
        for (i, j) in zone:
            if state[i][j][0] == 'H':
                if self.neighbors_in_tile_status(state, i, j, zone, 'S') >= 1: # more than 1 neighbors to infect
                    v_actions.append(("vaccinate", (i, j))) # could possibly vaccinate
            if state[i][j][0] == 'S':
                if self.neighbors_in_tile_status(state, i, j, zone, 'H') >= 3: # more than 3 neighbors to be 
                    q_actions.append(("quarantine", (i, j)))
        if v_actions is [] and zone == self.agent_zone_of_control:
            v_actions = self.vax_rand(state, zone)
        v_combs = list(chain.from_iterable(combinations(v_actions, r) for r in range(2)))[1:]
        q_combs = list(chain.from_iterable(combinations(q_actions, r) for r in range(3)))
        for i in range(len(v_combs)):
            for j in range(len(q_combs)):
                possible_actions.append(v_combs[i] + q_combs[j])
        return possible_actions


#   neighbors_in_tile_status finds all neighbors of any tile with a specific status and returns how many there are
    def neighbors_in_tile_status(self, state, row, col, zone, tile_status):
        neighbors = [0, 0, 0, 0]
        sum_total = 0
        if row == 0:
            neighbors[0] = 1
        if row == self.rows - 1:
            neighbors[1] = 1
        if col == 0:
            neighbors[2] = 1
        if col == self.columns - 1:
            neighbors[3] = 1
        if neighbors[0] == 0:
            if state[row - 1][col][0] == tile_status and (row - 1, col) in zone:
                sum_total += 1
        if neighbors[1] == 0:
            if state[row + 1][col][0] == tile_status and (row + 1, col) in zone:
                sum_total += 1
        if neighbors[2] == 0:
            if state[row][col - 1][0] == tile_status and (row, col - 1) in zone:
                sum_total += 1
        if neighbors[3] == 0:
            if state[row][col + 1][0] == tile_status and (row, col + 1) in zone:
                sum_total += 1
        return sum_total


#   new_state_generator generates a new state based on the taken action in order to create a new node
    def new_state_generator(self, state, action, mid_round):
        new_state = [list(row) for row in state]
        for act in action:
            if act[0] == "vaccinate":
                new_state[act[1][0]][act[1][1]] = ("I", 0)
            elif act[0] == "quarantine":
                new_state[act[1][0]][act[1][1]] = ("Q", 3)
        if not mid_round:
            for i in range(self.rows):
                for j in range(self.columns):
                    if new_state[i][j][0] == "H":
                        if self.neighbors_in_tile_status(new_state, i, j, self.zone_of_control, 'S') >= 1:
                            new_state[i][j] = ("H", 4)
                    elif new_state[i][j][0] == "S":
                        new_state[i][j] = ("S", (new_state[i][j][1]) - 1)
                    elif new_state[i][j][0] == "Q":
                        new_state[i][j] = ("Q", (new_state[i][j][1]) - 1)
            for i in range(self.rows):
                for j in range(self.columns):
                    if (new_state[i][j][0] == "S" or new_state[i][j][0] == "Q") and (new_state[i][j][1] == 0):
                        new_state[i][j] = ("H", 0)
                    if new_state[i][j] == ("H", 4):
                        new_state[i][j] = ("S", 3)
        new_state = tuple(tuple(row) for row in new_state)
        return new_state


#   vax_rand creates a list of healthy tiles for possible vaccination. The first tile that is near a sick tile is automatically dedicated for vaccination
    def vax_rand(self, state, zone):
        action = []
        h_tiles = set()
        for (i, j) in zone:
            if 'H' in state[i][j]:
                h_tiles.add((i, j))
                if self.neighbors_in_tile_status(state, i, j, zone, 'S') >= 1:
                    h_tiles = set()
                    h_tiles.add((i, j))
                    break
        try:
            to_vaccinate = random.sample(h_tiles, 1)
        except ValueError:
            to_vaccinate = []
        if len(to_vaccinate) != 0:
            action.append(('vaccinate', to_vaccinate[0]))
        return action

#------------------------------------------------------#
##################### END OF AGENT #####################
#------------------------------------------------------#
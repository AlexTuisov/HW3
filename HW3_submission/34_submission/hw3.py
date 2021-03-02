import random
import copy
import time
import math
import itertools

ids = ['317644730', '312884307']

def have_sick_neighbor(state, i, j):
    if i > 0:  # check for sick neighbors above me
        if state[i - 1][j] == "S":
            return True
    if i < len(state) - 1:  # check for sick neighbors below me
        if state[i + 1][j] == "S":
            return True
    if j > 0:  # check for healthy neighbors to the left
        if state[i][j - 1] == "S":
            return True
    if j < len(state[0]) - 1:  # check for healthy neighbors to the right
        if state[i][j + 1] == "S":
            return True
    return False

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.police_num = 2
        self.medic_num = 1
        self.my_state = initial_state
        self.unpopulated = []
        self.healthy = []
        self.sick = []
        self.immune = []
        self.quarantine = []
        self.time_dict = {}
        self.time = time.time()
        self.order = order
        self.zone = zone_of_control
        self.game_score = [0, 0]
        for (i, row) in enumerate(self.my_state):
            for (j, col) in enumerate(row):
                self.time_dict[(i, j)] = 0
        self.row_len=len(self.my_state[0])
        self.col_len=len(self.my_state)
        pass
        
    def act(self, state):
        if self.order == 'first':
                self.update_state(state,self.my_state,self.time_dict)
                self.time_counter(self.time_dict,self.my_state)
        self.my_state = state
        actions = self.actions(self.my_state)
        action = self.optimal_action(actions, self.my_state, self.time_dict)
        if self.order == 'second':
            if action:
                self.action_result(self.my_state,self.time_dict,action)
            self.update_state(state, self.my_state, self.time_dict)
            self.spread_virus(self.my_state,self.time_dict)
            self.time_counter(self.time_dict, self.my_state)
        return action

    def actions(self, state):
        healthy_list = []
        sick_list = []
        for x,y in self.zone:
            if state[x][y] == 'H':  # find all healthy people that can be vaccinated
                healthy_list.append(["vaccinate", (x, y)])
            if state[x][y] == 'S':  # find all sick people that can be quarantined
                sick_list.append(["quarantine", (x, y)])
        if not healthy_list:
            return []
        actions = [[action] for action in healthy_list]
        return actions

    def update_state(self, state, map, t_dict):
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] == 'S' and map[i][j] != 'S':
                    t_dict[(i, j)] = -1
                elif state[i][j] == 'Q' and map[i][j] != 'Q':
                    t_dict[(i, j)] = -1


    def spread_virus(self, map, t_dict):
        temp_state = [list(i) for i in map] # copying the tuple so it can be changed
        for (i, row) in enumerate(temp_state): # second stage - the virus spreads
            for (j, col) in enumerate(row):
                if col == "H" and have_sick_neighbor(temp_state,i,j):
                    map[i][j] = "S"
                    t_dict[(i, j)]= -1

    def time_counter(self, t_dict, map):
        for (i, row) in enumerate(map):  # the sickness expires
            for (j, col) in enumerate(row):
                if col == "S" and t_dict[(i, j)] > 3:
                    map[i][j] = "H"
                    t_dict[(i, j)] = -1

        for (i, row) in enumerate(map):  # quarantine expires
            for (j, col) in enumerate(row):
                if col == "Q" and t_dict[(i, j)] > 2:
                    map[i][j] = "H"
                    t_dict[(i, j)] = -1

        for (i, row) in enumerate(map):
            for (j, col) in enumerate(row):
                t_dict[(i, j)] = t_dict[(i, j)] + 1  # update the time of each cell


    def action_result(self,map,t_dict,action):
        for p in action:
            if p[0] == "vaccinate":
                map[p[1][0]][p[1][1]] = 'I'

    def h(self,map,actions):
        best_action = None
        best_score = float('-inf')
        for action in actions:

            ours = {'H':0,'S':0,'Q':0,'U':0,'I':0}
            not_ours = {'H': 0, 'S': 0, 'Q': 0, 'U': 0, 'I': 0}
            i = action[0][1][0]
            j = action[0][1][1]

            if i > 0:
                if (i,j) in self.zone: ours[map[i - 1][j]] += 1
                else: not_ours[map[i - 1][j]] += 1
            if i < len(map) - 1 :
                if (i,j) in self.zone: ours[map[i + 1][j]] += 1
                else: not_ours[map[i + 1][j]] += 1
            if j > 0:
                if (i,j) in self.zone: ours[map[i][j - 1]] += 1
                else: not_ours[map[i][j - 1]] += 1
            if j < len(map[0]) - 1 :
                if (i,j) in self.zone: ours[map[i][j + 1]] += 1
                else: not_ours[map[i][j + 1]] += 1
            temp_score = 0
            if ours['S'] + not_ours['S'] == 0 or ours['H'] + not_ours['H'] == 0:
                temp_score = 0
                if temp_score >  best_score:
                    best_score = temp_score
                    best_action = action
                    continue
            else:
                temp_score = ours['H'] * 3  + ours['Q'] * 2 + ours['S'] * 1
                if temp_score >  best_score:
                    best_score = temp_score
                    best_action = action
                    continue
        return best_action

    def optimal_action(self, actions, map, t_dict):
            max_score_value = float('-inf')
            best_action = []
            best_score_board = []
            begin = time.time()
            for action in actions:
                # print("action",action)
                map_copy = copy.deepcopy(map)
                time_dict = copy.deepcopy(t_dict)
                self.action_result(map_copy, time_dict, action)
                self.spread_virus(map_copy, time_dict)
                self.time_counter(time_dict, map_copy)
                temp_score = copy.deepcopy(self.game_score)
                self.final_score(map_copy, temp_score)
                score = temp_score[0] - temp_score[1]
                if score > max_score_value:
                    max_score_value = score
                    best_action = action
            return best_action


    def final_score(self, map, score):
        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] == 'H' or map[i][j] == 'I':
                    if (i, j) in self.zone:
                        score[0] += 1
                    else:
                        score[1] += 1
                if map[i][j] == 'S':
                    if (i, j) in self.zone:
                        score[0] -= 1
                    else:
                        score[1] -= 1
                if map[i][j] == 'Q':
                    if (i, j) in self.zone:
                        score[0] -= 5
                    else:
                        score[1] -= 5

    def final_test(self, state):
        """ Given a state, checks if there are existing tiles labeled "S":
        Returns True if there are, False otherwise."""
        for i in range(len(state[0])):
            for j in range (len(state[0][0])):
                if state[0][i][j] == 'S':
                    return False
        return True

    # class Node:
    #     def __init__(self, map, time_map, father, level):
    #         self.my_state = map
    #         self.time_dict = time_map
    #         self.father = father
    #         self.sons = []
    #         self.level = level
    #
    #     def print(self):
    #         print(self)
    #         for i in range(len(self.my_state)):
    #             print(self.my_state[i], '\t', self.time_dict[i])
    #         print("father:", self.father)
    #         print("sons:", self.sons)
    #
    #
    # def print_map(self,map,time_map):
    #     # print('\n')
    #     for i in range(len(map)):
    #         print(map[i], "\t", time_map[i])
    #
import random
import copy
import time
import math
import itertools

ids = ['307916346', '321019879']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        # print('\n initial_state',initial_state, '\n zone_of_control', zone_of_control, '\n order', order)
        self.n_police = 2
        self.n_medics = 1
        self.map = initial_state
        self.intialize_time()
        self.time_map
        self.time = time.time()
        self.order = order
        self.zoc = zone_of_control
        self.score_board = [0, 0]     # [us, AI]
        pass


    def intialize_time(self):
        # print("intialize_map")
        self.time_map = copy.deepcopy(self.map)
        # print(self.time_map)
        for i, row in enumerate(self.map):
            for j, col in enumerate(row):
                if self.map[i][j] == 'S':
                    self.time_map[i][j] = 3
                elif self.map[i][j] == 'Q':
                    self.time_map[i][j] = 2
                else:
                    self.time_map[i][j] = 0



    def act(self, state):
        if self.order == 'first':
            # self.update_scores(state, self.score_board)
            self.compare(state,self.map,self.time_map)
            self.adj_time(self.time_map,self.map)
        self.map = state
        actions = self.actions(self.map)
        # print(actions)
        # action = random.choice(self.actions(self.map))
        action = self.calc_score(actions, self.map, self.time_map)
        # action = self.h(self.map,actions)
        if self.order == 'second':
            if action:
                # print('\nactions:',actions)
                self.apply_action(self.map,self.time_map,action)
            self.infect(self.map,self.time_map)
            self.adj_time(self.time_map, self.map)
            # self.update_scores(self.map,self.score_board)
        # self.print_map(self.map, self.time_map)
        # print("\n",'action was:',action,"\n")
        # print(action)
        # print(self.score_board)
        return action


    def actions(self, state):
        begin = time.time()
        single_actions = {'police': [], 'medics': []}
        for coordinate in self.zoc:
            i = coordinate[0]
            j = coordinate[1]
            # print(i, j, '-', col)
            # if state[i][j] == 'S':
            #     single_actions['police'].append(["quarantine", (i, j)])
            if state[i][j] == 'H':
                single_actions['medics'].append(["vaccinate", (i, j)])
        # police_comb = itertools.combinations(single_actions['police'], self.n_police)
        # medics_comb = itertools.combinations(single_actions['medics'], self.n_medics)


        # police_actions = [[action] for action in single_actions['police']]
        # for c in police_comb:
        #     police_actions.append([c[n] for n in range(self.n_police)])

        medic_actions = [[action] for action in single_actions['medics']]
        # print("police_actions", police_actions)
        # print("medic_actions", medic_actions)
        # print()
        # print(medic_actions)
        # print(police_actions)
        # for c in medics_comb:
        #     medic_actions.append([c[n] for n in range(self.n_medics)])
        if medic_actions == []:
            # print("medic actions",medic_actions)
            # print("time:", time.time() - begin)
            return []
        actions = [[action] for action in single_actions['medics']]
        # if police_actions == []:
        #     return medic_actions
        #     # for m_act in medic_actions:
        #     #     actions.append(tuple(m_act))
        # elif medic_actions == []:
        #     return police_actions
        #     # for p_act in police_actions:
        #     #     actions.append(tuple(p_act))
        #     # actions = police_actions
        # else:
        #     for p_act in police_actions:
        #         for m_act in medic_actions:
        #             # print("p", p_act)
        #             # print("m", m_act)
        #             # print(p_act + m_act)
        #             actions.append(p_act + m_act)
        # # print(actions)
        # print("time:",time.time() - begin)
        return actions


    def compare(self, state, map, time_map):
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] == 'S' and map[i][j] != 'S':
                    time_map[i][j] = 4
                elif state[i][j] == 'Q' and map[i][j] != 'Q':
                    time_map[i][j] = 3


    def infect(self, temp_map, temp_time_map):
        change_list = []
        for i, row in enumerate(temp_map):
            for j, col in enumerate(row):
                if temp_map[i][j] == 'S':
                    if i > 0 and temp_map[i-1][j] == 'H':
                        change_list.append([i-1, j])
                    if i < len(temp_map)-1 and temp_map[i + 1][j] == 'H':
                        change_list.append([i + 1, j])
                    if j > 0 and temp_map[i][j-1] == 'H':
                        change_list.append([i, j-1])
                    if j < len(temp_map[0])-1 and temp_map[i][j+1] == 'H':
                        change_list.append([i, j+1])
        for c in change_list:
            temp_map[c[0]][c[1]] = 'S'
            temp_time_map[c[0]][c[1]] = 4       # very informative comment about this


    def adj_time(self, temp_time_map, temp_map):
        for i in range(len((temp_time_map))):
            for j in range(len((temp_time_map[i]))):
                # print(i, j, '-', col)
                if temp_time_map[i][j] > 0:
                    temp_time_map[i][j] -= 1
                    if temp_time_map[i][j] == 0:
                        temp_map[i][j] = 'H'


    def apply_action(self,map,time_map,action):
        for a in action:
            if a[0] == "vaccinate":
                map[a[1][0]][a[1][1]] = 'I'
            else:
                map[a[1][0]][a[1][1]] = 'Q'
                time_map[a[1][0]][a[1][1]] = 2

    def h(self,map,actions):
        dist_est = 0
        # print('actions',actions,'type',type(actions))
        max_action = None
        max_score = float('-inf')
        for action in actions:

            zoc_neighbors = {'H':0,'S':0,'Q':0,'U':0,'I':0}
            not_zoc_neighbors = {'H': 0, 'S': 0, 'Q': 0, 'U': 0, 'I': 0}
            # print('action:',action)
            i = action[0][1][0]
            j = action[0][1][1]

            if i > 0:
                if (i,j) in self.zoc: zoc_neighbors[map[i - 1][j]] += 1
                else: not_zoc_neighbors[map[i - 1][j]] += 1
            if i < len(map) - 1 :
                if (i,j) in self.zoc: zoc_neighbors[map[i + 1][j]] += 1
                else: not_zoc_neighbors[map[i + 1][j]] += 1
            if j > 0:
                if (i,j) in self.zoc: zoc_neighbors[map[i][j - 1]] += 1
                else: not_zoc_neighbors[map[i][j - 1]] += 1
            if j < len(map[0]) - 1 :
                if (i,j) in self.zoc: zoc_neighbors[map[i][j + 1]] += 1
                else: not_zoc_neighbors[map[i][j + 1]] += 1
            score = 0
            if zoc_neighbors['S'] + not_zoc_neighbors['S'] == 0 or zoc_neighbors['H'] + not_zoc_neighbors['H'] == 0:
                #Add other ifs
                score = 0
                if score >  max_score:
                    max_score = score
                    max_action = action
                    continue
            else:
                score = zoc_neighbors['H']*3 - not_zoc_neighbors['H']*2 + zoc_neighbors['Q']*1 + zoc_neighbors['S']*0.5
                if score >  max_score:
                    max_score = score
                    max_action = action
                    continue
        return max_action
                # U & I no points
                # if S H_AI -3 or H_us +3 points Q 1 point
                # if S in neigh

    def calc_score(self, actions, map, time_map):
            max_score_value = float('-inf')
            best_action = []
            best_score_board = []
            begin = time.time()
            for action in actions:
                # print("action",action)
                temp_map = copy.deepcopy(map)
                temp_time_map = copy.deepcopy(time_map)
                self.apply_action(temp_map, temp_time_map, action)
                self.infect(temp_map, temp_time_map)
                self.adj_time(temp_time_map, temp_map)
                temp_score_board = copy.deepcopy(self.score_board)  # []
                # print("before update:",temp_score_board)
                self.update_scores(temp_map, temp_score_board)
                # print("after update:", temp_score_board)
                # print(temp_score_board, max_score_value)
                score = temp_score_board[0] - temp_score_board[1]
                # print(score)
                if score > max_score_value:
                    max_score_value = score
                    best_action = action
                    # best_score_board = temp_score_board

            # self.score_board = best_score_board
            return best_action


    def update_scores(self, map, score):
        # print(map)
        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] == 'H' or map[i][j] == 'I':
                    if (i, j) in self.zoc:
                        score[0] += 1
                    else:
                        score[1] += 1
                if map[i][j] == 'S':
                    if (i, j) in self.zoc:
                        score[0] -= 1
                    else:
                        score[1] -= 1
                if map[i][j] == 'Q':
                    if (i, j) in self.zoc:
                        score[0] -= 5
                    else:
                        score[1] -= 5

    def map_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        #print(state[0])
        #print('\ngoal test')
        #print_map(state)
        for i in range(len(state[0])):
            #print('\n', state[0][i])
            for j in range (len(state[0][0])):
                #print(state[0][i][j])
                if state[0][i][j] == 'S':
                    return False
        #print("what")
        return True





    # class Node:
    #     def __init__(self, map, time_map, father, level):
    #         self.map = map
    #         self.time_map = time_map
    #         self.father = father
    #         self.sons = []
    #         self.level = level
    #
    #     def print(self):
    #         print(self)
    #         for i in range(len(self.map)):
    #             print(self.map[i], '\t', self.time_map[i])
    #         print("father:", self.father)
    #         print("sons:", self.sons)
    #
    #
    # def print_map(self,map,time_map):
    #     # print('\n')
    #     for i in range(len(map)):
    #         print(map[i], "\t", time_map[i])
    #

import random
import numpy as np
from copy import deepcopy

ids = ['342390135', '318171824']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.map_shape = np.shape(initial_state)
    def process_state(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick

    def sick_heuristic(self, healthy, coordinate):
        #print("coordinate", coordinate)
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))

        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h

    def immumize_heuristic(self, healthy, sick, coordinate, state):
        neighbors = self.get_neighbors(coordinate, self.map_shape)
        init_h_list = []
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        #print(self.zoc)
        #print("h", h)
        h = 0
        for neighbor in neighbors:
            #print(coordinate, neighbor)
            if state[neighbor[0]][neighbor[1]] == 'H':
                h += 1;
            if state[neighbor[0]][neighbor[1]] == 'S':
                h += 1
                break
        return h

    def get_neighbors(self, coordinate, dimenstions):

        # neighbors = ((coordinate[0] - 1, coordinate[1]),
        #              (coordinate[0] + 1, coordinate[1]),
        #              (coordinate[0], coordinate[1] - 1),
        #              (coordinate[0], coordinate[1] + 1))
        neighbors_list = []
        i, j = coordinate
        if i > 0:
            neighbors_list.append([i - 1, j])
        if i < dimenstions[0] - 1:
            neighbors_list.append([i + 1, j])
        if j > 0:
            neighbors_list.append([i, j - 1])
        if j < dimenstions[1] - 1:
            neighbors_list.append([i, j + 1])
        return tuple(neighbors_list)

    def act(self, state):
        #print("get_nb: ", self.get_neighbors((0, 0), np.shape(state)))
        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)

        #healthy.sort(key=lambda y: self.immumize_heuristic(healthy, sick,  y), reverse=True)
        init_dict = {}
        h = 0
        for H_area in healthy:
            h = self.immumize_heuristic(healthy, sick, H_area, state)
            #print("h", h)
            init_dict[H_area] = h
        #print(init_dict)
        init_dict = {k: v for k, v in sorted(init_dict.items(), key=lambda item: item[1])}
        #print(init_dict)
        h_list = list(init_dict.keys())
        #print(h_list)
        #init_list.sort(key=1, reverse=True)
        #print(init_dict)


        try:
            to_quarantine = (sick[:2])
        except KeyError:
            to_quarantine = []
        try:
            to_vaccinate = (h_list[:1])
        except ValueError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         # initial_state = initial_state
#         # print(initial_state)
#         self.state_shape = np.shape(initial_state)
#         self.zoc = zone_of_control
#         self.police = 2
#         self.medics = 1
#         self.initial_state = deepcopy(initial_state)
#         self.prev_state = []
#         self.init_time_map = self.set_time_map(initial_state)
#
#         self.updated_time_map = deepcopy(self.init_time_map)
#         self.updated_map = deepcopy(initial_state)
#         # print(np.array(self.init_time_map))
#         # print("From Agent: ", np.array(initial_state), np.array(self.current_state))
#         # print("AGEEEEEEEEEEEEEEEENT!!!")
#         # s = [(0,1), (2,4), (10,12)]
#         # print(s[:2])
#         # print("order: ", order)
#         pass
#
#     # prev_state = self.ini
#     def act(self, state):
#
#         # updated_time_map = [[0] * np.shape(state)[1] for i in range(np.shape(state)[0])]
#         # updated_map = [[0] * np.shape(state)[1] for i in range(np.shape(state)[0])]
#         self.updated_time_map = state
#         # print("From Agent: ", np.array(state))
#         # print("current_state: ", np.array(state))
#         # print("prev_state: ", np.array(self.prev_state))
#         if (len(self.prev_state)):
#             if (1):
#                 self.update_time_map(self.prev_state, state, self.updated_time_map)
#
#
#         action = []
#         self.prev_state = state
#         return action
#         pass
#
#     def update_time_map(self, prev_state, state, updated_time_map):
#         print(np.shape(prev_state), np.shape(state))
#         for ix, row in enumerate(state):
#             for ij, area in enumerate(row):
#                 if area != prev_state[ix][ij]:
#                     # if prev_state == 'H' and state == 'Q':
#                     #     updated_time_map[ix][ij] = -1
#                     if prev_state == 'H' and state == 'S':
#                         updated_time_map[ix][ij] = 1
#                     elif prev_state == 'S' and state == 'H':
#                         updated_time_map[ix][ij] = -1
#                     elif prev_state == 'S' and state == 'Q':
#                         updated_time_map[ix][ij] = 1
#                     elif prev_state == 'H' and state == 'I':
#                         updated_time_map[ix][ij] = -1
#                 else:
#                     self.updated_time_map[ix][ij] += 1
#         return
#
#     def set_time_map(self, initial_map):
#         time_map = [[0] * np.shape(initial_map)[1] for i in range(np.shape(initial_map)[0])]
#         for ix, row in enumerate(initial_map):
#             for ij, area in enumerate(row):
#                 if area == "Q":
#                     time_map[ix][ij] = 0
#                 elif area == "S":
#                     time_map[ix][ij] = 0
#                 else:
#                     time_map[ix][ij] = -1  # used to forbid changes
#
#         # print(time_map)
#         return time_map

# def minimax(self, state,  depth, alpha, beta, maximizingPlayer):
#     if depth == or game_over in state:
#         return state
#     if maximizingPlayer:
#         maxEval = -np.inf
#         #define get_child_func
#         for each child in children:
#             eval = minimax(self, child, depth - 1, alpha, beta, False)
#             maxEval = max(maxEval, eval)
#             alpha = max(alpha, eval)
#             if beta <= alpha
#                 break
#         return maxEval
#     else:
#         minVal = np.inf
#         for each child in children
#             eval = minimax(self ,child, depth - 1, alpha, beta, True)
#             minEval = min(minEval, eval)

#     #def


# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         print(initial_state)
#
#     def act(self, state):
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action

# Variant 1: if order 1 =>
# Variant 2: full minimax from current state

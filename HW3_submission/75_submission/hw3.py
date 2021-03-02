import random
from itertools import combinations
from copy import deepcopy
import time

ids = ['315881656']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.gamma0 = 0
        self.first = True if order == 'first' else False
        self.dimensions = (len(initial_state), len(initial_state[0]))
        self.map_cords = []
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                self.map_cords.append((i, j))
        self.zoc1 = zone_of_control
        self.zoc2 = [x for x in self.map_cords if
                     not any(x == y for y in self.zoc1) and initial_state[x[0]][x[1]] != 'U']
        self.turn = 1
        self.dic_state = self.state_to_dic(initial_state)

    def act(self, state):
        zipped1 = []
        for (i, j) in self.zoc1:
            zipped1.append((i, j, state[i][j]))
        #print(f"ZOC 1:{zipped1}")
        zipped2 = []
        for (i, j) in self.zoc2:
            zipped2.append((i, j, state[i][j]))
        #print(f"ZOC 2:{zipped2}")
        #print(f"******************************* state at turn {self.turn} before advancing, player 1 is first: {self.first} ************************")
        c = 1

        # for i in range(self.dimensions[0]):
        #     for j in range(self.dimensions[1]):
        #         print(self.dic_state[(i, j)], end=',  ')
        #         if c % 5 == 0:
        #             print()
        #         c += 1
        if self.first and self.turn > 1:
            for i in range(self.dimensions[0]):
                for j in range(self.dimensions[1]):
                    if state[i][j] == self.dic_state[(i, j)][0]:
                        if state[i][j] == 'Q' or state[i][j] == 'S':
                            turn = int(self.dic_state[(i, j)][1])
                            self.dic_state[(i, j)] = self.dic_state[(i, j)][0] + str(turn + 1)
                    elif state[i][j] != self.dic_state[(i, j)][0]:
                        if state[i][j] == 'S':
                            self.dic_state[(i, j)] = 'S1'
                        elif state[i][j] == 'Q':
                            self.dic_state[(i, j)] = 'Q1'
                        elif state[i][j] == 'H' or state[i][j] == 'I':
                            self.dic_state[(i, j)] = state[i][j]
        if not self.first and self.turn == 1:
            self.dic_state = self.state_to_dic(state)
        elif not self.first:
            for i in range(self.dimensions[0]):
                for j in range(self.dimensions[1]):
                    if self.dic_state[(i, j)][0] == state[i][j]:
                        if state[i][j] == 'Q' or state[i][j] == 'S':
                            turn = int(self.dic_state[(i, j)][1])
                            self.dic_state[(i, j)] = self.dic_state[(i, j)][0] + str(turn + 1)
                    elif state[i][j] != self.dic_state[(i, j)][0]:
                        if state[i][j] == 'S':
                            self.dic_state[(i, j)] = 'S1'
                        elif state[i][j] == 'Q':
                            self.dic_state[(i, j)] = 'Q0'
                        elif state[i][j] == 'H' or state[i][j] == 'I':
                            self.dic_state[(i, j)] = state[i][j]

        # else:
        #     for i in range(self.dimensions[0]):
        #         for j in range(self.dimensions[1]):
        #             if state[i][j] != self.dic_state[(i, j)][0]:
        #                 if state[i][j] == 'S':
        #                     self.dic_state[(i, j)] = 'S1'
        #                 elif state[i][j] == 'Q':
        #                     self.dic_state[(i, j)] = 'Q0'
        #                 elif state[i][j] == 'H' or state[i][j] == 'I':
        #                     self.dic_state[(i, j)] = state[i][j]

        print()
        print()
        # print(
        #     f"++++++++++++++++++++++++++++++++++++ state at turn {self.turn} after advancing +++++++++++++++++++++++++++++++++++")
        # c = 1
        # for i in range(self.dimensions[0]):
        #     for j in range(self.dimensions[1]):
        #         if (i, j) in self.zoc1:
        #             print(f"(1):{str(self.dic_state[(i, j)])}", end=',  ')
        #         elif (i, j) in self.zoc2:
        #             print(f"(2):{str(self.dic_state[(i, j)])}", end=',  ')
        #         else:
        #             print(f"(*):{str(self.dic_state[(i, j)])}", end=',  ')
        #         if c % 5 == 0:
        #             print()
        #         c += 1

        print()
        if all(self.dic_state[x][0] == state[x[0]][x[1]] for x in self.map_cords):
            all_good = 1
        else:
            all_good = 0
        # if all_good:
        #     print("all good")
        # else:
        #     print("not all!")
        if self.first:
            action = self.minimax_alg(self.dic_state, self.first)
        else:
            action = self.minimax_alg(self.dic_state, self.first)
            self.dic_state = self.advance_state_after_turn(self.dic_state)
        self.dic_state = apply_action(self.dic_state, action[0])
        self.turn += 1
        return action[0]

    def successors(self, state, player, first):
        if player == 1:
            zoc = self.zoc1
        else:
            zoc = self.zoc2
        if first:
            actions = self.applicable_actions(state, zoc)
            actions_successor_states = []
            for action in actions:
                new_state = self.advance_state_after_turn(apply_action(state.copy(), action))
                actions_successor_states.append((action, new_state))
            if player == 1:
                if len(actions_successor_states)>800:
                    actions_successor_states = actions_successor_states[:800]
            else:
                if len(actions_successor_states) > 300:
                    actions_successor_states = actions_successor_states[:300]
        else:
            actions = self.applicable_actions(state, zoc)
            actions_successor_states = [(action, self.advance_state_after_turn(apply_action(state.copy(), action))) for action in actions]
            if player == 1:
                if len(actions_successor_states) > 800:
                    actions_successor_states = actions_successor_states[:800]
            else:
                if len(actions_successor_states) > 300:
                    actions_successor_states = actions_successor_states[:300]
        return actions_successor_states

    def advance_state_after_turn(self, state):
        new_state = deepcopy(state)
        # virus spread
        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                if state[(i, j)] == 'H' and any(state[x][0]=='S' for x in self.neighbours(i, j)):
                    new_state[(i, j)] = 'S1'

        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                # advancing sick counters
                if 'S' in new_state[(i, j)]:
                    turn = int(new_state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'
                # advancing quarantine counters
                if 'Q' in state[(i, j)]:
                    turn = int(state[(i, j)][1])
                    if turn < 2:
                        new_state[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'
        return new_state

    # state is a dictionary with keys (i, j). S1 for zones that are sick for 1 turn
    def state_to_dic(self, state):  # function is good.
        new_dic_state = {}
        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                if 'S' in state[i][j]:
                    new_dic_state[(i, j)] = 'S1'
                elif 'Q' in state[i][j]:
                    new_dic_state[(i, j)] = 'Q0'
                else:
                    new_dic_state[(i, j)] = state[i][j]
        return new_dic_state

    def neighbours(self, x1, y1):
        _neighbours = [(x1 + 1, y1), (x1, y1 + 1), (x1 - 1, y1), (x1, y1 - 1)]
        for neighbour in tuple(_neighbours):
            if not any(x == neighbour for x in self.map_cords):
                _neighbours.remove(neighbour)
        return _neighbours

    def minimax_alg(self, state, first):
        infinity = float('inf')
        minus_infinity = float('-inf')

        def max_value(state, alpha, beta, depth):
            tic = time.perf_counter()
            if depth >= 3:
                #print(f'depth in max= {depth}')
                return_val = self.h_value(state)
                toc = time.perf_counter()
                #print(f"Function -max- completes in {toc - tic:0.4f} seconds, deph: {depth}, h = {return_val}")
                return return_val
            v = minus_infinity
            num_of_nodes_Opened = 0
            successors = self.successors(state, 1, self.first)
            for (a, s) in successors:
                # print("a, s in max: ")
                # print(a, s)
                # print(f'depth in max= {depth}')
                v = max(v, min_value(s, alpha, beta, depth + 1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            toc = time.perf_counter()
            # print(f"Function -max- completes in {toc - tic:0.4f} seconds, v = {v}, deph: {depth}, nodes_opened = {num_of_nodes_Opened}, num of successors = {len(successors)}")
            return v

        def min_value(state, alpha, beta, depth):
            tic = time.perf_counter()
            if depth >= 2:
                # print(f'depth in min= {depth}')
                return_val = self.h_value(state)
                toc = time.perf_counter()
                # print(f"Function -min- completes in {toc - tic:0.4f} seconds, deph: {depth}, h = {return_val}")
                return return_val
            v = infinity
            num_of_nodes_Opened = 0
            successors = self.successors(state, 2, not self.first)
            for (a, s) in successors:
                num_of_nodes_Opened += 1
                # print("a, s in min: ")
                # print(a, s)
                # print(f'depth in min= {depth}')
                v = min(v, max_value(s, alpha, beta, depth + 1))
                # print(f"v = {v}, alpha = {alpha}")
                if v <= alpha:
                    toc = time.perf_counter()
                    # print(f"Function -min- completes in {toc - tic:0.4f} seconds, v = {v}, deph: {depth}, nodes_opened = {num_of_nodes_Opened}, num of successors = {len(successors)}")
                    return v
                beta = min(beta, v)

            toc = time.perf_counter()
            #print(f"Function -min- completes in {toc - tic:0.4f} seconds, v = {v}, deph: {depth}, nodes_opened = {num_of_nodes_Opened}, num of successors = {len(successors)}")
            return v

        action = self.argmax(self.successors(state=state, player=1, first=self.first),
                        lambda s, alpha, beta: min_value(s, alpha, beta, 2))

        return action

    def argmax(self, successors, min_function):
        max_value = float('-inf')
        max_args = ([], [])
        alpha = float('-inf')
        beta = float('inf')
        v = float('-inf')
        print("successors len: ")
        print(len(successors))
        successor_num = 0
        for a, s in successors:
            m_v = min_function(s, alpha, beta)
            if v < m_v:
                max_args = (a, s)
            v = max(v, m_v)
            alpha = max(alpha, v)
            successor_num+=1
            # print(f"successor num: ({successor_num})")
        return max_args

    def update_factor(self,  gamma0):
        self.gamma0 = gamma0

    def h_value(self, state):

        def sick_neighbours(i, j):
            return [x for x in self.neighbours(i, j) if state[x][0] == 'S']

        def healthy_neighbours_of_P1(i, j):
            return [x for x in self.neighbours(i, j) if state[x] == 'H' and x in self.zoc1]

        def quarantined_neighbours(i, j):
            return [x for x in self.neighbours(i, j) if state[x][0] == 'Q']

        def vaccinated_neighbours(i, j):
            return [x for x in self.neighbours(i, j) if state[x] == 'I']
        h = 0
        # for i in range(self.dimensions[0]):
        #     for j in range(self.dimensions[1]):
        #         if any((i, j) == x for x in self.zoc1):
        #             if state[(i, j)][0] == 'S':
        #                 turn = int(state[(i, j)][1])
        #                 if turn > 0:
        #                     h -= 3*(4 - turn)
        #                 else:
        #                     h -= 3
        #                 if len(healthy_neighbours(i, j)) > 0:
        #                     h -= len([x for x in healthy_neighbours(i, j) if x in self.zoc1]) * (3)
        #                     h += len([x for x in healthy_neighbours(i, j) if x in self.zoc2]) * (3)
        #             elif state[(i, j)][0] == 'Q':
        #                 turn = int(state[(i, j)][1])
        #                 if turn > 0:
        #                     h -= (3 - turn) * 3
        #                 else:
        #                     h-= 6
        #                 if len(healthy_neighbours(i, j)) > 0:
        #                     h += len([x for x in healthy_neighbours(i, j) if x in self.zoc1]) * (3)
        #                     h -= len([x for x in healthy_neighbours(i, j) if x in self.zoc2]) * (3)
        #             elif state[(i, j)] == 'I':
        #                 h += 1
        #                 if len(sick_neighbours(i, j)) > 0:
        #                     h += 2
        #                     # if len(healthy_neighbours(i,j)) > 0:
        #                     #     h += 1*len([x for x in healthy_neighbours(i, j) if x in self.zoc1])-1
        #                     #     h -= 1*len([x for x in healthy_neighbours(i, j) if x in self.zoc2])-1
        #                 else:
        #                     h += 1
        #             elif state[(i, j)] == 'H':
        #                 h += 1
        #                 if len(sick_neighbours(i,j))>0:
        #                      h-=3
        num_of_Q = len([x for x in state if state[x][0] == 'Q' and x in self.zoc1]) # +5
        num_of_S_with_1_hlth = len([x for x in state if state[x][0]=='Q' and len(healthy_neighbours_of_P1(x[0], x[1]))<=1]) # -5
        num_of_healthy_nei_of_S_nodes = sum([len(healthy_neighbours_of_P1(x[0], x[1])) for x in state if state[x][0] == 'S'])
        num_of_sick_areas = len([x for x in self.zoc1 if state[x][0] == 'S'])
        num_of_oponent_S_areas = len([x for x in self.zoc2 if state[x][0]=='S'])

        h+=num_of_oponent_S_areas*4.2 # new
        h += num_of_Q*6 #1
        h -= num_of_S_with_1_hlth * 5.75 #4
        h -= num_of_sick_areas*2.6 #6
        if num_of_sick_areas >= 2:
            h -= num_of_S_with_1_hlth * 4.7 #2
        if num_of_sick_areas > 0:
            h -= (num_of_healthy_nei_of_S_nodes/num_of_sick_areas)*5 #3

        healthy_neigh_of_I_with_S_neighbour = [healthy_neighbours_of_P1(x[0], x[1]) for x in self.zoc1 if state[x] == 'I' and len(sick_neighbours(x[0], x[1]))>0]
        new_one = []
        for j in range(len(healthy_neigh_of_I_with_S_neighbour)):
            for x in healthy_neigh_of_I_with_S_neighbour[j]:
                new_one.append(x)
        new_one = set(new_one)
        healthy_neigh_of_I_with_S_neighbour = list(new_one)
        num_of_I_with_S = len([x for x in self.zoc1 if state[x] == 'I' and len(sick_neighbours(x[0], x[1])) > 0])
        factor =num_of_I_with_S + len(healthy_neigh_of_I_with_S_neighbour)*0.35 #1
        h+=factor
        return h

    def applicable_actions(self, state, zoc):
        quarantine_actions = []
        vaccination_actions = []
        all_actions = []
        num_of_sick_areas = len([x for x in zoc if state[x][0] == 'S'])
        num_of_healthy_areas = len([x for x in zoc if state[x] == 'H'])

        for zone in zoc:
            if 'S' in state[zone]:
                quarantine_actions.append(('quarantine', zone))
            if 'H' in state[zone]:
                if num_of_healthy_areas>10 and not any(state[x][0] =='S' or state[x][0]=='Q' for x in self.neighbours(zone[0], zone[1])) and num_of_sick_areas > 0:
                    pass
                else:
                    vaccination_actions.append(('vaccinate', zone))
        comb_of_two_qur = list(combinations(quarantine_actions, 2))

        if num_of_sick_areas>=2 and num_of_healthy_areas>=1:
            for x in comb_of_two_qur:
                for y in vaccination_actions:
                    all_actions.append([y, x[0], x[1]])
        elif num_of_sick_areas >=2 and num_of_healthy_areas==0:
            for x in comb_of_two_qur:
                all_actions.append([x[0], x[1]])
        elif num_of_sick_areas == 1 and num_of_healthy_areas>=1:
            for x in quarantine_actions:
                for y in vaccination_actions:
                    all_actions.append([y, x])
        elif num_of_sick_areas == 1 and num_of_healthy_areas == 0:
            for x in quarantine_actions:
                all_actions.append([x])
        elif num_of_sick_areas == 0 and num_of_healthy_areas>0:
            for y in vaccination_actions:
                all_actions.append([y])
        if len(all_actions) == 0:
            for zone in zoc:
                if 'S' in state[zone]:
                    quarantine_actions.append(('quarantine', zone))
                if 'H' in state[zone]:
                    vaccination_actions.append(('vaccinate', zone))

            if num_of_sick_areas >= 2 and num_of_healthy_areas >= 1:
                for x in comb_of_two_qur:
                    for y in vaccination_actions:
                        all_actions.append([y, x[0], x[1]])
            elif num_of_sick_areas >= 2 and num_of_healthy_areas == 0:
                for x in comb_of_two_qur:
                    all_actions.append([x[0], x[1]])
            elif num_of_sick_areas == 1 and num_of_healthy_areas >= 1:
                for x in quarantine_actions:
                    for y in vaccination_actions:
                        all_actions.append([y, x])
            elif num_of_sick_areas == 1 and num_of_healthy_areas == 0:
                for x in quarantine_actions:
                    all_actions.append([x])
            elif num_of_sick_areas == 0 and num_of_healthy_areas > 0:
                for y in vaccination_actions:
                    all_actions.append([y])

        return all_actions


def apply_action(state, actions):
    for atomic_action in actions:
        effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
        if 'v' in effect:
            state[location] = 'I'
        else:
            state[location] = 'Q0'
    return state

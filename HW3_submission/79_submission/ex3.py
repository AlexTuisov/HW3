
import time
import math
from copy import deepcopy
from itertools import combinations, chain

ids = ['305276693', ]

MIN = -math.inf
MAX = math.inf
ESCAPE = 3

def make_healthy(state):
    new_state = deepcopy(state)
    for i in range(len(state)):
        for j in range(len(state[i])):
            if new_state[i][j][0] == 'S':
                new_state[i][j] = ('H', 0, new_state[i][j][2])

    return new_state


def run_wild(state, zoc, iter):

    for n in range(iter):
        run_type = ["spread", "healing"]
        for t in run_type:
            i = 0
            for row in state:
                j = 0
                for col in row:
                    tile, time, frontier = col
                    if t == "spread":
                        if tile == "S" and time != 4:
                            infect_neighbours(state, i, j)
                    elif t == "healing":
                        if tile == "S":
                            time -= 1
                            if time == 0:
                                state[i][j] = ("H", 0, state[i][j][2])
                            else:
                                state[i][j] = ("S", time, state[i][j][2])
                        elif tile == "Q":
                            time -= 1
                            if time == 0:
                                state[i][j] = ("H", 0, state[i][j][2])
                            else:
                                state[i][j] = ("Q", time, state[i][j][2])
                    j += 1
                i += 1
    my_infected = 0
    opp_infected = 0

    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j][0] == 'S':
                if (i, j) in zoc:
                    my_infected += 1
                else:
                    opp_infected += 1

    return opp_infected - my_infected


def infect_neighbours(state_list, i, j):
    if i > 0:
        if state_list[i - 1][j][0] == 'H':
            state_list[i - 1][j] = ("S", 4, state_list[i][j][2])
    if j > 0:
        if state_list[i][j - 1][0] == 'H':
            state_list[i][j - 1] = ("S", 4, state_list[i][j][2])

    try:
        if state_list[i + 1][j][0] == 'H':
            state_list[i + 1][j] = ("S", 4, state_list[i][j][2])
    except:
        pass

    try:
        if state_list[i][j + 1][0] == 'H':
            state_list[i][j + 1] = ("S", 4, state_list[i][j][2])
    except:
        pass

    return None

def reward(player_zoc, ai_zoc, curr_state):
    r = 0
    player_comp = 50
    ai_comp = 50
    terminal = True
    for item in player_zoc:
        (i, j) = item
        if curr_state[i][j][0] == 'S':
            terminal = False
            r -= 1
            player_comp -= 1
        elif curr_state[i][j][0] in ['H', 'I']:
            r += 1
        elif curr_state[i][j][0] == 'Q':
            r -= 5

    for item in ai_zoc:
        (i, j) = item
        if curr_state[i][j][0] == 'S':
            terminal = False
            r += 1
            ai_comp -= 1
        elif curr_state[i][j][0] in ['H', 'I']:
            r -= 1
        elif curr_state[i][j][0] == 'Q':
            r += 5

    if terminal:
        r += 1000
    return r


def get_oponent_zoc(initial_state, zoc):
    oponent_zoc = list()
    for i in range(len(initial_state)):
        for j in range(len(initial_state[i])):
            if (i, j) not in zoc:
                oponent_zoc.append((i,j))

    return set(oponent_zoc)

def get_frontier_rank(oponent_zoc, i, j):
    frontier = 0
    for item in oponent_zoc:
        (k, m) = item
        if (k, m) in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
            frontier += 1

    return frontier


def state_adapt(state, zone_of_control, *args, initial=False):
    adapted_state = deepcopy(state)
    if initial:
        for i in range(len(state)):
            for j in range(len(state[i])):
                time = 0
                if state[i][j] == 'S':
                    time = 3
                adapted_state[i][j] = (state[i][j], time, get_frontier_rank(get_oponent_zoc(state, zone_of_control), i, j))
    else:
        prev_state = args[0]
        for i in range(len(state)):
            for j in range(len(state[i])):
                if prev_state[i][j][0] == state[i][j]:
                    if prev_state[i][j][1] != 0:
                        adapted_state[i][j] = (prev_state[i][j][0], prev_state[i][j][1] - 1, prev_state[i][j][2])
                    else:
                        adapted_state[i][j] = (prev_state[i][j][0], prev_state[i][j][1], prev_state[i][j][2])
                elif state[i][j] == 'S':
                    adapted_state[i][j] = ('S', 3, prev_state[i][j][2])
                elif state[i][j] == 'Q':
                    adapted_state[i][j] = ('Q', 2, prev_state[i][j][2])
                elif state[i][j] == 'I':
                    adapted_state[i][j] = ('I', 0, prev_state[i][j][2])
                elif state[i][j] == 'H':
                    adapted_state[i][j] = ('H', 0, prev_state[i][j][2])

    return adapted_state



class Node:
    def __init__(self, state):
        self.parent = None
        self.childrens = list()
        self.state = deepcopy(state)
        self.value = 0

    def get_actions(self, zoc, vac_prior, q_prior):

        qu_actions = list()
        im_actions = list()
        i = 0
        for row in self.state:
            j = 0
            for tile in row:
                if tile[0] == "S":
                    if (i, j) in zoc:
                        qu_actions.append(("quarantine", (i, j)))
                elif tile[0] == "H":
                    if (i, j) in zoc:
                        im_actions.append(("vaccinate", (i, j)))
                j += 1
            i += 1

        qu_actions_list = list(chain.from_iterable(combinations(qu_actions, x) for x in range(3)))

        final_actions_list = []

        for cmd1 in qu_actions_list:
            for cmd2 in im_actions:
                cmd_list = [x for x in cmd1]
                cmd_list.append(cmd2)
                final_actions_list.append(tuple(cmd_list))

        for cmd1 in qu_actions_list:
            for cmd2 in im_actions:
                cmd_list = [x for x in cmd1]
                cmd_list.append(cmd2)
                final_actions_list.append(tuple(cmd_list))

        action_with_score = list()
        for action in final_actions_list:
            action_total_score = 0
            for cmd in action:
                (word, (i, j)) = cmd
                if word == 'vaccinate':
                    action_total_score += vac_prior[(i, j)]
                elif word == 'quarantine':
                    action_total_score += q_prior[(i, j)]

                if self.state[i][j][2] == 4:
                    action_total_score = action_total_score / 100
                if self.state[i][j][2] == 3:
                    action_total_score = action_total_score / 20

            action_with_score.append((action, action_total_score))

        sorted_actions = sorted(action_with_score, key= lambda x: x[1], reverse=True)

        final_final_list = [x[0] for x in sorted_actions]

        return final_final_list

    def apply_action(self, action):
        for move in action:
            (k, (i, j)) = move
            if k == 'quarantine':
                self.state[i][j] = ('Q', self.state[i][j][1], self.state[i][j][2])
            elif k == 'vaccinate':
                self.state[i][j] = ('I', self.state[i][j][1], self.state[i][j][2])

    def run_turn(self):

        run_type = ["spread", "healing"]
        for t in run_type:
            i = 0
            for row in self.state:
                j = 0
                for col in row:
                    tile, time, frontier = col
                    if t == "spread":
                        if tile == "S" and time != 4:
                            infect_neighbours(self.state, i, j)
                    elif t == "healing":
                        if tile == "S":
                            time -= 1
                            if time == 0:
                                self.state[i][j] = ("H", 0, self.state[i][j][2])
                            else:
                                self.state[i][j] = ("S", time, self.state[i][j][2])
                        elif tile == "Q":
                            time -= 1
                            if time == 0:
                                self.state[i][j] = ("H", 0, self.state[i][j][2])
                            else:
                                self.state[i][j] = ("Q", time, self.state[i][j][2])
                    j += 1
                i += 1


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.oponnent_zoc = get_oponent_zoc(initial_state, zone_of_control)
        self.state = state_adapt(initial_state, zone_of_control, initial=True)
        self.order_of_play = order
        self.turn = 0
        self.vaccinate_priority = dict()
        self.quarantine_priority = dict()
        self.opp_vacc_priority = dict()
        self.opp_quar_priority = dict()
        self.deep_thinking()
        self.run_time_list = list()
        self.killer_moves = list()




    def act(self, state):
        start = time.process_time()
        if self.turn:
            new_state = state_adapt(state, self.zoc, self.state)
            self.state = new_state

        self.turn += 1
        start2 = time.process_time()
        if self.order_of_play == 'first':
            minmax_reward, action = self.minmaxAB(self.state, 0, MIN, MAX, 2, start)
            self.run_time_list.append(time.process_time() - start2)
            return action
        else:
            minmax_reward, action = self.minmaxAB(self.state, 0, MIN, MAX, 1, start, run_turn=True)
            self.run_time_list.append(time.process_time() - start2)
            return action

    def minmaxAB(self, state, current_depth, alpha, beta, max_depth, start, run_turn=False, is_max_turn=True):
        if current_depth == max_depth or time.process_time() - start > ESCAPE:
            return reward(self.zoc, self.oponnent_zoc, state), ()

        node = Node(state)
        best_value = MIN if is_max_turn else MAX
        if is_max_turn:
            ret_actions = node.get_actions(self.zoc, self.vaccinate_priority , self.quarantine_priority)
        else:
            ret_actions = node.get_actions(self.oponnent_zoc, self.opp_vacc_priority, self.opp_quar_priority)

        available_killer_moves = [x for x in self.killer_moves if x in ret_actions]
        available_actions = available_killer_moves + [x for x in ret_actions if x not in available_killer_moves]
        selected_action = available_actions[0]

        for action in available_actions:
            node.apply_action(action)
            if run_turn:
                node.run_turn()

            r_child, action_child = self.minmaxAB(node.state, current_depth+1, alpha, beta, max_depth, start, (not run_turn), (not is_max_turn))

            if is_max_turn and best_value < r_child:
                best_value = r_child
                selected_action = action
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            elif (not is_max_turn) and best_value > r_child:
                best_value = r_child
                selected_action = action
                beta = min(beta, best_value)
                if beta <= alpha:
                    self.killer_moves.append(selected_action)
                    break

        return best_value, selected_action

    def deep_thinking(self):

        healthy_state = make_healthy(self.state)

        for tile in self.zoc:
            (i, j) = tile
            one_sick = deepcopy(healthy_state)
            one_sick[i][j] = ('S', 3, one_sick[i][j][2])
            quarantine_score = run_wild(one_sick, self.zoc, 3) - 2.5
            self.quarantine_priority.update({tile: quarantine_score})
            one_immuned = deepcopy(self.state)
            one_immuned[i][j] = ('I', 0, self.state[i][j][2])
            immune_score = run_wild(one_immuned, self.zoc, 3)
            self.vaccinate_priority.update({tile: immune_score})

        for tile in self.oponnent_zoc:
            (i, j) = tile
            one_sick = deepcopy(healthy_state)
            one_sick[i][j] = ('S', 3, one_sick[i][j][2])
            quarantine_score = run_wild(one_sick, self.oponnent_zoc, 3) - 2.5
            self.opp_quar_priority.update({tile: quarantine_score})
            one_immuned = deepcopy(self.state)
            one_immuned[i][j] = ('I', 0, self.state[i][j][2])
            immune_score = run_wild(one_immuned, self.oponnent_zoc, 3)
            self.opp_vacc_priority.update({tile: immune_score})


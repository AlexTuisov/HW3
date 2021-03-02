import random
from itertools import combinations
import numpy as np

ids = ['318801701', '211876644']

NUM_POLICE = 2
NUM_MEDIC = 1


class Node:
    def __init__(self, state, timer, action=None, parent_node=None):
        self.state = state
        self.timer = timer
        self.parent = parent_node
        self.score = None
        self.action = action

    def set_score(self, score):
        self.score = score


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.num_rows = len(initial_state)
        self.num_cols = len(initial_state[0])
        self.timer = {}
        for x in range(self.num_rows):
            for y in range(self.num_cols):
                if initial_state[x][y] == "Q":
                    self.timer[(x, y)] = 3
                elif initial_state[x][y] == "S":
                    self.timer[(x, y)] = 2
                else:
                    self.timer[(x, y)] = 0

        self.ezoc = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) not in self.zoc:
                    self.ezoc.append((i, j))
        self.depth = 20

    def score(self, state, opponent=False):
        s = 0
        if opponent:
            sqrs = self.ezoc
        else:
            sqrs = self.zoc

        for x, y in sqrs:
            if state[x][y] == "H" or state[x][y] == "I":
                s += 1
            elif state[x][y] == "Q":
                s -= 5
            elif state[x][y] == "S":
                s -= 1
        return s

    def create_state(self, cur_state, action):
        for act_type, square in action:
            if act_type == 'quarantine':
                cur_state[square[0]][square[1]] = "Q"
                self.timer[square] = 3
            elif act_type == 'vaccinate':
                cur_state[square[0]][square[1]] = "I"
                self.timer[square] = 0
            else:
                raise Exception("Illegal action, weird")
        return cur_state

    def spread_sickness(self, state, timer):
        """

        """
        to_spread = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if state[i][j] == "H":
                    neighbours = [(i, j-1), (i, j+1), (i-1, j), (i+1, j)]
                    for x, y in neighbours:
                        if x < 0 or y < 0 or x == self.num_rows or y == self.num_cols:
                            continue
                        else:
                            if state[x][y] == "S":
                                to_spread.append([i, j])
        for i, j in to_spread:
            timer[(i,j)] = 4
            state[i][j] = "S"
        return state, timer

    def update_timers(self, state, timer):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if timer[(i,j)] != 0:
                    timer[(i,j)] -= 1
                    if state[i][j] == 0:
                        state[i][j] = "H"
        return state, timer

    def calc_actions(self, state, opponent=False):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        H_list = []
        S_list = []
        actions = []
        if opponent:
            sqrs = self.ezoc
        else:
            sqrs = self.zoc

        for i, j in sqrs:
            if state[i][j] == "H":
                H_list.append((i, j))
            if state[i][j] == "S":
                S_list.append((i, j))

        for num_police in range(0, NUM_POLICE+1):
            for num_medics in range(0, NUM_MEDIC+1):
                all_police_possiblities = combinations(S_list, num_police)
                all_medics_possibilities = combinations(H_list, num_medics)

                for paction in all_police_possiblities:
                    for maction in all_medics_possibilities:
                        action = []
                        for police in paction:
                            action.append(("quarantine", police))
                        for medic in maction:
                            action.append(("vaccinate", medic))
                        actions.append(action)
        return actions

    def find_action(self, state, order, parent=None, k=1):
        if order == 1:
            actions = self.calc_actions(state)
            best_node_per_action = []
            for action in actions:
                nodes = []
                temp_state = self.create_state(state, action)
                adv_actions = self.calc_actions(temp_state, opponent=True)
                for adv in adv_actions:
                    adv_state = self.create_state(temp_state, adv)
                    adv_node = Node(adv_state, self.timer, action)
                    adv_node.state, adv_node.timer = self.spread_sickness(adv_state, self.timer)
                    adv_node.state, adv_node.timer = self.update_timers(adv_node.state, adv_node.timer)
                    my_score = self.score(adv_node.state)
                    adv_score = self.score(adv_node.state, opponent=True)
                    adv_node.set_score(my_score-adv_score)
                    nodes.append(adv_node)

                nodes.sort(key=lambda x: x.score)
                best_node_per_action.append(nodes[0])
            best_node_per_action.sort(key=lambda x: x.score, reverse=True)

            if parent:
                for i in range(min(k,len(actions))):
                    best_node_per_action[i].parent = parent
            return best_node_per_action[:min(k,len(actions))]
        else:
            actions = self.calc_actions(state)
            nodes = []
            for action in actions:
                temp_state = self.create_state(state, action)
                adv_node = Node(temp_state, parent.timer, action)
                adv_node.state, adv_node.timer = self.spread_sickness(temp_state, parent.timer)
                adv_node.state, adv_node.timer = self.update_timers(adv_node.state, adv_node.timer)
                adv_node.score = self.score(adv_node.state) - self.score(adv_node.state, opponent=True)
                nodes.append(adv_node)
            nodes.sort(key=lambda x: x.score, reverse=True)
            if parent:
                for i in range(min(k,len(actions))):
                    nodes[i].parent = parent
            return nodes[:min(k,len(actions))]

    def act(self, state):
        if self.order == 1:
            action = self.act_for1(state)
        else:
            action = self.act_for2(state)
        return action

    def act_for1(self, state):
        nodes = {0:[Node(state,self.timer)]}
        nodes[0][0].set_score(0)
        for i in range(self.depth):
            nodes[i+1] = []
            for node in nodes[i]:
                best_nodes = self.find_action(node.state, self.order, parent=node, k=20)
                for item in best_nodes:
                    item.set_score(item.parent.score+item.score)
                    nodes[i+1].append(item)
        final_nodes = nodes[self.depth]
        final_nodes.sort(key=lambda x: x.score, reverse=True)
        best_node = final_nodes[0]
        for i in range(self.depth-1):
            best_node = best_node.parent
        return best_node.action

    def act_for2(self,state):
        nodes = {0: [Node(state, self.timer)]}
        nodes[0][0].set_score(0)
        for i in range(self.depth):
            nodes[i+1] = []
            for node in nodes[i]:
                best_nodes = self.find_action(node.state, 2, parent=node, k=20)
                for item in best_nodes:
                    best_adv_action = self.find_action(item.state, 1, parent=node, k=20)[0].action
                    temp = self.create_state(item.state, best_adv_action)
                    item.set_score(item.parent.score + item.score)
                    temp_node = Node(temp,item.timer,item.action,node)
                    temp_node.set_score(item.score)
                    nodes[i + 1].append(temp_node)
        final_nodes = nodes[self.depth]
        final_nodes.sort(key=lambda x: x.score, reverse=True)
        best_node = final_nodes[0]
        for i in range(self.depth - 1):
            best_node = best_node.parent
        return best_node.action

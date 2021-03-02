import random
from itertools import chain, combinations, product
from main import *
import math
from copy import deepcopy


ids = ['206203226', '205906225']

def powerset1(iterable, r):
    empty_list = []
    if (r == 0):
        return empty_list
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, i) for i in range(0, r + 1)))[1:]

def update_scores(self, state):
    score = 0
    for (i, j) in self.zoc:
        if 'H' in state[(i, j)]:
            score += 1
        if 'I' in state[(i, j)]:
            score += 1
        if 'S' in state[(i, j)]:
            score -= 1
        if 'Q' in state[(i, j)]:
            score -= 5
    return score


def isDanger(state, i, j, zoc):
    count = 0
    neighbours = ((i+1, j), (i-1, j), (i, j+1), (i, j-1))
    for tile in neighbours:
        if 'H' in state[tile] and tile in zoc:
            count += 1
    return bool(count == 4)


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.state = deepcopy(pad_the_input(initial_state))
        self.score = 0
        row_number = DIMENSIONS[0]
        col_number = DIMENSIONS[1]
        indices_set = set()
        for i in range(row_number):
            for j in range(col_number):
                indices_set.add((i, j))
        self.zoc = [(i+1, j+1) for (i, j) in indices_set if
                        ((i, j) in zone_of_control and 'U' not in initial_state[i][j])]
        self.zoc_enemy = [(i+1, j+1) for (i, j) in indices_set if
                        ((i, j) not in zone_of_control and 'U' not in initial_state[i][j])]
        if order == 'second':
            self.is_second = True
        else:
            self.is_second = False

    def act(self, state):
        new_state = deepcopy(pad_the_input(state))
        root = Node(new_state, self.is_second)
        alpha = -math.inf
        beta = math.inf
        val = self.minimax(root, root.depth, 3, True, alpha, beta)
        action = val.action
        new_action = []
        if action:
            for atomic_action in action:
                new_action.append((atomic_action[0], (atomic_action[1][0]-1, atomic_action[1][1]-1)))
        else:
            new_action = tuple()
        return new_action

    def actions(self, state, enemy=False):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        vaccinate_actions = []
        quarantine_actions = []
        medics = 1
        police = 2
        if not enemy:
            for (i, j) in self.zoc:
                if state[(i, j)] == 'H':
                    vaccinate_actions.append(('vaccinate', (i, j)))
                if (state[(i, j)] == 'S1' or state[(i, j)] == 'S2') and isDanger(state, i, j, self.zoc):
                    quarantine_actions.append(('quarantine', (i, j)))
        else:
            for (i, j) in self.zoc_enemy:
                if state[(i, j)] == 'H':
                    vaccinate_actions.append(('vaccinate', (i, j)))
                if (state[(i, j)] == 'S1' or state[(i, j)] == 'S2') and isDanger(state, i, j, self.zoc_enemy):
                    quarantine_actions.append(('quarantine', (i, j)))

        vaccinate_actions_pre = powerset1(vaccinate_actions, medics)
        quarantine_actions_pre = powerset1(quarantine_actions, police)
        vaccinate_actions_tup = tuple(vaccinate_actions_pre)
        quarantine_actions_tup = tuple(quarantine_actions_pre)

        if ((len(vaccinate_actions_tup) == 0) and (len(quarantine_actions_tup) != 0)):
            possible_actions = quarantine_actions_tup
        elif ((len(quarantine_actions_tup) == 0) and (len(vaccinate_actions_tup) != 0)):
            possible_actions = vaccinate_actions_tup
        elif ((len(quarantine_actions_tup) == 0) and (len(vaccinate_actions_tup) == 0)):
            possible_actions = [()]
        else:
            possible_actions = tuple()
            for action_p in quarantine_actions_tup:
                for action_m in vaccinate_actions_tup:
                    action_m += action_p
                    possible_actions += (action_m, action_p)
            possible_actions += vaccinate_actions_tup + quarantine_actions_tup
        return tuple(possible_actions)

    def apply_action(self, actions):
        cur_state = deepcopy(self.state)
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
            if 'v' in effect:
                cur_state[location] = 'I'
            else:
                cur_state[location] = 'Q0'
        return cur_state

    def change_state(self):
        new_state = deepcopy(self.state)
        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if self.state[(i, j)] == 'H' and ('S' in self.state[(i - 1, j)] or
                                                  'S' in self.state[(i + 1, j)] or
                                                  'S' in self.state[(i, j - 1)] or
                                                  'S' in self.state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'
        # advancing sick counters
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if 'S' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'
                # advancing quarantine counters
                if 'Q' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 2:
                        new_state[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'
        return new_state

    def goal_test(self, state):
        for (i, j) in state:
            if state[(i, j)] == 'S1' or state[(i, j)] == 'S2' or state[(i, j)] == 'S3':
                return False
        return True


    def minimax(self, cur_node, depth, max_depth, is_max, alpha, beta):
        if self.goal_test(cur_node.state) or depth == max_depth:
            if cur_node.depth == 0:
                return cur_node
            while cur_node.depth != 1:
                cur_node = cur_node.parent
            return cur_node
        best_node = None
        if is_max:
            max_val = -math.inf
            #possible_actions = self.actions(cur_node.state)
            succ = tuple()
            for child in cur_node.expand(self, self.is_second, False):
                succ += ((child), )
            for s in succ:
                some_node = self.minimax(s, depth+1, max_depth, not is_max, alpha, beta)
                if some_node.score > max_val:
                    max_val = some_node.score
                    best_node = some_node
                alpha = max(alpha, best_node.score)
                if beta <= alpha:
                    break
        else:
            min_val = math.inf
            #possible_actions = self.actions(cur_node.state, True)
            succ = tuple()
            for child in cur_node.expand(self, not self.is_second, True):
                succ += ((child),)
            for s in succ:
                some_node = self.minimax(s, depth+1, max_depth, is_max, alpha, beta)
                if some_node.score < min_val:
                    min_val = some_node.score
                    best_node = some_node
                beta = min(beta, best_node.score)
                if beta <= alpha:
                    break
        return best_node

#------------------------------------------------------------------------------------------------------#

class Node:
    def __init__(self, state, is_second, parent=None, action=None, score=0):
        self.state = deepcopy(state)
        self.is_second = is_second
        self.parent = parent
        self.action = action
        self.score = score
        self.child = None
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, agent, changing_now=False, enemy=False):
        return [self.child_node(agent, action, changing_now)
                for action in agent.actions(self.state, enemy)]

    def child_node(self, agent, action, changing_now=False):
        next1 = agent.apply_action(action)
        if changing_now:
            next1 = agent.change_state()
            return Node(next1, not self.is_second, self, action, (self.score + update_scores(agent, next1)))
        return Node(next1, not self.is_second, self, action, self.score)

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)
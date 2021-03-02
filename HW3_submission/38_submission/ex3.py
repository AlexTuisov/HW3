import random
from itertools import combinations
import utils


ids = ['313354235', '318358090']



class Node:

    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, zoc, adv_zoc, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.rows = len(state)
        self.cols = len(state[0])
        self.state = state
        self.zoc = zoc
        self.adv_zoc = adv_zoc
        self.parent = parent
        self.action = action
        self.path_cost = path_cost + self.reward_diff()
        self.depth = 0
        self.chosen_action = None
        self.last_act = None
        if parent:
            self.depth = parent.depth + 1


    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, a, t):
        """List the nodes reachable in one step from this node."""
        if t == 1:
            my_zoc = self.zoc
        else:
            my_zoc = self.adv_zoc
        # print("a.actions:", a.actions(self.state, my_zoc))
        return [self.child_node(a, action, t)
                for action in a.actions(self.state, my_zoc)]

    def child_node(self, a, action, t):
        """[Figure 3.10]"""

        res = a.result(self.state, action, t)
        res_node = Node(res, self.zoc, self.adv_zoc, self, action, self.path_cost)
        res_node.last_act = action
        return res_node

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

    def reward_per_zoc(self, zoc):
        reward = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in zoc:
                    if 'S' in self.state[i][j]:
                        reward -= 1
                    elif 'Q' in self.state[i][j]:
                        reward -= 5
                    elif 'H' in self.state[i][j] or 'I' in self.state[i][j]:
                        reward += 1
        return reward

    def reward_diff(self):
        return self.reward_per_zoc(self.zoc) - self.reward_per_zoc(self.adv_zoc)


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.police = 2
        self.medics = 1
        self.state = initial_state
        self.zoc = zone_of_control
        self.order = order
        self.rows = len(initial_state)
        self.cols = len(initial_state[0])
        self.last = [[0 for i in range(self.rows)] for j in range(self.cols)]
        self.last_last = [[0 for i in range(self.rows)] for j in range(self.cols)]
        self.adv_zoc = self.adversary_zoc()


        pass

    def adversary_zoc(self):
        adv_zoc = set()
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in self.zoc:
                    adv_zoc.add((i, j))
        return adv_zoc

    def correct_board(self, state, last, last_last):
        list_state = [list(tup) for tup in state]
        for i in range(self.rows):
            for j in range(self.cols):
                if list_state[i][j] == 'Q':
                    if last[i][j] == 'Q':
                        list_state[i][j] = 'Q1'
                elif list_state[i][j] == 'S':
                    if last[i][j] == 'S' and last_last[i][j] != 'S':
                        list_state[i][j] = 'S1'
                    if last[i][j] == 'S' and last_last[i][j] == 'S':
                        list_state[i][j] = 'S2'
        return tuple(tuple(l) for l in list_state)

    def better_powerset(self, l_action_units, n):
        c = []
        for i in range(n + 1):
            c.extend(combinations(l_action_units, i))
        return tuple(c)

    def count_str(self, combo, str):
        k = len(combo)
        count = 0
        for i in range(k):
            if combo[i][0] == str:
                count += 1
        return count

    def check_if_sick_neighbor(self, list_state, i, j):
        if j + 1 < self.cols:
            if 'S' in list_state[i][j + 1]:
                return True
        if j - 1 >= 0:
            if 'S' in list_state[i][j - 1]:
                return True
        if i + 1 < self.rows:
            if 'S' in list_state[i + 1][j]:
                return True
        if i - 1 >= 0:
            if 'S' in list_state[i - 1][j]:
                return True
        return False

    def check_if_n_neighbors_h(self, list_state, i, j):

        h_count = 0
        if j + 1 < self.cols:
            if 'H' in list_state[i][j + 1]:
                h_count += 1
        if j - 1 >= 0:
            if 'H' in list_state[i][j - 1]:
                h_count += 1
        if i + 1 < self.rows:
            if 'H' in list_state[i + 1][j]:
                h_count += 1
        if i - 1 >= 0:
            if 'H' in list_state[i - 1][j]:
                h_count += 1
        if h_count == 4:
            return True
        return False

    def actions(self, state, curr_zoc):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        v_action_units = []
        q_action_units = []
        possible_actions = []
        healthy = set()
        sick = set()
        possibility = ["quarantine", "vaccinate"]
        for (i, j) in curr_zoc:
            if 'H' in state[i][j]:
                healthy.add((i, j))
                if self.check_if_sick_neighbor(state, i, j):
                    v_action_units.append((possibility[1], (i, j)))
            if 'S' in state[i][j]:
                sick.add((i, j))
                if self.check_if_n_neighbors_h(state, i, j):
                    q_action_units.append((possibility[0], (i, j)))
        #changed:
        if v_action_units == []:
            if len(healthy) > 0:
                to_vacc = random.sample(healthy, 1)[0]
                v_action_units.append((possibility[1], to_vacc))

        if len(v_action_units) > 0:
            v_combo_actions = self.better_powerset(v_action_units, self.medics)[1:]
        else:
            v_combo_actions = self.better_powerset(v_action_units, self.medics)
        if len(q_action_units) > 0:
            q_combo_actions = self.better_powerset(q_action_units, self.police)[1:]
        else:
            q_combo_actions = self.better_powerset(q_action_units, self.police)


        for vacc in v_combo_actions:
            for quar in q_combo_actions:
                # print("vacc+quar:", vacc+quar)
                possible_actions.append(vacc+quar)
        # print("possible actions:", tuple(possible_actions))
        return tuple(possible_actions)

    def result(self, state, action, turn):

        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        list_state = [list(tup) for tup in state]
        dict_action = {"vaccinate": "I", "quarantine": "Q"}
        change_dict = {"X": "S", "U": "U", "I": "I", "H": "H", "S": "S1", "S1": "S2", "S2": "H", "Q": "Q1",
                       "Q1": "H"}
        coordinates = []
        for action_unit in action:
            if action_unit != ():
                coordinates.append(action_unit[1])
                list_state[action_unit[1][0]][action_unit[1][1]] = dict_action[action_unit[0]]
            if turn != 1:
                for i in range(self.rows):
                    for j in range(self.cols):
                        if (i, j) not in coordinates:
                            if list_state[i][j] == 'H':
                                if j + 1 < self.cols:
                                    if 'S' in list_state[i][j+1]:
                                        list_state[i][j] = 'X'
                                if j - 1 >= 0:
                                    if 'S' in list_state[i][j - 1]:
                                        list_state[i][j] = 'X'
                                if i + 1 < self.rows:
                                    if 'S' in list_state[i+1][j]:
                                        list_state[i][j] = 'X'
                                if i - 1 >= 0:
                                    if 'S' in list_state[i-1][j]:
                                        list_state[i][j] = 'X'
                for i in range(self.rows):
                    for j in range(self.cols):
                        if (i, j) not in coordinates:
                            list_state[i][j] = change_dict[list_state[i][j]]
        new_state = [tuple(x) for x in list_state]
        return tuple(new_state)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for i in range(self.rows):
            for j in range(self.cols):
                if 'S' in state[i][j]:
                    return False
        return True

    def act(self, state):
        infinity = float('inf')
        minus_infinity = float("-inf")
        updated_board = self.correct_board(state, self.last, self.last_last)
        self.last_last = self.last
        self.last = state
        n = Node(updated_board, self.zoc, self.adv_zoc)
        if self.order == "first":
            self.maxMin(n, 1, minus_infinity, infinity)
            # print("maxmin")
        else:
            self.minMax(n, 1, minus_infinity, infinity)
        if n.chosen_action == None:
            # print("returns ()")
            return (())
        return n.chosen_action

    def maxMin(self, node, t, alpha, beta):
        if node.depth >= 2 or self.goal_test(node.state):
            return node.path_cost
        value = float("-inf")
        for c in node.expand(self, t):
            # print("c:", c.state)
            if t == 1:
                t = 2
            else:
                t = 1
            minVal = self.minMax(c, t, alpha, beta)
            if value >= beta:
                return value
            alpha = max(alpha, value)
            if minVal >= value:
                # print("minVal>=val")
                value = minVal
                node.chosen_action = c.last_act
        return value

    def minMax(self, node, t, alpha, beta):
        if node.depth >= 2 or self.goal_test(node.state):
            return node.path_cost
        value = float('inf')
        for c in node.expand(self, t):
            if t == 1:
                t = 2
            else:
                t = 1
            maxVal = self.maxMin(c, t, alpha, beta)
            if value <= alpha:
                return value
            beta = min(beta, value)
            if maxVal <= value:
                value = maxVal
                node.chosen_action = c.last_act
        return value

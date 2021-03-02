from itertools import chain, combinations
from copy import deepcopy

NUM_ROWS = 10
NUM_COLUMNS = 10
ALPHA_VALUE_INIT = float("-inf")
BETA_VALUE_INIT = float("inf")
my_dept = 3
ids = ['205717176', '205633258']

"""****************************Initialize Functions****************************************"""


def init_timers(state, num_row, num_col):
    s_dict = {}
    q_dict = {}
    for i in range(num_row):
        for j in range(num_col):
            if state[i][j] == 'S':
                s_dict[(i, j)] = 3
            elif state[i][j] == 'Q':
                q_dict[(i, j)] = 2
    return s_dict, q_dict


# [(i, j)] : ('S' , 1)
def make_dict_state(state, num_rows, num_cols, q_info, s_info):
    dict_state = {}
    for i in range(num_rows):
        for j in range(num_cols):
            if state[i][j] == 'U' or state[i][j] == 'I' or state[i][j] == 'H':
                dict_state[(i, j)] = (state[i][j], 0)
            elif (i, j) in q_info:
                dict_state[(i, j)] = (state[i][j], q_info[(i, j)])
            else:
                dict_state[(i, j)] = (state[i][j], s_info[(i, j)])
    return dict_state


"""***************************************Algorithm Actions*********************************************************"""


def power_set_by_num(iterable, num):
    """ Given an object and a number
        Returns a list of all combinations by the number received."""
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(num + 1)))[1:]


def minmax_search(curr_node, zoc, ai_zoc, depth, maximizing_player, order, is_first, alpha=ALPHA_VALUE_INIT, beta=BETA_VALUE_INIT):
    # """Start the AlphaBeta algorithm.
    # :param state: The state to start from.
    # :param depth: The maximum allowed depth for the algorithm.
    # :param maximizing_player: Whether this is a max node (True) or a min node (False).
    # :param alpha: alpha value
    # :param: beta: beta value
    # :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
    # """

    if curr_node.is_goal() or depth == 0:
        if not is_first:
            return curr_node.score
        # else:
        #     return

    if maximizing_player:
        curr_max = float("-inf")
        childes = curr_node.expand(maximizing_player, order, zoc, ai_zoc)
        wanted_action = None
        for child_node in childes:
            value = minmax_search(child_node, zoc, ai_zoc, (depth-1), not maximizing_player, order, False, alpha, beta)
            #print("maximizer: depth", depth, "value", value, "curr max", curr_max, "alpha", alpha, "beta", beta)
            if value > curr_max:
                curr_max = value
                wanted_action = child_node.action
            if value >= beta:
                return value
            alpha = max(alpha, value)
        if is_first:
            return wanted_action
        else:
            return curr_max
    else:
        curr_min = float("inf")
        childes = curr_node.expand(maximizing_player, order, zoc, ai_zoc)
        for child_node in childes:
            value = minmax_search(child_node, zoc, ai_zoc, (depth - 1), not maximizing_player, order, False, alpha, beta)
            #print("minimizer: depth", depth, "value", value, "curr min", curr_min, "alpha", alpha, "beta", beta)
            if value < curr_min:
                curr_min = value
            if value <= alpha:
                return value
            beta = min(beta, value)
        return curr_min


"""******************************************Actions Actions**********************************************"""


def bring_the_actions(state, zoc):
    possible_to_immune = set()
    possible_to_quarantine = set()
    for (i, j) in zoc:
        if state[(i, j)][0] == 'H':
            possible_to_immune.add((i, j))
        elif state[(i, j)][0] == 'S':
            possible_to_quarantine.add((i, j))
    heuristic_to_quarantine = heuristic_func(possible_to_immune, possible_to_quarantine)
    possible_actions = bring_all_possible(possible_to_immune, heuristic_to_quarantine)
    return possible_actions


def heuristic_func(possible_to_immune, possible_to_quarantine):
    possible_quarantine_to_return = set()
    for coordinate in possible_to_quarantine:
        if (coordinate[0]-1, coordinate[1]) in possible_to_immune\
                and (coordinate[0], coordinate[1]-1) in possible_to_immune \
                and (coordinate[0]+1, coordinate[1]) in possible_to_immune \
                and (coordinate[0], coordinate[1]+1) in possible_to_immune:
            possible_quarantine_to_return.add(coordinate)
    return possible_quarantine_to_return


def bring_all_possible(healthy, sick):
    my_possible_immune = healthy
    my_possible_quarantine = power_set_by_num(sick, 2)
    my_final_possible_quarantine = []
    my_final_possible_immune = []
    for quarantine_act in my_possible_quarantine:
        tuple_quarantine = []
        for one_act in quarantine_act:
            tuple_quarantine.append(('quarantine', one_act))
        my_final_possible_quarantine.append(tuple_quarantine)
    for vaccinate_act in my_possible_immune:
        tuple_immune = [('vaccinate', vaccinate_act)]
        my_final_possible_immune.append(tuple_immune)
    len_possible_immune = len(my_final_possible_immune)
    len_possible_quarantine = len(my_final_possible_quarantine)

    my_possible_actions = []
    if len_possible_immune > 0 and len_possible_quarantine > 0:
        for q_act in my_final_possible_quarantine:
            for i_act in my_final_possible_immune:
                my_possible_actions.append((q_act + i_act))
        my_possible_actions = my_final_possible_immune + my_possible_actions
        return my_possible_actions  # my possible actions ############################################################
    elif len_possible_immune == 0 and len_possible_quarantine > 0:
        return my_final_possible_quarantine
    elif len_possible_immune > 0 and len_possible_quarantine == 0:
        return my_final_possible_immune
    else:
        return [tuple()]


def action_result(state, maximizing_player, order, my_actions):
    returned_state = deepcopy(state)
    curr_quarantine = []
    """Action activated"""
    for act in my_actions:
        if act[0] == 'quarantine':
            returned_state[act[1]] = ('Q', 2)
            curr_quarantine.append(act[1])
        else:
            returned_state[act[1]] = ('I', 0)
    """Let the dynamics... Begin!"""
    if (order != 'first' and maximizing_player) or (order == 'first' and not maximizing_player):
        to_infect = []
        keys = returned_state.keys()
        for coordinate in keys:
            if returned_state[coordinate][0] == 'H':
                if (coordinate[0] - 1) >= 0:
                    if returned_state[(coordinate[0]-1, coordinate[1])][0] == 'S':
                        to_infect.append(coordinate)
                        continue
                if (coordinate[0] + 1) < NUM_ROWS:
                    if returned_state[(coordinate[0]+1, coordinate[1])][0] == 'S':
                        to_infect.append(coordinate)
                        continue
                if (coordinate[1] - 1) >= 0:
                    if returned_state[(coordinate[0], coordinate[1]-1)][0] == 'S':
                        to_infect.append(coordinate)
                        continue
                if (coordinate[1] + 1) < NUM_COLUMNS:
                    if returned_state[(coordinate[0], coordinate[1]+1)][0] == 'S':
                        to_infect.append(coordinate)
                        continue
            elif returned_state[coordinate][0] == 'S' or (returned_state[coordinate][0] == 'Q' and coordinate not in curr_quarantine):
                returned_state[coordinate] = (returned_state[coordinate][0], returned_state[coordinate][1]-1)
                if returned_state[coordinate][1] == 0:
                    returned_state[coordinate] = ('H', 0)
        for infect in to_infect:
            returned_state[infect] = ('S', 3)

    return returned_state


""" ************************************************* Score Actions ****************************************************"""


def node_score(dict_state, zoc):
    my_action_score = 0
    rival_action_score = 0
    for coordinate in dict_state:
        if dict_state[coordinate][0] == 'S':
            if coordinate in zoc:
                my_action_score -= 1
            else:
                rival_action_score -= 1
        elif dict_state[coordinate][0] == 'H' or dict_state[coordinate][0] == 'I':
            if coordinate in zoc:
                my_action_score += 1
            else:
                rival_action_score += 1
        elif dict_state[coordinate][0] == 'Q':
            if coordinate in zoc:
                my_action_score -= 5
            else:
                rival_action_score -= 5
    return my_action_score - rival_action_score


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.num_of_rows = len(initial_state)
        self.num_of_columns = len(initial_state[0])
        self.turn = 0
        self.s_info, self.q_info = init_timers(initial_state, self.num_of_rows, self.num_of_columns)
        self.order = order
        """get rival's zoc"""
        ai_zoc = []
        for i in range(self.num_of_rows):
            for j in range(self.num_of_columns):
                if (i, j) not in zone_of_control:
                    ai_zoc.append((i, j))
        self.ai_zoc = ai_zoc

    def act(self, state):
        if self.turn != 0:
            self.update_info_timer(self.num_of_rows, self.num_of_columns, state)
        self.turn += 1
        """create dict state in which we are going to use in the recursion"""
        dict_state = make_dict_state(state, self.num_of_rows, self.num_of_columns, self.q_info, self.s_info)
        curr_node = Node(dict_state, 0)
        action = minmax_search(curr_node, self.zoc, self.ai_zoc, my_dept, True, self.order, True)
        return action

    def update_info_timer(self, num_row, num_col, state):
        """adding and updating states"""
        for i in range(num_row):
            for j in range(num_col):
                if state[i][j] == 'S':
                    if (i, j) in self.s_info:
                        self.s_info[(i, j)] -= 1
                    else:
                        self.s_info[(i, j)] = 3
                elif state[i][j] == 'Q':
                    if (i, j) in self.q_info:
                        self.q_info[(i, j)] -= 1
                    else:
                        self.q_info[(i, j)] = 2
        """removing healthy states"""
        remove_list = []
        for coordinate in self.s_info:
            if state[coordinate[0]][coordinate[1]] == 'H' or state[coordinate[0]][coordinate[1]] == 'Q':
                remove_list.append(coordinate)
        for coordinate in remove_list:
            del self.s_info[coordinate]

        remove_list = []
        for coordinate in self.q_info:
            if state[coordinate[0]][coordinate[1]] == 'H':
                remove_list.append(coordinate)
        for coordinate in remove_list:
            del self.q_info[coordinate]


class Node:

    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; """

    def __init__(self, state, score, parent=None, action=None):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        self.score = score
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

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

    """return True if there are no more S in map"""
    def is_goal(self):
        values = self.state.values()
        for coordinate in values:
            if coordinate[0] == 'S':
                return False
        return True

    def expand(self, maximizing, order, zoc, rival_zoc):
        """List the nodes reachable in one step from this node."""
        child_list = []
        if maximizing:
            if order == 'first':
                # my turn, we are first
                my_actions = bring_the_actions(self.state, zoc)
                for act in my_actions:
                    child_state = action_result(self.state, maximizing, order, act)
                    child_list.append(Node(child_state, self.score, self, act))
            else:
                # my turn, we are second
                my_actions = bring_the_actions(self.state, zoc)
                for act in my_actions:
                    child_state = action_result(self.state, maximizing, order, act)
                    child_score = node_score(child_state, zoc)
                    child_list.append(Node(child_state, self.score + child_score, self, act))
        else:
            if order == 'first':
                # his turn, we are first
                his_actions = bring_the_actions(self.state, rival_zoc)
                for act in his_actions:
                    child_state = action_result(self.state, maximizing, order, act)
                    child_score = node_score(child_state, zoc)
                    child_list.append(Node(child_state, self.score + child_score, self, act))
            else:
                # his turn, we are second
                his_actions = bring_the_actions(self.state, rival_zoc)
                for act in his_actions:
                    child_state = action_result(self.state, maximizing, order, act)
                    child_list.append(Node(child_state, self.score, self, act))
        return child_list




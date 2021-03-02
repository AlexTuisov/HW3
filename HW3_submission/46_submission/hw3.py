from itertools import combinations
import pickle

ids = ['205946866', '313551707']
DIMENSIONS = (10, 10)
POLICE = 2
MEDICS = 1
MAX_DEPTH = 4


def pad_the_input(a_map):
    state = {}
    new_i_dim = DIMENSIONS[0] + 2
    new_j_dim = DIMENSIONS[1] + 2
    for i in range(0, new_i_dim):
        for j in range(0, new_j_dim):
            if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                state[(i, j)] = 'U'
            elif 'S' in a_map[i - 1][j - 1]:
                state[(i, j)] = 'S1'
            else:
                state[(i, j)] = a_map[i - 1][j - 1]
    return state


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.init_state = pad_the_input(initial_state)
        self.order = order
        self.zoc = make_zoc(zone_of_control)
        self.op_zoc = make_op_zoc(self.init_state, self.zoc)

    def act(self, state):
        self.update_counters(state)
        act_to_do = minimax(MAX_DEPTH, self.zoc, self.op_zoc, self.init_state, self.order, float('-inf'), float('inf'),
                            float('-inf'))
        if act_to_do:
            if act_to_do[0] in ['vaccinate', 'quarantine']:
                return [act_to_do]
        return act_to_do

    def update_counters(self, state):
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                if state[i][j] == self.init_state[(i + 1, j + 1)][0]:
                    if self.init_state[(i + 1, j + 1)] in ['Q0', 'Q1']:
                        num = str(int(self.init_state[(i + 1, j + 1)][1]) + 1)
                        self.init_state[(i + 1, j + 1)] = 'Q' + num
                    elif self.init_state[(i + 1, j + 1)] in ['S0', 'S1', 'S2']:
                        num = str(int(self.init_state[(i + 1, j + 1)][1]) + 1)
                        self.init_state[(i + 1, j + 1)] = 'S' + num
                else:
                    self.init_state[(i + 1, j + 1)] = state[i][j]
                    if state[i][j] in ['S', 'Q']:
                        self.init_state[(i + 1, j + 1)] += '1'


def actions(state, tmp_zoc):
    sick = make_list_by_status(tmp_zoc, 'S', state)
    healthy = make_list_by_status(tmp_zoc, 'H', state)
    if sick:
        quarantine = do_quarantine(state, sick, healthy)
        if len(quarantine) > 2:
            quarantine = combinations_by_num(quarantine, POLICE)
    else:
        quarantine = tuple()
    if healthy:
        vaccinate = do_vaccinate(state, healthy)
    else:
        vaccinate = tuple()

    if vaccinate:
        if not quarantine:
            return vaccinate
        else:
            actions_list = []
            for i in vaccinate:
                for j in quarantine:
                    actions_list.append(i + j)
        return actions_list
    else:
        return tuple()


def make_list_by_status(tmp_zoc, status, state):
    tmp_list = []
    if status == 'H':
        for coordinate in tmp_zoc:
            if status in state[coordinate]:
                tmp_list.append(coordinate)
    else:
        for coordinate in tmp_zoc:
            if state[coordinate] in ['S0', 'S1', 'S2']:
                tmp_list.append(coordinate)
    return tmp_list


def make_op_zoc(state, zoc):
    op_zoc = []
    for (i, j) in state.keys():
        if (i, j) not in zoc and state[(i, j)] != 'U':
            op_zoc.append((i, j))
    return op_zoc


def make_zoc(zoc):
    zoc_list = []
    for (i, j) in zoc:
        zoc_list.append((i + 1, j + 1))
    return zoc_list


def do_quarantine(state, sick, healthy):
    """quarantine on sick if he has 4 healthy neighbors"""

    quarantine = []
    for coordinate in sick:
        count = 0
        row = coordinate[0]
        col = coordinate[1]
        # A neighbor from above
        if 'H' in state[(row - 1, col)]:
            if (row - 1, col) in healthy:
                count += 1
        # A neighbor from below
        if 'H' in state[(row + 1, col)]:
            if (row + 1, col) in healthy:
                count += 1
        # A neighbor to the right
        if 'H' in state[(row, col + 1)]:
            if (row, col + 1) in healthy:
                count += 1
        # A neighbor to the left
        if 'H' in state[(row, col - 1)]:
            if (row, col - 1) in healthy:
                count += 1
        if count == 4:
            quarantine.append(('quarantine', (row - 1, col - 1)))
    return quarantine


def do_vaccinate(state, healthy):
    """vaccinat healthy if he has sick neighbors"""
    vaccinate = []
    vaccinate_score = []
    for coordinate in healthy:
        count_sick, count_healthy = 0, 0
        row = coordinate[0]
        col = coordinate[1]
        # A neighbor from above
        if state[(row - 1, col)] in ['S0', 'S1', 'S2']:
            count_sick += 1
        elif 'H' in state[(row - 1, col)]:
            if (row - 1, col) in healthy:
                count_healthy += 1
        # A neighbor from below
        if state[(row + 1, col)] in ['S0', 'S1', 'S2']:
            count_sick += 1
        elif 'H' in state[(row + 1, col)]:
            if (row + 1, col) in healthy:
                count_healthy += 1
        # A neighbor to the right
        if state[(row, col + 1)] in ['S0', 'S1', 'S2']:
            count_sick += 1
        elif 'H' in state[(row, col + 1)]:
            if (row, col + 1) in healthy:
                count_healthy += 1
        # A neighbor to the left
        if state[(row, col - 1)] in ['S0', 'S1', 'S2']:
            count_sick += 1
        elif 'H' in state[(row, col - 1)]:
            if (row, col - 1) in healthy:
                count_healthy += 1

        if count_sick > 0:
            vaccinate_score.append(count_healthy+1)
        else:
            vaccinate_score.append(0)

    if vaccinate_score:
        max_val = max(vaccinate_score)
        if max_val != 0:
            for i in range(len(vaccinate_score)):
                if vaccinate_score[i] == max_val:
                    row = healthy[i][0]
                    col = healthy[i][1]
                    vaccinate.append(('vaccinate', (row - 1, col - 1)))
        else:
            vaccinate = ordinary_healthy_to_vaccinate(healthy)
        return vaccinate
    else:
        vaccinate = ordinary_healthy_to_vaccinate(healthy)
        return vaccinate


def ordinary_healthy_to_vaccinate(healthy):
    vaccinate = []
    for i in healthy:
        row = i[0]
        col = i[1]
        vaccinate.append(('vaccinate', (row - 1, col - 1)))
    return vaccinate


def combinations_by_num(list_of_state, num):
    """ Given a list of state and a number; returns all the combinations by the number ."""
    return list(combinations(list_of_state, num))


def minimax(max_depth, zoc, op_zoc, init_state, order, alpha, beta, value):
    tree_root = Node(init_state)
    child_of_root = tree_root.expand(order, zoc, op_zoc, MY_TURN=True)
    max_option = tree_root
    for child in child_of_root:
        min_val = min_value(max_depth, zoc, op_zoc, order, alpha, beta, child, MY_TURN=False)
        if min_val > value:
            value = min_val
            max_option = child
    if max_option.action:
        return max_option.action
    else:
        return tuple()


def min_value(max_depth, zoc, op_zoc, order, alpha, beta, tmp_child, MY_TURN):
    if tmp_child.depth == max_depth or check_goal(tmp_child.state):
        return tmp_child.utility
    value = float('inf')
    tmp_child_of_root = tmp_child.expand(order, zoc, op_zoc, MY_TURN)
    for child in tmp_child_of_root:
        value = min(value, max_value(max_depth, zoc, op_zoc, order, alpha, beta, child, MY_TURN=True))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


def max_value(max_depth, zoc, op_zoc, order, alpha, beta, tmp_child, MY_TURN):
    if tmp_child.depth == max_depth or check_goal(tmp_child.state):
        return tmp_child.utility
    value = float('-inf')
    tmp_child_of_root = tmp_child.expand(order, zoc, op_zoc, MY_TURN)
    for child in tmp_child_of_root:
        value = max(value, min_value(max_depth, zoc, op_zoc, order, alpha, beta, child, MY_TURN=False))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value


def check_goal(state):
    for (i, j) in state:
        if state[(i, j)] in ['S0', 'S1', 'S2']:
            return False
    return True


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1
        self.utility = 0

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, order, zoc, op_zoc, MY_TURN):
        """List the nodes reachable in one step from this node."""
        tree_nodes = []
        if order == "first" and MY_TURN:
            acts = actions(self.state, zoc)
            for action in acts:
                tmp_state = apply_action(self.state, action)
                tmp_child = self.child_node(tmp_state, action)
                tmp_child.utility = tmp_child.parent.utility
                tree_nodes.append(tmp_child)
        elif order == "second" and MY_TURN:
            acts = actions(self.state, zoc)
            for action in acts:
                tmp_state = apply_action(self.state, action)
                new_state = change_state(tmp_state)
                tmp_child = self.child_node(new_state, action)
                tmp_child.utility = tmp_child.parent.utility + (
                        update_scores(new_state, zoc) - update_scores(new_state, op_zoc))
                tree_nodes.append(tmp_child)
        elif order == "first" and not MY_TURN:
            acts = actions(self.state, op_zoc)
            for action in acts:
                tmp_state = apply_action(self.state, action)
                new_state = change_state(tmp_state)
                tmp_child = self.child_node(new_state, action)
                tmp_child.utility = tmp_child.parent.utility + (
                        update_scores(new_state, zoc) - update_scores(new_state, op_zoc))
                tree_nodes.append(tmp_child)
        elif order == "second" and not MY_TURN:
            acts = actions(self.state, op_zoc)
            for action in acts:
                tmp_state = apply_action(self.state, action)
                tmp_child = self.child_node(tmp_state, action)
                tmp_child.utility = tmp_child.parent.utility
                tree_nodes.append(tmp_child)
        return tree_nodes

    def child_node(self, state, action):
        """[Figure 3.10]"""
        return Node(state, self, action)

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


def apply_action(state, actions_list):
    new_state = pickle.loads(pickle.dumps(state,-1))
    if actions_list:
        if actions_list[0] in ['vaccinate', 'quarantine']:
            effect, location = actions_list[0], (actions_list[1][0] + 1, actions_list[1][1] + 1)
            if 'vaccinate' in effect:
                new_state[location] = 'I'
            elif 'quarantine' in effect:
                new_state[location] = 'Q0'
        else:
            for atomic_action in actions_list:
                effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                if 'vaccinate' in effect:
                    new_state[location] = 'I'
                elif 'quarantine' in effect:
                    new_state[location] = 'Q0'
    return new_state


def change_state(state):
    new_state = pickle.loads(pickle.dumps(state, -1))

    # virus spread
    for i in range(1, DIMENSIONS[0] + 1):
        for j in range(1, DIMENSIONS[1] + 1):
            if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                              'S' in state[(i + 1, j)] or
                                              'S' in state[(i, j - 1)] or
                                              'S' in state[(i, j + 1)]):
                new_state[(i, j)] = 'S1'

    # advancing sick counters
    for i in range(1, DIMENSIONS[0] + 1):
        for j in range(1, DIMENSIONS[1] + 1):
            if 'S' in state[(i, j)]:
                turn = int(state[(i, j)][1])
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


def update_scores(state, control_zone):
    score = 0
    for (i, j) in control_zone:
        if 'H' in state[(i, j)]:
            score += 1
        if 'I' in state[(i, j)]:
            score += 1
        if 'S' in state[(i, j)]:
            score -= 1
        if 'Q' in state[(i, j)]:
            score -= 5
    return score

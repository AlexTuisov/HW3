import random
from itertools import chain, combinations
from copy import deepcopy
import math
import time
import pickle

ids = ['307868208', '312360431']



class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.init_state = initial_state
        self.ZOC = zone_of_control
        self.rival_ZOC = self.rival_zone_of_control(zone_of_control, initial_state)
        if order == 'first':
            self.player = 0
        else:
            self.player = 1
        self.depth = 2
        self.my_ops = None
        self.rival_ops = None

        root = Node(initial_state, None, None, None, 0, self.player)
        root.depth = 0
        root.node_init_map()
        self.p_state = root


        self.start_time = 0

    def total_valid_ops(self, state):

        # my_ZOC = self.ZOC
        # rival_ZOC = self.rival_ZOC

        my_valid_ops = self.valid_actions(self, state, self.ZOC)
        rival_valid_ops = self.valid_actions(self, state, self.rival_ZOC)

        total_valid_ops = []  # all the combination of operations (I can take)X(rival can take)

        for i in my_valid_ops:
            for j in rival_valid_ops:
                total_valid_ops.append((i, j))
        return total_valid_ops

    def act(self, state):
        self.start_time = time.time()
        if self.player == 0:
            # we are first player
            if state == self.init_state:  # first run and we play first
                root = self.p_state
            else:
                updated_state = self.p_state.update_state_plus(state)
                root = Node(updated_state, self.p_state, None, None, 0, self.player)

            root.depth = 0
            # my_ZOC = self.ZOC
            # rival_ZOC = self.rival_ZOC
            my_valid_ops = self.valid_actions(root.state, self.ZOC)
            rival_valid_ops = self.valid_actions(root.state, self.rival_ZOC)

            # self.my_ops = deepcopy(my_valid_ops)
            self.my_ops = pickle.loads(pickle.dumps(my_valid_ops, -1))
            self.my_ops.append("N")
            # self.rival_ops = deepcopy(rival_valid_ops)
            self.rival_ops = pickle.loads(pickle.dumps(rival_valid_ops, -1))
            self.rival_ops.append("N")

            dest_node = self.tree_minimax_0_pruning(root, 0, True, -math.inf, math.inf)
            if dest_node == "TIME_OUT":
                dest_node = Node(None, root, my_valid_ops[0], None, 0, 0)
                dest_node.ops_execute(root.state)

        else:
            updated_state = self.p_state.update_state(state)
            root = Node(updated_state, self.p_state, None, None, 0, self.player)

            root.depth = 0
            # my_ZOC = self.ZOC
            # rival_ZOC = self.rival_ZOC
            my_valid_ops = self.valid_actions(root.state, self.ZOC)
            rival_valid_ops = self.valid_actions(root.state, self.rival_ZOC)

            # self.my_ops = deepcopy(my_valid_ops)
            self.my_ops = pickle.loads(pickle.dumps(my_valid_ops, -1))
            self.my_ops.append("N")
            # self.rival_ops = deepcopy(rival_valid_ops)
            self.rival_ops = pickle.loads(pickle.dumps(rival_valid_ops, -1))
            self.rival_ops.append("N")

            dest_node = self.tree_minimax_1_pruning(root, 0, True, -math.inf, math.inf)
            if dest_node == "TIME_OUT":
                dest_node = Node(None, root, my_valid_ops[0], None, 0, 0)
                dest_node.ops_execute(root.state)
                dest_node.update_map(self.p_state.state)

        self.p_state = dest_node
        return dest_node.action

    def tree_minimax_0_pruning(self, node, depth, maximizingPlayer, alpha, beta):
        if depth == 4:  # \or node.left_child == None:
            if time.time() - self.start_time > 4.96:
                return "TIME_OUT"
            node.set_score(self.ZOC, self.rival_ZOC)
            # print("tree_minimax_0 > last if > node.score", node.score)
            return node.score

        if maximizingPlayer:
            if time.time() - self.start_time > 4.97:
                return "TIME_OUT"
            maxEva = -math.inf
            lc = Node(None, node, self.my_ops[0], None, 0, 0)
            lc.depth = node.depth + 1
            lc.ops_execute(node.state)  # create its own map (after action)
            node.addChild(lc)

            for my_act in self.my_ops[1:]:
                # print("lc.action:", lc.action)
                eva = self.tree_minimax_0_pruning(lc, lc.depth, False, alpha, beta)
                if eva == "TIME_OUT":
                    return "TIME_OUT"
                if eva > maxEva:
                    dest_node = lc
                maxEva = max(maxEva, eva)
                # print("maxEva",maxEva)
                lc.score = maxEva
                alpha = max(alpha, maxEva)
                if beta <= alpha:
                    break
                if my_act != "N":
                    lc = Node(None, node, my_act, None, 0, 0)
                    lc.depth = node.depth + 1
                    lc.ops_execute(node.state)  # create its own map (after action)
                    node.left_child.addSibling(lc)
                    # node.addChild(lc)
                # print("tree_minimax_0 > if True > maxEva", maxEva)
            if lc.depth == 1:
                return dest_node
            else: return maxEva
            # return dest_node

        else:
            if time.time() - self.start_time > 4.97:
                return "TIME_OUT"
            minEva = math.inf
            lc2 = Node(None, node, self.rival_ops[0], None, 0, 1)
            lc2.depth = node.depth + 1
            lc2.ops_execute(node.state)
            lc2.update_map(node.parent.state)
            node.addChild(lc2)
            for rival_act in self.rival_ops[1:]:
                # print("lc2.action:", lc2.action)
                eva = self.tree_minimax_0_pruning(lc2, lc2.depth, True, alpha, beta)
                if eva == "TIME_OUT":
                    return "TIME_OUT"
                minEva = min(minEva, eva)
                beta = min(beta, minEva)
                if beta <= alpha:
                    break
                # lc.score = minEva
                # print("minEva", minEva)
                if rival_act != "N":
                    lc2 = Node(None, node, rival_act, None, 0, 1)
                    lc2.depth = node.depth + 1
                    lc2.ops_execute(node.state)
                    lc2.update_map(node.parent.state)
                    node.left_child.addSibling(lc2)
                    # node.addChild(lc)
                # print("tree_minimax_0 > if False > minEva", minEva)

            return minEva

    def tree_minimax_1_pruning(self, node, depth, maximizingPlayer, alpha, beta):
        if depth == 4:  # \or node.left_child == None:
            if time.time() - self.start_time > 4.96:
                return "TIME_OUT"
            node.set_score(self.ZOC, self.rival_ZOC)
            # print("tree_minimax_1 > last if > node.score", node.score)
            return node.score

        if maximizingPlayer:
            if time.time() - self.start_time > 4.97:
                return "TIME_OUT"
            maxEva = -math.inf
            lc = Node(None, node, self.my_ops[0], None, 0, 0)
            lc.depth = node.depth + 1
            lc.ops_execute(node.state)  # create its own map (after action)
            lc.update_map(node.parent.state)
            node.addChild(lc)
            for my_act in self.my_ops[1:]:
                # print("lc.action:", lc.action)
                eva = self.tree_minimax_1_pruning(lc, lc.depth, False, alpha, beta)
                if eva == "TIME_OUT":
                    return "TIME_OUT"
                if eva > maxEva:
                    dest_node = lc
                maxEva = max(maxEva, eva)
                # print("maxEva",maxEva)
                lc.score = maxEva
                alpha = max(alpha, maxEva)
                if beta <= alpha:
                    break
                if my_act != "N":
                    lc = Node(None, node, my_act, None, 0, 0)
                    lc.depth = node.depth + 1
                    lc.ops_execute(node.state)  # create its own map (after action)
                    lc.update_map(node.parent.state)
                    node.left_child.addSibling(lc)
                    # node.addChild(lc)
                # print("tree_minimax_1 > if True > maxEva", maxEva)
            if lc.depth == 1:
                return dest_node
            else: return maxEva
            # return dest_node

        else:
            if time.time() - self.start_time > 4.97:
                return "TIME_OUT"
            minEva = math.inf
            lc2 = Node(None, node, self.rival_ops[0], None, 0, 1)
            lc2.depth = node.depth + 1
            lc2.ops_execute(node.state)
            node.addChild(lc2)
            for rival_act in self.rival_ops[1:]:
                # print("lc2.action:", lc2.action)
                eva = self.tree_minimax_1_pruning(lc2, lc2.depth, True, alpha, beta)
                if eva == "TIME_OUT":
                    return "TIME_OUT"
                minEva = min(minEva, eva)
                beta = min(beta, minEva)
                if beta <= alpha:
                    break
                # lc.score = minEva
                # print("minEva", minEva)
                if rival_act != "N":
                    lc2 = Node(None, node, rival_act, None, 0, 1)
                    lc2.depth = node.depth + 1
                    lc2.ops_execute(node.state)
                    node.left_child.addSibling(lc2)
                    # node.addChild(lc)
                # print("tree_minimax_1 > if False > minEva", minEva)

            return minEva

    def powerset(self, actions_tuple, limit):
        st = tuple(actions_tuple)
        return tuple(chain.from_iterable(combinations(st, r) for r in range(limit + 1)))[1:]

    def rival_zone_of_control(self, zone_of_control, state):
        rival_ZOC_list = []
        state_columns = len(state)
        state_rows = len(state[0])

        for row in range(state_rows):
            for col in range(state_columns):
                if state[row][col] != 'U' and (row, col) not in zone_of_control:
                    rival_ZOC_list.append((row, col))
        return rival_ZOC_list

    def valid_actions(self, state, zone_of_control):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        vac_actions_tuple = ()
        quar_actions_tuple = ()

        # Extract medics and police teams
        m = 1
        p = 2

        row_num = len(state)
        col_num = len(state[0])

        for cord in zone_of_control:
            if state[cord[0]][cord[1]] == 'H':
                vac_actions_tuple += (("vaccinate", (cord[0], cord[1])),)
            if state[cord[0]][cord[1]][0] == 'S':
                quar_actions_tuple += (("quarantine", (cord[0], cord[1])),)

        profit_q = ()
        for sick in quar_actions_tuple:
            row = sick[1][0]
            col = sick[1][1]
            if row + 1 != row_num and row - 1 >= 0 and col + 1 != col_num and col - 1 >= 0:
                if ("vaccinate", ([row + 1], [col])) in vac_actions_tuple and \
                        ("vaccinate", ([row - 1], [col])) in vac_actions_tuple and \
                        ("vaccinate", ([row], [col + 1])) in vac_actions_tuple and \
                        ("vaccinate", ([row], [col - 1])) in vac_actions_tuple:
                    profit_q += sick
        quar_actions_tuple = profit_q

        # print("vac_actions_tuple:",vac_actions_tuple)
        len_vac_actions_tuple = len(vac_actions_tuple)
        len_quar_actions_tuple = len(quar_actions_tuple)

        if len_vac_actions_tuple < m and len_vac_actions_tuple != 0:
            m = len_vac_actions_tuple
        if len_quar_actions_tuple < p and len_quar_actions_tuple != 0:
            p = len_quar_actions_tuple

        quar_power_set = self.powerset(quar_actions_tuple, p)
        # vac_power_set = self.powerset(vac_actions_tuple, m)
        # print("vac_power_set:", vac_power_set)
        valid_actions_list = []
        qq_list = []
        qqi_list = []
        # i_list = []

        for qat in quar_actions_tuple:
            valid_actions_list.append([qat])

        if len_vac_actions_tuple == 0:
            for qps in quar_power_set:
                q_list = []
                if len(qps) > 1:
                    for q_act in qps:
                        q_list.append(q_act)
                    valid_actions_list.append(q_list)
        if len_quar_actions_tuple == 0:
            for vps in vac_actions_tuple:
                valid_actions_list.append([vps])
        if len_quar_actions_tuple > 0 and len_vac_actions_tuple > 0:
            flag = True
            for vps in vac_actions_tuple:
                valid_actions_list.append([vps])
                for qps in quar_power_set:
                    if flag:
                        if len(qps) > 1:
                            ql = []
                            for q in qps:
                                ql.append(q)
                            qq_list.append(ql)
                    operation_list = []
                    operation_list.append(vps)
                    if len(qps) > 1:
                        for q_act in qps:
                            operation_list.append(q_act)
                        qqi_list.append(operation_list)
                flag = False
        # print("qq_list", qq_list)
        # print("qqi_list", qqi_list)
        valid_actions_list.append([])
        valid_actions_list = qq_list + qqi_list + valid_actions_list
        random.shuffle(valid_actions_list)
        # print("valid_actions_list", valid_actions_list)

        return valid_actions_list


class Node:

    def __init__(self, state=None, parent=None, action=None, right_sib=None, score=0, order=None, left_child=None):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.left_child = left_child
        self.right_sib = right_sib
        self.action = action
        self.score = score
        self.depth = 0
        self.order = order
        if parent:
            self.depth = parent.depth + 1

    def addSibling(self, newSib): # Add Sibling Node to a Node
        if (self == None):
            print("cant add sibling to non existing node")
            return None

        while (self.right_sib):
            self = self.right_sib  # go to the last sibling

        self.right_sib = newSib  # add to the last one a new sib
        # return self.Next

    def addChild(self, newChild):  # Add child Node to a Node
        if (self == None):
            print("cant add child to non existing node")
            return None

        self.left_child = newChild
        # return n.child

    def update_own_score(self, control_zone):
        own_score = 0
        for cord in control_zone:
            if self.state[cord[0]][cord[1]][0] == 'H':
                own_score += 1
            if self.state[cord[0]][cord[1]][0] == 'I':
                own_score += 1
            if self.state[cord[0]][cord[1]][0] == 'S':
                own_score -= 1
            if self.state[cord[0]][cord[1]][0] == 'Q':
                own_score -= 5
        return own_score

    def set_score(self, ZOC, rival_ZOC):
        my_score = self.update_own_score(ZOC)
        rival_score = self.update_own_score(rival_ZOC)
        self.score = (my_score - rival_score)

    def ops_execute(self, parent_state):
        # temp_state = deepcopy(parent_state)
        temp_state = pickle.loads(pickle.dumps(parent_state, -1))
        op = self.action
        for act in op:
            if act[0] == 'quarantine':
                temp_state[act[1][0]][act[1][1]] = 'Q1'
            elif act[0] == 'vaccinate':
                temp_state[act[1][0]][act[1][1]] = 'I'

        self.state = temp_state

    def node_init_map(self):
        # new_state = deepcopy(self.state)
        new_state = pickle.loads(pickle.dumps(self.state, -1))

        row_num = len(self.state)
        col_num = len(self.state[0])
        for row in range(row_num):
            for col in range(col_num):
                if self.state[row][col] == 'S':
                    new_state[row][col] = 'S1'
                elif self.state[row][col] == 'Q':
                    new_state[row][col] = 'Q1'
        self.state = new_state

    def update_map(self, parent_state):
        # new_state = deepcopy(self.state)
        new_state = pickle.loads(pickle.dumps(self.state, -1))
        row_num = len(self.state)
        col_num = len(self.state[0])

        # Virus spread
        for row in range(row_num):
            for col in range(col_num):
                if self.state[row][col] == 'H':
                    sick_neighbor = []
                    if row + 1 != row_num:
                        sick_neighbor.append(self.state[row + 1][col][0])  # Sick neighbor at previous time
                    if row - 1 >= 0:
                        sick_neighbor.append(self.state[row - 1][col][0])
                    if col + 1 != col_num:
                        sick_neighbor.append(self.state[row][col + 1][0])
                    if col - 1 >= 0:
                        sick_neighbor.append(self.state[row][col - 1][0])

                    if 'S' in sick_neighbor:
                        new_state[row][col] = 'S1'

        # Advancing S/Q counters
        for row in range(row_num):
            for col in range(col_num):
                # Advancing sick counters
                if self.state[row][col][0] == parent_state[row][col][0] == 'S':
                    turn = int(self.state[row][col][1])
                    if turn < 3:
                        new_state[row][col] = 'S' + str(turn + 1)
                    else:
                        new_state[row][col] = 'H'

                # Advancing quarantine counters
                if self.state[row][col][0] == parent_state[row][col][0] == 'Q':
                    turn = int(self.state[row][col][1])
                    if turn < 2:
                        new_state[row][col] = 'Q' + str(turn + 1)
                    else:
                        new_state[row][col] = 'H'
        self.state = new_state

    def update_state(self, given_state):
        state_columns = len(given_state)
        state_rows = len(given_state[0])

        for row in range(state_rows):
            for col in range(state_columns):
                if self.state[row][col][0] == given_state[row][col]:
                    if given_state[row][col] == 'Q' or given_state[row][col] == 'S':
                        given_state[row][col] = self.state[row][col]
                else:
                    if given_state[row][col] == 'Q':
                        given_state[row][col] = 'Q1'
        return given_state

    def update_state_plus(self, given_state):
        state_columns = len(given_state)
        state_rows = len(given_state[0])

        for row in range(state_rows):
            for col in range(state_columns):
                if self.state[row][col][0] == given_state[row][col]:
                    if given_state[row][col] == 'Q' or given_state[row][col] == 'S':
                        given_state[row][col] = self.state[row][col][0] + str(int(self.state[row][col][1]) + 1)
                else:
                    if given_state[row][col] == 'Q':
                        given_state[row][col] = 'Q1'
                    elif given_state[row][col] == 'S':
                        given_state[row][col] = 'S1'
        return given_state
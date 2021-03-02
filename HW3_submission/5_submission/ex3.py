import main
import utils
import random
from itertools import product

ids = ['318864436','205704752']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.initState = initial_state
        self.rows = len(self.initState)
        self.cols = len(self.initState[0])
        self.rival_zoc = list()
        self.last_state = dict()
        self.map_dict = dict()
        pos_inf = float('inf')
        neg_inf = float('-inf')

        # make dict for all map
        for row in range(self.rows):
            for col in range(self.cols):
                self.map_dict[(row, col)] = (self.initState[row][col], 0)
        # make list for the rival zoc
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in self.zoc:
                    self.rival_zoc.append((row, col))

        self.init_state_as_pad_dict = main.pad_the_input(initial_state)
        if self.order == 'first':
            self.rival_max, self.next_map, self.next_act = miniMax(self.map_dict, True, [], self.zoc, self.rival_zoc,
                                                                   self.order, 2, neg_inf, pos_inf)

    def act(self, state):
        map_dict = dict()
        rows = len(state)
        cols = len(state[0])
        pos_inf = float('inf')
        neg_inf = float('-inf')
        for row in range(rows):
            for col in range(cols):
                map_dict[(row, col)] = (state[row][col], 0)

        if self.last_state:
            for key, value in map_dict.items():
                #print('val',value)
                if 'S' in value and 'S' in self.last_state[key]:
                    day=self.last_state[key][1]
                    map_dict[key] = (value[0],  day+ 1)
                if 'Q' in value and 'Q' in self.last_state[key]:
                    day = self.last_state[key][1]
                    map_dict[key] = (value[0], day + 1)
        self.last_state = map_dict

        if map_dict == self.map_dict and self.order == 'first':
            return self.next_act
        else:
            if self.order == 'first':
                rival_max, next_map, next_act = miniMax(map_dict, True, [], self.zoc, self.rival_zoc, self.order, 2,
                                                        neg_inf, pos_inf)
            else:
                rival_max, next_map, next_act = miniMax(map_dict, True, [], self.zoc, self.rival_zoc, self.order, 2,
                                                        neg_inf, pos_inf)

        return next_act



def miniMax(state, is_max, action, zoc, other_zoc, order, depth, al, be):
    inf_pos,inf_neg = float('inf'),float('-inf')
    best_node,best_action = state,action

    if depth == 0:
        #score to state
        p_me, p_rival = 0, 0
        for k in state.keys():
            if state[k][0] == 'S':
                if k in zoc:
                    p_me -= 1
                else:
                    p_rival -= 1
            elif state[k][0] == 'Q':
                if k in zoc:
                    p_me -= 5
                else:
                    p_rival -= 5
            elif state[k][0] in ['I', 'H']:
                if k in zoc:
                    p_me += 1
                else:
                    p_rival += 1
            res = p_me - p_rival
        return res, state, action

    if order == 'first' and is_max :
        maximum = inf_neg
        nodes_max = children_after_state(state, zoc)
        best_value = maximum
        if len(nodes_max)==0:
            return maximum, nodes_max, action

        for actions, node in nodes_max.items():

            val_node_after, node_after, action_node_after = miniMax(node, False, actions, zoc, other_zoc, order, depth - 1, al, be)
            if maximum>val_node_after:
                best_value, best_node, best_action = maximum,node,actions
            else:
                best_value, best_node, best_action = val_node_after,node_after,action_node_after

            al = max(al, val_node_after)
            if be <= al: #pruning
                break
        return best_value, best_node, best_action

    elif not is_max and order == 'first':
        minimum = inf_pos
        nodes_min = children_after_state(state, other_zoc)
        best_value = minimum
        if not nodes_min:
            return minimum, nodes_min, action
        for actions, node in nodes_min.items():
            change_node_after = do_change(node)
            val_node_after,node_after,action_node_after = miniMax(change_node_after, True, actions, zoc, other_zoc, order, depth - 1, al, be)

            if minimum< val_node_after:
                best_value, best_node, best_action = minimum,node,actions
            else:
                best_value, best_node, best_action =val_node_after,node_after,action_node_after
            be = min(be, val_node_after)

            if be <= al:
                break
        return best_value, best_node, action

    elif is_max and order == 'second':
        maximum = inf_neg
        nodes_max = children_after_state(state, zoc)
        best_value = maximum
        if not nodes_max:
            return maximum, nodes_max, action
        for actions, node in nodes_max.items():
            change_node_after = do_change(node)
            val_node_after, node_after, action_node_after = miniMax(change_node_after, False, actions, zoc, other_zoc, order, depth - 1, al, be)
            if maximum>val_node_after:
                best_value, best_node, best_action=maximum,node,actions
            else:
                best_value, best_node, best_action=val_node_after,node_after,action_node_after

            al = max(al, val_node_after)
            if be <= al: #pruning
                break
        return best_value, best_node, best_action

    # rival is first
    elif not is_max and order == 'second':
        minimum = inf_pos
        nodes_min = children_after_state(state, other_zoc)
        best_value = minimum
        if not nodes_min:
            return minimum, nodes_min, action
        for actions, node in nodes_min.items():
            val_node_after,node_after,action_node_after = miniMax(node, True, actions, zoc, other_zoc, order, depth - 1, al, be)
            if minimum< val_node_after:
                best_value, best_node, best_action = minimum,node,actions
            else:
                best_value, best_node, best_action =val_node_after,node_after,action_node_after

            be = min(be, val_node_after)
            if be <= al:
                break
        return best_value, best_node, action


def possible_actions(state, zoc):
    to_vaccinate,to_quarantine,all_to_vaccinate,all_to_quarantine = list(),list(),list(),list()
    result = list()
    l1, l2, l3 = list(), list(), list()
    r, c = 9, 9
    lfinal = list()

    for z in zoc:
        row_in_zoc,col_in_zoc=z[0],z[1]
        condition=state[z][0]
        if condition == 'S':
            all_to_quarantine.append(("quarantine", z))
            isH = 0
            if col_in_zoc - 1 >= 0:
                isH = isH + 1 if 'H' in state[(row_in_zoc, col_in_zoc - 1)] else isH
            if row_in_zoc - 1 >= 0:
                isH = isH + 1 if 'H' in state[(row_in_zoc - 1, col_in_zoc)] else isH
            if col_in_zoc + 1 <= c - 1:
                isH = isH + 1 if 'H' in state[(row_in_zoc, col_in_zoc + 1)] else isH
            if row_in_zoc + 1 <= r - 1:
                isH = isH + 1 if 'H' in state[(row_in_zoc + 1, col_in_zoc)] else isH

            if isH >= 3:
                to_quarantine.append(("quarantine", z))

        elif condition == 'H':
            all_to_vaccinate.append(("vaccinate", z))

            if row_in_zoc + 1 <= r - 1 and 'S' in state[(row_in_zoc+1,col_in_zoc)]:
                to_vaccinate.append(("vaccinate", z))
                continue
            if col_in_zoc + 1 <= c -1 and 'S' in state[(row_in_zoc,col_in_zoc+1)]:
                to_vaccinate.append(("vaccinate", z))
                continue
            if col_in_zoc - 1 >= 0 and 'S' in state[(row_in_zoc,col_in_zoc-1)]:
                to_vaccinate.append(("vaccinate", z))
                continue
            if row_in_zoc - 1 >= 0 and 'S' in state[(row_in_zoc-1,col_in_zoc)]:
                to_vaccinate.append(("vaccinate", z))
                continue


    if not to_vaccinate:
        if len(all_to_vaccinate)>0 and len(all_to_vaccinate) > 5:
            to_vaccinate = random.sample(all_to_vaccinate, 5)

    if not to_vaccinate and not to_quarantine:
        return list()

    elif not to_vaccinate:
        for q in all_to_quarantine:
            result.append([q])
        return result

    elif not to_quarantine:
        for v in to_vaccinate:
            result.append([v])
        return result


    for v in to_vaccinate:
        result.append([v])


    for i in product(to_vaccinate, to_quarantine):
        l1.append(i)
    result.extend(l1)

    for i in all_combs(to_quarantine, 2):
        l3.append(i)
    for i in product(to_vaccinate, l3):
        l2.append(i)

    for i in l2:
        lfinal.append((i[0], i[1][0], i[1][1]))
    result.extend(lfinal)

    return result


def do_change(state):
    list_S,list_Q,list_H = list(), list(),list()
    result = dict()
    r,c = 9,9
    newQ = list()
    l1 = list()
    for k, v in state.items():

        if v[0] == 'S':
            list_S.append(k)
        if v[0] == 'Q':
            list_Q.append(k)
        if v[0] == 'H':
            list_H.append(k)
        result[k] = v

    for i in list_S:
        l1.append(decide_neighbors(i,r,c,list_H))

    for i in list_S:
        if i not in l1:
            tmp1 = result[i][1]
            if tmp1 >= 2:
                result[i] = ('H', 0)
                list_H.append(i)
                list_S.remove(i)
            else:
                result[i] = ('S', tmp1 + 1)
    for i in l1:
        result[i] = ('S', 0)
        if i in list_H:
            list_H.remove(i)
            list_S.append(i)

    for k,v in state.items():
        if v == ('Q',None):
            newQ.append(k)
            result[k] = ('Q', 0)

    for i in list_Q:
        if i not in newQ:
            tmp2 =result[i][1]
            if tmp2 >= 1:
                result[i] = ('H', 0)
                list_H.append(i)
                list_Q.remove(i)
            else:
                result[i] = ('Q', tmp2 + 1)


    return utils.hashabledict(result)


def children_after_state(state, zoc):
    result = dict()
    res = state.copy()
    pos_actions = possible_actions(state, zoc)
    for action in pos_actions:
        pos=tuple(action)
        for i in (action):
            act=i[0]
            loc=(i[1][0],i[1][1])
            row, col = loc[0], loc[1]
            if act == 'vaccinate':
                res[(row, col)] = ('I', 0)
            elif act == 'quarantine':
                res[(row, col)] = ('Q', None)
        result[pos] = res
    return result


def decide_neighbors(index, row, col, lst):
    if index[1] + 1 < col and (index[0], index[1] + 1) in lst:
        return (index[0], index[1] + 1)
    if index[0] + 1 < row and (index[0] + 1, index[1]) in lst:
        return (index[0] + 1, index[1])
    if index[0] != 0 and (index[0] - 1, index[1]) in lst:
        return (index[0] - 1, index[1])
    if index[1] != 0 and (index[0], index[1] - 1) in lst:
        return (index[0], index[1] - 1)


def all_combs(a, tlen, a_before=None, len_a_before=0):
    combs = list()
    if a_before is None:
        a_before = list()
    if len_a_before == tlen:
        return [a_before]

    for i, val in enumerate(a):
        a_before_extended = a_before.copy()
        a_before_extended.append(val)
        next=i+1
        combs += all_combs(a[next:], tlen, a_before_extended, len(a_before_extended))
    return combs














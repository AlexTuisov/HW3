import random
from itertools import product
import utils

ids = ['204585301','311156327']



def Actions(state, zoc):
    rowsNum = 9
    colsNum = 9
    vaccinate_lst = []
    quarantine_lst = []
    full_vaccinate = []
    full_quarantine = []


    for pos in zoc:
    #for pos,value in state.items():
        value = state[pos]
        if value[0] == 'H':
            full_vaccinate.append(("vaccinate", pos))
            if pos[0] - 1 >= 0:
                if 'S' in state[(pos[0]-1,pos[1])]:
                    vaccinate_lst.append(("vaccinate", pos))
                    continue
            if pos[0] + 1 <= rowsNum - 1:
                if 'S' in state[(pos[0]+1,pos[1])]:
                    vaccinate_lst.append(("vaccinate", pos))
                    continue
            if pos[1] - 1 >= 0:
                if 'S' in state[(pos[0],pos[1]-1)]:
                    vaccinate_lst.append(("vaccinate", pos))
                    continue
            if pos[1] + 1 <= colsNum -1 :
                if 'S' in state[(pos[0],pos[1]+1)]:
                    vaccinate_lst.append(("vaccinate", pos))
                    continue
        elif value[0] == 'S':
            full_quarantine.append(("quarantine", pos))
            h_counter = 0
            if pos[0] - 1 >= 0:
                if 'H' in state[(pos[0]-1,pos[1])]:
                    h_counter += 1
            if pos[0] + 1 <= rowsNum - 1:
                if 'H' in state[(pos[0]+1,pos[1])]:
                    h_counter += 1
            if pos[1] - 1 >= 0:
                if 'H' in state[(pos[0],pos[1]-1)]:
                    h_counter += 1
            if pos[1] + 1 <= colsNum -1:
                if 'H' in state[(pos[0],pos[1]+1)]:
                    h_counter += 1
            if h_counter >= 3:
                quarantine_lst.append(("quarantine", pos))

    Combinations_lst = []

    if not vaccinate_lst:
        if full_vaccinate:
            if len(full_vaccinate) > 5:
                vaccinate_lst = random.sample(full_vaccinate, 5)

    if not vaccinate_lst and not quarantine_lst:
        return []
    elif not vaccinate_lst:
        for quarantine in full_quarantine:
            Combinations_lst.append([quarantine])
        return Combinations_lst
    elif not quarantine_lst:
        for vaccinate in vaccinate_lst:
            Combinations_lst.append([vaccinate])
        return Combinations_lst


    for vaccinate in vaccinate_lst:
        Combinations_lst.append([vaccinate])

    list_one = [i for i in product(vaccinate_lst, quarantine_lst)]
    Combinations_lst.extend(list_one)

    couple_list_tmp = [i for i in combinationsList(quarantine_lst, 2)]
    double_lst = [i for i in product(vaccinate_lst, couple_list_tmp)]
    double_lst = [(i[0], i[1][0], i[1][1]) for i in double_lst]
    Combinations_lst.extend(double_lst)

    Combinations_lst = [list(i) for i in Combinations_lst]
    return Combinations_lst


def execute_action(state, actions):
    state_cp = state.copy()
    for action in actions:
        eff, loc = action[0], (action[1][0], action[1][1])
        row = loc[0]
        col = loc[1]
        if 'v' in eff:
            state_cp[(row,col)] = ('I',0)
        else:
            state_cp[(row,col)] = ('Q',None)
    return state_cp


def change_state(state):
    rows = 9
    columns = 9
    list_S = list()
    list_Q = list()
    list_H = list()
    new_dict = {}

    list_Q_new = list()
    for pos, value in state.items():
        new_dict[pos] = value
        if str(value[0]) == 'H':
            list_H = list_H + [pos]
        if str(value[0]) == 'S':
            list_S = list_S + [pos]
        if str(value[0]) == 'Q':
            list_Q = list_Q + [pos]

    for pos,value in state.items():
        if value == ('Q',None):
            new_dict[pos] = ('Q', 0)
            list_Q_new = list_Q_new + [pos]

    list1 = list()
    for i in list_S:
        if int(i[0] + 1) < rows and (int(i[0] + 1), i[1]) in list_H:
            list1 = list1 + [(int(i[0] + 1), i[1])]
        if int(i[0]) != 0 and (int(i[0] - 1), i[1]) in list_H:
            list1 = list1 + [(int(i[0] - 1), i[1])]
        if int(i[1] + 1) < columns and (i[0], int(i[1] + 1)) in list_H:
            list1 = list1 + [(i[0], int(i[1] + 1))]
        if int(i[1]) != 0 and (i[0], int(i[1] - 1)) in list_H:
            list1 = list1 + [(i[0], int(i[1] - 1))]
    for a in list1:
        new_dict[a] = ('S', 0)
        if a in list_H:
            list_H.remove(a)
            list_S.append(a)
    for j in list(list_S):
        if j not in list1:
            temp = int(new_dict[j][1])
            if int(temp + 1) >= 3:
                new_dict[j] = ('H', 0)
                list_H.append(j)
                list_S.remove(j)
            else:
                new_dict[j] = ('S', int(temp + 1))
    for p in list_Q:
        if p not in list_Q_new:
            temp = int(new_dict[p][1])
            if int(temp + 1) >= 2:
                new_dict[p] = ('H', 0)
                list_H.append(p)
                list_Q.remove(p)
            else:
                new_dict[p] = ('Q', int(temp + 1))
    return utils.hashabledict(new_dict)


def eval_state(state, zoc):
    myPoints = 0
    rivalPoints = 0

    for pos,value in state.items():
        if value[0] == 'I' or value[0] == 'H':
            if pos in zoc:
                myPoints = myPoints + 1
            else:
                rivalPoints = rivalPoints + 1
        elif value[0] == 'S':
            if pos in zoc:
                myPoints = myPoints -1
            else:
                rivalPoints = rivalPoints - 1
        elif value[0] == 'Q':
            if pos in zoc:
                myPoints = myPoints - 5
            else:
                rivalPoints = rivalPoints - 5
    return myPoints - rivalPoints


def combinationsList(array, tuple_length, prev_array=None):
    if prev_array is None:
        prev_array = []
    if len(prev_array) == tuple_length:
        return [prev_array]
    combs = []
    for i, val in enumerate(array):
        prev_array_extended = prev_array.copy()
        prev_array_extended.append(val)
        combs += combinationsList(array[i + 1:], tuple_length, prev_array_extended)
    return combs

def ChildrenOfState(state, zoc):
    childrens_dict = {}

    actions_lst = Actions(state, zoc)
    for actions in actions_lst:
        post_action_state = execute_action(state, actions)
        childrens_dict[tuple(actions)] = post_action_state
    return childrens_dict

def max_child_and_val(child1, val1, action1, child2, val2, action2):
    if val1 > val2:
        return val1, child1, action1
    else:
        return val2, child2, action2

def min_child_and_val(child1, val1, action1, child2, val2, action2):
    if val1 < val2:
        return val1, child1, action1
    else:
        return val2, child2, action2

def miniMax(state, my_zoc, not_my_zoc, order, depth, alpha, beta, maximizingPlayer, max_action):
    posInfinity = float('inf')
    negInfinity = float('-inf')
    chosen_child = state
    chosen_action = max_action
    if depth == 0:
        return eval_state(state, my_zoc), state, max_action

    if maximizingPlayer and order == 'first':
        maxEval = negInfinity
        allMaxPlayerChildren = ChildrenOfState(state, my_zoc)
        chosen_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval, allMaxPlayerChildren, max_action
        for actions, child in allMaxPlayerChildren.items():
            GrandchildVal, grandChild, GChildAction = miniMax(child, my_zoc, not_my_zoc, order, depth - 1, alpha, beta, False, actions)
            chosen_val, chosen_child, chosen_action = max_child_and_val(child, maxEval, actions, grandChild, GrandchildVal, GChildAction)
            #chosen_val,chosed_child = max_child_and_val(child, maxEval, grandChild, GrandchildVal)
            #maxEval = max(maxEval, GrandchildVal)
            alpha = max(alpha, GrandchildVal)
            if beta <= alpha:
                break
        return chosen_val, chosen_child, chosen_action

    elif maximizingPlayer and order == 'second':
        maxEval = negInfinity
        allMaxPlayerChildren = ChildrenOfState(state, my_zoc)
        #print('len(All max players children when Im second)', len(allMaxPlayerChildren))
        chosen_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval, allMaxPlayerChildren, max_action
        for actions, child in allMaxPlayerChildren.items():
            childAfterChange = change_state(child)
            GrandchildVal, grandChild, GChildAction = miniMax(childAfterChange, my_zoc, not_my_zoc, order, depth - 1, alpha, beta, False, actions)
            chosen_val, chosen_child, chosen_action = max_child_and_val(childAfterChange, maxEval,actions, grandChild, GrandchildVal,GChildAction)
            alpha = max(alpha, GrandchildVal)
            if beta <= alpha:
                break
        return chosen_val, chosen_child, chosen_action

    elif not maximizingPlayer and order == 'second':
        minEval = posInfinity
        min_children = ChildrenOfState(state, not_my_zoc)
        chosen_val = minEval
        if not min_children:
            return minEval, min_children, max_action
        for actions, child in min_children.items():
            #print("in min second")
            GrandchildVal,grandChild,GChildAction = miniMax(child, my_zoc, not_my_zoc, order, depth - 1, alpha, beta, True, actions)
            #minEval = min(minEval, GrandchildVal)
            chosen_val,chosen_child,chosen_action = min_child_and_val(child,minEval,actions,grandChild,GrandchildVal,GChildAction)
            beta = min(beta, GrandchildVal)
            if beta <= alpha:
                break
        return chosen_val, chosen_child, max_action

    elif not maximizingPlayer and order == 'first':  # rival is second
        minEval = posInfinity
        min_children = ChildrenOfState(state, not_my_zoc)
        #print('len(allMinPlayerChildren when Im first)', len(allMinPlayerChildren))
        chosen_val = minEval
        if not min_children:
            return minEval, min_children, max_action
        for actions, child in min_children.items():
            childAfterChange = change_state(child)
            GrandchildVal,grandChild,GChildAction = miniMax(childAfterChange, my_zoc, not_my_zoc, order, depth - 1, alpha, beta, True, actions)
            #minEval = min(minEval, GrandchildVal)
            chosen_val, chosen_child, chosen_action = min_child_and_val(childAfterChange, minEval, actions, grandChild, GrandchildVal, GChildAction)
            beta = min(beta, GrandchildVal)
            if beta <= alpha:
                break
        return chosen_val, chosen_child, max_action


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        self.state_prev = {}
        self.state_dict = {}
        self.my_zoc = zone_of_control
        self.not_my_zoc = []
        self.init_state = initial_state

        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                self.state_dict[(i, j)] = (initial_state[i][j], 0)
                if (i, j) not in self.my_zoc:
                    self.not_my_zoc.append((i, j))


        inf = float('inf')
        neg_inf = float('-inf')
        if self.order == 'first':
            self.best_val, self.best_state, self.best_action = miniMax(self.state_dict, self.my_zoc, self.not_my_zoc, self.order, 2, neg_inf, inf,
                                                                       True, [])


    def list_to_dict(self,state):
        new_dict = {}
        for i in range(len(state)):
            for j in range(len(state[0])):
                new_dict[(i, j)] = (state[i][j], 0)
        return new_dict

    def act(self, state):
        state_dict = self.list_to_dict(state).copy()

        if self.state_prev:
            for pos,value in state_dict.items():
                if 'S' in value:
                    if 'S' in self.state_prev[pos]:
                        state_dict[pos] = ('S', self.state_prev[pos][1] + 1)
                elif 'Q' in value:
                    if 'Q' in self.state_prev[pos]:
                        state_dict[pos] = ('Q', self.state_prev[pos][1] + 1)
        self.state_prev = state_dict

        inf = float('inf')
        neg_inf = float('-inf')

        if state_dict == self.state_dict and self.order == 'first':
            return self.best_action

        else:
            if self.order == 'second':
                best_value, best_state, best_action = miniMax(state_dict, self.my_zoc, self.not_my_zoc, self.order, 2, neg_inf, inf,
                                                         True, [])
            else:
                best_value, best_state, best_action = miniMax(state_dict, self.my_zoc, self.not_my_zoc, self.order, 2, neg_inf, inf, True, [])

        return best_action



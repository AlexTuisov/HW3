import random
from collections import namedtuple, Counter, defaultdict
import random
import math
import functools
from copy import deepcopy

cache = functools.lru_cache(10**6)
from itertools import combinations, product
ids = ['318539103', '302816863']
infinity = math.inf

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc=zone_of_control
    def act(self, state):
        g=Game2(self.zoc)
        move2=[]
        _,move=h_alphabeta_search(g, state)
        action=move
        if action==None:
            return[]
        if 'quarentine' in action:
            varq = action[0]
        elif 'quarentine' in action[0]:
            varq = action[0][1]
        else:
            varq = []
        if 'vaccinate' in action:
            varv = action[1]
        elif 'vaccinate' in action[1]:
            varv = action[1][1]
        else:
            varv = []
        for var in varq:
            i = var[0]
            j = var[1]
            move2.append(('quarantine',(i,j)))
        for var in varv:
            ii = var[0]
            jj = var[1]
            move2.append(('vaccinate',(ii,jj)))

        return move2


class Game2:
    """A game is similar to a problem, but it has a terminal test instead of
    a goal test, and a utility for each terminal state. To create a game,
    subclass this class and implement `actions`, `result`, `is_terminal`,
    and `utility`. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""
    def __init__(self,zone_of_control):
        self.zoc=zone_of_control
        self.score=0
    def actions(self, state):
        """Return a collection of the allowable moves from this state."""
        # find all s and then insert the new ss to 'seakness_index_map'

        # make S's index list
        comb_list_S = get_comb_list(self, 'S', state,2,self.zoc)
        comb_list_S1 = get_comb_list(self, 'S', state, 1, self.zoc)
        # make H's index list
        comb_list_H = get_comb_list(self, 'H', state,1,self.zoc)

        # combined S an H
        if comb_list_H==-1 or comb_list_S==-1:
            combHS2=[]
        else:
            combHS2 = list(product(comb_list_S, comb_list_H))
        if comb_list_H == -1 or comb_list_S1 == -1:
            combHS1 = []
        else:
            combHS1 = list(product(comb_list_S1, comb_list_H))
        if combHS1 != -1:
            combHS2.extend(combHS1)
        if comb_list_S != -1:
            combHS2.extend(comb_list_S)
        if comb_list_S != -1:
            combHS2.extend(comb_list_S)
        if comb_list_H!=-1:
            combHS2.extend(comb_list_H)
        return tuple(combHS2)


    def result(self, state, action):
        """Return the state that results from making a move from a state."""
        # print(action)
        # print(state[0])
        seakness_index_map = {}
        x = find_all_map(self, 'S', state)
        q_index_map = {}
        y = find_all_map(self, 'Q', state)
        tuples = []
        tupleq = []
        for i, v in enumerate(x):
            tuples.append(tuple([0, v[0], v[1]]))
        for i, v in enumerate(y):
            tuples.append(tuple([0, v[0], v[1]]))
        tuples = tuple(tuples)
        tupleq = tuple(tupleq)
        state1 = (state, tuples, tupleq)

        state_a = action911(self, state1, action)
        # print("state a")
        # print(state_a[0])
        state_s = spreading(self, state_a)
        # print("state s")
        # print(state_s[0])
        state_out = illness_expired(self, state_s)
        # print("state_out")
        # print(state_out[0])
        self.state=state_out[0]
        return state_out[0]

    def is_terminal(self, state):
        """Return True if this is a final state for the game."""
        x=find_all_map(self,'S',state)
        if len(x)>0:
            return False
        else:
            return True
        return not self.actions(state)

    def utility(self, state, player):
        """Return the value of this final state to player."""
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                self.score += 1
            if 'I' in state[i][j]:
                self.score += 1
            if 'S' in state[i][j]:
                self.score -= 1
            if 'Q' in state[i][j]:
                self.score -= 5



def get_comb_list(self, Letter, state,NUM,zoc):
    #
    index_list = find_all_map(self, Letter, state)
    index_list2=list(set(index_list).intersection(self.zoc))
    if len(index_list2)-1 > NUM:
        if Letter == 'S':
            health_list = []
            for index in index_list2:
                #s index (i,j)
                healthy_neighbors = find_all_healthy_neighbors(state, index)#counter of healthy neighbors areas
                health_list.append((index, healthy_neighbors))
            min = 10
            for i in health_list:
                if i[1] < min:
                    min = i[1]
            index_ = health_list
            my_sorted_tuple = tuple(sorted(health_list, key=lambda item: item[1]))
            list_sorted = list(my_sorted_tuple)
            for i in range(len(health_list)):
                if i == len(health_list)-3:
                    break
                index_list2.pop(index_list2.index(list_sorted[i][0]))
    else:
        return -1

    comb = combinations(index_list2, NUM)
    comb_l = tuple(comb)
    comb_list = []
    for var in comb_l:
        if Letter == 'S':
            comb_list.append(("quarentine", var))
        else:
            comb_list.append(("vaccinate", var))
    return comb_list

def find_all_tuple(tuple_of_S, Letter):
    # find all letters in a tuple
    var = tuple_of_S
    j = []
    i = 0
    fromm = 0
    while (Letter in var[fromm:]):
        j.append(var[fromm:].index(Letter) + fromm)
        fromm = j[i] + 1
        i = i + 1
    return j

def find_all_map(self, Letter, state):
    # find all letters in a map
    index_list = []
    for var in state:
        i = state.index(var)
        if Letter in var:
            j = find_all_tuple(var, Letter)
        else:
            continue
        for js in j:
            index_list.append((i, js))  # Get all combinations of [1, 2, 3]
    return index_list

def action911(self, state, action):
    state_out = list(state)
    q_index_map = list(state[2])
    q_index_map2 = []
    seakness_index_map = list(state[1])
    seakness_index_map2 = []
    for v in q_index_map:
        q_index_map2.append((v[0] + 1, v[1], v[2]))
    if 'quarentine' in action:
        varq=action[1]
    elif 'quarentine' in action[0]:
        varq=action[0][1]
    else:
        varq=[]
    if 'vaccinate' in action:
        varv=action[1]
    elif 'vaccinate' in action[1]:
        varv=action[1][1]
    else:
        varv=[]
    for var in varq:
        i = var[0]
        j = var[1]
        # remove S from seakness_index_map


        for v in seakness_index_map:
            if (v[1] == i) and (v[2] == j):
                seakness_index_map.pop(seakness_index_map.index(v))
        state_out[0] = state_changement(state_out[0], i, j, 'Q')
        add_to_index_map(state_out, i, j, 'Q')
    for var in varv:
        i = var[0]
        j = var[1]
        state_out[0] = state_changement(state_out[0], i, j, 'I')
        # update the number of turns for S N Q
    for v in seakness_index_map:
        if v[0] == 0:
            seakness_index_map2.append((v[0] + 1, v[1], v[2]))

    # reassemble the state
    state_out = tuple([tuple(state_out[0]), tuple(seakness_index_map2), tuple(q_index_map)])
    return state_out


def state_changement(state, i, j, Letter):
    # this function change the element in state i,j index to Letter
    state = list(state)
    state_out = list(state[i])

    state_out[j] = Letter
    state[i] = tuple(state_out)
    return state

def add_to_index_map(state, i, j, Letter):
    if Letter == 'S':
        seakness_tuple = list(state[1])
        seakness_tuple.append((0, i, j))
        return [state[0], tuple(seakness_tuple), state[2]]
    else:
        seakness_tuple = list(state[2])
        seakness_tuple.append((0, i, j))
        return [state[0], state[1], tuple(seakness_tuple)]

def spreading(self, state_a):
    # this function do the spreading of the deasese
    # iterate tru S's and find all next doors
    S_index = []
    state_out = list(state_a)
    S_indexs = find_all_map(self, 'S', state_a[0])
    for var in S_indexs:
        i = var[0]
        j = var[1]
        if (len(state_out[0]) > i + 1):
            if state_out[0][i + 1][j] == 'H':
                state_out[0] = state_changement(state_out[0], i + 1, j, 'S')
                add_to_index_map(state_out, i + 1, j, 'S')
        if (len(state_out[0:]) > j + 1):
            if state_out[0][i][j + 1] == 'H':
                state_out[0] = state_changement(state_out[0], i, j + 1, 'S')
                add_to_index_map(state_out, i, j + 1, 'S')
        if (i - 1 >= 0):
            if state_out[0][i - 1][j] == 'H':
                state_out[0] = state_changement(state_out[0], i - 1, j, 'S')
                state_out = add_to_index_map(state_out, i - 1, j, 'S')
        if (j - 1 >= 0):
            if state_out[0][i][j - 1] == 'H':
                state_out[0] = state_changement(state_out[0], i, j - 1, 'S')
                state_out = add_to_index_map(state_out, i, j - 1, 'S')
    return tuple(tuple([tuple(state_out[0]), state_out[1], state_out[2]]))

def illness_expired(self, state):
    # this function turn expired S to H
    state_out = list([list(state[0]), state[1], state[2]])
    # find index with 4
    state_illness_list = list(state[1])
    for v in state_illness_list:
        if v[0] > 2:
            state_out[0] = state_changement(state[0], v[1], v[2], 'H')
            state_illness_list.pop(state_illness_list.index(v))
            state_out = tuple([state_out[0], tuple(state_illness_list), state[2]])
    state_q_list = list(state[2])
    for v in state_q_list:
        if v[0] > 1:
            state_out[0] = state_changement(state, v[1], v[2], 'H')
            state_q_list.pop(state_q_list.index(v))
            state_out = tuple([state_out[0], state[1], tuple(state_q_list)])

    return tuple([tuple(state_out[0]), state_out[1], state_out[2]])
        # iterete

def find_all_healthy_neighbors(state, index):
    counter = 0
    neighbors = []
    index_x = index[0]
    index_y = index[1]
    if index_x + 1 < len(state):
        neighbors.append((index_x+1, index_y))
    if index_y + 1 < len(state[0]):
        neighbors.append((index_x, index_y+1))
    if index_x - 1 >= 0:
        neighbors.append((index_x-1, index_y))
    if index_y - 1 >= 0:
        neighbors.append((index_x, index_y-1))
    for neighbor in neighbors:
        list_ = list(neighbor)
        if state[list_[0]][list_[1]] == 'H':
            counter += 1
    return counter


def find_all_sick_neighbors(state, index):
    counter = 0
    neighbors = []
    index_x = index[0]
    index_y = index[1]
    if index_x + 1 < len(state):
        neighbors.append((index_x+1, index_y))
    if index_y + 1 < len(state[0]):
        neighbors.append((index_x, index_y+1))
    if index_x - 1 >= 0:
        neighbors.append((index_x-1, index_y))
    if index_y - 1 >= 0:
        neighbors.append((index_x, index_y-1))
    for neighbor in neighbors:
        list_ = list(neighbor)
        if state[list_[0]][list_[1]] == 'S':
            counter += 1

    return counter


def find_all_neighbors(state, index):
    neighbors = []
    index_x = index[0]
    index_y = index[1]
    if index_x + 1 < len(state):
        neighbors.append((index_x+1,index_y))
    if index_y + 1 < len(state[0]):
        neighbors.append((index_x,index_y+1))
    if index_x - 1 >= 0:
        neighbors.append((index_x-1,index_y))
    if index_y - 1 >= 0:
        neighbors.append((index_x, index_y-1))
    return len(neighbors)




def alphabeta_search(game, state):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = 'me'

    def max_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta)
            # if v2 == None:
            #     return None, None
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta)
            # if v2 == None:
            #     return None, None
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity)

def minimax_search(game, state):
    """Search game tree to determine best move; return (value, move) pair."""

    player = 'me'

    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move

    return max_value(state)

def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d

def h_alphabeta_search(game, state, cutoff=cutoff_depth(1), h=lambda s, p: 0):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = 'me'

    # @cache1
    def max_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    # @cache1
    def min_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)

def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        y=(tuple(x[0]),tuple(x[1]),tuple(x[2]),tuple(x[3]),tuple(x[4]),tuple(x[5]),tuple(x[6]),tuple(x[7]),tuple(x[8]),tuple(x[9]))

        if y not in cache:
            cache[y] = function(y, *args)
        return cache[y]
    return wrapped

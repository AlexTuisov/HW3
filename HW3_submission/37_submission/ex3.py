import random
import itertools as it
from collections import defaultdict
from copy import deepcopy


ids = ['211821111', '312441157']


# returns a dictionary representation of the initial stata
def turn_to_dict(initial_state):

    state = defaultdict(lambda: 'U')
    for i in range(len(initial_state)):
        for j in range(len(initial_state[0])):
            state[(i, j)] = initial_state[i][j]
            if initial_state[i][j] in ['Q', 'S']:
                state[(i, j)] += str(1)
    return state


# returns a simple heuristic score for the given state for one of the agents
def get_score(zoc, state):
    score = 0
    for place in zoc:
        if state[place][0] == 'S':
            score -= 1 * (3 - int(state[place][1]))
        elif state[place][0] in ['H', 'I']:
            score += 1
        elif state[place][0] == 'Q':
            score -= 5 * (2 - int(state[place][1]))
    return score


# returns the state after the given action was implemented on it
def get_next_state(state, action):

    new_state = get_state_after_first_action(state, action)
    old_state = deepcopy(state)

    # calculate new state after actions
    for place in old_state.keys():
        val = new_state[place]
        i = place[0]
        j = place[1]
        if val[0] == 'H' and ('S' in state[(i - 1, j)] or 'S' in state[(i + 1, j)] or
                                                          'S' in state[(i, j - 1)] or
                                                          'S' in state[(i, j + 1)]):
            new_state[place] = 'S1'

        if val[0] == 'Q':
            turn = int(val[1])
            if turn < 2:
                new_state[place] = 'Q' + str(turn + 1)
            else:
                new_state[place] = 'H'
        if val[0] == 'S':
            turn = int(val[1])
            if turn < 3:
                new_state[place] = 'S' + str(turn + 1)
            else:
                new_state[place] = 'H'
    return new_state


# returns state after implementing given action but before infecting and increasing Q and S counters
def get_state_after_first_action(state, action):
    new_state = state
    for act in action:
        effect, location = act[0], (act[1][0], act[1][1])
        if 'v' in effect:
            new_state[location] = 'I'
        else:
            new_state[location] = 'Q0'

    return new_state


# returns all possible non-empty actions
def get_all_actions(state, zoc):

    actions = []
    healthy = set()
    sick = set()
    for (i, j) in zoc:
        if 'H' == state[(i, j)][0]:
            healthy.add((i, j))
        if 'S' == state[(i, j)][0]:
            sick.add((i, j))

    double_qua = []
    try:
        double_qua = it.combinations(sick, 2)
    except ValueError:
        double_qua = []

    for h in healthy:
        action = [('vaccinate', h)]
        actions.append([('vaccinate', h)])
        for pair in double_qua:
            action.append(('quarantine', pair[0]))
            action.append(('quarantine', pair[1]))
            actions.append(action)
            action = [('vaccinate', h)]
        for q in sick:
            action.append(('quarantine', q))
            actions.append(action)
            action = [('vaccinate', h)]

    return actions


# returns the action with the largest score difference
def get_max_act(state, zoc, rival_zoc):
    actions = get_all_actions(state, zoc)
    if ('S1' in state.values() or 'S2' in state.values() or 'S3' in state.values()) and len(actions) != 0:
        act = ()
        max_val = get_score(zoc, get_next_state(state, act))
        max_val = max_val - get_score(rival_zoc, get_next_state(state, act))
        for action in actions:
            val = get_score(zoc, get_next_state(state, action))
            val = val - get_score(rival_zoc, get_next_state(state, action))
            if val > max_val:
                max_val = val
                act = action
        return act
    else:
        return []


# gets the best action with min-max of depth of the current round for the first player and our heuristic
def get_max_min_act(state, actions, zoc, rival_zoc):

    max_action = ()
    next_state = get_state_after_first_action(state, max_action)
    next_state = get_next_state(next_state, get_max_act(next_state, rival_zoc, zoc))
    max_val = val = get_score(zoc, next_state) - get_score(rival_zoc, next_state)

    for action in actions[1:]:
        next_state = get_state_after_first_action(state, action)
        next_state = get_next_state(next_state, get_max_act(next_state, rival_zoc, zoc))
        val = get_score(zoc, next_state) - get_score(rival_zoc, next_state)
        if val > max_val:
            max_val = val
            max_action = action

    return max_action


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.rival_zoc = []
        self.initial = turn_to_dict(initial_state)
        for place in self.initial.keys():
            if place not in zone_of_control:
                self.rival_zoc.append(place)
        self.my_turn = order

    def act(self, state):
        state = turn_to_dict(state)
        my_actions = get_all_actions(state, self.zoc)
        if self.my_turn == 'first':
            return get_max_min_act(state, my_actions, self.zoc, self.rival_zoc)
        else:
            return get_max_act(state, self.zoc, self.rival_zoc)


# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         print(initial_state)
#
#     def act(self, state):
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action

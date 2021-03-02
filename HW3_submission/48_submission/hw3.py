import random
from copy import deepcopy
from itertools import combinations
from itertools import product

ids = ['207530551', '322401100']


# check if there is sick nearby me
def sick_nearby(state, grid_size, row_num, col_num):
    return (col_num > 0 and state[row_num][col_num - 1][0] == 'S') \
           or (col_num < grid_size[1] and state[row_num][col_num + 1][0] == 'S') \
           or (row_num > 0 and state[row_num - 1][col_num][0] == 'S') \
           or (row_num < grid_size[0] and state[row_num + 1][col_num][0] == 'S')


def health_nearby_check(state, grid_size, row_num, col_num, zoc):
    count = 0
    if col_num > 0 and state[row_num][col_num - 1][0] == 'H':
        if (row_num, col_num - 1) in zoc:
            count += 1
        else:
            count -= 1
    if col_num < grid_size[1] and state[row_num][col_num + 1][0] == 'H':
        if (row_num, col_num + 1) in zoc:
            count += 1
        else:
            count -= 1
    if row_num > 0 and state[row_num - 1][col_num][0] == 'H':
        if (row_num - 1, col_num) in zoc:
            count += 1
        else:
            count -= 1
    if row_num < grid_size[0] and state[row_num + 1][col_num][0] == 'H':
        if (row_num + 1, col_num) in zoc:
            count += 1
        else:
            count -= 1
    return count >= 3

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = initial_state
        self.zoc = zone_of_control
        self.order = order
        self.num_police = 2
        self.num_medics = 1
        self.rival_zoc = [(i, j) for i, j in product(range(len(initial_state)),
                                                     range(len(initial_state[0])))
                          if 'U' not in initial_state[i][j] and (i, j) not in zone_of_control]
        self.update__initial_state()
        self.prev_state = self.initial_state

    # This is for updating initial 'S' tiles in the map to be 'S1', we start counting the turns
    def update__initial_state(self):
        updated_state = []
        for row in self.initial_state:
            curr_row = []
            for pop in row:
                if pop == 'S':
                    if self.order == 'first':
                        curr_row.append('S0')
                    else:
                        curr_row.append('S1')
                else:
                    curr_row.append(pop)
            updated_state.append(curr_row)
        self.initial_state = updated_state
        return

    # returns all of the rival's possible actions, and all my wanted actions (always vaccinate if possible)
    def get_possible_actions(self, state, zoc, agent):
        healthy = []
        sick = []

        grid_size = (len(state) - 1, len(state[0]) - 1)  # dimensions = (num rows, num cols)

        for (i, j) in zoc:
            if state[i][j] == 'H':
                if sick_nearby(state, grid_size, i, j):
                    healthy.append(('vaccinate', (i, j)))
            # elif 'S' in state[i][j]:  # TODO check if this is okay
            #     if health_nearby_check(state, grid_size, i, j, zoc):
            #         sick.append(('quarantine', (i, j)))
        # if healthy:
        #    return list(combinations(healthy, min(self.num_medics, len(healthy))))
        return list(combinations(healthy, min(self.num_medics, len(healthy))))

        vaccs = list(combinations(healthy, min(self.num_medics, len(healthy))))  # added
        #if not healthy and not sick:
        #    for (i, j) in zoc:
        #        if state[i][j] == 'H':
        #            healthy.append(('vaccinate', (i, j)))
        #            break

        # if not healthy:
        #     for (i, j) in zoc:
        #         if 'S' in state[i][j]:
        #             sick.append(('quarantine', (i, j)))

        # vaccs = list(combinations(healthy, min(self.num_medics, len(healthy))))
        # if agent == 'rival':
        #    vaccs += [tuple()]
        quars = list(combinations(sick, min(1, len(sick)))) # + list(combinations(sick, min(self.num_police, len(sick)))) + [tuple()]

        actions = [healthy_comb + sick_comb for healthy_comb in vaccs for sick_comb in quars]
        # if actions[-1] == tuple():
        #     actions = actions[:-1]

        # if quars:
        #     print(quars)
        # else:
        #     print('#################################################################################################')
        return actions

    # This is for updating sick and quarantined times according to previous state and actions applied between rounds
    def update_prev_state(self, state):  # TODO implement this
        # TODO change this
        new_state = deepcopy(state)
        for i, row in enumerate(state):
            for j, pop in enumerate(row):
                if pop == 'S':
                    if 'S' in self.prev_state[i][j]:
                        new_state[i][j] += str(int(self.prev_state[i][j][1]) + 1)
                    elif 'H' in self.prev_state[i][j]:
                        new_state[i][j] += '1'
                if pop == 'Q':
                    if 'Q' in self.prev_state[i][j]:
                        new_state[i][j] += str(int(self.prev_state[i][j][1]) + 1)
                    elif 'S' in self.prev_state[i][j]:
                        new_state[i][j] += '0'

        self.prev_state = new_state

    # add times to sick and quarantined after rival's action (where he is first)
    def update_state_if_second(self, state):  # TODO check if this is okay
        new_state = deepcopy(state)
        for i, row in enumerate(state):
            for j, pop in enumerate(row):
                if (pop == 'S' and 'S' in self.prev_state[i][j]) or (pop == 'Q' and 'Q' in self.prev_state[i][j]):
                    new_state[i][j] = self.prev_state[i][j]
                if pop == 'Q' and 'Q' not in self.prev_state[i][j]:
                    new_state[i][j] = 'Q0'
        return new_state

    # select action to return to game
    def act(self, state):
        # TODO update self.prev_state
        # this depends on whether I'm first or second:
        #   if I'm first then I update at the start of this function
        #   if I'm second then I update at the end of this function
        # TODO check if this is okay
        if self.order == 'first':
            self.update_prev_state(state)
            new_state = self.prev_state
        else:  # order == 'second'
            new_state = self.update_state_if_second(state)

        # my_actions = self.get_possible_actions(new_state, self.zoc, agent='me')
        # rival_actions = self.get_possible_actions(new_state, self.rival_zoc, agent='rival')
        # if self.order == 'first':
        #     return random.sample(my_actions, 1)[0]  # TODO change this into getting optimal action

        # choose best move:
        actions = self.get_possible_actions(new_state, zoc=self.zoc, agent='me')
        if self.order == 'first':
            depth = 2
        else:
            depth = 3
            if len(actions) >= 10:
                depth -= 1
        # depth = 2
        value = float('-inf')
        chosen_action = None
        # i = 0
        for action in actions:
            # i += 1
            # if self.order == 'first':
            #     print(i, value, chosen_action)
            current_state = self.apply_action(new_state, action)
            new_value = self.min_value(current_state, alpha=float('-inf'), beta=float('inf'), depth=depth)
            if new_value > value:
                value = new_value
                chosen_action = action

        if self.order == 'second':
            new_state = self.apply_action(new_state, chosen_action)
            new_state = self.change_map(new_state)
            self.prev_state = new_state

        # for line in new_state:
        #     print(line)

        return chosen_action

    # apply action on state to simulate the game
    @staticmethod
    def apply_action(state, actions):
        if not actions:
            return state
        new_state = deepcopy(state)
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
            if 'v' in effect:
                new_state[location[0]][location[1]] = 'I'
            else:
                new_state[location[0]][location[1]] = 'Q0'
        return new_state

    # change map like they did to simulate game
    @staticmethod
    def change_map(state):  # TODO check if this is okay
        new_state = deepcopy(state)

        grid_size = (len(state) - 1, len(state[0]) - 1)
        for i in range(len(state)):
            for j in range(len(state[0])):
                # virus spread
                if state[i][j] == 'H' and sick_nearby(state, grid_size, i, j):
                    new_state[i][j] = 'S1'
                # advancing sick counters
                elif 'S' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 3:
                        new_state[i][j] = 'S' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'
                # advancing quarantine counters
                elif 'Q' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 2:
                        new_state[i][j] = 'Q' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'

        return new_state

    # max value from alpha-beta pruning algorithm
    def max_value(self, state, alpha, beta, depth):
        if self.order == 'first':
            depth = depth - 1
            if depth <= 0:
                return self.utility_diff(state)

        value = float('-inf')
        for action in self.get_possible_actions(state, self.zoc, agent='me'):
            new_state = self.apply_action(state, action)  # TODO check if this is okay
            if self.order == 'second':  # if I'm second, then after my action, dynamics are applied
                new_state = self.change_map(new_state)
            value = max(value, self.min_value(new_state, alpha, beta, depth))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    # min value from alpha-beta pruning algorithm
    def min_value(self, state, alpha, beta,  depth):
        if self.order == 'second':
            depth = depth - 1
            if depth <= 0:
                return self.utility_diff(state)

        value = float('inf')
        actions = self.get_possible_actions(state, self.rival_zoc, agent='rival')
        for action in actions:
            new_state = self.apply_action(state, action)  # TODO check if this is okay
            if self.order == 'first':  # if I'm first, then rival is second, then after his action, dynamics are applied
                new_state = self.change_map(new_state)
            value = min(value, self.max_value(new_state, alpha, beta, depth))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    # calculate the utility difference between me and rival:
    def utility_diff(self, state):
        my_score = 0
        rival_score = 0

        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                my_score += 1
            if 'I' in state[i][j]:
                my_score += 1
            if 'S' in state[i][j]:
                my_score -= 1
            if 'Q' in state[i][j]:
                my_score -= 5

        for (i, j) in self.rival_zoc:
            if 'H' in state[i][j]:
                rival_score += 1
            if 'I' in state[i][j]:
                rival_score += 1
            if 'S' in state[i][j]:
                rival_score -= 1
            if 'Q' in state[i][j]:
                rival_score -= 5

        return my_score - rival_score

    
# # implementation of a random agent
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

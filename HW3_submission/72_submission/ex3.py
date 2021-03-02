import copy
from itertools import combinations, product
from copy import deepcopy

ids = ["328711569", "312581655"]
cache = dict()


def aux_evaluation_function(current_map, zoc):
    eval_value = 0
    for (i, j) in zoc:
        if 'H' in current_map[i][j] or 'I' in current_map[i][j]:
            eval_value += 1
        if 'S' in current_map[i][j]:
            eval_value -= 1
        if 'Q' in current_map[i][j]:
            eval_value -= 5
    return eval_value


def result_function(state, action, turn):
    if len(action) == 0:
        return state
    current_map = list(list(sub) for sub in state[0])
    areas_to_be_vaccinated = list(action[0])
    areas_to_be_quarantined = list(action[1])
    quarantined_areas_map = change_area_status(current_map, areas_to_be_quarantined, "Q")
    quarantined_and_vaccinated_map = change_area_status(quarantined_areas_map, areas_to_be_vaccinated, "I")
    map_after_action = tuple(tuple(sub) for sub in quarantined_and_vaccinated_map)
    if turn == 'first':
        return map_after_action, state[1]

    sick_areas = find_areas_in_state((map_after_action, state[1]), 'S')
    state_after_infection_spread = update_H_areas_acc_to_neighbors((map_after_action, state[1]), sick_areas)
    state_after_sickness_expires = update_state(state, state_after_infection_spread)
    return state_after_sickness_expires


def find_areas_in_state(state, code):
    current_map = state[0]
    q_status_areas = ()
    for i in range(len(current_map)):
        for j in range(len(current_map[0])):
            if current_map[i][j] == code:
                q_status_areas = q_status_areas + ((i, j),)
    return q_status_areas


def update_H_areas_acc_to_neighbors(state, sick_areas):
    current_map = list(list(sub) for sub in state[0])
    for area in sick_areas:
        neighbors_list = []
        i = area[0]
        j = area[1]
        if i > 0:
            neighbors_list.append([i - 1, j])
        if i < len(current_map) - 1:
            neighbors_list.append([i + 1, j])

        if j > 0:
            neighbors_list.append([i, j - 1])
        if j < len(current_map[0]) - 1:
            neighbors_list.append([i, j + 1])

        for neighbor in neighbors_list:
            if current_map[neighbor[0]][neighbor[1]] == 'H':
                current_map[neighbor[0]][neighbor[1]] = 'S'
    return current_map, state[1]


def update_state(state, state_after_infection_spread):
    current_map = state[0]
    status_map = list(list(sub) for sub in state[1])
    map_after_infection_spread = state_after_infection_spread[0]
    for i in range(len(map_after_infection_spread)):
        for j in range(len(map_after_infection_spread[0])):
            if map_after_infection_spread[i][j] == current_map[i][j]:
                if map_after_infection_spread[i][j] == 'U' or map_after_infection_spread[i][j] == 'I' \
                        or map_after_infection_spread[i][j] == 'H':
                    continue
                if map_after_infection_spread[i][j] == 'Q' and status_map[i][j] < 2:
                    status_map[i][j] += 1
                elif map_after_infection_spread[i][j] == 'S' and status_map[i][j] < 3:
                    status_map[i][j] += 1
                else:
                    status_map[i][j] = -1
                    map_after_infection_spread[i][j] = "H"
                continue
            if (current_map[i][j] == "H" and map_after_infection_spread[i][j] == "S") or (
                    current_map[i][j] == "S" and map_after_infection_spread[i][j] == "Q"):
                status_map[i][j] = 1

    updated_status_map = tuple(tuple(sub) for sub in status_map)
    updated_map = tuple(tuple(sub) for sub in map_after_infection_spread)
    return updated_map, updated_status_map


def change_area_status(current_map, areas, code):
    aux_map = copy.deepcopy(current_map)
    for i in range(len(areas)):
        index = areas[i][1]
        if code == 'I':
            assert aux_map[index[0]][index[1]] == 'H'
        elif code == 'Q':
            assert aux_map[index[0]][index[1]] == 'S'
        else:
            raise NotImplementedError
        aux_map[index[0]][index[1]] = code
    return aux_map


def get_possible_actions(state, zoc):
    current_map = state[0]
    h_areas = set()
    s_areas = set()
    for (i, j) in zoc:
        if 'H' in current_map[i][j]:
            h_areas.add(('vaccinate', (i, j)))
        if 'S' in current_map[i][j]:
            s_areas.add(('quarantine', (i, j)))
    medics = 1
    s_combinations = list(combinations(s_areas, 1)) + list(combinations(s_areas, 0))
    h_combinations = list(combinations(h_areas, min(medics, len(h_areas))))
    all_actions = list(product(h_combinations, s_combinations))
    return all_actions


def sort_actions_list(actions):
    possible_actions = list(
        sorted(filter(lambda x: x != ((), ()), actions), key=lambda x: len(x[1])))
    n = (len(actions) // 2) + 1
    if len(actions) >= 10:
        n = 10
    return possible_actions[:n]


# class Agent:

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_map =tuple(tuple(sub) for sub in deepcopy(initial_state))
        self.status_map = self.init_state_status()
        self.initial_state = (deepcopy(self.initial_map), deepcopy(self.status_map))
        self.is_first_run = True
        self.zoc = zone_of_control
        self.max_depth = 2
        self.player_turn = order
        if order == 'first':
            self.max_depth_constructor = 6
            self.rival_order = 'second'
        else:
            self.max_depth_constructor = 5
            self.rival_order = 'first'
        self.rival_zoc = self.get_rival_zoc(initial_state)
        self.act(initial_state)
        self.is_first_run = False

    def update_status_map(self, state):
        status_map = deepcopy(self.status_map)
        status_map = list(list(sub) for sub in status_map)
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'U' or state[i][j] == 'I' or state[i][j] == 'H':
                    status_map[i][j] = -1
                elif state[i][j] == 'Q' and status_map[i][j] <2:
                    status_map[i][j] += 1
                elif state[i][j] == 'S' and status_map[i][j] < 3:
                    status_map[i][j] += 1
        self.status_map = tuple(tuple(sub) for sub in status_map)

    def act(self, new_map):
        new_map = tuple(tuple(sub) for sub in new_map)
        max_depth = self.max_depth
        if self.is_first_run:
            max_depth=self.max_depth_constructor
            state = self.initial_state
        # update status map acc to map and prev status map
        else:
            self.update_status_map(new_map)
            state = (new_map, self.status_map)
        eval_score, selected_action = self._minimax(0, max_depth, state, True, float('-inf'), float('inf'))
        flat_list = [item for sublist in selected_action for item in sublist]
        assert len(flat_list)>0
        return flat_list

    def _minimax(self, current_depth, max_depth, state, is_max_turn, alpha, beta):
        tup = (state, current_depth, is_max_turn)
        if cache.get(tup) is not None:
            element = cache[tup]
            action_target, best_value, a, b = element
            if a <= alpha and beta <= b:
                return best_value, action_target
        possible_actions = sort_actions_list(get_possible_actions(state, self.zoc))
        rival_possible_actions = sort_actions_list(get_possible_actions(state, self.rival_zoc))
        is_loc_free, final_action = self.is_loc_free_of_S(state, is_max_turn)
        if is_loc_free:
            return self.evaluation_function(state, is_max_turn), final_action
        if current_depth == max_depth:
            if is_max_turn:
                return self.evaluation_function(state, is_max_turn), possible_actions[0]
            return self.evaluation_function(state, is_max_turn), rival_possible_actions[0]
        best_value = float('-inf') if is_max_turn else float('inf')
        if is_max_turn:
            action_target = possible_actions[0]
        else:
            action_target = rival_possible_actions[0]

        if is_max_turn:
            for action in possible_actions:
                new_state = result_function(state, action, self.player_turn)
                eval_child, action_child = self._minimax(current_depth + 1, max_depth, new_state, not is_max_turn,
                                                         alpha, beta)
                if best_value < eval_child:
                    best_value = eval_child
                    action_target = action
                    alpha = max(alpha, best_value)
                    cache[(state, current_depth, is_max_turn)] = (
                        action, best_value, alpha, beta)
                if beta <= alpha:
                    break

        elif not is_max_turn:
            for action in rival_possible_actions:
                new_state = result_function(state, action, self.rival_order)
                eval_child, action_child = self._minimax(current_depth + 1, max_depth, new_state, not is_max_turn,
                                                         alpha, beta)
                if best_value > eval_child:
                    best_value = eval_child
                    action_target = action
                    beta = min(beta, best_value)
                    cache[(state, current_depth, is_max_turn)] = (
                        action, best_value, alpha, beta)
                if beta <= alpha:
                    break

        return best_value, action_target

    def evaluation_function(self, state, is_max_turn):
        current_map = state[0]
        agent1_val = aux_evaluation_function(current_map, self.zoc)
        agent2_val = aux_evaluation_function(current_map, self.rival_zoc)
        difference = agent1_val - agent2_val
        if is_max_turn:
            return difference
        return -difference

    def get_rival_zoc(self, state):
        rival_zoc = []
        for i in range(len(state)):
            for j in range(len(state[0])):
                if (i, j) not in self.zoc and state[i][j] != 'U':
                    rival_zoc.append((i, j))
        return rival_zoc

    def is_loc_free_of_S(self, state, is_max_turn):
        current_map = state[0]
        H_area = None
        if is_max_turn:
            zoc = self.zoc
        else:
            zoc = self.rival_zoc
        for index in zoc:
            i = index[0]
            j = index[1]
            if current_map[i][j] == "S":
                return False, None
            if H_area is None and current_map[i][j] == 'H':
                H_area = tuple((i, j))
        if H_area is not None:
            return True, [{('vaccinate', H_area)}]
        return True, []

    def init_state_status(self):
        status_map = [[0 for i in range(len(self.initial_map[0]))] for i in range(len(self.initial_map))]
        for i in range(len(self.initial_map)):
            for j in range(len(self.initial_map[0])):
                if self.initial_map[i][j] == "S" or self.initial_map[i][j] == "Q":
                    status_map[i][j] = 1
                else:
                    status_map[i][j] = -1
        return tuple(tuple(sub) for sub in status_map)

import random
import copy
import itertools
import numpy as np

ids = ['201209020', '308869700']


def find_healthy_sick_and_quarantine_locations(state_map):
    sick = []
    healthy = []
    quarantine = []
    for i in range(len(state_map)):
        for j in range(len(state_map[i])):
            if state_map[i][j] == 'S':
                sick.append((i, j))
            elif state_map[i][j] == 'H':
                healthy.append((i, j))
            elif state_map[i][j] == 'Q':
                quarantine.append((i, j))
    return healthy, sick, quarantine


def find_healthy_with_sick_neighbors(healthy, sick):
    temp = []
    for healthy_spot in healthy:
        for sick_spot in sick:
            if (abs(healthy_spot[0]-sick_spot[0]) == 1 and abs(healthy_spot[1]-sick_spot[1]) == 0) \
                    or (abs(healthy_spot[0]-sick_spot[0]) == 0 and abs(healthy_spot[1]-sick_spot[1]) == 1):
                temp.append(healthy_spot)
    return list(set(temp))


def update_dynamic_dict(dynamic_dict, current_state):
    current_healthy, current_sick, current_quarantine = find_healthy_sick_and_quarantine_locations(current_state)

    # step 1 - find new q and make them q0
    new_q0_loc = []
    for q_loc in current_quarantine:
        if q_loc not in dynamic_dict['q0']:
            new_q0_loc.append(q_loc)

    # step 2 - q0 goes to q1
    new_q1_loc = dynamic_dict['q0'].copy()

    # step 3 - remove new_q0_loc from s and update new_s1 and new_s2 (implement dynamics)
    new_s1_loc = dynamic_dict['s0'].copy()
    new_s2_loc = dynamic_dict['s1'].copy()
    for q0_loc in new_q0_loc:
        if q0_loc in dynamic_dict['s0']:
            new_s1_loc.remove(q0_loc)
        elif q0_loc in dynamic_dict['s1']:
            new_s2_loc.remove(q0_loc)

    # step 4 - find new s0
    new_s0_loc = []
    for s_loc in current_sick:
        if s_loc not in dynamic_dict['s0'] and s_loc not in dynamic_dict['s1']:
            new_s0_loc.append(s_loc)

    dynamic_dict_updated = {'s0': new_s0_loc, 's1': new_s1_loc, 's2': new_s2_loc, 'q0': new_q0_loc, 'q1': new_q1_loc}

    return dynamic_dict_updated


def actions(state, zoc, police, medics):
    """Returns all the actions that can be executed in the given
    state. The result should be a tuple (or other iterable) of actions
    as defined in the problem description file"""

    healthy, sick, quarantine = find_healthy_sick_and_quarantine_locations(state)
    healthy_in_zoc = [loc for loc in healthy if loc in zoc]
    sick_in_zoc = [loc for loc in sick if loc in zoc]
    final_list = []  # final list of possible actions
    temp = []
    for rs in (range(police + 1)):
        # combination of valid police locations when police number is rs
        police_comb = list(itertools.combinations(sick_in_zoc, rs))
        for rh in (range(medics + 1)):
            # combination of valid medic locations when medic number is rh
            medics_comb = list(itertools.combinations(healthy_in_zoc, rh))
            for p_comb1 in police_comb:
                for m_comb1 in medics_comb:
                    for location in p_comb1:
                        temp.append(("quarantine", location))
                    for location in m_comb1:
                        temp.append(("vaccinate", location))

                    final_list.append(temp)
                    temp = []
    return final_list


def result(state, action, dynamic_dict, new_q, order):
    """Return the state that results from executing the given
    action in the given state. The action must be one of
    self.actions(state).
    if order = 1 , it means we are looking for the action of player 1, and if 2 so player 2 action + dynamics
    """
    # new_state = copy.deepcopy(state)
    new_state = copy.deepcopy(state)
    new_q0_player_1 = new_q.copy()

    for act in action:
        if act[0] == "quarantine":
            new_state[act[1][0]][act[1][1]] = "Q"  # change S to Q
            new_q0_player_1.append((act[1][0], act[1][1]))
        elif act[0] == "vaccinate":
            new_state[act[1][0]][act[1][1]] = "I"  # change H to I

    if order == 2:  # dynamic implementation
        healthy, sick, quarantine = find_healthy_sick_and_quarantine_locations(new_state)
        h2s = find_healthy_with_sick_neighbors(healthy, sick)
        for loc in h2s:  # change H to S
            new_state[loc[0]][loc[1]] = "S"

        for q_loc in dynamic_dict['q1']:  # change Q to H
            new_state[q_loc[0]][q_loc[1]] = "H"

        for s_loc in dynamic_dict['s2']:  # change S to H
            if s_loc not in new_q0_player_1:
                new_state[s_loc[0]][s_loc[1]] = "H"

    return new_state, new_q0_player_1


def calculate_score(state, zoc, penalty_flag):
    score = 0
    for loc in zoc:
        if state[loc[0]][loc[1]] == 'H' or state[loc[0]][loc[1]] == 'I':
            score += 1
        elif state[loc[0]][loc[1]] == 'S':
            score -= 1
        elif state[loc[0]][loc[1]] == 'Q':
            score -= 5
    # if penalty_flag:
    #     score -= 1000

    return score


def calculate_delta_score(state, zoc_1, penalty_1, zoc_2, penalty_2):
    return calculate_score(state, zoc_1, penalty_1) - calculate_score(state, zoc_2, penalty_2)


def one_step_decision(state, dynamic_dict, zoc_1, zoc_2, police, medic, order):
    possible_actions_1 = actions(state, zoc_1, police, medic)
    min_list = []  # the best score for player 2
    max_list = []  # the best score for player 1 due to player 2 decision
    if order == 1:
        for action_1 in possible_actions_1:
            mid_state, new_q_1 = result(state, action_1, dynamic_dict, [], 1)
            penalty_1 = False
            # if not action_1:
            #     penalty_1 = True
            possible_actions_2 = actions(mid_state, zoc_2, police, medic)
            for action_2 in possible_actions_2:
                new_state, new_q_2 = result(mid_state, action_2, dynamic_dict, new_q_1, 2)
                penalty_2 = False
                # if not action_2:
                #     penalty_2 = True
                min_list.append(calculate_delta_score(new_state, zoc_1, penalty_1, zoc_2, penalty_2))
            max_list.append(min(min_list))
            min_list = []
        return possible_actions_1[np.argmax(max_list)]

    else:
        penalty_1 = False
        possible_actions_2 = actions(state, zoc_2, police, medic)
        for action_2 in possible_actions_2:
            new_state, new_q_2 = result(state, action_2, dynamic_dict, [], 2)
            penalty_2 = False
            # if not action_2:
            #     penalty_2 = True
            min_list.append(calculate_delta_score(new_state, zoc_1, penalty_1, zoc_2, penalty_2))

        return possible_actions_2[np.argmin(min_list)]


def is_goal(state):
    for row in state:
        for col in row:
            if col == 'S':
                return False
    return True


def min_value(counter, state, alpha, beta, zoc_1, penalty_1, zoc_2, dynamic_dict, police, medics, order, new_q):
    counter += 1
    max_width = 3
    new_score = np.inf
    possible_actions = actions(state, zoc_2, police, medics)
    if len(possible_actions) >= 10:
        possible_actions = possible_actions[:: max_width]
    else:
        possible_actions = possible_actions[:: 1]

    if is_goal(state):
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score

    for action in possible_actions:
        new_state, new_q0_player = result(state, action, dynamic_dict, new_q, 2)  # because min is the 2nd player.
        penalty_2 = False

        dynamic_dict_updated = update_dynamic_dict(dynamic_dict, new_state)
        max_value_score = max_value(counter, new_state, alpha, beta, zoc_1, zoc_2, penalty_2,
                                                               dynamic_dict_updated, police, medics, order)
        new_score = min(new_score, max_value_score)
        if new_score < alpha:
            return new_score
        beta = min(beta, new_score)
    return new_score


def max_value(counter, state, alpha, beta, zoc_1, zoc_2, penalty_2, dynamic_dict, police, medics, order):
    max_width = 3
    new_score = -np.inf
    possible_actions = actions(state, zoc_1, police, medics)
    if len(possible_actions) >= 10:
        possible_actions = possible_actions[:: max_width]
    else:
        possible_actions = possible_actions[:: 1]

    if is_goal(state):
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score
    if counter > 1:
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score

    for action in possible_actions:
        new_state, new_q0_player = result(state, action, dynamic_dict, [], 1)  # 1 is for the order (player number)
        penalty_1 = False

        min_value_score = min_value(counter, new_state, alpha, beta, zoc_1, penalty_1, zoc_2,
                                                               dynamic_dict, police, medics, order, new_q0_player)
        new_score = max(new_score, min_value_score)

        if new_score > beta:
            return new_score
        alpha = max(alpha, new_score)
    return new_score


def min_value_60_sec(counter, state, alpha, beta, zoc_1, penalty_1, zoc_2, dynamic_dict, police, medics, order, new_q):
    counter += 1
    max_width = 2
    new_score = np.inf
    possible_actions = actions(state, zoc_2, police, medics)
    if len(possible_actions) >= 20:
        possible_actions = possible_actions[:: max_width]
    else:
        possible_actions = possible_actions[:: 1]

    if is_goal(state):
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score

    for action in possible_actions:
        new_state, new_q0_player = result(state, action, dynamic_dict, new_q, 2)  # because min is the 2nd player.
        penalty_2 = False

        dynamic_dict_updated = update_dynamic_dict(dynamic_dict, new_state)
        max_value_score = max_value_60_sec(counter, new_state, alpha, beta, zoc_1, zoc_2, penalty_2,
                                                               dynamic_dict_updated, police, medics, order)
        new_score = min(new_score, max_value_score)
        if new_score < alpha:
            return new_score
        beta = min(beta, new_score)
    return new_score


def max_value_60_sec(counter, state, alpha, beta, zoc_1, zoc_2, penalty_2, dynamic_dict, police, medics, order):
    max_width = 2
    new_score = -np.inf
    possible_actions = actions(state, zoc_1, police, medics)
    if len(possible_actions) >= 20:
        possible_actions = possible_actions[:: max_width]
    else:
        possible_actions = possible_actions[:: 1]

    if is_goal(state):
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score
    if counter > 1:
        new_score = calculate_score(state, zoc_1, False) - calculate_score(state, zoc_2, False)
        return new_score

    for action in possible_actions:
        new_state, new_q0_player = result(state, action, dynamic_dict, [], 1)  # 1 is for the order (player number)
        penalty_1 = False

        min_value_score = min_value_60_sec(counter, new_state, alpha, beta, zoc_1, penalty_1, zoc_2,
                                                               dynamic_dict, police, medics, order, new_q0_player)
        new_score = max(new_score, min_value_score)

        if new_score > beta:
            return new_score
        alpha = max(alpha, new_score)
    return new_score


def alpha_beta_search(state, order, zoc_1, zoc_2, police, medics, dynamic_dict, new_q, game_counter):

    if game_counter == 0 and order == 1:
        max_width = 1
    else:
        max_width = 3

    if order == 1:
        possible_actions = actions(state, zoc_1, police, medics)
        max_from_min = -np.inf
        optimal_action = possible_actions[-1]
        if len(possible_actions) >= 10:
            possible_actions = possible_actions[:: max_width]
        else:
            possible_actions = possible_actions[:: 1]

        for action in possible_actions:
            new_state, new_q0_player = result(state, action, dynamic_dict, new_q, 1)
            if game_counter > 0:
                temp = min_value(0, new_state, -np.inf, np.inf, zoc_1, False, zoc_2, dynamic_dict, police, medics,
                                        order, new_q0_player)
            else:
                temp = min_value_60_sec(0, new_state, -np.inf, np.inf, zoc_1, False, zoc_2, dynamic_dict, police,
                                        medics, order, new_q0_player)

            if temp >= max_from_min:
                max_from_min = temp
                optimal_action = action

    else:  # order == 2
        possible_actions = actions(state, zoc_2, police, medics)
        min_from_max = np.inf
        optimal_action = possible_actions[-1]
        if len(possible_actions) >= 10:
            possible_actions = possible_actions[:: max_width]
        else:
            possible_actions = possible_actions[:: 1]

        for action in possible_actions:
            new_state, new_q0_player = result(state, action, dynamic_dict, new_q, 2)
            temp = max_value(1, new_state, -np.inf, np.inf, zoc_1, zoc_2, False, dynamic_dict, police, medics, order)

            if temp <= min_from_max:
                min_from_max = temp
                optimal_action = action

    return optimal_action


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = initial_state
        self.zoc = zone_of_control  # list of tuples
        self.rival_zoc = [(i, j) for i in range(len(initial_state)) for j in range(len(initial_state[0]))
                          if (i, j) not in zone_of_control]
        print(zone_of_control)
        if order == 'first':
            self.order = 1
        else:
            self.order = 2
        self.medics = 1
        self.police = 2
        healthy, sick, quarantine = find_healthy_sick_and_quarantine_locations(initial_state)
        print(len([loc for loc in healthy if loc in self.zoc]))
        self.dynamic_dict = {'s0': sick, 's1': [], 's2': [], 'q0': quarantine, 'q1': []}
        self.counter = 0
        self.search_depth = 2
        self.alpha = -np.inf
        self.beta = np.inf

        if self.order == 1:  # OUR Heuristic - use only one agent - the medic - do vaccine

            self.action_order_1 = alpha_beta_search(self.initial_state, self.order, self.zoc, self.rival_zoc, 0, 1,
                                                    self.dynamic_dict, [], self.counter)
            # if not self.action_order_1:
            #     self.action_order_1 = alpha_beta_search(self.initial_state, self.order, self.zoc, self.rival_zoc, 1, 0,
            #                                             self.dynamic_dict, [], self.counter)

    def act(self, state):

        if self.order == 1:
            if self.counter > 0:  # means we are not in the initial state, we ar already in the middle of the game
                self.dynamic_dict = update_dynamic_dict(self.dynamic_dict, state)

            if self.counter == 0:
                action = self.action_order_1
            else:
                # ### in this case we are taking one step forward:
                # action = one_step_decision(state, self.dynamic_dict, self.zoc, self.rival_zoc, 0, 1, self.order)
                # if not action:
                #     action = one_step_decision(state, self.dynamic_dict, self.zoc, self.rival_zoc, 1, 0, self.order)

                action = alpha_beta_search(state, self.order, self.zoc, self.rival_zoc, 0, 1,
                                                        self.dynamic_dict, [], 1)
                # if not action:
                #     action = alpha_beta_search(state, self.order, self.zoc, self.rival_zoc, 1, 0,
                #                                             self.dynamic_dict, [], self.counter)

        else:  # order = 2

            # ## we have to decide if we want to use the first 60 seconds
            # ## or just looking two steps forward in 5 seconds
            # if self.counter == 0:
            #     # dict with X options due to player 1 staring move. compare the real move he made to the dict you
            #     # previously calculated (in the 60 seconds you had during the init func. (constructor)
            #     action = self.action_order_2

            # ## in this case we are taking one step forward:
            # our heuristic - one step decision - use only one medic
            # action = one_step_decision(state, self.dynamic_dict, self.rival_zoc, self.zoc, 0, 1, self.order)
            # if not action:
            #     # our heuristic - one step decision - use only one police
            #     action = one_step_decision(state, self.dynamic_dict, self.rival_zoc, self.zoc, 1, 0, self.order)

            # ### we are taking 2 steps forward:
            # ## Attention - rival ZOC and Self ZOC are given in a reverse order!!!
            # create mid dict: (in this case the state is the state after player 1 made his plays)
            mid_dynamic_dict = update_dynamic_dict(self.dynamic_dict, state)

            action = alpha_beta_search(state, self.order, self.rival_zoc, self.zoc, 0, 1,
                                       self.dynamic_dict, mid_dynamic_dict['q0'], 1)
            # if not action:
            #     action = alpha_beta_search(state, self.order, self.rival_zoc, self.zoc, 1, 0,
            #                                self.dynamic_dict, mid_dynamic_dict['q0'], 1)

            # update the the new state after player 2 and player 1 made the plays.
            new_state, new_q0_player = result(state, action, self.dynamic_dict, mid_dynamic_dict['q0'], 2)
            self.dynamic_dict = update_dynamic_dict(self.dynamic_dict, new_state)

        self.counter += 1

        return action

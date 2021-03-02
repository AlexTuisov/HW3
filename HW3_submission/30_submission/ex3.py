from itertools import chain, combinations
from copy import deepcopy
from math import inf
from time import time

ids = ['314653270']

NO_MEDICS = 1
NO_POLICE = 2
ME = 1
OTHER_AGENT = 0
DEPTH = 2
ACT_EXIT_TIME = 4.9
INIT_EXIT_TIME = 59.9


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self._t1 = time()
        self._no_row = len(initial_state)
        self._no_col = len(initial_state[0])
        self._state = [["" for j in range(self._no_col)] for i in range(self._no_row)]
        self._my_zoc = zone_of_control
        self._other_agent_zoc = [(i, j) for i in range(self._no_row) for j in range(self._no_col)
                                 if (i, j) not in self._my_zoc]
        self._order = order
        self._depth_counter = 0
        self._in_init = True
        self.update_state(initial_state)
        self._is_first_action = True
        if self._order == "first":
            _, vac_action, qua_action = self.max_value(self._state, 0, -inf, inf)
            self._first_action = self.get_action(vac_action, qua_action)
        self._in_init = False

    def act(self, state):
        self._t1 = time()
        if self._order == "first" and self._is_first_action:
            self._is_first_action = False
            return self._first_action
        self.update_state(state)
        _, vac_action, qua_action = self.max_value(self._state, 0, -inf, inf)
        return self.get_action(vac_action, qua_action)

    def update_state(self, state):
        for i in range(self._no_row):
            for j in range(self._no_col):
                if state[i][j] == "H" or state[i][j] == "I" or state[i][j] == "U":
                    self._state[i][j] = state[i][j]
                elif state[i][j] == "Q" or state[i][j] == "S":
                    if state[i][j] not in self._state[i][j]:
                        self._state[i][j] = state[i][j] + "1"
                    else:
                        self.advance_state_code_by_one(self._state, i, j)

    def get_action(self, vac_action, qua_action):
        action = []
        for loc in vac_action:
            action.append(('vaccinate', loc))
        for loc in qua_action:
            action.append(('quarantine', loc))
        return action

    def max_value(self, state, my_utility, alpha, beta):
        self._depth_counter += 1
        is_game_over = self.game_over(state)
        if not self._in_init:
            if is_game_over or self._depth_counter == 2 * DEPTH + 1:
                healthy_list = self.get_player_state_code_list(state, "H", ME)
                if is_game_over and len(healthy_list) > 0:
                    vac_action = tuple([healthy_list[0]])
                else:
                    vac_action = tuple()
                self._depth_counter -= 1
                return my_utility, vac_action, tuple()
        else:
            if self.game_over(state) or self._depth_counter == 2 * (DEPTH + 1) + 1:
                healthy_list = self.get_player_state_code_list(state, "H", ME)
                if is_game_over and len(healthy_list) > 0:
                    vac_action = tuple([healthy_list[0]])
                else:
                    vac_action = tuple()
                self._depth_counter -= 1
                return my_utility, vac_action, tuple()

        max_dict = {"v": -inf, "vac_action": tuple(), "qua_action": tuple()}
        vaccinate_actions, quarantine_actions = self.get_player_actions(state, ME)
        for qua_action in quarantine_actions:
            for vac_action in vaccinate_actions:
                if (time() - self._t1 >= ACT_EXIT_TIME and not self._in_init) or \
                        (time() - self._t1 >= INIT_EXIT_TIME and self._in_init):
                    self._depth_counter -= 1
                    return max_dict["v"], max_dict["vac_action"], max_dict["qua_action"]

                # if len(vac_action) == 0 and len(qua_action) == 0:
                #     continue

                new_state = deepcopy(state)
                self.activate_action(new_state, vac_action, qua_action)
                if self._order == "second":
                    self.contagion_heal_free(new_state)
                    state_utility = self.get_my_utility(new_state)
                else:
                    state_utility = 0

                tmp_v, _, _ = self.min_value(new_state, my_utility + state_utility, alpha, beta)
                if tmp_v > max_dict["v"]:
                    max_dict["v"] = tmp_v
                    max_dict["vac_action"] = vac_action
                    max_dict["qua_action"] = qua_action

                if max_dict["v"] >= beta:
                    self._depth_counter -= 1
                    return max_dict["v"], max_dict["vac_action"], max_dict["qua_action"]

                alpha = max(alpha, max_dict["v"])

        self._depth_counter -= 1
        return max_dict["v"], max_dict["vac_action"], max_dict["qua_action"]

    def min_value(self, state, my_utility, alpha, beta):
        self._depth_counter += 1
        # print("min value " + str(self._depth_counter))
        if not self._in_init:
            if self.game_over(state) or self._depth_counter == 2 * DEPTH + 1:
                self._depth_counter -= 1
                return my_utility, tuple(), tuple()
        else:
            if self.game_over(state) or self._depth_counter == 2 * (DEPTH + 1) + 1:
                self._depth_counter -= 1
                return my_utility, tuple(), tuple()

        min_dict = {"v": inf, "vac_action": tuple(), "qua_action": tuple()}
        vaccinate_actions, quarantine_actions = self.get_player_actions(state, OTHER_AGENT)

        for qua_action in quarantine_actions:
            for vac_action in vaccinate_actions:
                if (time() - self._t1 >= ACT_EXIT_TIME and not self._in_init) or\
                        (time() - self._t1 >= INIT_EXIT_TIME and self._in_init):
                    self._depth_counter -= 1
                    return min_dict["v"], min_dict["vac_action"], min_dict["qua_action"]

                # if len(vac_action) == 0 and len(qua_action) == 0:
                #     continue

                new_state = deepcopy(state)
                self.activate_action(new_state, vac_action, qua_action)
                if self._order == "first":
                    self.contagion_heal_free(new_state)
                    state_utility = self.get_my_utility(new_state)
                else:
                    state_utility = 0

                tmp_v, _, _ = self.max_value(new_state, my_utility + state_utility, alpha, beta)
                if tmp_v < min_dict["v"]:
                    min_dict["v"] = tmp_v
                    min_dict["vac_action"] = vac_action
                    min_dict["qua_action"] = qua_action

                if min_dict["v"] <= alpha:
                    self._depth_counter -= 1
                    return min_dict["v"], min_dict["vac_action"], min_dict["qua_action"]

                beta = min(beta, min_dict["v"])

        self._depth_counter -= 1
        return min_dict["v"], min_dict["vac_action"], min_dict["qua_action"]

    def contagion_heal_free(self, state):
        sick_list = self.get_state_code_list(state, "S")
        quarantined_list = self.get_state_code_list(state, "Q")
        self.contagion(state, sick_list)
        self.heal(state, sick_list)
        self.free(state, quarantined_list)

    def free(self, state, quarantined_list):
        for i, j in quarantined_list:
            if "2" in state[i][j]:
                state[i][j] = "H"
            else:
                self.advance_state_code_by_one(state, i, j)

    def heal(self, state, sick_list):
        for i, j in sick_list:
            if "3" in state[i][j][1]:
                state[i][j] = "H"
            else:
                self.advance_state_code_by_one(state, i, j)

    def contagion(self, state, sick_list):
        for i, j in sick_list:
            if i > 0 and state[i-1][j] == "H":
                state[i-1][j] = "S1"
            elif i < self._no_row-1 and state[i+1][j] == "H":
                state[i+1][j] = "S1"
            elif j > 0 and state[i][j-1] == "H":
                state[i][j-1] = "S1"
            elif j < self._no_col-1 and state[i][j+1] == "H":
                state[i][j+1] = "S1"

    def activate_action(self, state, vac_action, qua_action):
        if len(vac_action) > 0:
            for i, j in vac_action:
                state[i][j] = "I"

        if len(qua_action) > 0:
            for i, j in qua_action:
                state[i][j] = "Q1"

    def get_player_actions(self, state, player):
        healthy_list = self.get_player_state_code_list(state, "H", player)
        # sick_list = self.get_player_state_code_list(state, "S", player)

        if len(healthy_list) == 0:
            vaccinate_actions = [tuple()]
        else:
            vaccinate_actions = list(chain.from_iterable(combinations(healthy_list, r) for r in range(NO_MEDICS + 1)))[1:]

        # if len(sick_list) == 0:
        quarantine_actions = [tuple()]
        # else:
        #     quarantine_actions = list(chain.from_iterable(combinations(sick_list, r) for r in range(NO_POLICE)))

        return vaccinate_actions, quarantine_actions

    def game_over(self, state):
        if self.get_no_state_code(state, "S") == 0:
            return True
        return False

    def get_my_utility(self, state):
        my_score = self.calc_player_score(state, ME)
        other_agent_score = self.calc_player_score(state, OTHER_AGENT)
        for i in range(3):
            calc_state = deepcopy(state)
            if self.get_no_state_code(calc_state, "S") == 0:
                break
            self.contagion_heal_free(calc_state)
            my_score += self.calc_player_score(calc_state, ME)
            other_agent_score += self.calc_player_score(calc_state, OTHER_AGENT)
        return my_score - other_agent_score

    def calc_player_score(self, state, player):
        score = 0
        zoc = self.get_player_zoc(player)
        for i,j in zoc:
            if state[i][j] == "H" or state[i][j] == "I":
                score += 1
            elif "S" in state[i][j]:
                score -= 1
            elif "Q" in state[i][j]:
                score -= 5
        return score

    def advance_state_code_by_one(self, state, i, j):
        sc = state[i][j]
        state[i][j] = sc[0] + str(int(sc[1]) + 1)

    def get_no_state_code(self, state, state_code):
        return self.get_player_no_state_code(state, state_code, ME) +\
               self.get_player_no_state_code(state, state_code, OTHER_AGENT)

    def get_state_code_list(self, state, state_code):
        return self.get_player_state_code_list(state, state_code, ME) +\
               self.get_player_state_code_list(state, state_code, OTHER_AGENT)

    def get_player_no_state_code(self, state, state_code, player):
        return len(self.get_player_state_code_list(state, state_code, player))

    def get_player_state_code_list(self, state, state_code, player):
        zoc = self.get_player_zoc(player)
        state_code_list = []
        for i,j in zoc:
            if state_code in state[i][j]:
                state_code_list.append((i,j))
        return state_code_list

    def get_player_zoc(self, player):
        if player == ME:
            return self._my_zoc
        return self._other_agent_zoc

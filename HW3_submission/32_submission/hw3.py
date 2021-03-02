

ids = ['322758483', '318724218']

LOW_BOUND = float("-inf")
UP_BOUND = float("inf")


def argmax(dct):
    max_key, max_val = -1, LOW_BOUND
    for key, val in dct.items():
        if val[-1] > max_val:
            max_key, max_val = key, val[-1]
    return max_key


def cross_prod(iterable1, iterable2, iterable3_ind, same_flag):
    crossprodlist = []

    if not iterable3_ind and same_flag:
        for i in range(len(iterable1)):
            for j in range(i + 1, len(iterable2)):
                crossprodlist.append((iterable1[i], iterable2[j]))

    elif not iterable3_ind and not same_flag:
        for i in range(len(iterable1)):
            for j in range(len(iterable2)):
                crossprodlist.append((iterable1[i], iterable2[j]))
    else:
        for i in range(len(iterable1)):
            for j in range(len(iterable2)):
                it21, it22 = iterable2[j]
                crossprodlist.append((iterable1[i],it21,it22))
    return crossprodlist


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.i_state = initial_state
        self.len_rows = len(initial_state)
        self.len_cols = len(initial_state[0])
        self.zoc = zone_of_control
        self.opp_zoc = []
        if order == 'first':
            self.turn = 1
        else:
            self.turn = 2
        for i in range(self.len_rows):
            for j in range(self.len_cols):
                if (i, j) not in self.zoc and self.i_state[i][j] != 'U':
                    self.opp_zoc.append((i, j))
        self.score = 0
        self.grades = {'H': 1, 'I': 1, 'S': -1, 'Q': -5}
        self.oper_dict = {'vaccinate': 'I', 'quarantine': 'Q'}

    def get_neighs(self, i, j, state):
        neighs = []
        if i == 0:
            neighs.append(((i + 1, j), state[i + 1][j]))
        elif i == self.len_rows - 1:
            neighs.append(((i - 1, j), state[i - 1][j]))
        else:
            neighs.append(((i - 1, j), state[i - 1][j]))
            neighs.append(((i + 1, j), state[i + 1][j]))
        if j == 0:
            neighs.append(((i, j + 1), state[i][j + 1]))
        elif j == self.len_cols - 1:
            neighs.append(((i, j - 1), state[i][j - 1]))
        else:
            neighs.append(((i, j + 1), state[i][j + 1]))
            neighs.append(((i, j - 1), state[i][j - 1]))
        return neighs

    def act(self, state):
        act = self.minmax(state, 0)
        try:
            return list(act[:-1][0])
        except:
            return list(())
            #Used to handle edge cases where my zoc has no healthy/sick tiles and my opp does

    def value(self, suc_state, action, aleph, bet, depth, maxi):
        curr_rel_score = self.score_heuristic(suc_state, action)
        if self.goal_test(suc_state) or depth == 0:
            return curr_rel_score

        depth -= 1
        if maxi:
            val = LOW_BOUND
            success = self.up_next(suc_state, False)
            for _, n_state in success:
                val = max(val, self.value(n_state, aleph, bet, depth, False))
                aleph = max(aleph, val)
                if aleph >= bet:
                    return val + curr_rel_score
            return val + curr_rel_score

        else:
            val = UP_BOUND
            success = self.up_next(suc_state, True)
            for _, suc in success:
                val = min(val, self.value(suc, aleph, bet, depth, True))
                bet = min(bet, val)
                if bet <= aleph:
                    return val + curr_rel_score
            return val + curr_rel_score

    def minmax(self, state, depth):
        vals = {}
        successor = self.up_next(state, False)
        for i, (act, suc) in enumerate(successor):
            vals[i] = (act, self.value(suc, act, LOW_BOUND, UP_BOUND, depth, False))
        try:
            return vals[argmax(vals)]
        except:
            return ()

    def zoc_check(self, opp):
        if opp:
            zoc = self.opp_zoc
        else:
            zoc = self.zoc
        return zoc

    def scorer_func(self, state, opp):
        scorer = 0
        zoc = self.zoc_check(opp)
        for i, j in zoc:
            for let, grade in self.grades.items():
                if let in state[i][j]:
                    scorer += grade
        return scorer

    def score_heuristic(self, state, action):
        h_val = self.scorer_func(state, False) - self.scorer_func(state, True)

        try:
            subnautica = action[0]
        except:
            return h_val

        for subact in action:
            zoc_count = 0
            opp_count = 0
            sick_ind = False

            cond = subact[0]
            index1 = subact[1][0]
            index2 = subact[1][1]

            neighs = self.get_neighs(index1, index2, state)  # ---- ((ind1,ind2),let)
            for neigh in neighs:
                if neigh[1] == 'S':
                    sick_ind = True
                elif neigh[1] == 'H':
                    if neigh[0] in self.zoc:
                        zoc_count += 1
                    else:
                        opp_count += 1
            if cond == 'vaccinate':
                if not sick_ind:
                    continue
                h_val += (zoc_count - opp_count+1) ** 3
            elif cond == 'quarantine':
                if zoc_count == len(neighs):
                    h_val += zoc_count ** 2
                else:
                    h_val += -5 * ((zoc_count+1)**2)

        return h_val

    def create_acts_list(self, state, opp):
        zoc = self.zoc_check(opp)
        healthy_cells = []
        sick_cells = []
        for cell in zoc:
            if state[cell[0]][cell[1]] == 'H':
                healthy_cells.append(('vaccinate', cell))
            if state[cell[0]][cell[1]] == 'S':
                sick_cells.append(('quarantine', cell))

        vacc_acts = [(healthy_cells[i],) for i in range(len(healthy_cells))]
        one_quar_acts = [(sick_cells[i],) for i in range(len(sick_cells))]
        two_quar_acts = cross_prod(sick_cells, sick_cells, False, True)
        vacc_x_quar_acts = cross_prod(healthy_cells, sick_cells, False, False)
        vacc_x_duoquar_acts = cross_prod(healthy_cells, two_quar_acts, True, False)
        vacc_x_quar_acts.extend(vacc_x_duoquar_acts)
        vacc_x_quar_acts.extend(vacc_acts)
        vacc_x_quar_acts.extend(one_quar_acts)
        vacc_x_quar_acts.extend(())

        return vacc_x_quar_acts

    def res_state(self, state, actions):
        nu_state = [row.copy() for row in state]
        for oper, let in self.oper_dict.items():
            for act in actions:
                if act[0][0] == oper:
                    nu_state[act[0][1][0]][act[0][1][1]] = let
        return nu_state

    # Returns an action,nu_state tuple where nu_state = result state after action is applied
    def up_next(self, state, opp):
        next_states = []
        act_list = self.create_acts_list(state, opp)
        for act in act_list:
            next_states.append((act, self.res_state(state, act)))
        return next_states

    def goal_test(self, state):
        for i in range(self.len_rows):
            for j in range(self.len_cols):
                if state[i][j] == 'S':
                    return False
        return True

import random
from operator import itemgetter

ids = ["311395834", "314981259"]
LOW_PRIORITY = -5
MID1_PRIORITY = 0
MID2_PRIORITY = 5
HIGH_PRIORITY = 10


class Agent:
    def __init__(self, initial_state, zoc, order):
        self.initial_state = initial_state
        self.state = None
        self.zoc = zoc
        self.h, self.s = [], []

    """ UTILS """

    def parse_state(self, status, my_zoc=True):
        x = []
        for i, j in self.zoc:
            if my_zoc and (i, j) in self.zoc and self.state[i][j] == status:
                x.append((i, j))
            elif not my_zoc and (i, j) not in self.zoc and self.state[i][j] == status:
                x.append((i, j))
        return x

    def S_neighbors(self):
        s_neighbors = {}
        for i, j in self.h:
            if i - 1 >= 0 and (i - 1, j) in self.s:
                if (i, j) in s_neighbors:
                    s_neighbors[(i, j)] += 1
                else:
                    s_neighbors[(i, j)] = 1
            if j - 1 >= 0 and (i, j - 1) in self.s:
                if (i, j) in s_neighbors:
                    s_neighbors[(i, j)] += 1
                else:
                    s_neighbors[(i, j)] = 1
            if i + 1 < len(self.state) and (i + 1, j) in self.s:
                if (i, j) in s_neighbors:
                    s_neighbors[(i, j)] += 1
                else:
                    s_neighbors[(i, j)] = 1
            if j + 1 < len(self.state[0]) and (i, j + 1) in self.s:
                if (i, j) in s_neighbors:
                    s_neighbors[(i, j)] += 1
                else:
                    s_neighbors[(i, j)] = 1
        return max(s_neighbors, key=s_neighbors.get) if len(s_neighbors) > 0 else None

    def H_neighbors(self):
        for i, j in self.h:
            if i - 1 >= 0 and (i - 1, j) in self.h:
                return i, j
            if j - 1 >= 0 and (i, j - 1) in self.h:
                return i, j
            if i + 1 < len(self.state) and (i + 1, j) in self.h:
                return i, j
            if j + 1 < len(self.state[0]) and (i, j + 1) in self.h:
                return i, j

    def spread_potential(self, H):
        spread_count = 0
        for i, j in self.h:
            if i - 1 >= 0 and (i - 1, j) == H:
                spread_count += 1
            if j - 1 >= 0 and (i, j - 1) == H:
                spread_count += 1
            if i + 1 < len(self.state) and (i + 1, j) == H:
                spread_count += 1
            if j + 1 < len(self.state[0]) and (i, j + 1) == H:
                spread_count += 1
        return spread_count

    def infection_potential(self):
        S_pref = []
        for i, j in self.s:
            if i - 1 >= 0 and (i - 1, j) in self.h:
                S_pref.append((i, j))
            if j - 1 >= 0 and (i, j - 1) in self.h:
                S_pref.append((i, j))
            if i + 1 < len(self.state) and (i + 1, j) in self.h:
                S_pref.append((i, j))
            if j + 1 < len(self.state[0]) and (i, j + 1) in self.h:
                S_pref.append((i, j))

        return S_pref if len(S_pref) > 0 else False

    def m(self):
        first_H = self.S_neighbors()
        if first_H:
            if self.spread_potential(first_H) > 0:
                return [MID2_PRIORITY, [('vaccinate', first_H)]]
            else:
                return [MID2_PRIORITY, [('vaccinate', first_H)]]
        second_H = self.H_neighbors()
        if second_H:
            return [MID1_PRIORITY, [('vaccinate', second_H)]]
        if len(self.h) > 0:
            return [MID1_PRIORITY, [('vaccinate', random.sample(self.h, 1)[0])]]
        return [LOW_PRIORITY, ()]

    def p(self, used=None):
        if used is None:
            used = []
        s_infection_potential = self.infection_potential()
        if s_infection_potential:
            for i in range(4, 0, -1):
                for s in self.s:
                    risk = sum([1 if t == s else 0 for t in s_infection_potential])
                    if risk == i and s not in used:
                        return [i * 2, [('quarantine', s)]]
        return [LOW_PRIORITY, ()]

    def mp(self):
        valid_actions = []
        m_value, m_action = self.m()
        if m_action != ():
            valid_actions.append(m_action[0])
        p_value, p_action = self.p()
        if p_action != ():
            valid_actions.append(p_action[0])
        return [(m_value + p_value) / 2, valid_actions]

    def mpp(self):
        valid_actions = []
        value, div = 0, 0
        m_value, m_action = self.m()
        if m_action != ():
            valid_actions.append(m_action[0])
            value += m_value
            div += 1
        p_value, p_action = self.p()
        if p_action != ():
            valid_actions.append(p_action[0])
            value += p_value
            div += 1
            p2_value, p2_action = self.p([p_action[0][1]])
            if p2_action != ():
                valid_actions.append(p2_action[0])
                value += p2_value
                div += 1
        return [(value / div) if div != 0 else LOW_PRIORITY, valid_actions]

    def _max(self):
        resource_options = [self.mpp(), self.mp(), self.p(), self.m()]
        return max(resource_options, key=itemgetter(0))[1]

    def act(self, state):
        self.state = state
        self.h, self.s = self.parse_state('H', my_zoc=True), self.parse_state('S', my_zoc=True)
        return self._max()

from operator import itemgetter

ids = ['322277179', '207829581']

directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def get_directions(i, j):
    ret = []
    for direction in directions:
        x = i + direction[0]
        y = j + direction[1]
        ret.append((x, y))
    return ret


def tuplify(listovlistov):
    return tuple([tuple(x) for x in listovlistov])


class Agent:
    def __init__(self, initial_state, zone_of_control, order):

        self.first = True if order == 'first' else False
        self.zoc = zone_of_control
        self.advers_zoc = []


        self.rows = len(initial_state)
        self.cols = len(initial_state[0])
        self.init_state = initial_state

        self.player_util = 0

        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in self.zoc and initial_state[i][j] != 'U':
                    self.advers_zoc.append((i, j))

    def act(self, state):

        vac_act = self.heuristic_med_act(state)
        quara = self.quarantine_if_you_have_to(self.result(state, vac_act, False))

        return list(vac_act) + list(quara)

    def heuristic_med_act(self, state):
        values = [(a, self.state_utility(s)) for (a, s) in self.med_sucs(state, 'ani')]
        return max(values, key=itemgetter(1))[0]

    def neighbors(self, state, i, j, char, zoc):
        neighbors_with_char = []
        for direction in directions:
            x = i + direction[0]
            y = j + direction[1]
            if self.in_board(x, y) and state[x][y] == char and (x, y) in zoc:
                neighbors_with_char.append((x, y))
        return neighbors_with_char

    def quarantine_if_you_have_to(self, state):
        bidud = []
        second_neigh = []
        for (i, j) in self.zoc:
            if state[i][j] == 'S':
                helthim_near_sick = len(self.neighbors(state, i, j, 'H', self.zoc)) - \
                                    len((self.neighbors(state, i, j, 'H', self.advers_zoc)))
                for neigh in self.neighbors(state, i, j, 'H', self.zoc):
                    second_neigh.extend(self.neighbors(state, neigh[0], neigh[1], 'H', self.zoc))
                helthim_near_helthi = 0.5 * len(list(set(second_neigh)))
                score_quara = helthim_near_helthi + helthim_near_sick
                if score_quara >= 3:
                    bidud.append(('quarantine', (i, j), score_quara))
        # TODO if agent vaccinates one of the sick neighbors, dont qurai
        to_bidud = [(q, c) for (q, c, s) in bidud]
        return sorted(to_bidud, reverse=True)[:2]

    def state_utility(self, state):

        return self.current_score(state, self.zoc) - self.current_score(state, self.advers_zoc)

    def current_score(self, state, control_zone):
        score = 0
        for (i, j) in control_zone:
            if 'H' in state[i][j]:
                score += 1
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                score -= 1
            if 'Q' in state[i][j]:
                score -= 5
        return score

    def med_sucs(self, state, player):
        zoc = self.zoc if player == 'ani' else self.advers_zoc
        return [(act, self.result(state, act, True)) for act in self.med_actions(state, zoc)]

    def med_actions(self, state, zoc):
        healthy_tups = []
        for (i, j) in zoc:
            if 'H' in state[i][j]:
                healthy_tups.append((('vaccinate', (i, j)),))
        healthy_tups.append(tuple())
        return healthy_tups

    def in_board(self, i, j):
        return 0 < i < self.rows and 0 < j < self.cols

    def result(self, state, action, with_spread):
        new_state = [x[:] for x in state]

        def do_act(act):
            if act[0] == 'vaccinate':
                new_state[act[1][0]][act[1][1]] = 'I'
            else:
                new_state[act[1][0]][act[1][1]] = 'Q'

        if len(action) != 0:

            if isinstance(action[0][0], tuple):
                for act in action[0]:
                    do_act(act)
                do_act(action[1])
            elif isinstance(action[0], str):
                do_act(action)
            else:
                for act in action:
                    do_act(act)

        # Spread sickness
        if with_spread:
            for i in range(self.rows):
                for j in range(self.cols):
                    if new_state[i][j] == 'S':
                        for direction in directions:
                            x = i + direction[0]
                            y = j + direction[1]
                            if self.in_board(x, y) and new_state[x][y] == 'H':
                                new_state[x][y] = 'S'
        return new_state

    def terminal_test(self, state):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.init_state[i][j] == 'S':
                    return False
        return True


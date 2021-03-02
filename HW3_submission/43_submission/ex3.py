import random

ids = ['207541293', '205968043']


def zoc_states_setter(zone_of_control, initial_state):
    states_dict = {'S': [], 'H': [], 'I': [], 'Q': [], 'U': []}
    for tile in zone_of_control:
        states_dict[initial_state[tile[0]][tile[1]]].append(tile)

    return states_dict

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.n_rows = len(initial_state)
        self.n_columns = len(initial_state[0])
        self.order = order
        self.map = initial_state

    def has_neighbor(self, tile, neighbor, ours=True):
        i = tile[0]
        j = tile[1]
        counter = 0
        if not ours:
            if i + 1 < self.n_rows and self.map[i+1][j] == neighbor:
                counter += 1
            if i - 1 >= 0 and self.map[i-1][j] == neighbor:
                counter += 1
            if j + 1 < self.n_columns and self.map[i][j+1] == neighbor:
                counter += 1
            if j - 1 >= 0 and self.map[i][j-1] == neighbor:
                counter += 1
        else:
            if i + 1 < self.n_rows and self.map[i+1][j] == neighbor and (i+1, j) in self.zoc:
                counter += 1
            if i - 1 >= 0 and self.map[i-1][j] == neighbor and (i-1, j) in self.zoc:
                counter += 1
            if j + 1 < self.n_columns and self.map[i][j+1] == neighbor and (i, j+1) in self.zoc:
                counter += 1
            if j - 1 >= 0 and self.map[i][j-1] == neighbor and (i, j-1) in self.zoc:
                counter += 1
        return counter

    def healthy_neighbourhood(self, tile):
        i = tile[0]
        j = tile[1]
        neighbor = 'H'
        counter = 0
        if i + 1 < self.n_rows and self.map[i + 1][j] == neighbor and (i + 1, j) in self.zoc:
            counter += self.has_neighbor((i+1, j), neighbor) + 1
        if i - 1 >= 0 and self.map[i - 1][j] == neighbor and (i - 1, j) in self.zoc:
            counter += self.has_neighbor((i-1, j), neighbor) + 1
        if j + 1 < self.n_columns and self.map[i][j + 1] == neighbor and (i, j + 1) in self.zoc:
            counter += self.has_neighbor((i, j+1), neighbor) + 1
        if j - 1 >= 0 and self.map[i][j-1] == neighbor and (i, j - 1) in self.zoc:
            counter += self.has_neighbor((i, j-1), neighbor) + 1

        return counter

    def act(self, state):
        zoc_dict = zoc_states_setter(self.zoc, state)
        actions = []
        # setting the most contagious sick tiles
        quarantine_list = sorted([tile for tile in zoc_dict['S']], key=lambda x: self.healthy_neighbourhood(x), reverse=True)
        vaccinate_list = sorted([tile for tile in zoc_dict['H']], key=lambda x: (int(bool(self.has_neighbor(x, 'S', False))), self.healthy_neighbourhood(x)), reverse=True)
        try:
            to_quarantine = []
            if random.random() > 0.9:
                to_quarantine = quarantine_list[:2]
            else:
                to_quarantine = quarantine_list[:1]
        except ValueError:
            to_quarantine = []
        try:
            to_vaccinate = [vaccinate_list[0]]
        except ValueError:
            to_vaccinate = []
        for item in to_quarantine:
            actions.append(('quarantine', item))
        for item in to_vaccinate:
            actions.append(('vaccinate', item))

        return actions

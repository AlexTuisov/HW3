from copy import deepcopy

ids = ['308292051']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.unpopulated = []
        self.num_healthy_w_sick = 0
        self.state = deepcopy(initial_state)
        self.my_score = 0
        self.sick_h_counter = 0

        for i, row in enumerate(initial_state):
            for j, col in enumerate(row):
                if initial_state[i][j] == 'U':
                    self.unpopulated.append((i, j))
        a = 0

    def update_scores(self):
        def calc(state):
            if state == 'H':
                return 1
            if state == 'I':
                return 1
            if state == 'S':
                return -1
            if state == 'Q':
                return -5

        for i, row in enumerate(self.state):
            for j, col in enumerate(row):
                if (i, j) in self.zoc:
                    self.my_score += calc(self.state[i][j])
                elif (i, j) in self.unpopulated:
                    continue
                else:
                    self.opponent_score += calc(self.state[i][j])

    def process_state(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick

    def sick_heuristic(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        if h == 4:
            self.sick_h_counter += 1
            return h
        else:
            return 0

    def healthy_heuristic(self, sick, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = 0
        for neighbor in neighbors:
            if neighbor in sick:
                self.num_healthy_w_sick += 1
                h += 1
                if h > 1:
                    return 2
        return 1 if h == 1 else 0

    def act(self, state):
        sick_map = []
        for i, row in enumerate(self.state):
            for j, col in enumerate(row):
                if state[i][j] == 'S':
                    sick_map.append((i, j))

        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        healthy.sort(key=lambda x: self.healthy_heuristic(sick_map, x), reverse=True)

        try:
            if self.sick_h_counter == 1:
                to_quarantine = (sick[:1])
            elif self.sick_h_counter >= 2:
                to_quarantine = (sick[:2])
            else:
                to_quarantine = []
        except KeyError:
            to_quarantine = []
        try:
            to_vaccinate = [(healthy[0])]
        except:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        self.num_healthy_w_sick = 0
        return action
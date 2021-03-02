
ids = ['931177406', '342436953']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):

        self.zoc = zone_of_control
        self.shape = (len(initial_state), len(initial_state[0]))

    def act(self, state):
        healthy = self.get_healthy(state)
        max_score = -100

        if len(healthy) == 0:
            action = []
            sicks = self.get_sick(state)
            sicks.sort(key=lambda x: self.S_score(healthy, x), reverse=True)
            try:
                to_quarantine = (sicks[:1])
            except KeyError:
                to_quarantine = []
            for item in to_quarantine:
                action.append(('quarantine', item))
            return action

        heuristic_max = healthy[0]
        for i in healthy:
            actual_score = self.H_score(state, i[0], i[1])
            if actual_score > max_score:
                max_score = actual_score
                heuristic_max = i
        act = ("vaccinate", (heuristic_max[0], heuristic_max[1]))
        action = [act]
        return action

    def is_defined(self, i, j):
        if 0 <= i < self.shape[0] and 0 <= j < self.shape[1]:
            return True
        else:
            return False

    def get_healthy(self, state):
        healthy = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
        return healthy

    def get_sick(self, state):
        sicks = []
        for (i, j) in self.zoc:
            if 'S' in state[i][j]:
                sicks.append((i, j))
        return sicks

    def H_score(self, state, i, j):
        score = 0
        if self.is_defined(i + 1, j):
            if state[i + 1][j] == 'S':
                score += 10
        if self.is_defined(i - 1, j):
            if state[i - 1][j] == 'S':
                score += 10
        if self.is_defined(i, j + 1):
            if state[i][j + 1] == 'S':
                score += 10
        if self.is_defined(i, j - 1):
            if state[i][j - 1] == 'S':
                score += 10
        return score

    def S_score(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h


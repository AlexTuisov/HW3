
ids = ["205756117", "315691451"]


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control

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
        return h


    def health_heuristic(self, sick, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in sick and neighbor in self.zoc))
        return h

    def act(self, state):
        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        healthy.sort(key=lambda x: self.sick_heuristic(sick, x), reverse=True)
        try:
            to_quarantine = (sick[:2])
        except KeyError:
            to_quarantine = []
        try:
            to_vaccinate = (healthy[:1])
        except ValueError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

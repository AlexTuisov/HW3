ids = ['320867781', '307841189']

DIMENSIONS = (10, 10)


def sick_heuristic(healthy, coordinate, zoc):
    neighbors = ((coordinate[0] - 1, coordinate[1]),
                 (coordinate[0] + 1, coordinate[1]),
                 (coordinate[0], coordinate[1] - 1),
                 (coordinate[0], coordinate[1] + 1))
    h1 = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in zoc))
    neighborsOfNeighbors = []
    for neighbor in neighbors:
        neighborsOfNeighbors.append((neighbor[0] - 1, neighbor[1]))
        neighborsOfNeighbors.append((neighbor[0] + 1, neighbor[1]))
        neighborsOfNeighbors.append((neighbor[0], neighbor[1] - 1))
        neighborsOfNeighbors.append((neighbor[0], neighbor[1] + 1))
    neighborsOfNeighbors = tuple(neighborsOfNeighbors)
    h2 = sum(0.5 for neighborOfNeighbors in neighborsOfNeighbors if
             (neighborOfNeighbors in healthy and neighborOfNeighbors in zoc))
    return h1 + h2


def healthy_heuristic(state, coordinate):
    sick = list()
    healthy = list()
    for i in range(DIMENSIONS[0]):
        for j in range(DIMENSIONS[1]):
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
    neighbors = ((coordinate[0] - 1, coordinate[1]),
                 (coordinate[0] + 1, coordinate[1]),
                 (coordinate[0], coordinate[1] - 1),
                 (coordinate[0], coordinate[1] + 1))
    h1 = sum(1 for neighbor in neighbors if (neighbor in sick))
    neighborsOfNeighbors = []
    for neighbor in neighbors:
        if neighbor in healthy:
            neighborsOfNeighbors.append((neighbor[0] - 1, neighbor[1]))
            neighborsOfNeighbors.append((neighbor[0] + 1, neighbor[1]))
            neighborsOfNeighbors.append((neighbor[0], neighbor[1] - 1))
            neighborsOfNeighbors.append((neighbor[0], neighbor[1] + 1))
    neighborsOfNeighbors = tuple(neighborsOfNeighbors)
    h2 = sum(0.5 for neighborOfNeighbors in neighborsOfNeighbors if
             (neighborOfNeighbors in sick))
    return h1 + h2


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

    def act(self, state):
        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: sick_heuristic(healthy, x, self.zoc), reverse=True)
        healthy.sort(key=lambda x: healthy_heuristic(state, x), reverse=True)
        if healthy:
            to_vaccinate = [healthy[0]]
            for item in to_vaccinate:
                action.append(('vaccinate', item))
            return action
        else:
            return ()



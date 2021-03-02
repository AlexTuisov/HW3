import random

ids = ['204795090', '209063320']

ADJACENTS = {(0, 1), (-1, 0), (1, 0), (0, -1)}


def get_neigbours(coordinate, neighbours):
    for dx, dy in ADJACENTS:
        neighbours.append((coordinate[0] + dx, coordinate[1] + dy))
    return tuple(neighbours)


class Agent:

    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.lim_i = len(initial_state)
        self.lim_j = len(initial_state[0])

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
        neighbours = []
        neighboursOfNeighbours = []
        neighboursOfNeighboursOfNeighbours = []

        neighbours = get_neigbours(coordinate, neighbours)
        h1 = sum(1 for neighbour in neighbours if (neighbour in healthy and neighbour in self.zoc))

        for neighbour in neighbours:
            for dx, dy in ADJACENTS:
                neighboursOfNeighbours.append((neighbour[0] + dx, neighbour[1] + dy))
        neighboursOfNeighbours = tuple(neighboursOfNeighbours)
        h2 = sum(0.5 for neighbourOfNeighbours in neighboursOfNeighbours if
                 (neighbourOfNeighbours in healthy and neighbourOfNeighbours in self.zoc))

        for nn in neighboursOfNeighbours:
            for dx, dy in ADJACENTS:
                neighboursOfNeighboursOfNeighbours.append((nn[0] + dx, nn[1] + dy))
        neighboursOfNeighboursOfNeighbours = tuple(neighboursOfNeighboursOfNeighbours)
        h3 = sum(0.25 for n in neighboursOfNeighboursOfNeighbours if
                 (n in healthy and n in self.zoc))

        return h1 + h2 + h3

    def healthy_heuristic(self, sick, healthy, coordinate):
        neighbours = []
        neighboursOfNeighbours = []
        neighboursOfneighboursOfNeighbours = []

        neighbours = get_neigbours(coordinate, neighbours)
        h1 = sum(1 for neighbour in neighbours if (neighbour in sick))

        for neighbour in neighbours:
            if neighbour in healthy:
                for dx, dy in ADJACENTS:
                    neighboursOfNeighbours.append((neighbour[0] + dx, neighbour[1] + dy))
        neighboursOfNeighbours = tuple(neighboursOfNeighbours)
        h2 = sum(0.5 for neighbourOfNeighbours in neighboursOfNeighbours if
                 (neighbourOfNeighbours in sick))

        for n in neighboursOfNeighbours:
            if n in healthy:
                for dx, dy in ADJACENTS:
                    neighboursOfneighboursOfNeighbours.append((n[0] + dx, n[1] + dy))
        neighboursOfneighboursOfNeighbours = tuple(neighboursOfneighboursOfNeighbours)
        h3 = sum(0.5 for n in neighboursOfneighboursOfNeighbours if
                 (n in sick))

        return h1 + h2 + h3

    def act(self, state):
        action = []
        healthy, sick = self.process_state(state)
        unpopulated = []
        for i in range(self.lim_i):
            for j in range(self.lim_j):
                if state[i][j] == "U":
                    unpopulated.append((i, j))
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        healthy.sort(key=lambda x: self.healthy_heuristic(sick, healthy, x), reverse=True)

        if healthy:
            to_vaccinate = [healthy[0]]
            for item in to_vaccinate:
                action.append(('vaccinate', item))

        else:
            try:
                to_quarantine = (sick[:2])
            except KeyError:
                to_quarantine = []
            try:
                to_vaccinate = []
            except KeyError:
                to_vaccinate = []
            for item in to_quarantine:
                action.append(('quarantine', item))
            if to_vaccinate:
                for item in to_vaccinate:
                    action.append(('vaccinate', item))


        return action

import itertools
import random
from copy import deepcopy

ids = ["207630658", "312236219"]

DIMENSIONS = (10, 10)


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        # build zoc of opponent
        habitable_tiles = [(i, j) for i, j in itertools.product(range(0, DIMENSIONS[0]), range(0, DIMENSIONS[1]))
                           if 'U' not in initial_state[i][j]]
        self.opponent_zoc = list(set(habitable_tiles) - set(self.zoc))
        self.state = initial_state

    def process_state(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick

    @staticmethod
    def get_neighbours(index):
        neighbors = ((index[0] - 1, index[1]),
                     (index[0] + 1, index[1]),
                     (index[0], index[1] - 1),
                     (index[0], index[1] + 1))
        return neighbors

    def sick_heuristic(self, healthy, coordinate):
        """
        Heurstic to determine who to quarantine (max h):
            h = #num_our_h - #num_ai_h*hyper_param
            Quarantine only if h>0
        """

        our_h_real = 0
        ai_h_real = 0
        s3_neighbors = 0
        for neighbor in Agent.get_neighbours(coordinate):
            try:
                if self.state[neighbor[0]][neighbor[1]] == 'S' and self.old_state[neighbor[0]][neighbor[1]] != 'S':
                    s3_neighbors += 1
            except IndexError:
                pass
            if neighbor in healthy:
                h_neighbors = Agent.get_neighbours(neighbor)
                is_h_neighbor_going_to_stay_h = True
                for neighbor_neighbor in h_neighbors:
                    try:
                        if neighbor_neighbor != coordinate and self.state[neighbor_neighbor[0]][neighbor_neighbor[1]] == 'S':
                            is_h_neighbor_going_to_stay_h = False
                    except IndexError:
                        pass
                if is_h_neighbor_going_to_stay_h:
                    our_h_real += 1
            elif neighbor in self.opponent_zoc and self.state[neighbor[0]][neighbor[1]] == 'H':
                h_neighbors = Agent.get_neighbours(neighbor)
                is_h_neighbor_going_to_stay_h = True
                for neighbor_neighbor in h_neighbors:
                    try:
                        if neighbor_neighbor != coordinate and self.state[neighbor_neighbor[0]][neighbor_neighbor[1]] == 'S':
                            is_h_neighbor_going_to_stay_h = False
                    except IndexError:
                        pass
                if is_h_neighbor_going_to_stay_h:
                    ai_h_real += 1

        h = our_h_real - ai_h_real * 1
        if s3_neighbors > 0:
            h *= 0.99
        return h

    def healthy_heuristic(self, healthy, coordinate):
        """
        Heurstic:
            If all neighbours are AI: -1
            Else: #num_our_h + 5*I[has_sick_neighbor]
            Vaccinate if val >= 0 (max val)

        Tie breaker:
        1.  minus Num H of ai
        2. Num s neighbors
        3. num h neighbors that dont have s neighbor
        """
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        our_h = 0
        ai_n = 0
        ai_h = 0
        num_s_n = 0
        for neighbor in neighbors:
            try:
                if self.state[neighbor[0]][neighbor[1]] == 'S':
                    num_s_n += 1
            except IndexError:
                pass
            if neighbor in healthy and neighbor in self.zoc:
                our_h += 1

            if neighbor in self.opponent_zoc:
                ai_n += 1
                if self.state[neighbor[0]][neighbor[1]] == 'H':
                    ai_h += 1

        h_val = our_h
        if num_s_n > 0:
            h_val += 5
            h_val += (num_s_n/100)

        if ai_h > 0:
            h_val *= 0.99

        if ai_n == 4:
            h_val = -1

        return h_val

    def act(self, state):
        self.old_state = deepcopy(self.state)
        self.state = state
        action = []
        healthy, sick = self.process_state(state)
        healthy_unsorted = healthy.copy()
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        healthy.sort(key=lambda x: self.healthy_heuristic(healthy_unsorted, x), reverse=True)

        try:

            to_quarantine = []

            val1 = self.sick_heuristic(healthy, sick[0])
            if val1 > 0:
                to_quarantine.append(sick[0])

            val2 = self.sick_heuristic(healthy, sick[1])
            if val2 > 0:
                to_quarantine.append(sick[1])

        except IndexError:
            to_quarantine = []

        try:
            val1 = self.healthy_heuristic(healthy_unsorted, healthy[0])
            if val1 >= 0:
                to_vaccinate = [(healthy[0])]
            else:
                to_vaccinate = []
        except IndexError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

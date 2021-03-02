from copy import deepcopy
ids = ['206202731']

DIMENSIONS = (10, 10)

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        if order == 'first':
            self.order = 0
        else:
            self.order = 1
        len_row = DIMENSIONS[0]
        len_col = DIMENSIONS[1]
        i_j_set = set()
        for i in range(len_row):
            for j in range(len_col):
                i_j_set.add((i, j))
        self.adv_zoc = [(i, j) for (i, j) in i_j_set if ((i, j) not in zone_of_control and 'U' not in initial_state[i][j])]


    def process_state(self, state):
        healthy = []
        sick = []
        adv_healthy = []
        adv_sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        for (i, j) in self.adv_zoc:
            if 'H' in state[i][j]:
                adv_healthy.append((i, j))
            if 'S' in state[i][j]:
                adv_sick.append((i, j))

        for coordinate in sick:  # remove S without neighbors H
            neighbors = ((coordinate[0] - 1, coordinate[1]),
                         (coordinate[0] + 1, coordinate[1]),
                         (coordinate[0], coordinate[1] - 1),
                         (coordinate[0], coordinate[1] + 1))
            h = sum(1 for neighbor in neighbors if (neighbor in healthy or neighbor in adv_healthy))
            if h == 0:
                sick.remove(coordinate)

        return healthy, sick, adv_healthy, adv_sick

    def healthy_heuristic(self, sick, adv_sick, coordinate):  # neighbors S from both areas of zoc
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in sick or neighbor in adv_sick))
        return h

    def healthy_heuristic2(self, healthy, sick, adv_sick, coordinate):  # neighbors S from both areas of zoc
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = 0
        for neighbor in neighbors:
            neighbors_of_neighbors = ((neighbor[0] - 2, neighbor[1]),
                                      (neighbor[0] + 2, neighbor[1]),
                                      (neighbor[0], neighbor[1] - 2),
                                      (neighbor[0], neighbor[1] + 2))
            for neighbor2 in neighbors_of_neighbors:
                if neighbor in healthy and (neighbor2 in sick or neighbor2 in adv_sick):
                    h += 1
        return h

    def healthy_heuristic_my_zoc(self, sick, coordinate):  # neighbors S from my area of zoc
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in sick and neighbor in self.zoc))
        return h

    def healthy_heuristic_adv_zoc(self, adv_sick, coordinate):  # neighbors S from adv area of zoc
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in adv_sick and neighbor in self.adv_zoc))
        return h

    def sick_heuristic_my_zoc(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h

    def sick_heuristic_adv_zoc(self, adv_healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in adv_healthy and neighbor in self.adv_zoc))
        return h

    def remove_redundent_sick(self, healthy, sick, adv_healthy):
        new_sick = []
        for coordinate in sick:
            neighbors = ((coordinate[0] - 1, coordinate[1]),
                         (coordinate[0] + 1, coordinate[1]),
                         (coordinate[0], coordinate[1] - 1),
                         (coordinate[0], coordinate[1] + 1))
            h1 = sum(1 if (neighbor in healthy) else 0 for neighbor in neighbors)
            h2 = 0
            for neighbor in neighbors:
                neighbors_of_neighbors = ((neighbor[0] - 2, neighbor[1]),
                                          (neighbor[0] + 2, neighbor[1]),
                                          (neighbor[0], neighbor[1] - 2),
                                          (neighbor[0], neighbor[1] + 2))
                for neighbor2 in neighbors_of_neighbors:
                    if neighbor in healthy and neighbor2 in healthy:
                        h2 += 1
            h3 = sum(1 if (neighbor in adv_healthy) else 0 for neighbor in neighbors)
            if (h1 >= 3 or h2 >= 5) and ((h3 < 1 and not self.order) or (h3 < 2 and self.order)):
                new_sick.append(coordinate)
        return new_sick

    def sick_heuristic_my_zoc2(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = 0
        for neighbor in neighbors:
            neighbors_of_neighbors = ((neighbor[0] - 2, neighbor[1]),
                                      (neighbor[0] + 2, neighbor[1]),
                                      (neighbor[0], neighbor[1] - 2),
                                      (neighbor[0], neighbor[1] + 2))
            for neighbor2 in neighbors_of_neighbors:
                if neighbor in healthy and neighbor2 in healthy:
                    h += 1
        return h

    def heuristic_act(self, state):
        action = []
        healthy, sick, adv_healthy, adv_sick = self.process_state(state)
        healthy.sort(key=lambda x: self.healthy_heuristic2(healthy, sick, adv_sick, x),
                     reverse=True)  # now sort on primary key
        healthy.sort(key=lambda x: self.healthy_heuristic_adv_zoc(adv_sick, x), reverse=True)  # sort on secondary key, descending order
        healthy.sort(key=lambda x: self.healthy_heuristic(sick, adv_sick, x), reverse=True)  # now sort on primary key, descending order
        try:
            to_vaccinate = (healthy[:1])
            healthy = healthy[1:]
            # optimization for not consider this item as H anymore while counting neighbors H of S. because will be I
        except ValueError:
            to_vaccinate = []
        sick = self.remove_redundent_sick(healthy, sick, adv_healthy)
        sick.sort(key=lambda x: self.sick_heuristic_adv_zoc(adv_healthy, x))  # sort on secondary key, ascending order
        sick.sort(key=lambda x: self.sick_heuristic_my_zoc2(healthy, x), reverse=True)  # now sort on primary key, descending order
        sick.sort(key=lambda x: self.sick_heuristic_my_zoc(healthy, x), reverse=True)  # now sort on primary key, descending order
        try:
            to_quarantine = (sick[:2])
        except KeyError:
            try:
                to_quarantine = (sick[:1])
            except KeyError:
                to_quarantine = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))

        return action


    def act(self, state):
        return self.heuristic_act(state)

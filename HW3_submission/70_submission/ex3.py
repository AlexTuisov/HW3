from copy import deepcopy

ids = ['Our Agent']

def create_initial(initial_state):
    for i in range(len(initial_state)):
        for j in range(len(initial_state[1])):
            if initial_state[i][j] == 'S':
                initial_state[i][j] = 'S1'
            # relevant only if order == second
            elif initial_state[i][j] == 'Q':
                initial_state[i][j] = 'Q1'
    return initial_state


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.initial_state = create_initial(initial_state)
        self.updated_state = deepcopy(self.initial_state)
        self.prev_state = self.updated_state
        self.order = order
        self.started = False

    def process_state(self, state):
        our_healthy, total_healthy = [], []
        our_sick, total_sick = [], []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                our_healthy.append((i, j))
            if 'S' in state[i][j]:
                our_sick.append((i, j))

        for i in range(len(state)):
            for j in range(len(state[0])):
                if 'H' in state[i][j]:
                    total_healthy.append((i, j))
                if 'S' in state[i][j]:
                    total_sick.append((i, j))

        return our_healthy, our_sick, total_healthy, total_sick

    def calc_score(self, healthy, coordinate):

        x, y = coordinate[0], coordinate[1]

        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))

        # Wrong number of far neighbors - with duplicates - works better overall
        h += sum(1 for neighbor in neighbors
                 for far_neighbor in self.get_healthy_neighbors(healthy, neighbor)
                 if (neighbor in healthy and far_neighbor in healthy))

        # get_n_enemy_healthy_neighbors()
        # Right number of far neighbors -  without duplicates
        # h+= len(set(far_neighbor for neighbor in neighbors
        #                  for far_neighbor in self.get_healthy_neighbors(healthy, neighbor)
        #                  if (neighbor in healthy and far_neighbor in healthy)))

        # Subtract number of sick turns from score ( if S3 :  h = h-3 )
        # h -= int(self.updated_state[x][y][1])

        return h

    def n_of_healthy_neighbors(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        h += sum(1 for neighbor in neighbors
                 for far_neighbor in self.get_healthy_neighbors(healthy, neighbor)
                 if (neighbor in healthy and far_neighbor in healthy))

        # h+= len(set(far_neighbor for neighbor in neighbors
        #                  for far_neighbor in self.get_healthy_neighbors(healthy, neighbor)
        #                  if (neighbor in healthy and far_neighbor in healthy)))

        return h

    def get_healthy_neighbors(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h_neighbors = [neighbor for neighbor in neighbors if (neighbor in healthy)]
        return h_neighbors

    def get_n_enemy_healthy_neighbors(self, all_healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h_neighbors = [neighbor for neighbor in neighbors if (neighbor in all_healthy and neighbor not in self.zoc)]
        return len(h_neighbors)

    def sum_all_healthy_neighbors_distance_2(self, all_healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h_neighbors = [neighbor for neighbor in neighbors if (neighbor in all_healthy)]

        # h_neighbors += [far_neighbor for neighbor in neighbors
        #                 for far_neighbor in self.get_healthy_neighbors(all_healthy, neighbor)
        #                 if (neighbor in all_healthy and far_neighbor in all_healthy)]

        return sum(1 for neighbor in set(h_neighbors) if neighbor in self.zoc)

    def update_state(self, input_state):
        self.updated_state = deepcopy(input_state)

        for i in range(len(self.updated_state)):
            for j in range(len(self.updated_state[0])):
                if self.order == 'first':
                    if 'Q' in self.updated_state[i][j] and 'S' in self.prev_state[i][j]:  # sick and was healthy
                        self.updated_state[i][j] = 'Q1'

                elif self.order == 'second':
                    if 'Q' in self.updated_state[i][j] and 'S' in self.prev_state[i][j]:  # sick and was healthy
                        self.updated_state[i][j] = 'Q0'
                    # WE FORGOT THIS CONDITION
                    elif 'Q' in self.updated_state[i][j] and 'H' in self.prev_state[i][j]:  # sick and was healthy
                        self.updated_state[i][j] = 'Q0'

                if 'S' in self.updated_state[i][j] and 'H' in self.prev_state[i][j]:  # sick and was healthy
                    self.updated_state[i][j] = 'S1'
                elif 'S' in self.updated_state[i][j] and 'S' in self.prev_state[i][j]:  # sick and was sick
                    turn = int(self.prev_state[i][j][1])
                    self.updated_state[i][j] = 'S' + str(turn + 1)
                elif 'Q' in self.updated_state[i][j] and 'Q' in self.prev_state[i][j]:  # quarantined and was quarantined
                    turn = int(self.prev_state[i][j][1])
                    self.updated_state[i][j] = 'Q' + str(turn + 1)

        self.prev_state = deepcopy(self.updated_state)

    def act(self, state):

        # self.print_state(state)

        # Update the state in order to use them in our score func
        if not self.started:
            # updated_state = self.initial_state
            self.started = True
        else:
            self.update_state(state)

        action = []
        our_healthy, our_sick, total_healthy, total_sick = self.process_state(state)
        # our_sick.sort(key=lambda x: self.sum_all_healthy_neighbors_distance_2(total_healthy, x), reverse=True)
        our_sick.sort(key=lambda x: self.calc_score(our_healthy, x), reverse=True)

        vac_potential = set()
        for sick_tile in total_sick:
            h_neighbors = self.get_healthy_neighbors(our_healthy, sick_tile)
            vac_potential.update(h_neighbors)
            # for inner_neighbor in h_neighbors:
            #     h_h_neighbors = self.get_healthy_neighbors(our_healthy, inner_neighbor)

        vac_priority = list(vac_potential)
        # vac_priority.sort(key=lambda x: self.sum_all_healthy_neighbors_distance_2(total_healthy, x), reverse=True)
        vac_priority.sort(key=lambda x: self.n_of_healthy_neighbors(our_healthy, x), reverse=True)

        vac_priority.extend([tile for tile in our_healthy if tile not in vac_potential])

        try:
            to_quarantine = []
            if (self.calc_score(our_healthy, our_sick[0]) >= 3):
                to_quarantine.append(our_sick[0])
            # if (self.n_of_healthy_neighbors(our_healthy,  our_sick[1]) >= 4):
            #     to_quarantine.append(our_sick[1])
        except (KeyError, IndexError):
            to_quarantine = []

        try:
            if (self.calc_score(our_healthy, our_sick[1]) >= 3):
                to_quarantine.append(our_sick[1])
        except (KeyError, IndexError):
            pass

        try:
            i = 0
            # Doesn't allow vaccination to H tiles near to_quarantine tiles
            while vac_priority[i] in [item2 for item in to_quarantine
                                      for item2 in self.get_healthy_neighbors(our_healthy, item)]:
                i += 1
            to_vaccinate = [(vac_priority[i])]
        except (ValueError, IndexError):
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

    def print_state(self, state):
        for i in range(len(state)):
            #
            for j in range(len(state[0])):
                if i == 0:
                    print(j, end="     ")
            print()
            for j in range(len(state[1])):
                if (i, j) in self.zoc:
                    print('*' + str(state[i][j]) + '*', end="   ")
                else:
                    print('_' + str(state[i][j]) + '_', end="   ")
            print()
        print()

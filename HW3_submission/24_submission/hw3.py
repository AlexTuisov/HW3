DIMENSIONS = (10, 10)

ids = ['315880575', '205847932']


def get_neighbors(coordinates, board_size=DIMENSIONS, exclude=tuple()):
    # gets the coordinates of the neighboring tile
    neighbors = list()
    if coordinates[0] != 0 and (coordinates[0] - 1, coordinates[1]) not in exclude:
        neighbors.append((coordinates[0] - 1, coordinates[1]))
    if coordinates[1] != 0 and (coordinates[0], coordinates[1] - 1) not in exclude:
        neighbors.append((coordinates[0], coordinates[1] - 1))
    if coordinates[0] != board_size[0] - 1 and (coordinates[0] + 1, coordinates[1]) not in exclude:
        neighbors.append((coordinates[0] + 1, coordinates[1]))
    if coordinates[1] != board_size[1] - 1 and (coordinates[0], coordinates[1] + 1) not in exclude:
        neighbors.append((coordinates[0], coordinates[1] + 1))
    return neighbors  # left down right up


def get_neighbors_neighbors(coordinates, board_size=DIMENSIONS, exclude=tuple()):
    non = list()
    neighbors = get_neighbors(coordinates, board_size, exclude)
    for n in neighbors:
        nn = get_neighbors(n, board_size, exclude)
        non.append([])  # seperating them is unnecessary here so this is commented
        for tile in nn:
            if tile not in non and tile != coordinates:
                non[-1].append(tile)
    return non  # [[LL, LD, LU], [DL, DD, DR], [RD, RR, RU], [UL, UU, UR]] #currently not seperated (irrelevant)


def get_possible_actions(teams, actions):
    if teams == 0:
        return [[()]]
    possible_actions = list()
    starters = list()
    actions_len = len(actions)
    for i in range(actions_len):
        possible_actions.append([actions[i]])
        starters.append(i + 1)

    temp_actions = list()
    next_len = 0

    for i in range(1, teams):
        for comb in possible_actions[next_len:]:
            for action in actions:
                # comparing (y1, x1) and (y2, x2), the comparison is  y1*10 + x1 > y2*10 + x2
                if action[1][0] * 10 + action[1][1] > comb[-1][1][0] * 10 + comb[-1][1][1]:
                    temp_actions.append(comb + [action])
        next_len = len(possible_actions)
        possible_actions += temp_actions
        temp_actions = list()

    temp_actions.append([()])
    # possible_actions.append([()])
    return possible_actions
    # return temp_actions if teams > 1 else possible_actions


def mapper(elem):
    if elem == 'U' or elem == 'H' or elem == 'I':
        return elem, 0
    elif elem == 'Q':
        return elem, 2
    return elem, 3

#### Single Mega Heuristic agent #####
class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order

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
        neighbors = get_neighbors(coordinate)
        neighbors_neighbors = get_neighbors_neighbors(coordinate)
        h = sum(2 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        nh = 0
        for i in range(len(neighbors_neighbors)):
            for nn in neighbors_neighbors[i]:
                if neighbors[i] in healthy and nn in healthy and nn in self.zoc:
                    nh += 1
        # nh = sum(0.5 for nn in neighbors_neighbors if (nn in healthy and nn in self.zoc))
        return h + nh

    def healthy_heuristic(self, coordinate, state):
        neighbors = get_neighbors(coordinate)
        neighbors_neighbors = get_neighbors_neighbors(coordinate)
        h = sum(10 for neighbor in neighbors if (state[neighbor[0]][neighbor[1]] == "S"))
        nh = 0
        for i in range(len(neighbors_neighbors)):
            for nn in neighbors_neighbors[i]:
                if state[neighbors[i][0]][neighbors[i][1]] == "H" and state[nn[0]][nn[1]] == "S":
                    nh += 1
        return h + nh

    def action_heuristic(self, action, state):
        h = 0
        threatened_sick = set()
        far_threat_sick = set()
        threat = set()
        far_threat = set()
        actions = set()
        for curr_action in action:
            actions.add(curr_action[1])
            n = get_neighbors(curr_action[1])
            nn = get_neighbors_neighbors(curr_action[1])
            if curr_action[0] == 'quarantine':
                for i in n:
                    if state[i[0]][i[1]] == "H" and i in self.zoc:
                        threatened_sick.add(i) # 3
                for id, i in enumerate(nn):
                    for j in i:
                        if state[n[id][0]][n[id][1]] == "H" and state[j[0]][j[1]] == "H" and j in self.zoc:
                            far_threat_sick.add(j) # 1
            elif curr_action[0] == 'vaccinate':
                for i in n:
                    if state[i[0]][i[1]] == "S":
                        threat.add(i) # 10
                    for id, i in enumerate(nn):
                        for j in i:
                            if state[n[id][0]][n[id][1]] == "H" and state[j[0]][j[1]] == "S":
                                far_threat.add(j) # 1
        #insert math here
        for i in threatened_sick:
            if i not in actions:
                h += 10
        for i in far_threat_sick:
            if i not in actions:
                h += 3
        for i in threat:
            factor = 1
            n = get_neighbors(i)
            nn = get_neighbors_neighbors(i)
            for j in n:
                factor += 1
            if i not in actions:
                h += 10 + factor
        for i in far_threat:
            if i not in actions:
                h += 1
        return h

    def act(self, state):
        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        healthy.sort(key=lambda x: self.healthy_heuristic(x, state), reverse=True)
        sick = sick[:min(10, len(sick))]
        healthy = healthy[:min(10, len(healthy))]

        paction, maction = [], []
        for item in sick:
            paction.append(('quarantine', item))
        for item in healthy:
            maction.append(('vaccinate', item))
        police_actions = get_possible_actions(2, paction)
        medics_actions = get_possible_actions(1, maction)
        actions = list()
        for i in range(len(police_actions)):
            actions.append(tuple(police_actions[i]))
            for j in range(len(medics_actions)):
                actions.append(tuple(medics_actions[j]))
                actions.append(tuple(police_actions[i] + medics_actions[j]))
        actions.append(tuple())

        actions = [(i, self.action_heuristic(i, state)) for i in actions]
        actions.sort(key=lambda x: x[1], reverse=True)
        action = actions[0][0]

        return action


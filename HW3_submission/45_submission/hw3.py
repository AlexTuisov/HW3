import itertools
import random
import time

ids = ['319126397', '211990270']

NUM_MEDICS = 1
NUM_POLICE = 2
VAC = 'vaccinate'
QUAR = 'quarantine'
MAX_DECISION_TIME = 4  # seconds


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = self.get_initial_state(initial_state)  # convert "map" form state to "dict" form
        self.zoc = zone_of_control  # list of zoc tiles (i, j)
        self.order = order  # play first or second

        # do stuff
        self.rows = len(initial_state)
        self.cols = len(initial_state[0])
        self.current_state = self.initial_state
        self.all_neighbours_dict = self.get_all_neighbours_dict()  # {(i, j): [neighbours]}
        self.zoc_neighbours_dict = self.get_zoc_neighbours_dict()  # {(i, j): [neighbour s.t. neighbour in ZOC]}
        self.turn = -1
        self.minmax_depth = 3
        self.sample_proba = None
        self.sort_inside_max = True
        self.sort_inside_min = True
        self.with_police = False
        self.agent_name = f"Itai Arieli, depth={self.minmax_depth} use_police={self.with_police}"
        self.total_succ = 0
        self.longest_sorting_time = float('-inf')
        self.print = False
        if self.print:
            print("Welcome to the stage, the one and only, rational agent:")
            print(self.agent_name)

    def get_zoc_neighbours_dict(self):
        zoc_neighbours_dict = {}
        for tile, neighbours in self.all_neighbours_dict.items():
            tile_zoc_neighbours = []
            for neighbour in neighbours:
                if neighbour in self.zoc:
                    tile_zoc_neighbours.append(neighbour)
            zoc_neighbours_dict[tile] = tile_zoc_neighbours
        return zoc_neighbours_dict

    def get_tile_neighbours(self, tile):
        i, j = tile
        neighbours = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        if i == 0:
            neighbours.remove((i - 1, j))
        if i == self.rows - 1:
            neighbours.remove((i + 1, j))
        if j == 0:
            neighbours.remove((i, j - 1))
        if j == self.cols - 1:
            neighbours.remove((i, j + 1))
        return neighbours

    def get_all_neighbours_dict(self):
        neighbours_dict = {}
        for i in range(self.rows):
            for j in range(self.cols):
                neighbours_dict[(i, j)] = self.get_tile_neighbours((i, j))
        return neighbours_dict

    @staticmethod
    def get_initial_state(initial_map: list) -> dict:
        """
        Gets an initial map List[List[str]] and returns it's state representation dict[tuple: str]
        :param initial_map: map of the game
        :return:
        """
        initial_state = {}
        for i in range(len(initial_map)):
            for j in range(len(initial_map[0])):
                if initial_map[i][j] == 'S':
                    initial_state[(i, j)] = 'S0'
                    continue
                if initial_map[i][j] == 'U':
                    initial_state[(i, j)] = 'U'
                    continue
                if initial_map[i][j] == 'H':
                    initial_state[(i, j)] = 'H'
                    continue
                if initial_map[i][j] == 'Q':
                    print(f"Warning! Initial state includes Q tile at [{i}][{j}]")
                    initial_state[(i, j)] = 'Q0'
                    continue
                if initial_map[i][j] == 'I':
                    print(f"Warning! Initial state includes I tile at [{i}][{j}]")
                    initial_state[(i, j)] = 'I'
                    continue
        return initial_state

    @staticmethod
    def get_new_state(current_state: dict, new_map: list, order: str) -> dict:
        """
        Gets a new map  and current state and returns it's evolved state .
        :param current_state: dict[tuple: str]
        :param new_map: List[List[str]]
        :param order: 'first' / 'second'
        :return:
        """
        new_state = {}
        for (i, j), t in current_state.items():
            if new_map[i][j] == 'S':
                if t == 'H':
                    new_state[(i, j)] = 'S0'
                elif t == 'S0':
                    new_state[(i, j)] = 'S1'
                elif t == 'S1':
                    new_state[(i, j)] = 'S2'
                else:
                    raise RuntimeError(f"Illegal update! Tried to replace current_state[({i}, {j})]={t} with {new_map[i][j]}!")
                continue
            if new_map[i][j] == 'U':
                if t == 'U':
                    new_state[(i, j)] = 'U'
                else:
                    raise RuntimeError(f"Illegal update! Tried to replace current_state[({i}, {j})]={t} with {new_map[i][j]}!")
                continue
            if new_map[i][j] == 'H':
                if t == 'S2' or t == 'Q1' or t == 'H':
                    new_state[(i, j)] = 'H'
                else:
                    raise RuntimeError(f"Illegal update! Tried to replace current_state[({i}, {j})]={t} with {new_map[i][j]}!")
                continue
            if new_map[i][j] == 'Q':
                if t[0] == 'S':
                    new_state[(i, j)] = 'Q0'
                elif t == 'Q0':
                    new_state[(i, j)] = 'Q1'
                elif order == 'second' and t == 'H':
                    new_state[(i, j)] = 'Q0'
                elif order == 'second' and t == 'Q1':
                    new_state[(i, j)] = 'H'
                else:
                    raise RuntimeError(f"Illegal update! Tried to replace current_state[({i}, {j})]={t} with {new_map[i][j]}!")
                continue
            if new_map[i][j] == 'I':
                if t == 'H' or t == 'I' or (order == 'second' and t == 'S2') or (order == 'second' and t == 'Q1'):
                    new_state[(i, j)] = 'I'
                else:
                    raise RuntimeError(f"Illegal update! Tried to replace current_state[({i}, {j})]={t} with {new_map[i][j]}!")
                continue
        return new_state

    def act(self, state):
        start = time.time()
        # update current state based on new map observation
        self.turn += 1
        if self.print:
            print()
            print(f"turn={self.turn:2d}")
        if not self.turn == 0:
            self.current_state = self.get_new_state(current_state=self.current_state,
                                                    new_map=state,
                                                    order=self.order)

        # choose action
        action = self.minimax_decision(self.current_state)
        if self.print:
            print(f"\tseconds to act                      {time.time() - start:.3f}")
        return action

    def get_possible_actions(self, state):
        """
        Given a current state and ZOC, returns all possible actions that our agent is able to perform.
        :param state: board
        :return:
        """

        healthy = set()
        sick = set()
        for (i, j) in self.zoc:
            if state[(i, j)] == 'H':
                healthy.add((i, j))
            if state[(i, j)][0] == 'S':  # S0 / S1 / S2
                sick.add((i, j))

        # TODO https://moodle.technion.ac.il/mod/forum/discuss.php?d=560106

        # all_police = set()
        all_police = set(itertools.combinations(sick, 0))
        if self.with_police:
            all_police = all_police.union(set(itertools.combinations(sick, 1)))
            all_police = all_police.union(set(itertools.combinations(sick, 2)))

        all_medics = set()
        # all_medics = set(itertools.combinations(healthy, 0))
        all_medics = all_medics.union(set(itertools.combinations(healthy, 1)))

        legal_actions = set(itertools.product(all_police, all_medics))
        returned_actions = []
        for action in legal_actions:
            police_stuff, medics_stuff = action[0], action[1]
            combined = []
            for atom_action in police_stuff:
                combined.append((QUAR, atom_action))
            for atom_action in medics_stuff:
                combined.append((VAC, atom_action))
            returned_actions.append(combined)

        return sorted(returned_actions)

    def succ(self, state):
        succ = [(action, self.apply_action(action, state)) for action in self.get_possible_actions(state)]
        self.total_succ += len(succ)
        return succ

    def minimax_decision(self, state):
        start = time.time()
        chosen_value, chosen_action = float('-inf'), []

        alpha, beta = float('-inf'), float('inf')

        # sort based on heuristic
        succ = self.succ(state)
        succ.sort(key=lambda x: self.sick_heuristic(x[1]), reverse=True)
        sorting_time = time.time() - start
        if self.print:
            print(f"\tseconds wasted on heuristic         {time.time() - start:.3f}")
        if sorting_time > self.longest_sorting_time:
            self.longest_sorting_time = sorting_time

        total_explored = 0
        for action, s_tag in succ:

            if time.time() - start > MAX_DECISION_TIME:
                if self.print:
                    print(f"\tTimed out, states explored: {total_explored:5d} / {len(succ):5d}")
                break

            new_value = self.min_value(s_tag, alpha, beta, 1)
            if new_value > chosen_value:
                chosen_value = new_value
                chosen_action = action
            total_explored += 1

        return chosen_action

    def min_value(self, state, alpha, beta, depth):
        if self.terminal_test(state) or depth == self.minmax_depth:
            return self.utility(state)

        value = float('inf')

        succ = self.succ(state)
        if self.sample_proba:
            succ = random.sample(population=succ, k=round(self.sample_proba * len(succ)))
        if self.sort_inside_min:
            succ.sort(key=lambda x: self.sick_heuristic(x[1]), reverse=True)

        for _, s_tag in succ:
            new_value = self.max_value(s_tag, alpha, beta, depth + 1)
            if new_value < value:
                value = new_value
            if value <= alpha:
                return value
            beta = min(beta, value)

        depth += 1

        return value

    def max_value(self, state, alpha, beta, depth):
        if self.terminal_test(state) or depth == self.minmax_depth:
            return self.utility(state)

        value = float('-inf')

        succ = self.succ(state)
        if self.sample_proba:
            succ = random.sample(population=succ, k=round(self.sample_proba * len(succ)))
        if self.sort_inside_max:
            succ.sort(key=lambda x: self.sick_heuristic(x[1]), reverse=True)

        for _, s_tag in succ:
            new_value = self.min_value(s_tag, alpha, beta, depth + 1)
            if new_value > value:
                value = new_value
            if value >= beta:
                return value
            alpha = max(alpha, value)

        depth += 1

        return value

    def utility(self, state):
        utility = 0

        for (i, j) in self.zoc:
            if state[(i, j)] == 'H':
                utility += 1
                continue
            if state[(i, j)] == 'I':
                utility += 1
                continue
            if state[(i, j)] == 'S':
                utility -= 1
                continue
            if state[(i, j)] == 'Q':
                utility -= 5
                continue

        return utility

    def sick_heuristic(self, state):
        h = 0
        for tile in state.keys():
            neighbors = self.zoc_neighbours_dict[tile]
            h += sum(1 for neighbor in neighbors if state[neighbor] == 'H')
        return h

    @staticmethod
    def terminal_test(state):
        return 'S' not in [v[0] for v in state.values()]  # take first letter of state

    def has_sick_neighbour(self, i, j, state):
        for neighbour in self.all_neighbours_dict[(i, j)]:
            if state[neighbour][0] == 'S':
                return True
        return False

    @staticmethod
    def __2_action_effects(action, new_state):
        for atomic_action in action:
            effect, (i, j) = atomic_action[0], atomic_action[1]
            if effect == VAC:
                new_state[(i, j)] = 'I'
                continue
            if effect == QUAR:
                new_state[(i, j)] = 'Q0'
                continue
        return new_state

    def __3_spread_infection(self, current_state, protected_tiles, new_state):
        for (i, j) in current_state.keys():
            if (i, j) in protected_tiles:
                continue
            if 'H' in current_state[(i, j)] and self.has_sick_neighbour(i, j, current_state):
                new_state[(i, j)] = 'S0'
        return new_state

    @staticmethod
    def __4_5_expire_sickness_and_quar(current_state, protected_tiles, new_state):
        for (i, j) in current_state.keys():
            if (i, j) in protected_tiles:
                continue

            if 'S' in current_state[(i, j)]:
                turn = int(current_state[(i, j)][1])
                if turn < 2:
                    new_state[(i, j)] = 'S' + str(turn + 1)
                else:
                    new_state[(i, j)] = 'H'

            elif 'Q' in current_state[(i, j)]:
                turn = int(current_state[(i, j)][1])
                if turn < 1:
                    new_state[(i, j)] = 'Q' + str(turn + 1)
                else:
                    new_state[(i, j)] = 'H'
        return new_state

    def apply_action(self, action, current_state):
        """
        Gets a state and an action and returns the state after applying this action.
        Does not account for nature.
        :param action:
        :param current_state:
        :return:
        """
        new_state = current_state.copy()
        protected_tiles = [atom_action[1] for atom_action in action]

        # 1) You choose which actions to perform

        # 2) Your chosen actions take effect
        new_state = self.__2_action_effects(action, new_state)

        # 3) Infection spreads
        new_state = self.__3_spread_infection(current_state, protected_tiles, new_state)

        # 4 + 5) Sickness + quarantine expires
        new_state = self.__4_5_expire_sickness_and_quar(current_state, protected_tiles, new_state)

        return new_state

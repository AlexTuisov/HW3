import itertools
import random

import hw3
import sample_agent
from copy import deepcopy
import time

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5
DIMENSIONS = (10, 10)
PENALTY = 1000


def pad_the_input(a_map):
    state = {}
    new_i_dim = DIMENSIONS[0] + 2
    new_j_dim = DIMENSIONS[1] + 2
    for i in range(0, new_i_dim):
        for j in range(0, new_j_dim):
            if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                state[(i, j)] = 'U'
            else:
                state[(i, j)] = a_map[i - 1][j - 1]
    return state


class Game:
    def __init__(self, a_map):
        self.ids = [hw3.ids, sample_agent.ids]
        self.initial_state = pad_the_input(a_map)
        self.control_zone_1 = None
        self.control_zone_2 = None
        self.divide_map()
        self.score = [0, 0]
        self.agents = []
        self.state = deepcopy(self.initial_state)

    def state_to_agent(self):
        state_as_list = []
        for i in range(DIMENSIONS[0]):
            state_as_list.append([])
            for j in range(DIMENSIONS[1]):
                state_as_list[i][j] = self.state[(i + 1, j + 1)][0]
        return state_as_list

    def initiate_agent(self, module, control_zone, first):
        start = time.time()
        control_zone_to_agent = [(i -1, j - 1) for (i, j) in control_zone]
        agent = module.Agent(control_zone_to_agent, first)
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(module.ids)
        return agent

    def divide_map(self):
        habitable_tiles = [(i, j) for i, j in
                           itertools.product(range(1, DIMENSIONS[0] + 1),
                                             range(1, DIMENSIONS[1] + 1)) if 'U' not in self.state[(i, j)]]
        random.shuffle(habitable_tiles)

        half = len(habitable_tiles)//2
        self.control_zone_1 = set(habitable_tiles[:half])
        self.control_zone_2 = set(habitable_tiles[half:])
        assert len(self.control_zone_1) == len(self.control_zone_2)

    def get_action(self, agent):
        action = agent.act(self.state_to_agent())
        return action

    def check_if_action_legal(self, action):
        if len(action) > 3:
            return False
        count = {'vaccinate': 0, 'quarantine': 0}
        for atomic_action in action:
            location, effect = atomic_action[1], atomic_action[0]
            try:
                status = self.state[location]
            except KeyError:
                return False
            if effect.lower() not in ['vaccinate', 'quarantine']:
                return False
            count[effect] += 1
            if count['vaccinate'] > 1 or count['quarantine'] > 2:
                return False
            if effect == 'vaccinate' and 'H' not in status:
                return False
            if effect == 'quarantine' and 'S' not in status:
                return False

        return True

    def apply_action(self, actions):
        for action in actions:
            location, effect = action[1], action[0]
            if 'v' in effect:
                self.state[location] = 'I'
            else:
                self.state[location] = 'Q0'

    def change_state(self):
        new_state = deepcopy(self.state)

        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if self.state[(i, j)] == 'H' and ('S' in self.state[(i - 1, j)] or
                                                  'S' in self.state[(i + 1, j)] or
                                                  'S' in self.state[(i, j - 1)] or
                                                  'S' in self.state[(i, j + 1)]):
                    new_state[(i, j)] = 'S0'

        # advancing sick counters
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if 'S' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

                # advancing quarantine counters
                if 'Q' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 2:
                        new_state[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

        self.state = new_state

    def update_scores(self):
        for (i, j) in self.control_zone_1:
            if 'H' in self.state[(i, j)]:
                self.score[0] += 1
            if 'S' in self.state[(i, j)]:
                self.score[0] -= 1
            if 'Q' in self.state[(i, j)]:
                self.score[0] -= 5

    def handle_constructor_timeout(self, agent):
        pass

    def get_legal_action(self, number_of_agent):
        start = time.time()
        action = self.get_action(self.agents[number_of_agent])
        finish = time.time()
        if finish - start > ACTION_TIMEOUT:
            self.score[number_of_agent] -= PENALTY
            print(f'agent of {self.ids[number_of_agent]} timed out on action!')
            return []
        if not self.check_if_action_legal(action):
            self.score[number_of_agent] -= PENALTY
            print(f'agent of {self.ids[number_of_agent]} chose illegal action!')
            return []
        return action

    def play_episode(self, swapped=False):
        while 'S' in self.state.values():
            if not swapped:
                action = self.get_legal_action(0)
                if not action:
                    return
                self.apply_action(action)

                action = self.get_legal_action(1)
                if not action:
                    return
                self.apply_action(action)
            else:
                action = self.get_legal_action(1)
                if not action:
                    return
                self.apply_action(action)

                action = self.get_legal_action(0)
                if not action:
                    return
                self.apply_action(action)

            self.change_state()
            self.update_scores()

    def play_game(self):
        print(f'starting a first round!')
        self.agents = [self.initiate_agent(hw3, self.control_zone_1, 'first'),
                       self.initiate_agent(sample_agent, self.control_zone_2, 'second')]
        self.play_episode()

        print(f'starting a second round!')
        self.state = deepcopy(self.initial_state)

        self.agents = [self.initiate_agent(hw3, self.control_zone_2, 'second'),
                       self.initiate_agent(sample_agent, self.control_zone_1, 'first')]

        self.play_episode(swapped=True)
        print(f'end of game!')
        return self.score


def main():
    a_map = []
    assert len(a_map) == DIMENSIONS[0]
    assert len(a_map[0]) == DIMENSIONS[1]
    game = Game(a_map)
    try:
        results = game.play_game()
        print(f'Score for {hw3.ids} is {results[0]}, score for {sample_agent.ids} is {results[1]}')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

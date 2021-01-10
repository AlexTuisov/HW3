import itertools

import hw3
import sample_agent
from copy import deepcopy
import time

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5
DIMENSIONS = (10, 10)


def state_to_agent(state):
    pass


class Game:
    def __init__(self):
        self.ids = [hw3.ids, sample_agent.ids]
        self.initial_state = None
        self.control_zone_1 = None
        self.control_zone_2 = None
        self.divide_map()
        self.score = [0, 0]
        self.agents = []
        self.state = deepcopy(self.initial_state)

    # def initiate_agents(self, control_zone_1, control_zone_2, swap=False):
    #     if swap:
    #         control_zone_1, control_zone_2 = control_zone_2, control_zone_1
    #     start = time.time()
    #     agent_1 = hw3.Agent(control_zone_1, 'first')
    #     if time.time() - start > CONSTRUCTOR_TIMEOUT:
    #         self.handle_constructor_timeout(agent_1)
    #
    #     start = time.time()
    #     agent_2 = sample_agent.Agent(control_zone_2, 'second')
    #     if time.time() - start > CONSTRUCTOR_TIMEOUT:
    #         self.handle_constructor_timeout(agent_2)
    #
    #     if swap:
    #         return agent_2, agent_1
    #     return agent_1, agent_2

    def initiate_agent(self, module, control_zone, first):
        start = time.time()
        agent = module.Agent(control_zone, first)
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(module.ids)
        return agent

    def divide_map(self):
        self.initial_state = None
        self.control_zone_1 = None
        self.control_zone_2 = None

    def get_action(self, agent):
        start = time.time()
        action = agent.act(self.state)
        if time.time() - start > ACTION_TIMEOUT:
            self.handle_action_timeout(agent)
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

        # advancing the sickness
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if 'S' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

                # quarantine expires
                if 'Q' in self.state[(i, j)]:
                    turn = int(self.state[(i, j)][1])
                    if turn < 2:
                        new_state[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

        self.state = new_state

    def update_scores(self):
        pass

    def handle_illegal_action(self, agent):
        pass

    def handle_action_timeout(self, agent):
        pass

    def handle_constructor_timeout(self, agent):
        pass

    def play_game(self):
        self.agents = [self.initiate_agent(hw3, self.control_zone_1, 'first'),
                       self.initiate_agent(sample_agent, self.control_zone_2, 'second')]
        self.play_episode()

        self.state = deepcopy(self.initial_state)

        self.agents = [self.initiate_agent(hw3, self.control_zone_2, 'second'),
                       self.initiate_agent(sample_agent, self.control_zone_1, 'first')]

        self.play_episode(swapped=True)
        return self.score

    def play_episode(self, swapped=False):
        while 'S' in self.state.values():
            action_1 = self.get_action(self.agents[0])
            if not self.check_if_action_legal(action_1):
                self.handle_illegal_action(agent_1)
            action_2 = self.get_action(agent_2)
            if not self.check_if_action_legal(action_2):
                self.handle_illegal_action(agent_2)
            if swapped:
                self.apply_action()
            self.apply_action([action_1, action_2])
            self.change_state()
            self.update_scores()


def main():
    game = Game()
    try:
        results = game.play_game()
        print(f'Score for {hw3.ids} is {results[0]}, score for {sample_agent.ids} is {results[1]}')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

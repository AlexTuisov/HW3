import agent1
import agent2
from copy import deepcopy
import time

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5

class Game:
    def __init__(self):
        self.state = None
        self.control_zone_1 = None
        self.control_zone_2 = None
        self.agent_1 = None
        self.agent_2 = None
        self.divide_map()
        self.initiate_agents()

    def initiate_agents(self):
        start = time.time()
        self.agent_1 = agent1.Agent(self.control_zone_1)
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(self.agent_1)
        start = time.time()
        self.agent_2 = agent2.Agent(self.control_zone_2)
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(self.agent_2)

    def divide_map(self):
        self.state = None
        self.control_zone_1 = None
        self.control_zone_2 = None

    def get_action(self, agent):
        start = time.time()
        action = agent.act(self.state)
        if time.time() - start > ACTION_TIMEOUT:
            self.handle_action_timeout(agent)
        return action

    def check_if_action_legal(self, action):
        pass

    def apply_action(self, action):
        self.check_if_action_legal(action)

    def handle_action_timeout(self, agent):
        pass

    def handle_constructor_timeout(self, agent):
        pass

    def play_episode(self):
        while 'S' in self.state.values():
            action_1 = self.get_action(self.agent_1)
            action_2 = self.get_action(self.agent_2)


def main():
    game = Game()


if __name__ == '__main__':
    main()



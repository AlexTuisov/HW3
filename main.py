import agent1
import agent2
from copy import deepcopy
import time

ACTION_TIMEOUT = 5

MAP = [
    [],
    [],
    [],
]

class Game:
    def __init__(self):
        state, control_zone_1, control_zone_2 = self.divide_map()
        agent_1 = agent1.Agent(control_zone_1)
        agent_2 = agent2.Agent(control_zone_2)

    def divide_map(self):
        return {}, None, None

    def get_action(self, agent, state):
        start = time.time()
        action = agent1.act(state)
        if time.time() - start > ACTION_TIMEOUT:
            self.handle_timeout(agent)


    def handle_timeout(self, agent):
        pass


    def play_episode(self, state, agent1, agent2):
        while 'S' in state.values():



def main():


    play_episode(deepcopy(state), agent1, agent2)





if __name__ == '__main__':
    main()



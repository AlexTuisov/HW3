import hw3
import sample_agent
from copy import deepcopy
import time

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5


def state_to_agent(state):
    pass

# meaningless comment


class Game:
    def __init__(self):
        self.initial_state = None
        self.control_zone_1 = None
        self.control_zone_2 = None
        self.score = [0, 0]
        self.agents = {hw3.ids: None,
                       sample_agent.ids: None}
        self.divide_map()
        self.state = deepcopy(self.initial_state)

    def initiate_agents(self, control_zone_1, control_zone_2, swap=False):
        if swap:
            control_zone_1, control_zone_2 = control_zone_2, control_zone_1
        start = time.time()
        agent_1 = hw3.Agent(control_zone_1, 'first')
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(agent_1)

        start = time.time()
        agent_2 = sample_agent.Agent(control_zone_2, 'second')
        if time.time() - start > CONSTRUCTOR_TIMEOUT:
            self.handle_constructor_timeout(agent_2)

        if swap:
            return agent_2, agent_1
        return agent_1, agent_2

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
        vaccine_count = 0
        quarantine_count = 0
        for atomic_action in action:
            location, effect = atomic_action[1], atomic_action[0]
            try:
                status = self.state[location]
            except KeyError:
                return False
            if effect.lower() not in ['vaccinate', 'quarantine']:
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
        pass

    def update_scores(self):
        pass

    def handle_illegal_action(self, agent):
        pass

    def handle_action_timeout(self, agent):
        pass

    def handle_constructor_timeout(self, agent):
        pass

    def play_game(self):
        agent_1, agent_2 = self.initiate_agents(self.control_zone_1, self.control_zone_2)
        self.play_episode(agent_1, agent_2)

        self.state = deepcopy(self.initial_state)

        agent_1, agent_2 = self.initiate_agents(self.control_zone_1, self.control_zone_2, swap=True)
        self.play_episode(agent_1, agent_2)
        return self.score

    def play_episode(self, agent_1, agent_2):
        while 'S' in self.state.values():
            action_1 = self.get_action(agent_1)
            if not self.check_if_action_legal(action_1):
                self.handle_illegal_action(agent_1)
            action_2 = self.get_action(agent_2)
            if not self.check_if_action_legal(action_2):
                self.handle_illegal_action(agent_2)
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



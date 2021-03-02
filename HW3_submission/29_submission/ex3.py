import random
import itertools
from copy import deepcopy

from time import time

ids = ['206312506', '206217366']


class Agent:
    # Class variables
    rewards = {'H':1, 'S':-1, 'Q':-5, 'U':0, 'I':0}
    police = 2
    medics = 1

    initial_state_encoding = {'H':'H','S':'S3','Q':'Q2','U':'U','I':'I'}
    progress_table = {'H':'H','S3':'S2','S2':'S1','S1':'H','Q2':'Q1','Q1': 'H','U':'U','I':'I'}

    max_minimax_depth = 1

    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = initial_state
        self.dim = (len(initial_state), len(initial_state[0]))
        
        self.zoc = zone_of_control

        # Find the opponent's ZOC
        zone = [(i,j) for i in range(self.dim[0]) for j in range(self.dim[1])]
        for z in self.zoc:
            zone.remove(z)
        self.non_zoc = zone

        self.order = 1*( order=='first' ) + 2*( order=='second' )
        self.act(initial_state)


    @staticmethod
    def evaluate_state(state,zoc):
        """
        Evaluate the value of a state according to a given ZOC
        """
        value = 0
        for i,j in zoc:
            value += Agent.rewards[state[i][j][0]]
        return value

    @staticmethod
    def actions(state, zoc, police=2, medics=1):
        """
        Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file
        """
        
        actions = list()

        for i,j in zoc:
            if state[i][j][0] == "H":
                actions.append(("vaccinate",(i,j)))
            if state[i][j][0] == "S":
                actions.append(("quarantine",(i,j)))


        max_actions = police + medics
        valid_actions = list()

        action_combinations = list()
        for i in range(1,max_actions+1):
            action_combinations.extend(itertools.combinations(actions, i))

        for action in action_combinations:
            # TODO: Consider removing redundent actions here!
            police_count = 0
            medics_count = 0
            for atomic_action in action:
                if atomic_action[0] == "vaccinate":
                    medics_count += 1
                if atomic_action[0] == "quarantine":
                    police_count += 1
            if police_count <= police and medics_count <= medics:
                valid_actions.append(action)

        return tuple(valid_actions)


    @staticmethod
    def perform_action(state, action):
        result_state = deepcopy(state)
        i = action[1][0]
        j = action[1][1]
        if action[0] == "vaccinate":
            result_state[i][j] = 'I'
        elif action[0] == "quarantine":
            result_state[i][j] = 'Q2'
        return result_state


    @staticmethod
    def count_neighbors(state, row, col, neighbor_state):
        count = 0
        if row > 0 and state[row-1][col][0] == neighbor_state:
                count += 1
        if col > 0 and state[row][col-1][0] == neighbor_state:
                count += 1
        if row + 1 < len(state) and state[row+1][col][0] == neighbor_state:
                count += 1
        if col + 1 < len(state[0]) and state[row][col+1][0] == neighbor_state:
                count += 1
        return count

    @staticmethod
    def progress_state(state):
        _state = list()
        for i in range(len(state)):
            row = list()
            for j in range(len(state[i])):
                if state[i][j] == "H" and Agent.count_neighbors(state, i, j, "S") > 0:
                    row.append("S3")
                else:
                    row.append(Agent.progress_table[state[i][j]])
            _state.append(row)
        return _state


    @staticmethod
    def encode_initial_state(state):
        _state = deepcopy(state)
        for row in _state:
            for i in range(len(row)):
                row[i] = Agent.initial_state_encoding[row[i]]
        return _state

    @staticmethod
    def test_terminal_state(state):
        flat_state = [s for row in state for s in row]
        return not ('S1' in flat_state or 'S2' in flat_state or 'S3' in flat_state)

    def act(self, state):
        # start = time()
        state = Agent.encode_initial_state(state)
        desicion = self.minimax_decision(state)
        end = time()
        return desicion

    def minimax_decision(self,state):
        possible_actions = Agent.actions(state, self.zoc, police=0)
        if len(possible_actions) == 0:
            return ()
        # print("I have {} possible actions".format(len(possible_actions)))
        expected_value = list()
        for action in possible_actions:
            result_state = deepcopy(state)
            for atomic_action in action:
                result_state = Agent.perform_action(result_state,atomic_action)
            result_state = Agent.progress_state(result_state)
            expected_value.append(self.min_value(result_state,depth=1))
        best_action_index = expected_value.index(max(expected_value, default=0))
        return possible_actions[best_action_index]

    def max_value(self,state,depth):
        if Agent.test_terminal_state(state) or depth == Agent.max_minimax_depth:
            return Agent.evaluate_state(state, self.zoc)
        possible_actions = Agent.actions(state,self.zoc)
        expected_value = list()
        for action in possible_actions:
            result_state = deepcopy(state)
            for atomic_action in action:
                result_state = Agent.perform_action(result_state,atomic_action)
            result_state = Agent.progress_state(result_state)
            expected_value.append(self.min_value(result_state,depth+1))
        return max(expected_value, default=0)

    def min_value(self,state,depth):
        if Agent.test_terminal_state(state) or depth == Agent.max_minimax_depth:
            return Agent.evaluate_state(state, self.non_zoc)
        possible_actions = Agent.actions(state,self.non_zoc)
        expected_value = list()
        for action in possible_actions:
            result_state = deepcopy(state)
            for atomic_action in action:
                result_state = Agent.perform_action(result_state,atomic_action)
            result_state = Agent.progress_state(result_state)
            expected_value.append(self.max_value(result_state,depth+1))
        # we evaluate the state's value by replacing the ZOC
        # therefore the opponent wants to maximize it
        return max(expected_value, default=0)
# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         print(initial_state)
#
#     def act(self, state):
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action

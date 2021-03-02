from copy import deepcopy
from itertools import chain, combinations
import time
import math
import random

DIMENSIONS = (10, 10)
ids = ['205460686']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_map = initial_state
        self.zoc = zone_of_control
        self.zoc2 = self.find_zoc2()
        self.order = order
        self.previously_s = {}
        self.previously_q = {}
        self.first_action = True
        pass

    def find_zoc2(self):
        zoc2 = []
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                if (i, j) not in self.zoc and self.initial_map[i][j] != 'U':
                    zoc2.append((i, j))
        return zoc2

    def update_previously_status(self, state):
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                for status, previously_dict in zip(['S', 'Q'], (self.previously_s, self.previously_q)):
                    if (i, j) in previously_dict.keys():
                        if status in state[i][j]:
                            previously_dict[(i, j)] += 1
                        else:
                            del previously_dict[(i, j)]
                    else:
                        if status in state[i][j]:
                            previously_dict[(i, j)] = 1

    def act(self, state):
        self.update_previously_status(state)
        initial_state = State(state, self.zoc, 1, self.zoc2, self.previously_s, self.previously_q)
        # if not any('S' in sublist for sublist in state):
        #     return tuple()
        s_count = 0
        for location in self.zoc:
            if 'S' in initial_state.map[location]:
                s_count += 1
        if s_count < 1:
            return initial_state.get_player_action(self.zoc, self.zoc2)
        searcher = mcts(timeLimit=4850, rolloutPolicy=simulation_policy)
        bestAction = searcher.search(initialState=initial_state)
        if bestAction is None:
            print('best action is None')
            return initial_state.get_player_action(self.zoc, self.zoc2)
        if bestAction == (('empty', ), ):
            return tuple()
        else:
            return bestAction

class State():

    def __init__(self, game_map, zoc, currentPlayer, zoc2, previously_s, previously_q):
        self.map = self.pad_the_input(deepcopy(game_map), previously_s, previously_q)
        self.zoc = zoc
        self.zoc2 = zoc2
        self.currentPlayer = currentPlayer
        self.medics = 1
        self.police = 2
        self.score = [0, 0]

    def getCurrentPlayer(self):
        """Returns 1 if it is the maximizer player's turn to choose an action, or -1 for the minimiser player"""
        return self.currentPlayer

    @staticmethod
    def power_of_k_elements(k, iterable):
        return list(chain.from_iterable(combinations(iterable, i) for i in [k])) + list(tuple())

    def change_state(self):
        new_map = deepcopy(self.map)

        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if self.map[(i, j)] == 'H' and ('S' in self.map[(i - 1, j)] or
                                                  'S' in self.map[(i + 1, j)] or
                                                  'S' in self.map[(i, j - 1)] or
                                                  'S' in self.map[(i, j + 1)]):
                    new_map[(i, j)] = 'S1'

        # advancing sick counters
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if 'S' in self.map[(i, j)]:
                    turn = int(self.map[(i, j)][1])
                    if turn < 3:
                        new_map[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_map[(i, j)] = 'H'

                # advancing quarantine counters
                if 'Q' in self.map[(i, j)]:
                    turn = int(self.map[(i, j)][1])
                    if turn < 2:
                        new_map[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_map[(i, j)] = 'H'

        self.map = new_map

    @staticmethod
    def pad_the_input(a_map, previously_s, previously_q):
        state = {}
        new_i_dim = DIMENSIONS[0] + 2
        new_j_dim = DIMENSIONS[1] + 2
        for i in range(0, new_i_dim):
            for j in range(0, new_j_dim):
                if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                    state[(i, j)] = 'U'
                elif 'S' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'S' + str(previously_s[(i-1, j-1)])
                elif 'Q' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'Q' + str(previously_q[(i-1, j-1)])
                else:
                    state[(i, j)] = a_map[i - 1][j - 1]
        return state

    def getPossibleActions(self):
        # This currently does not include quarantine to only one place
        """Returns an iterable of all actions which can be taken from this state"""
        healthy, sick = set(), set()
        for (i, j) in self.zoc:
            i, j = i+1, j+1
            if 'H' in self.map[(i, j)]:
                healthy.add((i-1, j-1))
            if 'S' in self.map[(i, j)]:
                sick.add((i-1, j-1))
        basic_vaccinate_actions = tuple(("vaccinate", index) for index in healthy)
        basic_quarantine_actions = tuple(("quarantine", index) for index in sick)
        medics_actions = self.power_of_k_elements(min(self.medics, len(healthy)), basic_vaccinate_actions)
        police_actions = self.power_of_k_elements(min(1, len(sick)), basic_quarantine_actions)
        all_actions = []
        for medic_action in medics_actions:
            all_actions.append(medic_action)

        if len(police_actions) > 0:
            for medic_action in medics_actions:
                for police_action in police_actions:
                    all_actions.append(medic_action + police_action)

        # for police_action in police_actions:
        #     all_actions.append(police_action)

        all_actions.append((('empty', ), ))

        return all_actions

    def takeAction(self, action1):
        """Returns the state which results from taking action action"""
        result_state = deepcopy(self)
        action2 = self.get_player_action(self.zoc2, self.zoc)
        actions = [action2]
        if action1 != (('empty',), ):
            actions.append(action1)
        for action in actions:
            for atomic_action in action:
                effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                if 'v' in effect:
                    result_state.map[location] = 'I'
                else:
                    result_state.map[location] = 'Q0'
        result_state.change_state()
        result_state.update_scores()
        return result_state

    def process_state(self, player_zoc, other_player_zoc):
        healthy = []
        sick = []
        healthy2 = []
        for (i, j) in player_zoc:
            i, j = i+1, j+1
            if 'H' in self.map[(i, j)]:
                healthy.append((i, j))
            if 'S' in self.map[(i, j)]:
                sick.append((i, j))
        #
        # for (i, j) in other_player_zoc:
        #     i, j = i+1, j+1
        #     if 'H' in self.map[(i, j)]:
        #         healthy2.append((i, j))
        return healthy, sick, healthy2

    def sick_heuristic(self, healthy, coordinate, player_zoc, other_player_zoc):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))

        h = sum(1 for neighbor in neighbors if (neighbor in healthy and (neighbor[0]-1, neighbor[1]-1) in player_zoc))
        # b = sum(1 for neighbor in neighbors if (neighbor in healthy2 and (neighbor[0]-1, neighbor[1]-1) in other_player_zoc))
        return h

    def helthy_heuristic(self, sick, coordinate, player_zoc, other_player_zoc):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        for neighbor in neighbors:
            if neighbor in sick:
                return 1
        return 0

    def get_player_action(self, player_zoc, other_player_zoc):
        """returns actions indexes in not padded map"""
        action = []
        healthy, sick, healthy2 = self.process_state(player_zoc, other_player_zoc)
        sick.sort(key=lambda x: self.sick_heuristic(healthy,  x, player_zoc, other_player_zoc), reverse=True)
        healthy.sort(key=lambda x: self.sick_heuristic(healthy,  x, player_zoc, other_player_zoc), reverse=True)
        to_quarantine = []
        if len(sick) > 0:
            if self.sick_heuristic(healthy,  sick[0], player_zoc, other_player_zoc) > 1:
                to_quarantine = (sick[:1])
        try:
            to_vaccinate = (healthy[:1])
        except ValueError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', (item[0]-1, item[1]-1)))
        for item in to_vaccinate:
            action.append(('vaccinate', (item[0]-1, item[1]-1)))
        return action

    def isTerminal(self):
        """Returns True if this state is a terminal state"""
        there_is_s = ('S1' in self.map.values() or 'S2' in self.map.values() or 'S3' in self.map.values())
        return not there_is_s

    def update_scores(self):
        control_zone = self.zoc
        for i in range(1, DIMENSIONS[0]+1):
            for j in range(1, DIMENSIONS[1]+1):
                player = 1
                if (i-1, j-1) in control_zone:
                    player = 0
                if 'H' in self.map[(i, j)]:
                    self.score[player] += 1
                if 'I' in self.map[(i, j)]:
                    self.score[player] += 1
                if 'S' in self.map[(i, j)]:
                    self.score[player] -= 1
                if 'Q' in self.map[(i, j)]:
                    self.score[player] -= 5

    def getReward(self):
        """Returns the reward for this state. Only needed for terminal states."""
        score = self.score
        return score[0] - score[1]




def simulation_policy(state):
    i = 1
    while not state.isTerminal():
        try:
            action = state.get_player_action(state.zoc, state.zoc2)
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
        i += 1
        if i == 4:
            break
    return state.getReward()


def randomPolicy(state):
    i = 1
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
        i += 1
        if i == 10:
            break
    return state.getReward()

class treeNode():
    def __init__(self, state, parent):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        self.totalReward = 0
        self.children = {}



class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState, needDetails=False):
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        bestChild = self.getBestChild(self.root, 0)
        if bestChild is None:
            return
        action = (action for action, node in self.root.children.items() if node is bestChild).__next__()
        if needDetails:
            return {"action": action, "expectedReward": bestChild.totalReward / bestChild.numVisits}
        else:
            # print("action:", action, "expectedReward:", bestChild.totalReward / bestChild.numVisits)
            return action

    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        for action in actions:
            if action not in node.children:
                newNode = treeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        return node

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = node.state.getCurrentPlayer() * child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        if len(bestNodes) != 0:
            return random.choice(bestNodes)

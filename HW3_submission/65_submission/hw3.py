import random
from copy import deepcopy
from itertools import product
import main
import utils

ids = ['311281190', '203371034']


def combinations(arr, tuple_len, prev_arr=None):
    if prev_arr is None:
        prev_arr = []
    if len(prev_arr) == tuple_len:
        return [prev_arr]
    allCombinations = []
    for i, val in enumerate(arr):
        prev_array_extended = prev_arr.copy()
        prev_array_extended.append(val)
        allCombinations += combinations(arr[i + 1:], tuple_len, prev_array_extended)
    return allCombinations


def all_actions(state, zoc):
    vaccinateList = []
    quarantineList = []
    allVaccinateList = []
    allQuarantineList = []
    rowsNum = 9
    colsNum = 9

    for coordinates in zoc:
        row = coordinates[0]
        col = coordinates[1]
        value = state[coordinates]
        if value[0] == 'H':
            allVaccinateList.append(("vaccinate", coordinates))
            if row - 1 >= 0:
                if 'S' in state[(row - 1, col)]:
                    vaccinateList.append(("vaccinate", coordinates))
                    continue
            if row + 1 <= rowsNum - 1:
                if 'S' in state[(row + 1, col)]:
                    vaccinateList.append(("vaccinate", coordinates))
                    continue
            if col - 1 >= 0:
                if 'S' in state[(row, col - 1)]:
                    vaccinateList.append(("vaccinate", coordinates))
                    continue
            if col + 1 <= colsNum - 1:
                if 'S' in state[(row, col + 1)]:
                    vaccinateList.append(("vaccinate", coordinates))
                    continue
        elif value[0] == 'S':
            allQuarantineList.append(("quarantine", coordinates))
            hCount = 0
            if row - 1 >= 0:
                if 'H' in state[(row - 1, col)]:
                    hCount += 1
            if row + 1 <= rowsNum - 1:
                if 'H' in state[(row + 1, col)]:
                    hCount += 1
            if col - 1 >= 0:
                if 'H' in state[(row, col - 1)]:
                    hCount += 1
            if col + 1 <= colsNum - 1:
                if 'H' in state[(row, col + 1)]:
                    hCount += 1
            if hCount >= 3:
                quarantineList.append(("quarantine", coordinates))

    allCombinations = []

    if not vaccinateList:
        if allVaccinateList:
            if len(allVaccinateList) > 5:
                vaccinateList = random.sample(allVaccinateList, 5)

    if not vaccinateList and not quarantineList:
        return []
    elif not vaccinateList:
        for quarantine in allQuarantineList:
            allCombinations.append([quarantine])
        return allCombinations
    elif not quarantineList:
        for vaccinate in vaccinateList:
            allCombinations.append([vaccinate])
        return allCombinations

    for vaccinate in vaccinateList:
        allCombinations.append([vaccinate])

    listOne = [i for i in product(vaccinateList, quarantineList)]
    allCombinations.extend(listOne)

    listTwoTemp = [i for i in combinations(quarantineList, 2)]
    listTwo = [i for i in product(vaccinateList, listTwoTemp)]
    listTwo = [(i[0], i[1][0], i[1][1]) for i in listTwo]

    allCombinations.extend(listTwo)

    allCombinations = [list(i) for i in allCombinations]
    return allCombinations


def apply_actions(state, actions):
    new_state = deepcopy(state)
    for atomic_action in actions:
        effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
        row = location[0]
        col = location[1]
        if 'v' in effect:
            new_state[(row, col)] = ('I', 0)
        else:
            new_state[(row, col)] = ('Q', None)
    return new_state


def change_state(state):
    S_coordinates = []
    Q_coordinates = []
    H_coordinates = []
    new_dict = {}
    rows = 9
    columns = 9
    Q_coordinatesNew = []
    for coordinates, value in state.items():
        new_dict[coordinates] = value
        if 'H' in value:
            H_coordinates = H_coordinates + [coordinates]
        if 'S' in value:
            S_coordinates = S_coordinates + [coordinates]
        if 'Q' in value:
            Q_coordinates = Q_coordinates + [coordinates]

    for coordinates, value in state.items():
        if value == ('Q', None):
            new_dict[coordinates] = ('Q', 0)
            Q_coordinatesNew = Q_coordinatesNew + [coordinates]

    list1 = list()
    for i in S_coordinates:
        if int(i[0] + 1) < rows and (int(i[0] + 1), i[1]) in H_coordinates:
            list1 = list1 + [(int(i[0] + 1), i[1])]
        if int(i[0]) != 0 and (int(i[0] - 1), i[1]) in H_coordinates:
            list1 = list1 + [(int(i[0] - 1), i[1])]
        if int(i[1] + 1) < columns and (i[0], int(i[1] + 1)) in H_coordinates:
            list1 = list1 + [(i[0], int(i[1] + 1))]
        if int(i[1]) != 0 and (i[0], int(i[1] - 1)) in H_coordinates:
            list1 = list1 + [(i[0], int(i[1] - 1))]
    for a in list1:
        new_dict[a] = ('S', 0)
        if a in H_coordinates:
            H_coordinates.remove(a)
            S_coordinates.append(a)
    for j in list(S_coordinates):
        if j not in list1:
            temp = int(new_dict[j][1])
            if int(temp + 1) >= 3:
                new_dict[j] = ('H', 0)
                H_coordinates.append(j)
                S_coordinates.remove(j)
            else:
                new_dict[j] = ('S', int(temp + 1))
    for p in Q_coordinates:
        if p not in Q_coordinatesNew:
            temp = int(new_dict[p][1])
            if int(temp + 1) >= 2:
                new_dict[p] = ('H', 0)
                H_coordinates.append(p)
                Q_coordinates.remove(p)
            else:
                new_dict[p] = ('Q', int(temp + 1))
    return utils.hashabledict(new_dict)


def allPossibleChildrenFromState(state, zoc):
    allPossibleChildStatesList = {}

    allActions = all_actions(state, zoc)
    for actions in allActions:
        stateAfterActions = apply_actions(state, actions)
        allPossibleChildStatesList[tuple(actions)] = stateAfterActions
    return allPossibleChildStatesList


def eval_state(state, zoc):
    myPoints = 0
    rivalPoints = 0

    for pos, value in state.items():
        if 'I' in value or 'H' in value:
            if pos in zoc:
                myPoints = myPoints + 1
            else:
                rivalPoints = rivalPoints + 1
        elif 'S' in value:
            if pos in zoc:
                myPoints = myPoints - 1
            else:
                rivalPoints = rivalPoints - 1
        elif 'Q' in value:
            if pos in zoc:
                myPoints = myPoints - 5
            else:
                rivalPoints = rivalPoints - 5
    return myPoints - rivalPoints


def miniMax(state, zoc, notZoc, order, depth, alpha, beta, maximizingPlayer, action_org):
    posInfinity = float('inf')
    negInfinity = float('-inf')
    best_child = state
    best_action = action_org
    if depth == 0:
        return eval_state(state, zoc), state, action_org

    if maximizingPlayer and order == 'first':
        maxEval = negInfinity
        allMaxPlayerChildren = allPossibleChildrenFromState(state, zoc)
        best_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval, allMaxPlayerChildren, action_org
        for actions, child in allMaxPlayerChildren.items():
            grandChildVal, grandChild, grandChildAction = miniMax(child, zoc, notZoc, order,
                                                                  depth - 1, alpha, beta, False, actions)
            if maxEval > grandChildVal:
                best_val, best_child, best_action = maxEval, child, actions
            else:
                best_val, best_child, best_action = grandChildVal, grandChild, grandChildAction

            alpha = max(alpha, grandChildVal)
            if beta <= alpha:
                break
        return best_val, best_child, best_action

    elif maximizingPlayer and order == 'second':
        maxEval = negInfinity
        allMaxPlayerChildren = allPossibleChildrenFromState(state, zoc)
        best_val = maxEval
        if not allMaxPlayerChildren:
            return maxEval, allMaxPlayerChildren, action_org
        for actions, child in allMaxPlayerChildren.items():
            childAfterChange = change_state(child)
            grandChildVal, grandChild, grandChildAction = miniMax(childAfterChange, zoc, notZoc, order, depth - 1,
                                                                  alpha, beta, False, actions)
            if maxEval > grandChildVal:
                best_val, best_child, best_action = maxEval, childAfterChange, actions
            else:
                best_val, best_child, best_action = grandChildVal, grandChild, grandChildAction
            alpha = max(alpha, grandChildVal)
            if beta <= alpha:
                break
        return best_val, best_child, best_action

    elif not maximizingPlayer and order == 'second':  # rival is first
        minEval = posInfinity
        allMinPlayerChildren = allPossibleChildrenFromState(state, notZoc)
        best_val = minEval
        if not allMinPlayerChildren:
            return minEval, allMinPlayerChildren, action_org
        for actions, child in allMinPlayerChildren.items():
            grandChildVal, grandChild, grandChildAction = miniMax(child, zoc, notZoc, order,
                                                                  depth - 1, alpha, beta, True, actions)
            if minEval < grandChildVal:
                best_val, best_child, best_action = minEval, child, actions
            else:
                best_val, best_child, best_action = grandChildVal, grandChild, grandChildAction

            beta = min(beta, grandChildVal)
            if beta <= alpha:
                break
        return best_val, best_child, action_org

    elif not maximizingPlayer and order == 'first':  # rival is second
        minEval = posInfinity
        allMinPlayerChildren = allPossibleChildrenFromState(state, notZoc)
        best_val = minEval
        if not allMinPlayerChildren:
            return minEval, allMinPlayerChildren, action_org
        for actions, child in allMinPlayerChildren.items():
            childAfterChange = change_state(child)
            grandChildVal, grandChild, grandChildAction = miniMax(childAfterChange, zoc, notZoc, order,
                                                                  depth - 1, alpha, beta, True, actions)
            if minEval < grandChildVal:
                best_val, best_child, best_action = minEval, child, actions
            else:
                best_val, best_child, best_action = grandChildVal, grandChild, grandChildAction

            beta = min(beta, grandChildVal)
            if beta <= alpha:
                break
        return best_val, best_child, action_org


def list_to_dict(state):
    new_dict = {}
    for i in range(len(state)):
        for j in range(len(state[0])):
            new_dict[(i, j)] = (state[i][j], 0)
    return new_dict


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        self.zoc = zone_of_control
        self.notZoc = []
        self.initialState = initial_state
        self.prev_state = {}
        self.state_dict = {}
        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                self.state_dict[(i, j)] = (initial_state[i][j], 0)
                if (i, j) not in self.zoc:
                    self.notZoc.append((i, j))

        self.initialStateAsPaddedDict = main.pad_the_input(initial_state)

        posInfinity = float('inf')
        negInfinity = float('-inf')
        if self.order == 'first':
            self.evalMax, self.nextState, self.nextAction = miniMax(self.state_dict, self.zoc, self.notZoc, self.order,
                                                                    2, negInfinity, posInfinity, True, [])

    def act(self, state):
        state_dict = list_to_dict(state).copy()

        if self.prev_state:
            for pos, value in state_dict.items():
                if 'S' in value:
                    if 'S' in self.prev_state[pos]:
                        state_dict[pos] = ('S', self.prev_state[pos][1] + 1)
                elif 'Q' in value:
                    if 'Q' in self.prev_state[pos]:
                        state_dict[pos] = ('Q', self.prev_state[pos][1] + 1)
        self.prev_state = state_dict

        posInfinity = float('inf')
        negInfinity = float('-inf')

        if state_dict == self.state_dict and self.order == 'first':
            return self.nextAction

        else:
            if self.order == 'second':
                evalMax, nextState, nextAction = miniMax(state_dict, self.zoc, self.notZoc, self.order, 2, negInfinity,
                                                         posInfinity, True, [])
            else:
                evalMax, nextState, nextAction = miniMax(state_dict, self.zoc, self.notZoc, self.order, 2, negInfinity,
                                                         posInfinity, True, [])

        return nextAction

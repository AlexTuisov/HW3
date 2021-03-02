import random
from enum import Enum
import copy
import itertools
from itertools import product


ids = ['204411730', '204241202']


def goal_test(state):
    state = state.board
    for i in range(10):
        for j in range(10):
            if state[i][j] == 'S1' or state[i][j] == 'S2' or state[i][j] == 'S3' or state[i][j] == 'S':
                return False
    return True


def possible_actions(state, isAgentTurn=True):
    board = state.board
    if isAgentTurn is True:
        zoc = state.zoc
    else:
        zoc = state.opponents_zoc
    medics = 1
    police = 2
    can_be_vaccinated = []
    can_be_quarantined = []
    for t_cor in zoc: #cordinate
        cor = t_cor[0] , t_cor[1]
        #cor = t_cor[0] - 1, t_cor[1] - 1
        if board[cor[0]][cor[1]] == 'H':
            can_be_vaccinated.append(("vaccinate", cor))
        #elif board[cor[0]][cor[1]] == 'S' or board[cor[0]][cor[1]] == 'S1' or board[cor[0]][cor[1]] == 'S2' or board[cor[0]][cor[1]] == 'S3':
        #    can_be_quarantined.append(("quarantine", cor))
    t_vaccinated = []
    for i in range(medics + 1):
        t_vaccinated += itertools.combinations(can_be_vaccinated, i)
    t_quarantined = []
    t_quarantined.append(())
    #for i in range(police + 1):
    #    t_quarantined += itertools.combinations(can_be_quarantined, i)
    actions_list = list(product(t_quarantined, t_vaccinated))
    actions_list = tuple(actions_list)
    return actions_list


def apply_action(board, actions):
    # map = state['map']
    map = board
    #for i in range(len(map)):
    #    map[i] = list(map[i])

    for item in actions:
        if item == ():
            continue
        item = item[0]  # cause of annoying comma!!
        st = map[item[1][0]][item[1][1]]
        if item[0] == "vaccinate":
            if st == "H":
                map[item[1][0]][item[1][1]] = "I"
        elif item[0] == "quarantine":
            if st == "S1" or st == "S2" or st == "S3":
                map[item[1][0]][item[1][1]] = "Q1"
    return map

def check_valid_boundaries(row, col):
    if col < 0 or col >= 10 or row < 0 or row >= 10:
        return False
    return True

def change_state(board):
    map = board
    for i in range(10):
        for j in range(10):
            if map[i][j] == 'H':
                row = i
                col = j - 1
                if check_valid_boundaries(row, col):
                    if map[row][col] == 'S1' or map[row][col] == 'S2' or map[row][col] == 'S3':
                        map[row][col] = 'T'

                row = i
                col = j + 1
                if check_valid_boundaries(row, col):
                    if map[row][col] == 'S1' or map[row][col] == 'S2' or map[row][col] == 'S3':
                        map[row][col] = 'T'

                row = i + 1
                col = j
                if check_valid_boundaries(row, col):
                    if map[row][col] == 'S1' or map[row][col] == 'S2' or map[row][col] == 'S3':
                        map[row][col] = 'T'

                row = i - 1
                col = j
                if check_valid_boundaries(row, col):
                    if map[row][col] == 'S1' or map[row][col] == 'S2' or map[row][col] == 'S3':
                        map[row][col] = 'T'
            elif map[i][j] == 'S1':
                map[i][j] = 'S2'
            elif map[i][j] == 'S2':
                map[i][j] = 'S3'
            elif map[i][j] == 'S3':
                map[i][j] = 'H'
            elif map[i][j] == 'Q1':
                map[i][j] = 'Q2'
            elif map[i][j] == 'Q2':
                map[i][j] = 'H'

    for i in range(10):
        for j in range(10):
            if map[i][j] == 'T':
                map[i][j] = 'S1'
    return map


#TODO: Which player zoc to use
def heuristic(state):
    h_val = 0
    H_num = 0
    I_num = 0
    S_num = 0
    Q_num = 0
    O_H_num = 0
    O_I_num = 0
    O_S_num = 0
    O_Q_num = 0
    zoc = state.zoc
    opponents_zoc = state.opponents_zoc
    board = state.board

    for (i, j) in zoc:
        #a = i - 1
        #b = j - 1
        a = i
        b = j
        if board[a][b] == 'H':
            H_num += 1
        elif board[a][b] == 'I':
            I_num += 1
        elif board[a][b] == 'S' or board[a][b] == 'S1' or board[a][b] == 'S2' or board[a][b] == 'S3':
            S_num += 1      #TODO: check if Q0
        elif board[a][b] == 'Q0' or board[a][b] == 'Q1' or board[a][b] == 'Q2':
            Q_num += 1

    for (i, j) in opponents_zoc:
        #a = i - 1
        #b = j - 1
        a = i
        b = j
        if board[a][b] == 'H':
            O_H_num += 1
        elif board[a][b] == 'I':
            O_I_num += 1
        elif board[a][b] == 'S' or board[a][b] == 'S1' or board[a][b] == 'S2' or board[a][b] == 'S3':
            O_S_num += 1      #TODO: check if Q0
        elif board[a][b] == 'Q0' or board[a][b] == 'Q1' or board[a][b] == 'Q2':
            O_Q_num += 1

    Mine =  H_num*2 + I_num*10+ S_num*-1 + Q_num*-5
    Opponents = O_H_num*3 + O_I_num*20+ O_S_num*-1 + O_Q_num*-5
    h_val = 1.2*Mine - Opponents
    return h_val

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.board = initial_state
        self.order = order
        # calculate opponents zoc
        all_tiles = []
        for i in range(10):
            for j in range(10):
                all_tiles.append((i,j))
        #all_tiles = [(i, j) for i, j in
        #            itertools.product(range(0, 10),
        #                               range(0, 10))]  # if 'U' not in self.board[i - 1][j - 1]]
        self.opponents_zoc = []
        for cor in all_tiles:
            if cor not in self.zoc:
                if self.board[cor[0]][cor[1]] != 'U':
                    self.opponents_zoc.append(cor)

    class Turn(Enum):
        AGENT_TURN = 'AGENT_TURN'
        OPPONENTS_TURN = 'OPPONENTS_TURN'

    class TurnState:
        def __init__(self, board, zoc, opponents_zoc, action):
            self.board = board  #grid/state/MASHEU
            self.zoc = zoc
            self.action = action
            self.opponents_zoc = opponents_zoc

        @property
        def turn(self):
            return Agent.Turn.AGENT_TURN if self.action is None else Agent.Turn.OPPONENTS_TURN


    def AlphaBeta_MiniMax(self, state, D, alpha, beta):
        if D == 0 :#or goal_test(state) is True:
            return (heuristic(state), state.action)

        if state.turn == Agent.Turn.AGENT_TURN:
            possible_actions_l = possible_actions(state, isAgentTurn=True)
            CurMax = (-float("inf"), possible_actions_l[0])
            for action in possible_actions_l:
                state.action = action
                value = self.AlphaBeta_MiniMax(state, D, alpha, beta)
                if value[0] > CurMax[0]:
                    CurMax = (value[0], action)
                alpha = max(CurMax[0], alpha)
                if CurMax[0] >= beta:
                    return (float("inf"), action)
            return CurMax
        else:
            CurMin = (float("inf"), state.action)
            for opponents_action in possible_actions(state, isAgentTurn=False):
                temp_board = copy.deepcopy(state.board)
                temp_board = apply_action(temp_board, opponents_action)
                temp_board = apply_action(temp_board, state.action)
                temp_board = change_state(temp_board)
                value = self.AlphaBeta_MiniMax(Agent.TurnState(temp_board, state.zoc, state.opponents_zoc, None), D - 1, alpha, beta)
                if value[0] < CurMin[0]:
                    CurMin = (value[0], state.action)
                beta = min(CurMin[0], beta)
                if CurMin[0] <= alpha :
                    return (-float("inf"), state.action)
            return CurMin

    def act(self, state):
        D, alpha, beta = 2, -float("inf"), float("inf")
        #self.board = change_state(self.board)
        t_res = Agent.AlphaBeta_MiniMax(self, Agent.TurnState(state, self.zoc, self.opponents_zoc, None), D, alpha, beta)
        res = format_corrector(t_res[1])
        #self.board = apply_action(self.board, t_res[1])
        return res

def format_corrector(actions):
    action_list = []
    healthy = set()
    for action in actions:
        if len(action) == 0:
            continue
        action = action[0]
        (i, j) = action[1][0], action[1][1]
        #(i, j) = action[1][0] + 1, action[1][1] + 1
        if action[0] == 'quarantine':
            action_list.append(('quarantine', (i, j)))
        elif action[0] == 'vaccinate':
            action_list.append(('vaccinate', (i, j)))
    return action_list



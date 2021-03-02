import itertools
import random
from copy import deepcopy
import time
ids = ['336481148', '314625039']

CONSTRUCTOR_TIMEOUT = 60
ACTION_TIMEOUT = 5
DIMENSIONS = (10, 10)
PENALTY = 1000


def pad_the_input(a_map):
    state = {}
    new_i_dim = 12
    new_j_dim = 12
    for i in range(0, new_i_dim):
        for j in range(0, new_j_dim):
            if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                state[(i, j)] = 'U'
            elif 'S' in a_map[i - 1][j - 1]:
                state[(i, j)] = 'S1'
            else:
                state[(i, j)] = a_map[i - 1][j - 1]

    return state

class Agent():
    def __init__(self, initial_state, zone_of_control,order):
        self.initial_state = pad_the_input(initial_state)
        self.state = deepcopy(self.initial_state)
        self.order = order
        self.zoc = zone_of_control
        self.zoc2 = []
        for i in range(10):
            for j in range(10):
                if (i, j) not in self.zoc and 'U' not in self.initial_state[(i,j)]:
                    self.zoc2.append((i, j))
        self.police = 2
        self.medics = 1
        self.height = len(initial_state)
        self.width = len(initial_state[0])
        self.actionmax = 2
        self.day_count = 0
        self.allowed_time = 5
        self.start_time = 5
        self.my_first_move = self.minimaxRoot(5, self.initial_state, True, 10)
        self.flag_of_time = False

    def choose_meds_police(self, nm, np, h_set, s_set):
        '''
        Given Number of Medics avaliable (nm) and of Police(np) the:
        '''
        medics_combs = set(itertools.combinations(h_set, nm))
        police_combs = set(itertools.combinations(s_set, np))
        med_pol_coords = set(itertools.product(medics_combs, police_combs))
        result = list(
            map(lambda comb: tuple(map(lambda mt: ("vaccinate", mt), comb[0])) + tuple(
                map(lambda pt: ("quarantine", pt), comb[1])),
                med_pol_coords))
        return result

    def give_sick_healthy(self, state, who):
        S_list = []
        H_list = []
        if who == 'zoc':
            for (i,j) in self.zoc:
                if 'H' in state[(i+1, j+1)]:
                    H_list.append((i, j))
                elif 'S' in state[(i+1, j+1)]:
                    S_list.append((i, j))
        elif who == 'zoc2':
            for (i, j) in self.zoc2:
                if 'H' in state[(i+1, j+1)]:
                    H_list.append((i, j))
                elif 'S' in state[(i+1, j+1)]:
                    S_list.append((i, j))
        return (S_list, H_list)


    def has_sick_neighbors(self,state_lst,row,col):
        has_sick = False
        if state_lst[(row,col)] == 'H' and ('S' in state_lst[(row - 1,col)] or
                                       'S' in state_lst[(row + 1,col)] or
                                       'S' in state_lst[(row,col - 1)] or
                                       'S' in state_lst[(row,col + 1)]):
            has_sick = True
        return has_sick
    
    def h_S(self,who,S_list):        #gets S_list with real coords
        Max_h=0
       
        S_max_list=[]
        if who:
                zocality=self.zoc
        else :
                zocality=self.zoc2
        for i in range(len(S_list)):
            h=0
            coord=S_list[i]
            coord=(coord[0]+1,coord[1]+1)
            if (coord[0]-1,coord[1]) in zocality and 'H' in self.state[(coord[0]-1,coord[1])]:#above
                h+=1
            if (coord[0],coord[1]-1) in zocality and 'H' in self.state[(coord[0]-1,coord[1])]:#left
                h+=1
            if (coord[0]+1,coord[1]) in zocality and 'H' in self.state[(coord[0]-1,coord[1])]:#below
                h+=1
            if (coord[0],coord[1]+1) in zocality and 'H' in self.state[(coord[0]-1,coord[1])]:#right
                h+=1
            coord=(coord[0]-1,coord[1]-1)#not sure , depends on how state looks
            S_list[i]=(coord,h)
            if h > Max_h:
                Max_h = h
                
        for i in range(len(S_list)):
            if S_list[i][1] == Max_h:
                S_max_list.append(S_list[i][0])
        return S_max_list

    def h_H(self,H_list):
        Max_h=0
        H_max_list=[]
        for i in range(len(H_list)):
            h=0
            coord=H_list[i]
            coord=(coord[0]+1,coord[1]+1)
            if 'S' in self.state[(coord[0]-1,coord[1])]:#above
                h+=1
            if 'S' in self.state[(coord[0]-1,coord[1])]:#left
                h+=1
            if 'S' in self.state[(coord[0]-1,coord[1])]:#below
                h+=1
            if 'S' in self.state[(coord[0]-1,coord[1])]:#right
                h+=1
            coord=(coord[0]-1,coord[1]-1)#not sure , depends on how state looks
            H_list[i]=(coord,h)
            if h > Max_h:
                Max_h = h
        for i in range(len(H_list)):
            if H_list[i][1] == Max_h:
                H_max_list.append(H_list[i][0])
        return H_max_list
        

        
                



    def actions(self, state, who):  # stopped here
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        def meds_police_shuffle(mp_pairs, h_list, s_list):
            return [mp_comb for (nm, np) in mp_pairs for mp_comb in self.choose_meds_police(nm, np, h_list, s_list)]

        (S_list, H_list) = self.give_sick_healthy(state, who)
        H_risk_list = list(filter(lambda coord: self.has_sick_neighbors(state, coord[0]+1, coord[1]+1), H_list))
        H_max_list = self.h_H(H_risk_list)
        S_max_list = self.h_S(who,S_list)
        max_p = min(len(S_max_list), self.police)
        max_m = min(len(H_max_list), self.medics)
        mp_combinations=[]#added
        if max_p == 2 :
            mp_combinations.append((max_m,max_p))
            mp_combinations.append((max_m,max_p-1))
            mp_combinations.append((max_m,0))
        elif max_p == 1 :
            mp_combinations.append((max_m,max_p))
            mp_combinations.append((max_m,0))
        else:
            mp_combinations.append((max_m,0))
    
        #mp_combinations = [(max_m, max_p)]
        final_actions=meds_police_shuffle(mp_combinations, H_max_list, S_max_list)
        #print(len(final_actions),"amount of possible actions")
        return final_actions


    def apply_actions_for_mm(self,actions,state):
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
            if 'v' in effect:
                state[location] = 'I'
            else:
                state[location] = 'Q0'
        return state


    def change_states(self,state):
        new_state = deepcopy(state)
        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                                  'S' in state[(i + 1, j)] or
                                                  'S' in state[(i, j - 1)] or
                                                  'S' in state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'
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

        return new_state

    def minimaxRoot(self, depth, state, is_maximizing, thinking_time = 4.9):
        self.flag_of_time = True
        self.start_time = time.time()
        self.allowed_time = thinking_time
        state_mm = deepcopy(state)
        possibleMoves = self.actions(state_mm,'zoc')
        bestMove = -99999
        bestMoveFinal = None
        for x in possibleMoves:
            if not self.flag_of_time:
                break
            move = x
            next_state = self.apply_actions_for_mm(x, state_mm)
            value = max(bestMove, self.minimax(depth - 1, next_state, -10000, 10000, not is_maximizing))
            if (value > bestMove):
                #print("Best score: ", str(bestMove))
                #print("Best move: ", str(bestMoveFinal))
                bestMove = value
                bestMoveFinal = move
        self.flag_of_time = True
        return bestMoveFinal


    def minimax(self, depth, state, alpha, beta, is_maximizing):
        if (depth == 0):
            if self.time_over():
                self.flag_of_time = False
            return -self.update_scores(state, is_maximizing)
        if is_maximizing:
            possibleMoves = self.actions(state, 'zoc2')
            best_move = -99999
            for x in possibleMoves:
                if not self.flag_of_time:
                    break
                move = x
                next_state = self.apply_actions_for_mm(move, state)
                next_day = self.change_states(next_state)
                best_move = max(best_move, self.minimax(depth - 1, next_day, alpha, beta, not is_maximizing))
                alpha = max(alpha, best_move)
                if beta <= alpha:
                    return best_move
            return best_move
        else:
            possibleMoves = self.actions(state, 'zoc2')
            best_move = 99999
            for x in possibleMoves:
                if not self.flag_of_time:
                    break
                move = x
                next_state = self.apply_actions_for_mm(move, state)
                next_day = self.change_states(next_state)
                best_move = min(best_move, self.minimax(depth - 1, next_day, alpha, beta, not is_maximizing))
                beta = min(beta, best_move)
                if beta <= alpha:
                    return best_move
            return best_move

    def update_scores(self, state_art, who):
        count = 0
        zocality = []
        scores1 = {('H', None): 1.0,
                   ('S', 1): -10,
                   ('Q', 1): -4,
                   ('S', 2): -15,
                   ('S', 3): -20,
                   ('Q', 2): -250,
                   ('U', None): 0.1,
                   ('I', None): 1.5}


        scores2 = {('H', None): 1,
                   ('S', 1): -1,
                   ('Q', 1): -5,
                   ('S', 2): -2,
                   ('S', 3): -3,
                   ('Q', 2): -10,
                   ('U', None): 0,
                   ('I', None): 17}

        scores3 = {('H', None): 1.0,
                   ('S', 1): 0.9,
                   ('Q', 1): 0.8,
                   ('S', 2): 0.7,
                   ('S', 3): 0.6,
                   ('Q', 2): 0.4,
                   ('U', None): 0,
                   ('I', None): 0}
        if who:
            zocality = deepcopy(self.zoc)
        elif not who:
            zocality = deepcopy(self.zoc2)
        for (i, j) in zocality:
            if not zocality:
                break
            if 'H' in state_art[(i,j)]:
                count = count + scores1[('H', None)]
            if 'I' in state_art[(i,j)]:
                count = count + scores1[('I', None)]
            if 'S1' in state_art[(i,j)]:
                count = count + scores1[('S', 3)]
            if 'S2' in state_art[(i,j)]:
                count = count + scores1[('S', 2)]
            if 'S3' in state_art[(i,j)]:
                count = count + scores1[('S', 1)]
            if 'Q1' in state_art[(i,j)]:
                count = count + scores1[('Q', 2)]
            if 'Q2' in state_art[(i,j)]:
                count = count + scores1[('Q', 1)]
        if not who:
            count = count * (-1)
        return count

    def time_over(self):
        return self.allowed_time and time.time()-self.start_time>self.allowed_time











    def apply_actions_for_real(self,actions):
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
            if 'v' in effect:
                self.state[location] = 'I'
            else:
                self.state[location] = 'Q0'

    def change_states_for_real(self):
        new_state = deepcopy(self.state)
        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if self.state[(i, j)] == 'H' and ('S' in self.state[(i - 1, j)] or
                                                  'S' in self.state[(i + 1, j)] or
                                                  'S' in self.state[(i, j - 1)] or
                                                  'S' in self.state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'
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

        self.state = deepcopy(new_state)


    def what_did_he_do(self, state):
        action = []
        count = 0
        while count < self.actionmax:
            for i in range(1,DIMENSIONS[0]+1):
                for j in range(1, DIMENSIONS[1] + 1):
                        my = self.state[(i,j)][0]
                        his = state[i-1][j-1]
                        if 'I' not in my[0] and his == 'I':
                            move = ("vaccinate", (i-1,j-1))
                            action.append(move)
                            count = count+1
                        elif 'Q' not in my[0] and his == 'Q':
                            move = ("quarantine", (i-1, j-1))
                            action.append(move)
                            count = count + 1
        #print('enemy action was',action)
        return action

    def act(self, state):
        choice = []
        if self.order == 'first':
            if self.day_count == 0:
                choice = self.my_first_move
                self.day_count = self.day_count +1
                self.apply_actions_for_real(choice)
            else:
                enemy_move = self.what_did_he_do(state)
                self.apply_actions_for_real(enemy_move)
                self.change_states_for_real()
                self.day_count = self.day_count + 1
                choice = self.minimaxRoot(4, self.state, True)
                self.apply_actions_for_real(choice)
            # minimaxRoot as 'first'

        elif self.order == 'second':  #TODO we need to consider frst move of oponent in minimax
            if self.day_count == 0:
                enemy_move = self.what_did_he_do(state)
                choice = self.my_first_move
                self.day_count = self.day_count +1
                self.apply_actions_for_real(enemy_move)
                self.apply_actions_for_real(choice)
                self.change_states_for_real()
            else:
                enemy_move = self.what_did_he_do(state)
                self.apply_actions_for_real(enemy_move)
                choice = self.minimaxRoot(4, self.state, True)
                self.apply_actions_for_real(choice)
                self.change_states_for_real()
                self.day_count = self.day_count + 1
        return choice



import random
from copy import deepcopy
from itertools import chain, combinations
import math

DIMENSIONS = (10, 10)
ids = ['316219997', '316278670']

def pad_the_input(a_map):
    state = {}
    new_i_dim = DIMENSIONS[0] + 2
    new_j_dim = DIMENSIONS[1] + 2
    for i in range(0, new_i_dim):
        for j in range(0, new_j_dim):
            if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                state[(i, j)] = 'U'
            elif 'S' in a_map[i - 1][j - 1]:
                state[(i, j)] = 'S1'
            else:
                state[(i, j)] = a_map[i - 1][j - 1]
    return state



class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.initial = pad_the_input(initial_state)
        pass

    def act(self, state):

        state = pad_the_input(state)
        health = set()
        sick = set()
        for (i, j) in self.zoc:
            if 'H' in state[(i+1,j+1)]:
                health.add(("vaccinate", (i, j)))
            if 'S' in state[(i+1,j+1)] and '3' not in state[(i+1,j+1)]:
                sick.add(("quarantine", (i, j)))
        res = []
        health_pow = list(chain.from_iterable(combinations(health, r) for r in range(2)))[1:]
        sick_pow = list(chain.from_iterable(combinations(sick, r) for r in range(2)))[1:]

        if len(health)>0:
            res = health_pow
        elif len(sick)>0:
            res= sick_pow
        else:
            res=()
        h_max=-math.inf
        best_act=[]
        for act in res:
           h, state1= Agent.change_state(self,Agent.apply_action(self,act,state))
           if h>h_max:
              h_max=h
              best_act=act
        return best_act

    def apply_action(self, actions,state):

        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
            if 'v' in effect:
                state[location] = 'I'
            else:
                state[location] = 'Q0'
        return state

    def change_state(self,state):
        new_state = deepcopy(state)
        points=0


        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                                  'S' in state[(i + 1, j)] or
                                                  'S' in state[(i, j - 1)] or
                                                  'S' in state[(i, j + 1)]):

                    new_state[(i, j)] = 'S1'
                    if (i,j) in self.zoc:
                        points-=1
                    else:
                        points+=1
                elif state[(i,j)]=='H' or state[(i,j)]=='I' and (i,j) in self.zoc:
                    points+=1


        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if 'S' in state[(i, j)]:
                    turn = int(state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                        if (i,j) in self.zoc:
                            points-=1
                    else:
                        new_state[(i, j)] = 'H'
                        if (i,j) in self.zoc:
                            points+=1


                if 'Q' in state[(i, j)]:
                    if 'H' in state[(i - 1, j)] and state[(i - 1, j)] in self.zoc:
                        points+=1
                    if 'H' in state[(i + 1, j)] and state[(i + 1, j)] in self.zoc:
                        points+=1
                    if 'H' in state[(i, j-1)] and state[(i, j-1)] in self.zoc:
                        points+=1
                    if 'H' in state[(i, j+1)] and state[(i, j+1)] in self.zoc:
                        points+=1
                    points-=5

        
        return points,new_state







import random
from typing import Set, Any, Tuple


import itertools
from copy import deepcopy

ids = ['345134696','209405067']

DIMENSIONS=(10, 10)

def powerset_size(iterable,max_size):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return list(itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(max_size+1)))[1:]


class Agent:
    def pad_the_input(self,a_map):
        state = {}
        new_i_dim = self.dimensions[0] + 2
        new_j_dim = self.dimensions[1] + 2
        for i in range(0, new_i_dim):
            for j in range(0, new_j_dim):
                if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                    state[(i, j)] = 'U'
                elif 'S' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'S1'
                else:
                    state[(i, j)] = a_map[i - 1][j - 1]
        return state

    def state_to_agent(self,state):
        state_as_list = []
        for i in range(self.dimensions[0]):
            state_as_list.append([]*self.dimensions[1])
            for j in range(self.dimensions[1]):
                state_as_list[i].append(state[(i + 1, j + 1)][0])
        return state_as_list

    def detect_zoc(self):
        coordinates= set([(i, j) for i, j in
                           itertools.product(range(1, self.dimensions[0]+1),
                                             range(1, self.dimensions[1]+1)) if 'U' not in self.initial_state[(i, j)]])

        zoc_2=[(i-1, j-1) for i, j in coordinates]
        zoc=[]
        for elem in zoc_2:
            if elem not in self.zoc_1:
                zoc.append(elem)
        return zoc

    def possible_actions(self, state,zone_of_control):
        sick = set()
        healthy = set()

        for (i, j) in zone_of_control:
            if 'H' in state[i][j]:
                healthy.add((i, j))
            if 'S' in state[i][j]:
                sick.add((i, j))
        medics = []
        police = []
        for item in healthy:
            medics.append(('vaccinate', item))
        for item in sick:
            police.append(('quarantine', item))

        actions = []
        for i in range(len(police)):
            for j in range(i+1, len(police)):
                    temp = [police[i], police[j]]
                    actions.append(temp)
            actions.append([police[i]])

        actions2 = []

        for item in medics:
            actions2.append([item])
            for item2 in actions:
                temp = [e for e in item2]
                temp.append(item)
                actions2.append(temp)

        possible_actions = actions + actions2
        return possible_actions




    def factor2(self,state):
        his_healthy_proximity=dict()

        for (i, j) in self.zoc_1:
            count = 0
            if (i + 1, j) in self.zoc_2 and 'H' in state[(i + 1, j)]:
                count += 1
            if (i - 1, j) in self.zoc_2 and 'H' in state[(i - 1, j)]:
                count += 1
            if (i, j + 1) in self.zoc_2 and 'H' in state[(i, j + 1)]:
                count += 1
            if (i, j - 1) in self.zoc_2 and 'H' in state[(i, j - 1)]:
                count += 1
            his_healthy_proximity.update({(i, j): count})

        my_healthy_proximity=dict()

        for (i, j) in self.zoc_1:
            count = 0
            if (i + 1, j) in self.zoc_1 and 'H' in state[(i + 1, j)]:
                count += 1
            if (i - 1, j) in self.zoc_1 and 'H' in state[(i - 1, j)]:
                count += 1
            if (i, j + 1) in self.zoc_1 and 'H' in state[(i, j + 1)]:
                count += 1
            if (i, j - 1) in self.zoc_1 and 'H' in state[(i, j - 1)]:
                count += 1
            my_healthy_proximity.update({(i, j): count})


        sick_proximity=dict()
        table=self.zoc_1+self.zoc_2

        for (i, j) in self.zoc_1:
            count=0
            if (i+1,j) in  table and 'S' in state[(i+1,j)]:
                count+=1
            if (i-1,j) in table and 'S' in state[(i-1,j)]:
                count+=1
            if (i,j+1) in table and 'S' in state[(i,j+1)]:
                count+=1
            if (i,j-1) in table and 'S' in state[(i,j-1)]:
                count+=1
            sick_proximity.update({(i, j): count})


        return his_healthy_proximity,my_healthy_proximity,sick_proximity




    def __init__(self, initial_state, zone_of_control, order):
        self.dimensions=(len(initial_state),len(initial_state[0]))
        self.initial_state = self.pad_the_input(initial_state)
        self.zoc_1 = deepcopy(zone_of_control)
        self.zoc_2 = self.detect_zoc()
        self.order = order

    def h2_quarantine(self, current_actions, his_actions):

        x = 0
        my_healthy_proximity = 0
        his_healthy_proximity = 0
        vaccinations_actions = []
        quarantine_actions = []
        his_vaccinations_actions = []

        for act in current_actions:
            if 'v' in act[0]:
                vaccinations_actions.append(act)
            elif 'q' in act[0]:
                quarantine_actions.append(act)
        for act in his_actions:
            if 'v' in act[0]:
                his_vaccinations_actions.append(act)
        for actions in quarantine_actions:
            (q_i, q_j) = actions[1]
            for vac in vaccinations_actions:
                (i, j) = vac[1]
                if (i - 1, j) == (q_i, q_j) or (i + 1, j) == (q_i, q_j) or (i, j - 1) == (q_i, q_j) or (i, j + 1) == (
                q_i, q_j):
                    my_healthy_proximity -= 1
            for vac in his_vaccinations_actions:
                (i, j) = vac[1]
                if (i - 1, j) == (q_i, q_j) or (i + 1, j) == (q_i, q_j) or (i, j - 1) == (q_i, q_j) or (i, j + 1) == (
                q_i, q_j):
                    his_healthy_proximity -= 1

            x -= 7
            x -= (self.his_healthy_proximity[(q_i, q_j)] + his_healthy_proximity)
            x += 2*(self.my_healthy_proximity[(q_i, q_j)] + my_healthy_proximity)


        return x

    def h2_vaccination(self, my_current_actions, his_actions):
        x = 0

        sick_proximity = 0
        vaccinations_actions = []
        my_quarantine_actions = []
        his_quarantine_actions = []

        for act in my_current_actions:
            if 'q' in act[0]:
                my_quarantine_actions.append(act)
            elif 'v' in act[0]:
                vaccinations_actions.append(act)
        for act in his_actions:
            if 'q' in act[0]:
                his_quarantine_actions.append(act)

        quarantines = my_quarantine_actions + his_quarantine_actions
        for actions in vaccinations_actions:
            (vac_i, vac_j) = actions[1]
            for quar in quarantines:
                (i, j) = quar[1]
                if (i - 1, j) == (vac_i, vac_j) or (i + 1, j) == (vac_i, vac_j) or (i, j - 1) == (vac_i, vac_j) or (
                i, j + 1) == (vac_i, vac_j):
                    sick_proximity -= 1

            x += (self.sick_proximity[(vac_i, vac_j)] + sick_proximity) + 1

        return x

    def act(self, state):

        try:
            my_actions = self.possible_actions(state, self.zoc_1)
            opponent_actions = self.possible_actions(state, self.zoc_2)
            state = self.pad_the_input(state)
            self.his_healthy_proximity, self.my_healthy_proximity, self.sick_proximity = self.factor2(state)
            min_key = tuple(my_actions[0])

        except:
            return []

        alpha_key = min_key
        alpha = -10000
        for my_current_actions in my_actions:
            min_value = 10000
            for his_actions in opponent_actions:
                value = self.h2_quarantine(my_current_actions, his_actions) + self.h2_vaccination(my_current_actions,
                                                                                                  his_actions)
                if value < min_value:
                    min_value = value
                    min_key = tuple(my_current_actions)
                if min_value <= alpha:
                    break

            if alpha < min_value:
                alpha = min_value
                alpha_key = min_key

        return list(alpha_key)


























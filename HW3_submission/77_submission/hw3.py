from utils import *
from copy import deepcopy
import math
ids = ['308036441', '316407873']


class Agent:
    def __init__(self, initial_state, zone_of_control, order, ):
        self.zoc = zone_of_control
        self.order = order
        time = []
        for k in initial_state:
            time.append([0 for i in range(len(k))])
        for i in range(len(initial_state)):
            for j in range(len(initial_state[i])):
                if initial_state[i][j] == 'S':
                    time[i][j] += 1
        result = self.minimax(initial_state, 4, 1, -math.inf, +math.inf, 'None', [], time)[2]
        self.gameTree = result
        pass

    def act(self, state):

        for i in self.gameTree:
            if state == i[0]:
                temp = [i[1]]
                return temp
        zoc_agent = []
        time = []
        for k in state:
            time.append([0 for i in range(len(k))])
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] == 'S':
                    time[i][j] += 1
        result = self.minimax(state, 2, 1, -math.inf, +math.inf, 'None', [], time)[2]
        for i in result:
            if i[0] == state:
                return [i[1]]
        for i in self.zoc:
            zoc_agent.append((state[i[0]][i[1]], i))
        agent_actions = self.act_list(zoc_agent)
        if len(agent_actions) > 1:
            agent_action = random.choices(agent_actions, k=1)
        else:
            agent_action = agent_actions
        if agent_action == ():
            return []
            # flag = True
            # for loc in self.zoc:
            #     if state[loc[0]][loc[1]] == 'S':
            #         agent_action = [('quarantine', loc)]
            #         flag = False
            #         break
            # if flag:
            #     return agent_action
        temp = [agent_action[0]]
        return temp

    def minimax(self, state,depth, player, alpha, beta, bestact, gameTree, timer):
        if player == 1:
            zoc_agent = []
            for i in self.zoc:
                zoc_agent.append((state[i[0]][i[1]], i))
            agent_actions = self.act_list(zoc_agent)
        else:
            zoc_rival = []
            for i in range(len(state)):
                for j in range(len(state[0])):
                    k = (i, j)
                    if k not in self.zoc:
                        zoc_rival.append((state[i][j], k))
            rival_actions = self.act_list(zoc_rival)
        # s_counter = 0
        # for i in range(len(state)):
        #     for j in range(len(state[0])):
        #         if state[i][j][0] == 'S':
        #             s_counter += 1
        # if s_counter == 0 or depth == 0:
        if depth == 0:
            if player == 1:
                bestVal = self.score(state, player, zoc_agent)
            else:
                bestVal = self.score(state, player, zoc_rival)
            return (bestVal, bestact,  gameTree)

        if player == 1:
            bestVal = -math.inf
            for act in agent_actions:
                value = self.score(state, player, zoc_agent)
                temp_state = deepcopy(state)
                timer, temp_state = self.result(temp_state, act, timer)
                value += self.minimax(temp_state,depth-1, -player, alpha, beta, bestact, gameTree, timer)[0]
                bestVal = max(bestVal, value)
                if bestVal == value:
                    bestact = act
                    flag = True
                    for s in gameTree:
                        if s[0] == state:
                            s[1] = bestact
                            flag = False
                            break
                    if flag == True:
                        gameTree.append([state,bestact])
                alpha = max(alpha, bestVal)
                if beta <= alpha:
                    break
            return (bestVal, bestact, gameTree)
        else:
            bestVal = +math.inf
            for act in rival_actions:
                value = self.score(state, player, zoc_rival)
                temp_state = deepcopy(state)
                timer, temp_state = self.result(temp_state, act, timer)
                value += self.minimax(temp_state, depth-1, -player, alpha, beta, bestact, gameTree, timer)[0]
                bestVal = min(bestVal, value)
                if bestVal == value:
                    best_act = act
                beta = min(beta, bestVal)
                if beta <= alpha:
                    break
            return (bestVal, bestact, gameTree)


    def result(self, state, action, timer):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        if action != ():
            i = action[1][0]
            j = action[1][1]
            state[i][j] = 'I'
        # infection spreads
        new_state = deepcopy(state)
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'S':
                    for k in range(len(state)):
                        for l in range(len(state[0])):
                            if state[k][l] == 'H' and \
                                    ((k == i + 1 and l == j) or
                                     (k == i - 1 and l == j) or
                                     (k == i and l == j + 1) or
                                     (k == i and l == j - 1)):
                                new_state[k][l] = 'S'
        for i in range(len(timer)):
            for j in range(len(timer)):
                timer[i][j] += 1
                if timer[i][j] >= 4 and new_state[i][j] == 'S' or timer[i][j] >= 3 and new_state[i][j] == 'Q':
                    new_state[i][j] = 'H'
                    timer[i][j] = 0
        return timer, new_state

    def score(self, state, player, control_zone):
        score = 0
        for i in control_zone:
            if i[0] == 'H':
                score += 1
            if i[0] == 'I':
                score += 1
            if i[0] == 'S':
                score -= 1
            if i[0] == 'Q':
                score -= 5
        return score


    def act_list(self, zone):
        actions = ()
        for i in zone:
            if i[0] == 'H':
                temp = ('vaccinate', i[1])
                actions = actions + (temp,)
        return actions

    def p_powerset(self, s, r):
        q = []
        for i in range(1, r+1):
            for element in combinations(s, i):
                h_counter = 1
                flag = True
                for k in element:
                    if k[0] == 'H':
                        h_counter -= 1
                    if h_counter < 0:
                        flag = False
                        break
                    if k[0] == 'U' or k[0] == 'Q' or k[0] == 'S':
                        flag = False
                        break
                if flag:
                    q.append(element)
        return q


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

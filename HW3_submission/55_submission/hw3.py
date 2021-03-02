import random
from itertools import combinations

ids = ['211428941']
INF = -1


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.max_depth = 4
        if order == 'first':
            self.maximizer = True
        else:
            self.maximizer = False
        self.zone = zone_of_control
        self.first_round = True
        self.score = 0
        self.med = 1
        self.pol = 2
        self.prev_map = list()
        self.prev_quarred = list()
        self.prev_im = list()
        self.previous_maps = list()
        self.actions = list()
        a_map = initial_state
        i=0
        for row in a_map:
            j=0
            self.prev_map.append(list())
            for item in row:
                if item == 'H':
                    self.prev_map[i].append(('H',INF))
                elif item == 'S':
                    self.prev_map[i].append(('S',3))
                elif item == 'Q':
                    self.prev_map[i].append(('Q',2))
                elif item == 'I':
                    self.prev_map[i].append(('I',INF))
                elif item == 'U':
                    self.prev_map[i].append(('U',INF))
                j+=1
            i+=1
        self.previous_maps.append(self.prev_map)
    
    def get_complete_information_map(self, partial_map,order):
        action = list()
        i = 0
        for row in partial_map:
            j = 0
            for item in row:
                if item == 'Q' and self.prev_map[i][j][0] != 'Q':
                    action.append(('quarantine',(i,j)))
                if item == 'I' and self.prev_map[i][j][0] != 'I':
                    action.append(('vaccinate',(i,j)))
                j+=1
            i+=1
        if order == 'first':
            return self.play_action(self.prev_map,action,'second')
        return self.play_action(self.prev_map,action,'first')






        #action = list()
        #i=0
        #for row in partial_map:
        #    j=0
        #    for item in row:
        #        if item == 'Q' and self.prev_map[i][j][0] != 'Q':
        #            action.append(('quarantine', (i,j)))
        #        elif item == 'I' and self.prev_map[i][j][0] != 'I':
        #            action.append(('vaccinate',(i,j)))
        #        j += 1
        #    i += 1
        #if order == 'first':
        #    next_order = 'second'
        #else:
        #    next_order = 'first'
        #self.actions.append(action)
        #new_map = self.play_action(self.prev_map,action,next_order)
        #return new_map

    def copy_map(self,old_map):
        map = list()
        i=0
        for row in old_map:
            map.append(list())
            for item in row:
                map[i].append(item)
            i+=1
        return map

    def play_action(self,map,action,order):
        just_im = list()
        just_quar = list()
        new_map = self.copy_map(map)
        for act in action:
            i = act[1][0]
            j = act[1][1]
            if act[0] == 'quarantine':
                if order == 'first':
                    new_map[i][j] = ('Q',3)
                else:
                    new_map[i][j] = ('Q',2)
                just_quar.append((i,j))
            elif act[0] == 'vaccinate':
                new_map[i][j] = ('I',INF)
                just_im.append((i,j))
        if order == 'first':
            return new_map
        #just_quar.extend(self.prev_quarred)
        #just_im.extend(self.prev_im)
        just_sick = list()
        i = 0
        for row in new_map:
            j = 0
            for item in row:
                if item[0] == 'S' and (i,j) not in just_sick:
                    if i > 0 and new_map[i-1][j][0] == 'H':
                        new_map[i-1][j] = ('S',3)
                        just_sick.append((i-1,j))
                    if i < len(new_map)-1 and new_map[i+1][j][0] == 'H':
                        new_map[i+1][j] = ('S',3)
                        just_sick.append((i+1,j))
                    if j > 0 and new_map[i][j-1][0] == 'H':
                        new_map[i][j-1] = ('S',3)
                        just_sick.append((i,j-1))
                    if j < len(new_map[0])-1 and new_map[i][j+1][0] == 'H':
                        new_map[i][j+1] = ('S',3)
                        just_sick.append((i,j+1))
                j+=1
            i+=1
        i = 0
        for row in new_map:
            j = 0
            for item in row:
                if (i,j) not in just_sick and (i,j) not in just_quar:
                    if item[1] > 1:
                        new_map[i][j] = (item[0],item[1]-1)
                    elif item[1] != -1:
                        new_map[i][j] = ('H',INF)
                j+=1
            i+=1
        return new_map














        #new_map = self.copy_map(map)
        #just_quarred = list()
        #just_im = list()
        #for act in action:
        #    i = act[1][0]
        #    j = act[1][1]
        #    if act[0] == 'vaccinate':
        #        new_map[i][j] = ('I',INF)
        #        just_im.append((i,j))
        #    else:
        #        new_map[i][j] = ('Q',2)
        #        just_quarred.append((i,j))
        #if order == 'first':
        #    self.prev_im = just_im
        #    self.prev_quarred = just_quarred
        #    return new_map
        #just_im.extend(self.prev_im)
        #just_quarred.extend(self.prev_quarred)
        #just_infected = list()
        #flag = True
        #i = 0
        #for row in new_map:
        #    j = 0
        #    for item in row:
        #        if (i,j) in just_quarred or (i,j) in just_im or (i,j) in just_infected:
        #            flag= False
        #        if item[0] == 'S' and flag:
        #            if i > 0 and new_map[i-1][j][0] == 'H':
        #                new_map[i-1][j] = ('S',3)
        #                just_infected.append((i-1,j))
        #            if i < len(new_map)-1 and new_map[i+1][j][0] == 'H':
        #                new_map[i+1][j] = ('S',3)
        #                just_infected.append((i+1,j))
        #            if j > 0 and new_map[i][j-1][0] == 'H':
        #                new_map[i][j-1] = ('S',3)
        #                just_infected.append((i,j-1))
        #            if j < len(new_map[0])-1 and new_map[i][j+1][0] == 'H':
        #                new_map[i][j+1] = ('S',3)
        #                just_infected.append((i,j+1))
        #        flag = True
        #        j+=1
        #    i+=1
        #i = 0
        #for row in new_map:
        #    j = 0
        #    for item in row:
        #        if (i,j) not in just_quarred and (i,j) not in just_infected:
        #            if item[0] == 'S':
        #                if item[1] > 1:
        #                    new_map[i][j] = ('S', item[1]-1)
        #                else:
        #                    new_map[i][j] = ('H',INF)
        #            if item[0] == 'Q':
        #                if item[1] > 1:
        #                    new_map[i][j] = ('Q', item[1]-1)
        #                else:
        #                    new_map[i][j] = ('H',INF)
        #        j+=1
        #    i+=1
        #return new_map

    def is_terminal(self,map,depth):
        if depth == self.max_depth:
            return True
        for row in map:
            for item in row:
                if item[0] == 'S':
                    return False
        return True

    def calc_utility(self,map):
        score = 0
        coef = 1
        if self.maximizer:
            c = 1
        else:
            c = -1
        i = 0
        for row in map:
            j = 0
            for item in row:
                if (i,j) in self.zone:
                    coef = 1
                else:
                    coef = -1
                if item[0] == 'H' or item[0] == 'I':
                    score += coef*1
                elif item[0] == 'S':
                    score -= coef*1
                elif item[0] == 'Q':
                    score -= coef*5
                j+=1
            i+=1
        return score

    def generate_successor_actions(self, map,player):
        med = self.med
        pol = self.pol
        healthy = list()
        sick = list()
        if player == 'me':
            i = 0
            for row in map:
                j = 0
                for item in row:
                    if item[0] == 'S':
                        if (i,j) in self.zone:
                            sick.append((i,j))
                        if i > 0 and (i-1,j) in self.zone and map[i-1][j][0] == 'H' and (i-1,j) not in healthy:
                            healthy.append((i-1,j))
                        if i < len(map)-1 and (i+1,j) in self.zone and map[i+1][j][0] == 'H' and (i+1,j) not in healthy:
                            healthy.append((i+1,j))
                        if j > 0 and (i,j-1) in self.zone and map[i][j-1][0] == 'H' and (i,j-1) not in healthy:
                            healthy.append((i,j-1))
                        if j < len(map[0])-1 and (i,j+1) in self.zone and map[i][j+1][0] == 'H' and (i,j+1) not in healthy:
                            healthy.append((i,j+1))
                    j+=1
                i+=1
        else:
            i = 0
            for row in map:
                j = 0
                for item in row:
                    if item[0] == 'S':
                        if (i,j) not in self.zone:
                            sick.append((i,j))
                        if i > 0 and (i-1,j) not in self.zone and map[i-1][j][0] == 'H' and (i-1,j) not in healthy:
                            healthy.append((i-1,j))
                        if i < len(map)-1 and (i+1,j) not in self.zone and map[i+1][j][0] == 'H' and (i+1,j) not in healthy:
                            healthy.append((i+1,j))
                        if j > 0 and (i,j-1) not in self.zone and map[i][j-1][0] == 'H' and (i,j-1) not in healthy:
                            healthy.append((i,j-1))
                        if j < len(map[0])-1 and (i,j+1) not in self.zone and map[i][j+1][0] == 'H' and (i,j+1) not in healthy:
                            healthy.append((i,j+1))
                    j+=1
                i+=1
        if not healthy:
            if len(sick) + len(healthy) == 0:
                for row in map:
                    j = 0
                    for item in row:
                        if ((i,j) in self.zone and player == 'me') or ((i,j) in self.zone and player == 'foe'):
                            if item[0] == 'H':
                                healthy.append((i,j))
                        j+=1
                i+=1
        med_possibilities = []
        pol_possibilities = []
        if med < len(healthy):
            for i in range(1,med+1):
                med_possibilities.extend(combinations(healthy,i))
        else:
            for i in range(1,len(healthy)+1):
                med_possibilities.extend(combinations(healthy,i))
        if not healthy:
            pol_possibilities.extend(combinations(sick,1))
        #if pol < len(sick):
        #    pol_possibilities.extend(combinations(sick,1))
        #else:
        #    for i in range(1,len(sick)+1):
        #        pol_possibilities.extend(combinations(sick,i))
        act_list = []
        act_item = []
        for med_pos in med_possibilities:
            for pol_pos in pol_possibilities:
                act_item = []
                for single_med in med_pos:
                    act_item.append(("vaccinate",single_med))
                for single_pol in pol_pos:
                    act_item.append(("quarantine",single_pol))
                if not act_item:
                    continue
                act_list.append(tuple(act_item))
        for med_pos in med_possibilities:
            act_item = []
            for single_med in med_pos:
                act_item.append(("vaccinate",single_med))
            if not act_item:
                continue
            act_list.append(tuple(act_item))
        for pol_pos in pol_possibilities:
            act_item = []
            for single_pol in pol_pos:
                act_item.append(("quarantine",single_pol))
            if not act_item:
                continue
            act_list.append(tuple(act_item))
        return act_list


        #med = self.med
        #pol = self.pol
        #healthy_list = list()
        #sick_list = list()
        #i = 0
        #for row in map:
        #    j = 0
        #    for item in row:
        #        if (i,j) in self.zone:
        #            if item[0] == 'S':
        #                sick_list.append((i,j))
        #                if i > 0 and (i-1,j) in self.zone and map[i-1][j][0] == 'H':
        #                    healthy_list.append((i-1,j))
        #                if i < len(map)-1 and (i+1,j) in self.zone and map[i+1][j][0] == 'H':
        #                    healthy_list.append((i+1,j))
        #                if j > 0 and (i,j-1) in self.zone and map[i][j-1][0] == 'H':
        #                    healthy_list.append((i,j-1))
        #                if i < len(map[0])-1 and (i,j+1) in self.zone and map[i][j+1][0] == 'H':
        #                    healthy_list.append((i,j+1))
        #        else:
        #            if item[0] == 'S':
        #                if i > 0 and (i-1,j) in self.zone and map[i-1][j][0] == 'H':
        #                    healthy_list.append((i-1,j))
        #                if i < len(map)-1 and (i+1,j) in self.zone and map[i+1][j][0] == 'H':
        #                    healthy_list.append((i+1,j))
        #                if j > 0 and (i,j-1) in self.zone and map[i][j-1][0] == 'H':
        #                    healthy_list.append((i,j-1))
        #                if i < len(map[0])-1 and (i,j+1) in self.zone and map[i][j+1][0] == 'H':
        #                    healthy_list.append((i,j+1))
        #        j += 1
        #    i += 1
        #med_possibilities = []
        #pol_possibilities = []
        #if med < len(healthy_list):
        #    med_possibilities.extend(combinations(healthy_list,med))
        #else:
        #    med_possibilities.extend(combinations(healthy_list,len(healthy_list)))
        #if pol < len(sick_list):
        #    pol_possibilities.extend(combinations(sick_list,pol))
        #else:
        #    pol_possibilities.extend(combinations(sick_list,len(sick_list)))
        #act_list = []
        #act_item = []
        #for med_pos in med_possibilities:
        #    for pol_pos in pol_possibilities:
        #        act_item = []
        #        for single_med in med_pos:
        #            act_item.append(("vaccinate",single_med))
        #        for single_pol in pol_pos:
        #            act_item.append(("quarantine",single_pol))
        #        act_list.append(tuple(act_item))
        #for med_pos in med_possibilities:
        #    act_item = []
        #    for single_med in med_pos:
        #        act_item.append(("vaccinate",single_med))
        #    act_list.append(tuple(act_item))
        #for pol_pos in pol_possibilities:
        #    act_item = []
        #    for single_pol in pol_pos:
        #        act_item.append(("quarantine",single_pol))
        #    act_list.append(tuple(act_item))
        #return act_list

    def minimize(self,map,alpha,beta,depth,order,sum):
        if self.is_terminal(map,depth):
            return ((),sum+self.calc_utility(map))
        actions = self.generate_successor_actions(map,'foe')
        if not actions:
            return ((),sum + 1000)
        if order == 'first':
            next_order = 'second'
        else:
            next_order = 'first'
        map_results = list()
        value = ((),10000)
        for act in actions:
            new_map = self.play_action(map,act,order)
            new_value = self.maximize(new_map,alpha,beta,depth+1,next_order,sum+self.calc_utility(new_map))
            if new_value[1] < value[1]:
                value = (act,new_value[1])
            if value[1] < alpha:
                return value
            if value[1] < beta:
                beta = value[1]
        return value



    def maximize(self, map, alpha, beta, depth, order,sum):
        if self.is_terminal(map,depth):
            return ((),sum + self.calc_utility(map))
        actions = self.generate_successor_actions(map,'me')
        if not actions:
            return ((),sum - 1000)
        if order == 'first':
            next_order = 'second'
        else:
            next_order = 'first'
        map_results = list()
        value = ((),-10000)
        for act in actions:
            if not act:
                return ((),sum-1000)
            new_map = self.play_action(map,act,order)
            new_value = self.minimize(new_map,alpha,beta,depth+1,next_order,sum+self.calc_utility(new_map))
            if new_value[1] > value[1]:
                value = (act,new_value[1])
            if value[1] >= beta:
                return value
            if value[1] >= alpha:
                alpha = value[1]
        return value
    def simulate_full_game(self, maps ,actions):
        counter = 0 
        next_order = 'first'
        for action in actions:
            if next_order == 'first':
                maps[int(counter/2)] = self.play_action(maps[int(counter/2)],action,next_order)
            else:
                maps[int(counter/2)+1] = self.play_action(maps[int(counter/2)],action,next_order)
            counter+=1
            if next_order == 'first':
                next_order = 'second'
            else: 
                next_order = 'first'
        self.previous_maps = maps


    def act(self, state):
        map = None
        order = ''
        if self.maximizer:
            order = 'first'
        else:
            order = 'second'
        if self.first_round and self.maximizer:
            map = self.prev_map
            self.first_round = False
        else:
            map = self.get_complete_information_map(state,order)
        #for i in range(len(map)):
        #    for j in range(len(map[0])):
        #        if map[i][j][0] != state[i][j]:
        #            self.get_complete_information_map(state,order)
        self.prev_map = self.copy_map(map)
        action = self.maximize(self.prev_map,-10000,10000, 0,order,0)[0]
        self.prev_map = self.play_action(self.prev_map,action,order)
        return action








        #map = None
        #order = ''
        #if self.maximizer:
        #    order = 'first'
        #else:
        #    order = 'second'
        #if self.first_round and self.maximizer:
        #    map = self.prev_map
        #    self.first_round = False
        #else:
        #    map = self.get_complete_information_map(state,order)
        ##for i in range(len(map)):
        ##    for j in range(len(map[0])):
        ##        if map[i][j][0] != state[i][j]:
        ##            self.simulate_full_game(self.previous_maps,self.actions)
        ##            for k in range(len(map)):
        ##                for h in range(len(map[0])):
        ##                    if self.previous_maps[len(self.previous_maps)-1][i][j][0] != state[i][j]:
        ##                        k=5
        #self.prev_map = self.copy_map(map)
        #action = None
        #if self.maximizer:
        #    action = self.maximize(map,10000,-10000,0,order,0)[0]
        #    self.prev_map = self.play_action(self.prev_map,action,order)
        #    self.previous_maps.append(self.prev_map)
        #else:
        #    action = self.minimize(map,10000,-10000,0,order,0)[0]
        #    self.prev_map = self.play_action(self.prev_map,action,order)
        #    self.previous_maps.append(self.prev_map)
        #self.actions.append(action)
        
        #return action

# implementation of a random agent
# class Agent:
#     def __init__(self, zone_of_control, order):
#         self.zoc = zone_of_control
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

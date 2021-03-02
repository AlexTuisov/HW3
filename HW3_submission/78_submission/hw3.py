import random


ids = ['314936568']

cutoff = 0

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        #for i in sorted(self.zoc, key=lambda x: x[0]):
        #    print(i)
        
        tmp = []
        print('other')
        for i in range(len(initial_state)):
            for t in range(len(initial_state[-1])):
                if ((i, t) not in self.zoc and initial_state[i][t] != 'U'):
                    #print((i, t))
                    tmp.append((i, t))
            
        self.other_player = tmp
        print(len(self.zoc), len(self.other_player))
        
        self.other_health = []
        self.other_sick = []
        self.other_q = []

    def process_state(self, state):
        healthy = []
        sick = []
        q = []
        
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
            if 'Q' in state[i][j]:
                q.append((i, j))
                
        self.other_health = []
        self.other_sick = []
        self.other_q = []  
        
        for (i, j) in self.other_player:
            if 'H' in state[i][j]:
                self.other_health.append((i, j))
            if 'S' in state[i][j]:
                self.other_sick.append((i, j))
            if 'Q' in state[i][j]:
                self.other_q.append((i, j))
        
        return healthy, sick, q

    def sick_heuristic(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1.0 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        tmp = sum(-0.75 for neighbor in neighbors if (neighbor in self.other_health and neighbor in self.other_player))
        return h+tmp
    
    def health_heuristic(self, sick, healthy, coord):
        num = 0
        for coordinate in healthy:
            if coord != coordinate:
                neighbors = ((coordinate[0] - 1, coordinate[1]),
                             (coordinate[0] + 1, coordinate[1]),
                             (coordinate[0], coordinate[1] - 1),
                             (coordinate[0], coordinate[1] + 1))
                for t in neighbors:
                    if (t in sick or t in self.other_sick):
                        num += 1
        return num

    def act(self, state):
        action = []
        healthy, sick, q = self.process_state(state)
        sick_lis = [[i, self.sick_heuristic(healthy, i)] for i in sick]
        sick_lis.sort(key = lambda x: x[1], reverse=True)
        sick_tru = [i[0] for i in sick_lis if i[1] > cutoff]
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        if (len(q) <= len(self.other_q)):
            try:
                to_quarantine = (sick_tru[:2])
            except KeyError:
                to_quarantine = []
        else:
            try:
                to_quarantine = (sick[:2])
            except KeyError:
                to_quarantine = []
            
        healthy.sort(key = lambda x: self.health_heuristic(sick, healthy, x), reverse=True)
        try:
            to_vaccinate = random.sample(healthy, 1)
        except ValueError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

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

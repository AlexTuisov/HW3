import random

ids = ['204485601', '304995715']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = initial_state
        self.zoc = zone_of_control
        self.order = order
        self.H_loc = []
        self.S_loc = []

    def S_loc_zoc(self, state):
        S_location = []
        for loc in self.zoc:
            if state[loc[0]][loc[1]] == 'S':
                S_location.append(loc)
        return tuple(tuple(i) for i in S_location)

    def H_loc_zoc(self, state):
        H_location = []
        for loc in self.zoc:
            if state[loc[0]][loc[1]] == 'H':
                H_location.append(loc)
        return tuple(tuple(i) for i in H_location)

    def S_rival_loc_zoc(self, state):
        S_rival_loc = []
        self.S_loc = self.S_loc_zoc(state)
        for i in state:
            for j in i:
                if j == 'S' and (i, j) not in self.S_loc:
                    loc = (i, j)
                    S_rival_loc.append(loc)
        return tuple(tuple(i) for i in S_rival_loc)

    def S_H_neighbours(self, state):
        H_loc_mine = self.H_loc_zoc(state)
        for loc1 in H_loc_mine:
            for loc2 in self.S_rival_loc_zoc(state):
                if loc1[0] == loc2[0]:
                    if loc1[1] + 1 == loc2[1] and loc1[1] != 9:
                        return loc1
                    elif loc1[1] - 1 == loc2[1] and loc1[1] != 0:
                        return loc1
                if loc1[1] == loc2[1]:
                    if loc1[0] + 1 == loc2[0] and loc1[0] != 9:
                        return loc1
                    elif loc1[0] - 1 == loc2[0] and loc1[0] != 0:
                        return loc1
        
        S_loc_mine = self.S_loc_zoc(state)
        for loc1 in H_loc_mine:
            for loc2 in S_loc_mine:
                if loc1[0] == loc2[0]:
                    if loc1[1] + 1 == loc2[1] and loc1[1] != 9:
                        return loc1
                    elif loc1[1] - 1 == loc2[1] and loc1[1] != 0:
                        return loc1
                if loc1[1] == loc2[1]:
                    if loc1[0] + 1 == loc2[0] and loc1[0] != 9:
                        return loc1
                    elif loc1[0] - 1 == loc2[0] and loc1[0] != 0:
                        return loc1
        return 0

    def H_loc_rival_zoc(self, state):
        rival_H_loc = []
        self.H_loc = self.H_loc_zoc(state)
        for i in state:
            for j in i:
                if j == 'H' and (i, j) not in self.H_loc:
                    rival_H_loc.append((i, j))
        return tuple(tuple(i) for i in rival_H_loc)

    def H_H_neighbours(self, state, H_pr):
        H_loc_mine = self.H_loc_zoc(state)
        for loc1 in H_loc_mine:
            if loc1[0] == H_pr[0]:
                if loc1[1] + 1 == H_pr[1] and loc1[1] != 9:
                    return True
                elif loc1[1] - 1 == H_pr[1] and loc1[1] != 0:
                    return True
            if loc1[1] == H_pr[1]:
                if loc1[0] + 1 == H_pr[0] and loc1[0] != 9:
                    return True
                elif loc1[0] - 1 == H_pr[0] and loc1[0] != 0:
                    return True
        
        rival_H_loc = self.H_loc_rival_zoc(state)
        for loc1 in rival_H_loc:
            if loc1[0] == H_pr[0]:
                if loc1[1] + 1 == H_pr[1] and loc1[1] != 9:
                    return True
                elif loc1[1] - 1 == H_pr[1] and loc1[1] != 0:
                    return True
            if loc1[1] == H_pr[1]:
                if loc1[0] + 1 == H_pr[0] and loc1[0] != 9:
                    return True
                elif loc1[0] - 1 == H_pr[0] and loc1[0] != 0:
                    return True
        return False

    def H_with_H_neighbour(self, state):
        H_loc_mine = self.H_loc_zoc(state)
        for loc1 in H_loc_mine:
            for loc2 in H_loc_mine:
                if loc1[0] == loc2[0]:
                    if loc1[1] + 1 == loc2[1] and loc1[1] != 9:
                        return loc1
                    elif loc1[1] - 1 == loc2[1] and loc1[1] != 0:
                        return loc1
                if loc1[1] == loc2[1]:
                    if loc1[0] + 1 == loc2[0] and loc1[0] != 9:
                        return loc1
                    elif loc1[0] - 1 == loc2[0] and loc1[0] != 0:
                        return loc1
        
        rival_H_loc = self.H_loc_rival_zoc(state)
        for loc1 in H_loc_mine:
            for loc2 in rival_H_loc:
                if loc1[0] == loc2[0]:
                    if loc1[1] + 1 == loc2[1] and loc1[1] != 9:
                        return loc1
                    elif loc1[1] - 1 == loc2[1] and loc1[1] != 0:
                        return loc1
                if loc1[1] == loc2[1]:
                    if loc1[0] + 1 == loc2[0] and loc1[0] != 9:
                        return loc1
                    elif loc1[0] - 1 == loc2[0] and loc1[0] != 0:
                        return loc1
        return 0

    def one_med(self, state):
        if self.S_H_neighbours(state):
            action = ('vaccinate', self.S_H_neighbours(state))
            return [3, action]
        elif self.H_with_H_neighbour(state):
            action = ('vaccinate', self.H_with_H_neighbour(state))
            return [0, action]
        elif self.H_loc:
            vaccinate = random.sample(self.H_loc, 1)
            action = ('vaccinate', vaccinate[0])
            return [0, action]
        else:
            return [-1,()]

    def my_H_S_neighbours(self, state):
        S_pr = []
        S_loc_mine = self.S_loc_zoc(state)
        H_loc_mine = self.H_loc_zoc(state)
        for loc1 in S_loc_mine:
            for loc2 in H_loc_mine:
                if loc1[0] == loc2[0]:
                    if loc1[1] + 1 == loc2[1] and loc1[1] != 9:
                        S_pr.append(loc1)
                    elif loc1[1] - 1 == loc2[1] and loc1[1] != 0:
                        S_pr.append(loc1)
                if loc1[1] == loc2[1]:
                    if loc1[0] + 1 == loc2[0] and loc1[0] != 9:
                        S_pr.append(loc1)
                    elif loc1[0] - 1 == loc2[0] and loc1[0] != 0:
                        S_pr.append(loc1)
        
        if len(S_pr) > 0:
            return tuple(tuple(i) for i in S_pr)
        return 0

    def count_times(self, S_location, S_pr):
        count = 0
        for loc in S_pr:
            if loc == S_location:
                count = count + 1
        return count

    def one_med_one_police(self, state):
        action = []
        action.append(self.one_med(state)[1])
        count = int(self.one_med(state)[0])
        if self.S_loc == ():
            return [count, action]
        if not self.my_H_S_neighbours(state):
            return [count - 3, action]
        if self.my_H_S_neighbours(state):
            S_pr = self.my_H_S_neighbours(state)           
            for S_location in self.S_loc:
                if self.count_times(S_location, S_pr) == 4:
                    action.append(('quarantine', S_location))
                    return [count + 9, action]

            for S_location in self.S_loc:
                if self.count_times(S_location, S_pr) == 3:
                    action.append(('quarantine', S_location))
                    return [count + 6, action]

            for S_location in self.S_loc:
                if self.count_times(S_location, S_pr) == 2:
                    action.append(('quarantine', S_location))
                    return [count + 3, action]

            for S_location in self.S_loc:
                if self.count_times(S_location, S_pr) == 1:
                    action.append(('quarantine', S_location))
                    return [count, action]

        return [-3, action]

    def one_med_two_police(self, state):
        action = []
        action.append(self.one_med(state)[1])
        count = self.one_med(state)[0]
        a_count = 2
        if self.S_loc == ():
            return [count, action]
        if not self.my_H_S_neighbours(state):
            return [count - 3, action]
        if self.my_H_S_neighbours(state):
            S_pr = self.my_H_S_neighbours(state)
            for S_location in self.S_loc:
                if a_count == 0:
                    return [count, action]

                if self.count_times(S_location, S_pr) == 4:
                    count = count + 9
                    action.append(('quarantine', S_location))
                    a_count = a_count - 1

            for S_location in self.S_loc:
                if a_count == 0:
                    return [count, action]

                if self.count_times(S_location, S_pr) == 3:
                    count = count + 6
                    action.append(('quarantine', S_location))
                    a_count = a_count - 1

            for S_location in self.S_loc:
                if a_count == 0:
                    return [count, action]

                if self.count_times(S_location, S_pr) == 2:
                    count = count + 3
                    action.append(('quarantine', S_location))
                    a_count = a_count - 1

            for S_location in self.S_loc:
                if a_count == 0:
                    return [count, action]

                if self.count_times(S_location, S_pr) == 1:
                    action.append(('quarantine', S_location))
                    a_count = a_count - 1
        return [count, action]

    def act(self, state):
        action = []
        if self.order == "first" or "second":
            action.append(self.one_med(state)[1])
            count = int(self.one_med(state)[0])
            if self.one_med_one_police(state)[0] >= count:
                action = self.one_med_one_police(state)[1]
                count = self.one_med_one_police(state)[0]
            if self.one_med_two_police(state)[0] >= count:
                action = self.one_med_two_police(state)[1]
                count = self.one_med_two_police(state)[0]
            if count == -1:
                return []
        return action
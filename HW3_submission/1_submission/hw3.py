import random

ids = ['312234784', '316365410']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial = initial_state
        self.zoc = zone_of_control
        self.order = order
        self.h_locations = []
        self.s_locations = []

    def act(self, state):
        action = []
        ZOC = self.zoc
        self.H_locations_my_zoc(state)
        self.S_locations_my_zoc(state)

        if self.order == "first":
            action = self.Max_function(state, ZOC)

        elif self.order == "second":
            action = self.Max_function(state, ZOC)

        return action

    def Max_function(self, state, ZOC):
        action = []
        action.append(self.using_one_Medic(state, ZOC)[1])
        count = int(self.using_one_Medic(state, ZOC)[0])
        cout1 = self.using_one_Medic_one_Police(state, ZOC)
        cout2 = self.using_one_Medic_two_Police(state, ZOC)
        if cout1[0] >= count:
            action = self.using_one_Medic_one_Police(state, ZOC)[1]
            count = cout1[0]
        if cout2[0] >= count:
            action = self.using_one_Medic_two_Police(state, ZOC)[1]
            count = cout2[0]
        if count == -1:
            return []
        return action

    # def Min_function(self, state, ZOC):
    #     action = []
    #
    #     return action

    def using_one_Medic(self, state, ZOC):
        count = 0
        if self.my_H_S_neighbour(state):
            H_priority = self.my_H_S_neighbour(state)
            if self.my_H_H_neighbour(state, H_priority):
                count = 3
                action = ('vaccinate', H_priority)
                return [count, action]
            else:
                count = 3
                action = ('vaccinate', H_priority)
                return [count, action]
        elif self.find_H_with_my_H_neighbour(state):
            H_priority = self.find_H_with_my_H_neighbour(state)
            count = 0
            action = ('vaccinate', H_priority)
            return [count, action]
        else:
            if self.h_locations:
                to_vaccinate = random.sample(self.h_locations, 1)
                action = ('vaccinate', to_vaccinate[0])
                return [count, action]
            else:
                return [-1,()]

    def using_one_Medic_one_Police(self, state, ZOC):
        action = []
        count = int(self.using_one_Medic(state, ZOC)[0])
        action.append(self.using_one_Medic(state, ZOC)[1])
        if self.s_locations == ():
            return [count, action]
        if self.my_S_my_H_neighbour(state) is False:
            count = count - 3
            return [count, action]
        elif self.my_S_my_H_neighbour(state):
            s_priority = self.my_S_my_H_neighbour(state)
            for s_loc in self.s_locations:
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 4:
                    count = count + 9
                    action.append(('quarantine', s_loc))
                    return [count, action]
            for s_loc in self.s_locations:
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 3:
                    count = count + 6
                    action.append(('quarantine', s_loc))
                    return [count, action]
            for s_loc in self.s_locations:
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 2:
                    count = count + 3
                    action.append(('quarantine', s_loc))
                    return [count, action]
            for s_loc in self.s_locations:
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 1:
                    action.append(('quarantine', s_loc))
                    return [count, action]

        return [-3, action]

    def using_one_Medic_two_Police(self, state, ZOC):
        action_count = 2
        action = []
        count = self.using_one_Medic(state, ZOC)[0]
        action.append(self.using_one_Medic(state, ZOC)[1])
        if self.s_locations == ():
            return [count, action]
        if self.my_S_my_H_neighbour(state) is False:
            count = count - 3
            return [count, action]
        elif self.my_S_my_H_neighbour(state):
            s_priority = self.my_S_my_H_neighbour(state)
            for s_loc in self.s_locations:
                if action_count == 0:
                    return [count, action]
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 4:
                    count = count + 9
                    action.append(('quarantine', s_loc))
                    action_count = action_count - 1
            for s_loc in self.s_locations:
                if action_count == 0:
                    return [count, action]
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 3:
                    count = count + 6
                    action.append(('quarantine', s_loc))
                    action_count = action_count - 1
            for s_loc in self.s_locations:
                if action_count == 0:
                    return [count, action]
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 2:
                    count = count + 3
                    action.append(('quarantine', s_loc))
                    action_count = action_count - 1
            for s_loc in self.s_locations:
                if action_count == 0:
                    return [count, action]
                how_many = self.count_how_many_times(s_loc, s_priority)
                if how_many == 1:
                    action.append(('quarantine', s_loc))
                    action_count = action_count - 1
        return [count, action]

    def H_locations_my_zoc(self, state):
        H_Locations = []
        for loc in self.zoc:
            if state[loc[0]][loc[1]] == 'H':
                H_Locations.append(loc)
        H_Locations = tuple(tuple(i) for i in H_Locations)
        return H_Locations

    def S_locations_my_zoc(self, state):
        S_Locations = []
        for loc in self.zoc:
            if state[loc[0]][loc[1]] == 'S':
                S_Locations.append(loc)
        S_Locations = tuple(tuple(i) for i in S_Locations)
        return S_Locations

    def H_locations_rival_zoc(self, state):
        rival_H_Locations = []
        self.h_locations = self.H_locations_my_zoc(state)
        for i in state:
            for j in i:
                if j == 'H':
                    if (i, j) not in self.h_locations:
                        loc = (i, j)
                        rival_H_Locations.append(loc)
        rival_H_Locations = tuple(tuple(i) for i in rival_H_Locations)
        return rival_H_Locations

    def S_locations_rival_zoc(self, state):
        rival_S_Locations = []
        self.s_locations = self.S_locations_my_zoc(state)
        for i in state:
            for j in i:
                if j == 'S':
                    if (i, j) not in self.s_locations:
                        loc = (i, j)
                        rival_S_Locations.append(loc)
        rival_S_Locations = tuple(tuple(i) for i in rival_S_Locations)
        return rival_S_Locations

    def my_H_S_neighbour(self, state):
        rival_s_loc = self.S_locations_rival_zoc(state)
        my_s_loc = self.S_locations_my_zoc(state)
        my_h_loc = self.H_locations_my_zoc(state)

        for location1 in my_h_loc:
            for location2 in rival_s_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        return location1
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        return location1
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        return location1
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        return location1
        for location1 in my_h_loc:
            for location2 in my_s_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        return location1
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        return location1
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        return location1
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        return location1
        return 0

    def my_H_rival_S_neighbour(self, state):
        rival_s_loc = self.S_locations_rival_zoc(state)
        my_h_loc = self.H_locations_my_zoc(state)

        priority_H = []
        for location1 in my_h_loc:
            for location2 in rival_s_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        priority_H.append(location1)
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        priority_H.append(location1)
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        priority_H.append(location1)
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        priority_H.append(location1)
        return priority_H

    def my_H_H_neighbour(self, state, H_priority):
        my_h_loc = self.H_locations_my_zoc(state)
        rival_h_loc = self.H_locations_rival_zoc(state)

        for location1 in my_h_loc:
            if location1[0] == H_priority[0]:
                if (location1[1] + 1) == H_priority[1] and location1[1] != 9:
                    return True
                elif (location1[1] - 1) == H_priority[1] and location1[1] != 0:
                    return True
            if location1[1] == H_priority[1]:
                if (location1[0] + 1) == H_priority[0] and location1[0] != 9:
                    return True
                elif (location1[0] - 1) == H_priority[0] and location1[0] != 0:
                    return True
        for location1 in rival_h_loc:
            if location1[0] == H_priority[0]:
                if (location1[1] + 1) == H_priority[1] and location1[1] != 9:
                    return True
                elif (location1[1] - 1) == H_priority[1] and location1[1] != 0:
                    return True
            if location1[1] == H_priority[1]:
                if (location1[0] + 1) == H_priority[0] and location1[0] != 9:
                    return True
                elif (location1[0] - 1) == H_priority[0] and location1[0] != 0:
                    return True
        return False

    def find_H_with_my_H_neighbour(self, state):
        my_h_loc = self.H_locations_my_zoc(state)
        rival_h_loc = self.H_locations_rival_zoc(state)

        for location1 in my_h_loc:
            for location2 in my_h_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        return location1
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        return location1
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        return location1
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        return location1
        for location1 in my_h_loc:
            for location2 in rival_h_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        return location1
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        return location1
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        return location1
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        return location1
        return 0

    def my_S_my_H_neighbour(self, state):
        priority_S = []
        my_s_loc = self.S_locations_my_zoc(state)
        my_h_loc = self.H_locations_my_zoc(state)

        for location1 in my_s_loc:
            for location2 in my_h_loc:
                if location1[0] == location2[0]:
                    if (location1[1] + 1) == location2[1] and location1[1] != 9:
                        priority_S.append(location1)
                    elif (location1[1] - 1) == location2[1] and location1[1] != 0:
                        priority_S.append(location1)
                if location1[1] == location2[1]:
                    if (location1[0] + 1) == location2[0] and location1[0] != 9:
                        priority_S.append(location1)
                    elif (location1[0] - 1) == location2[0] and location1[0] != 0:
                        priority_S.append(location1)
        if len(priority_S) != 0:
            priority_S = tuple(tuple(i) for i in priority_S)
            return priority_S
        else:
            return 0

    def count_how_many_times(self, s_loc, s_priority):
        count = 0
        for loc in s_priority:
            if loc == s_loc:
                count += 1
        return count

from itertools import combinations
ids = ['318188984', '207406638']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zone = tuple(zone_of_control)
        self.state= initial_state
        self.state1 = []
        self.time = []
        for i in range(len(self.state)):
            self.state1.append([])
            for j in range(len(self.state[0])):
                self.state1[i].append([])
                self.state1[i][j].append(self.state[i][j])
                self.state1[i][j].append(0)
                self.state1[i][j] = (self.state1[i][j])
            self.state1[i] = (self.state1[i])
        self.state1 = (self.state1)
        self.state = self.state1
        self.order = order

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        my_list = []
        my_time = []

        for i in range(len(self.state)):
            my_list.append([])
            my_time.append([])
            for j in range(len(state[0])):
                my_list[i].append(self.state[i][j][0])
                my_time[i].append(self.state[i][j][1])

        for act in action:
            if len(act) > 0:
                if act[0] == "quarantine":
                    my_list[act[1][0]][act[1][1]] = 'Q'
                    my_time[act[1][0]][act[1][1]] = -1
                if act[0] == "vaccinate":
                    my_list[act[1][0]][act[1][1]] = 'I'
                    my_time[act[1][0]][act[1][1]] = 0

        for i in range(len(my_list)):
            for j in range(len(my_list[0])):
                if my_list[i][j] == 'S' and my_time[i][j] >= 0:
                    if i != 0:
                        if my_list[i - 1][j] == 'H' and my_time[i - 1][j] >= 0:
                            my_list[i - 1][j] = 'S'
                            my_time[i - 1][j] = 0
                    if i != len(my_list) - 1:
                        if my_list[i + 1][j] == 'H' and my_time[i + 1][j] >= 0:
                            my_list[i + 1][j] = 'S'
                            my_time[i + 1][j] = -1
                    if j != 0:
                        if my_list[i][j - 1] == 'H' and my_time[i][j - 1] >= 0:
                            my_list[i][j - 1] = 'S'
                            my_time[i][j - 1] = 0
                    if j != len(my_list[0]) - 1:
                        if my_list[i][j + 1] == 'H' and my_time[i][j + 1] >= 0:
                            my_list[i][j + 1] = 'S'
                            my_time[i][j + 1] = -1

                if my_list[i][j] == 'H':
                    my_time[i][j] += 1
                if my_list[i][j] == 'Q':
                    if my_time[i][j] >= 1:
                        my_list[i][j] = 'H'
                        my_time[i][j] = -1
                    else:
                        my_time[i][j] += 1
                if my_list[i][j] == 'S':
                    if my_time[i][j] >= 2:
                        my_list[i][j] = 'H'
                        my_time[i][j] = -1

                    else:
                        my_time[i][j] += 1

        result_state = []
        for i in range(len(my_list)):
            result_state.append([])
            for j in range(len(my_list[0])):
                result_state[i].append([])
                result_state[i][j].append(my_list[i][j])
                result_state[i][j].append(my_time[i][j])
                result_state[i][j] = tuple(result_state[i][j])
            result_state[i] = tuple(result_state[i])
        result_state = tuple(result_state)
        self.state1 = result_state
        return result_state



    def act(self, state):
        my_s = []
        my_h = []
        count = 0
        count2 = 0
        n = len(state)
        m = len(state[0])

        if self.order == 'first':
            for i in range(n):
                for j in range(m):
                    if self.state[i][j][0] == 'S':
                        if state[i][j] == 'S':
                            self.state[i][j][1] += 1
                        else:
                            self.state[i][j][1] = 0
                    if self.state[i][j][0] == 'Q':
                        if state[i][j] == 'Q':
                            self.state[i][j][1] += 1
                        else:
                            self.state[i][j][1] = 0
                    self.state[i][j][0] = state[i][j]

        if self.order == 'second':
            for i in range(n):
                for j in range(m):
                    if (i,j) in self.zone:
                        if self.state[i][j][0] == 'S':
                            if state[i][j] == 'S':
                                self.state[i][j][1] += 1
                            else:
                                self.state[i][j][1] = 0
                        if self.state[i][j][0] == 'Q':
                            if state[i][j] == 'Q':
                                self.state[i][j][1] += 1
                            else:
                                self.state[i][j][1] = 0
                        self.state[i][j][0] = state[i][j]
                    else:
                        if state[i][j] == 'S':
                            if self.state[i][j][0] == 'S':
                                self.state[i][j][1] += 1
                            else:
                                self.state[i][j][1] = 0
                        if state[i][j] == 'Q':
                            if self.state[i][j][0] == 'Q':
                                self.state[i][j][1] += 1
                            else:
                                self.state[i][j][1] = 0
                        self.state[i][j][0] = state[i][j]






        for (i,j) in self.zone:
                if state[i][j] == 'S':
                    my_s.append(("quarantine", (i, j)))
                    count += 1
                if state[i][j] == 'H':
                    my_h.append(("vaccinate", (i, j)))
                    count2 += 1

        new_s = [[()]]
        new_h = [[()]]
        if count>= 1:
            new_s.append(list(combinations(my_s, 1)))
        if count>= 2:
            new_s.append(list(combinations(my_s, 2)))
        if count2 >= 1:
            new_h.append(list(combinations(my_h, 1)))

        my_new_s=[]
        my_new_h=[]
        for i in range(len(new_s)):
            my_new_s.extend(new_s[i])

        for i in range(len(new_h)):
            my_new_h.extend(new_h[i])

        actions = []
        if len(my_new_h) == 0:
            for i in range(len(my_new_s)):
                my_list = []
                my_list.extend(my_new_s[i])
                actions.append(tuple(my_list))
        if len(my_new_s) == 0:
            for i in range(len(my_new_h)):
                my_list = []
                my_list.extend(my_new_h[i])
                actions.append(tuple(my_list))

        for i in range(len(my_new_s)):
            for j in range(len(my_new_h)):
                my_list = []
                my_list.extend(my_new_s[i])
                my_list.extend(my_new_h[j])
                actions.append(tuple(my_list))
        actions = tuple(actions)
        count0 = -9999999999
        for action in actions:
            count = 0
            for act in action:
                if len(act) == 0:
                    break
                if act[0] == 'vaccinate':
                    if (act[1][0]>0 and state[act[1][0]-1][act[1][1]] == 'S' and self.state[act[1][0]-1][act[1][1]][1] != 2):
                        count +=1
                    if      (act[1][0] < len(state)-1 and state[act[1][0]+1][act[1][1]] == 'S' and self.state[act[1][0]+1][act[1][1]][1] != 2) :
                        count+=1
                    if        (act[1][1]>0 and state[act[1][0]][act[1][1]-1] == 'S' and self.state[act[1][0]][act[1][1]-1][1] != 2) :
                        count+=1
                    if        (act[1][1] < len(state[0])-1 and state[act[1][0]][act[1][1]+1] == 'S' and self.state[act[1][0]][act[1][1]+1][1] != 2):
                        count += 1
                    x = 0.8
                    if (act[1][0] > 1 and state[act[1][0] - 2][act[1][1]] == 'S' and
                            self.state[act[1][0] - 2][act[1][1]][1] != 2):
                        count += x
                    if (act[1][0] < len(state) - 2 and state[act[1][0] + 2][act[1][1]] == 'S' and
                            self.state[act[1][0] + 2][act[1][1]][1] != 2):
                        count += x
                    if (act[1][1] > 1 and state[act[1][0]][act[1][1] - 2] == 'S' and
                            self.state[act[1][0]][act[1][1] - 2][1] != 2):
                        count += x
                    if (act[1][1] < len(state[0]) - 2 and state[act[1][0]][act[1][1] + 2] == 'S' and
                            self.state[act[1][0]][act[1][1] + 2][1] != 2):
                        count += x

                    if (act[1][0]>0 and act[1][1] > 0 and state[act[1][0]-1][act[1][1]-1] == 'S' and self.state[act[1][0]-1][act[1][1]-1][1] != 2):
                        count += x*0.5
                    if (act[1][0] < len(state)-1 and act[1][1] > 0 and state[act[1][0]+1][act[1][1]-1] == 'S' and self.state[act[1][0]+1][act[1][1]-1][1] != 2) :
                        count += x*0.5
                    if (act[1][0]>0 and act[1][1] < len(state[0])-1 and state[act[1][0]-1][act[1][1]+1] == 'S' and self.state[act[1][0]-1][act[1][1]+1][1] != 2):
                        count+=x*0.5
                    if  (act[1][0] < len(state)-1 and act[1][1] < len(state[0])-1 and state[act[1][0]+1][act[1][1]+1] == 'S' and self.state[act[1][0]+1][act[1][1]+1][1] != 2) :
                        count+=x*0.5


                i = act[1][0]
                j = act[1][1]
                y = 1.5
                a= 0.5
                if act[0] == 'quarantine':
                    if (act[1][0] > 0 and state[act[1][0] - 1][act[1][1]] == 'H'):
                        if (i-1, j) in self.zone:
                            count += 1
                        else:
                            count -= 1
                        if (act[1][0] > 1 and state[act[1][0] - 2][act[1][1]] == 'H'):
                            if (i - 2, j) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][1] < len(state[0]) - 1 and state[act[1][0] - 1][act[1][1]+1] == 'H'):
                            if (i - 1, j + 1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][1] > 0 and state[act[1][0]-1][act[1][1] - 1] == 'H'):
                            if (i - 1, j - 1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                    if (act[1][0] < len(state)-1 and state[act[1][0]+1][act[1][1]] == 'H'):
                        if (i+1, j) in self.zone:
                            count += 1
                        else:
                            count -= 1
                        if (act[1][1] > 0 and state[act[1][0] + 1][act[1][1]-1] == 'H'):
                            if (i + 1, j -1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][1] < len(state[0]) - 1 and state[act[1][0] +1 ][act[1][1] + 1] == 'H'):
                            if (i - 1, j + 1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][0] < len(state[0]) - 2 and state[act[1][0] + 2][act[1][1]] == 'H'):
                            if (i + 2, j ) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                    if (act[1][1]>0 and state[act[1][0]][act[1][1]-1] == 'H'):
                        if (i, j-1) in self.zone:
                            count += 1
                        else:
                            count -= 1
                        if (act[1][0] > 0 and state[act[1][0] - 1][act[1][1]-1] == 'H'):
                            if (i - 1, j-1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][0] < len(state) - 1 and state[act[1][0] + 1][act[1][1]-1] == 'H'):
                            if (i + 1, j - 1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][1] > 1 and state[act[1][0]][act[1][1] - 2] == 'H'):
                            if (i, j - 2) in self.zone:
                                count += y*a
                            else:
                                count -= y*a

                    if (act[1][1] < len(state[0])-1 and state[act[1][0]][act[1][1]+1] == 'H'):
                        if (i, j+1) in self.zone:
                            count += 1
                        else:
                            count -= 1
                        if (act[1][0] > 0 and state[act[1][0] - 1][act[1][1]+1] == 'H'):
                            if (i -1, j+1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][1] < len(state[0]) - 2 and state[act[1][0]][act[1][1]+2] == 'H'):
                            if (i , j + 2) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
                        if (act[1][0] < len(state) - 1 and state[act[1][0]+1][act[1][1] + 1] == 'H'):
                            if (i + 1, j + 1) in self.zone:
                                count += y*a
                            else:
                                count -= y*a
            if count > count0:
                best_act = action
                count0 = count

        return best_act



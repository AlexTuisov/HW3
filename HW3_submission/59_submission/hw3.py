
ids = ['209294503', '316597574']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control

    def process_state(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick

    def healthy_nieghboors(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h

    # return all sick nieghboors from my zone
    def sick_nieghboors(self, sick, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        s = sum(1 for neighbor in neighbors if (neighbor in sick))
        return s

    def get_health_and_sick(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick
    def count_health_in_zoc(self,state,i,j):
        list_coordinates=[]

        if i > 0:
            if 'H' in state[i - 1][j] and (i-1,j) in self.zoc :
                list_coordinates.append((i-1,j))
        if i < len(state)-1:
            if 'H' in state[i + 1][j] and (i+1,j) in self.zoc :
                list_coordinates.append((i+1,j))
        if j > 0:
            if 'H' in state[i][j - 1] and (i,j-1) in self.zoc :
                list_coordinates.append((i,j-1))

        if j < len(state[0])-1:
            if 'H' in state[i][j + 1] and (i,j+1) in self.zoc:
                list_coordinates.append((i, j + 1))
        list_coordinates_exp=[]
        list_coordinates_exp.extend(list_coordinates)
        for c in list_coordinates:
            i=c[0]
            j=c[1]
            if i > 0:
                if 'H' in state[i - 1][j] and (i-1,j) in self.zoc:
                    list_coordinates_exp.append((i - 1, j))
            if i < len(state) - 1:
                if 'H' in state[i + 1][j] and (i+1,j) in self.zoc:
                    list_coordinates_exp.append((i + 1, j))
            if j > 0:
                if 'H' in state[i][j - 1] and (i,j-1) in self.zoc:
                    list_coordinates_exp.append((i, j - 1))

            if j < len(state[0]) - 1:
                if 'H' in state[i][j + 1] and (i,j+1) in self.zoc:
                    list_coordinates_exp.append((i, j + 1))

        list_coordinates_exp=set(list_coordinates_exp)
        return len(list_coordinates_exp)




    def act(self, state):
        action = []
        healthy, sick = self.get_health_and_sick(state)

        healthy_dict = {}
        for h in healthy:
            num_sick_nieghboors = self.sick_nieghboors(sick, h)
            if num_sick_nieghboors not in healthy_dict.keys():
                healthy_dict[num_sick_nieghboors] = [h]
            else:
                healthy_dict[num_sick_nieghboors].append(h)


        try:
            sick_dict={}
            for s in sick:
                n=self.count_health_in_zoc(state,s[0],s[1])
                if n >=6:
                    if n in sick_dict:
                        sick_dict[n].append(s)
                    else:
                        sick_dict[n]=[s]
            if len(sick_dict)>0:
                max_key = max(sick_dict, key=int)
                to_quarantine = sick_dict[max_key]
                if len(to_quarantine)>1 :
                    #to_quarantine=to_quarantine[:2]
                    action.append(('quarantine', to_quarantine[0]))
                    action.append(('quarantine', to_quarantine[1]))
                else:
                    action.append(('quarantine', to_quarantine[0]))

        except KeyError:
            to_quarantine = []
        try:
            max_key = max(healthy_dict, key=int)
            to_vaccinate = healthy_dict[max_key]
            to_vaccinate=to_vaccinate[0]

        except ValueError:
            to_vaccinate = []
        if len(to_vaccinate)==0:
            return action
        action.append(('vaccinate',to_vaccinate))
        return action

import random
import utils
from itertools import combinations
import copy
import pickle
import numpy as np
ids = ['208660621', '316368679']

class Node:
    def __init__(self,state,act1=None,act2=None,depth=0,parent=None,score1=0,score2=0):
        self.state=state
        if act1:
            self.act1=act1
        elif act2:
            self.act2=act2
        else:
            self.act1,self.act2= None,None
        self.depth=depth
        self.parent=parent
        self.children=[]
        self.score1=score1
        self.score2=score2
        self.diff_score = score1-score2
        self.value=0
        self.mamas_boy=None

class Agent:
    def get_enemy_zone(self):
        enemy_zone=[]
        for i in range(len(self.state)):
            for j in range(i):
                if (i,j) not in self.zoc and not self.state[i][j] == 'U':
                    enemy_zone.append((i,j))
        return set(enemy_zone)

    def __init__(self, initial_state, zone_of_control, order):
        self.zoc=set(zone_of_control)
        self.state=initial_state
        self.turn=0
        self.order=order
        self.medics = 1
        self.police = 2
        self.rows = len(self.state)
        self.cols = len(self.state[0])
        self.transformations = {("Q", -1): ("Q", 0), ("Q", 0): ("Q", 1), ("Q", 1): ("H", 0), ("H", 0): ("H", 0), ("U", 0): ("U", 0),\
                                ("S", -1): ("S", 0), ("S", 0): ("S", 1), ("S", 1): ("S", 2), ("S", 2): ("H", 0), ("I", 0): ("I", 0)}
        self.state = [[(i, 0) for i in j] for j in initial_state]
        self.sick = [("S", 0), ("S", 1), ("S", 2)]
        self.enemy_zone = self.get_enemy_zone()
        self.score=0
        self.enemy_score=0

    def check_neighbors(self,arr, location, criteria, cols=1, non_binary=False):
        """
        checks whether any of the neigbors are sick,
         if non_binary = False : if yes return true
         if non_binary = True : returns total number of sick neighbors
        """
        if non_binary == True:
            total = 0
        neighbors_sick = False
        try:
            if arr[location[0] + 1][location[1]] in criteria: #bottom neighbor
                neighbors_sick = True
                if non_binary:
                    total += 1
        except IndexError:
            neighbors_sick = False
        if not neighbors_sick:
            try:
                if location[0] and arr[location[0] - 1][location[1]] in criteria: #top neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1] + 1) % cols and arr[location[0]][location[1] + 1] in criteria: #right neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1]) and arr[location[0]][location[1] - 1] in criteria: #left neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if non_binary:
            return total
        return neighbors_sick
    def check_my_neighbors(self, location, criteria, non_binary=False,me=True):
        """
        checks whether any of the neigbors are sick,
         if non_binary = False : if yes return true
         if non_binary = True : returns total number of sick neighbors
        """
        if me:
            zoc=self.zoc
        else:
            zoc=self.enemy_zone
        if non_binary == True:
            total = 0
        neighbors_sick = False
        try:
            if self.state[location[0] + 1][location[1]] in criteria and \
                    tuple([location[0] + 1,location[1]]) in zoc: #bottom neighbor
                neighbors_sick = True
                if non_binary:
                    total += 1
        except IndexError:
            neighbors_sick = False
        if not neighbors_sick:
            try:
                if location[0] and self.state[location[0] - 1][location[1]] in criteria and\
                        tuple([location[0] - 1,location[1]]) in zoc: #top neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1] + 1) % 1 and self.state[location[0]][location[1] + 1] in criteria and\
                        tuple([location[0],location[1]+1]) in zoc: #right neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if not neighbors_sick:
            try:
                if (location[1]) and self.state[location[0]][location[1] - 1] in criteria and\
                        tuple([location[0],location[1]-1]) in zoc: #left neighbor
                    neighbors_sick = True
                    if non_binary:
                        total += 1
            except IndexError:
                neighbors_sick = False
        if non_binary:
            return total
        return neighbors_sick

    def update_action(self, result, action):
        '''
        Update according to action, vaccinate vaccinates while quarantine goes to lockdown(quarantine)
        '''
        action_name = action[0]
        row = action[1][0]
        col = action[1][1]
        if action_name == "vaccinate":
            result[row][col] = ("I", 0)
        elif action_name == "quarantine":
            result[row][col] = ("Q", -1)
        else:
            return



    def actions(self, state,me):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file
        returns a tuple of actions in the format (("vaccinate",(R,C),("quarantine",(R,C))
        """
        all_H=[]
        s_opt={i:[] for i in range(5)}
        all_S=[]
        if me:
            for (i,j) in self.zoc:
                    if state[i][j][0]=="H" and \
                            self.check_neighbors(arr=self.state,location=[i,j],criteria=self.sick):
                        all_H.append(("vaccinate",(i,j)))
                    if state[i][j][0]=="S":
                        count_h=self.check_my_neighbors(location=[i,j],criteria=[('H',0)],me=True,non_binary=True)
                        s_opt[count_h].append(("quarantine",(i,j)))
            for i in s_opt:
                random.shuffle(s_opt[i])
            all_S=s_opt[4]+s_opt[3]
            # all_S=all_S[:max(10,len(s_opt[4])+len(s_opt[3]))]
        else:
            for (i,j) in self.enemy_zone:
                    if state[i][j][0]=="H" and \
                            self.check_neighbors(arr=self.state,location=[i,j],criteria=self.sick):
                        all_H.append(("vaccinate",(i,j)))
                    if state[i][j][0]=="S":
                        count_h=self.check_my_neighbors(location=[i,j],criteria=[('H',0)],me=True,non_binary=True)
                        s_opt[count_h].append(("quarantine", (i, j)))
            for i in s_opt:
                random.shuffle(s_opt[i])
            all_S = s_opt[4] + s_opt[3]
            # all_S = all_S[:max(10, len(s_opt[4])+len(s_opt[3]))]

        r=min(self.medics,len(all_H))
        actions_H = tuple([tuple(i) for i in combinations(all_H,r)])
        r=min(self.police,len(all_S))
        actions_S = tuple([tuple(i) for i in combinations(all_S,r)])
        all_actions=[]
        for quarantine in actions_S:
            for vaccinate in actions_H:
                all_actions.append((quarantine+vaccinate))
        return all_actions


    def temp_result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        result=pickle.loads(pickle.dumps(state,-1))
        # change according to actions
        if action:
            for act in action:
                self.update_action(result,act)
        return result

    def result(self, state):
        # change according to sick infecting healthy
        result = pickle.loads(pickle.dumps(state,-1))
        for i in range(self.rows):
            for j in range(self.cols):
                if result[i][j]==("H",0):
                    if self.check_neighbors(result,(i,j),self.sick,self.cols):
                        result[i][j]=("S",-1)

        # update according to time dynamics
        for i in range(self.rows):
            for j in range(self.cols):
                result[i][j]=self.transformations[result[i][j]]
        return result

    def update_scores(self, state):
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                self.score += 1
            if 'I' in state[i][j]:
                self.score += 1
            if 'S' in state[i][j]:
                self.score -= 1
            if 'Q' in state[i][j]:
                self.score -= 5
        for (i, j) in self.enemy_zone:
            if 'H' in state[i][j]:
                self.enemy_score += 1
            if 'I' in state[i][j]:
                self.enemy_score += 1
            if 'S' in state[i][j]:
                self.enemy_score -= 1
            if 'Q' in state[i][j]:
                self.enemy_score -= 5

    def action_score(self, state):
        score,enemy_score = 0,0
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                score += 1
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                score -= 1
            if 'Q' in state[i][j]:
                score -= 5
        for (i, j) in self.enemy_zone:
            if 'H' in state[i][j]:
                enemy_score += 1
            if 'I' in state[i][j]:
                enemy_score += 1
            if 'S' in state[i][j]:
                enemy_score -= 1
            if 'Q' in state[i][j]:
                enemy_score -= 5

        return [score,enemy_score]
    def goal(self,state):
        for i in state:
            for j in i:
                if j[0]=="S":
                    return False
        return True
    def first_min_val(self, node, alpha, beta, me=False):
        if node.depth==5 or self.goal(node.state):
            return node.diff_score
        value=np.inf
        actions2 = self.actions(node.state, me=me)
        for act2 in actions2:
            child2 = self.temp_result(node.state, act2)
            child2=self.result(child2)
            scores = self.action_score(child2)
            scores[0] += node.score1
            scores[1] += node.score2
            child2 = Node(child2, act1=node.act1, act2=act2,
                          depth=node.depth + 1, parent=node, score1=scores[0], score2=scores[1])
            node.children.append(child2)
        node.children.sort(key=lambda x:x.diff_score)
        node.children = node.children[:30//max(1,node.depth)]
        node.value=value
        for child in node.children:
            child.value=self.first_max_val(child, alpha, beta)
            if child.value<node.value:
                node.mamas_boy=child
                node.value=child.value
                value=child.value
            if value<=alpha:
                return value
            beta=min(beta,value)

        return value


    def first_max_val(self, node, alpha, beta, me=True):
        if node.depth==5 or self.goal(node.state):
            return node.diff_score
        value= -np.inf
        actions1 = self.actions(node.state, me=me)
        for act1 in actions1:
            child1 = self.temp_result(node.state, act1)
            scores=self.action_score(child1)
            child1 = Node(child1, act1=act1, act2=None,
                          depth=node.depth + 1, parent=node, score1=scores[0], score2=scores[1])
            node.children.append(child1)
        node.children.sort(key=lambda x:x.diff_score,reverse=True)
        node.children = node.children[:30//max(1,node.depth)]
        node.value = value
        for child in node.children:
            child.value = self.first_min_val(child, alpha, beta)
            if child.value > node.value:
                node.mamas_boy = child
                node.value = child.value
                value = child.value
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def second_min_val(self, node, alpha, beta, me=False):
        if node.depth == 4 or self.goal(node.state):
            return node.diff_score
        value = np.inf
        actions2 = self.actions(node.state, me=me)
        for act2 in actions2:
            child2 = self.temp_result(node.state, act2)
            scores=self.action_score(child2)
            child2 = Node(child2, act1=None, act2=act2,
                          depth=node.depth + 1, parent=node, score1=scores[0], score2=scores[1])
            node.children.append(child2)
        node.children.sort(key=lambda x:x.diff_score)
        node.children = node.children[:45]
        node.value = value
        for child in node.children:
            child.value = self.second_max_val(child, alpha, beta)
            if child.value < node.value:
                node.mamas_boy = child
                node.value = child.value
                value = child.value
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value

    def second_max_val(self, node, alpha, beta, me=True):
        if node.depth == 4 or self.goal(node.state):
            return node.diff_score
        value = -np.inf
        actions1 = self.actions(node.state, me=me)
        for act1 in actions1:
            child1 = self.temp_result(node.state, act1)
            child1=self.result(child1)
            scores = self.action_score(child1)
            scores[0] += node.score1
            scores[1] += node.score2
            child1 = Node(child1, act1=act1, act2=None,
                          depth=node.depth + 1, parent=node, score1=node.score1, score2=node.score2)
            node.children.append(child1)

        node.children.sort(key=lambda x:x.diff_score, reverse=True)
        node.children=node.children[:45]
        node.value = value
        for child in node.children:
            child.value = self.second_min_val(child, alpha, beta)
            if child.value > node.value:
                node.mamas_boy = child
                node.value = child.value
                value = child.value
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def first_best_action(self,node:Node):
        node.value=self.first_max_val(node, -np.inf, np.inf)
        if node.mamas_boy:
            return node.mamas_boy.act1



    def second_best_action(self,node:Node):
        node.value=self.second_max_val(node, -np.inf, np.inf)
        if node.mamas_boy:
            return node.mamas_boy.act1

    def convert_state(self,state):
        temp_state=pickle.loads(pickle.dumps(state,-1))
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j]=='I':
                    temp_state[i][j]=('I',0)
                elif state[i][j]=='U':
                    temp_state[i][j]=('U',0)
                elif state[i][j]=='H':
                    temp_state[i][j]=('H',0)
                elif state[i][j]=='S' and self.state[i][j][0]=='S':
                    temp_state[i][j]=self.transformations[self.state[i][j]]
                elif state[i][j]=='Q' and self.state[i][j][0]=='Q':
                    temp_state[i][j]=self.transformations[self.state[i][j]]
                elif state[i][j]=='S':
                    temp_state[i][j] = ('S', 0)
                elif state[i][j]=='Q':
                    temp_state[i][j] = ('Q', 0)
        self.state=temp_state
    def act(self, state):
        if self.turn:
            self.update_scores(state)
            self.convert_state(state)
        if self.order=='first':
            action=self.first_best_action(Node(self.state,score1=self.score,score2=self.enemy_score))
        else:
            action=self.second_best_action(Node(self.state,score1=self.score,score2=self.enemy_score))
        self.turn += 1
        if not action:
            action = []
            healthy = set()

            for (i, j) in self.zoc:
                if 'H' in state[i][j]:
                    healthy.add((i, j))
            try:
                to_vaccinate = random.sample(healthy, 1)
            except ValueError:
                to_vaccinate = []
            for item in to_vaccinate:
                action.append(('vaccinate', item))

        return action

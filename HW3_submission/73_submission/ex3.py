import random
import time
from copy import deepcopy
from itertools import product
import math
import numpy as np
DIMENSIONS = (10, 10)
ids = ['313136491', '205684269']


class Node:

    def __init__(self, state, parent=None, action=None, player=0, H_list=[], S_list=[], score=0, problem=None):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.player = player
        self.H_list = H_list
        self.S_list = S_list
        self.parent = parent
        self.action = action
        self.wins = 0
        self.games_played = 0
        self.problem = problem
        self.actions_to_play = problem.actions(self.H_list,self.S_list,self.player)
        self.unvisited = deepcopy(self.actions_to_play)
        self.children_UCT = {}
        self.children_UCT[self.actions_to_play[0]] = 0
        self.children_scores = {}
        self.children = {}
        self.score = score
        if parent:
            self.depth = parent.depth+1
        else:
            self.depth=0

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def child_node(self, action,update):
        if action in self.children.keys():
            return self.children[action]
        score = self.score
        if self.player==update:
            next,H,S, score = self.problem.score(self.state, action,self.H_list,self.S_list)
            self.score+=score
            score = self.score
        else:
            next,H,S = self.problem.apply_action(self.state, action, self.H_list, self.S_list)
        node =Node(next, self, action,
                    1-self.player,H,S, score, self.problem)
        self.children[action]=node
        return node

    def is_terminal(self):
        if self.S_list:
            return False
        return True

    def best_UCT (self):
        best_action = max(self.children_UCT.items(), key = lambda k : k[1])[0]
        return self.children[best_action]

    def best_child (self):
        best_action = self.actions_to_play[0]
        value= float('-inf')
        for k,v in self.children_scores.items():
            temp_val =v[0]*((v[1]/v[2])+1)
            if temp_val>value:
                best_action=k
                value=temp_val
        return best_action


    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class specific_problem:
    def __init__(self, zoc):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.zoc = zoc
        self.police_number = 2
        self.medical_number = 1

    def find_action_player_0 (self,H_list,S_list):
        vaccine_1 =[]
        quarantine_1 = []
        for h in H_list:
            if h in self.zoc:
                i=h[0]
                j=h[1]
                heuristic =-0.25
                if (i-1,j) in S_list:
                    heuristic-=1.5
                if (i+1,j) in S_list:
                    heuristic-=1.5
                if (i,j-1) in S_list:
                    heuristic-=1.5
                if (i,j+1) in S_list:
                    heuristic-=1.5
                vaccine_1.append(((('vaccinate',h),),heuristic))
        for s in S_list:
            if s in self.zoc:
                i=s[0]
                j=s[1]
                heuristic =1.25  ##1.25
                if (i-1,j) in H_list:
                    if (i-1,j) not in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i+1,j) in H_list:
                    if (i+1,j) not in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i,j-1) in H_list:
                    if (i,j-1) not in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i,j+1) in H_list:
                    if (i,j+1) not in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                quarantine_1.append(((('quarantine',s),),heuristic))
        if quarantine_1 and vaccine_1:
            comb = [((x[0][0][0],x[1][0][0]),x[0][1]+x[1][1]) for x in list(product(quarantine_1,vaccine_1))] + vaccine_1 + [(((),0))]
            final= [x[0] for x in sorted(comb , key=lambda k: k[1])]
        elif quarantine_1:
            final= [x[0] for x in sorted(quarantine_1+[(((),0))] , key=lambda k: k[1])]
        elif vaccine_1:
            final= [x[0] for x in sorted(vaccine_1+[(((),0))] , key=lambda k: k[1])]
        else:
            final = [()]
        if len(final)<=50:
            return final[0:10]
        else:
            upper_bound = int(np.floor(len(final)*0.2))
            return final[0:upper_bound]


    def find_action_player_1 (self,H_list,S_list):
        vaccine_1 =[]
        quarantine_1 = []
        for h in H_list:
            if h not in self.zoc:
                i=h[0]
                j=h[1]
                heuristic =-0.25
                if (i-1,j) in S_list:
                    heuristic-=1.5
                if (i+1,j) in S_list:
                    heuristic-=1.5
                if (i,j-1) in S_list:
                    heuristic-=1.5
                if (i,j+1) in S_list:
                    heuristic-=1.5
                vaccine_1.append(((('vaccinate',h),),heuristic))
        for s in S_list:
            if s not in self.zoc:
                i=s[0]
                j=s[1]
                heuristic =1.25  #1.25
                if (i-1,j) in H_list:
                    if (i-1,j) in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i+1,j) in H_list:
                    if (i+1,j) in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i,j-1) in H_list:
                    if (i,j-1) in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                if (i,j+1) in H_list:
                    if (i,j+1) in self.zoc:
                        heuristic+=1
                    else:
                        heuristic-=0.5
                quarantine_1.append(((('quarantine',s),),heuristic))
        if quarantine_1 and vaccine_1:
            comb = [((x[0][0][0],x[1][0][0]),x[0][1]+x[1][1]) for x in list(product(quarantine_1,vaccine_1))] + vaccine_1 + [(((),0))]
            final= [x[0] for x in sorted(comb , key=lambda k: k[1])]
        elif quarantine_1:
            final= [x[0] for x in sorted(quarantine_1+[(((),0))] , key=lambda k: k[1])]
        elif vaccine_1:
            final= [x[0] for x in sorted(vaccine_1+[(((),0))] , key=lambda k: k[1])]
        else:
            final = [()]
        if len(final)<=50:
            return final[0:10]
        else:
            upper_bound = int(np.floor(len(final)*0.2))
            return final[0:upper_bound]

    def actions(self, H_list, S_list, player):
        if player==0:
            return self.find_action_player_0(H_list,S_list)
        else:
            return self.find_action_player_1(H_list,S_list)


    def apply_action(self,state,actions, H_list,S_list):
        new_H_list = deepcopy(H_list)
        new_S_list = deepcopy(S_list)
        new_state = list(state)
        for atomic_action in actions:
            effect, i,j = atomic_action[0], atomic_action[1][0] , atomic_action[1][1]
            new_state[i] = list(new_state[i])
            if 'v' in effect:
                new_state[i][j] = 'I'
                new_H_list.remove((i,j))
            else:
                new_state[i][j]= 'Q0'
                new_S_list.remove((i,j))
            new_state[i]=tuple(new_state[i])
        return tuple(new_state), new_H_list, new_S_list

    def score(self, cur_state, action, H,S):
        state, H_list,S_list = self.apply_action(cur_state, action,H,S)
        new_S_list = []
        new_H_list = []
        player_0_score = 0
        player_1_score = 0
        state = list(state)
        new_state=[]
        # virus spread
        for s in S_list:
            i=s[0]
            j=s[1]
            if (i-1,j) in H_list:
                state[i-1]=list(state[i-1])
                state[i-1][j]='S0'
            if (i+1,j) in H_list:
                state[i+1]=list(state[i+1])
                state[i+1][j]='S0'
            if (i,j-1) in H_list:
                state[i]=list(state[i])
                state[i][j-1]='S0'
            if (i,j+1) in H_list:
                state[i]=list(state[i])
                state[i][j+1]='S0'
        for i in range (DIMENSIONS[0]):
            row = list(state[i])
            for j in range (DIMENSIONS[1]):
                tile_score = 0
                if 'S' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 3:
                        row[j] = 'S' + str(turn + 1)
                        new_S_list += [(i,j)]
                        tile_score = -1
                    else:
                        row[j] = 'H'
                        new_H_list += [(i,j)]
                        tile_score = 1
                elif 'H' in state[i][j]:
                    new_H_list += [(i,j)]
                    tile_score = 1
                elif 'Q' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 2:
                        row[j] = 'Q' + str(turn + 1)
                        tile_score = -5
                    else:
                        row[j] = 'H'
                        new_H_list += [(i,j)]
                        tile_score = 1
                elif 'I' in state[i][j]:
                    tile_score = 1
                if (i,j) in self.zoc:
                    player_0_score += tile_score
                else:
                    player_1_score += tile_score
            new_state.append(tuple(row))
        return tuple(new_state), new_H_list,new_S_list, player_0_score-player_1_score

    def termination_test(self,S_list):
        if S_list:
            return False
        return True

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.start = time.time()
        self.zoc = zone_of_control
        if order=='first':
            self.update=1
        else:
            self.update=0
        self.GameProblem = specific_problem(zone_of_control)
        self.depth = 8
        self.root = self.create_root_node(initial_state,1-self.update)
        self.round = 0
        self.cur_state_of_game = []
        self.cur_H_list = []
        self.cur_S_list = []
        self.t =0
        self.max_time = 58-(time.time()-self.start)
        if self.update==1:
            self.monte_carlo_tree_search(self.root)


    def act(self, state):
        self.start = time.time()
        self.round +=1
        if self.round==1:
            self.state_to_tuple_first_round(state)
            if self.update==1:
                node = self.root
            else:
                node=Node(self.cur_state_of_game,None,None,0,self.cur_H_list,self.cur_S_list,0,self.GameProblem)
        else:
            self.state_to_tuple_other_round(state)
            node = Node(self.cur_state_of_game,None,None,0,self.cur_H_list,self.cur_S_list,0,self.GameProblem)
        if self.update==1:
            self.depth=2
        else:
            self.depth=3
        self.max_time = 4.25-(time.time()-self.start)
        try:
            self.monte_carlo_tree_search(node)
            return node.best_child()
        except:
            return node.best_child()


    def create_root_node(self,state,player):
        H_list = []
        S_list = []
        state_as_list = []
        for i in range(DIMENSIONS[0]):
            j_list = []*DIMENSIONS[1]
            for j in range(DIMENSIONS[1]):
                x =state[i][j]
                if state[i][j]=='H':
                    H_list.append((i,j))
                if 'S' in state[i][j]:
                    x='S1'
                    S_list.append((i,j))
                j_list.append(x)
            state_as_list.append(tuple(j_list))
        tuple_state = tuple(state_as_list)
        return Node(tuple_state,None,None,player,H_list,S_list,0,self.GameProblem)

    def state_to_tuple_first_round (self,state):
        new_tuple = []
        for i in range(DIMENSIONS[0]):
            row = state[i]
            for j in range(DIMENSIONS[1]):
                if row[j]=='S':
                    row[j]='S1'
                    self.cur_S_list.append((i,j))
                elif row[j]=='H':
                    self.cur_H_list.append((i,j))
                elif row[j]=='Q':
                    row[j]='Q0'
            new_tuple.append(tuple(row))
        self.cur_state_of_game = tuple(new_tuple)

    def state_to_tuple_other_round (self,state):
        new_tuple = []
        temp_S = []
        temp_H = []
        for i in range(DIMENSIONS[0]):
            row = state[i]
            for j in range(DIMENSIONS[1]):
                cur_tile = self.cur_state_of_game[i][j]
                if row[j]=='S':
                    temp_S.append((i,j))
                    if 'S' in cur_tile:
                        row[j]='S'+str(int(cur_tile[1])+1)
                    else:
                        row[j] = 'S1'
                elif row[j]=='H':
                    temp_H.append((i,j))
                elif row[j] =='Q':
                    if 'Q' in cur_tile:
                        row[j]='Q'+str(int(cur_tile[1])+1)
                    else:
                        if self.update==0:
                            row[j] = 'Q0'
                        else:
                            row[j]='Q1'
            new_tuple.append(tuple(row))
        self.cur_state_of_game = tuple(new_tuple)
        self.cur_S_list = temp_S
        self.cur_H_list = temp_H

    def monte_carlo_tree_search(self, root):
        while time.time()-self.start<self.max_time:
            self.t+=1
            leaf = self.traverse(root)
            if time.time()-self.start>self.max_time:
                return
            simulation_win,simulation_result, node = self.rollout(leaf)
            if time.time()-self.start>self.max_time:
                return
            self.backpropagate(node,simulation_win, simulation_result)

    # function for node traversal
    def traverse(self,node):
        if node.unvisited:
            action = node.unvisited[0]
            node.unvisited.remove(action)
            if time.time()-self.start>=self.max_time:
                return  node
            new_node = node.child_node(action, self.update)
            return new_node
        else:
            while not node.unvisited:
                if time.time()-self.start>=self.max_time:
                    return node
                node = node.best_UCT()
            action = node.unvisited[0]
            node.unvisited.remove(action)
            new_node = node.child_node(action, self.update)
            return new_node
            # in case no children are present / node is terminal
    # function for the result of the simulation

    def rollout(self,node):
        while time.time()-self.start<self.max_time and node.depth<=self.depth and not node.is_terminal():
            node = self.rollout_policy(node)
        return 1 if node.score>0 else 0,node.score, node

    # function for randomly selecting a child node
    def rollout_policy(self,node):
        random_action = random.sample(node.actions_to_play,1)[0]
        new_node = node.child_node(random_action,self.update)
        return new_node

    # function for backpropagation
    def backpropagate(self,node, win,result,child_score=0, child_action = None, child_uct=0):
        child_score, child_uct = self.update_stats(node, win, result, child_score, child_action, child_uct)
        if time.time()-self.start>=self.max_time or not node.parent:
            return
        self.backpropagate(node.parent,win,result,child_score, node.action,child_uct)

    def update_stats(self, node, win, result, child_score = 0, child_action=None, child_UCT=0):
        node.wins += win
        node.games_played += 1
        UCT=0 if self.t<1 else  math.sqrt(2*math.log(self.t)/node.games_played)
        if child_action:
            node.children_UCT [child_action] =child_score + child_UCT
            if child_action not in node.children_scores.keys():
                node.children_scores[child_action] = (result,node.wins,node.games_played)
            else:
                cur_score = node.children_scores[child_action]
                node.children_scores[child_action] = (cur_score[0]+result, node.wins ,node.games_played)
        return node.wins/node.games_played, UCT
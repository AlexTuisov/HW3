import random
import numpy as np
import itertools

ids = ['931161715', '931158984']
#1 medics, 2 police team


def bestAction(init, zone):
    maxVac = 0
    actionVac = None
   # actionQuar = None
    for z in zone:
        if init[z[0]][z[1]] == 'H':
            AroundNumber = areaCheck(init,z[0],z[1])
            if AroundNumber >= maxVac:
                maxVac = AroundNumber
                actionVac = ("vaccinate",(z[0],z[1]))

       # if init[z[0]][z[1]] == 'S':
    return actionVac



def IsInMap(map,i,j):
    if i >=0 and i<len(map) and j>=0 and j<len(map[0]):
        return True
    else:
        return False


#retourne le nombre de s qu'il y a autour d'une case
def areaCheck(state,i,j):
    nb=0

    if IsInMap(state,i+1,j):
        if state[i+1][j] == 'S':
            nb=+1
    if IsInMap(state,i-1,j):
        if state[i-1][j] == 'S':
            nb=+1
    if IsInMap(state,i,j+1):
        if state[i][j+1] == 'S':
            nb=+1
    if IsInMap(state,i,j-1):
        if state[i][j-1] == 'S':
            nb=+1
    return nb

class Agent:
    def __init__(self, initial_state,  zone_of_control, order):

        self.zoc = zone_of_control


    def act(self, state):

        listOfAction = []
        action = bestAction(state, self.zoc)
        if action == None:

            action = []
            print("noneeee")
            return ()
        listOfAction.append(action)
        return listOfAction
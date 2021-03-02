import random

ids = ['206609810']

class Agent:
  def __init__(self, initial_state, zone_of_control, order):
    self.zoc = zone_of_control
    
  def getScoreAfterTurnApplied(self, state):
    score = 0;
    
    copiedState = state[:]
    
    for (i,j) in self.zoc:
      if state[i][j] == 'H':
        if ((i + 1) < 10 and state[i + 1][j] == 'S') or ((i - 1) > 0 and state[i - 1][j] == 'S') or ((j + 1) < 10 and state[i][j + 1] == 'S') or ((j - 1) > 0 and state[i][j - 1] == 'S'):
          copiedState[i][j] = 'S'
          
    for (i, j) in self.zoc:
      if copiedState[i][j] == 'H':
        score += 1
      if copiedState[i][j] == 'I':
        score += 1
      if copiedState[i][j] == 'S':
        score -= 1
      if copiedState[i][j] == 'Q':
        score -= 5
    return score
    
  def act(self, state):
    actions = self.getActions(state)
    print(actions)
    return actions
    
  def getActions(self, state):
    actions = [];
    
    bestMoveToVaccinate = self.getBestMove(state, 'H', 'I', None)
    if bestMoveToVaccinate:
      actions.append(('vaccinate', (bestMoveToVaccinate[0], bestMoveToVaccinate[1])))
    bestMoveToQuarantine1 = self.getBestMove(state, 'S', 'Q', None)
    if bestMoveToQuarantine1:
      actions.append(('quarantine', (bestMoveToQuarantine1[0], bestMoveToQuarantine1[1])))
    bestMoveToQuarantine2 = self.getBestMove(state, 'S', 'Q', bestMoveToQuarantine1)
    if bestMoveToQuarantine2:
      actions.append(('quarantine', (bestMoveToQuarantine2[0], bestMoveToQuarantine2[1])))          
      
    return actions
    
  def getBestMove(self, state, target, action, coordsToIgnore):
    
    score = self.getScoreAfterTurnApplied(state)
    
    copiedState = state[:]
    bestAction = []
    anyLegalAction = []
    for (i, j) in self.zoc:
      if copiedState[i][j] == target and (not coordsToIgnore or (i != coordsToIgnore[0] and j != coordsToIgnore[1])):
        
        copiedState[i][j] = action
        scoreAfterActionApplied = self.getScoreAfterTurnApplied(copiedState)

        anyLegalAction = [i, j]
        
        if scoreAfterActionApplied >= score:
          score = scoreAfterActionApplied
          bestAction = [i, j]
          
    if bestAction:
      return bestAction
    else:
      return anyLegalAction
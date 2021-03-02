import random
import numpy as np
import itertools

ids = ['342457421']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):

        self.zoc = zone_of_control
        self.shape = (len(initial_state), len(initial_state[0]))

    def act(self, state):
        action = self.chose_best_action(state)
        return action

    def is_in_map(self, i, j):
        if 0 <= i < self.shape[0] and 0 <= j < self.shape[1]:
            return True
        else:
            return False

    def process_state(self, state):
        healthy = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append((i, j))
        return healthy

    def sick_process_state(self, state):
        sicks = []
        for (i, j) in self.zoc:
            if 'S' in state[i][j]:
                sicks.append((i, j))
        return sicks

    def healthy_heuristic(self, state, i, j):
        val = 0
        val2 =0
        if self.is_in_map(i + 1, j):
            if state[i + 1][j] == 'S':
                val += 1
            x = i + 1
            y = j
            if self.is_in_map(x + 1, y):
                if state[x + 1][y] == 'S':
                    val2 += 0.5

        if self.is_in_map(i - 1, j):
            if state[i - 1][j] == 'S':
                val += 1
            x = i - 1
            y = j
            if self.is_in_map(x - 1, y):
                if state[x - 1][y] == 'S':
                    val2 += 0.5

        if self.is_in_map(i, j + 1):
            if state[i][j + 1] == 'S':
                val += 1
            x = i
            y = j + 1
            if self.is_in_map(x + 1, y):
                if state[x + 1][y] == 'S':
                    val2 += 0.5
            if self.is_in_map(x - 1, y):
                if state[x - 1][y] == 'S':
                    val2 += 0.5
            if self.is_in_map(x, y + 1):
                if state[x][y + 1] == 'S':
                    val2 += 0.5

        if self.is_in_map(i, j - 1):
            if state[i][j - 1] == 'S':
                val += 1
            x = i
            y = j - 1
            if self.is_in_map(x + 1, y):
                if state[x + 1][y] == 'S':
                    val2 += 0.5
            if self.is_in_map(x - 1, y):
                if state[x - 1][y] == 'S':
                    val2 += 0.5
            if self.is_in_map(x, y - 1):
                if state[x][y + 1] == 'S':
                    val2 += 0.5

        return val

    def sick_heuristic(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h

    def chose_best_action(self, state):
        healthy = self.process_state(state)
        max_score = -1000

        if len(healthy) == 0:
            action = []
            sicks = self.sick_process_state(state)
            sicks.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
            try:
                to_quarantine = (sicks[:1])
            except KeyError:
                to_quarantine = []
            for item in to_quarantine:
                action.append(('quarantine', item))
            return action
        maxh = healthy[0]
        for ht in healthy:
            temp_val = self.healthy_heuristic(state, ht[0], ht[1])
            if temp_val > max_score:
                max_score = temp_val
                maxh = ht
        act = ("vaccinate", (maxh[0], maxh[1]))
        final_action = [act]
        return final_action

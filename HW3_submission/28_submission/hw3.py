import random
from copy import deepcopy
import itertools
import math
import time

ids = ['208241760', '205567514']
DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
n_medics = 1
n_police = 2


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.n_rows = len(initial_state)
        self.n_cols = len(initial_state[0])
        # self.state = deepcopy(initial_state)
        zone = [[-1] * len(initial_state[0]) for _ in range(len(initial_state))]
        rival_zone = [[1] * len(initial_state[0]) for _ in range(len(initial_state))]
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if initial_state[i][j] == 'U':
                    zone[i][j] = 0
                    rival_zone[i][j] = 0
        for index in zone_of_control:
            zone[index[0]][index[1]] = 1
            rival_zone[index[0]][index[1]] = -1
        self.zone = zone
        self.rival_zone = rival_zone
        self.order = order
        time_map = [[0] * self.n_cols for _ in range(self.n_rows)]
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if initial_state[i][j] == 'S':
                    time_map[i][j] = 3 - 1
                elif initial_state[i][j] == 'Q':
                    time_map[i][j] = 2 - 1
        self.previous_node = Node(initial_state, time_map)
        self.problem = Problem(self.previous_node, self.zone, self.order)
        self.is_initial = True

        rival_order = 'second' if order == 'first' else 'first'
        # self.rival = SimpleAgent(initial_state, rival_zoc, rival_order)
        self.hue_agent = HeuristicAgent(initial_state, zone_of_control, order)
        # self.rival = Agent(initial_state, rival_zoc, rival_order)
        self.rival_problem = Problem(self.previous_node, self.rival_zone, rival_order)

    def act(self, state):
        t1 = time.time()
        too_many_actions = False
        max_actions = 3000

        # infer current time-map
        cur_time_map = self.problem.update_time_map(self.previous_node, state, self.is_initial)
        if self.is_initial:
            self.is_initial = False
        # build Node from state, time-map
        cur_node = Node(state, cur_time_map)

        # if we are player1
        if self.order == 'first':
            actions = self.problem.actions(cur_node)

            max_f = -math.inf
            max_action = ()
            for action in actions:
                t2 = time.time()
                if t2 - t1 > 4.5:
                    self.previous_node = self.problem.result(cur_node, max_action)
                    return max_action
                new_node = self.problem.result(cur_node, action)
                rival_actions = self.rival_problem.rival_actions(new_node)
                too_many_actions = False
                if len(actions) * len(rival_actions) > max_actions:
                    too_many_actions = True

                min_f = -math.inf
                min_action = ()
                for rival_action in rival_actions:
                    new_node_rival = self.problem.result(new_node, rival_action)
                    new_node_rival = self.problem.run_dynamics(new_node_rival)

                    # #add from here:
                    # actions2 = self.problem.actions(new_node_rival)
                    #
                    # max_f2 = -math.inf
                    # max_action2 = ()
                    # for action2 in actions2:
                    #     new_node2 = self.problem.result(new_node_rival, action2)
                    #     rival_actions2 = self.rival_problem.rival_actions(new_node2)
                    #
                    #     min_f2 = -math.inf
                    #     min_action2 = ()
                    #     for rival_action2 in rival_actions2:
                    #         new_node_rival2 = self.problem.result(new_node2, rival_action2)
                    #         new_node_rival2 = self.problem.run_dynamics(new_node_rival2)
                    #
                    #         f_rival2 = new_node_rival2.f(self.rival_problem, depth=2)
                    #         if f_rival2 > min_f2:
                    #             min_f2 = f_rival2
                    #             min_action2 = rival_action2
                    #
                    # new_node = self.problem.result(new_node, min_action)
                    # new_node = self.problem.run_dynamics(new_node)
                    #
                    # #until here

                    depth = 2
                    if too_many_actions:
                        depth = 1
                    f_rival = new_node_rival.f(self.rival_problem, depth)
                    if f_rival > min_f:
                        min_f = f_rival
                        min_action = rival_action
                new_node = self.problem.result(new_node, min_action)
                new_node = self.problem.run_dynamics(new_node)

                depth = 2
                if too_many_actions:
                    depth = 1
                f_new_node = new_node.f(self.problem, depth)

                if f_new_node > max_f:
                    max_f = f_new_node
                    max_action = action
            self.previous_node = self.problem.result(cur_node, max_action)
            return max_action

        # if we are player2
        else:
            actions = self.problem.actions(cur_node)
            max_f = -math.inf
            max_action = ()
            for action in actions:
                t2 = time.time()
                if t2 - t1 > 4.5:
                    self.previous_node = self.problem.result(cur_node, max_action)
                    return max_action
                new_node = self.problem.result(cur_node, action)
                new_node = self.problem.run_dynamics(new_node)
                r = new_node.reward(self.problem)
                rival_actions = self.rival_problem.rival_actions(new_node)

                too_many_actions = False
                if len(actions) * len(rival_actions) > max_actions:
                    too_many_actions = True

                min_h = -math.inf
                min_action = ()
                for rival_action in rival_actions:
                    new_node_rival = self.problem.result(new_node, rival_action)
                    hue_action = self.hue_agent.act(new_node_rival.state_map)
                    new_node_hue = self.problem.result(new_node_rival, hue_action)
                    new_node_hue = self.problem.run_dynamics(new_node_hue)

                    depth = 2
                    if too_many_actions:
                        depth = 1
                    h_rival = new_node_hue.h(self.rival_problem, depth)
                    if h_rival > min_h:
                        min_h = h_rival
                        min_action = rival_action
                h = -min_h
                f_new_node = r + h
                if f_new_node > max_f:
                    max_f = f_new_node
                    max_action = action
            self.previous_node = self.problem.result(cur_node, max_action)
            return max_action

        pass

    def built_tree(self):
        pass


class Problem:
    def __init__(self, init_node, zone, order):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        self.n_rows = len(init_node.state_map)
        self.n_cols = len(init_node.state_map[0])
        # time_map = [[0]*self.n_cols for _ in range(self.n_rows)]
        # for i in range(self.n_rows):
        #     for j in range(self.n_cols):
        #         if initial['map'][i][j] == 'S':
        #             time_map[i][j] = 3 - 1
        #         elif initial['map'][i][j] == 'Q':
        #             time_map[i][j] = 2 - 1
        # time_map = tuple([tuple(x) for x in time_map])
        # initial['time_map'] = time_map
        # self.initial = tuple(initial.values()) #todo: tuple?
        self.zone = zone
        self.order = order
        # self.init_node = init_node

    def actions(self, node):
        # state is the states map (without countdown)
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = node.state_map

        healthy = Problem.find_populations_healthy(state, n_medics, self.zone)
        healthy = [index for index in healthy if self.zone[index[0]][index[1]] == 1]  # in our coz
        if len(healthy) == 0:
            healthy = Problem.find_populations(state, 'H')
            healthy = [index for index in healthy if self.zone[index[0]][index[1]] == 1]  # in our coz
        medics_options = Problem.find_all_combinations(healthy, n_medics)
        medics_options = [tuple([("vaccinate", option[i]) for i in range(len(option))]) for option in
                          medics_options]

        # sick = Problem.find_populations(state, 'S')
        sick = Problem.find_populations_sick_2(state, 'S', self.zone)
        sick_need = int(math.sqrt((2*120)/len(medics_options)))
        if len(sick) < sick_need:
            sick1 = Problem.find_populations_sick_1(state, 'S', self.zone)
            sick += random.sample(sick1, min(sick_need-len(sick), len(sick1)))
        police_options = Problem.find_all_combinations(sick, n_police)
        police_options = [tuple([("quarantine", option[i]) for i in range(len(option))]) for option in
                          police_options]
        res = []
        # merge
        for m_option in medics_options:
            for p_option in police_options:
                res.append(m_option + p_option)
        res_need = 175
        if len(res) > res_need:
            random.shuffle(res)
            res = res[:res_need]
        return res

    def rival_actions(self, node):
        # state is the states map (without countdown)
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        state = node.state_map
        # sick = Problem.find_populations(state, 'S')
        healthy = Problem.find_populations_healthy(state, n_medics, self.zone)
        healthy = [index for index in healthy if self.zone[index[0]][index[1]] == 1]  # in our coz
        if len(healthy) == 0:
            healthy = Problem.find_populations(state, 'H')
            healthy = [index for index in healthy if self.zone[index[0]][index[1]] == 1]  # in our coz
        medics_options = Problem.find_all_combinations(healthy, n_medics)
        medics_options = [tuple([("vaccinate", option[i]) for i in range(len(option))]) for option in
                          medics_options]

        sick = Problem.find_populations_sick_2(state, 'S', self.zone)
        sick = [index for index in sick if self.zone[index[0]][index[1]] == 1]  # in our coz
        police_options = Problem.find_all_combinations(sick, n_police)
        police_options = [tuple([("quarantine", option[i]) for i in range(len(option))]) for option in
                          police_options]
        res = []
        # merge
        for m_option in medics_options:
            for p_option in police_options:
                if len(m_option) + len(p_option) != 0:
                    res.append(m_option + p_option)
        res_need = 40
        random.shuffle(res)
        return res[:res_need]

    def run_dynamics(self, node):
        new_map = [list(x) for x in node.state_map]
        new_time_map = [list(x) for x in node.time_map]

        # step 2: spread the virus
        sick = Problem.find_populations(new_map, 'S')
        for sick_pop in sick:
            for direc in DIRECTIONS:
                i = sick_pop[0] + direc[0]
                j = sick_pop[1] + direc[1]

                if 0 <= i < self.n_rows and 0 <= j < self.n_cols:  # in bounds
                    if new_map[i][j] == 'H':
                        new_map[i][j] = 'S'
                        new_time_map[i][j] = 3

        # step 3: sickness/quarantine expires and run time
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if new_map[i][j] in ['S', 'Q']:
                    if new_time_map[i][j] == 0:  # time expired
                        new_map[i][j] = 'H'
                    else:
                        new_time_map[i][j] -= 1
        result_node = Node(new_map, new_time_map)
        return result_node

    def result(self, node, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        new_map = [list(x) for x in node.state_map]
        new_time_map = [list(x) for x in node.time_map]

        # step 1: do action
        for item in action:
            i = item[1][0]
            j = item[1][1]
            if item[0] == 'vaccinate':
                assert new_map[i][j] == 'H'
                new_map[i][j] = 'I'  # 'H' => 'I'
                # new_time_map is 0 anyway
            elif item[0] == 'quarantine':
                assert new_map[i][j] == 'S'
                new_map[i][j] = 'Q'  # 'S' => 'Q'
                new_time_map[i][j] = 2

        result_node = Node(new_map, new_time_map)
        return result_node

    @staticmethod
    def find_combinations(s, n):
        return list(itertools.combinations(s, n))

    @staticmethod
    def findsubsets(s, n):
        return list(itertools.combinations(s, n))

    @staticmethod
    def find_all_combinations(s, n):
        # n is number of handlers
        # s is list of optional patients
        all_options = []
        for i in range(min(n, len(s)) + 1):
            all_options += list(itertools.combinations(s, i))
        return all_options

    @staticmethod
    def find_populations_healthy(state_map, n_medics, zoc):
        res_s = []
        res_q_s = []
        n_rows = len(state_map)
        n_cols = len(state_map[0])
        for i in range(n_rows):
            for j in range(n_cols):
                if state_map[i][j] == 'H':
                    for dirc in DIRECTIONS:
                        out = False
                        i2 = i + dirc[0]
                        j2 = j + dirc[1]
                        if 0 <= i2 < n_rows and 0 <= j2 < n_cols:
                            if state_map[i2][j2] == 'S':
                                res_s.append((i, j))
                                break
                            elif state_map[i2][j2] == 'Q':
                                for direc2 in DIRECTIONS:
                                    i3 = i2 + direc2[0]
                                    j3 = j2 + direc2[1]
                                    if 0 <= i3 < n_rows and 0 <= j3 < n_cols and state_map[i3][j3] == 'S':
                                        res_q_s.append((i, j))
                                        out = True
                                        break
                                if out:
                                    break
        if len(res_s) < n_medics:
            return res_s + res_q_s
        return res_s

    @staticmethod
    def find_populations_sick_1(state_map, n_police, zoc):
        res_s = []
        n_rows = len(state_map)
        n_cols = len(state_map[0])
        for i in range(n_rows):
            for j in range(n_cols):
                if state_map[i][j] == 'S' and zoc[i][j] == 1:
                    count = 0
                    for dirc in DIRECTIONS:
                        i2 = i + dirc[0]
                        j2 = j + dirc[1]
                        if 0 <= i2 < n_rows and 0 <= j2 < n_cols:
                            if state_map[i2][j2] == 'H':
                                if zoc[i2][j2] == 1:
                                    count += 1
                    if count == 1:
                        res_s.append((i, j))
        return res_s

    @staticmethod
    def find_populations_sick_2(state_map, n_police, zoc):
        res_s = []
        n_rows = len(state_map)
        n_cols = len(state_map[0])
        for i in range(n_rows):
            for j in range(n_cols):
                if state_map[i][j] == 'S' and zoc[i][j] == 1:
                    count = 0
                    for dirc in DIRECTIONS:
                        i2 = i + dirc[0]
                        j2 = j + dirc[1]
                        if 0 <= i2 < n_rows and 0 <= j2 < n_cols:
                            if state_map[i2][j2] == 'H':
                                if zoc[i2][j2] == 1:
                                    count += 1
                    if count >= 2:
                        res_s.append((i, j))
        return res_s

    @staticmethod
    def find_populations(state_map, pop_tag):
        res = []
        for i in range(len(state_map)):
            for j in range(len(state_map[0])):
                if state_map[i][j] == pop_tag:
                    res.append((i, j))
        return res

    def update_time_map(self, previous_node, current_state, is_initial=False):
        if is_initial:
            new_time_map = deepcopy(previous_node.time_map)
            if self.order == 'first':
                return new_time_map
            else:
                for i in range(self.n_rows):
                    for j in range(self.n_cols):
                        if current_state[i][j] == 'Q' and previous_node.state_map[i][j] == 'S':
                            new_time_map[i][j] = 2
            return new_time_map
        new_time_map = deepcopy(previous_node.time_map)
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if current_state[i][j] in ['S', 'Q']:
                    if previous_node.state_map[i][j] == current_state[i][j]:
                        new_time_map[i][j] -= 1
                    else:
                        if current_state[i][j] == 'S':
                            new_time_map[i][j] = 2
                        else:
                            if self.order == 'first':
                                # player2 quarantied a cell in the previous round
                                new_time_map[i][j] = 0
                            else:
                                new_time_map[i][j] = 1

        # return current time:
        return new_time_map


class Node:
    def __init__(self, state_map, time_map):
        self.state_map = state_map
        self.time_map = time_map
        self.n_rows = len(state_map)
        self.n_cols = len(state_map[0])

    def h(self, p, depth=2):
        zoc_rival = [[-1] * self.n_cols for _ in range(self.n_rows)]
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                zoc_rival[i][j] = -p.zone[i][j]
        if p.order == 'first':
            # agent1 = SimpleAgent(self.state_map, p.zone)
            # agent2 = SimpleAgent(self.state_map, zoc_rival)
            zoc1 = p.zone
            zoc2 = zoc_rival
        else:
            # agent1 = SimpleAgent(self.state_map, zoc_rival)
            # agent2 = SimpleAgent(self.state_map, p.zone)
            zoc1 = zoc_rival
            zoc2 = p.zone

        node = self
        rewards = 0
        gamma = 0.9
        for turn in range(depth):
            # ac1 = agent1.act(node.state_map)
            ac1 = self.not_simple_act(node, zoc1)
            node = p.result(node, ac1)
            # ac2 = agent2.act(node.state_map)
            ac2 = self.not_simple_act(node, zoc2)
            node = p.result(node, ac2)
            node = p.run_dynamics(node)
            rewards += ((gamma**(turn + 1)) * node.reward(p))
        return rewards

    # def simple_act(self, node, zoc):
    #     action = []
    #     healthy = set()
    #     sick = set()
    #     for i in range(self.n_rows):
    #         for j in range(self.n_cols):
    #             if zoc[i][j] == 1:
    #                 if 'H' in node.state_map[i][j]:
    #                     healthy.add((i, j))
    #                 if 'S' in node.state_map[i][j]:
    #                     sick.add((i, j))
    #     if len(sick) > 1:
    #         to_quarantine = random.sample(sick, 2)
    #     else:
    #         to_quarantine = []
    #     if len(healthy) > 0:
    #         to_vaccinate = random.sample(healthy, 1)
    #     else:
    #         to_vaccinate = []
    #     for item in to_quarantine:
    #         action.append(('quarantine', item))
    #     for item in to_vaccinate:
    #         action.append(('vaccinate', item))
    #
    #     return action

    def process_state(self, state, zoc):
        healthy = []
        sick = []
        for i in range(10):
            for j in range(10):
                if zoc[i][j] == 1:
                    if 'H' in state.state_map[i][j]:
                        healthy.append((i, j))
                    if 'S' in state.state_map[i][j]:
                        sick.append((i, j))
        return healthy, sick

    def sick_heuristic(self, healthy, coordinate, zoc):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in zoc))
        return h

    def not_simple_act(self, state, zoc):
        action = []
        healthy, sick = self.process_state(state, zoc)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x, zoc), reverse=True)
        # try:
        #     to_quarantine = (sick[:2])
        # except KeyError:
        #     to_quarantine = []
        try:
            to_vaccinate = random.sample(healthy, 1)
        except ValueError:
            to_vaccinate = []

        # for item in to_quarantine:
        #     action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action

    def reward(self, p):
        zoc = p.zone
        res = 0
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.state_map[i][j] in ['I', 'H']:
                    res += (zoc[i][j] * 1)
                elif self.state_map[i][j] == 'S':
                    res += (zoc[i][j] * -1)
                elif self.state_map[i][j] == 'Q':
                    res += (zoc[i][j] * -5)
        return res

    def f(self, p, depth=2):
        return self.reward(p) + self.h(p, depth)


# implementation of a random agent
class SimpleAgent:
    def __init__(self, initial_state, zone_of_control):
        self.zoc = zone_of_control
        self.n_rows = len(initial_state)
        self.n_cols = len(initial_state[0])

    def act(self, state):
        action = []
        healthy = set()
        sick = set()
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.zoc[i][j] == 1:
                    if 'H' in state[i][j]:
                        healthy.add((i, j))
                    if 'S' in state[i][j]:
                        sick.add((i, j))
        if len(sick) > 1:
            to_quarantine = random.sample(sick, 2)
        else:
            to_quarantine = []
        if len(healthy) > 0:
            to_vaccinate = random.sample(healthy, 1)
        else:
            to_vaccinate = []
        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))

        return action

# implementation of heuristic agent
class HeuristicAgent:
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

    def sick_heuristic(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        h = sum(1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zoc))
        return h

    def act(self, state):
        action = []
        healthy, sick = self.process_state(state)
        sick.sort(key=lambda x: self.sick_heuristic(healthy, x), reverse=True)
        try:
            to_quarantine = (sick[:2])
        except KeyError:
            to_quarantine = []
        try:
            to_vaccinate = random.sample(healthy, 1)
        except ValueError:
            to_vaccinate = []

        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action
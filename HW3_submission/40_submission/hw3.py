import random
from itertools import combinations, product
import time
from random import sample, shuffle

ids = ['205552599', '322621921']
DIMENSIONS = (10, 10)




class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.first_round = True
        self.map = self.pad_the_input(initial_state, init=True)
        self.zoc = [(i+1, j+1) for i, j in zone_of_control]  # list of indices
        habitable_tiles = [(i, j) for i, j in
                           product(range(1, DIMENSIONS[0] + 1),
                                   range(1, DIMENSIONS[1] + 1)) if 'U' not in self.map[(i, j)]
                           and (i, j) not in self.zoc]
        self.other_zoc = habitable_tiles  # list of indices
        self.order = order
        self.b = None
        self.start = None
        self.score = 0 #todo
        self.round = 1
        self.to_estimate = False
        self.initiate_sample_num()

    def initiate_sample_num(self):
        self.deep_sample_factor = 5
        self.sample_num = 2000

        #print('other zoc', self.other_zoc)

    def pad_the_input(self, a_map, init=False):

        stats_dict = {'0S': 0, '0I': 0,  '0Q': 0,  '0H': 0, '0U': 0, '1S': 0,  '1I': 0,  '1Q': 0,  '1H': 0, '1U': 0}

        state = {}
        new_i_dim = DIMENSIONS[0] + 2
        new_j_dim = DIMENSIONS[1] + 2
        if init:
            for i in range(0, new_i_dim):
                for j in range(0, new_j_dim):

                    if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                        state[(i, j)] = 'U'
                    elif 'S' in a_map[i - 1][j - 1]:

                        state[(i, j)] = 'S1'
                    else:
                        state[(i, j)] = a_map[i - 1][j - 1]
            return state
        else:
            for i in range(0, new_i_dim):
                for j in range(0, new_j_dim):
                    if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                        state[(i, j)] = 'U'
                    elif 'S' in a_map[i - 1][j - 1]:
                        if 'S' not in self.map[(i, j)] or self.first_round:
                            state[(i, j)] = 'S1'
                        else:
                            state[(i, j)] = 'S' + str(int(self.map[(i, j)][1])+1)
                    elif 'Q' in a_map[i - 1][j - 1]:
                        if 'Q' not in self.map[(i, j)] or self.first_round:
                            state[(i, j)] = 'Q1'
                        else:
                            state[(i, j)] = 'Q2'
                    else:
                        state[(i, j)] = a_map[i - 1][j - 1]
                    if (i, j) in self.zoc:
                        stats_dict[f'0{state[(i, j)][0]}'] += 1
                    else:
                        stats_dict[f'1{state[(i, j)][0]}'] += 1
            self.first_round = False
            return state, stats_dict

    def act(self, state):
        self.start = start = time.time()
        state_dict, stats_dict = self.pad_the_input(state)
        self.map = state_dict

        #todo
        # if self.first_round:
        #     self.first_round = False
        ##

        # new_i_dim = DIMENSIONS[0]
        # new_j_dim = DIMENSIONS[1]
        # for i in range(0, new_i_dim):
        #     for j in range(0, new_j_dim):
        #         assert state[i][j] in self.map[(i+1, j+1)]
        best_action = self.minimax_decision(state_dict, stats_dict)
        self.first_round = False
        self.initiate_sample_num()
        finish = time.time()
        # print(f'time for option = {(finish - start)/self.b}')
        return best_action


    def actions(self, state, is_max, with_no_q_actions=False,to_sample=True):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        healthy_list = []
        sick_list = []
        zoc = self.zoc if is_max else self.other_zoc
        for (i, j) in zoc:
            if state[(i, j)] == 'H':
                healthy_list.append((i, j))
            elif 'S' in state[(i, j)]:
                sick_list.append((i, j))

        vaccine_combinations = list(combinations(healthy_list, min([1, len(healthy_list)])))
        quarantine_combinations = list(combinations(sick_list, min([2, len(sick_list)])))
        if with_no_q_actions and len(quarantine_combinations) == 1:
            quarantine_combinations += list(combinations(sick_list, min([1, len(sick_list)])))  # todo!!!
        actions_list = []

        if vaccine_combinations and quarantine_combinations:
            for vaccine in vaccine_combinations:
                current_vac_action = [("vaccinate", pos) for pos in vaccine]
                if with_no_q_actions:
                    actions_list.append(tuple(current_vac_action)) #todo!!!
                for quarantine in quarantine_combinations:
                    current_quar_action = [("quarantine", pos) for pos in quarantine]
                    actions_list.append(tuple(current_vac_action + current_quar_action))
        elif vaccine_combinations:
            actions_list = vaccine_combinations
        else:
            actions_list = quarantine_combinations
        if to_sample:
            sampled_action_list = sample(actions_list,min(self.sample_num,len(actions_list))//self.deep_sample_factor)
        else:
            sampled_action_list = actions_list
        return tuple(sampled_action_list)

    def is_goal(self, state):
        return 'S1' in state.values() or 'S2' in state.values() or 'S3' in state.values()

    def vaccinate_and_quarantine(self, state, action, stats_dict_original):
        stats_dict = dict(stats_dict_original)
        s = dict(state)
        if action:
            if action[0][1] in self.zoc:
                player = '0'
            else:
                player = '1'
        for atom_action in action:
            type_action, place_action = atom_action
            if 'q' in type_action:
                s[place_action] = 'Q0'
                stats_dict[f'{player}S'] -= 1
                stats_dict[f'{player}Q'] += 1
            else:
                s[place_action] = 'I'
                stats_dict[f'{player}H'] -= 1
                stats_dict[f'{player}I'] += 1
        return s, stats_dict

    def change_state(self, state, stats_dict):
        new_state = dict(state)
        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                             'S' in state[(i + 1, j)] or
                                             'S' in state[(i, j - 1)] or
                                             'S' in state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'
                    if (i,j) in self.zoc:
                        stats_dict['0S'] += 1
                        stats_dict['0H'] -= 1
                    else:
                        stats_dict['1S'] += 1
                        stats_dict['1H'] -= 1
        for loc, stat in state.items():
            if 'S' in stat:
                turn = int(stat[1])
                if turn < 3:
                    new_state[loc] = 'S' + str(turn + 1)
                else:
                    new_state[loc] = 'H'
                    if loc in self.zoc:
                        stats_dict['0H'] += 1
                        stats_dict['0S'] -= 1
                    else:
                        stats_dict['1H'] += 1
                        stats_dict['1S'] -= 1
                if 'Q' in stat:
                    turn = int(stat[1])
                    if turn < 2:
                        new_state[loc] = 'Q' + str(turn + 1)
                    else:
                        new_state[loc] = 'H'
                        if loc in self.zoc:
                            stats_dict['0H'] += 1
                            stats_dict['0Q'] -= 1
                        else:
                            stats_dict['1H'] += 1
                            stats_dict['1Q'] -= 1
        # # advancing sick counters
        # for i in range(1, DIMENSIONS[0] + 1):
        #     for j in range(1, DIMENSIONS[1] + 1):
        #         if 'S' in state[(i, j)]:
        #             turn = int(state[(i, j)][1])
        #             if turn < 3:
        #                 new_state[(i, j)] = 'S' + str(turn + 1)
        #             else:
        #                 new_state[(i, j)] = 'H'
        #                 if (i, j) in self.zoc:
        #                     stats_dict['0H'] += 1
        #                     stats_dict['0S'] -= 1
        #                 else:
        #                     stats_dict['1H'] += 1
        #                     stats_dict['1S'] -= 1
        #
        #         # advancing quarantine counters
        #         if 'Q' in state[(i, j)]:
        #             turn = int(state[(i, j)][1])
        #             if turn < 2:
        #                 new_state[(i, j)] = 'Q' + str(turn + 1)
        #             else:
        #                 new_state[(i, j)] = 'H'
        #                 if (i, j) in self.zoc:
        #                     stats_dict['0H'] += 1
        #                     stats_dict['0Q'] -= 1
        #                 else:
        #                     stats_dict['1H'] += 1
        #                     stats_dict['1Q'] -= 1

        return new_state, stats_dict
        # new_state = dict(state)
        #
        # # virus spread
        # for i in range(1, DIMENSIONS[0] + 1):
        #     for j in range(1, DIMENSIONS[1] + 1):
        #         if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
        #                                      'S' in state[(i + 1, j)] or
        #                                      'S' in state[(i, j - 1)] or
        #                                      'S' in state[(i, j + 1)]):
        #             new_state[(i, j)] = 'S1'
        #
        #         elif 'S' in state[(i, j)]:
        #             turn = int(state[(i, j)][1])
        #             if turn < 3:
        #                 new_state[(i, j)] = 'S' + str(turn + 1)
        #             else:
        #                 new_state[(i, j)] = 'H'
        #
        #         # advancing quarantine counters
        #         elif 'Q' in state[(i, j)]:
        #             turn = int(state[(i, j)][1])
        #             if turn < 2:
        #                 new_state[(i, j)] = 'Q' + str(turn + 1)
        #             else:
        #                 new_state[(i, j)] = 'H'
        #
        # return new_state

    def calc_reward(self, stats_dict):
        reward = -stats_dict['0S'] +stats_dict['0H'] +stats_dict['0I'] - 5 * stats_dict['0Q']
        reward -= -stats_dict['1S'] + stats_dict['1H'] + stats_dict['1I'] - 5 * stats_dict['1Q']
        return reward

    def special_estimation(self,state, stats_dict):
        s, updated_stats_dict = self.change_state(dict(state), stats_dict)
        reward = self.calc_reward(updated_stats_dict)
        return reward
    #     for loc in self.zoc:
    #         i, j = loc
    #         if 'S' in state[loc]:

    def min_value(self, state, alpha, beta, counter, score, stats_dict):
        mins_order = 'first' if self.order == 'second' else 'second'
        if self.is_goal(state) and mins_order == 'first':
            return score  # self.update_scores([0, 0])
        if counter == 0:
            reward = 0
            if self.to_estimate:
                reward = self.special_estimation(dict(state), stats_dict)
                # if mins_order == 'first':
            return score + reward  # + F
        # TODO check goal state: is the final score calculate with respect to the last two actions
        value = float('inf')
        # if cond:
        #     counter -= 1
        actions_list = self.actions(state, is_max=False,with_no_q_actions=True)
        for action in actions_list:
            # create state s after action
            s, updated_stats_dict = self.vaccinate_and_quarantine(state, action, stats_dict)
            temp_score = score
            reward = 0
            # updated_stats_dict = self.update_stats(stats_dict,action)
            if mins_order == 'second':
                # s, temp_score = self.change_state(s)
                s, updated_stats_dict = self.change_state(s, updated_stats_dict)
                reward = self.calc_reward(updated_stats_dict)
                # temp_score = self.update_scores(s, temp_score)
            value = min(value, self.max_value(s, alpha, beta, counter - 1, temp_score + reward, updated_stats_dict))
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value

    def max_value(self, state, alpha, beta, counter, score, stats_dict):
        max_order = self.order
        if self.is_goal(state) and max_order == 'first':
            return score
        if counter == 0:
            reward = 0
            # if max_order == 'first':
            if self.to_estimate:
                reward = self.special_estimation(dict(state), stats_dict)
            return score + reward  # + F
        # TODO check goal state: is the final score calculate with respect to the last two actions
        value = float('-inf')
        actions_list = self.actions(state, is_max=True,with_no_q_actions=True)
        for action in actions_list:
            # create state s after action
            s, updated_stats_dict = self.vaccinate_and_quarantine(state, action,stats_dict)
            temp_score = score
            reward = 0
            # updated_stats_dict = self.update_stats(stats_dict,action)
            if max_order == 'second':
                # s, temp_score = self.change_state(s)
                s, stats_dict = self.change_state(s,updated_stats_dict)
                reward = self.calc_reward(updated_stats_dict)
                #  temp_score = self.update_scores(s, temp_score)
            value = max(value, self.min_value(s, alpha, beta, counter - 1, temp_score + reward, updated_stats_dict))
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value


    def minimax_decision(self, initial_state, stats_dict):
        value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        value_for_action = {}  #  {s:self.min_value(s, alpha, beta, counter) for action in 'action combinations'}
        full_actions_list = self.actions(initial_state, is_max=True,with_no_q_actions=True,to_sample=False)
        for action in full_actions_list:
            action = tuple([(atom[0],(atom[1][0]-1, atom[1][1]-1)) for atom in action])
            value_for_action[action] = float('-inf')
        actions_list = list(full_actions_list)
        shuffle(actions_list)
        self.b = len(value_for_action)
        counter = 20
        if len(actions_list) < 200:
            counter = 6
            self.deep_sample_factor = 3
        longest_iteration = 0
        for i, action in enumerate(actions_list):
            t = time.time()
            reward = 0
            s, updated_stats_dict = self.vaccinate_and_quarantine(initial_state, action, stats_dict)
            # updated_stats_dict = self.update_stats(stats_dict, action)
            if self.order == 'second':
                s, updated_stats_dict = self.change_state(s, updated_stats_dict)
                # score = self.update_scores(s, score)
                reward = self.calc_reward(updated_stats_dict)
            action = tuple([(atom[0],(atom[1][0]-1, atom[1][1]-1)) for atom in action])
            # print(action)
            value_for_action[action] = self.min_value(s, alpha, beta, counter-1, reward,
                                                      updated_stats_dict)
            longest_iteration = max(time.time() - t, longest_iteration)
            #todo add value_for_action[action] to list of values and afterwards delete bad actions!!!!!!!!!!
            if i>=self.sample_num or time.time()-self.start + longest_iteration> 4.6 or time.time() - t > 1:
                break
        #     value = max(value, self.min_value(s, alpha, beta, counter))
        while time.time()-self.start < 0.2 and self.deep_sample_factor > 1:
            self.deep_sample_factor -= 1
            for i, action in enumerate(sorted(value_for_action,key=value_for_action.get,reverse=True)):
                action = tuple([(atom[0], (atom[1][0] + 1, atom[1][1] + 1)) for atom in action])
                t = time.time()
                reward = 0
                s, updated_stats_dict = self.vaccinate_and_quarantine(initial_state, action, stats_dict)
                # updated_stats_dict = self.update_stats(stats_dict, action)
                if self.order == 'second':
                    s, updated_stats_dict = self.change_state(s, updated_stats_dict)
                    # score = self.update_scores(s, score)
                    reward = self.calc_reward(updated_stats_dict)
                action = tuple([(atom[0], (atom[1][0] - 1, atom[1][1] - 1)) for atom in action])
                # print(action)
                value_for_action[action] = self.min_value(s, alpha, beta, counter - 1, reward,
                                                          updated_stats_dict)
                longest_iteration = max(time.time() - t, longest_iteration)
                # todo add value_for_action[action] to list of values and afterwards delete bad actions!!!!!!!!!!
                if i >= self.sample_num or time.time() - self.start + longest_iteration > 4.6 or time.time() - t > 1:
                    break


        # if time.time()-self.start<3.5:#0.5725:#todo
        #     counter += 1# todo increase counter if |I| and |Q| are high or round number is high
        #     print(f'depth {counter} begin')
        #     alpha = float('-inf')
        #     beta = float('inf')
        #     reward = 0
        #     for i, action in enumerate(sorted(value_for_action,key=value_for_action.get,reverse=True)):
        #         t = time.time()
        #         action = tuple([(atom[0],(atom[1][0]+1, atom[1][1]+1)) for atom in action])
        #         s, updated_stats_dict = self.vaccinate_and_quarantine(initial_state, action, stats_dict)
        #         if self.order == 'second':
        #             s, updated_stats_dict = self.change_state(s, updated_stats_dict)
        #             reward = self.calc_reward(updated_stats_dict)
        #         action = tuple([(atom[0], (atom[1][0] - 1, atom[1][1] - 1)) for atom in action])
        #         # print(type(action))
        #         value_for_action[action] = self.min_value(s, alpha, beta, counter - 1, reward,
        #                                                   updated_stats_dict)
        #         if time.time()-self.start + time.time()-t > 4.7 or i >self.sample_num:  # todo change!
        #             return list(max(value_for_action, key=value_for_action.get))
        #
        # elif time.time()-self.start<3.5:#todo2.0725:
        #     self.to_estimate = True
        #     print(f'special {counter} estimation')
        #     alpha = float('-inf')
        #     beta = float('inf')
        #     reward = 0
        #     for action in sorted(value_for_action, key=value_for_action.get, reverse=True):
        #         t = time.time()  # todo check if search on action takes more than 1.5 seconds
        #         action = tuple([(atom[0], (atom[1][0] + 1, atom[1][1] + 1)) for atom in action])
        #         s, updated_stats_dict = self.vaccinate_and_quarantine(initial_state, action, stats_dict)
        #         if self.order == 'second':
        #             s, updated_stats_dict = self.change_state(s, updated_stats_dict)
        #             reward = self.calc_reward(updated_stats_dict)
        #         action = tuple([(atom[0], (atom[1][0] - 1, atom[1][1] - 1)) for atom in action])
        #         value_for_action[action] = self.min_value(s, alpha, beta, counter - 1, reward,
        #                                                   updated_stats_dict)
        # self.to_estimate = False
        # print(f'depth {counter} done')

        # while time.time()-self.start<1.7 and counter<100:#<0.531 and counter<100:#todo
        #     self.sample_num += 25
        #     counter += 2 # todo increase counter if |I| and |Q| are high or round number is high
        #     if counter<=15 or counter%20==0:
        #         print(f'depth {counter} begin')
        #     alpha = float('-inf')
        #     beta = float('inf')
        #     reward = 0
        #     x = 0
        #     for i, action in enumerate(sorted(value_for_action,key=value_for_action.get,reverse=True)):
        #         t = time.time()
        #         action = tuple([(atom[0],(atom[1][0]+1, atom[1][1]+1)) for atom in action])
        #         s, updated_stats_dict = self.vaccinate_and_quarantine(initial_state, action, stats_dict)
        #         if self.order == 'second':
        #             s, updated_stats_dict = self.change_state(s, updated_stats_dict)
        #             reward = self.calc_reward(updated_stats_dict)
        #         action = tuple([(atom[0], (atom[1][0] - 1, atom[1][1] - 1)) for atom in action])
        #         # print(type(action))
        #         value_for_action[action] = self.min_value(s, alpha, beta, counter - 1, reward,
        #                                                   updated_stats_dict)
        #         x = max(time.time()-t,x)
        #         if time.time()-self.start + x > 4.15:#4 or time.time()-t > 1.4:
        #             if i==0:
        #                 print('!!')
        #             if time.time() - self.start > 4.9:
        #                 print('$')
        #             return list(max(value_for_action, key=value_for_action.get))
        #         if i>self.sample_num:
        #             break
        #     if counter <= 15 or counter % 20 == 0:
        #         print(f'depth {counter} done')
        # if time.time()-self.start > 4:
        #     print('@')
        return list(max(value_for_action, key=value_for_action.get))












# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         print(initial_state)
#
#     def act(self, state):
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action


    def update_scores(self, state, score):
        # TODO return score function of parent + change
        for (i, j) in self.zoc:
            if 'H' in state[(i, j)]:
                score += 1
            if 'I' in state[(i, j)]:
                score += 1
            if 'S' in state[(i, j)]:
                score -= 1
            if 'Q' in state[(i, j)]:
                score -= 5

        for (i, j) in self.other_zoc:
            if 'H' in state[(i, j)]:
                score -= 1
            if 'I' in state[(i, j)]:
                score -= 1
            if 'S' in state[(i, j)]:
                score += 1
            if 'Q' in state[(i, j)]:
                score += 5

        return score

from copy import deepcopy
from itertools import combinations

ids = ['311445639', '312132640']

QUARANTINE_SCORE_THRESHOLD = 2


class Agent:

    def __init__(self, initial_state, zone_of_control, order):
        self.max_action_combinations = 180
        self.zone_of_control = zone_of_control
        self.opponent_zone_of_control = Agent.find_opponent_zone_of_control(zone_of_control, 10)
        self.previous_opponent_states = []
        # Doesn't change
        self.num_of_police = 2
        self.num_of_medics = 1
        # Max predictions
        self.minimax_max_depth = 10
        self.alpha_beta_pruning_counter = 0
        self.timeline_state = [[1 for _ in range(10)] for _ in range(10)]
        self.order = True if order.lower() == "first" else False
        self.desired_move_state = None

    def act(self, state):
        opponent_state_delta = Agent.find_opponent_state_delta(list(self.previous_opponent_states),
                                                               Agent.find_opponent_states(self.opponent_zone_of_control,
                                                                                          state))
        # At the beginning of each turn, mutate the opponent cells timeline state
        opponent_action_sequence = self.find_opponent_action_sequence(opponent_state_delta)
        self.apply_timeline_shift_from_action_sequence(opponent_action_sequence)

        select_action_predicted_score, selected_action_sequence = self._minimax(0, state, deepcopy(self.timeline_state),
                                                                                True,
                                                                                float('-inf'),
                                                                                float('inf'), 1)
        self.adjust_timeline(state, selected_action_sequence)
        sequence_formatted = self.to_game_sequence_format(selected_action_sequence)

        # print("Maximal minimax score of move is: ", select_action_predicted_score)
        # print("The selected action sequence is: ", sequence_formatted)
        # print("Alpha-Beta pruning counter (cumulative): ", self.alpha_beta_pruning_counter)
        # print("Final desired state is: ", self.desired_move_state)

        # At the end of each turn, save the known opponent state
        self.previous_opponent_states = Agent.find_opponent_states(list(self.opponent_zone_of_control), state)
        return sequence_formatted

    def _minimax(self, current_depth, board, timeline_state, is_max_turn, alpha, beta, virtual_turn):
        if virtual_turn != 1 and virtual_turn % 2 != 0:
            self.apply_game_dynamics(board, timeline_state)

        if current_depth == self.minimax_max_depth:
            return self.evaluation_function(board, self.zone_of_control), []

        action_sequences = self.get_full_sorted_actions_sequences(self.zone_of_control, board)
        action_sequences = action_sequences[:self.max_action_combinations]
        best_value = float('-inf') if is_max_turn else float('inf')
        action_target = None
        for evaluated_sequence in action_sequences:
            new_state = self.apply_actions(board, evaluated_sequence.sequence, timeline_state)

            eval_child, action_child = self._minimax(current_depth + 1, new_state, list(timeline_state),
                                                     not is_max_turn,
                                                     alpha, beta, virtual_turn + 1)

            if is_max_turn and best_value < eval_child:
                best_value = eval_child
                action_target = evaluated_sequence
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    self.alpha_beta_pruning_counter += 1
                    break
                self.desired_move_state = new_state

            elif (not is_max_turn) and best_value > eval_child:
                best_value = eval_child
                action_target = evaluated_sequence
                beta = min(beta, best_value)
                if beta <= alpha:
                    self.alpha_beta_pruning_counter += 1
                    break
                self.desired_move_state = new_state

        return best_value, action_target

    def get_full_sorted_actions_sequences(self, zone_of_control, board):
        healthy, sick = self.find_sick_and_healthy_in_zoc(board)

        police_actions = [
            [Action('quarantine', cord[0], cord[1], self.sick_hotspot_heuristic(healthy, (cord[0], cord[1]))) for cord
             in action_cords] for action_cords in
            self.get_action_combinations(zone_of_control, board, self.num_of_police - 1, 'S')]
        medic_actions = [
            [Action('vaccinate', cord[0], cord[1], Agent.blast_radius_heuristic(sick, (cord[0], cord[1]))) for cord in
             action_cords] for action_cords in
            self.get_action_combinations(zone_of_control, board, self.num_of_medics, 'H')]

        action_sequences = []

        for police_action in police_actions:
            for medics_action in medic_actions:
                combined_action = []
                combined_action.extend(police_action)
                combined_action.extend(medics_action)
                action_sequences.append(ActionSequence(combined_action))

        action_sequences.sort(key=lambda action_sequence: ActionSequence.get_score(action_sequence.sequence),
                              reverse=True)
        return action_sequences

    @staticmethod
    def get_action_combinations(zone_of_control, board, to_the_power_of, state_code):
        code_positions = []
        for (i, j) in zone_of_control:
            if state_code in board[i][j]:
                code_positions.append((i, j))

        # find the limited power-set of actions with the positions in hand
        s = list(code_positions)
        for r in range(to_the_power_of + 1)[::-1]:
            combs = list(combinations(s, r))

            if len(combs) > 0:
                return combs

    def evaluation_function(self, board, zone_of_control):
        current_score = 0
        for element in zone_of_control:
            if board[element[0]][element[1]] == 'H':
                current_score = current_score + 1
            if board[element[0]][element[1]] == 'I':
                current_score = current_score + 1
            if board[element[0]][element[1]] == 'S':
                current_score = current_score - 1  # self.calc_spread_potential(25)  # up-to 5 turns ahead
            if board[element[0]][element[1]] == 'Q':
                current_score = current_score - 5

        competitive_score = self.evaluation_function_competitive(board, zone_of_control)

        return (current_score * 9) + (competitive_score * 1)

    @staticmethod
    def evaluation_function_competitive(board, zone_of_control):
        our_sick_counter = 0
        for element in zone_of_control:
            if board[element[0]][element[1]] == 'S':
                our_sick_counter += 1

        opponent_sick_counter = 0
        for i in range(len(board)):
            for j in range(len(board)):
                element = board[i][j]
                if element == 'S' and (i, j) not in zone_of_control:
                    opponent_sick_counter += 1

        if our_sick_counter > opponent_sick_counter:
            return -50 * (our_sick_counter / opponent_sick_counter if opponent_sick_counter > 0 else 1)
        if our_sick_counter == opponent_sick_counter:
            return 0
        else:
            return 50 * (opponent_sick_counter / our_sick_counter if our_sick_counter > 0 else 1)

    @staticmethod
    def calc_spread_potential(prediction_turn):
        spread_score = 1
        for i in range(1, prediction_turn + 1):
            spread_score = spread_score + (4 + (i - 1) * 4)
        return spread_score

    @staticmethod
    def apply_actions(board, evaluated_sequence, timeline_state):
        new_board = list(board)
        for action in evaluated_sequence:
            effect, i, j = action.action, action.row, action.column
            if 'v' in effect:
                new_board[i][j] = 'I'
                timeline_state[i][j] = 1
            else:
                new_board[i][j] = 'Q'
                timeline_state[i][j] = 1
        return new_board

    @staticmethod
    def apply_game_dynamics(board, virtual_timeline_state):
        current_sick = []
        for i in range(len(board)):
            for j in range(len(board)):
                element = board[i][j]
                if element == 'S':
                    current_sick.append((i, j))

        max_i = len(board) - 1
        max_j = len(board) - 1
        healthy_to_sick = []
        for x in range(len(current_sick)):
            i = current_sick[x][0]
            j = current_sick[x][1]
            if i + 1 <= max_i:
                if board[i + 1][j] == 'H':
                    healthy_to_sick.append((i + 1, j))
            if j + 1 <= max_j:
                if board[i][j + 1] == 'H':
                    healthy_to_sick.append((i, j + 1))
            if i - 1 >= 0:
                if board[i - 1][j] == 'H':
                    healthy_to_sick.append((i - 1, j))
            if j - 1 >= 0:
                if board[i][j - 1] == 'H':
                    healthy_to_sick.append((i, j - 1))

        for i in range(len(healthy_to_sick)):
            index1 = healthy_to_sick[i][0]
            index2 = healthy_to_sick[i][1]
            board[index1][index2] = 'S'
            virtual_timeline_state[index1][index2] = 0

        for i in range(len(board)):
            for j in range(len(board)):
                # if its Q for 2 turns, then the next turn it should change to H
                if board[i][j] == 'Q' and virtual_timeline_state[i][j] == 2:
                    board[i][j] = 'H'
                    virtual_timeline_state[i][j] = 0
                    continue
                # if its S for 3 turns, then the next turn it should change to H
                if board[i][j] == 'S' and virtual_timeline_state[i][j] == 3:
                    board[i][j] = 'H'
                    virtual_timeline_state[i][j] = 0
                    continue

        for i in range(len(board)):
            for j in range(len(board)):
                virtual_timeline_state[i][j] = virtual_timeline_state[i][j] + 1

    def adjust_timeline(self, board, action_sequence):
        for i in range(len(board)):
            for j in range(len(board)):
                if self.timeline_state[i][j] >= 3:
                    self.timeline_state[i][j] = 1
                elif board[i][j] == 'Q' and self.timeline_state[i][j] == 2:
                    self.timeline_state[i][j] = 1
                else:
                    self.timeline_state[i][j] = self.timeline_state[i][j] + 1

        self.apply_timeline_shift_from_action_sequence(action_sequence)

    def apply_timeline_shift_from_action_sequence(self, action_sequence):
        for action in action_sequence.sequence:
            self.timeline_state[action.row][action.column] = 1

    @staticmethod
    def to_game_sequence_format(action_sequence):
        sequence = action_sequence.sequence
        return list(map(lambda action: (action.action, (action.row, action.column)), sequence))

    def sick_hotspot_heuristic(self, healthy, coordinate):
        neighbors = ((coordinate[0] - 1, coordinate[1]),
                     (coordinate[0] + 1, coordinate[1]),
                     (coordinate[0], coordinate[1] - 1),
                     (coordinate[0], coordinate[1] + 1))
        total_healthy_neighbours = sum(
            1 for neighbor in neighbors if (neighbor in healthy and neighbor in self.zone_of_control))
        return total_healthy_neighbours

    @staticmethod
    def blast_radius_heuristic(sick, healthy_cell_coordinate):
        adjacent_cells = ((healthy_cell_coordinate[0] - 1, healthy_cell_coordinate[1]),
                          (healthy_cell_coordinate[0] + 1, healthy_cell_coordinate[1]),
                          (healthy_cell_coordinate[0], healthy_cell_coordinate[1] - 1),
                          (healthy_cell_coordinate[0], healthy_cell_coordinate[1] + 1))

        blast_radius = (
            (healthy_cell_coordinate[0] - 2, healthy_cell_coordinate[1]),
            (healthy_cell_coordinate[0] + 2, healthy_cell_coordinate[1]),
            (healthy_cell_coordinate[0], healthy_cell_coordinate[1] - 2),
            (healthy_cell_coordinate[0], healthy_cell_coordinate[1] + 2))

        blast_radius_ranking = sum(1 for far_neighbor in blast_radius if (far_neighbor in sick))
        return blast_radius_ranking + sum(2 for neighbor in adjacent_cells if (neighbor in sick))

    @staticmethod
    def find_opponent_zone_of_control(our_zone_of_control, fixed_dimensions):
        fake_board = [[0 for _ in range(fixed_dimensions)]] * fixed_dimensions  # doesn't change
        opponent_zone_of_control = []
        for i in (range(len(fake_board))):
            for j in (range(len(fake_board))):
                if (i, j) not in our_zone_of_control:
                    opponent_zone_of_control.append((i, j))

        return opponent_zone_of_control

    def find_sick_and_healthy_in_zoc(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zone_of_control:
            if 'H' in state[i][j]:
                healthy.append((i, j))
            if 'S' in state[i][j]:
                sick.append((i, j))
        return healthy, sick

    @staticmethod
    def find_opponent_states(opponent_zone_of_control, board):
        opponent_states = []
        for coordinate in opponent_zone_of_control:
            cell = Cell(coordinate[0], coordinate[1], board[coordinate[0]][coordinate[1]])
            opponent_states.append(cell)
        return opponent_states

    @staticmethod
    def find_opponent_state_delta(previous_opponent_state, new_opponent_state):
        opponent_state_deltas = []
        if not previous_opponent_state:
            return []
        for new_opponent_cell in new_opponent_state:
            for old_opponent_cell in previous_opponent_state:
                if old_opponent_cell.row == new_opponent_cell.row and old_opponent_cell.column == new_opponent_cell. \
                        column:
                    if old_opponent_cell.state != new_opponent_cell.state:
                        opponent_state_deltas.append(new_opponent_cell)

        return opponent_state_deltas

    @staticmethod
    def find_opponent_action_sequence(opponent_state_delta):
        sequence = []
        for opponent_cell in opponent_state_delta:
            action = ""
            cell_state = opponent_cell.state
            if cell_state == "Q":
                action = "quarantine"
            elif cell_state == "I":
                action = "vaccinate"
            sequence.append(Action(action, opponent_cell.row, opponent_cell.column, 0))

        return ActionSequence(sequence)


class Action:
    def __init__(self, action, row, column, heuristic_score):
        self.action = action
        self.row = row
        self.column = column
        self.heuristic_score = heuristic_score

    def __eq__(self, other):
        if not isinstance(other, Action):
            return NotImplemented

        return self.action == other.action and self.row == other.row and self.column == other.column

    def __str__(self) -> str:
        return self.action + "(" + self.row + "," + self.column + ")"


class ActionSequence:
    def __init__(self, sequence):
        clean_sequence = []
        for action in sequence:
            if action.action == "quarantine":
                if action.heuristic_score >= QUARANTINE_SCORE_THRESHOLD:
                    clean_sequence.append(action)
            else:
                clean_sequence.append(action)
        self.sequence = clean_sequence

    @staticmethod
    def get_score(sequence):
        all_scores = list(map(lambda action: action.heuristic_score, sequence))
        return sum(all_scores)

    def __eq__(self, other):
        if not isinstance(other, ActionSequence):
            return NotImplemented

        return self.sequence == other.sequence

    def has_quarantine(self):
        return any(action.action == "quarantine" for action in self.sequence)


class Cell:

    def __init__(self, row, column, state):
        self.state = state
        self.column = column
        self.row = row

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented

        return self.state == other.state and self.row == other.row and self.column == other.column

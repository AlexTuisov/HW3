from itertools import product
ids = ['313471435', '206388266']


def game_over(board):
    """ Given a board, checks if this is the goal state.
            Returns True if it is, False otherwise."""
    for i in board:
        for j in i:
            if 'S' == j:
                return False
    return True


def get_possible_action(board, zoc):
    healthy = []
    sick = []
    for (i, j) in zoc:
        if 'H' in board[i][j]:
            healthy.append((i, j))
        if 'S' in board[i][j]:
            sick.append((i, j))
    return {'vaccinate': healthy, 'quarantine': sick}


def will_be_H_next_turn(i, j, days_map):
    if days_map[i][j] == 0:
        return True
    else:
        return False


def count_neighbor_type(i, j, board, control_zone):
    col_len = len(board[0])
    row_len = len(board[:])
    count_s = 0
    count_h = 0
    if 0 <= (j + 1) < col_len:
        if (i, j+1) in control_zone:
            if board[i][j + 1] == 'S':
                count_s += 1
            if board[i][j + 1] == 'H':
                count_h += 1
        else:
            if board[i][j + 1] == 'H':
                count_h -= 1
    if 0 <= (j - 1):
        if (i, j-1) in control_zone:
            if board[i][j - 1] == 'S':
                count_s += 1
            if board[i][j - 1] == 'H':
                count_h += 1
        else:
            if board[i][j - 1] == 'H':
                count_h -= 1
    if 0 <= (i + 1) < row_len:
        if (i+1, j) in control_zone:
            if board[i + 1][j] == 'S':
                count_s += 1
            if board[i + 1][j] == 'H':
                count_h += 1
        else:
            if board[i + 1][j] == 'H':
                count_h -= 1
    if 0 <= i - 1:
        if (i-1, j) in control_zone:
            if board[i - 1][j] == 'S':
                count_s += 1
            if board[i - 1][j] == 'H':
                count_h += 1
        else:
            if board[i - 1][j] == 'H':
                count_h -= 1
    return count_s, count_h


def zone_score(control_zone, board, days_map):
    # with heuristic
    score = 0
    for (i, j) in control_zone:
        if 'H' in board[i][j]:
            score += 1
            score -= count_neighbor_type(i, j, board, control_zone)[0]
        if 'I' in board[i][j]:
            score += 1
        if 'S' in board[i][j]:
            score -= 1
            score -= 2 * count_neighbor_type(i, j, board, control_zone)[1]
            if will_be_H_next_turn(i, j, days_map):
                score += 2
        if 'Q' in board[i][j]:
            score -= 5
            if will_be_H_next_turn(i, j, days_map):
                score += 7
    return score


def S_loc(current_loc):
    index_row = -1
    index_col = -1
    S_location = []
    for row in current_loc:
        index_row += 1
        for cell in row:
            index_col += 1
            if cell == 'S':
                S_location.append((index_row, index_col))
        index_col = -1
    return S_location


def infection_spreads(new_map, new_days):
    new_sick_count = 0
    sick_locations = S_loc(new_map)
    col = len(new_map[0])
    row = len(new_map[:])

    for i, j in sick_locations:
        if 0 <= i - 1:
            if new_map[i - 1][j] == 'H':
                new_map[i - 1][j] = 'S'
                new_days[i - 1][j] = 3
                new_sick_count += 1
        if 0 <= (i + 1) < row:
            if new_map[i + 1][j] == 'H':
                new_map[i + 1][j] = 'S'
                new_days[i + 1][j] = 3
                new_sick_count += 1
        if 0 <= (j - 1) < col:
            if new_map[i][j - 1] == 'H':
                new_map[i][j - 1] = 'S'
                new_days[i][j - 1] = 3
                new_sick_count += 1
        if 0 <= (j + 1) < col:
            if new_map[i][j + 1] == 'H':
                new_map[i][j + 1] = 'S'
                new_days[i][j + 1] = 3
                new_sick_count += 1
    return new_map, new_days, new_sick_count


def result(state_and_days, action_index, action):
    """Return the board that results from executing the given
    action in the given index."""

    col_num = len(state_and_days[0][0])
    row_num = len(state_and_days[0][:])
    curr_map = state_and_days[0]
    days = state_and_days[1]
    row_index, col_index = action_index[0], action_index[1]

    if action == "vaccinate":
        curr_map[row_index][col_index] = 'I'
        days[row_index][col_index] = -1
    if action == "quarantine":
        curr_map[row_index][col_index] = 'Q'
        days[row_index][col_index] = 2

    new_map, new_days, _ = infection_spreads(curr_map, days)

    for i in range(row_num):
        for j in range(col_num):
            if new_map[i][j] != curr_map[i][j]:
                continue
            if days[i][j] == 0:
                new_map[i][j] = 'H'
            if days[i][j] >= 0:
                new_days[i][j] -= 1

    state_and_days = [new_map, new_days]

    return state_and_days


def init_counter(status):
    if 'S' == status:
        return 3
    if 'Q' == status:
        return 2
    return -1


def init_days_per_turns(board):
    col = len(board[0])
    row = len(board[:])
    return [[init_counter(board[i][j]) for j in
             range(col)] for i in range(row)]


def get_all_action_tuples(possible_action_dict):
    #all profitable action(never do Q)
    H = possible_action_dict['vaccinate']
    len_H = len(H)
    H_act = ['vaccinate']*len_H
    H = list(zip(H_act, H))
    poss_h = H
    possible_actions = tuple(product(poss_h))

    return possible_actions


def _minimax(current_depth, state_and_days, is_max_turn, alpha, beta, player_alias, control_zone, max_depth):
    board = state_and_days[0]
    days_map = state_and_days[1]
    if current_depth == max_depth or game_over(board):
        return zone_score(control_zone, board, days_map), ""

    possible_action_dict = get_possible_action(board, control_zone)

    best_value = float('-inf') if is_max_turn else float('inf')
    best_action = []
    all_action_tuples = get_all_action_tuples(possible_action_dict)

    for action in all_action_tuples:
        updated_state_and_days = state_and_days.copy()
        for sub_action in action:
            if sub_action:
                index_action = sub_action[1]
                act = sub_action[0]
                updated_state_and_days = result(updated_state_and_days, index_action, act)
        current_depth += 1
        child_score, child_action = _minimax(current_depth, updated_state_and_days, not is_max_turn, alpha, beta, player_alias, control_zone, max_depth)

        if is_max_turn and best_value < child_score:
            best_value = child_score
            best_action = action
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        elif (not is_max_turn) and best_value > child_score:
            best_value = child_score
            best_action = action
            beta = min(beta, best_value)
            if beta <= alpha:
                break

    return best_value, best_action


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.board = initial_state
        self.alias = order
        self.max_depth = 4
        print(initial_state)

    def act(self, state):
        day_counters = init_days_per_turns(state)
        state_and_days = [state, day_counters]
        _, action = _minimax(current_depth=0, state_and_days=state_and_days, is_max_turn=True, alpha=-2000, beta=2000, player_alias=self.alias, control_zone=self.zoc, max_depth=self.max_depth)
        best_action_result = []
        if len(action) > 1:
            for act in action:
                if act:
                    best_action_result.append(act)
        else:
            best_action_result = action
        return best_action_result

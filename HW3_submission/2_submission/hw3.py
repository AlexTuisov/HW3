# from __future__ import annotations

import math
import random
import time

# from typing import List, Optional

ids = ['313410938']

CELL_STATES = {
    'H': 'H',
    'S': 'S',
    'U': 'U',
    'Q': 'Q',
    'I': 'I'
}

AGENT_ACTIONS = {
    'v': 'vaccinate',
    'q': 'quarantine'
}

AVAILABLE_ACTIONS = {
    AGENT_ACTIONS['v']: 1,
    AGENT_ACTIONS['q']: 2
}

STATE_PLAYER = {
    'US': 'US',
    'AI': 'AI'
}

NEIGHBORS_CELLS = {
    'RIGHT': 'RIGHT',
    'LEFT': 'LEFT',
    'DOWN': 'DOWN',
    'TOP': 'TOP',
}

PLAY_ORDERS = {
    'FIRST': 'first',
    'SECOND': 'second'
}

EMPTY_ACTION = []


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self._zone_of_control = zone_of_control
        self._order = order
        self._initial_state = initial_state

        # TODO: check
        # check initial player by order STATE_PLAYER['US']
        self._current_state = ObservationState(initial_state, self._zone_of_control, self._order, STATE_PLAYER['US'])
        self._current_maintained_state = self._current_state
        # self._last_3_states: List[ObservationState] = []
        self._last_3_states = []

    # def update_last_states(self, current_state: ObservationState):
    def update_last_states(self, current_state):
        self._last_3_states.insert(0, current_state)
        if len(self._last_3_states) > 3:
            self._last_3_states.pop()

    # def get_last_state_by_index(self, state_index) -> Optional[ObservationState]:
    def get_last_state_by_index(self, state_index):
        if state_index < 0 or state_index > len(self._last_3_states):
            return None
        return self._last_3_states[state_index - 1]

    def act(self, state):

        obj_state = ObservationState(state, self._zone_of_control, self._order, STATE_PLAYER['US'])
        self._current_state = obj_state

        states_handler = PossibleStatesHandler(obj_state, AVAILABLE_ACTIONS)

        states_handler.set_list_last_3_states(self._last_3_states)
        best_next_state = states_handler.get_next_best_possible_state_by_current_state()

        # update last states
        self.update_last_states(self._current_state)

        if best_next_state is not None and best_next_state.get_action() is not None:

            result_action_tuple = states_handler.get_action_tuple_for_next_possible_state(best_next_state)
            if result_action_tuple is None:
                return EMPTY_ACTION
            return result_action_tuple
        default_action = states_handler.select_default_next_state_action()
        if default_action is None:
            return EMPTY_ACTION
        default_action_tuple = default_action.get_action_tuple()
        if default_action_tuple is None:
            return EMPTY_ACTION
        return default_action_tuple


class CellState:
    def __init__(self, raw_state):
        self._raw_state = raw_state
        self._is_valid = None
        self._state_key = None
        self._turn = None
        self._update_state_data_by_raw_state()

    def _update_state_data_by_raw_state(self):
        self._is_valid = self.is_valid_raw_state(self._raw_state)
        self._state_key = self.get_state_key_from_raw_state(self._raw_state)
        if self.has_turns():
            self._turn = self.get_state_turn_from_raw_state(self._raw_state)

    def get_state_key(self):
        return self._state_key

    def get_state_key_from_raw_state(self, raw_state):
        if not self.is_valid_raw_state(raw_state):
            return None
        return raw_state[0]

    def get_state_turn_from_raw_state(self, raw_state):
        if not self.is_valid_raw_state(raw_state):
            return None
        if len(raw_state) < 2:
            return None
        return raw_state[1]

    def is_valid(self):
        return self._is_valid

    def has_turns(self):
        return self._state_key in self.get_list_states_with_turns()

    def get_turn(self):
        return self._turn

    def is_valid_turn(self, turn):
        if not self.has_turns():
            return False

        if turn < 1:
            return False

        if self._state_key == CELL_STATES['S'] and turn > 3:
            return False

        if self._state_key == CELL_STATES['Q'] and turn > 2:
            return False

        return True

    def update_turn(self, new_turn):
        if not self.is_valid_turn(new_turn):
            return False
        self._turn = new_turn
        return True

    def is_valid_raw_state(self, raw_state):
        return raw_state is not None and raw_state[0] in CELL_STATES

    def get_list_states_with_turns(self):
        return [CELL_STATES['Q'], CELL_STATES['S']]


class ObservationCell:
    # def __init__(self, row, column, state: CellState):
    def __init__(self, row, column, state):
        self._row = row
        self._column = column
        self._state = state

    # def get_state(self) -> CellState:
    def get_state(self):
        return self._state

    def get_row(self):
        return self._row

    def get_column(self):
        return self._column

    def get_position_tuple(self):
        position = (self._row, self._column)
        return position

    def is_action_valid(self, action):
        if action == AGENT_ACTIONS['v']:
            if self._state.get_state_key() == CELL_STATES['H']:
                return True

        if action == AGENT_ACTIONS['q']:
            if self._state.get_state_key() == CELL_STATES['S']:
                return True

        return False

    def apply_action(self, action):
        if not self.is_action_valid(action):
            return False

        if action == AGENT_ACTIONS['v']:
            self._state = CellState(CELL_STATES['I'])
            return True

        if action == AGENT_ACTIONS['q']:
            self._state = CellState(CELL_STATES['Q'])
            return True

        return False

    def get_cell_neighbor_position_tuple(self, cell_neighbor_type):
        position_tuple = None

        if cell_neighbor_type == NEIGHBORS_CELLS['RIGHT']:
            position_tuple = (self._row, self._column + 1)
            return position_tuple

        elif cell_neighbor_type == NEIGHBORS_CELLS['LEFT']:
            position_tuple = (self._row, self._column - 1)
            return position_tuple

        elif cell_neighbor_type == NEIGHBORS_CELLS['DOWN']:
            position_tuple = (self._row + 1, self._column)
            return position_tuple

        elif cell_neighbor_type == NEIGHBORS_CELLS['DOWN']:
            position_tuple = (self._row - 1, self._column)
            return position_tuple

        return None

    def get_neighbor_cell_instance(self, cell_neighbor_type):
        neighbor_position_tuple = self.get_cell_neighbor_position_tuple(cell_neighbor_type)
        if neighbor_position_tuple is None:
            return None
        row = neighbor_position_tuple[0]
        column = neighbor_position_tuple[1]
        return ObservationCell(row, column, None)


class PossibleElementaryCellAction:
    # def __init__(self, cell: ObservationCell, action):
    def __init__(self, cell, action):
        self._cell = cell
        self._action = action

    def get_action(self):
        return self._action

    def get_cell(self):
        return self._cell

    def get_action_tuple(self):
        action_tuple = (self._action, self._cell.get_position_tuple())
        return action_tuple


class ObservationState:

    # def create_instance_by_existing_instance(existing_instance: ObservationState):
    @staticmethod
    def create_instance_by_existing_instance(existing_instance):
        new_instance = ObservationState(existing_instance.get_state(), existing_instance.get_control_zone(),
                                        existing_instance.get_order(), existing_instance.get_state_player())
        return new_instance

    def __init__(self, current_observation_raw_state, current_control_zone, raw_order, state_player):
        # source state
        self._raw_state = current_observation_raw_state
        self._cells = []
        self._number_of_rows = len(self._raw_state)
        self._number_of_columns = 0
        if self._number_of_rows > 0:
            self._number_of_columns = len(self._raw_state[0])

        self._control_zone = current_control_zone
        self._control_zone_opponent = []
        self._update_control_zone_opponent()

        self._state_score = 0

        self._raw_order = raw_order
        self._state_player = state_player
        self._update_cells()

    def _update_cells(self):
        self._cells = []
        for row in range(self._number_of_rows):
            self._cells.insert(row, [])
            for column in range(self._number_of_columns):
                raw_cell_state = self._raw_state[row][column]
                cell_state = CellState(raw_cell_state)
                cell = ObservationCell(row, column, cell_state)
                self._cells[row].insert(column, cell)

    def _update_control_zone_opponent(self):
        control_zone_opponent = []
        for row in range(self._number_of_rows):
            for column in range(self._number_of_columns):
                if (row, column) not in self._control_zone:
                    control_zone_opponent.append((row, column))

        self._control_zone_opponent = control_zone_opponent

    def get_state(self):
        return self._raw_state

    def get_control_zone(self):
        return self._control_zone

    def get_order(self):
        return self._raw_order

    def get_state_player(self):
        return self._state_player

    def get_number_of_rows(self):
        return self._number_of_rows

    def get_number_of_columns(self):
        return self._number_of_columns

    def is_valid_row(self, row):
        if row < 0 or row > (self.get_number_of_rows() - 1):
            return False
        return True

    def is_valid_column(self, column):
        if column < 0 or column > (self.get_number_of_columns() - 1):
            return False
        return True

    # def get_cell(self, row, column) -> Optional[ObservationCell]:
    def get_cell(self, row, column):
        if not self.is_valid_row(row) or not self.is_valid_column(column):
            return None
        # cell_state = self._raw_state[row][column]
        # return ObservationCell(row, column, cell_state)
        return self._cells[row][column]

    # def get_cell_by_cell_instance(self, cell: ObservationCell) -> Optional[ObservationCell]:
    def get_cell_by_cell_instance(self, cell):
        if cell is None:
            return None
        return self.get_cell(cell.get_row(), cell.get_column())

    def update_cell(self, row, column, new_state):
        if not self.is_valid_row(row) or not self.is_valid_column(column):
            return
        # self._raw_state[row][column] = ObservationCell(row, column, new_state)
        self._cells[row][column] = ObservationCell(row, column, new_state)
        return self._cells[row][column]

    def update_new_cell(self, new_cell: ObservationCell):
        return self.update_cell(new_cell.get_row(), new_cell.get_column(), new_cell.get_state())

    def update_cell_as_sick(self, sick_cell: ObservationCell, turn):
        new_sick_cell_state = CellState(CELL_STATES['S'])
        new_sick_cell_state.update_turn(turn)
        new_sick_cell = ObservationCell(sick_cell.get_row(), sick_cell.get_column(), new_sick_cell_state)
        return self.update_new_cell(new_sick_cell)

    def update_cell_as_healthy(self, sick_cell: ObservationCell):
        new_healthy_cell_state = CellState(CELL_STATES['H'])
        new_healthy_cell = ObservationCell(sick_cell.get_row(), sick_cell.get_column(), new_healthy_cell_state)
        return self.update_new_cell(new_healthy_cell)

    def update_cell_as_quarantine(self, sick_cell: ObservationCell, turn):
        new_quarantine_cell_state = CellState(CELL_STATES['Q'])
        new_quarantine_cell_state.update_turn(turn)
        new_quarantine_cell = ObservationCell(sick_cell.get_row(), sick_cell.get_column(), new_quarantine_cell_state)
        return self.update_new_cell(new_quarantine_cell)

    def evaluate_our_state_score(self):
        eval_state_score = 0
        for (i, j) in self._control_zone:
            eval_state_score += self._evaluate_cell_score(self.get_cell(i, j))

        return eval_state_score

    def evaluate_opponent_state_score(self):
        eval_state_score = 0
        for (i, j) in self._control_zone_opponent:
            eval_state_score += self._evaluate_cell_score(self.get_cell(i, j))

        return eval_state_score

    # def _evaluate_cell_score(self, cell: ObservationCell):
    def _evaluate_cell_score(self, cell):
        if cell is None:
            return 0

        cell_state = cell.get_state()
        if cell_state is None:
            return 0

        cell_state_key = cell_state.get_state_key()
        if cell_state_key == CELL_STATES['H']:
            return 1

        if cell_state_key == CELL_STATES['I']:
            return 1

        if cell_state_key == CELL_STATES['S']:
            return -1

        if cell_state_key == CELL_STATES['Q']:
            return -5

        return 0

    # def is_valid_cell(self, cell: ObservationCell):
    def is_valid_cell(self, cell):
        return self.is_cell_in_observation_control_zone(cell)

    # def is_cell_in_observation(self, cell: ObservationCell):
    def is_cell_in_observation(self, cell):
        pass

    # def is_cell_in_observation_control_zone(self, cell: ObservationCell):
    def is_cell_in_observation_control_zone(self, cell):
        return cell.get_position_tuple() in self._control_zone

    # def apply_elementary_action(self, elementary_action: PossibleElementaryCellAction):
    def apply_elementary_action(self, elementary_action):
        target_cell = elementary_action.get_cell()
        if not self.is_valid_cell(target_cell):
            return None

        target_action = elementary_action.get_action()

        new_state = ObservationState.create_instance_by_existing_instance(self)

        updated_cell = new_state.get_cell(target_cell.get_row(), target_cell.get_column())
        if not updated_cell.is_action_valid(target_action):
            return None

        updated_cell.apply_action(target_action)
        new_state.update_new_cell(updated_cell)
        return new_state

    def is_cell_position_in_our_control_zone(self, row, column):
        position = (row, column)
        return position in self._control_zone

    # def get_cell_neighbors_cells(self, cell: ObservationCell):
    def get_cell_neighbors_cells(self, cell):
        list_neighbors = []

        right_neighbor = cell.get_neighbor_cell_instance(
            NEIGHBORS_CELLS['RIGHT']
        )
        right_neighbor = self.get_cell_by_cell_instance(right_neighbor)

        left_neighbor = cell.get_neighbor_cell_instance(
            NEIGHBORS_CELLS['LEFT']
        )
        left_neighbor = self.get_cell_by_cell_instance(left_neighbor)

        down_neighbor = cell.get_neighbor_cell_instance(
            NEIGHBORS_CELLS['DOWN']
        )
        down_neighbor = self.get_cell_by_cell_instance(down_neighbor)

        top_neighbor = cell.get_neighbor_cell_instance(
            NEIGHBORS_CELLS['TOP']
        )
        top_neighbor = self.get_cell_by_cell_instance(top_neighbor)

        if right_neighbor is not None:
            list_neighbors.append(right_neighbor)

        if left_neighbor is not None:
            list_neighbors.append(left_neighbor)

        if down_neighbor is not None:
            list_neighbors.append(down_neighbor)

        if top_neighbor is not None:
            list_neighbors.append(top_neighbor)

        return list_neighbors

    # def get_cell_neighbors_cells_states_map(self, cell: ObservationCell):
    def get_cell_neighbors_cells_states_map(self, cell):
        map_states = {}
        list_neighbors = self.get_cell_neighbors_cells(cell)
        for neighbor in list_neighbors:
            neighbor_state_key = neighbor.get_state().get_state_key()
            if neighbor_state_key not in map_states:
                map_states[neighbor_state_key] = []
            map_states[neighbor_state_key].append(neighbor)

        return map_states

    # ref:def change_state(self): in main
    # def get_new_observation_state_after_virus_spread(self, input_current_state: ObservationState,
    #                                                  list_last_3_states: List[ObservationState]):
    def get_new_observation_state_after_virus_spread(self, input_current_state, list_last_3_states):
        # new_state = deepcopy(self.state)
        new_state = ObservationState.create_instance_by_existing_instance(self)

        # virus spread
        for row in range(new_state.get_number_of_rows()):
            for column in range(new_state.get_number_of_columns()):
                current_cell = new_state.get_cell(row, column)
                new_state = self.progress_cell_state_transition(current_cell, input_current_state, list_last_3_states,
                                                                new_state)

        return new_state

    # def progress_cell_state_transition(self, current_cell: ObservationCell, input_current_state: ObservationState,
    #                                    list_last_3_states: List[ObservationState], new_state: ObservationState):
    def progress_cell_state_transition(self, current_cell, input_current_state, list_last_3_states, new_state):
        # virus spread
        if current_cell is None:
            return new_state

        cell_state = current_cell.get_state()
        if cell_state is None:
            return new_state

        state_key = cell_state.get_state_key()

        prev_state_m1 = input_current_state
        prev_state_m2 = None
        prev_state_m3 = None

        len_list_prev_states = len(list_last_3_states)
        if len_list_prev_states >= 1:
            prev_state_m2 = list_last_3_states[0]

        if len_list_prev_states >= 2:
            prev_state_m3 = list_last_3_states[1]

        # prev_cell_m1 - is what we got at the beginning of the act()
        prev_cell_m1 = prev_state_m1.get_cell_by_cell_instance(current_cell)
        # meaning, prev_cell_m1 == 'S'
        prev_cell_m2 = None
        if prev_state_m2 is not None:
            prev_cell_m2 = prev_state_m2.get_cell_by_cell_instance(current_cell)

        prev_cell_m3 = None
        if prev_state_m3 is not None:
            prev_cell_m3 = prev_state_m3.get_cell_by_cell_instance(current_cell)

        # prev_cell_m1_state_key = prev_cell_m1.get_state().get_state_key()
        prev_cell_m1_state = prev_cell_m1.get_state()
        prev_cell_m1_state_key = None
        if prev_cell_m1_state is not None:
            prev_cell_m1_state_key = prev_cell_m1_state.get_state_key()

        if state_key == CELL_STATES['H']:
            neighbors_states_map = new_state.get_cell_neighbors_cells_states_map(current_cell)
            # if 'S' in neighbors_states_map:
            if CELL_STATES['S'] in neighbors_states_map:
                new_state.update_cell_as_sick(current_cell, 1)
                return new_state

        if state_key == CELL_STATES['S']:
            # turn = int(self.state[(i, j)][1])
            # turn = None

            if prev_cell_m2 is None:
                # not m2 state
                new_sick_cell = new_state.update_cell_as_sick(current_cell, 2)
                return new_state

            # prev_cell_m2_state_key = prev_cell_m2.get_state().get_state_key()
            prev_cell_m2_state = prev_cell_m2.get_state()
            prev_cell_m2_state_key = None
            if prev_cell_m2_state is not None:
                prev_cell_m2_state_key = prev_cell_m2_state.get_state_key()

            if prev_cell_m2_state_key == CELL_STATES['H']:
                new_sick_cell = new_state.update_cell_as_sick(current_cell, 2)
                return new_state

            if prev_cell_m2_state_key == CELL_STATES['S']:
                if prev_cell_m3 is None:
                    new_sick_cell = new_state.update_cell_as_sick(current_cell, 3)
                    return new_state

                # prev_cell_m3_state_key = prev_cell_m3.get_state().get_state_key()
                prev_cell_m3_state = prev_cell_m3.get_state()
                prev_cell_m3_state_key = None
                if prev_cell_m3_state is not None:
                    prev_cell_m3_state_key = prev_cell_m3_state.get_state_key()

                if prev_cell_m3_state_key == CELL_STATES['H']:
                    new_sick_cell = new_state.update_cell_as_sick(current_cell, 3)
                    return new_state

                if prev_cell_m3_state_key == CELL_STATES['S']:
                    new_healthy_cell = new_state.update_cell_as_healthy(current_cell)
                    return new_state

            # if turn < 3:
            #     new_state[(i, j)] = 'S' + str(turn + 1)
            # else:
            #     new_state[(i, j)] = 'H'

        if state_key == CELL_STATES['Q']:
            if prev_cell_m1_state_key == CELL_STATES['S']:
                new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 1)
                return new_state

            if prev_cell_m1_state_key == CELL_STATES['Q']:
                new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 2)
                return new_state

            if prev_cell_m2 is None:
                # new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 2)
                new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 1)
                return new_state

            # prev_cell_m2_state_key = prev_cell_m2.get_state().get_state_key()
            prev_cell_m2_state = prev_cell_m2.get_state()
            prev_cell_m2_state_key = None
            if prev_cell_m2_state is not None:
                prev_cell_m2_state_key = prev_cell_m2_state.get_state_key()

            if prev_cell_m2_state_key == CELL_STATES['Q']:
                new_healthy_cell = new_state.update_cell_as_healthy(current_cell)
                return new_state

            if prev_cell_m2_state_key == CELL_STATES['H']:
                new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 1)
                return new_state

            if prev_cell_m2_state_key == CELL_STATES['S']:
                if prev_cell_m1_state_key == CELL_STATES['S']:
                    new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 1)
                    return new_state

                if prev_cell_m1_state_key == CELL_STATES['Q']:
                    new_quarantine_cell = new_state.update_cell_as_quarantine(current_cell, 2)
                    return new_state

        return new_state


class PossibleFullAction:
    # def __init__(self, list_elementary_actions: List[PossibleElementaryCellAction], available_actions):
    def __init__(self, list_elementary_actions, available_actions):
        self._list_elementary_actions = list_elementary_actions
        self._available_actions = available_actions
        self._map_possible_actions = self.get_map_possible_actions()
        self._map_possible_actions_numbers = {}
        self._update_map_possible_actions_numbers()

    def _update_map_possible_actions_numbers(self):
        for possible_action in self._map_possible_actions:
            self._map_possible_actions_numbers[possible_action] = len(self._map_possible_actions[possible_action])

    def get_action_tuple(self):
        full_action_tuple = []
        for elementary_action in self._list_elementary_actions:
            if elementary_action is None:
                continue
            action_tuple = elementary_action.get_action_tuple()
            if action_tuple is None:
                continue
            full_action_tuple.append(action_tuple)

        # TODO: check if tuple or list
        # return tuple(full_action_tuple)
        return full_action_tuple

    def get_list_elementary_actions(self):
        return self._list_elementary_actions

    def get_map_possible_actions(self):
        map_actions = {}
        for current_elementary_action in self._list_elementary_actions:
            current_action = current_elementary_action.get_action()
            if current_action is None:
                continue

            # if current_action not in AGENT_ACTIONS.values():
            #     continue

            if current_action not in map_actions:
                map_actions[current_action] = []

            # update! should be probably a list
            # map_actions[current_action] = current_elementary_action
            map_actions[current_action].append(current_elementary_action)

        return map_actions

    def is_valid_list_of_elementary_actions(self):
        for possible_action in self._map_possible_actions_numbers:
            # if self._available_actions[possible_action] is None:
            if possible_action not in self._available_actions:
                return False

            if self._available_actions[possible_action] is None:
                return False

            if self._available_actions[possible_action] < 1:
                return False

            if self._map_possible_actions_numbers[possible_action] > self._available_actions[possible_action]:
                return False

        return True

    def check_if_contains_elementary_action(self, elemenatary_action_name):
        for elementary_action in self._list_elementary_actions:
            if elementary_action.get_action() == elemenatary_action_name:
                return True

        return False


class PossibleStatesHandler:

    # removed args:, zone_of_control, order
    # def __init__(self, current_state: ObservationState, available_actions):
    def __init__(self, current_state, available_actions):
        self._current_state = current_state
        self._map_available_cells_states = {}
        # TODO: check if need other states
        self._map_available_cells_for_action = self._get_map_available_cells_for_action()
        self._available_actions = available_actions
        # self._list_last_3_states: List[ObservationState] = []
        self._list_last_3_states = []

    def _get_map_available_cells_for_action(self):
        cells_map = {}
        for row in range(self._current_state.get_number_of_rows()):
            for column in range(self._current_state.get_number_of_columns()):
                if not self.is_cell_position_in_our_control_zone(row, column):
                    continue

                current_cell = self._current_state.get_cell(row, column)
                if current_cell is None:
                    continue

                cell_state = current_cell.get_state()
                if cell_state is None:
                    continue
                cell_state_key = cell_state.get_state_key()
                if cell_state_key in [CELL_STATES['H'], CELL_STATES['S']]:
                    if cell_state_key not in cells_map:
                        cells_map[cell_state_key] = []
                    cells_map[cell_state_key].append(current_cell)

        return cells_map

    # TODO: check if this method needed
    def is_cell_position_in_our_control_zone(self, row, column):
        return self._current_state.is_cell_position_in_our_control_zone(row, column)

    def _get_available_cells_by_state(self, cell_state):
        if cell_state not in self._map_available_cells_for_action:
            return []

        # list_cells = []
        # for current_cell in self._map_available_cells_for_action[cell_state]:
        #     list_cells.append(current_cell)
        #
        # return list_cells
        # check type() is list
        return self._map_available_cells_for_action[cell_state]

    # def apply_full_action_on_state(self, state: ObservationState, action: PossibleFullAction):
    def apply_full_action_on_state(self, state, action):
        if action is None:
            return None

        if not action.is_valid_list_of_elementary_actions():
            return None

        # new_state = ObservationState.create_instance_by_existing_instance(self._current_state)
        new_state = ObservationState.create_instance_by_existing_instance(state)
        new_next_possible_state = None
        # for possible_action in action.get_list_elementary_actions():
        #     new_state = new_state.apply_elementary_action(possible_action)
        #     full_action = PossibleFullAction([possible_action], self._available_actions)
        #     #new_next_possible_state = NextPossibleObservationState(new_state, self._current_state, full_action)
        #     new_next_possible_state = NextPossibleObservationState(new_state, state, full_action)

        list_active_actions = []
        for possible_action in action.get_list_elementary_actions():
            new_state = new_state.apply_elementary_action(possible_action)
            list_active_actions.append(possible_action)

        # full_action = PossibleFullAction([possible_action], self._available_actions)
        # new_next_possible_state = NextPossibleObservationState(new_state, self._current_state, full_action)
        full_action = PossibleFullAction(list_active_actions, self._available_actions)
        new_next_possible_state = NextPossibleObservationState(new_state, state, full_action)

        # TODO: spread the disease if second
        return new_next_possible_state

    # def set_list_last_3_states(self, list_last_3_states: List[ObservationState]):
    def set_list_last_3_states(self, list_last_3_states):
        self._list_last_3_states = list_last_3_states

    # def get_map_cells_with_max_healthy_neighbors_in_our_zoc(self, cells_list: List[ObservationCell]):
    def get_map_cells_with_max_healthy_neighbors_in_our_zoc(self, cells_list):
        map_cells_with_max_healthy_neighbors_in_our_zoc = {}
        for current_cell in cells_list:
            number_of_healthy_cells_in_our_zoc = 0
            map_h_cell_neighbors_states = self._current_state.get_cell_neighbors_cells_states_map(current_cell)
            if CELL_STATES['H'] in map_h_cell_neighbors_states:
                for h_neighbor in map_h_cell_neighbors_states[CELL_STATES['H']]:
                    # TODO: check this method
                    # if self._current_state.is_cell_position_in_our_control_zone(h_neighbor):
                    #     number_of_healthy_cells_in_our_zoc += 1
                    # is_cell_in_observation_control_zone
                    if self._current_state.is_cell_in_observation_control_zone(h_neighbor):
                        number_of_healthy_cells_in_our_zoc += 1

            if number_of_healthy_cells_in_our_zoc > 0:
                if number_of_healthy_cells_in_our_zoc not in map_cells_with_max_healthy_neighbors_in_our_zoc:
                    map_cells_with_max_healthy_neighbors_in_our_zoc[number_of_healthy_cells_in_our_zoc] = []
                map_cells_with_max_healthy_neighbors_in_our_zoc[number_of_healthy_cells_in_our_zoc].append(current_cell)

        return map_cells_with_max_healthy_neighbors_in_our_zoc

    def get_list_with_max_numeric_key_in_map(self, map_cells_list_by_keys):
        max_list = []
        if map_cells_list_by_keys is None:
            return []

        map_keys = map_cells_list_by_keys.keys()
        if len(map_keys) > 0:
            max_key = max(map_keys)
            # max_h_cell = map_cell_with_max_healthy_neighbors[max_key]
            max_cells_list = map_cells_list_by_keys[max_key]
            return max_cells_list

        return max_list

    def get_cell_with_max_numeric_key_in_map(self, map_cells_list_by_keys):
        selected_cell = None
        max_cells_list = self.get_list_with_max_numeric_key_in_map(map_cells_list_by_keys)
        # selected_cell = max_h_cell
        if max_cells_list is not None and len(max_cells_list) > 0:
            selected_cell = max_cells_list[0]

        return selected_cell

    # def select_default_next_state_action(self) -> PossibleFullAction:
    def select_default_next_state_action(self):
        cells_h = self._get_available_cells_by_state(CELL_STATES['H'])
        if len(cells_h) > 0:
            # selected_cell = None
            map_cell_with_max_healthy_neighbors = self.get_map_cells_with_max_healthy_neighbors_in_our_zoc(cells_h)
            selected_cell = self.get_cell_with_max_numeric_key_in_map(map_cell_with_max_healthy_neighbors)

            if selected_cell is None:
                selected_cell = cells_h[0]
                if selected_cell is None:
                    # return EMPTY_ACTION
                    return self.get_empty_possible_full_action()

            elementary_action_v = PossibleElementaryCellAction(selected_cell, AGENT_ACTIONS['v'])
            action_v = PossibleFullAction([elementary_action_v], self._available_actions)
            return action_v

        # new logic - if no H cells in next state then empty action
        # skip quarantine for this step/state
        # TODO: check if this new logic is OK

        # cells_s = self._get_available_cells_by_state(CELL_STATES['S'])
        # # should be sick cells while playing
        # if len(cells_s) > 0:
        #     # TODO: check if need to add priority to some cells
        #     elementary_action_q = PossibleElementaryCellAction(cells_s[0], AGENT_ACTIONS['q'])
        #     action_q = PossibleFullAction([elementary_action_q], self._available_actions)
        #     return action_q

        # return None
        return self.get_empty_possible_full_action()

    # def get_empty_possible_full_action(self) -> PossibleFullAction:
    def get_empty_possible_full_action(self):
        return PossibleFullAction([], self._available_actions)

    def get_next_best_possible_state_by_current_state(self):
        next_possible_states = self.create_next_possible_states_list()
        # next_best_state: Optional[
        #     NextPossibleObservationState] = self.select_best_next_possible_state_from_list(
        #     next_possible_states)
        next_best_state = self.select_best_next_possible_state_from_list(
            next_possible_states)
        return next_best_state

    # def get_action_tuple_for_next_best_possible_state_by_current_state(self):
    #     best_next_state = self.get_next_best_possible_state_by_current_state()
    #     return self.get_action_tuple_for_next_possible_state(best_next_state)

    # def get_action_tuple_for_next_possible_state(self, next_possible_state: NextPossibleObservationState):
    def get_action_tuple_for_next_possible_state(self, next_possible_state):
        if next_possible_state is None:
            return EMPTY_ACTION

        action = next_possible_state.get_action()

        if action is None:
            # return None
            return EMPTY_ACTION

        return action.get_action_tuple()

    # def is_cell_has_sick_neighbors(self, cell: ObservationCell):
    def is_cell_has_sick_neighbors(self, cell):
        # by current state
        neighbors_cells_states_map = self._current_state.get_cell_neighbors_cells_states_map(cell)
        return CELL_STATES['S'] in neighbors_cells_states_map

    # def eliminate_healthy_cells_from_action_vaccinate(self, list_h: List[ObservationCell]):
    def eliminate_healthy_cells_from_action_vaccinate(self, list_h):
        # by current state
        new_h_list = []
        for current_h_cell in list_h:
            if self.is_cell_has_sick_neighbors(current_h_cell):
                new_h_list.append(current_h_cell)

        if len(new_h_list) == 0:
            if len(list_h) > 0:
                # return [list_h[0]]
                map_cell_with_max_healthy_neighbors = self.get_map_cells_with_max_healthy_neighbors_in_our_zoc(list_h)
                # selected_cell = self.get_cell_with_max_numeric_key_in_map(map_cell_with_max_healthy_neighbors)
                max_cells_list = self.get_list_with_max_numeric_key_in_map(map_cell_with_max_healthy_neighbors)
                if max_cells_list is not None and len(max_cells_list) > 0:
                    return max_cells_list

                return list_h

            return []

        map_cell_with_max_healthy_neighbors = self.get_map_cells_with_max_healthy_neighbors_in_our_zoc(new_h_list)
        # selected_cell = self.get_cell_with_max_numeric_key_in_map(map_cell_with_max_healthy_neighbors)
        max_cells_list = self.get_list_with_max_numeric_key_in_map(map_cell_with_max_healthy_neighbors)
        if max_cells_list is not None and len(max_cells_list) > 0:
            return max_cells_list

        return new_h_list

    # def eliminate_sick_cells_from_action_quarantine(self, list_s: List[ObservationCell]):
    def eliminate_sick_cells_from_action_quarantine(self, list_s):
        # by current state
        new_s_list = []
        map_healthy_neighbors_numbers = {}
        for current_s_cell in list_s:
            neighbors_cells_states_map = self._current_state.get_cell_neighbors_cells_states_map(current_s_cell)
            if CELL_STATES['H'] not in neighbors_cells_states_map:
                continue

            # our zone of control
            # is_healthy_cells_in_our_zoc = None
            number_of_healthy_neighbors_cells_in_our_zoc = 0
            for test_h_cell in neighbors_cells_states_map[CELL_STATES['H']]:
                if self._current_state.is_cell_in_observation_control_zone(test_h_cell):
                    # is_healthy_cells_in_our_zoc = True
                    # break
                    number_of_healthy_neighbors_cells_in_our_zoc += 1

            # if is_healthy_cells_in_our_zoc is True:
            if number_of_healthy_neighbors_cells_in_our_zoc > 0:
                # new_s_list.append(current_s_cell)
                # number_of_healthy_neighbors = len(neighbors_cells_states_map[CELL_STATES['H']])
                # if number_of_healthy_neighbors not in map_healthy_neighbors_numbers:
                if number_of_healthy_neighbors_cells_in_our_zoc not in map_healthy_neighbors_numbers:
                    map_healthy_neighbors_numbers[number_of_healthy_neighbors_cells_in_our_zoc] = []
                map_healthy_neighbors_numbers[number_of_healthy_neighbors_cells_in_our_zoc].append(current_s_cell)

        # take sick cell with max number of healthy neighbors
        map_keys = map_healthy_neighbors_numbers.keys()
        if len(map_keys) > 0:
            # take sick cell with max healthy neighbors
            max_number = max(map_keys)
            # sick_cell = map_healthy_neighbors_numbers[max_number][0]
            sick_cells_list = map_healthy_neighbors_numbers[max_number]
            if sick_cells_list is not None and len(sick_cells_list) > 0:
                # sick_cell = sick_cells_list[0]
                # new_s_list.append(sick_cell)

                return sick_cells_list

        # if len(new_s_list) == 0:
        #     return new_s_list

        return new_s_list

    def get_next_elementary_actions_v(self):
        elementary_v = []
        # TODO: add logic for examining if action should be applied
        # if self._available_actions[AGENT_ACTIONS['v']] is not None:
        if AGENT_ACTIONS['v'] in self._available_actions:
            if self._available_actions[AGENT_ACTIONS['v']] > 0:
                list_h = self._get_available_cells_by_state(CELL_STATES['H'])
                list_h = self.eliminate_healthy_cells_from_action_vaccinate(list_h)
                for cell_h in list_h:
                    possible_action_v = PossibleElementaryCellAction(cell_h, AGENT_ACTIONS['v'])
                    # possible_full_action_v = PossibleFullAction([possible_action_v],self._available_actions)
                    elementary_v.append(possible_action_v)

        return elementary_v

    def get_next_elementary_actions_q(self):
        elementary_q = []
        # if self._available_actions[AGENT_ACTIONS['q']] is not None:
        if AGENT_ACTIONS['q'] in self._available_actions:
            if self._available_actions[AGENT_ACTIONS['q']] > 0:
                list_s = self._get_available_cells_by_state(CELL_STATES['S'])
                list_s = self.eliminate_sick_cells_from_action_quarantine(list_s)
                for cell_s in list_s:
                    possible_action_q = PossibleElementaryCellAction(cell_s, AGENT_ACTIONS['q'])
                    # possible_full_action_q = PossibleFullAction([possible_action_q],self._available_actions)
                    elementary_q.append(possible_action_q)

        return elementary_q

    def get_next_full_actions_vq(self, elementary_v, elementary_q):
        # elementary_vq
        elementary_vq = []
        for possible_action_v in elementary_v:
            for possible_action_q in elementary_q:
                elementary_vq.append(
                    PossibleFullAction([possible_action_v, possible_action_q], self._available_actions))

        return elementary_vq

    def get_next_full_actions_qq(self, elementary_q):
        # elementary_qq
        elementary_qq = []
        for possible_action_q1 in elementary_q:
            for possible_action_q2 in elementary_q:
                row1 = possible_action_q1.get_cell().get_row()
                column1 = possible_action_q1.get_cell().get_column()
                row2 = possible_action_q2.get_cell().get_row()
                column2 = possible_action_q2.get_cell().get_column()
                if row1 == row2 and column1 == column2:
                    continue
                elementary_qq.append(
                    PossibleFullAction([possible_action_q1, possible_action_q2], self._available_actions))

        return elementary_qq

    def get_next_full_actions_vqq(self, elementary_v, elementary_q):
        # elementary_vqq
        full_vqq = []
        for possible_action_v in elementary_v:
            for possible_action_q1 in elementary_q:
                for possible_action_q2 in elementary_q:
                    row1 = possible_action_q1.get_cell().get_row()
                    column1 = possible_action_q1.get_cell().get_column()
                    row2 = possible_action_q2.get_cell().get_row()
                    column2 = possible_action_q2.get_cell().get_column()
                    if row1 == row2 and column1 == column2:
                        continue
                    full_vqq.append(
                        PossibleFullAction([possible_action_v, possible_action_q1, possible_action_q2],
                                           self._available_actions))

        return full_vqq

    def create_next_possible_states_list(self):
        next_possible_states = []

        # TODO: add logic for examining if action should be applied
        elementary_v = self.get_next_elementary_actions_v()
        elementary_q = self.get_next_elementary_actions_q()

        # [[l,n] for l in list1 for n in list2]
        # additional lists
        full_vq = self.get_next_full_actions_vq(elementary_v, elementary_q)
        # full_qq = self.get_next_full_actions_qq(elementary_q)
        full_vqq = self.get_next_full_actions_vqq(elementary_v, elementary_q)

        # for possible_action_v in elementary_v:
        #     possible_full_action_v = PossibleFullAction([possible_action_v], self._available_actions)
        #     new_state = self.apply_full_action_on_state(self._current_state, possible_full_action_v)
        #     if new_state is None:
        #         continue
        #
        #     next_possible_states.append(new_state)

        # for possible_action_q in elementary_q:

        # ref good: list_full_actions = elementary_v + elementary_q
        # ref good!!:  list_full_actions = elementary_v + full_vq

        # list_full_actions = elementary_v + elementary_q + elementary_qq + elementary_vq + elementary_vqq

        # good: list_full_actions = elementary_v + full_vq
        # list_full_actions = full_vqq

        list_full_actions = elementary_v

        # TODO: check if need to included elementary_q
        # new logic - adding test for elementary_q
        # if len(elementary_q) < 3:
        #     list_full_actions += elementary_q
        # else:
        #     list_full_actions += elementary_q[0:3]

        # TODO: return after tests
        if len(elementary_q) < 3:
            # recommended value is 3
            list_full_actions += full_vqq
        elif len(elementary_q) < 5:
            # recommended value is 5
            list_full_actions += full_vq

        for possible_action in list_full_actions:
            # new_state = None
            if isinstance(possible_action, PossibleFullAction):
                new_state = self.apply_full_action_on_state(self._current_state, possible_action)
            elif isinstance(possible_action, PossibleElementaryCellAction):
                possible_full_action = PossibleFullAction([possible_action], self._available_actions)
                new_state = self.apply_full_action_on_state(self._current_state, possible_full_action)
            else:
                continue
            if new_state is None:
                continue

            next_possible_states.append(new_state)

        return next_possible_states

    def select_best_next_possible_state_from_list(self, list_next_possible_states):
        best_possible_state = None
        # action_max_scores_diff = None
        # action_max_our_score = None
        max_scores_diff = -math.inf
        for next_possible_state in list_next_possible_states:
            if next_possible_state is None:
                continue

            state = next_possible_state.get_state()
            if state is None:
                continue

            # TODO: check
            if state.get_order() == PLAY_ORDERS['SECOND']:
                # TODO: check if needed -  new test options - storing spread
                # next_possible_state.set_is_spread_performed(True)
                # next_possible_state.set_state_before_spread(state)

                state = state.get_new_observation_state_after_virus_spread(self._current_state,
                                                                           self._list_last_3_states)

            state_score_our = state.evaluate_our_state_score()
            state_score_opponent = state.evaluate_opponent_state_score()
            states_score_delta = state_score_our - state_score_opponent

            if states_score_delta > max_scores_diff:
                max_scores_diff = states_score_delta
                best_possible_state = next_possible_state

        return best_possible_state

    # def check_for_quarantine(self, next_possible_state: NextPossibleObservationState):
    def check_for_quarantine(self, next_possible_state):
        new_possible_state = NextPossibleObservationState.create_instance_by_existing_instance(next_possible_state)
        current_action = new_possible_state.get_action()
        # check if contains quarantine action
        if not current_action.check_if_contains_elementary_action(AGENT_ACTIONS['q']):
            # add best quarantine action for state
            # observation_state = new_possible_state.get_state()
            # new_observation_state = observation_state.get_best_quarantine_action_for_current_state()
            # new_possible_state.set_state(new_observation_state)
            # new_possible_state = self.get_best_quarantine_action_for_state(new_possible_state)
            if new_possible_state.get_is_spread_performed():
                new_states_handler = PossibleStatesHandler(new_possible_state.get_state_before_spread(),
                                                           self._available_actions)
            else:
                new_states_handler = PossibleStatesHandler(new_possible_state.get_state(), self._available_actions)

            new_possible_state = new_states_handler.get_best_quarantine_action_for_state(new_possible_state)

        return new_possible_state

    # def get_best_quarantine_action_for_state(self, next_possible_state: NextPossibleObservationState):
    def get_best_quarantine_action_for_state(self, next_possible_state):

        # new_state = ObservationState.create_instance_by_existing_instance(next_possible_state.get_state())
        # if next_possible_state.get_is_spread_performed():
        # check state before spread

        list_s = self._get_available_cells_by_state(CELL_STATES['S'])
        list_s = self.eliminate_sick_cells_from_action_quarantine(list_s)
        # possible to take the max
        list_test_states = []
        best_state = next_possible_state
        for test_s_cell in list_s:
            possible_q_action = PossibleElementaryCellAction(test_s_cell, AGENT_ACTIONS['q'])
            possible_full_action = PossibleFullAction([possible_q_action], self._available_actions)
            new_test_state = self.apply_full_action_on_state(self._current_state, possible_full_action)
            if new_test_state is None:
                continue
            list_test_states.append(new_test_state)

        max_scores_diff = -math.inf
        for test_next_possible_state in list_test_states:
            test_state = test_next_possible_state.get_state()
            if test_state is None:
                continue

            if test_state.get_order() == PLAY_ORDERS['SECOND']:
                # TODO: check if needed -  new test options - storing spread
                # next_possible_state.set_is_spread_performed(True)
                # next_possible_state.set_state_before_spread(state)
                test_state = test_state.get_new_observation_state_after_virus_spread(self._current_state,
                                                                                     self._list_last_3_states)

            state_score_our = test_state.evaluate_our_state_score()
            state_score_opponent = test_state.evaluate_opponent_state_score()
            states_score_delta = state_score_our - state_score_opponent

            if states_score_delta > max_scores_diff:
                max_scores_diff = states_score_delta
                # best_state = next_possible_state
                best_state = test_next_possible_state

        return best_state


class NextPossibleObservationState:

    # def create_instance_by_existing_instance(existing_instance: NextPossibleObservationState):
    @staticmethod
    def create_instance_by_existing_instance(existing_instance):
        new_instance = NextPossibleObservationState(existing_instance.get_state(),
                                                    existing_instance.get_previous_state(),
                                                    existing_instance.get_action())
        return new_instance

    # def __init__(self, state: ObservationState, previous_state: ObservationState, action: PossibleFullAction):
    def __init__(self, state, previous_state, action):
        self._state = state
        self._action = action
        self._previous_state = previous_state
        # new test properties
        self._is_spread_performed = False
        self._state_before_spread = None

    def get_state(self):
        return self._state

    def get_previous_state(self):
        return self._previous_state

    # def get_action(self) -> PossibleFullAction:
    def get_action(self):
        return self._action

    # def set_state(self,new_state:ObservationState):
    def set_state(self, new_state):
        self._state = new_state

    # def set_is_spread_performed(self, is_spread_performed):
    #     self._is_spread_performed = is_spread_performed
    #
    # def set_state_before_spread(self,state_before_spread:ObservationState):
    #     self._state_before_spread = state_before_spread

    def get_is_spread_performed(self):
        return self._is_spread_performed

    def get_state_before_spread(self):
        return self._state_before_spread

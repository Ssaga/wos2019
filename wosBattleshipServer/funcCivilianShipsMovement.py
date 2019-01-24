import time
import collections
import copy
import numpy as np
import enum

from cCommonGame import ShipInfo
from cCommonGame import Boundary

from wosBattleshipServer.cCommon import PlayerStatus
from wosBattleshipServer.cCommon import check_collision

from wosBattleshipServer.funcCivilianShipsGeneration import civilian_ship_generation
from wosBattleshipServer.funcIslandGeneration import generate_island


class ShipMoveType(enum.IntEnum):
    FORWARD = 0
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = 2


def civilian_ship_movement(ship_info_list,
                           map_data_array,
                           player_status_dict=dict(),
                           boundary_layer_dict=dict(),
                           move_possibility=0.25):
    if isinstance(ship_info_list, collections.Iterable) and \
            isinstance(map_data_array, np.ndarray) and \
            isinstance(player_status_dict, dict) and \
            isinstance(boundary_layer_dict, dict):

        # Generate the mask for the island and player ship
        island_player_ships = copy.deepcopy(map_data_array)
        for player_id in player_status_dict.keys():
            player_status = player_status_dict[player_id]
            if isinstance(player_status, PlayerStatus):
                for ship_info in player_status.ship_list:
                    if not ship_info.is_sunken:
                        for pos in ship_info.area:
                            island_player_ships[pos[0], pos[1]] = 2
                        # end of for..loop for ship position
                # end of for..loop for ship list
        # end of for..loop for player status list

        # for all the civilian ship
        for ship_info in ship_info_list:
            if isinstance(ship_info, ShipInfo):
                if not ship_info.is_sunken:
                    # check if the ship has the chance to
                    if np.random.rand() < move_possibility:

                        ship_boundary_layer = None
                        # get the sector the ship is in
                        for key in boundary_layer_dict.keys():
                            boundary_layer = boundary_layer_dict[key]
                            if isinstance(boundary_layer, np.ndarray):
                                if boundary_layer[int(ship_info.position.x), int(ship_info.position.y)]:
                                    ship_boundary_layer = np.invert(boundary_layer)

                        island_other_ships = copy.deepcopy(island_player_ships)
                        other_civilian_ships = [value for value in ship_info_list if
                                                value is not ship_info and not value.is_sunken]
                        for other_civilian_ship in other_civilian_ships:
                            if isinstance(other_civilian_ship, ShipInfo):
                                for pos in other_civilian_ship.area:
                                    island_other_ships[pos[0], pos[1]] = 3
                                # end of for..loop for ship position
                        # end of for..loop for ship list

                        # generate the action to perform
                        action = np.random.randint(0, len(ShipMoveType))
                        action = ShipMoveType(action)

                        # make a copy of the ship
                        tmp_ship_info = copy.deepcopy(ship_info)

                        if action == ShipMoveType.FORWARD:
                            # Move the ship forward
                            tmp_ship_info.move_forward()
                        elif action == ShipMoveType.CLOCKWISE:
                            # Turn the ship clockwise
                            tmp_ship_info.turn_clockwise()
                        elif action == ShipMoveType.COUNTER_CLOCKWISE:
                            # Turn the ship anti-clockwise
                            tmp_ship_info.turn_counter_clockwise()

                        # get the obstacle for the ship
                        obstacle_dict = dict()
                        obstacle_dict["Island_Ship"] = island_other_ships
                        if isinstance(ship_boundary_layer, np.ndarray):
                            obstacle_dict["Boundary"] = ship_boundary_layer

                        # Check if civilian ship hit any obstacle
                        is_ok = check_collision(tmp_ship_info, obstacle_dict)

                        # update the civilian ship on its new position
                        if is_ok:
                            ship_info.heading = tmp_ship_info.heading
                            ship_info.position = tmp_ship_info.position
                            ship_info.area = tmp_ship_info.area
                        else:
                            print("Civilian ship %s is unable to move %s" % (ship_info.ship_id, action.name))
                    else:
                        print("Civilian ship %s do not have the chance to move" % ship_info.ship_id)
                else:
                    print("Civilian ship %s unable to move as it has sunk" % ship_info.ship_id)

        # end of for..loop for the list of civilian ships
    else:
        raise ValueError("Incorrect input parameters")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    print("Test civilian_ship_generation")
    board_size = np.array([20, 20])
    island_layer = np.zeros(board_size.tolist())
    pos = tuple(np.divide(board_size, 2).astype(int).tolist())
    generate_island(island_layer, pos, 10)

    civilian_ship_list = []
    boundary_dict = dict()
    print(civilian_ship_list)
    x_div = 2
    y_div = 2
    x_len = board_size[0] // x_div
    y_len = board_size[1] // y_div
    for i in range(x_div * y_div):
        x_min = (i // x_div) * x_len
        x_max = x_min + x_len
        y_min = (i % y_div) * y_len
        y_max = y_min + y_len
        civilian_ship_generation(civilian_ship_list,
                                 island_layer,
                                 Boundary(x_min,
                                          x_max,
                                          y_min,
                                          y_max),
                                 2)
        boundary = np.zeros(board_size, dtype=np.bool)
        boundary[x_min:x_max, y_min:y_max] = True
        boundary_dict[i] = boundary
    # print for visual
    print(civilian_ship_list)
    tmp_board = copy.deepcopy(island_layer)
    for ship_info in civilian_ship_list:
        if isinstance(ship_info, ShipInfo):
            for pos in ship_info.area:
                tmp_board[pos[0], pos[1]] = 2
    print(tmp_board.T)

    print("Test civilian_ship_movement")
    for i in range(20):
        civilian_ship_movement(civilian_ship_list, island_layer, dict(), boundary_dict, 1.0)
        # print for visual
        tmp_board = copy.deepcopy(island_layer)
        for ship_info in civilian_ship_list:
            if isinstance(ship_info, ShipInfo):
                for pos in ship_info.area:
                    tmp_board[pos[0], pos[1]] = 2
        print("-----------------------------")
        print("Turn %s:\r\n%s" % (i, tmp_board.T))

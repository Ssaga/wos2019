import time
import numpy as np
import copy

from cCommonGame import Boundary
from cCommonGame import Position
from cCommonGame import ShipInfo

from wosBattleshipServer.cCommon import check_collision

from wosBattleshipServer.funcIslandGeneration import generate_island


def civilian_ship_generation(civilian_ship_list,
                             map_data,
                             boundary,
                             num_of_civilian_ships=0):
    chance = 5
    stop_cond = len(civilian_ship_list) + num_of_civilian_ships

    if isinstance(civilian_ship_list, list) and \
            isinstance(boundary, Boundary) and \
            isinstance(map_data, np.ndarray):

        while chance > 0 and len(civilian_ship_list) < stop_cond:

            # get the size of the civilian ships
            max_ship_size = min((boundary.max_x - boundary.min_x) // 2,
                                (boundary.max_y - boundary.min_y) // 2)

            max_ship_size = min(max_ship_size, 6)                   # restrict to max of 6 or min len/width of boundary
            if max_ship_size <= 2:
                raise ValueError("Boundary is too small")
            ship_size = np.random.randint(2, max_ship_size)

            # get the position of the civilian ships
            ship_position = Position(np.random.randint(boundary.min_x + ship_size, boundary.max_x - ship_size),
                                     np.random.randint(boundary.min_y + ship_size, boundary.max_y - ship_size))

            # get the heading
            ship_head = np.random.randint(0, 4)

            # generate the ship object
            ship = ShipInfo(len(civilian_ship_list),
                            ship_position,
                            (ship_head * 90),
                            ship_size)

            # Generate the obstacle dictionary
            obstacle_dict = dict()

            # Add the island obstacle
            obstacle_dict["island"] = map_data

            # Add other civilian ships as obstacles
            other_civilian_ships = [value for value in civilian_ship_list if
                                    not value.is_sunken]
            other_ships = np.zeros(map_data.shape)
            for other_civilian_ship in other_civilian_ships:
                if isinstance(other_civilian_ship, ShipInfo):
                    for pos in other_civilian_ship.area:
                        other_ships[pos[0], pos[1]] = 1
                    # end of for..loop for ship position
            # end of for..loop for ship list
            obstacle_dict["other_civilian_ships"] = other_ships

            # check for collision
            is_ok = check_collision(ship, obstacle_dict)

            # add the ship if collision is not detected
            if is_ok:
                civilian_ship_list.append(ship)
                chance = 5
            else:
                chance = chance - 1
    else:
        raise ValueError("Invalid input parameters")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    print("Test civilian_ship_generation")
    board_size = np.array([20, 20])
    island_layer = np.zeros(board_size.tolist())
    pos = tuple(np.divide(board_size, 2).astype(int).tolist())
    generate_island(island_layer, pos, 10)

    civilian_ship_list=[]
    print(civilian_ship_list)
    x_div = 2
    y_div = 2
    x_len = board_size[0] // x_div
    y_len = board_size[1] // y_div
    for i in range(x_div * y_div):
        x_min = (i // x_div) * x_len
        y_min = (i % y_div) * y_len
        civilian_ship_generation(civilian_ship_list,
                                 island_layer,
                                 Boundary(x_min,
                                          x_min + x_len,
                                          y_min,
                                          y_min + y_len),
                                 2)
    print(civilian_ship_list)
    tmp_board = copy.deepcopy(island_layer)
    for ship_info in civilian_ship_list:
        if isinstance(ship_info, ShipInfo):
            for pos in ship_info.area:
                tmp_board[pos[0], pos[1]] = 2
    print(tmp_board)

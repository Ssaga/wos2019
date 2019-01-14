import time
import collections
import numpy as np

from cCommonGame import Boundary
from cCommonGame import Position

from wosBattleshipServer.cCommon import ShipInfo


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

            is_ok = True

            # get the size of the civilian ships
            ship_size = np.random.randint(2, 5)

            # get the position of the civilian ships
            ship_position = Position(np.random.randint(boundary.min_x + ship_size, boundary.max_x - ship_size),
                                     np.random.randint(boundary.min_y + ship_size, boundary.max_y - ship_size))

            # get the heading
            ship_head = np.random.randint(0, 3)

            # generate the ship object
            ship = ShipInfo(len(civilian_ship_list),
                            ship_position,
                            (ship_head * 90),
                            ship_size)

            # check for collision
            for pos in ship.area:
                if map_data[int(pos[0]), int(pos[1])] > 0:
                    is_ok = False

            # add the ship if collision is not detected
            if is_ok:
                civilian_ship_list.append(ship)
            else:
                chance = chance - 1
    else:
        raise ValueError("Invalid input parameters")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    civilian_ship_list=[]
    print(civilian_ship_list)
    civilian_ship_generation(civilian_ship_list, 10)
    print(civilian_ship_list)

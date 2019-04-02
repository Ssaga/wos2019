import time
import collections
import math
import numpy as np

from cCommonGame import ShipInfo
from cCommonGame import Position

def get_heading(pos_1, pos_2):
    """
    Get the heading (based on true-north) of pos_2 from pos_1
    :param pos_1: Vehicle position
    :param pos_2: Dst position to compute the heading
    :return: heading; unit in degree (0 to 360)
    """
    heading = 0
    if isinstance(pos_1, collections.Iterable) and isinstance(pos_2, collections.Iterable):
        vec_a = [0, 1]
        vec_b = [(pos_2[0] - pos_1[0]), (pos_2[1] - pos_1[1])]
        mag_a = math.sqrt((vec_a[0] * vec_a[0]) + (vec_a[1] * vec_a[1]))
        mag_b = math.sqrt((vec_b[0] * vec_b[0]) + (vec_b[1] * vec_b[1]))

        dot_product = np.dot(vec_a, vec_b)
        print("-------------------------")
        print("\tpos_1: %s" % pos_1)
        print("\tpos_2: %s" % pos_2)
        print("\tvec_a: %s" % vec_a)
        print("\tvec_b: %s" % vec_b)
        print("\tmag_a: %s" % mag_a)
        print("\tmag_b: %s" % mag_b)
        print("\tdot_product: %s" % dot_product)
        heading = math.acos(dot_product / (mag_a * mag_b))

        if (pos_2[0] - pos_1[0]) < 0:
            # pos_2 is in the 3rd or 4th quadant; hence invert the sign
            heading = -heading

        heading = heading / math.pi * 180.0
        print("\theading: %s" % heading)

        heading = ((heading + 180.0) % 360) - 180.0
        if heading < 0:
            heading += 360
        print("\theading: %s" % heading)

    return heading

if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    is_running = True

    print("Test")
    pass

    heading = get_heading([0, 0], [0, 2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [1, 2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [2, 2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [2, 1])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [2, 0])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [2, -1])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [2, -2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [1, -2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [0, -2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-1, -2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-2, -2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-2, -1])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-2, 0])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-2, 1])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-2, 2])
    print("heading: %s" % heading)

    heading = get_heading([0, 0], [-1, 2])
    print("heading: %s" % heading)

    # for y in range(-5, 6):
    #     for x in range(-5, 6):
    #         for ship_size in range(3, 6):
    #             for ship_heading in range(-360, 360, 90):
    #                 print("- %3s degree ---------" % ship_heading)
    #                 test_ship = ShipInfo(0, Position(x, y), ship_heading, ship_size, False)
    #                 for i in range(5):
    #                     print("rotate %s : %s" % (i, test_ship))
    #                     test_ship.turn_clockwise()
    #                 print("----------------------")

    print("*** END (%s)" % (time.ctime(time.time())))

import time

from cCommonGame import ShipInfo
from cCommonGame import Position

if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    is_running = True

    print("Test")
    pass

    for y in range(-5, 6):
        for x in range(-5, 6):
            for ship_size in range(3, 6):
                for ship_heading in range(-360, 360, 90):
                    print("- %3s degree ---------" % ship_heading)
                    test_ship = ShipInfo(0, Position(x, y), ship_heading, ship_size, False)
                    for i in range(5):
                        print("rotate %s : %s" % (i, test_ship))
                        test_ship.turn_clockwise()
                    print("----------------------")

    print("*** END (%s)" % (time.ctime(time.time())))

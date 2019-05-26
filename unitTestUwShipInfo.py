import time
import matplotlib.pyplot as plt
import numpy as np
import collections
import unittest

from wosBattleshipServer.funcUwCompute import uw_compute
import wosBattleshipServer.funcUwCompute
import wosBattleshipServer.cCommon
import cCommonGame

#
# This is experimenting with the unit-testing...
# The following code is incomplete...
#

class TestUwShipInfo(unittest.TestCase):
    def test_scenario_01(self):
        ###
        """
        Scenario:
            1) Start at position (0, 0) :               : Turn 0
            2) Move to  position (2, 2) : Take 3 turn   : Turn 0
            3) Scan for 2 turn          : Take 2 turn   : Turn 3
            4) Move to  position (2, 4) : Take 2 turn   : Turn 5
            5) Scan for 2 turn          : Take 2 turn   : Turn 7
            6) Move to  position (0, 4) : Take 2 turn   : Turn 9
            7) Move to  position (0, 0) : Take 4 turn   : Turn 11
            8) Scan for 5 turn          : Take 5 turn   : Turn 15
            9) End                      :               : Turn 20
        """

        # set the position of the ship
        uw_ship = wosBattleshipServer.cCommon.UwShipInfo(ship_id=0,
                                                         position=cCommonGame.Position(0, 0),
                                                         size=1,
                                                         is_sunken=False,
                                                         ship_type=cCommonGame.ShipType.MIL,
                                                         mov_speed=1,
                                                         scan_size=3)

        print("Is ship idle: %s" % uw_ship.is_idle())

        # set the order for the ship
        orders = list()
        orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(2, 2), 2))
        orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(2, 4), 2))
        orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(0, 4), 0))
        orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(0, 0), 0))
        orders.append(cCommonGame.UwActionMoveScan(None, 5))
        orders.append(cCommonGame.UwActionMoveScan())

        # plant the ship for testing
        # todo:...

        if len(orders) > 0:
            print("Set orders")
            uw_ship.set_ops_order(orders)

        print("Is ship idle: %s" % uw_ship.is_idle())

        # execute the order
        print("Executing")
        # counter = 0
        while not uw_ship.is_idle():
            uw_ship.execute()
            # print("--- %s ---" % counter)
            # counter += 1
            # print("pos: x=%s, y=%s" % (uw_ship.position.x,
            #                            uw_ship.position.y))
            # print("\tscan=%s" % ((uw_ship.remain_scan_ops > 0) and
            #                      (uw_ship.remain_move_ops == 0)))
            # print("\tremaining: move=%s, scan=%s, order=%s" %
            #       (uw_ship.remain_move_ops,
            #        uw_ship.remain_scan_ops,
            #        len(uw_ship.orders)))
            # print("\treport size=%s" % len(uw_ship.report))
            # print("\tIs ship idle: %s" % uw_ship.is_idle())
            # # uw_ship.execute()
        print("ship pos: x=%s, y=%s" % (uw_ship.position.x, uw_ship.position.y))

        print("*** Get the report ***")
        uw_ship_report = uw_ship.get_report()

        # print the report
        print("Report:")
        print("\tnum of row: %s " % len(uw_ship_report))
        for uw_ship_report_data in uw_ship_report:
            if isinstance(uw_ship_report, cCommonGame.UwDetectInfo):
                print("\tDist: %s   Ship: %s" % (uw_ship_report_data.dist, uw_ship_report_data.ship_info))

        # convert the ship report
        processed_report = uw_compute(uw_ship_report, False)

        # check if the required ship is in the report
        self.assertEqual(len(uw_ship_report), 20)
        # todo: ...


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    unittest.main()

    print("*** END (%s)" % time.ctime(time.time()))

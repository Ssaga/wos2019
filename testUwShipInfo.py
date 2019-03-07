import time

from wosBattleshipServer.funcUwCompute import uw_compute
import wosBattleshipServer.cCommon
import cCommonGame

if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    print("Test UwShipInfo")

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
    while not uw_ship.is_idle():
        uw_ship.execute()
        print("---")
        print("pos: x=%s, y=%s" % (uw_ship.position.x,
                                   uw_ship.position.y))
        print("\tscan=%s" % ((uw_ship.remain_scan_ops > 0) and
                             (uw_ship.remain_move_ops == 0)))
        print("\tremaining: move=%s, scan=%s, order=%s" %
              (uw_ship.remain_move_ops,
               uw_ship.remain_scan_ops,
               len(uw_ship.orders)))
        print("\treport size=%s" % len(uw_ship.report))
        print("\tIs ship idle: %s" % uw_ship.is_idle())
        # uw_ship.execute()
    print("ship pos: x=%s, y=%s" % (uw_ship.position.x, uw_ship.position.y))

    print("*** Get the report ***")
    uw_ship_report = uw_ship.get_report()
    print("Report: %s" % uw_ship_report)

    # convert the ship report
    processed_report = uw_compute(uw_ship_report)

    # display the processed report
    # todo: ...

    # check if the required ship is in the report
    # todo: ...

    print("*** END (%s)" % time.ctime(time.time()))
import time
import matplotlib.pyplot as plt
import numpy as np
import collections

from wosBattleshipServer.funcUwCompute import uw_compute
import wosBattleshipServer.funcUwCompute
import wosBattleshipServer.cCommon
import cCommonGame

def plot_generated_uw_data(in_data, verbose=False):
    if isinstance(in_data, collections.Iterable):
        for i in range(8):
            data = in_data[i]

            if verbose:
                print("------------------------------------------------------")
                print("# %s" % i)
                print("%s" % data)

            plt.figure(1)
            plt.subplot(4, 2, i + 1)
            if i is 0:
                plt.title("N")
            elif i is 1:
                plt.title("NE")
            elif i is 2:
                plt.title("E")
            elif i is 3:
                plt.title("SE")
            elif i is 4:
                plt.title("S")
            elif i is 5:
                plt.title("SW")
            elif i is 6:
                plt.title("W")
            elif i is 7:
                plt.title("NW")
            else:
                plt.title("???")
            plt.plot(data)
            plt.gca().invert_yaxis()
        # plt.show()
    else:
        print("Unsupported variable-type")

def plot_generated_uw_data_as_img(in_data, verbose=False):
    if isinstance(in_data, collections.Iterable):
        for i in range(8):
            data = np.array(in_data[i])
            data = data.reshape((-1, 100));

            if verbose:
                print("------------------------------------------------------")
                print("# %s" % i)
                for print_data in data:
                    print("%s" % print_data)

            # Perform fft to get the frequent domain of the signal
            data = np.real(np.fft.fft(data[:]))

            plt.figure(2)
            plt.subplot(4, 2, i + 1)
            if i is 0:
                plt.title("N")
            elif i is 1:
                plt.title("NE")
            elif i is 2:
                plt.title("E")
            elif i is 3:
                plt.title("SE")
            elif i is 4:
                plt.title("S")
            elif i is 5:
                plt.title("SW")
            elif i is 6:
                plt.title("W")
            elif i is 7:
                plt.title("NW")
            else:
                plt.title("???")
            plt.imshow(data)
            plt.gca().invert_yaxis()
        # plt.show()
    else:
        print("Unsupported variable-type")

# def plot_generated_uw_data(in_data, verbose=False):
#     if isinstance(in_data, collections.Iterable):
#         for i in range(8):
#             # get the N output report
#             data = in_data[i::8]
#             disp_data = np.array(data)
#
#             if verbose:
#                 print("------------------------------------------------------")
#                 print("# %s" % i)
#                 for print_data in data:
#                     print("%s" % print_data)
#
#             plt.subplot(4, 2, i + 1)
#             if i is 0:
#                 plt.title("N")
#             elif i is 1:
#                 plt.title("NE")
#             elif i is 2:
#                 plt.title("E")
#             elif i is 3:
#                 plt.title("SE")
#             elif i is 4:
#                 plt.title("S")
#             elif i is 5:
#                 plt.title("SW")
#             elif i is 6:
#                 plt.title("W")
#             elif i is 7:
#                 plt.title("NW")
#             else:
#                 plt.title("???")
#             plt.imshow(disp_data)
#             plt.gca().invert_yaxis()
#         # plt.show()
#     else:
#         print("Unsupported variable-type")

def test_scenerio_1():
    ###
    """
    Scenario:
    ----------
        Ship position:
        --------------
        (1,1) size:3, heading=0
        (5,2) size:3, heading=0

        Movement:
        ---------
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
    ships_list = list()
    ships_list.append(cCommonGame.ShipInfo(ship_id=1,
                                           position=cCommonGame.Position(1, 1),
                                           heading=0,
                                           size=3,
                                           ship_type=cCommonGame.ShipType.CIV,
                                           is_sunken=False))
    ships_list.append(cCommonGame.ShipInfo(ship_id=2,
                                           position=cCommonGame.Position(5, 2),
                                           heading=0,
                                           size=3,
                                           ship_type=cCommonGame.ShipType.CIV,
                                           is_sunken=False))

    if len(orders) > 0:
        print("Set orders")
        uw_ship.set_ops_order(orders)

    print("Is ship idle: %s" % uw_ship.is_idle())

    # execute the order
    print("Executing")
    counter = 0
    while not uw_ship.is_idle():
        uw_ship.execute(ships_list)
        print("--- %s ---" % counter)
        counter += 1
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

    # print the report
    print("Report:")
    print("\tnum of row: %s " % len(uw_ship_report))
    for uw_ship_report_data in uw_ship_report:
        print("\t%s" % uw_ship_report_data)
    assert (len(uw_ship_report) is 20)

    # convert the ship report
    processed_report = uw_compute(uw_ship_report, False)

    # display the processed report
    plot_generated_uw_data(processed_report, True)
    plot_generated_uw_data_as_img(processed_report, True)
    plt.show()

    # check if the required ship is in the report
    # todo: ...


def test_scenerio_2():
    ###
    """
    Scenario:
    ----------
        Ship position:
        --------------
        (1,1) size:3, heading=0
        (5,2) size:3, heading=0

        Movement:
        ---------
        1) Start at position (0, 0) :               : Turn 0
        2) Move to  position (4, 4) : Take 6 turn   : Turn 0
        3) Scan for 1 turn          : Take 1 turn   : Turn 6
        4) Do nothing for 3 turns   : Take 3 turn   : Turn 7
        5) End                      :               : Turn 7
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
    orders.append(cCommonGame.UwActionMoveScan(cCommonGame.Position(4, 4), 1))
    #orders.append(cCommonGame.UwActionMoveScan(None, 5))
    #orders.append(cCommonGame.UwActionMoveScan())

    # plant the ship for testing
    ships_list = list()
    ships_list.append(cCommonGame.ShipInfo(ship_id=1,
                                           position=cCommonGame.Position(5, 5),
                                           heading=0,
                                           size=3,
                                           ship_type=cCommonGame.ShipType.CIV,
                                           is_sunken=False))
    ships_list.append(cCommonGame.ShipInfo(ship_id=2,
                                           position=cCommonGame.Position(3, 3),
                                           heading=0,
                                           size=3,
                                           ship_type=cCommonGame.ShipType.CIV,
                                           is_sunken=False))

    if len(orders) > 0:
        print("Set orders")
        uw_ship.set_ops_order(orders)

    print("Is ship idle: %s" % uw_ship.is_idle())

    # execute the order
    print("Executing")

    #while not uw_ship.is_idle():
    for counter in range(10):
        uw_ship.execute(ships_list)
        print("--- %s ---" % counter)
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

    # print the report
    print("Report:")
    print("\tnum of row: %s " % len(uw_ship_report))
    for uw_ship_report_data in uw_ship_report:
        print("\t%s" % uw_ship_report_data)
    assert (len(uw_ship_report) is 7)

    # convert the ship report
    processed_report = uw_compute(uw_ship_report, False)

    # display the processed report
    plot_generated_uw_data(processed_report, True)
    plot_generated_uw_data_as_img(processed_report, True)
    plt.show()

    # check if the required ship is in the report
    # todo: ...


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    print("Test UwShipInfo")

    #
    # test_scenerio_1()

    #
    test_scenerio_2()

    print("*** END (%s)" % time.ctime(time.time()))

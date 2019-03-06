import time
import numpy as np
from timeit import default_timer as timer
from threading import Thread
import threading
import matplotlib.pyplot as plt

from cCommonGame import SatcomInfo
from cCommonGame import Size

from wosBattleshipServer.satcom_scan.cSatcomScanner import SatcomScanner

satcom_mask_dict = dict()


def satcom_scan(map_size, satcom_param):
    outp = None
    if isinstance(satcom_param, SatcomInfo) and \
            isinstance(map_size, Size):
        satcom_scanner = SatcomScanner(map_size.x,
                                       map_size.y,
                                       True)

        # outp = np.ones((map_size.x, map_size.y))
        outp = satcom_scanner.compute_scan_mask(satcom_param.a,
                                                satcom_param.e,
                                                satcom_param.i,
                                                satcom_param.om,
                                                satcom_param.Om,
                                                satcom_param.M,
                                                satcom_param.is_enable,
                                                satcom_param.is_rhs)
        outp = outp.astype(np.bool)
        print(outp)
    return outp


def thread_test_satcom_scan(map_size, satcom_param):
    global satcom_mask_dict
    outp = satcom_scan(map_size, satcom_param)
    satcom_mask_dict[str(threading.current_thread())] = outp


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    print("Test satcom scanner")
    # board_size = np.array([120, 120])
    board_size = np.array([140, 100])
    board = np.zeros(board_size.tolist())

    # satcom_param = SatcomInfo(6378 + 2000,
    #                           0,
    #                           5,
    #                           0,
    #                           150,
    #                           0)

    start = timer()
    thread_list = []
    for i in range(4):
        print("Start Thread %s" % i)

        satcom_param = SatcomInfo(6378 + 2000,
                                  0,
                                  5,
                                  0,
                                  150,
                                  0)
        if i is 0:
            satcom_param = SatcomInfo(a=7000,
                                      e=0,
                                      i=45,
                                      om=0,
                                      Om=101.5,
                                      M=0,
                                      is_enable=False,
                                      is_rhs=False)
        elif i is 1:
            satcom_param = SatcomInfo(a=7000,
                                      e=0,
                                      i=45,
                                      om=0,
                                      Om=101.5,
                                      M=0,
                                      is_enable=True,
                                      is_rhs=False)
        elif i is 2:
            satcom_param = SatcomInfo(a=7000,
                                      e=0,
                                      i=45,
                                      om=0,
                                      Om=101.5,
                                      M=0,
                                      is_enable=True,
                                      is_rhs=True)
        elif i is 3:
            satcom_param = SatcomInfo(a=7000,
                                      e=0,
                                      i=45,
                                      om=0,
                                      Om=101.5,
                                      M=0,
                                      is_enable=False,
                                      is_rhs=True)
        # elif i is 4:
        #     satcom_param = SatcomInfo(a=7000,
        #                               e=0,
        #                               i=45,
        #                               om=0,
        #                               Om=101.5,
        #                               M=0,
        #                               is_enable=False,
        #                               is_rhs=False)

        thread = Thread(target=thread_test_satcom_scan, args=(Size(board_size[0], board_size[1]), satcom_param))
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    stop = timer()
    print("Duration : %f s" % (stop - start))

    for key, mask in satcom_mask_dict.items():
        plt.figure(key)
        plt.imshow(mask)
    plt.show()

    # start = timer()
    # mask = satcom_scan(Size(board_size[0], board_size[1]), satcom_param)
    # stop = timer()
    #
    # print("Mask     : %s" % mask)
    # print("Mask Type: %s" % type(mask))
    # print("Duration : %f s" % (stop - start))

    print("*** END (%s)" % time.ctime(time.time()))

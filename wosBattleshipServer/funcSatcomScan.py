import time
import numpy as np
from timeit import default_timer as timer
from threading import Thread

from cCommonGame import SatcomInfo
from cCommonGame import Size

from wosBattleshipServer.satcom_scan.cSatcomScanner import SatcomScanner


def satcom_scan(map_size, satcom_param):
    outp = None
    if isinstance(satcom_param, SatcomInfo) and \
            isinstance(map_size, Size):
        satcom_scanner = SatcomScanner(map_size.x)

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
    return outp


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    print("Test satcom scanner")
    board_size = np.array([120, 120])
    board = np.zeros(board_size.tolist())

    satcom_param = SatcomInfo(6378 + 2000,
                              0,
                              5,
                              0,
                              150,
                              0)
    start = timer()
    thread_list = []
    for i in range(5):
        print("Start Thread %s" % i)
        thread = Thread(target=satcom_scan, args=(Size(board_size[0], board_size[1]), satcom_param))
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    stop = timer()
    print("Duration : %f s" % (stop - start))

    # start = timer()
    # mask = satcom_scan(Size(board_size[0], board_size[1]), satcom_param)
    # stop = timer()
    #
    # print("Mask     : %s" % mask)
    # print("Mask Type: %s" % type(mask))
    # print("Duration : %f s" % (stop - start))

    print("*** END (%s)" % time.ctime(time.time()))

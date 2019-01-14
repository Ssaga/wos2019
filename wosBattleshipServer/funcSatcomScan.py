import time
import numpy as np

from cCommonGame import SatcomInfo
from cCommonGame import Size


def satcom_scan(map_size, satcom_param):
    outp = None
    if isinstance(satcom_param, SatcomInfo) and \
            isinstance(map_size, Size):
        outp = np.ones((map_size.x, map_size.y))
    return outp


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    print("Test satcom scan")
    board_size = np.array([20, 20])
    board = np.zeros(board_size.tolist())
    satcom_scan(board, SatcomInfo())

    print("*** END (%s)" % (time.ctime(time.time())))

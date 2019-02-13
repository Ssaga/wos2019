import time
import numpy as np
import collections

from cCommonGame import ShipType
from cCommonGame import ShipInfo
from cCommonGame import Position
from cCommonGame import UwCollectedData


def uw_compute(uw_data):
    print("uw_data:")
    if isinstance(uw_data, collections.Iterable):
        for data in uw_data:
            print(data)
    else:
        print(uw_data)


    outp = list()
    for i in range(len(uw_data)):
        data = list()
        for j in range(8):
            data.append(np.ones(50).tolist())
        outp.append(data)
    return outp


#
if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    print("Test u/w ops")
    print("Sample data")
    collected_uw_data = list()
    collected_uw_data.append(UwCollectedData(N=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0,0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(E=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0,0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(S=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0,0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))

    # Perform computation
    outp = uw_compute(collected_uw_data)
    print("output:")
    if isinstance(outp, collections.Iterable):
        for data in outp:
            print(data)
    else:
        print(outp)

    print("*** END (%s)" % time.ctime(time.time()))
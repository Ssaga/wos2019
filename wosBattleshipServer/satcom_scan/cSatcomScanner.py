"""
Created on Tue Jan 29 17:32:39 2019

@author: npingyi
"""

import json
import numpy as np

# import wosBattleshipServer.satcom_scan.orbitFns_v2 as orb
import wosBattleshipServer.satcom_scan.orbitFns_v3 as orb

from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonDecoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonEncoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import SatcomScanConfig

from timeit import default_timer as timer


class SatcomScanner:
    def __init__(self,
                 ngrids=120):
        self.ngrids = ngrids
        self.config = self.load_satcom_scanner_config("satcom_scan_setting.cfg")

    @staticmethod
    def load_satcom_scanner_config(filename):
        write_config = False
        satcom_scanner_setting = None
        try:
            with open(filename) as infile:
                satcom_scanner_setting = json.load(infile, cls=JsonDecoder)
            if isinstance(satcom_scanner_setting, SatcomScanConfig) is not True:
                raise ValueError("Incorrect configuration file parameters (%s)" % filename)
        except:
            print("Unable to load satcom scanner setting")
            write_config = True

        if write_config:
            try:
                satcom_scanner_setting = SatcomScanConfig()
                with open(filename, 'w') as outfile:
                    json.dump(satcom_scanner_setting, outfile, cls=JsonEncoder, indent=4)
                    print("Created satcom scanner setting: %s" % filename)
            except:
                print("Unable to write satcom scanner setting")

        return satcom_scanner_setting

    def compute_scan_mask(self, a, e, i, om, Om, M, is_enable, isRHS):

        start = timer()
        valid = orb.feasibilityCheck(a, i, e, om, Om, M)
        stop = timer()
        print("1. Duration : %f s" % (stop - start))

        if valid:
            start = timer()
            line1, line2 = orb.orbitElems2TLE(a, e, i, om, Om, M)
            stop = timer()
            print("2. Duration : %f s" % (stop - start))

            start = timer()
            r, v, satLat, satLon = orb.satlla_from_TLE(line1, line2)
            stop = timer()
            print("3. Duration : %f s" % (stop - start))

            start = timer()
            if is_enable:
                satLat_new = np.zeros([len(satLat), 1])
                satLon_new = np.zeros([len(satLon), 1])
                for idx in range(len(satLat)):
                    deltaLat, deltaLon = orb.sar_boresight(r[idx, :], self.config.lookang_degree, 0)
                    satLat_new[idx] = satLat[idx] + deltaLat
                    satLon_new[idx] = satLon[idx] + deltaLon
                    del deltaLat, deltaLon
            stop = timer()
            print("4. Duration : %f s" % (stop - start))

            start = timer()
            satAlt = np.linalg.norm(r, axis=1)
            stop = timer()
            print("5. Duration : %f s" % (stop - start))

            start = timer()
            [gridLat, gridLon] = orb.makeGrid(self.config.tl,
                                              self.config.tr,
                                              self.config.bl,
                                              self.config.br,
                                              self.ngrids);
            stop = timer()
            print("6. Duration : %f s" % (stop - start))

            start = timer()
            [mask, posIdx] = orb.getPass(satLat, satLon, gridLat, gridLon);
            stop = timer()
            print("7. Duration : %f s" % (stop - start))

            start = timer()
            gs = orb.getSwathWidth(satAlt, posIdx, self.config.ifov_radians)
            if np.sum(mask) != 0:
                gridOkay = orb.swathWidth2Grid(i, gs, gridLat, gridLon)
                mask = orb.addWidth(mask, gridOkay, gs)
            stop = timer()

            print("8. Duration : %f s" % (stop - start))

        return mask

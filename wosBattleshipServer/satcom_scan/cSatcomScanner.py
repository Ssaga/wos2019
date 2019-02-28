"""
Created on Tue Jan 29 17:32:39 2019

@author: npingyi
"""

import json
import numpy as np

# import wosBattleshipServer.satcom_scan.orbitFns_v2 as orb
# import wosBattleshipServer.satcom_scan.orbitFns_v3 as orb
import wosBattleshipServer.satcom_scan.orbitFns_v4 as orb

from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonDecoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonEncoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import SatcomScanConfig

from timeit import default_timer as timer


class SatcomScanner:
    def __init__(self,
                 ngrids_x=120,
                 ngrids_y=120):
        self.ngrids_x = ngrids_x
        self.ngrids_y = ngrids_y
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
        if orb.feasibilityCheck(a, i, e, om, Om, M):

            print('Feasible Orbit!')

            orb.editScript(a, e, i, om, Om, M,
                           self.config.tl,
                           self.config.tr,
                           self.config.bl,
                           self.config.br,
                           self.config.gmat_dir)

            orb.executeScript(self.config.gmat_dir)

            lat, lon, alt = orb.readLatLon(self.config.gmat_dir)
            vel = orb.readVel(self.config.gmat_dir)
            xyz = orb.readECEF(self.config.gmat_dir)

            if is_enable:
                # --- find ground-boresight intersection --- #
                zeta = np.zeros(len(lat))  # look angle
                vperp2n = np.zeros(len(lat))  # sanity check (always 90deg)
                v2n = np.zeros(len(lat))  # sanity check (always 90deg)
                R = np.zeros([3, 3])
                if isRHS:
                    theta = -np.deg2rad(self.config.lookang_degree)
                else:
                    theta = np.deg2rad(self.config.lookang_degree)

                x = np.zeros([3, len(lat)])  # vel component perpendicular to nadir
                y = np.zeros([3, len(lat)])  # vel vector
                z = np.zeros([3, len(lat)])  # nadir vector
                b = np.zeros([3, len(lat)])  # boresight vector
                insct = np.zeros([3, len(lat)])  # boresight-ground intersection
                insct_lat = np.zeros(len(lat))
                insct_lon = np.zeros(len(lat))
                insct_alt = np.zeros(len(lat))

                for idx in range(len(lat)):
                    y[:, idx] = vel[idx, :] / np.linalg.norm(vel[idx, :])
                    z[:, idx] = -xyz[idx, :] / np.linalg.norm(xyz[idx, :])
                    k = np.cross(z[:, idx], y[:, idx])
                    x[:, idx] = np.cross(k, z[:, idx])

                    # calculate rotation matrix
                    R[0, 0] = np.cos(theta) + (1 - np.cos(theta)) * x[0, idx] ** 2
                    R[1, 0] = x[0, idx] * x[1, idx] * (1 - np.cos(theta)) + x[2, idx] * np.sin(theta)
                    R[2, 0] = x[2, idx] * x[0, idx] * (1 - np.cos(theta)) - x[1, idx] * np.sin(theta)
                    R[0, 1] = x[0, idx] * x[1, idx] * (1 - np.cos(theta)) - x[2, idx] * np.sin(theta)
                    R[1, 1] = np.cos(theta) + (1 - np.cos(theta)) * x[1, idx] ** 2
                    R[2, 1] = x[2, idx] * x[1, idx] * (1 - np.cos(theta)) + x[0, idx] * np.sin(theta)
                    R[0, 2] = x[0, idx] * x[2, idx] * (1 - np.cos(theta)) + x[1, idx] * np.sin(theta)
                    R[1, 2] = x[2, idx] * x[1, idx] * (1 - np.cos(theta)) - x[0, idx] * np.sin(theta)
                    R[2, 2] = np.cos(theta) + (1 - np.cos(theta)) * x[2, idx] ** 2

                    b[:, idx] = np.matmul(R, z[:, idx])
                    insct[:, idx] = orb.grdBoresightIntersection(xyz[idx, :], b[:, idx])
                    insct_lat[idx], insct_lon[idx], insct_alt[idx] = orb.ecef2lla(insct[:, idx])
                    final_lat = insct_lat
                    final_lon = insct_lon
            else:
                # if doing EO, then use satellite lat-lon
                final_lat = lat
                final_lon = lon

            # TODO: add width to grid
            # TODO: altitude is assumed to be scalar

            [gridLat, gridLon] = orb.makeGrid(self.config.tl,
                                              self.config.tr,
                                              self.config.bl,
                                              self.config.br,
                                              [self.ngrids_x, self.ngrids_y]);
            [mask, posIdx, final_lat, final_lon, final_alt] = orb.getPass(final_lat, final_lon, alt, gridLat, gridLon);

            if np.sum(mask) != 0:
                gs = orb.getSwathWidth(final_alt, posIdx, self.config.ifov_radians)
                gridOkay = orb.swathWidth2Grid(gs, gridLat, gridLon)
                mask = orb.addWidth(mask, gridOkay, gs)

        else:
            print('Infeasible Orbital Parameters!')
            mask = np.zeros((self.ngrids_x, self.ngrids_y))
        return mask

   # def compute_scan_mask(self, a, e, i, om, Om, M, is_enable, isRHS):
   #
   #      start = timer()
   #      valid = orb.feasibilityCheck(a, i, e, om, Om, M)
   #      stop = timer()
   #      print("1. Duration : %f s" % (stop - start))
   #
   #      if valid:
   #          start = timer()
   #          line1, line2 = orb.orbitElems2TLE(a, e, i, om, Om, M)
   #          stop = timer()
   #          print("2. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          r, v, satLat, satLon = orb.satlla_from_TLE(line1, line2)
   #          stop = timer()
   #          print("3. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          if is_enable:
   #              satLat_new = np.zeros([len(satLat), 1])
   #              satLon_new = np.zeros([len(satLon), 1])
   #              for idx in range(len(satLat)):
   #                  deltaLat, deltaLon = orb.sar_boresight(r[idx, :], self.config.lookang_degree, 0)
   #                  satLat_new[idx] = satLat[idx] + deltaLat
   #                  satLon_new[idx] = satLon[idx] + deltaLon
   #                  del deltaLat, deltaLon
   #          stop = timer()
   #          print("4. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          satAlt = np.linalg.norm(r, axis=1)
   #          stop = timer()
   #          print("5. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          [gridLat, gridLon] = orb.makeGrid(self.config.tl,
   #                                            self.config.tr,
   #                                            self.config.bl,
   #                                            self.config.br,
   #                                            self.ngrids);
   #          stop = timer()
   #          print("6. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          [mask, posIdx] = orb.getPass(satLat, satLon, gridLat, gridLon);
   #          stop = timer()
   #          print("7. Duration : %f s" % (stop - start))
   #
   #          start = timer()
   #          gs = orb.getSwathWidth(satAlt, posIdx, self.config.ifov_radians)
   #          if np.sum(mask) != 0:
   #              gridOkay = orb.swathWidth2Grid(i, gs, gridLat, gridLon)
   #              mask = orb.addWidth(mask, gridOkay, gs)
   #          stop = timer()
   #
   #          print("8. Duration : %f s" % (stop - start))
   #
   #      return mask

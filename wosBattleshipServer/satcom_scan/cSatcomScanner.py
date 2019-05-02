"""
Created on Tue Jan 29 17:32:39 2019

@author: npingyi
"""

import json
import numpy as np
import os
import datetime
import threading

# import wosBattleshipServer.satcom_scan.orbitFns_v2 as orb
# import wosBattleshipServer.satcom_scan.orbitFns_v3 as orb
import wosBattleshipServer.satcom_scan.orbitFns_v5 as orb

from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonDecoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import JsonEncoder
from wosBattleshipServer.satcom_scan.cSatcomScannerConfig import SatcomScanConfig

# from timeit import default_timer as timer


class SatcomScanner:
    counter = 0
    lock = threading.Lock()

    def __init__(self,
                 ngrids_x=120,
                 ngrids_y=120,
                 rmv_iofiles=False):
        self.ngrids_x = ngrids_x
        self.ngrids_y = ngrids_y
        self.config = self.load_satcom_scanner_config("satcom_scan_setting.cfg")
        self.rmv_iofiles = rmv_iofiles

    @staticmethod
    def load_satcom_scanner_config(filename):
        write_config = False
        satcom_scanner_setting = None
        try:
            with open(filename, mode="r") as infile:
                satcom_scanner_setting = json.load(infile, cls=JsonDecoder)
            if isinstance(satcom_scanner_setting, SatcomScanConfig) is not True:
                raise ValueError("Incorrect configuration file parameters (%s)" % filename)
            infile.close()
        except:
            print("Unable to load satcom scanner setting")
            write_config = True

        if write_config:
            try:
                satcom_scanner_setting = SatcomScanConfig()
                with open(filename, mode='w') as outfile:
                    json.dump(satcom_scanner_setting, outfile, cls=JsonEncoder, indent=4)
                    print("Created satcom scanner setting: %s" % filename)
            except:
                print("Unable to write satcom scanner setting")

        return satcom_scanner_setting

    def compute_scan_mask(self, a, e, i, om, Om, M, is_enable, is_rhs):
        """
        :param a:  Semi major axis (SMA)
        :param e:  eccentricity (ECC)
        :param i:  inclination (INC)
        :param om: argument of perigee (AOP)
        :param Om: RAAN
        :param M:  true anomaly (TA)
        :param is_enable:
        :param is_rhs:
        :return: Masking of the Game Map
        """
        # Added by ttl
        # setup the directory for the operation
        extra = self.config.extra
        isOk = True
        print(os.path.dirname(os.path.realpath(__file__)))
        count = 0
        with SatcomScanner.lock:
            count = SatcomScanner.counter
            SatcomScanner.counter += 1
            SatcomScanner.counter %= 100
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        session_io_root_dir = self.config.gmat_io__dir + "/" + timestamp + "-" + str(count).zfill(2)
        startup_script_file = session_io_root_dir + "/gmat_startup.txt"
        runtime_script_file = session_io_root_dir + "/wos_final_orbit.script"

        print("startup_script_file : %s" % startup_script_file)
        print("runtime_script_file : %s" % runtime_script_file)

        # create the required io session directory
        try:
            os.makedirs(session_io_root_dir)
        except OSError:
            isOk = False
        # end of modification

        if orb.feasibilityCheck(a, i, e, om, Om, M) and (isOk is True):

            print('Feasible Orbit!')

            # setup the startup
            orb.editStartup(self.config.gmat_startup_template,
                            startup_script_file,
                            self.config.gmat_root_dir,
                            session_io_root_dir)
            # setup the run-script
            orb.editScript(a, e, i, om, Om, M,
                           self.config.tl,
                           self.config.tr,
                           self.config.bl,
                           self.config.br,
                           self.config.gmat_script_template,
                           runtime_script_file)

            orb.executeScript(self.config.gmat_exec,
                              runtime_script_file,
                              startup_script_file)

            lat, lon, alt = orb.readLatLon(session_io_root_dir)
            vel = orb.readVel(session_io_root_dir)
            xyz = orb.readECEF(session_io_root_dir)

            if is_enable:
                # --- find ground-boresight intersection --- #
                zeta = np.zeros(len(lat))  # look angle
                vperp2n = np.zeros(len(lat))  # sanity check (always 90deg)
                v2n = np.zeros(len(lat))  # sanity check (always 90deg)
                R = np.zeros([3, 3])
                if is_rhs:
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

            # [gridLat, gridLon] = orb.makeGrid(self.config.tl,
            #                                   self.config.tr,
            #                                   self.config.bl,
            #                                   self.config.br,
            #                                   [self.ngrids_x, self.ngrids_y])
            [gridLat, gridLon] = orb.makeGrid(self.config.tl,
                                              self.config.tr,
                                              self.config.bl,
                                              self.config.br,
                                              [self.ngrids_y, self.ngrids_x], 
                                              extra)
            # print("GRID LAT: %s %s" % (gridLat, len(gridLat)))
            # print("GRID LON: %s %s" % (gridLon, len(gridLon)))
            # print("final_lat: %s %s" % (final_lat, len(final_lat)))
            # print("final_lon: %s %s" % (final_lon, len(final_lon)))
            # print("alt: %s %s" % (alt, len(alt)))

            [mask, pos_idx, final_lat, final_lon, final_alt] = orb.getPass(final_lat, final_lon, alt, gridLat, gridLon)

            
            if np.sum(mask) != 0:
                gs = orb.getSwathWidth(final_alt, pos_idx, self.config.ifov_radians)
                grid_okay = orb.swathWidth2Grid(gs, gridLat, gridLon)
                mask = orb.addWidth(mask, grid_okay, gs)
            mask = mask[extra:-extra, extra:-extra]

        else:
            print('Infeasible Orbital Parameters!')
            mask = np.zeros((self.ngrids_x, self.ngrids_y))

        # Added by ttl
        # clean-up for the files created for the operation
        # todo:...
        try:
            if self.rmv_iofiles:
                os.remove(session_io_root_dir + "/GmatLog.txt")
                os.remove(session_io_root_dir + "/SatECEF.txt")
                os.remove(session_io_root_dir + "/SatLLA.txt")
                os.remove(session_io_root_dir + "/SatVel.txt")
                os.remove(runtime_script_file)
                os.remove(startup_script_file)
                os.removedirs(session_io_root_dir)
            else:
                print("os.remove(%s)" % (session_io_root_dir + "/GmatLog.txt"))
                print("os.remove(%s)" % (session_io_root_dir + "/SatECEF.txt"))
                print("os.remove(%s)" % (session_io_root_dir + "/SatLLA.txt"))
                print("os.remove(%s)" % (session_io_root_dir + "/SatVel.txt"))
                print("os.remove(%s)" % runtime_script_file)
                print("os.remove(%s)" % startup_script_file)
                print("os.remove(%s)" % session_io_root_dir)
        except OSError:
            print("Unable to remove: %s" % session_io_root_dir)
        #
        # end of modification

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

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 14:03:09 2019

@author: admin
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 18:11:57 2019

@author: admin
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d as conv2


def readLatLon(session_outp_path):
    filename = ""
    if isinstance(session_outp_path, str):
        # Generate the full-pathname of the expected file
        filename = session_outp_path + "/SatLLA.txt"

    print("Loading SatLLA @ %s" % filename)
    ll = np.loadtxt(filename, skiprows=1)
    # repack into separate lat and lon variables
    ll = ll.squeeze()
    lat = ll[:, 0]
    lon = ll[:, 1]
    alt = ll[:, 2]

    return lat, lon, alt

def readVel(session_outp_path):
    filename = ""
    if isinstance(session_outp_path, str):
        # Generate the full-pathname of the expected file
        filename = session_outp_path + "/SatVel.txt"

    print("Loading SatVel @ %s" % filename)
    vt = np.loadtxt(filename, skiprows=1)
    vt = vt.squeeze()
    return vt

def readECEF(session_outp_path):
    filename = ""
    if isinstance(session_outp_path, str):
        # Generate the full-pathname of the expected file
        filename = session_outp_path + "/SatECEF.txt"

    print("Loading SatECEF @ %s" % filename)
    xyz = np.loadtxt(filename, skiprows=1)
    xyz = xyz.squeeze()
    return xyz

# def readLatLon(fileDir):
#     import numpy as np
#     #    ll = np.loadtxt('D://gabriel//LatLon.txt')
#     #    ll = np.loadtxt('C:/Users/admin/AppData/Local/GMAT/R2018a/output/SatLLA.txt', skiprows=1)
#     ll = np.loadtxt(fileDir + '/output/SatLLA.txt', skiprows=1)
#
#     # repack into separate lat and lon variables
#     ll = ll.squeeze()
#     lat = ll[:, 0]
#     lon = ll[:, 1]
#     alt = ll[:, 2]
#     return lat, lon, alt


# def readVel(fileDir):
#     #    vt = np.loadtxt('C:/Users/admin/AppData/Local/GMAT/R2018a/output/SatVel.txt', skiprows=1)
#     vt = np.loadtxt(fileDir + '/output/SatVel.txt', skiprows=1)
#     vt = vt.squeeze()
#     return vt


# def readECEF(fileDir):
#     #    xyz = np.loadtxt('C:/Users/admin/AppData/Local/GMAT/R2018a/output/SatECEF.txt', skiprows=1)
#     xyz = np.loadtxt(fileDir + '/output/SatECEF.txt', skiprows=1)
#     xyz = xyz.squeeze()
#     return xyz

# modified by ttl : to remove the cmd to change the current working path
def executeScript(exec_file, exec_script, startup_file=""):
    if isinstance(exec_file, str) and isinstance(exec_script, str):

        # setup the execution cmd
        exec_cmd = exec_file + ' --minimize --run ' + exec_script
        if isinstance(startup_file, str):
            exec_cmd += ' --startup_file ' + startup_file
        exec_cmd += ' --exit'

        # executes GMAT script from command line
        print("Exec : %s" % exec_cmd)
        os.system(exec_cmd)
    else:
        print('ERROR: Unable to run GMAT application !!!')
    return None

# def executeScript(fileDir):
#     #    fileStr_toLaunch = 'D:\gabriel\GMAT\GMAT\WOS_finalOrbit.script'
#     fileStr_toLaunch = 'WOS_finalOrbit.script'
#     # executes GMAT script from command line
#     #    os.chdir( 'C:/Users/admin/AppData/Local/GMAT/R2018a/bin' )
#     os.chdir(fileDir + '/bin')
#     os.system('GMAT --minimize --run ' + fileStr_toLaunch + ' --exit')
#     #    os.system( 'GMAT --run ' + fileStr)
#     #    os.system(' GMAT --run')
#     return None


def editStartup(gmat_startup_template,
                startup_script_file,
                gmat_root_dir,
                session_io_root_dir):

    print("template File : %s" % gmat_startup_template)
    print("Session File  : %s" % startup_script_file)

    tt = open(gmat_startup_template)
    t = tt.read()
    tt.close()

    # orbit params
    t = t.replace("<gmat_installed_dir>", gmat_root_dir)
    t = t.replace("<output_path>", session_io_root_dir)

    l = open(startup_script_file, 'w+')
    l.write(t)
    l.close()

    return None


def editScript(a, e, i, om, Om, gam, TL, TR, BL, BR,
               gmat_script_template,
               runtime_script_file):
    # a - Semi major axis (SMA)
    # e - eccentricity (ECC)
    # i - inclination (INC)
    # om - argument of perigee (AOP)
    # Om - RAAN
    # gam - true anomaly (TA)

    #    fileStr_template = 'D:\gabriel\GMAT\GMAT\WOS_template.script'
    #    fileStr_toLaunch = 'D:\gabriel\GMAT\GMAT\WOS_finalOrbit.script'

    print("fileStr_template: %s" % gmat_script_template)
    print("fileStr_toLaunch: %s" % runtime_script_file)

    tt = open(gmat_script_template)
    t = tt.read()
    tt.close()

    # orbit params
    t = t.replace('PUTSMAHERE', str(a))
    t = t.replace('PUTECCHERE', str(e))
    t = t.replace('PUTINCHERE', str(i))
    t = t.replace('PUTRAANHERE', str(Om))
    t = t.replace('PUTAOPHERE', str(om))
    t = t.replace('PUTTAHERE', str(gam))

    # Area of Ops params
    t = t.replace('TLLATHERE', str(TL[0]))
    t = t.replace('TLLONHERE', str(TL[1]))
    t = t.replace('TRLATHERE', str(TR[0]))
    t = t.replace('TRLONHERE', str(TR[1]))
    t = t.replace('BLLATHERE', str(BL[0]))
    t = t.replace('BLLONHERE', str(BL[1]))
    t = t.replace('BRLATHERE', str(BR[0]))
    t = t.replace('BRLONHERE', str(BR[1]))

    l = open(runtime_script_file, 'w+')
    l.write(t)
    l.close()

    return None


def grdBoresightIntersection(satPos, bsVec):
    a = 6378.137
    b = 6356.7523142518

    u = bsVec[0]
    v = bsVec[1]
    w = bsVec[2]

    xs = satPos[0]
    ys = satPos[1]
    zs = satPos[2]

    A = (u ** 2 + v ** 2) / a ** 2 + w ** 2 / b ** 2
    B = 2 * ((u * xs + v * ys) / a ** 2 + w * zs / b ** 2)
    C = (xs ** 2 + ys ** 2) / a ** 2 + zs ** 2 / b ** 2 - 1

    t1 = (-B + np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)
    t2 = (-B - np.sqrt(B ** 2 - 4 * A * C)) / (2 * A)

    intersect1 = satPos + t1 * bsVec
    intersect2 = satPos + t2 * bsVec

    ii = np.argmin([np.linalg.norm(satPos - intersect1), np.linalg.norm(satPos - intersect2)])

    if ii == 0:
        intersect = intersect1
    elif ii == 1:
        intersect = intersect2

    return intersect


def ecef2lla(xyz):
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    a = 6378.137
    f = 1 / 298.257223563
    e2 = f * (2 - f)
    eprime2 = e2 / (1 - e2)
    b = a * (1 - f)

    lon = np.arctan2(y, x)
    rho = np.sqrt(x ** 2 + y ** 2)

    beta = np.arctan2(z, (1 - f) * rho)
    lat = np.arctan2(z + b * eprime2 * np.sin(beta) ** 3, rho - a * e2 * np.cos(beta) ** 3)

    betaNew = np.arctan2((1 - f) * np.sin(lat), np.cos(lat))
    count = 0

    while beta != betaNew and count < 5:
        beta = betaNew
        lat = np.arctan2(z + b * eprime2 * np.sin(beta) ** 3, rho - a * e2 * np.cos(beta) ** 3)
        betaNew = np.arctan2((1 - f) * np.sin(lat), np.cos(lat))
        count += 1

    sinphi = np.sin(lat)
    N = a / np.sqrt(1 - e2 * sinphi ** 2)
    alt = rho * np.cos(lat) + (z + e2 * N * sinphi) * sinphi - N
    lat = lat / np.pi * 180
    lon = lon / np.pi * 180

    return lat, lon, alt


def feasibilityCheck(a, i, e, om, Om, gam):
    # read threshold from config file
    a_threshold = 6378.137 + 2000
    i_threshold = [-90, 90]
    e_threshold = [0, 1]
    om_threshold = [0, 360]
    Om_threshold = [0, 360]
    gam_threshold = [0, 360]

    b = float(a) * np.sqrt(1.0 - float(e) ** 2)

    valid = True

    if float(a) > a_threshold:
        valid = False
    if float(b) <= 6378.137:
        valid = False
    if float(e) < e_threshold[0] or float(e) >= e_threshold[1]:
        valid = False
    if float(i) < i_threshold[0] or float(i) > i_threshold[1]:
        valid = False
    if float(om) < om_threshold[0] or float(om) > om_threshold[1]:
        valid = False
    if float(Om) < Om_threshold[0] or float(Om) > Om_threshold[1]:
        valid = False
    if float(gam) < gam_threshold[0] or float(gam) > gam_threshold[1]:
        valid = False

    return valid


def makeGrid(tl, tr, bl, br, ngrids, EXTRA=0):
    # requires map grid to be aligned to lat-lon grid
    # tr = [top right lat, top right lon]
    # ngrids is 2 element list [N_lat, N_lon]

    latDiff = np.abs(tl[0] - bl[0]) / ngrids[0] / 2
    lonDiff = np.abs(tl[1] - tr[1]) / ngrids[1] / 2

    gridLat = np.linspace(tl[0] - latDiff, bl[0] + latDiff, ngrids[0])
    gridLon = np.linspace(tl[1] + lonDiff, tr[1] - lonDiff, ngrids[1])
    
    gridLat = np.append(gridLat, np.arange(ngrids[0], ngrids[0]+EXTRA)*\
                        (gridLat[1]-gridLat[0]) + gridLat[0])    
    gridLat = np.append(np.arange(-EXTRA, 0)*(gridLat[1]-gridLat[0]) + \
                        gridLat[0], gridLat)
    gridLon = np.append(gridLon, np.arange(ngrids[1], ngrids[1]+EXTRA)*\
                        (gridLon[1]-gridLon[0]) + gridLon[0])
    gridLon = np.append(np.arange(-EXTRA, 0)*(gridLon[1]-gridLon[0]) + \
                        gridLon[0], gridLon)

    return gridLat, gridLon


def getPass(satLat, satLon, satAlt, gridLat, gridLon):
    satLat = np.squeeze(satLat)
    satLon = np.squeeze(satLon)

    latMin = np.min(gridLat)
    latMax = np.max(gridLat)
    lonMin = np.min(gridLon)
    lonMax = np.max(gridLon)

    inGridLat = np.logical_and(satLat >= latMin, satLat <= latMax)
    inGridLon = np.logical_and(satLon >= lonMin, satLon <= lonMax)
    inGrid = np.logical_and(inGridLat, inGridLon)

    latThresh = np.abs(gridLat[0] - gridLat[1]) / 2
    lonThresh = np.abs(gridLon[0] - gridLon[1]) / 2
    mask = np.zeros((len(gridLat), len(gridLon)))
    posIdx = np.array([])

    inGridIdx = np.nonzero(inGrid)
    if inGridIdx[0].size != 0:
        if np.min(inGridIdx) > 0:
            inGridIdx = np.append(np.min(inGridIdx) - 1, inGridIdx)
        if np.max(inGridIdx) < (len(inGrid) - 1):
            inGridIdx = np.append(inGridIdx, np.max(inGridIdx) + 1)
        satLat = np.interp(np.arange(0, len(inGridIdx), 0.01), \
                           np.arange(0, len(inGridIdx), 1), \
                           satLat[inGridIdx])
        satLon = np.interp(np.arange(0, len(inGridIdx), 0.01), \
                           np.arange(0, len(inGridIdx), 1), \
                           satLon[inGridIdx])
        satAlt = np.interp(np.arange(0, len(inGridIdx), 0.01), \
                           np.arange(0, len(inGridIdx), 1), \
                           satAlt[inGridIdx])
        for satIdx in range(0, len(satLat)):
            latFlag = abs(satLat[satIdx] - gridLat) <= latThresh
            lonFlag = abs(satLon[satIdx] - gridLon) <= lonThresh
            latPos = np.where(latFlag == True)
            lonPos = np.where(lonFlag == True)

            #        latPos = np.argmin(np.abs(satLat[satIdx] - gridLat))
            #        lonPos = np.argmin(np.abs(satLon[satIdx] - gridLon))
            if latPos[0].size and lonPos[0].size:
                mask[latPos[0][0]][lonPos[0][0]] = 1
                posIdx = np.append(posIdx, satIdx)

    return mask, posIdx, satLat, satLon, satAlt


def getGrdDist(lat1, lon1, lat2, lon2):
    # assumes spherical earth
    # lat/lon in [deg]
    lat1 = np.deg2rad(lat1)
    lon1 = np.deg2rad(lon1)
    lat2 = np.deg2rad(lat2)
    lon2 = np.deg2rad(lon2)
    ang = 2 * np.arcsin(np.sqrt(np.sin(abs(lat1 - lat2) / 2) ** 2 + \
                                np.cos(lat1) * np.cos(lat2) * \
                                np.sin(abs(lon1 - lon2) / 2) ** 2))
    R_earth = 6378.137  # Radius of earth, [km]
    grdDist = R_earth * ang

    return grdDist


def swathWidth2Grid(groundSwath, gridLat, gridLon):
    vertDist = getGrdDist(gridLat[0], gridLon[0], gridLat[1], gridLon[0])
    horiDist = getGrdDist(gridLat[0], gridLon[0], gridLat[0], gridLon[1])
    diagDist = getGrdDist(gridLat[0], gridLon[0], gridLat[1], gridLon[1])

    # gridOkay = [np.round(groundSwath/vertDist), np.round(groundSwath/horiDist), np.round(groundSwath/diagDist)]

    # gridOkay = np.array([vertDist <= groundSwath, horiDist <= groundSwath, diagDist <= groundSwath]);
    gridOkay = [vertDist, horiDist, diagDist]
    return gridOkay


def addWidth(mask, gridOkay, groundSwath):
    radius = groundSwath / 2
    vertDist = gridOkay[0]
    horiDist = gridOkay[1]
    minDist = np.min(gridOkay)
    N = np.round(radius / minDist)

    y, x = np.meshgrid(np.arange(-N, N + 1) * vertDist, np.arange(-N, N + 1) * horiDist)
    filt = x ** 2 + y ** 2 <= radius ** 2

    mask = conv2(mask, filt, mode='same')
    mask = (mask != 0)
    return mask


def getSwathWidth(satAlt, posIdx, ifov):
    # ifov - instantaneous field of view [radians]

    satIdx = list(posIdx.astype(int))
    avgAlt = np.average(satAlt[satIdx])
    groundSwath = avgAlt * ifov
    return groundSwath


# TODO: enable rectangular map

# TODO: feasibility checks

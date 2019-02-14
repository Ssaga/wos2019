# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:05:33 2018

@author: admin
"""
from sgp4.earth_gravity import wgs72, wgs84
from sgp4.io import twoline2rv
import datetime
import matplotlib.pyplot as plt
import numpy as np
from astropy import coordinates as coord
#from astropy.time import Time
import astropy.units as u
from scipy.signal import convolve2d as conv2


from timeit import default_timer as timer


def feasibilityCheck(a, i, e, om, Om, M):
    # read threshold from config file
    a_threshold = 6378.137 + 2000
    i_threshold = [-90, 90]
    e_threshold = [0, 1]
    om_threshold = [0, 360]
    Om_threshold = [0, 360]
    M_threshold = [0, 360]
    
    
    b = a*np.sqrt(1.0 - e**2)
    

    
    valid = True
    
    if a > a_threshold:
        valid = False
    if b <= 6378.137:
        valid = False
    if e < e_threshold[0] or e >= e_threshold[1]:
        valid = False
    if i < i_threshold[0] or i > i_threshold[1]:
        valid = False    
    if om < om_threshold[0] or om > om_threshold[1]:
        valid = False
    if Om < Om_threshold[0] or Om > Om_threshold[1]:
        valid = False    
    if M < M_threshold[0] or M > M_threshold[1]:
        valid = False
        
    return valid

def orbitElems2TLE(a, e, i, om, Om, M):
    # read from config file
    line1 = ('1 00005U 58002B   00179.78495062  .00000023  00000-0  28098-4 0  4752')
        
    i_str= '%.4f' % i
    if i < 10:
        i_str = '00' + i_str
    elif i < 100:
        i_str = '0' + i_str
        
    Om_str = '%3.4f' % Om
    
    e_str = ('%.7f' % e).lstrip('0').lstrip('.')
    
    om_str = ('%.4f' % om)
    if om < 10:
        om_str = '00' + om_str
    elif om < 100:
        om_str = '0' + om_str
    
    M_str = ('%.4f' % M)
    if M < 10:
        M_str = '00' + M_str
    elif M < 100:
        M_str = '0' + M_str
    
    
    n = np.sqrt(398600.4418/a**3)/(2*np.pi)*86400
    n_str = '%.8f' % n
    
    line2 = '2 ' + '25544 ' + i_str + ' ' + Om_str + ' ' + e_str + ' ' + om_str + ' ' + M_str + ' ' + n_str + '56353' + '7'
    
    
    return line1, line2
    
    


def satlla_from_TLE(line1, line2):
    start = timer()
    satellite = twoline2rv(line1, line2, wgs72)
    stop = timer()
    print("3 i  . Duration : %f s" % (stop - start))

    start = timer()
    # try to propagate for a period of time
    propTimeSecs = np.pi*2/satellite.no*60
    timeDivisor = 10
    STARTTIME = satellite.epoch
    stop = timer()
    print("3 ii . Duration : %f s" % (stop - start))

#    STOPTIME = STARTTIME + datetime.timedelta(seconds = propTimeSecs)
    
    start = timer()
    r = np.zeros((int(propTimeSecs/timeDivisor), 3))
    v = np.zeros((int(propTimeSecs/timeDivisor), 3))
    lat = np.zeros((int(propTimeSecs/timeDivisor), 1))
    lon = np.zeros((int(propTimeSecs/timeDivisor), 1))
    stop = timer()
    print("3 iii. Duration : %f s" % (stop - start))

    #print(STARTTIME)
    #print(STOPTIME)
    
    start = timer()
    print("%s / %s = %s" % (propTimeSecs, timeDivisor, propTimeSecs/timeDivisor))
    for i in range(int(propTimeSecs/timeDivisor)): # propagate orbit and convert to LLA
        CURRTIME = STARTTIME + datetime.timedelta(seconds=i*timeDivisor)
        r[i,], v[i,] = satellite.propagate(CURRTIME.year, CURRTIME.month, CURRTIME.day, CURRTIME.hour, CURRTIME.minute, CURRTIME.second)
        cartRep = coord.CartesianRepresentation(x=r[i,0], y=r[i,1], z=r[i,2], unit=u.km)
        gcrs = coord.GCRS(cartRep, obstime=CURRTIME) # cast xyz coordinate in ECI frame
        itrs = gcrs.transform_to(coord.ITRS(obstime=CURRTIME))
        lat[i], lon[i] = itrs.spherical.lat.value , itrs.spherical.lon.value
    stop = timer()
    print("3 iv . Duration : %f s" % (stop - start))

    return r, v, lat, lon

###########################################
    
def sar_boresight(r, lookangle, i):
    R_e = 6378.137                                              # earth radius
    H = np.mean(np.sqrt(r[0,]**2 + r[1,]**2 + r[2,]**2)) - R_e # mean height
    theta = np.deg2rad(180 - lookangle) - (np.pi - np.arcsin((R_e + H)*np.sin(np.deg2rad(lookangle))/R_e))
    print(np.rad2deg(theta))
    delta_lat = np.rad2deg(  np.arcsin(np.sin(np.pi/2-np.deg2rad(i))*np.sin(theta))  )
    delta_lon = np.rad2deg(  np.arctan(np.cos(np.pi/2-np.deg2rad(i))*np.tan(theta))  )
    
#    print(delta_lat)
#    print(delta_lon)
    
    return delta_lat, delta_lon


def rot_fn(axis, angle):
    #angle is rads
    if axis in 'x':
        rot_mat = np.array([[1, 0, 0], 
                            [0, np.cos(angle), -np.sin(angle)],
                            [0, np.sin(angle), np.cos(angle)]]);
    elif axis in 'y':
        rot_mat = np.array([[np.cos(angle), 0, np.sin(angle)], 
                            [0, 1, 0],
                            [-np.sin(angle), 0, np.cos(angle)]]);
    elif axis in 'z':
        rot_mat = np.array([[np.cos(angle), -np.sin(angle), 0], 
                            [np.sin(angle), np.cos(angle), 0],
                            [0, 0, 1]]);
    else: 
        return np.zeros((3,3));
    
    return rot_mat;



###################################################
    
def makeGrid(tl, tr, bl, br, ngrids):
    # requires map grid to be aligned to lat-lon grid
    # tr = [top right lat, top right lon]
    # ngrids is scalar, making the grid a square (and not a rectangle)
    
    latDiff = np.abs(tl[0] - bl[0])/ngrids/2;
    lonDiff = np.abs(tl[1] - tr[1])/ngrids/2;
    
    gridLat = np.linspace( tl[0]-latDiff,  bl[0]+latDiff, ngrids);
    gridLon = np.linspace(tl[1]+lonDiff, tr[1]-lonDiff, ngrids);
    
    return gridLat, gridLon;

###################################################

def displayGrid(mask):
    strMask = '';
    for row in mask:
        strMask = strMask + '\n';
        for elem in row:
            if elem > 0:
                strMask = strMask  + 'X'; 
            else: 
                strMask = strMask + '.';
                
    return strMask
#    
#    
#    for x in zip(*[iter(it)]*4):
#            print('{:<4}{:^6}{:^6}{:^6}'.format(*x))

###################################################    

#def displayGrid2(mask)
#
#plt.imshow(mask)
#plt.colorbar()
#plt.ylim(())
#plt.show()    


###################################################

def getPass(satLat, satLon, gridLat, gridLon):
    satLat = np.squeeze(satLat)
    satLon = np.squeeze(satLon)
    
    latMin = np.min(gridLat)
    latMax = np.max(gridLat)
    lonMin = np.min(gridLon)
    lonMax = np.max(gridLon)
    
    inGridLat = np.logical_and(satLat >= latMin, satLat <= latMax)
    inGridLon = np.logical_and(satLon >= lonMin, satLon <= lonMax)
    inGrid = np.logical_and(inGridLat, inGridLon)
    
    ngrids = len(gridLat);
    latThresh = np.abs(gridLat[0] - gridLat[1])/2;
    lonThresh = np.abs(gridLon[0] - gridLon[1])/2;
    mask = np.zeros((ngrids, ngrids));
    posIdx = np.array([]);
    
    inGridIdx = np.nonzero(inGrid)
    if inGridIdx[0].size != 0:
        inGridIdx = np.append(np.min(inGridIdx)-1, inGridIdx)
        inGridIdx = np.append(inGridIdx, np.max(inGridIdx) + 1)
        satLat = np.interp(np.arange(0, len(inGridIdx), 0.01), \
                           np.arange(0, len(inGridIdx), 1), \
                           satLat[inGridIdx])
        satLon = np.interp(np.arange(0, len(inGridIdx), 0.01), \
                           np.arange(0, len(inGridIdx), 1), \
                           satLon[inGridIdx])
        for satIdx in range(0, len(satLat)):
            latFlag = abs(satLat[satIdx] - gridLat) <= latThresh;
            lonFlag = abs(satLon[satIdx] - gridLon) <= lonThresh;
            latPos = np.where(latFlag == True);
            lonPos = np.where(lonFlag == True);
    
    #        latPos = np.argmin(np.abs(satLat[satIdx] - gridLat))
    #        lonPos = np.argmin(np.abs(satLon[satIdx] - gridLon))
            if latPos[0].size and lonPos[0].size:
                mask[latPos[0][0]][lonPos[0][0]] = 1;
                posIdx = np.append(posIdx, satIdx);
        
    return mask, posIdx
        
################################################### 

def getSwathWidth(satAlt, posIdx, ifov):
    #ifov - instantaneous field of view [radians]
    
    satIdx = list(posIdx.astype(int));
    avgAlt = np.average(satAlt[satIdx]);
    groundSwath = avgAlt*ifov;
    return groundSwath

################################################### 
    
def getGrdDist(lat1, lon1, lat2, lon2):
    # assumes spherical earth
    # lat/lon in [deg] 
    lat1 = np.deg2rad(lat1);  #  NEED TO CHECK FOR WRAP AROUND ISSUES
    lon1 = np.deg2rad(lon1);
    lat2 = np.deg2rad(lat2);
    lon2 = np.deg2rad(lon2);
    ang = 2*np.arcsin(np.sqrt(np.sin(abs(lat1 - lat2)/2)**2 + \
                              np.cos(lat1) * np.cos(lat2) * \
                              np.sin(abs(lon1 - lon2)/2)**2));
    R_earth = 6378.137 #Radius of earth, [km]
    grdDist = R_earth*ang;
    
    return grdDist;

################################################### 
    
def swathWidth2Grid(i, groundSwath, gridLat, gridLon):
    # i is orbital incline
    # i, gridLat, and gridLon is to be used for accuracy of number of grids
    
    vertDist = getGrdDist(gridLat[0],gridLon[0], gridLat[1], gridLon[0]);
    horiDist = getGrdDist(gridLat[0],gridLon[0], gridLat[0], gridLon[1]);
    diagDist = getGrdDist(gridLat[0],gridLon[0], gridLat[1], gridLon[1]);
    
    # gridOkay = [np.round(groundSwath/vertDist), np.round(groundSwath/horiDist), np.round(groundSwath/diagDist)]
    
    # gridOkay = np.array([vertDist <= groundSwath, horiDist <= groundSwath, diagDist <= groundSwath]);
    gridOkay = [vertDist, horiDist, diagDist]
    return gridOkay;

###################################################        

def addWidth(mask, gridOkay, groundSwath):
    radius = groundSwath/2
    vertDist = gridOkay[0]
    horiDist = gridOkay[1]
    minDist = np.min(gridOkay)
    N = np.round(radius/minDist);
    
    y, x = np.meshgrid(np.arange(-N,N+1)*vertDist, np.arange(-N,N+1)*horiDist)
    filt = x**2 + y**2 <= radius**2
    
    mask = conv2(mask, filt, mode='same')
    mask = (mask != 0)
    return mask

#def addWidth(mask, gridOkay):
#    #get original mask
#    origMaskIdx = np.argwhere(mask > 0);
#    ngrids = len(mask[0]);
#    #add width accordingly
#    addVert = int(gridOkay[0]);
#    addHori = int(gridOkay[1]);
#    addDiag = int(gridOkay[2]);
#    
#    for idx in range(0, len(origMaskIdx)):
#        
#        row= origMaskIdx[idx][0];
#        col = origMaskIdx[idx][1];
#        
#        if addVert > 0:
#            for x in range(1, addVert + 1):
#                if (row - x >= 0) and (row - x < ngrids):
#                    mask[row - x][col] = 1;
#                if (row + x >= 0) and (row + x < ngrids):
#                    mask[row + x][col] = 1;
#                    
#        if addHori > 0:
#            for x in range(1, addHori + 1):
#                if (col - x >= 0) and (col - x < ngrids):
#                    mask[row][col - x] = 1;
#                if (col + x >= 0) and (col + x < ngrids):
#                    mask[row][col + x] = 1;
#        
#        if addDiag > 0:
#            for x in range(1, addDiag +1):
#                if (row - x >= 0) and (col - x >= 0): #top left
#                    mask[row - x][col - x] = 1;
#                if (row - x >= 0) and (col + x < ngrids): #top right
#                    mask[row - x][col + x] = 1;
#                if (row + x < ngrids) and (col - x >= 0): #bottom left
#                    mask[row + x][col - x] = 1;
#                if (row + x < ngrids) and (col + x < ngrids): #bottom right
#                    mask[row + x][col + x] = 1;
#    
#    return mask;


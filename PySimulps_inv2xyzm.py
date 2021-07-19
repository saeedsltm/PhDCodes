#!/home/saeed/Programs/miniconda3/bin/python

'''

This script reads "inverion.out" and "polar.out"
and make xyzm.dat file

'''

import numpy as np
from datetime import datetime as dt
from LatLon import lat_lon as ll
from pandas import read_csv
import os

def get_header(l):

    if l[13] == "-": l = l[:13]+" "+l[14:]

    if l[13] == "6":

        l = l[:13]+"59.99"+l[18:]

    for i in [1,3,5,8,10]:

        if not l[i].strip(): l = l[:i]+"0"+l[i+1:]

        
    ort = dt.strptime(l[:18], " %y%m%d %H%M %S.%f")
    ort = ort.strftime('  %Y %m %d %H %M %S.%f')[:24]
    lat = ll.Latitude(degree=float(l[19:21]), minute=float(l[22:27])).decimal_degree
    lon = ll.Latitude(degree=float(l[29:31]), minute=float(l[32:37])).decimal_degree
    dep = float(l[39:44])
    mag = float(l[47:51])
    nob = float(l[52:54])
    rms = float(l[64:68])

    return ort, lat, lon, dep, mag, nob, rms
    
header = "     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC\n"

with open("polar.modi") as f, open("xyzm.dat", "w") as g:

    g.write(header)

    for line in f:

        if "DATE    ORIGIN" in line:

            l = next(f)

            ort, lat, lon, dep, mag, nob, rms = get_header(l)

        if "STN  DIST" in line:

            l = next(f)
            az = []
            ds = []

            while l.strip():
                
                ds.append(float(l[6:11]))
                az.append(float(l[12:15]))
                l = next(f)
                
            az = np.array(az)
            az = np.sort(az)
            u = np.hstack((az, 360))
            l = np.hstack((0, az))
            gap = u -l
            if gap.size<3: gap = np.max(gap)
            elif np.max(gap[1:-1]) < np.max([gap[0], gap[-1]]): gap = gap[0] + gap[-1]
            else: gap = np.max(gap[1:-1])
            mds = np.min(ds)
            nop = -99
            seh = 99
            sez = 99            
            fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
            fmt = fmt + ort+'\n'

            # lon lat dep mag phusd no_st mds gap rms seh sez

            g.write(fmt%(lon, lat, -dep, mag, nop, nob, mds, gap, rms, seh, sez))

data = read_csv("xyzm.dat", delim_whitespace=True)

with open("inversion.out") as f:

    hint = "St.Er.="
    i = 0

    for l in f:

        if "*******" in l:

            i+=1
            continue

        if hint in l:

            seh = np.sqrt(float(l[100:107])**2 + float(l[110:117])**2)
            sez = float(l[120:127])
            data.loc[i, "SEH"] = seh
            data.loc[i, "SEZ"] = sez
            i+=1

data.to_csv("tmp.dat", sep='\t', index=False, float_format="%.3f")
os.rename("tmp.dat", "xyzm.dat")

print "\n+++ %d events found."%i

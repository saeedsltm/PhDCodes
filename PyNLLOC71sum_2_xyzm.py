#!/home/saeed/Programs/miniconda3/bin/python

from glob import glob
from datetime import datetime as dt
from LatLon import lat_lon as ll
from random import gammavariate, choice, seed

def get_mag():

    seed(1)
    mag = [gammavariate(2,2) for _ in range(500)]
    mag = [_/max(mag) for _ in mag]
    mag = [_*5.5 for _ in mag]

    return mag

random_mag = get_mag()

inp = glob("loc/*.sum.grid0.loc.hypo_71")[0]

with open(inp) as f, open("xyzm.dat", "w") as g:

    g.write('     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC\n')

    for i,l in enumerate(f):

        if i>1:

            ot = l[:18]
            if not ot[13].strip(): ot = ot[:13]+"0"+ot[14:]
            if float(l[13:18])>=60.0: ot = ot[:13]+"59.99"
            ot = dt.strptime(ot, " %y%m%d %H%M %S.%f")
            ort = ot.strftime('  %Y %m %d %H %M %S.%f')[:24]

            lat = ll.Latitude(degree=float(l[19:21]), minute=float(l[22:27])).decimal_degree
            lon = ll.Longitude(degree=float(l[29:31]), minute=float(l[32:37])).decimal_degree
            dep = float(l[39:44])
            mag = choice(random_mag)
            nop = float(l[52:54])
            nst = nop
            mds = float(l[54:57])
            gap = float(l[58:61])
            rms = float(l[64:68])
            seh = float(l[69:73])
            sez = float(l[74:78])
            

            fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
            fmt = fmt + ort+'\n'

            # lon lat dep mag phusd no_st mds gap rms seh sez

            g.write(fmt%(lon, lat, dep, mag, nop, nst, mds, gap, rms, seh, sez))

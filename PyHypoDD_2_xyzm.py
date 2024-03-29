#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from math import sqrt
import os, sys
from pandas import read_json, to_datetime

events = read_json("events.json")
ots = to_datetime(events["OT"])
with open("hypoDD.reloc") as f, open("xyzm.dat", "w") as g:
    header = "     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC"
    g.write(header+"\n")
    for l in f:
        if "NaN" in l.split():continue
        _, lat, lon, dep,_,_,_,ex,ey,ez,yr,mo,dy,hr,mn,sc,mag,_,_,_,_,_,rms,_ = [float(_) for _ in l.split()]
        if sc == 60.0: sc = 59.99
        yr, mo, dy, hr, mn = [int(_) for _ in [yr, mo, dy, hr, mn]]
        msc = int((sc - int(sc))*1e6)
        sc = int(sc)
        ort = dt(yr,mo,dy,hr,mn,sc,msc)
        mag = events[abs(ots-ort)<td(seconds=5)].Mag.values[0]
        if not mag: mag = 0.0
        ort = ort.strftime("  %Y %m %d %H %M %S.%f")[:24]
        nop = 99
        nst = 99
        mds = 99
        gap = 360
        ex, ey, ez = ex/1000., ey/1000., ez/1000.
        seh = sqrt((ex)**2 + (ey)**2)
        sez = ez
        fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
        fmt = fmt + ort+'\n'
        # lon lat dep mag phusd no_st mds gap rms seh sez
        g.write(fmt%(lon, lat, dep, mag, nop, nst, mds, gap, rms, seh, sez))
cmd = "rm *reloc*"
os.system(cmd)

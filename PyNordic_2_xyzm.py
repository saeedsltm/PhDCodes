#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from random import gammavariate, choice, seed
from math import sqrt
import os

def get_mag():

    seed(1)
    mag = [gammavariate(2,2) for _ in range(500)]
    mag = [m/max(mag) for m in mag]
    mag = [m*3.5 for m in mag]

    return mag

random_mag = get_mag()

def mk_seisan_report():

    sfile = input('\n+++ Enter NORDIC file name:\n\n')

    with open('report.inp','w') as f:

        f.write('Date TimeE L E LatE LonE Dep E F Aga Nsta Rms Gap McA MlA MbA MsA MwA Fp Spec \n')
        f.write('1    2         3  6 4  7 5   8       9    10  11      12                      \n')

    os.system('report %s report.inp > /dev/null'%sfile)

mk_seisan_report()

with open("report.out") as f, open("xyzm.dat", "w") as g:

    g.write('     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC\n')

    next(f)
    n_corr_mag = 0
    n_events = 0

    for l in (f):

        if not l[22:43].strip(): continue

        yr = int(l[1:5])
        mo = int(float(l[6:8]))
        dy = int(float(l[8:10]))
        hh = int(float(l[11:13]))
        mm = int(float(l[13:15]))
        ss = float(l[16:20])
        if ss>=60.0: ss=59.99 
        ms = ss - int(ss)
        ms = int(ms*1e6)
        ort = dt(yr,mo,dy,hh,mm,int(ss),ms)
        ort = ort.strftime('  %Y %m %d %H %M %S.%f')[:24]
        lat = float(l[21:28])
        lon = float(l[29:37])
        dep = float(l[38:43])
        try:
            seh = sqrt(float(l[44:49])**2 + float(l[50:55])**2)
        except ValueError: 
            seh = 0.0
        try:
            sez = float(l[56:61])
        except ValueError:
            sez = 0.0 
        nst = int(l[62:65])
        rms = float(l[67:70])
        gap = int(l[71:74])
        if l[76:79].strip(): mag = float(l[76:79])
        else: mag = choice(random_mag); n_corr_mag+=1

        nop=nst
        mds=0
        
        fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
        fmt = fmt + ort+'\n'

        g.write(fmt%(lon, lat, dep, mag, nop, nst, mds, gap, rms, seh, sez))
        n_events+=1

cmd = "rm report*"
os.system(cmd)

print("\n+++ Number of converted events:", n_events)
print("+++ Number of corrected Magnitudes:", n_corr_mag)

#!/home/saeed/Programs/miniconda3/bin/python

from zipfile import ZipFile as zf
from glob import glob
from functools import reduce
from string import ascii_uppercase, digits
from random import choice
import os

LON_min=float(input("LON_min: "))
LON_max=float(input("LON_max: "))
LAT_min=float(input("LAT_min: "))
LAT_max=float(input("LAT_max: "))

lats = range(int(LAT_min), int(LAT_max+1))
lons = range(int(LON_min), int(LON_max+1))

def mergeGrd(grd1, grd2):
    grd3 = ''.join(choice(ascii_uppercase + digits) for _ in range(5))+".GRD"
    print("Merging %s & %s > %s"%(grd1, grd2, grd3))
    cmd = "gmt grdpaste %s %s -G%s"%(grd1, grd2, grd3)
    os.system(cmd)
    os.remove(grd1)
    os.remove(grd2)
    return grd3

for lat in lats:
    for lon in lons:
        f = r"N%2dE%03d.SRTMGL1.hgt.zip"%(lat, lon)
        if os.path.exists(f):
            print("Extracting %s"%(f))
            hgt = zf(f)
            hgt.extractall()
            hgtName = hgt.filelist[0].filename
            cmd = "gmt grdconvert %s `echo %s | cut -d. -f1`.grd"%(hgtName, hgtName)
            os.system(cmd)
            os.remove(hgtName)
        else:
            print("Required file '%s' not exists! Download it from: http://dwtkns.com/srtm30m/"%(f))

for lat in lats:
    grdFiles = sorted(glob("N%2dE*.grd"%(lat)))
    if len(grdFiles):
        reduce(mergeGrd, grdFiles)
        os.rename(glob("*.GRD")[0], "%d.grd"%(lat))
grdFiles = sorted(glob("*.grd"))
reduce(mergeGrd, grdFiles)
os.rename(glob("*.GRD")[0], "%d_%d-%d_%d.grd"%(LON_min, LON_max,
                                               LAT_min, LAT_max))

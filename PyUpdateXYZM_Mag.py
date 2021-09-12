#!/home/saeed/Programs/miniconda3/bin/python

from pandas import read_csv, to_datetime
from numpy import abs, sqrt, mean, pi
from datetime import timedelta as td

def d2k(degrees, radius=6371):

    return degrees * (2.0 * radius * pi / 360.0)

ref_xyzm = input("\n+++ Reference 'xyzm' file:\n\n")
tar_xyzm = input("\n+++ Target 'xyzm' file:\n\n")

#ref_xyzm = "xyzm.dat"
#tar_xyzm = "xyzm1.dat"

ref_db = read_csv(ref_xyzm, delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])
ref_db_dt = to_datetime(ref_db.YYYY_MM_DD_HH_MN_SEC.values, format="%Y %m %d %H %M %S.%f")

tar_db_w = read_csv(tar_xyzm, delim_whitespace=True)
tar_db = read_csv(tar_xyzm, delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])
tar_db_dt = to_datetime(tar_db.YYYY_MM_DD_HH_MN_SEC.values, format="%Y %m %d %H %M %S.%f")

c, cc = 0, 0
for x,y,t in zip(tar_db.LON.values, tar_db.LAT.values, tar_db_dt):

    cx = abs(x-ref_db.LON.values)
    cy = abs(y-ref_db.LAT.values)
    ch = d2k(sqrt(cx**2 + cy**2))
    ct = abs(t-ref_db_dt)
    ct = ct.total_seconds()
    ct = ct.values
    CT = (ch<30)&(ct<5)

    if any(CT):

        tar_db_w.MAG.values[c] = mean(ref_db[CT].MAG.values)
        
        cc+=1

    c+=1

tar_db_w.to_csv("xyzm_CorrMag.dat", sep="\t", float_format="%.3f", index=False)    
    
print("\n+++ %d corrected magnitudes"%(cc))


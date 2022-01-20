#!/home/saeed/Programs/miniconda3/bin/python

import pandas as pn
from datetime import timedelta as td
import os

inpNordic = input("\n+++ Enter NORDIC file:\n")


with open("report.inp", "w") as f:
    f.write("Date TimeE L E LatE LonE Dep E F Aga Nsta Rms Gap McA MlA MbA MsA MwA Fp Spec \n\
1    2         4    3    5                            6                         ")

cmd = "report {0} report.inp".format(inpNordic)
os.system(cmd)

with open("report.out") as f, open("tmp", "w") as g:
    next(f)
    g.write(" Year Date HRMM  Sec Longitud Latitud Depth   Ml\n")
    for l in f:
        for c in [6, 8, 11, 13, 16]:
            if l[c] == " ": l = l[:c]+"0"+l[c+1:]
        g.write(l)

os.rename("tmp", "report.out")
src = pn.read_csv("report.out", delim_whitespace=True)
des = pn.read_csv("xyzm.dat", delim_whitespace=True)
print(src.Ml.map(lambda x: '%3.1f' % float(x)))
with open("xyzm_new.dat", 'w') as f:
    f.write('LON\tLAT\tDEPTH\tMAG\tPHUSD\tNO_ST\tMIND\tGAP\tRMS\tSEH\tSEZ\tYYYY\tMM\tDD\tHH\tMN\tSEC\n')
    tmp = des.copy()
    tmp.LON = tmp.LON.map(lambda x: '%6.3f' % x)
    tmp.LAT = tmp.LAT.map(lambda x: '%6.3f' % x)
    tmp.DEPTH = tmp.DEPTH.map(lambda x: '%4.1f' % x)
    tmp.MAG = src.Ml.map(lambda x: '%3.1f' % float(x))
    tmp.PHUSD = tmp.PHUSD.map(lambda x: '%2d' % x)
    tmp.NO_ST = tmp.NO_ST.map(lambda x: '%2d' % x)
    tmp.MIND = tmp.MIND.map(lambda x: '%4.1f' % x)
    tmp.GAP = tmp.GAP.map(lambda x: '%2d' % x)
    tmp.RMS = tmp.RMS.map(lambda x: '%4.2f' % x)
    tmp.SEH = tmp.SEH.map(lambda x: '%4.2f' % x)
    tmp.SEZ = tmp.SEZ.map(lambda x: '%4.2f' % x)
    tmp.to_csv(f, index=False, header=False, sep="\t", 
                columns=["LON","LAT","DEPTH","MAG","PHUSD","NO_ST","MIND","GAP","RMS","SEH","SEZ", "YYYY","MM","DD","HH","MN","SEC"])
print("\n+++ Magnitude substitution for %d events."%(src.Ml.size))
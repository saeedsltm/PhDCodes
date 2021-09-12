#!/home/saeed/Programs/miniconda3/bin/python

import pandas as pn


"""
script for converting IIEES catalog file to xyzm file format.

LogChange:
21-Jun-2020 : Init.


"""

iieesInp = input("\n+++ IIEES catalog file:\n")

d = pn.read_csv(iieesInp, delim_whitespace=True, usecols=[0,1,2,3,4,5,6])
d = d.sort_values("Mag.")

with open("xyzm.dat", "w") as f:

    f.write("LON	LAT	DEPTH	MAG	PHUSD	NO_ST	MIND	GAP	RMS	SEH	SEZ	YYYY	MM	DD	HH	MN	SEC\n")
    
    for i,v in d.iterrows():

        if i == 0: continue

        x = float(v["Lon."])
        y = float(v["Lat."])
        z = float(v["Depth"])
        m = float(v["Mag."])
        Y = int(v["Date(yyyy/mm/dd)"].split("/")[0])
        M = int(v["Date(yyyy/mm/dd)"].split("/")[1])
        D = int(v["Date(yyyy/mm/dd)"].split("/")[2])
        HH = int(v["Time(UTC)"].split(":")[0])
        MM = int(v["Time(UTC)"].split(":")[1])
        SS = float(v["Time(UTC)"].split(":")[2])      

        f.write("%5.2f	%5.2f	%5.1f	%4.1f	99	99	0	0	0	0	0	%4d	%02d	%02d	%02d	%02d	%4.1f\n"%(
            x,y,z,m,Y,M,D,HH,MM,SS))

print("\n+++ %d events converted."%(d["Lon."].size))

#!/home/saeed/Programs/miniconda3/bin/python

import pandas as pn


"""
script for converting ISC catalog file to xyzm file format.

Use ISC Web-Page: http://www.isc.ac.uk/iscbulletin/search/catalogue/
Note: set magnitude author to only ISC and magnitude type to MB (MS).

LogChange:
21-Jun-2020 : Init.


"""

iscInp = input("\n+++ ISC catalog file:\n")

d = pn.read_csv(iscInp, skipinitialspace=True, index_col=False)
d = d.sort_values("MAG ")

with open("xyzm.dat", "w") as f:

    f.write("LON	LAT	DEPTH	MAG	PHUSD	NO_ST	MIND	GAP	RMS	SEH	SEZ	YYYY	MM	DD	HH	MN	SEC\n")
    
    for i,v in d.iterrows():

        if i == 0: continue

        x = float(v["LON      "])
        y = float(v["LAT     "])
        z = float(v["DEPTH"])
        m = float(v["MAG "])
        Y = int(v["DATE      "].split("-")[0])
        M = int(v["DATE      "].split("-")[1])
        D = int(v["DATE      "].split("-")[2])
        HH = int(v["TIME       "].split(":")[0])
        MM = int(v["TIME       "].split(":")[1])
        SS = float(v["TIME       "].split(":")[2])      

        f.write("%5.2f	%5.2f	%5.1f	%4.1f	99	99	0	0	0	0	0	%4d	%02d	%02d	%02d	%02d	%4.1f\n"%(
            x,y,z,m,Y,M,D,HH,MM,SS))

print("\n+++ %d events converted."%(d["LON      "].size))

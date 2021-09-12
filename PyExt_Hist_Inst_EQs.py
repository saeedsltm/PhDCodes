#!/home/saeed/Programs/miniconda3/bin/python

import pandas as pn
import os

##LON_min=50.7926
##LON_max=51.4074
##LAT_min=28.4891
##LAT_max=29.2109

LON_min = float(input("\n+++ Min Longitude:\n"))
LON_max = float(input("\n+++ Max Longitude:\n"))
LAT_min = float(input("\n+++ Min Latitude:\n"))
LAT_max = float(input("\n+++ Max Latitude:\n"))

dFile = os.path.join(os.environ["GMTHOME"], "Events", "Catoalog_2000.xls")
d_hist = pn.read_excel(dFile, sheet_name="Historical")
d_1900_1963 = pn.read_excel(dFile, sheet_name="1900-1963")
d_1964_2000 = pn.read_excel(dFile, sheet_name="1964-2000")

d_hist = d_hist[(d_hist["Lat."]>=LAT_min)&(d_hist["Lat."]<=LAT_max)&
      (d_hist["Long."]>=LON_min)&(d_hist["Long."]<=LON_max)]

d_1900_1963 = d_1900_1963[(d_1900_1963["Lat."]>=LAT_min)&(d_1900_1963["Lat."]<=LAT_max)&
      (d_1900_1963["Long."]>=LON_min)&(d_1900_1963["Long."]<=LON_max)]

d_1964_2000 = d_1964_2000[(d_1964_2000["Lat."]>=LAT_min)&(d_1964_2000["Lat."]<=LAT_max)&
      (d_1964_2000["Long."]>=LON_min)&(d_1964_2000["Long."]<=LON_max)]



with open("xyzm_historical.dat", "w") as f:

    f.write("LON	LAT	DEPTH	MAG	PHUSD	NO_ST	MIND	GAP	RMS	SEH	SEZ	YYYY	MM	DD	HH	MN	SEC\n")

    for x,y,m in zip(d_hist["Long."], d_hist["Lat."], d_hist["Ms"]):

        f.write("%5.2f	%5.2f	10	%4.1f	10	10	10	10	0	0	0	1000	01	01	00	00	00\n"%(x,y,m))

d_hist.to_csv("historical.csv")


with open("xyzm_1900_1963.dat", "w") as f:

    f.write("LON	LAT	DEPTH	MAG	PHUSD	NO_ST	MIND	GAP	RMS	SEH	SEZ	YYYY	MM	DD	HH	MN	SEC\n")

    for Y,M,D,x,y,z,mb,Ms in zip(d_1900_1963["Y"],d_1900_1963["M"],d_1900_1963["D"],
                                 d_1900_1963["Long."], d_1900_1963["Lat."], d_1900_1963["Dept"],
                                 d_1900_1963["mb"],d_1900_1963["Ms"]):

        f.write("%5.2f	%5.2f	%4.1f	%4.1f	10	10	10	10	0	0	0	%4d	%2d	%2d	00	00	00\n"%(x,y,z,Ms,Y,M,D))

d_1900_1963.to_csv("1900_1963.csv")

with open("xyzm_1964_2000.dat", "w") as f:

    f.write("LON	LAT	DEPTH	MAG	PHUSD	NO_ST	MIND	GAP	RMS	SEH	SEZ	YYYY	MM	DD	HH	MN	SEC\n")

    for Y,M,D,x,y,z,mb,Ms in zip(d_1964_2000["Y"],d_1964_2000["M"],d_1964_2000["D"],
                                 d_1964_2000["Long."], d_1964_2000["Lat."], d_1964_2000["Dept"],
                                 d_1964_2000["mb"],d_1964_2000["Ms"]):

        f.write("%5.2f	%5.2f	%4.1f	%4.1f	10	10	10	10	0	0	0	%4d	%2d	%2d	00	00	00\n"%(x,y,z,mb,Y,M,D))

d_1964_2000.to_csv("1964_2000.csv")

print("\n+++ historical events:%6d"%(d_hist["Lat."].size))
print("+++ 1900-1963 events :%6d"%(d_1900_1963["Lat."].size))
print("+++ 1964-2000 events :%6d"%(d_1964_2000["Lat."].size))
print("\n+++ 6 Files created.")

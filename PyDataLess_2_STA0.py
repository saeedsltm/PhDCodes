#!/home/saeed/Programs/miniconda3/bin/python

import obspy as obs
from LatLon import lat_lon as ll

"""

Script for converting dataless to STATION0.HYP.

outputs:

STATION0.HYP

ChangeLogs:

20-APR-2021 > Initial.

"""
inp = input("\n+++ Input DataLess file:\n")
d = obs.read_inventory(inp)
dic = {}
for net in d:
    for sta in net:
        lat = ll.Latitude(sta.latitude)
        lon = ll.Longitude(sta.longitude)
        dic[sta.code] = (sta.code, lat, lon, sta.elevation)
with open('stations.dat', 'w') as f, open("STATION0.HYP", "w") as g:
    for i in dic:
        g.write("  %-4s%02d%05.2f%1s %02d%05.2f%1s%0004d\n"%(dic[i][0],
                                                             dic[i][1].degree, dic[i][1].decimal_minute, dic[i][1].get_hemisphere(),
                                                             dic[i][2].degree, dic[i][2].decimal_minute, dic[i][2].get_hemisphere(),
                                                             dic[i][3]))

#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll
from numpy import loadtxt

def upper(s):
    return s.upper()

# read station info
def readStaInfo(name):
    stations = {}
    with open("%s"%(name)) as f:
        for l in f:
            if "*" in l: continue
            sta = l[:4].strip()
            lat = ll.Latitude(degree=float(l[4:6]), minute=float(l[7:12])).decimal_degree
            lon = ll.Longitude(degree=float(l[14:16]), minute=float(l[17:22])).decimal_degree
            elv = float(l[22:27])
            stations[sta] = {"lat":round(lat, 4), "lon":round(lon, 4), "elv":elv}
    return stations

def sta2txt(sta_dic):
    with open("station.dat", "w") as f:
        for sta in sorted(sta_dic.keys(), key=lambda x:(len(x), upper(x), sorted(x))):
            lat = ll.Latitude(sta_dic[sta]["lat"])
            lon = ll.Longitude(sta_dic[sta]["lon"])
            elv = sta_dic[sta]["elv"]
            f.write("%-4s %7.4f %7.4f %0004d\n"%(sta, lat.decimal_degree, lon.decimal_degree, elv))

inp = input("\n+++ Hypoellipse station file:\n")
sta_dic = readStaInfo(inp)
sta2txt(sta_dic)

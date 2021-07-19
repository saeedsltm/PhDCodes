#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from random import gammavariate, choice, seed
from copy import deepcopy as dp
from LatLon import lat_lon as ll
import os, sys

#_________GET INPUT

inp = input("\n+++ Nordic file:\n")


if not os.path.exists("STATION0.HYP"): print("\n+++ No STATION0.HYP found!\n"); sys.exit(0)

#_________CONVERT PHASE

def get_mag():

    seed(1)
    mag = [gammavariate(2,2) for _ in range(500)]
    mag = [_/max(mag) for _ in mag]
    mag = [_*5.5 for _ in mag]

    return mag

random_mag = get_mag()    

def get_ot(l):

    if l[16]=="6": l = l[:16]+"59.00"+l[20:]
    
    for i in [6,8,11,13,16]:

        if not l[i].strip():

            l = l[:i]+"0"+l[i+1:]

    ot = dt.strptime(l[:20], " %Y %m%d %H%M %S.%f")
    lat = float(l[23:30])
    lon = float(l[31:38])
    dep = float(l[39:43])
    erh = 0
    erz = 0
    rms = float(l[52:55])

    if l[56:59].strip() and float(l[56:59])!=0: mag = float(l[56:59])
    else: mag = choice(random_mag)

    return ot, lat, lon, dep, mag, erh, erz, rms

def get_ttim(ot, l, wet, log):

    for i in [18, 19, 20, 22, 23]:

        if not l[i].strip():

            l = l[:i]+"0"+l[i+1:]

    tmp = dp(ot)

    sec = float(l[22:28])
    if sec>=60.00: sec=59.999
    l = l[:22]+'%006.3f'%(sec)+l[28:]
    at = dt.strptime(l[18:28], "%H%M%S.%f")    
    at = at.replace(year=tmp.year, month=tmp.month, day=tmp.day, hour=at.hour, minute=at.minute, second=at.second, microsecond=at.microsecond)
    if ot.hour == 23 and at.hour==0: at = at + td(days=1)
    ttim = at-ot
    ttim = ttim.total_seconds()

    if wet>1e-5 and (ttim>100 or ttim<0):
        print("Warning! Travel time exceeded 100s or is negative! Check log.dat")
        log.write(ot.isoformat()+" > "+l)

    return ttim
    

def get_wet(l):

    if l[14] == " ": return 1
    elif l[14] == "4": return 1e-6
    else: return (0.5)**float(l[14])

def get_pha(l, log):

    if l[10].strip() and l[10].upper()=="P":

        sta = l[:5].strip().upper()
        wet = get_wet(l)
        pha = "P"
        tti = get_ttim(ot, l, wet, log)

        line = "%4s %7.3f %.1e %1s\n"%(sta, tti, wet, pha)
        g.write(line)
            
    elif l[10].strip() and l[10].upper()=="S":

        sta = l[:5].strip().upper()
        wet = get_wet(l)
        pha = "S"
        tti = get_ttim(ot, l, wet, log)

        line = "%4s %7.3f %.1e %1s\n"%(sta, tti, wet, pha)
        g.write(line)

#________MAIN
        
with open(inp) as f, open("phase.dat", "w") as g, open("log.dat", "w") as log:

    evn = 0
    flag = False

    for l in f:

        if l.strip() and l[24:43].strip() and l[79]=="1":

            ot, lat, lon, dep, mag, erh, erz, rms = get_ot(l)
            if not ((lat>23)&(lat<42))&((lon>42)&(lon<63)): continue
            evn+=1

            header = "#, YR, MO, DY, HR, MN, SC, LAT, LON, DEP, MAG, EH, EZ, RMS, ID"
            line = "# %22s %7.3f %7.3f %5.1f %4.1f %6.1f %6.1f %5.2f %6d\n"%(ot.strftime("%Y %m %d %H %M %S.%f")[:22],
                                                                             lat, lon, dep, mag, erh, erz, rms, evn)
            g.write(line)
            flag = True

        if flag and not l.strip(): flag = False 

        if flag and l.strip() and l[79] in ["4", " "]:

            pha = get_pha(l, log)

#_________CONVERT STATION
            
with open("STATION0.HYP") as f, open("station.dat", "w") as g:

    sta_list = []

    for l in f:

        if len(l.strip())>20 and [l[13],l[22]] == ["N", "E"]:

            sta = l[:6].strip().upper()
            if sta not in sta_list: sta_list.append(sta)
            else: continue
            lat = ll.Latitude(degree=float(l[6:8]), minute=float(l[8:13])).decimal_degree
            lon = ll.Longitude(degree=float(l[15:17]), minute=float(l[17:21])).decimal_degree
            elv = float(l[23:27])
            g.write("%4s %7.3f %7.3f %5d\n"%(sta, lat, lon, elv))

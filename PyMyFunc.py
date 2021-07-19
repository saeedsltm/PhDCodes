#!/home/saeed/Programs/miniconda3/bin/python

from numpy import min, max, pi
from datetime import datetime as dt

#__________________FUNCTION TO SCALE INPUT DATA FROM RANGE (a,b) TO NEW RANGE (c,d).

def scale_data(data, new_range=[4.,8.]):

    old_min = float(min(data))
    old_max = float(max(data))
    new_min = float(min(new_range))
    new_max = float(max(new_range))

    return ( (data - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min

##Example
##from numpy import arange
##print scale_data(arange(1.,256.), new_range=[4.,8.])

#__________________FUNCTIONS TO CONVERT KILOMETER TO DEGREE AND VIC VERCA.

def k2d(kilometer, radius=6371):

    return kilometer / (2.0 * radius * pi / 360.0)

def d2k(degrees, radius=6371):

    return degrees * (2.0 * radius * pi / 360.0)

#__________________FUNCTION TO GET CORRECT ORIGIN TIME.

def get_ot(yy,mm,dd,HH,MM,SS,MS):

    if SS >= 60:

        SS = SS - 60
        MM+=1

    if MM >= 60:

        MM = MM - 60
        HH+=1

    if HH >= 24:

        HH = HH - 24
        dd+=1

    if 0<=yy<=80: yy+=2000
    if 80<=yy<=99: yy+=1900
            
    ot = dt(yy,mm,dd,HH,MM,int(SS),MS)

    return ot

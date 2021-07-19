#!/home/saeed/Programs/miniconda3/bin/python

import os
import sys
from datetime import datetime as dt
from numpy import array, sqrt
from scipy.stats import linregress
import pylab as plt
from statsmodels.formula.api import ols
from initial_mpl import init_plotting

"""

Script for make a reduction velocity plot.

ChangeLogs:

04-Aug-2017 > Initial.

"""

nordic_inp = raw_input('\n\n+++ Enter file with NORDIC format:\n\n')
reduced_v  = input('\n+++ Enter Reduction Velocity [km/s]:\n\n')

def outlier(x, y, r=0.5):

    regression   = ols("data ~ x", data=dict(data=y, x=x)).fit()
    test         = regression.outlier_test()
    outliers_ind  = list((i for i,t in enumerate(test.iloc[:,2]) if t < r))
    good_id       = list(set(range(len(x)))-set(outliers_ind))

    return good_id, outliers_ind

def get_time(year,month,day,hour,minute,sec,msec):

    if sec >= 60:

        sec = sec - 60
        minute+=1

    if minute >= 60:

        minute = minute - 60
        hour+=1

    if hour >= 24:

        hour = hour - 24
        day+=1
            
    time = dt(year,month,day,hour,minute,int(sec),msec)

    return time

def run_red_v(evt):

    # get OT time

    l1 = evt[0]
   
    year   = int(l1[0:5])
    month  = int(l1[6:8])
    day    = int(l1[8:10]) 
    hour   = int(l1[11:13])
    minute = int(l1[13:15]) 
    sec    = float(l1[16:20])
    msec   = int((sec-int(sec))*1e6)
    ot     = get_time(year,month,day,hour,minute,sec,msec)
    tt     = []
    ds     = []

    # get AR time

    for l in evt:

        if l[79:80] in ['4',' '] and l[10:11].upper() == 'P' and l[14:15] != '4':

            year   = int(l1[0:5])
            month  = int(l1[6:8])
            day    = int(l1[8:10]) 
            hour   = int(l[18:20])
            minute = int(l[20:22]) 
            sec    = float(l[23:28])
            msec   = int((sec-int(sec))*1e6)
            ar     = get_time(year,month,day,hour,minute,sec,msec)

            try:

                dis = float(l[70:75])

            except ValueError:

                continue

            # calculate TT

            df = ar - ot
            df = df.total_seconds()

            if 0 < df < 500 :

                tt.append(df)
                ds.append(dis)

    return ds,tt

distance = []
travel_t = []

with open(nordic_inp) as f:

    evt = []

    for l in f:

        evt.append(l)

        if not l.strip():

            d, t =  run_red_v(evt)

            for i,j in zip(d,t):
                
                distance.append(i)
                travel_t.append(j)

            evt = []

d = array(distance)
t = array(travel_t)

x = d
y = t-x/reduced_v

init_plotting()
plt.plot(x,y,'ro',linestyle='')
plt.ylim(-20,20)
plt.xlabel('$Distance [km]$',fontsize=18)
plt.ylabel('$t-x/v_{red} [s]$',fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()

xc = input('\n+++ Enter crossover distance [km]:\n\n')
v2 = input('\n+++ Enter Moho velocity [km/s]:\n\n')

h = xc/(2.0*sqrt((v2+reduced_v)/(v2-reduced_v)))

print '\n+++ The Moho depth is: %.1f'%h

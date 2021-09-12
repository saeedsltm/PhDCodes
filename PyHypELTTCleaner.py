#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from LatLon import lat_lon as ll
from time import mktime
from numpy import array, abs, arange, char, genfromtxt, linspace, newaxis, logical_not, zeros, sqrt
from sklearn import linear_model, datasets
import proplot as plt
from PyMyFunc import get_ot
import os, sys
from shutil import copy

"""

Script for remove outlier phases from hypoellipse output file "hypel.out", using
RANSAC algorithm. All P and S phases whom are identified as outliers will be miss-
weighted by assining w=4 in "hypoel_clean.out".

see: http://scikit-learn.org/stable/auto_examples/linear_model/plot_ransac.html

inputs:

hypoel.pha
hypoel.out

outputs:

hypoel_clean.pha

ChangeLogs:

19-Feb-2018 > Initial.
24-Jul-2019 > Fixed issue for S phase reweighting.
09-Jul-2020 > True raypath (including hypocenter instead of epicenter) replaced with x-projected one.
31-Mar-2021 > Improved figures quality using ProPlot.

"""

#___________________Get inputs from user

dist_max = input('\n+++ Maximum Distance between source-station pair [def=100km]:\n')
dist_step = input('\n+++ Distance interval between source-station pair [def=25km]:\n')
dep_max = input('\n+++ Maximum depth for EQ source [def=20km]:\n')
p_outlier_trs = input('\n+++ P outlier rejection threshold [def=2sec]:\n')
s_outlier_trs = input('\n+++ S outlier rejection threshold [def=2sec]:\n')

defaults = {'dist_max':100,
            'dist_step':25,
            'dep_max':20,
            'p_outlier_trs':2,
            's_outlier_trs':2}

for key in defaults.keys():
    if eval(key):
        defaults[key] = float(eval(key))
   
#___________________Detect outliers using Random Sample Consensus (RANSAC) method

def get_ransac(x, y, tr):
    
    # Robustly fit linear model with RANSAC algorithm
    ransac = linear_model.RANSACRegressor(residual_threshold=tr, min_samples=(x.size//3+1))
    ransac.fit(x, y)
    inlier_mask = ransac.inlier_mask_
    outlier_mask = logical_not(inlier_mask)

    # Predict data of estimated models
    predict_x = arange(x.min(), x.max())[:, newaxis]
    predict_y = ransac.predict(predict_x)
    velocity = 1./ransac.estimator_.coef_

    return inlier_mask, outlier_mask, predict_x, predict_y, velocity

#___________________Read DateTime value

def get_dt(l):

    for i in range(0,12,2):
        if l[i] == " ": l = l[:i]+"0"+l[i+1:]

    DateTime = dt.strptime(l,"%y%m%d%H%M%S.%f")

    return DateTime
    
#___________________Define output files

output = open('tt.dat','w')
outlier = open('outliers.dat','w')
hypclean = open('hypoel_clean.pha','w')

with open(output.name, 'a') as f:
    f.write('# Sta Pha     OriginTime  ObservedTime  TravelTime  Distance   Depth\n')

with open(outlier.name, 'a') as f:
    f.write('# Sta Pha     OriginTime  ObservedTime  TravelTime  Distance   Depth\n')
    
#___________________Read Hypoellipse output file

if not os.path.exists('hypoel.out'):
    print('\n+++ No "hypoel.out" file was found!\n')
    sys.exit()
    
with open('hypoel.out') as f:

    new_evt = []

    for l in f:

        if 'earthquake location' in l:
            new_evt = []
            flag_xx = False

        if 'xxxxx insufficient data' in l:
            flag_xx = True

        if 'date    origin' in l:
            l = next(f)
            y = int(l[1:5])
            m = int(l[5:7])
            d = int(l[7:9])
            H = int(l[10:12])
            M = int(l[12:14])
            S = float(l[15:20])
            MS= int((S-int(S))*1e6)
            S = int(S)
            OT = get_ot(y,m,d,H,M,S,MS)
            dep = float(l[41:46])
            
        if 'travel times and delays' in l:
            l = next(f)
            l = next(f)
            
            while l.strip() and "*****" not in l:
                sta = l[1:5].strip()
                pha = l[12:14].replace("  ","P").upper()
                if "P" in pha: pha = "P"
                if "S" in pha: pha = "S"
                pol = l[14]
                wet = int(l[15].replace(' ','0'))
                
                if pha == "P":
                    trt = float(l[73:79])
                    dis = float(l[46:51])
                else:
                    trt = float(l[73:79])
                    
                with open(output.name, 'a') as o:
                    if not flag_xx and wet < 4:
                        obs = OT + td(seconds=trt)
                        obs = float(obs.strftime("%s.%f"))
                        ort = float(OT.strftime("%s.%f"))
                        o.write('%5s %1s   %14.2f %14.2f   %6.2f     %6.1f   %6.1f\n'%(sta, pha, ort, obs, trt, dis, dep))
                
                l = next(f)
            
#___________________Plot Travel-Time curve and cross outlires

import warnings
warnings.filterwarnings("ignore")

distances = range(0, int(defaults['dist_max']), int(defaults['dist_step']))
dist_step = defaults['dist_step']
velOut = open("velOut.dat", "w")

for distance in distances:

    print('+++ Working on distances => %d-%d.'%(distance, distance+dist_step))

    data = genfromtxt('tt.dat')
    phas = genfromtxt('tt.dat',dtype=str)

    c = (data[:,5]>=distance)&(data[:,5]<=(distance+dist_step))
    phas=phas[c]
    data=data[c]

    dep_max = int(defaults['dep_max'])
    bnd = linspace(0, dep_max, 6, dtype=int)
    dep_step = int(bnd[1]-bnd[0])

    data_p = data[phas[:,1]=='P']
    data_s = data[phas[:,1]=='S']

    fig, axs = plt.subplots(ncols=3, nrows=2, share=1)
    axs.format(xlabel="Distance (km)", ylabel="Travel Time (s)")

    for i,b in enumerate(bnd):

        ax = axs[i]
        ax.grid(ls=':')
        
        # phase-P
        p_outlier_trs = defaults['p_outlier_trs']
        z = data_p[(data_p[:,6]>=b)&(data_p[:,6]<=b+dep_step)][:,6]
        x = data_p[(data_p[:,6]>=b)&(data_p[:,6]<=b+dep_step)][:,5]
        y = data_p[(data_p[:,6]>=b)&(data_p[:,6]<=b+dep_step)][:,4]
        z = z.reshape((z.size,1))
        x = x.reshape((x.size,1))
        y = y.reshape((y.size,1))
        
        # Note! we should consider total raypath not only x projection, so x = sqrt(x^2 + z^2)
        x = sqrt(x**2 + z**2)

        if x.size < 5:
            continue
        else:
            inlier_mask, outlier_mask, predict_x, predict_y, pvelocity = get_ransac(x, y, p_outlier_trs)
            outliers = phas[phas[:,1]=='P'][(data_p[:,6]>=b)&(data_p[:,6]<=b+dep_step)][outlier_mask]
            ax.scatter(x[inlier_mask][:,0], y[inlier_mask][:,0], marker="o", facecolors="lime9", edgecolors="k", label='P', legend="lr")
            ax.scatter(x[outlier_mask][:,0], y[outlier_mask][:,0], marker="x", color="k")
            ax.plot(predict_x[:,0], predict_y[:,0], color="lime5")
            ax.format(ultitle=r'Depth=%d-%d, $\mathrm{V_p}$=%.1f'%(b,b+dep_step,pvelocity))
            with open(velOut.name, "a") as f: f.write("%d\t%d\t%d\t%d\t%.2f\t\n"%(distance,distance+dist_step,b,b+dep_step,pvelocity))
            with open(outlier.name,'a') as f:
                for l in outliers:
                    f.write('%5s %1s   %14.2f %14.2f   %6.2f     %6.1f   %6.1f\n'%(l[0].upper(), l[1].upper(), float(l[2]),
                                                                                   float(l[3]), float(l[4]), float(l[5]), float(l[6])))

        # phase-S
        s_outlier_trs = defaults['s_outlier_trs']
        z = data_s[(data_s[:,6]>=b)&(data_s[:,6]<=b+dep_step)][:,6]
        x = data_s[(data_s[:,6]>=b)&(data_s[:,6]<=b+dep_step)][:,5]
        y = data_s[(data_s[:,6]>=b)&(data_s[:,6]<=b+dep_step)][:,4]
        z = z.reshape((z.size,1))
        x = x.reshape((x.size,1))
        y = y.reshape((y.size,1))

        # Note! we should consider total raypath not only x-projeced, so x = sqrt(x^2 + z^2)
        x = sqrt(x**2 + z**2)
                
        if x.size<5:
            continue
        else:
            inlier_mask, outlier_mask, predict_x, predict_y, svelocity = get_ransac(x, y, s_outlier_trs)
            outliers = phas[phas[:,1]=='S'][(data_s[:,6]>=b)&(data_s[:,6]<=b+dep_step)][outlier_mask]
            ax.scatter(x[inlier_mask][:,0], y[inlier_mask][:,0], marker="o", facecolors="orange9", edgecolors="k", label='S', legend="lr")
            ax.scatter(x[outlier_mask][:,0], y[outlier_mask][:,0], marker="x", color="k")
            ax.plot(predict_x[:,0], predict_y[:,0], color="orange5")
            ax.format(ultitle=r'Depth=%d-%d, $\mathrm{V_p}$=%.1f, $V_s$=%.1f'%(b,b+dep_step,pvelocity,svelocity))
            with open(velOut.name, "a") as f: f.write("%d\t%d\t%d\t%d\t%.2f\t%.2f\n"%(distance,distance+dist_step,b,b+dep_step,pvelocity,svelocity))
            with open(outlier.name,'a') as f:
                for l in outliers:
                    f.write('%5s %1s   %14.2f %14.2f   %6.2f     %6.1f   %6.1f\n'%(l[0].upper(), l[1].upper(), float(l[2]),
                                                                                   float(l[3]), float(l[4]), float(l[5]), float(l[6])))
    output='TT_%d_%d.png'%(distance,distance+dist_step)
    fig.save(output, transparent=False)
    plt.close()

#___________________Remove outliers from origin file

print('\n+++ Removing outliers from origin file.')

outliers = genfromtxt('outliers.dat', dtype=str)
NCO = 0

if outliers.ndim == 1:
    outliers = outliers.reshape((1,outliers.size))

if outliers.size:
    with open('hypoel.pha') as f, open(hypclean.name, 'a') as g:
        for l in f:
            if l[:10].strip():
                sta = l[:4].strip().upper()
                ppha= l[5].upper()
                if len(l)>=38 and "*****" not in l: spha= l[37].strip().upper()
                else: spha = ""
                year= int(l[9:11])
                mont= int(l[11:13])
                day = int(l[13:15])
                hor = int(l[15:17])
                miu = int(l[17:19])
                sec = float(l[19:24])
                msec= sec-int(sec)
                obs = get_dt(l[9:24])
                obs = float(obs.strftime("%s.%f"))
                
                cp1 = char.upper(outliers[:,0])==sta
                cp2 = char.upper(outliers[:,1])==ppha
                cp3 = array(outliers[:,3],dtype=float)==obs
                outlier_p = outliers[(cp1)&(cp2)&(cp3)]

                outlier_s = zeros(0)
                if spha:
                    obs = obs - sec + float(l[30:36])
                    cs1 = char.upper(outliers[:,0])==sta
                    cs2 = char.upper(outliers[:,1])==spha
                    cs3 = array(outliers[:,3],dtype=float)==obs
                    outlier_s = outliers[(cs1)&(cs2)&(cs3)]
                    
                if outlier_p.size and not outlier_s.size:
                    l = l[:7]+'4'+l[8:]
                    g.write(l)
                    NCO+=1
                    continue

                if outlier_p.size and outlier_s.size:
                    l = l[:7]+'4'+l[8:39]+'4'+l[40:]
                    g.write(l)
                    NCO+=1
                    continue

                if not outlier_p.size and outlier_s.size:
                    l = l[:39]+'4'+l[40:]
                    g.write(l)
                    NCO+=1
                    continue
                
                g.write(l)
                
            else:
                g.write(l)
            
else: copy("hypoel.pha", hypclean.name)

os.remove('tt.dat')
print("+++ %d Outlier(s) Re-Weighted."%NCO)

#!/home/saeed/Programs/miniconda3/bin/python

import matplotlib.pyplot as plt
from numpy import loadtxt
from glob import glob
from re import split
import os, sys
sys.path.append(os.environ["PYT_PRG"])
from initial_mpl import init_plotting_isi
from adjustText import adjust_text


"""
name:
PySimulps_SingleTOC.py

Dec:
plot single iteration for damping values

ChangeLog:
02-April-2020 > initial.

"""

#Read damping files and damping values
daming_files = glob("damp_*.dat")
daming_files = sorted(daming_files, key=lambda x: int(split("_|\.", x)[1]))
dampings = loadtxt("damping.dat", dtype=int)

#Make an empty dictionary for damping vales, data variance and model variance of Vp and Vp/Vs
DVp, DVpVs = {"D":[], "DV":[], "MV":[]}, {"D":[], "DV":[], "MV":[]}

for i, df in enumerate(daming_files):

    DVp["D"].append(dampings[i][0])
    DVpVs["D"].append(dampings[i][1])

    with open(df) as f:

        for line in f:

            if "DATA VARIANCE" == line.strip():

                l = next(f)
                
                DVp["DV"].append(float(l.split()[0]))
                DVpVs["DV"].append(float(l.split()[0]))

            if "Vp VARIANCE" == line.strip():

                l = next(f)
                
                DVp["MV"].append(float(l.split()[0]))

            if "VpVs VARIANCE" == line.strip():

                l = next(f)
                
                DVpVs["MV"].append(float(l.split()[0]))


#Plot Section, Parameter initialization
init_plotting_isi(16,7)
plt.rcParams['axes.labelsize'] = 8

#Vp damping L-Curve
ax = plt.subplot(121)
ax.set_facecolor("#FFFBD0")
(i.set_linewidth(0.6) for i in ax.spines.items())
title = 'TOC ($V_p$)'
ax.set_title(title)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

ax.plot(DVp["MV"], DVp["DV"],lw=1,mew=.5,mfc='w',marker='o',ms=3,c='k')

texts = [ax.text(x, y, t, ha='center', va='center') for x,y,t in zip(DVp["MV"], DVp["DV"], DVp["D"])]
ax.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
xbond = ax.get_xlim()
ybond = ax.get_ylim()
xlen = xbond[1] -xbond[0]
ylen = ybond[1] -ybond[0]
ax.set_xlim(0-.05*xlen,xbond[1]+.05*xlen)
ax.set_ylim(ybond[0]-.05*ylen,ybond[1]+.05*ylen)
adjust_text(texts)

#Vp/Vs damping L-Curve
ax = plt.subplot(122)
ax.set_facecolor("#FFFBD0")
(i.set_linewidth(0.6) for i in ax.spines.items())
title = 'TOC ($V_p\//V_s$)'
ax.set_title(title)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

ax.plot(DVpVs["MV"], DVpVs["DV"],lw=1,mew=.5,mfc='w',marker='o',ms=3,c='k')

texts = [ax.text(x, y, t, ha='center', va='center') for x,y,t in zip(DVpVs["MV"], DVpVs["DV"], DVpVs["D"])]
ax.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
xbond = ax.get_xlim()
ybond = ax.get_ylim()
xlen = xbond[1] -xbond[0]
ylen = ybond[1] -ybond[0]
ax.set_xlim(0-.05*xlen,xbond[1]+.05*xlen)
ax.set_ylim(ybond[0]-.05*ylen,ybond[1]+.05*ylen)
adjust_text(texts)

#Save figure
plt.tight_layout(pad=.3, w_pad=0.5, h_pad=0.5)   
plt.savefig('TOS_SIngle.png', dpi=500, quality=100)
plt.close()

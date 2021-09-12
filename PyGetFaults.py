#!/home/saeed/Programs/miniconda3/bin/python

import pandas as pn
from glob import glob
import os

import numpy as np
from shapely.geometry import LineString
import pylab as plt
from glob import glob
import os, sys
import matplotlib.font_manager as fm
from PyMyFunc import d2k

def draw_fault_simple(ax, lon_org=None, lat_org=None):
    
    NOR = glob(os.path.join(os.environ["GMT_STUFF"], "Fault", "IranFaults", "NOR", "*.dat"))
    SSL = glob(os.path.join(os.environ["GMT_STUFF"], "Fault", "IranFaults", "SSL", "*.dat"))
    SSR = glob(os.path.join(os.environ["GMT_STUFF"], "Fault", "IranFaults", "SSR", "*.dat"))
    THL = glob(os.path.join(os.environ["GMT_STUFF"], "Fault", "IranFaults", "THL", "*.dat"))
    THR = glob(os.path.join(os.environ["GMT_STUFF"], "Fault", "IranFaults", "THR", "*.dat"))

    for flts in [NOR, SSL, SSR, THL, THR]:

        for flt in flts:

            d = np.loadtxt(flt)
            
            line = LineString(d)
            nflt = np.array([])

            for dis in np.arange(0, line.length, .02):

                p = line.interpolate(dis)
                nflt = np.append(nflt, [p.x, p.y])

            nflt = nflt.reshape((nflt.size//2, 2))
            x = nflt[:,0]
            y = nflt[:,1]

            if lon_org and lat_org: x, y = d2k(x-lon_org), d2k(y-lat_org)
            
            ax.plot(x, y, linestyle="-", lw=1.5, color="k")

def draw_fault_names(ax, lon_org=None, lat_org=None):

    with open(os.path.join(os.environ["GMT_STUFF"], "Fault", "FN.dat")) as f:

        for line in f:

            l = line.split()
            x , y, _, r = [ float(_) for _ in l[:4] ]
            name = " ".join(l[6:])

            if lon_org and lat_org: x, y = d2k(x-lon_org), d2k(y-lat_org)
            ax.text(x, y, name, rotation=r, ha="center", va="center", clip_on=True,
                    fontproperties=fm.FontProperties(family='Times New Roman', size=4, weight='bold'))
            
def draw_border(ax, city, lon_org=None, lat_org=None):
    border = os.path.join(os.environ["GMT_STUFF"], "Ostanha/%s.dat"%(city))
    db = pn.read_csv(border, delim_whitespace=True, names=["LON", "LAT"]) 
    x, y = db.LON.values, db.LAT.values
    if lon_org and lat_org: x, y = d2k(x-lon_org), d2k(y-lat_org)
    ax.plot(x, y, color="k", lw=.7, linestyle="-")

#!/home/saeed/Programs/miniconda3/bin/python

from pyrocko import cake
import numpy as num
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import interp1d as intp
import os, sys
sys.path.append(os.environ["PYT_PRG"])
from initial_mpl import init_plotting_isi
from PyMyFunc import d2k

"""
This script is used for estimating ray density from
event source through predefined layers fetched by
stations on earth surface.

ChangeLog:

Initial: > 15 May 2020

"""

# Make Linear Interpolation of arrays x,y
def get_int(x, y, d=2):

    f = intp(x, y, kind="linear")
    xn = num.arange(min(x), max(x), d)
    if xn.size < len(x):
        xn = num.linspace(min(x), max(x), len(x))
    yn = f(xn)

    return xn, yn

# Convert .prm Velocity Model to .nd File
def prm2nd(vel, r=1.75):

    v = vel[:,0]
    v = num.array([(i,j) for i,j in zip(v,v)]).flatten()
    v = num.append(v,8.1)

    d = vel[:,1]
    d = num.array([(i,j) for i,j in zip(d,d)]).flatten()
    d = num.delete(d,0)
    d = num.append(d,120)
    d = num.append(d,120)

    with open('vel.nd', 'w') as f:

        for i,j in zip(d,v):

            f.write('%7.2f%7.2f%7.2f%7.1f%7.1f%7.1f\n'%(i,j,j/r,2.6,1264,600))
            
# Define Phases to use. example for refracted from 16km > cake.PhaseDef('Pv_16p')
Phases = [cake.PhaseDef('p'), cake.PhaseDef('P'), cake.PhaseDef('S')]
Phases = [cake.PhaseDef('p'), cake.PhaseDef('P')]

# Get User Inputs
deps = input('\n\n+++ Depth sources: [def=5,10]\n\n')
diss = input('+++ Distance ranges; start, end, number: [def=1,200,5 (km,km,#)]\n\n')
max_pen = input('+++ Maximum depth penetration: [def=25 km]\n\n')
outName = "RayDenHist_"+"_".join(diss.split(",")[:2])+".png"

if not deps.strip(): deps = num.array([5., 10.])
else:
    deps = num.array(deps.split(','), dtype=float)

if not diss.strip(): diss = num.linspace(1,200,5)
else:
    diss = num.array(diss.split(','), dtype=float)
    diss = num.linspace(diss[0], diss[1], int(diss[2]))
if not max_pen.strip(): max_pen = 25
else:
    max_pen = float(max_pen)

    
# Load & Convert Velocity Model
if not os.path.exists('hypoel.prm'):

    print('\n\n+++ Velocity model file "hypoel.prm" is missing.\n')
    
vel = num.genfromtxt('hypoel.prm', usecols=(1,2))
r = num.genfromtxt('hypoel.prm', usecols=(3))
prm2nd(vel, r=r[0])

# Define km
km = 1000.

# Load .nd Velocity Model.
model = cake.load_model('vel.nd')

# Source depth [m].
sources_depth = deps * km

# Distances as a numpy array [deg].
distances = diss * km * cake.m2d

# Calculate Distances & Arrivals Then, Plot:
init_plotting_isi(12,8)
plt.rc('font', family='Times New Roman')
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
    
ax = plt.subplot(111)
(i.set_linewidth(0.6) for i in ax.spines.items())
ax.set_xlabel('Ray Density')
ax.set_ylabel('Depth (km)')
ax.invert_yaxis()
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.locator_params(axis = 'x', nbins=5)
ax.locator_params(axis = 'y', nbins=5)

h = num.array([])
for c,source_depth in enumerate(sources_depth):

    for arrival in model.arrivals(distances, phases=Phases, zstart=source_depth):

        phase = arrival.given_phase()
        phase = phase.definition()
        
        z, x, t = arrival.zxt_path_subdivided()
        x, z = get_int(x[0], z[0], d=2)
        h = num.append(h, z/km)

bins = 10
ax.hist(h, bins, orientation='horizontal', rwidth=0.8, color='grey', edgecolor='r')

plt.tight_layout(pad=.3, w_pad=0.01, h_pad=0.01)
plt.savefig(outName, dpi=500)
plt.close()

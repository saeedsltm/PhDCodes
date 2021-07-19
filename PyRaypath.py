#!/home/saeed/Programs/miniconda3/bin/python

from pyrocko import cake
import numpy as num
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from collections import OrderedDict
import os, sys
sys.path.append(os.environ["PYT_PRG"])
from initial_mpl import init_plotting_isi
from PyMyFunc import d2k

"""

Script for make a simple plot of raypaths using hypoel.prm file. The "cake" program
must be installed on your system. (Goto Pyroko pakage).

ChangeLogs:

10-Jun-2018 > Initial.
06-Nov-2018 > Bug fixed for integers and floats.

"""

# Define the phase to use. example for refracted from 16km > cake.PhaseDef('Pv_16p')

Phases = [cake.PhaseDef('p'), cake.PhaseDef('P'), cake.PhaseDef('S')]
Phases = [cake.PhaseDef('p'), cake.PhaseDef('P')]
colors = {'p':'red', 'P':'black', 'S':'cyan'}
widths = {'p':1.0, 'P':1.2, 'S':1.4}
#___________________________________________________________________________________

deps = input('\n\n+++ Depth sources: [def=5,10]\n\n')
diss = input('+++ Distance ranges; start, end, number: [def=1,200,5 (km,km,#)]\n\n')
max_pen = input('+++ Maximum depth penetration: [def=25 km]\n\n')

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

def prm2nd(vel, r=1.73):

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

    
# Load Velocity Model
if not os.path.exists('hypoel.prm'):

    print('\n\n+++ Velocity model file "hypoel.prm" is missing.\n')
    
vel = num.genfromtxt('hypoel.prm', usecols=(1,2))
r = num.genfromtxt('hypoel.prm', usecols=(3))
prm2nd(vel, r=r[0])

km = 1000.

# Load builtin model.
model = cake.load_model('vel.nd')

# Source depth [m].
sources_depth = deps * km

# Distances as a numpy array [deg].
distances = diss * km * cake.m2d

# calculate distances and arrivals and plot them:
init_plotting_isi(17,10)
#plt.rc('text', usetex=True)
plt.rc('font', family='Times New Roman')
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
    
ax = plt.subplot(111)
ax.set_xlabel('Distance (km)')
ax.set_ylabel('Depth (km)')

for c,source_depth in enumerate(sources_depth):

    for arrival in model.arrivals(distances, phases=Phases, zstart=source_depth):

        phase = arrival.given_phase()
        phase = phase.definition()
        
        z, x, t = arrival.zxt_path_subdivided()
        ax.plot(d2k(x[0]), -z[0]/km, color=colors[phase], lw=widths[phase], alpha=.9, label=phase)
        
ax.plot(num.zeros_like(sources_depth),-sources_depth/km, marker='*', mfc='r', mec='w', ms=9, mew=.7, linestyle='')
ax.plot(d2k(distances), num.zeros_like(distances), marker='^', mfc='w', mec='b', ms=7, mew=2, linestyle='', clip_on=False)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)

handles, labels = ax.get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc=4)

v,d=num.meshgrid(vel[:,0],vel[:,1])

X, Z = num.meshgrid(num.arange(-3., num.max(diss)+3., 1.), num.arange(-1, max_pen, 0.1))
speed = num.ones_like(Z)*vel[:,0][0]

for u,z1,z2 in zip(vel[:,0], vel[:,1].tolist(), vel[:,1][1:].tolist() + [max_pen]):

    speed[(Z>=z1)&(Z<z2)] = u

bounds = (-3., num.max(diss)+3., -max_pen, 1)
cmap = plt.cm.get_cmap(plt.cm.viridis_r, vel[:,0].size)

im = ax.imshow(speed, extent=bounds, cmap=cmap)
#ax.set_aspect('auto')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.05)
cb = plt.colorbar(im, cax=cax)
cb.set_label('Velocity (km/s)')
tick_locator = ticker.MaxNLocator(nbins=6)
cb.locator = tick_locator
cb.update_ticks()
cb.ax.invert_yaxis()
bounds = ax.get_xbound()
for i in vel[:,1]: ax.hlines(y=-i, xmin=min(bounds), xmax=max(bounds), linewidth=1, linestyle=':', color='w')
ax.set_ylim(-max_pen, 0)
plt.tight_layout()        
plt.savefig('RayPath.png', dpi=500, quality=100)
plt.close()

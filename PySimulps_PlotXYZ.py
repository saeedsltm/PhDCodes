#!/home/saeed/Programs/miniconda3/bin/python

import numpy as np
import os,sys
import matplotlib.pylab as plt
from initial_mpl import init_plotting_isi
from LatLon import lat_lon as ll

with open('PLOT-ABS/plot-each-layer.thu_abs.sh') as f:

    for l in f:

        if l.startswith('lon1=') : lon1 = float(l.split('=')[1])
        if l.startswith('lon2=') : lon2 = float(l.split('=')[1])
        if l.startswith('lat1=') : lat1 = float(l.split('=')[1])
        if l.startswith('lat2=') : lat2 = float(l.split('=')[1])
        
with open('h71tolatlon.inp','w') as f:

    f.write('h71-3d-loc.out\n')
    f.write('hyp71.xyz\n\n')

os.system('h71tolatlon < h71tolatlon.inp > /dev/null')

sta_lon = []
sta_lat = []

with open(os.path.join('SELECTION','staz.dat')) as f:

    for i,l in enumerate(f):

        if i>1:

            lat = ll.Latitude(degree=float(l[6:8]), minute=float(l[9:14]))
            lon = ll.Longitude(degree=float(l[16:18]), minute=float(l[19:24]))
            sta_lat.append(lat) 
            sta_lon.append(lon) 

ini = np.loadtxt('SELECTION/used.dat')
fin = np.loadtxt('hyp71.xyz')

init_plotting_isi(18,10)

ax = plt.subplot(2,2,1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
x = ini[:,1]
y = ini[:,0]
z = ini[:,2]
ax.scatter(x,y,s=10,marker='o',facecolors='grey', edgecolors='r',zorder=1)
ax.scatter(x[z<1.],y[z<1.],s=10,marker='o',facecolors='black', edgecolors='r',zorder=2)
ax.set_xlim(lon1,lon2)
ax.set_ylim(lat1,lat2)
ax.grid(True, linestyle='--', linewidth=.5, color='k', alpha=.3)

ax = plt.subplot(2,2,2)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
x = fin[:,0]
y = fin[:,1]
z = fin[:,2]
ax.scatter(x,y,s=10,marker='o',facecolors='grey', edgecolors='r',zorder=1)
ax.scatter(x[z<1.],y[z<1.],s=10,marker='o',facecolors='black', edgecolors='r',zorder=2)
ax.set_xlim(lon1,lon2)
ax.set_ylim(lat1,lat2)
ax.grid(True, linestyle='--', linewidth=.5, color='k', alpha=.3)

ax = plt.subplot(2,2,3)
data = -ini[:,2]
binwidth=2
bins=np.arange(min(data), max(data) + binwidth, binwidth)
_,_,p = ax.hist(data, bins=bins, orientation="horizontal", rwidth=0.8, color='grey', edgecolor='r')
p[-1].set_fc('k')
ax.set_ylim(-50,2)
ax.grid(True, linestyle='--', linewidth=.5, color='k', alpha=.3)
ax.set_xlabel('Number of event (#)')
ax.set_ylabel('Depth (km)')

ax = plt.subplot(2,2,4,sharex=ax)
data = -fin[:,2]
binwidth=2
bins=np.arange(min(data), max(data) + binwidth, binwidth)
a,b,p = ax.hist(data, bins=bins, orientation="horizontal", rwidth=0.8, color='grey', edgecolor='r')
pos_dep = -1 - sum([1 for _ in b>0 if _])
for _ in range(pos_dep,0): p[_].set_fc('k')
ax.set_ylim(-50,2)
ax.grid(True, linestyle='--', linewidth=.5, color='k', alpha=.3)
ax.set_xlabel('Number of event (#)')
ax.set_ylabel('Depth (km)')

plt.tight_layout(True)
plt.savefig('Ini_Fin.png', bbox_inches='tight', dpi=300)

os.remove('h71tolatlon.inp')
os.remove('hyp71.xyz')

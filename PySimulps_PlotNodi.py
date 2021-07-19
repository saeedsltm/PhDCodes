#!/home/saeed/Programs/miniconda3/bin/python

from numpy import array, loadtxt, min, max, arange, unique, meshgrid
from LatLon import lat_lon as ll
from PyGetFaults import draw_fault_simple, draw_fault_names, draw_border
import os, sys
from PyMyFunc import d2k
import proplot as plt

"""

Script for plotting Grid/Nodes and Raypath.

outputs:

- PNG file will be saved in "START" directort.

ChangeLogs:

27-Aug-2017 > Initial.
25-Mar-2021 > Improved Figures quality using ProPlot.

"""

#___________________DEFINE REGION BORDER

with open("modthu_v2.inp") as f:
    next(f)
    for l in f:
        lat_org = float(l.split()[0])
        lon_org = float(l.split()[1])
        break

nodi_xy = loadtxt("nodi.xy")
lon_min = d2k(sorted(set(nodi_xy[:,0]))[1] - lon_org)
lon_max = d2k(sorted(set(nodi_xy[:,0]))[-2] - lon_org)
lat_min = d2k(sorted(set(nodi_xy[:,1]))[1] - lat_org)
lat_max = d2k(sorted(set(nodi_xy[:,1]))[-2] - lat_org)
dep_max = float(input("\n+++ Maximum Depth:\n"))

#___________________READ STATION INFORMATION

sta_dic = {}
with open(os.path.join('..','SELECTION','staz.dat')) as f:
    for i ,l in enumerate(f):
        if i>2:
            sta = l[2:6].strip()
            lat = ll.Latitude(degree=float(l[6:8]),minute=float(l[9:14]))
            lon = ll.Longitude(degree=float(l[14:18]),minute=float(l[19:24]))
            sta_dic[sta] = {
                'LAT':d2k(lat.decimal_degree-lat_org),
                'LON':d2k(lon.decimal_degree-lon_org)
                }

#___________________MAKE RAY-PATH GEOMETRY FILE

with open('rays.dat','w') as rays:
    with open(os.path.join('..','SELECTION','travel.dat')) as f:
        for l in f:
            if not l.strip():
                rays.write('#\n')
                evt = []
            elif l.strip() and len(l) >30 and l[20] == 'N' and l[30] == 'E':
                evt_lat = ll.Latitude(degree=float(l[18:20]),minute=float(l[21:26]))
                evt_lat = d2k(evt_lat.decimal_degree-lat_org)
                evt_lon = ll.Longitude(degree=float(l[26:30]),minute=float(l[31:36]))
                evt_lon = d2k(evt_lon.decimal_degree-lon_org)
                evt_dep = float(l[37:43])
            elif l.strip():
                i = 1
                c = 0
                while i < len(l)/14:
                    try:
                        sta  = l[c:c+14][:4].strip()
                        line = '%7.3f %7.3f %7.3f %7.3f\n'%(evt_lon, evt_lat, sta_dic[sta]['LON'], sta_dic[sta]['LAT']) 
                        rays.write(line)
                    except KeyError:
                        pass
                    c+=14
                    i+=1

#___________________EXTRACT DEPTH LAYERS

deps = []                    
with open('mod.thu') as f:
    for l in f:
        deps.append(l.strip())
        if '0  0  0' in l:  break
deps = array(deps[-2].split(),dtype=float)

#___________________READ HYPOCENTRES & GRID POINTS

eqks = loadtxt(os.path.join('..','SELECTION','used.dat'))
eqks_x = d2k(eqks[:,1]-lon_org)
eqks_y = d2k(eqks[:,0]-lat_org)
eqks_z = eqks[:,2]
nods = loadtxt('nodi.xy')
nodx = d2k(unique(nods[:,0])-lon_org)[1:-1]
nody = d2k(unique(nods[:,1])-lat_org)[1:-1]
nodz = deps[1:-1]

#___________________PLOT FIGURE


# Plot and save results
with plt.rc.context(abc=False):
    fig, axs = plt.subplots([[1, 1, 2],
                             [1, 1, 2],
                             [3, 3, 4]],
                            wspace=(0.07, 0.07), hspace=(0.07, 0.07),
                            share=0,
                            wratios=(2, 1, 1), hratios=(2, 1, 1))

axs[1].sharey(axs[0])
axs[2].sharex(axs[0])
axs[1].sharex(axs[3])

##
##_________AXES-1
##
axs[0].set_facecolor("#FFFBD0")
axs[0].set_ylabel('Latitude (km)')
axs[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ndx, ndy = meshgrid(nodx, nody)
axs[0].plot(ndx.flatten(), ndy.flatten(), marker='+', color='k', ms=3, mew=.3, linestyle='', zorder=2, label='Grid Node')
axs[0].scatter(eqks_x, eqks_y, s=5, c='r', lw=.1, edgecolors='k', label='Event', zorder=3)
axs[0].locator_params(axis='x', nbins=5)
axs[0].locator_params(axis='y', nbins=6)

x = []
y = []
with open('rays.dat') as f:
    for l in f:
        if '#' in l:
            axs[0].plot(x, y, color='gray', lw=.1, zorder=1)
            x = []
            y = []
        else:
            [x.append(float(i)) for i in l.split()[0::2]]
            [y.append(float(i)) for i in l.split()[1::2]]
x = []
y = []
for sta in sta_dic.keys():
    x.append(sta_dic[sta]['LON'])
    y.append(sta_dic[sta]['LAT'])

axs[0].plot(x, y, marker='^', mec='b', mfc='w', ms=4, mew=.9, linestyle='', zorder=4, label='Station')
# Add Faults
draw_fault_simple(axs[0], lon_org, lat_org)
draw_fault_names(axs[0], lon_org, lat_org)
# Add Provience Border
draw_border(axs[0], "Bushehr", lon_org, lat_org)
# Add feature
### axs[0].plot(50.962, 36.376, mfc="yellow", mec="k", marker="^", mew=.5, ms=8, zorder=6)
axs[0].set_xlim(lon_min, lon_max)
axs[0].set_ylim(lat_min, lat_max)
axs[0].grid(False)

##
##_________AXES-2
##
axs[2].set_facecolor("#FFFBD0")
ndx, ndy = meshgrid(nodx, nodz)
axs[2].set_xlabel('Longitude (km)')
axs[2].set_ylabel('Depth (km)')
axs[2].set_ylim(0, dep_max)
axs[2].plot(ndx.flatten(), ndy.flatten(), marker='+', color='k', ms=3, mew=.3, linestyle='')
axs[2].scatter(eqks_x, eqks_z, s=5, c='r', lw=.1 , edgecolors='k')
axs[2].invert_yaxis()
axs[2].grid(False)

##
##_________AXES-3
##
axs[1].set_facecolor("#FFFBD0")
axs[1].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ndx, ndy = meshgrid(nodz, nody)
axs[1].yaxis.tick_right()
axs[1].set_xlim(0, dep_max)
axs[1].yaxis.set_label_position("right")
axs[1].plot(ndx.flatten(), ndy.flatten(), marker='+', color='k', ms=3, mew=.3, linestyle='')
axs[1].scatter(eqks_z, eqks_y, s=5, c='r', lw=.1 , edgecolors='k')
axs[1].grid(False)

##
##_________AXES-4
##
axs[3].set_facecolor("#FFFBD0")
axs[3].tick_params(axis="both")
axs[3].xaxis.tick_bottom()
axs[3].yaxis.tick_right()
axs[3].yaxis.set_label_position("right")
axs[3].set_xlabel('Depth (km)')
axs[3].set_ylabel('Events (#)')
axs[3].set_xlim(0, dep_max)
binwidth=2
bins=arange(min(eqks_z), max(eqks_z) + binwidth, binwidth)
axs[3].hist(eqks_z, bins=bins, rwidth=0.8, color='grey', edgecolor='r')
axs[3].invert_xaxis()
axs[3].grid(ls=":")

##
##___________________SAVE FIGURE
##
fig.save("DataRayPath.png", transparent=False)
plt.close()

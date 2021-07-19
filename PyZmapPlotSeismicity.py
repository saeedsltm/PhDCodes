#!/home/saeed/Programs/miniconda3/bin/python

from numpy import genfromtxt, linspace
import matplotlib.pyplot as plt
import pySW4 as sw4
import os, sys
from pycpt.load import cmap_from_cptcity_url
sys.path.append(os.environ['PYT_PRG'])
from initial_mpl import init_plotting_isi

zmap_inp = raw_input('\n\n+++ Input file name with ZMAP format:\n\n')
lon_min  = input('\n\n+++ Enter Longitude-Min:\n\n')
lon_max  = input('\n\n+++ Enter Longitude-Max:\n\n')
lat_min  = input('\n\n+++ Enter Latitude-Min:\n\n')
lat_max  = input('\n\n+++ Enter Latitude-Max:\n\n')

#___________________READ TEXT FILE IN GMT PSTEXT INPUT

def read_iran_cities(file_in):

    lon = []
    lat = []
    nam = []

    with open(file_in) as f:

        for line in f:

            l = line.split()

            lon.append(float(l[0]))
            lat.append(float(l[1]))
            nam.append(' '.join(l[6:]))

    return lon, lat, nam
           
#___________________DEFINE INPUTS FOR TIFF, PROVIENCE, CITIES

iran_tif = os.path.join(os.environ['GMTHOME'],'grd','IRN.tif')
iran_cit = os.path.join(os.environ['GMTHOME'],'grd','IRN_cities.dat')
iran_prov = os.path.join(os.environ['GMTHOME'],'grd','IRN_prov.dat')

#___________________READ TIFF DATA

topo = sw4.utils.geo.read_GeoTIFF(iran_tif)
topo.keep(lon_min,lon_max,lat_min,lat_max)

cmap = cmap_from_cptcity_url(u'mby/mby.cpt')

# hillshade parameters
definition = 0.5
contrast = 1.1

# cmap and labels
cmap = cmap_from_cptcity_url(u'mby/mby.cpt')

# stretch the cmap to the desired colors
cmax = topo.elev.max() * 1.5
cmin = -cmax * 1.58
norm = plt.Normalize(cmin, cmax)

# set the plotting vmin and vmax
vmax = topo.elev.max()
vmin = 0
cmap = sw4.utils.trim_cmap(cmap, norm(vmin), norm(vmax))

cb_label = 'Elevation (m)'

init_plotting_isi(10,10)
ax = plt.subplot(1, 1, 1)
plt.rcParams['axes.labelsize']  = 6
[_.set_linewidth(0.6) for _ in ax.spines.itervalues()]

# Overlay Hillshading
axsw4 = sw4.plotting.hillshade_plot(topo.elev, extent=topo.extent, cmap=cmap, vmin=vmin, vmax=vmax,
                                    blend_mode='soft', contrast=contrast, definition=definition, ax=ax,
                                    colorbar=cb_label)
axsw4.ax.tick_params(labelsize=5)


cat = genfromtxt(zmap_inp)

#___________________DEFINE MAGNITUDES

m1 = (cat[:,5]>=2.5)&(cat[:,5]<3.5)
m2 = (cat[:,5]>=3.5)&(cat[:,5]<4.5)
m3 = (cat[:,5]>=4.5)&(cat[:,5]<5.5)
m4 = (cat[:,5]>=5.5)&(cat[:,5]<6.5)
m5 = (cat[:,5]>=6.5)

ax.plot(cat[:,0][m1], cat[:,1][m1], ls='', marker='o', ms=3, mew=.3, mec='w', mfc='r', alpha=.8, label='2.5<=M<=3.5')
ax.plot(cat[:,0][m2], cat[:,1][m2], ls='', marker='o', ms=5, mew=.3, mec='w', mfc='r', alpha=.8, label='3.5<=M<=4.5')
ax.plot(cat[:,0][m3], cat[:,1][m3], ls='', marker='o', ms=7, mew=.3, mec='w', mfc='r', alpha=.8, label='4.5<=M<=5.5')
ax.plot(cat[:,0][m4], cat[:,1][m4], ls='', marker='o', ms=9, mew=.3, mec='w', mfc='r', alpha=.8, label='5.5<=M<=6.5')
ax.plot(cat[:,0][m5], cat[:,1][m5], ls='', marker='o', ms=11,mew=.3, mec='w', mfc='r', alpha=.8, label='M>=6.5')

#___________________PLOT CITIES

for i,j in zip([iran_cit, iran_prov],[1,1.2]):
    
    lon, lat, nam = read_iran_cities(i)

    for x,y,s in zip(lon,lat,nam):
        ax.annotate(s, xy=(x, y), xycoords='data', xytext=(2.5, 2.5), textcoords='offset points', fontsize=6*j)
        ax.plot(x,y, ls='', marker='s', ms=3*j, mew=.8, mec='k', mfc='w')

ax.text(0.7, 1.015, '@Earthquake_Seismology', transform=ax.transAxes, fontsize=6, alpha=.5)

ax.axis(topo.extent)

[tick.label.set_fontsize(6) for tick in ax.xaxis.get_major_ticks()]
[tick.label.set_fontsize(6) for tick in ax.yaxis.get_major_ticks()]


ax.legend(loc=3, fontsize=5)

#___________________SAVE

plt.tight_layout()
plt.savefig('seismicity.tiff')

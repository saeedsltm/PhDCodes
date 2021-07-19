#!/home/saeed/Programs/miniconda3/bin/python

from numpy import array,deg2rad, sin, cos, float, isclose
from scipy.interpolate import griddata
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from initial_mpl import init_plotting_isi
import numpy as np
from glob import glob
import os
from LatLon import lat_lon as ll
from PyMyFunc import d2k, k2d
import sys
from scipy.ndimage import zoom

"""

Plot Simulps velocity results in Cross-Section.

input files: 

    lay-??.xyz, ris-??.xyz, prt-??.xyz 

outputs:


ChangeLogs:

14-Mar-2019 > Initial.


"""

def rotate_around_point(x, y, radians, origin=(0, 0)):
    
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = cos(radians)
    sin_rad = sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy


def f(x,y,z):

    return x+y+z

def str_dip_nez(strike, dip):
    
    """
    Convert Strike and Dip to a normal vector of (n,e,z).
    
    """

    strike = deg2rad(strike)
    dip = deg2rad(dip)
    
    n = -sin(dip)*sin(strike)
    e = sin(dip)*cos(strike)
    z = -cos(dip)

    return np.array([n,e,z])

def load_lay_file(folder_name, mode):

        
    xg = np.array([])
    yg = np.array([])
    zg = np.array([])
    vg = np.array([])

    with open('inversion.out') as f:

       for l in f:

           if "origin :" in l:

               origin = f.next()
               origin = origin.split()
               lat = ll.Latitude(degree=float(origin[0]), minute=float(origin[1])).decimal_degree
               lon = ll.Longitude(degree=float(origin[2]), minute=float(origin[3])).decimal_degree

           if "xgrid" in l:

               longs = f.next()
               longs = np.array(longs.split()[1:-1], dtype=float)
               nx = longs.size

           if "ygrid" in l:

               lats = f.next()
               lats = np.array(lats.split()[1:-1], dtype=float)
               ny = lats.size
               
           if "zgrid" in l:

               depths = f.next()
               depths = np.array(depths.split()[1:-1], dtype=float)
               nz = depths.size

    lays = sorted(glob(os.path.join(folder_name, "%s*.xyz"%(mode))))

    for lay, depth in zip(lays, depths):

        cmd = "awk '{print $1,$2,$3,$4,$5}' %s > tmp"%(lay)
        os.system(cmd)
        model = np.loadtxt("tmp")
        x, y, v = model[:,3], model[:,4], model[:,2]
        z = np.ones_like(x) * depth

        xg = np.append(xg, x)
        yg = np.append(yg, y)
        zg = np.append(zg, z)
        vg = np.append(vg, v)

    xg = xg.reshape((nz,ny,nx)).transpose()
    yg = yg.reshape((nz,ny,nx)).transpose()
    zg = zg.reshape((nz,ny,nx)).transpose()
    vg = vg.reshape((nz,ny,nx)).transpose()
    
    return lon, lat, xg, yg, zg, vg
       
###################

H_flag = True
V_flag = False
mode = 'spr' # what do you want to plot? lay (vp, vpvs), ris (resolution matrix), spr (spread function)
cont_lev = 0.5

# load velocity data
lon, lat, xg, yg, zg, vg = load_lay_file(folder_name="vp-spr", mode=mode)

xnodes = np.sort(list(set(xg.flatten())))
ynodes = np.sort(list(set(yg.flatten())))
znodes = np.sort(list(set(zg.flatten())))

di = RegularGridInterpolator((xnodes, ynodes, znodes), vg, method="linear")

########### cross-section


if H_flag:

    depth = 10
    strike = 0
    xl = np.linspace(-210, 210, 15)
    yl = np.linspace(-120, 120, 9)
    #xl = np.arange(-210, 210, 30)
    #yl = np.arange(-120, 120, 30)
    zl = np.arange(0, 35, 5)

    Xl, Yl = np.meshgrid(xl, yl)
    Xl, Yl = rotate_around_point(Xl, Yl, radians=deg2rad(strike), origin=(0, 0))
    Zl = np.ones_like(Xl)*depth

    shape = yl.size, xl.size
    extent = [Xl.min(), Xl.max(), Yl.min(), Yl.max()]

if V_flag:

    cross_start_pnt = 51, 35.0 # start point of cross section
    cross_grid_pnts = 20 # number of grid points along cross section
    cross_len, cross_strike = 200, 45 # length and azimuth of cross section
    cross_depth = 0, 35, 5 # cross section  depth range and increment

    #cross_strike*=-1
    dx = d2k(cross_start_pnt[0] - lon)
    dy = d2k(cross_start_pnt[1] - lat)
    r = np.linspace(0, cross_len, cross_grid_pnts)
    xl = r*sin(deg2rad(cross_strike)) + dx
    yl = r*cos(deg2rad(cross_strike)) + dy
    zl = np.arange(cross_depth[0], cross_depth[1], cross_depth[2])

    Xl = np.ones((zl.size, xl.size))
    Yl = np.ones((zl.size, yl.size))
    Zl = np.ones((zl.size, xl.size))

    Xl*=xl
    Yl*=yl
    Zl*=zl.reshape(zl.size, 1)

    shape = zl.size, xl.size
    extent = [Xl.min(), Xl.max(), -Zl.max(), -Zl.min()]

# Plot Media
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
ax.plot(Xl.flatten(), Yl.flatten(), -Zl.flatten(), 'go ')
ax.scatter(xg.flatten(),yg.flatten(),-zg.flatten(),c=vg.flatten(), cmap='jet_r')

#ax.view_init(0, 22)
plt.show()


# Plot Cross-Section

ax=plt.subplot(111)

X, Y, Z = Xl.flatten(), Yl.flatten(), Zl.flatten()
p = np.array([X,Y,Z]).T
p = di(p)

im=ax.imshow(p.reshape(shape), interpolation='gaussian',
             origin='upper', cmap='jet_r', extent=extent)

Z = p.reshape(shape)
Z = zoom(Z, 5)
levels = np.arange(Z.min(), Z.max(), cont_lev)
contours = plt.contour(Z, levels, origin='upper', linewidths=.7, colors='black', extent=extent)
plt.clabel(contours, inline=True, fontsize=6)

plt.colorbar(im)

plt.tight_layout()
plt.show()


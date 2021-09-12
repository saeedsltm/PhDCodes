#!/home/saeed/Programs/miniconda3/bin/python

import numpy as np
import pylab as plt
import numpy.ma as ma
import sys
import warnings
warnings.filterwarnings("ignore")

"run: PyAdjustFM.py Aa_File xmin xmax ymin ymax nx ny"

inp = np.loadtxt(sys.argv[1])
if inp.ndim == 1: inp = inp.reshape(1, inp.size)

if not inp.size:

    np.savetxt("Adjusted_FM.dat", [])
    sys.exit(0)

#inp = np.delete(inp, [6, 7, 8, 10], 1)

xmin , xmax = float(sys.argv[2]), float(sys.argv[3])
ymin , ymax = float(sys.argv[4]), float(sys.argv[5])

nx , ny = int(sys.argv[6]), int(sys.argv[7])

#xgrd = np.linspace(xmin, xmax, nx)
xgrd = np.array([xmin+18, xmax-10])
ygrd = np.linspace(ymin, ymax, ny)

X, Y = np.meshgrid(xgrd, ygrd)
x_ind, y_ind = np.indices(X.shape)

D = []
xp = inp[:,0]
yp = inp[:,1]

for x,y in zip(xp, yp):

    diff = np.sqrt((x-X)**2 + (y-Y)**2)
    ind = np.nanargmin(diff)
    ind_x = x_ind.flatten()[ind]
    ind_y = y_ind.flatten()[ind]

    D.append(diff[ind_x][ind_y])

ind = np.lexsort((D,D))    

inp = np.array([inp[i] for i in ind])
xp = inp[:,0]
yp = inp[:,1]

xn = []
yn = []

for x,y in zip(xp, yp):

    diff = np.sqrt((x-X)**2 + (y-Y)**2)
    ind = np.nanargmin(diff)
    ind_x = x_ind.flatten()[ind]
    ind_y = y_ind.flatten()[ind]

    D.append(diff[ind_x][ind_y])

    xn.append(X[ind_x][ind_y])
    yn.append(Y[ind_x][ind_y])
    
    X[ind_x][ind_y] = np.nan
    Y[ind_x][ind_y] = np.nan    

##ax = plt.subplot(211)
##ax.set_xlim(xmin, xmax)
##ax.set_ylim(ymin, ymax)
##
##ax.plot(xp, yp, "ro")
##
##ax = plt.subplot(212)
##ax.set_xlim(xmin, xmax)
##ax.set_ylim(ymin, ymax)
##
##
##ax.plot(xn, yn, "bo")
##ax.plot([xp,xn], [yp,yn], "g-")
##
##plt.show()

if inp[0].size == 15:

    inp[:,11] = xn
    inp[:,12] = yn

    np.savetxt("Adjusted_FM.dat", inp, fmt="%6.3f %6.3f %4.1f %3d %2d %4d %3d %2d %4d %3.1f %2d %6.3f %6.3f %3d %3d")

if inp[0].size == 10:

    inp[:,7] = xn
    inp[:,8] = yn

    np.savetxt("Adjusted_FM.dat", inp, fmt="%6.3f %6.3f %4.1f %3d %2d %4d %3.1f %6.3f %6.3f %3d  %3d")

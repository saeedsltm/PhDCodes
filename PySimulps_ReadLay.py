#!/home/saeed/Programs/miniconda3/bin/python

import numpy as np
import sys

inp = sys.argv[1]
d = np.loadtxt(inp)

xmin = d[:,0].min()
xmax = d[:,0].max()
ymin = d[:,1].min()
ymax = d[:,1].max()

dx = np.unique(np.diff(d[:,0]))[1]
dy = abs(np.unique(np.diff(d[:,1]))[-2])

nx = np.unique(d[:,0]).size
ny = np.unique(d[:,1]).size

print(xmin, xmax, ymin, ymax, "%.4f"%dx, "%.4f"%dy, nx, ny)

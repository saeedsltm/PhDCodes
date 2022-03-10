#!/home/saeed/Programs/miniconda3/bin/python
import numpy as np
import sys, os
from glob import glob
from PyGetFaults import draw_fault_simple, draw_border
from pathlib import Path
import proplot as plt

"""

Script for plotting model Covariance.

outputs:

- Figures will be saved in "PLOT/COV".

ChangeLogs:

10-Mar-2022 > Initial.

"""

# PLOT COV

# Create directory for saving plots
Path(os.path.join("PLOT", "COV")).mkdir(parents=True, exist_ok=True)

vp_cov_files = sorted(glob(os.path.join("COVARIANZA", "vp", "cov-*.xyz")))
vs_cov_files = sorted(glob(os.path.join("COVARIANZA", "vpvs", "cov-*.xyz")))

# Read nx,ny grind number
def get_nx_ny():
    with open(os.path.join("START", "mod.thu")) as f:
        tmp = []
        for i,l in enumerate(f):
            tmp.append(l.strip())
            if i==0: nx = int(l.split()[1])
            if i==0: ny = int(l.split()[2])
            if "  0  0  0" in l:  return nx-2, ny-2, [float(_) for _ in tmp[-2].split()][1:-1]

nx, ny, dp = get_nx_ny()
c = 0
for vp_cov_file, vs_cov_file in zip(vp_cov_files, vs_cov_files):

    print("Working on Depth=%d"%(dp[c]))

    vp_cov = np.loadtxt(vp_cov_file)
    vs_cov = np.loadtxt(vs_cov_file)
    
    X = vp_cov[:,0][::-1].reshape(ny, nx)
    Y = vp_cov[:,1][::-1].reshape(ny, nx)
    X = np.flip(X)
    Y = np.flip(Y)

    cov_vp = vp_cov[:,2].reshape(ny, nx)
    cov_vs = vs_cov[:,2].reshape(ny, nx)

    # Plot and save results
    with plt.rc.context(abc="a)"):
        fig, axs = plt.subplots(ncols=2, share=0)
    axs.format(xlabel='Longitude',
               ylabel='Latitude')
    colorbar_kw = {"length":"8em",
                   "labelsize":6,
                   "ticklabelsize":5,
                   "labelweight":"bold"}
    
    # Vp
    axs[0].format(title=r"$V_p$", lrtitle="Depth=%d"%(dp[c]))
    vmin = np.where(cov_vp==-1.00e+03, 0, cov_vp).min()
    vmax = np.where(cov_vp==-1.00e+03, 0, cov_vp).max()
    pc = axs[0].pcolormesh(X, Y, cov_vp[:-1, :-1], cmap="jet_r", vmin=vmin, vmax=vmax, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[0].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[0].set_xlim(X.min(), X.max()) 
    axs[0].set_ylim(Y.min(), Y.max()) 

    # Vp/Vs
    axs[1].format(title=r"$V_p/V_s$", lrtitle="Depth=%d"%(dp[c]))
    vmin = np.where(cov_vs==-1.00e+03, 0, cov_vs).min()
    vmax = np.where(cov_vs==-1.00e+03, 0, cov_vs).max()    
    pc = axs[1].pcolormesh(X, Y, cov_vs[:-1, :-1], cmap="jet_r", vmin=vmin, vmax=vmax, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[1].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[1].set_xlim(X.min(), X.max()) 
    axs[1].set_ylim(Y.min(), Y.max()) 
    
    # Saveing
    out_name = os.path.join("PLOT", "COV", "COV_%d.png"%(dp[c]))
    fig.save(out_name, transparent=False)
    plt.close()

    c+=1

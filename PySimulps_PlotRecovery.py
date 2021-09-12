#!/home/saeed/Programs/miniconda3/bin/python

import pylab as plt
import numpy as np
import sys, os, re
from glob import glob
from pathlib import Path
import proplot as plt

# Create directory for saving plots
Path(os.path.join("PLOT", "RECOVER")).mkdir(parents=True, exist_ok=True)

vp_pert_files_ini = sorted(glob(os.path.join("..", "CREA-SYNTH-MOD", "OUTDIR", "vp-pert", "lay-*.xyz")))
vp_pert_files_fin = sorted(glob(os.path.join("OUTDIR", "vp-pert", "lay-*.xyz")))
vs_pert_files_ini = sorted(glob(os.path.join("..", "CREA-SYNTH-MOD", "OUTDIR", "vpvs-pert", "lay-*.xyz")))
vs_pert_files_fin = sorted(glob(os.path.join("OUTDIR", "vpvs-pert", "lay-*.xyz")))

def get_xyz_deps():    
    deps = []
    with open("model.out") as f:
        for i,l in enumerate(f):
            if i==0: x,y,z = [int(v) for v in l.split()[1:4]]
            deps.append(l)
            if "  0  0  0" in l: break
    dep = deps[-2]
    it = len(dep.strip())//6
    deps = []
    c = 0
    for i in range(it):
        deps.append(float(dep[c:c+6]))
        c+=6
    return x-2,y-2,deps[1:-1]

nx, ny, dp = get_xyz_deps()
c = 0
for vp_pert_ini, vs_pert_ini, vp_pert_fin, vs_pert_fin in zip(vp_pert_files_ini, vs_pert_files_ini, vp_pert_files_fin, vs_pert_files_fin):
    print("Depth=%d"%(dp[c]))
    vp_pert_ini = np.loadtxt(vp_pert_ini)
    vp_pert_fin = np.loadtxt(vp_pert_fin)
    vs_pert_ini = np.loadtxt(vs_pert_ini)
    vs_pert_fin = np.loadtxt(vs_pert_fin)
    X = vp_pert_ini[:,0].reshape(ny, nx)
    Y = vp_pert_ini[:,1].reshape(ny, nx)
    rec_vp = vp_pert_fin[:,2].reshape(ny, nx) / vp_pert_ini[:,2].reshape(ny, nx) * 100
    rec_vs = vs_pert_fin[:,2].reshape(ny, nx) / vs_pert_ini[:,2].reshape(ny, nx) * 100

    # Plot and save results
    with plt.rc.context(abc=True, abcstyle="a)"):
        fig, axs = plt.subplots(ncols=2, share=0)
    axs.format(xlabel='Longitude',
               ylabel='Latitude')
    colorbar_kw = {"length":"8em",
                   "labelsize":6,
                   "ticklabelsize":5,
                   "labelweight":"bold"}

    # Vp
    axs[0].format(title=r"$V_p$", lrtitle="Depth=%d"%(dp[c]))
    pc = axs[0].pcolormesh(X, Y, rec_vp[:-1, :-1], cmap="jet_r", vmin=0, vmax=100, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[0].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[0].set_xlim(X.min(), X.max()) 
    axs[0].set_ylim(Y.min(), Y.max()) 

    # Vp/Vs
    axs[1].format(title=r"$V_p/V_s$", lrtitle="Depth=%d"%(dp[c]))
    pc = axs[1].pcolormesh(X, Y, rec_vs[:-1, :-1], cmap="jet_r", vmin=0, vmax=100, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[1].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[1].set_xlim(X.min(), X.max()) 
    axs[1].set_ylim(Y.min(), Y.max()) 
    
    # Saveing
    out_name = os.path.join("PLOT", "RECOVER", "REC_%d.png"%(dp[c]))
    fig.save(out_name, transparent=False)
    plt.close()

    c+=1

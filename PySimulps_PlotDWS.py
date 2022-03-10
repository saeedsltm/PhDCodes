#!/home/saeed/Programs/miniconda3/bin/python
import numpy as np
import sys, os
from glob import glob
from PyGetFaults import draw_fault_simple, draw_border
from pathlib import Path
import proplot as plt

"""

Script for plotting DWS and Spread function.

outputs:

- DWS files extraced from "inversion.out" will be saved in "DWS".
- Figures will be saved in "PLOT/DWS".

ChangeLogs:

27-Aug-2017 > Initial.
25-Mar-2021 > Improved Figures quality using ProPlot.

"""

# PLOT DWS

# Create directory for saving plots
Path(os.path.join("PLOT", "DWS")).mkdir(parents=True, exist_ok=True)

vp_dws_files = sorted(glob(os.path.join("DWS", "vp", "dws-*.xyz")))
vs_dws_files = sorted(glob(os.path.join("DWS", "vpvs", "dws-*.xyz")))
vp_spr_files = sorted(glob(os.path.join("RISOLUZIONE", "vp", "spr-*.xyz")))
vs_spr_files = sorted(glob(os.path.join("RISOLUZIONE", "vpvs", "spr-*.xyz")))

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
for vp_dws_file, vs_dws_file in zip(vp_dws_files, vs_dws_files):

    print("Working on Depth=%d"%(dp[c]))

    vp_dws = np.loadtxt(vp_dws_file)
    vs_dws = np.loadtxt(vs_dws_file)
    
    X = vp_dws[:,0][::-1].reshape(ny, nx)
    Y = vp_dws[:,1][::-1].reshape(ny, nx)
    X = np.flip(X)
    Y = np.flip(Y)

    dws_vp = vp_dws[:,2].reshape(ny, nx)
    dws_vs = vs_dws[:,2].reshape(ny, nx)

    # Plot and save results
    with plt.rc.context(abc="a)"):
        fig, axs = plt.subplots(ncols=2, share=0)
    axs.format(xlabel='Longitude',
               ylabel='Latitude')
    colorbar_kw = {"length":"8em",
                   "labelsize":6,
                   "ticklabelsize":5,
                   "labelweight":"bold",
                   "formatter":plt.constructor.Formatter("sci")}
    
    # Vp
    axs[0].format(title=r"$V_p$", lrtitle="Depth=%d"%(dp[c]))
    pc = axs[0].pcolormesh(X, Y, dws_vp[:-1, :-1], cmap="jet_r", vmin=dws_vp.min(), vmax=dws_vp.max(), colorbar="ll", colorbar_kw=colorbar_kw)
    axs[0].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[0].set_xlim(X.min(), X.max()) 
    axs[0].set_ylim(Y.min(), Y.max()) 

    # Vp/Vs
    axs[1].format(title=r"$V_p/V_s$", lrtitle="Depth=%d"%(dp[c]))
    pc = axs[1].pcolormesh(X, Y, dws_vs[:-1, :-1], cmap="jet_r", vmin=dws_vp.min(), vmax=dws_vp.max(), colorbar="ll", colorbar_kw=colorbar_kw)
    axs[1].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[1].set_xlim(X.min(), X.max()) 
    axs[1].set_ylim(Y.min(), Y.max()) 
    
    # Saveing
    out_name = os.path.join("PLOT", "DWS", "DWS_%d.png"%(dp[c]))
    fig.save(out_name, transparent=False)
    plt.close()

    c+=1

# PLOT SpreadFunction

# Plot and save results
with plt.rc.context(abc=True, abcstyle="a)"):
    fig, axs = plt.subplots(ncols=2, share=0)
axs.format(xlabel="Spread",
           ylabel="DWS",
           yformatter="sci")

axs[0].format(title=r"$V_p$")
axs[1].format(title=r"$V_p/V_s$")

print("Plotting Spread function")

for vp_dws_file, vs_dws_file, vp_spr_file, vs_spr_file in zip(vp_dws_files, vs_dws_files, vp_spr_files, vs_spr_files):

    vp_dws = np.loadtxt(vp_dws_file)
    vs_dws = np.loadtxt(vs_dws_file)
    vp_spr = np.loadtxt(vp_spr_file)
    vs_spr = np.loadtxt(vs_spr_file)

    dws_vp = vp_dws[:,2]
    dws_vs = vs_dws[:,2]
    spr_vp = vp_spr[:,2]
    spr_vs = vs_spr[:,2]
    
    axs[0].scatter(spr_vp, dws_vp, s=.2, c="k", marker="o")
    axs[0].set_ylim(bottom=0)
    axs[0].grid(linestyle=":")
    axs[1].scatter(spr_vs, dws_vs, s=.2, c="k", marker="o")
    axs[1].set_ylim(bottom=0)
    axs[1].grid(linestyle=":")
    
out_name = os.path.join("PLOT", "DWS", "SPR-DWS.png")
fig.save(out_name, transparent=False)
plt.close()    

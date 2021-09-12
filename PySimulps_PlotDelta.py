#!/home/saeed/Programs/miniconda3/bin/python

import numpy as np
import sys, os
from glob import glob
from PyGetFaults import draw_fault_simple, draw_fault_names, draw_border
from pathlib import Path
import proplot as plt

"""

Script for plotting Velocity Changes.

outputs:

- Figures will be saved in "PLOT/DELTA".

ChangeLogs:

27-Aug-2017 > Initial.
25-Mar-2021 > Improved Figures quality using ProPlot.

"""

# Create directory for saving plots
Path(os.path.join("PLOT", "DELTA")).mkdir(parents=True, exist_ok=True)

# Get input from user
if len(sys.argv) < 2:
    iter_n = 1
    print('\n+++ No iteration number was defined as an input argument. Delta-plots for the %dth iterarion.\n'%(iter_n))
else:
    iter_n = int(sys.argv[1])
    if iter_n == 0:
        print('\n+++ Total Delta-plots for the whole iterarions.\n')
    else:
        print('\n+++ Delta-plots for the %dth iterarion.\n'%(iter_n))

# Flag reverser
def flag_rev(flag):
    if flag: return False
    else: return True

# Get maximum deviation for Vp and VpVs
def get_MinMaxDev():
    with open("control-par") as f:
        for i,l in enumerate(f):
            if i == 2:
                dev_vp = float(l.split()[1])
                dev_vs = float(l.split()[2])
    return dev_vp, dev_vs
                
# Get Delta for Vp and VpVs from "inversion.out" file
def get_dvp_dvs(iter_n):
    with open(os.path.join("inversion.out")) as f:
        flag_1 = False
        flag_2 = False
        flag_3 = False
        flag_4 = False
        flag_v = False
        hint_1_str = 'iteration step  %1d; simultaneous inversion'%(iter_n)
        hint_1_stp = 'iteration step  %1d; hypocenter adjustments'%(iter_n)
        hint_2_str = 'velocity model changes'
        hint_2_stp = 'corrected velocity model'
        hint_3_str = 'P-Vel nodes'
        hint_4_str = 'Vp/Vs nodes'
        dv_vp   = [[]]
        dv_vpvs = [[]]
        dep     = []
        for l in f:
            if 'bld =' in l:
                nx = int(l.split()[5])
                ny = int(l.split()[8])
            if 'dvpmx  dvpvsmx' in l:
                line = next(f).split()
                dv_vp_max = float(line[0])
                dv_vpvs_max = float(line[1])
            if hint_1_str in l:
                flag_1 = True
            if hint_1_stp in l:
                flag_1 = False
            if flag_1 and hint_2_str in l:
                flag_2 = True
                flag_v = flag_rev(flag_v)            
            if flag_1 and hint_2_stp in l:
                flag_2 = False
            if flag_1 and flag_2 and hint_3_str in l:
                flag_3 = True
                dep.append(int(float(l.split()[-1])))
            if flag_3 and not l.strip():
                flag_3 = False
            if flag_3:
                if hint_3_str not in l:
                    for i in l.split(): dv_vp[-1].append(float(i))
                if hint_3_str in l:
                    dv_vp.append([])
            if flag_1 and flag_2 and hint_4_str in l:
                flag_4 = True
            if flag_4 and not l.strip():
                flag_4 = False
            if flag_4:
                if hint_4_str not in l:
                    for i in l.split(): dv_vpvs[-1].append(float(i))
                if hint_4_str in l:
                    dv_vpvs.append([])
    dv_vp.pop(0)
    dv_vpvs.pop(0)

    return dv_vp, dv_vpvs

# Read final Delta forVp and VpVs
vp_pert_files = sorted(glob(os.path.join("OUTDIR", "vp-delta", "lay-*.xyz")))
vs_pert_files = sorted(glob(os.path.join("OUTDIR", "vpvs-delta", "lay-*.xyz")))

if iter_n: dv_vp, dv_vpvs = get_dvp_dvs(iter_n)

# Read nx,ny grind number
def get_nx_ny():
    dp = []
    with open("inversion.out") as f:
        for l in f:
            if "velocity grid size:" in l:
                l = next(f)
                ll = l.split()
                nx, ny, nz = int(ll[5]), int(ll[8]), int(ll[11])
            if "zgrid" in l:
                l = next(f)
                while l.strip():
                    [dp.append(float(_)) for _ in l.split()]
                    l = next(f)
    dp = dp[1:-1]
    return nx-2, ny-2, dp

nx, ny, dp = get_nx_ny()
vpMax, vsMax = get_MinMaxDev()
c = 0
for vp_pert, vs_pert in zip(vp_pert_files, vs_pert_files):
    print("Working on Depth=%d"%(dp[c]))
    vp_pert = np.loadtxt(vp_pert)
    vs_pert = np.loadtxt(vs_pert)   
    X = vp_pert[:,0].reshape(ny,nx)
    Y = vp_pert[:,1].reshape(ny,nx)
    if iter_n == 0:
        delta_vp = vp_pert[:,2].reshape(ny,nx)
        delta_vs = vs_pert[:,2].reshape(ny,nx)
    else:
        delta_vp = np.array(dv_vp[c]).reshape(ny+2,nx+2)
        delta_vp = delta_vp[1:-1, 1:-1]
        delta_vs = np.array(dv_vpvs[c]).reshape(ny+2,nx+2)
        delta_vs = delta_vs[1:-1, 1:-1]   
    # Plot and save results
    with plt.rc.context(abc=True, abcstyle="a)"):
        fig, axs = plt.subplots(ncols=2, share=0)
    axs.format(xlabel='Longitude',
               ylabel='Latitude')
    colorbar_kw = {"length":"8em",
                   "width":"1em",
                   "labelsize":6,
                   "ticklabelsize":5,
                   "labelweight":"bold"}
    # Vp
    axs[0].format(title=r"$V_p$", lrtitle="Depth=%d"%(dp[c]))
    vMax = vpMax
    pc = axs[0].pcolormesh(X, Y, delta_vp[:-1, :-1], cmap="jet_r", vmin=-vMax, vmax=vMax, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[0].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[0].set_xlim(X.min(), X.max()) 
    axs[0].set_ylim(Y.min(), Y.max())
    # Vp/Vs
    axs[1].format(title=r"$V_p/V_s$", lrtitle="Depth=%d"%(dp[c]))
    vMax = vsMax
    pc = axs[1].pcolormesh(X, Y, delta_vs[:-1, :-1], cmap="jet_r", vmin=-vMax, vmax=vMax, colorbar="ll", colorbar_kw=colorbar_kw)
    axs[1].scatter(X, Y, s=10, lw=.5, c="k", marker="+")
    axs[1].set_xlim(X.min(), X.max()) 
    axs[1].set_ylim(Y.min(), Y.max()) 
    # Saveing
    out_name = os.path.join("PLOT", "DELTA", "DELTA_%d.png"%(dp[c]))
    fig.save(out_name, transparent=False)
    plt.close()

    c+=1

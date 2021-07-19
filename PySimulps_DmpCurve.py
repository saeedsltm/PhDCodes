#!/home/saeed/Programs/miniconda3/bin/python

import proplot as plt
from glob import glob
from pandas import read_csv

"""

Script for plotting Damping L-Curve.

outputs:

- Figures will be saved in "DAMPING-TEST-DIEHL".

ChangeLogs:

27-Aug-2017 > Initial.
25-Mar-2021 > Improved Figures quality using ProPlot.

"""


# Read damping files
dampFiles = sorted(glob("damp_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
dampings = read_csv("damping.dat", delim_whitespace=True, names=["vp", "vs", "st"], comment="#")
damping_vp = dampings.vp.values
damping_vs = dampings.vs.values

res = {}
for df in dampFiles:
    dep = df.split("_")[1].split(".")[0]
    res[dep] = {"DV":[], "VPV":[], "VSV":[], "WRMS":[]}
    with open(df) as f:
        for l in f:
            if "DATA VARIANCE" in l and not "INITIAL" in l:
                l = next(f)
                [res[dep]["DV"].append(float(_)) for _ in l.split()]
            if "Vp VARIANCE" in l:
                l = next(f)
                [res[dep]["VPV"].append(float(_)) for _ in l.split()]
            if "VpVs VARIANCE" in l:
                l = next(f)
                [res[dep]["VSV"].append(float(_)) for _ in l.split()]
            if "WEIGHTED-RMS" in l:
                l = next(f)
                [res[dep]["WRMS"].append(float(_)) for _ in l.split()]

dampings = sorted(res.keys(), key=lambda x: int(x))

# Plot L-Curve
fig, axs = plt.subplots(ncols=2)
axs.format(collabels=["$V_{p}$", "$V_{p}/V_{s}$"], xlabel="Model Variance $(km/s)^2$", ylabel="Data Variance $(s)^2$", yformatter="%.3f")
axs.grid(ls=":")
cycle = plt.Cycle('greys', left=0.2, N=len(res))

c = 0
for dep, dic in res.items():
    legend_kw = {"title":"damping", "fontsize":5}

    axs[0].plot(dic["VPV"], dic["DV"], lw=2, ls="", marker="o", ms=3, cycle=cycle)
    axs[0].plot(dic["VPV"], dic["DV"], lw=2, ms=3, cycle=cycle, label=str(damping_vp[c]), legend="ur", legend_kw=legend_kw)

    axs[1].plot(dic["VSV"], dic["DV"], lw=2, ls="", marker="o", ms=3, cycle=cycle)
    axs[1].plot(dic["VSV"], dic["DV"], lw=2, ms=3, cycle=cycle, label=str(damping_vs[c]), legend="ur", legend_kw=legend_kw)
    c+=1

y1 = res[dampings[0]]["DV"][0]
y2 = res[dampings[-1]]["DV"][0]

for i,j in zip([0, 1], ["P", "S"]):
    
    xlim = axs[i].get_xlim()
    ylim = axs[i].get_ylim()
    x1 = res[dampings[-1]]["V%sV"%j][0]
    x2 = res[dampings[0]]["V%sV"%j][0]
    iax = axs[i].inset([.4, .3, .5, .3],
                       transform="axes",
                       zoom=True,
                       zoom_kw={"color": "red3", "lw": 1, "ls": ":"})
    iax.format(title="All dampings - First iteration",
               titlesize=5,
               titleweight="bold",
               xlim=(x1, x2),
               ylim=(y1, y2),
               color="k",
               linewidth=.5,
               ticklabelweight="bold",
               ticklabelsize=5,
               yformatter="%.3f")
    iax.plot([res[dep]["V%sV"%j][0] for dep in sorted(res.keys(), reverse=True, key=lambda x: int(x))],
             [res[dep]["DV"][0] for dep in sorted(res.keys(), reverse=True, key=lambda x: int(x))],
             color="r",
             lw=1,
             ls=":",
             marker="o",
             ms=2)
    iax.grid(ls=":")
    axs[i].set_xlim(xlim)
    axs[i].set_ylim(ylim)

fig.save("Damping.png", transparent=False)
print("\n+++ 'Damping.png' was saved.")

# Plot Weighted RMS for selected damping
inp = input("\n+++ Which damping to use for Weighted-RMS figure:\n")
fig, axs = plt.subplots()
axs.format(xlabel="Iteration", ylabel="Weighted RMS (s)", yformatter="%.3f")
axs.grid(ls=":")
axs.plot(res[inp]["WRMS"], lw=2, ls=":", marker="o", ms=4, color="k")

fig.save("WTRMS.png", transparent=False)

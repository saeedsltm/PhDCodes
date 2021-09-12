#!/home/saeed/Programs/miniconda3/bin/python

from scipy.interpolate import interp1d
from pandas import read_csv
from numpy import array, meshgrid, savetxt
import proplot as plt
import os, sys

"""

Script for get interpolated values of a given velocity model.

Output:
PNG file "GradedModel.png" will be saved in "START" directory.

ChangeLogs:

01-Aug-2017 > Initial.
29-Mar-2021 > Use Proplot for making high quality figure.

"""

if not os.path.exists("hypoel.prm"):
    print("\n+++ Velocity file 'hypoel.prm' not found.")
    sys.exit()

inp = input("\n+++ Enter file name with desired depths inside, [Enter for 'dn.dat' file]:\n")
if not inp : inp = "dn.dat"

# Read input files
vm = read_csv("hypoel.prm", delim_whitespace=True, names=["VELOVITY", "vp", "z","vpvs"])
target = read_csv(inp, delim_whitespace=True, names=["ddep"])

# Interpolate velocity
x, y = vm.z.values, vm.vp.values
f = interp1d(x, y, fill_value="extrapolate")

xnew = target.ddep.values
ynew = f(xnew)

# Make grid and plot
X, Y = meshgrid(xnew, ynew)
extent = [0, xnew.max(), -xnew.max(), 0]

fig, ax = plt.subplots()
ax.format(suptitle="1D Graded Model", ylabel="Depth (km)", yformatter="%d")
ax.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
colorbar_kw = {"title":"$V_{p}$ (km/s)", "maxn":6, "reverse":True, "formatter":plt.constructor.Formatter("%.2f")}
im = ax.imshow(Y, extent=extent, interpolation="spline16", colorbar="r", cmap="Spectral_r", N=100, colorbar_kw=colorbar_kw)
for z in xnew: ax.hlines(y=-z, xmin=X.min(), xmax=X.max(), ls=":", color="k")
ax.set_aspect("auto")
ax.grid(False)

# Save results
fig.save("GradedModel.png", transparent=False)
plt.close()

out = array([xnew, ynew])
savetxt("GradedModel.dat", out, fmt="%6.2f")

print("+++ 'GradedModel.dat' and 'GradedModel.png' were saved.")

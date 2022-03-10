#!/home/saeed/Programs/miniconda3/bin/python

import matplotlib.pyplot as plt
import os, sys
from glob import glob
from pathlib import Path

seiscompArchivePath = os.path.join(os.environ["SEISCOMP_ROOT"], "var", "lib", "archive")

db = {}
for year in sorted(glob(os.path.join(seiscompArchivePath, "*"))):
    if os.path.isdir(year):
        yearName = year.split(os.sep)[-1]
        db[yearName] = {}
        for net in sorted(glob(os.path.join(year, "*"))):
            if os.path.isdir(net):
                netName = net.split(os.sep)[-1]
                db[yearName][netName] = {}
                for sta in sorted(glob(os.path.join(net, "*"))):
                    if os.path.isdir(sta):
                        staName = sta.split(os.sep)[-1]
                        db[yearName][netName][staName] = {}
                        for chn in sorted(glob(os.path.join(sta, "*Z.D"))):
                            chnName = chn.split(os.sep)[-1]
                            db[yearName][netName][staName][chnName] = []
                            for mseedFile in sorted(glob(os.path.join(chn, "*"))):
                                day = int(mseedFile.split(os.sep)[-1].split(".")[-1])
                                db[yearName][netName][staName][chnName].append(day)

for year in db:
    for net in db[year]:
        for sta in db[year][net]:
            Path(os.path.join(year, net, sta)).mkdir(parents=True, exist_ok=True)
            for chn in db[year][net][sta]:
                x = db[year][net][sta][chn]
                y = [0 for _ in x]
                ax = plt.subplot(111)
                ax.hlines(y=0, xmin=1, xmax=365, color="k")
                ax.plot(x, y, marker="|", ms=10, color="r", ls="", mew=0.5)
                ax.set_xlabel(str(year))
                ax.set_ylim(-0.1, 0.1)
                name = "_".join([year, net, sta])+".png"
                plt.savefig(os.path.join(year, net, sta, name))
                plt.close()


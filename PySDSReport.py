#!/home/saeed/Programs/miniconda3/bin/python

from obspy.imaging.scripts.scan import Scanner
from numpy import empty
from obspy import UTCDateTime as utc
import proplot as ppl
from glob import glob
import os

"""

Script for makeing visual report from SDS archive

ChangeLogs:

11-Oct-2021 > Initial.

"""

# Get information from user
net = input("\n+++ Network code:\n")
year = input("\n+++ Year:\n")
starttime=utc(input("\n+++ StartTime [2000-01-01]:\n"))
endtime=utc(input("\n+++ EndTime [2000-01-01]:\n"))

# Seiscomp archive path
scArchive = os.path.join(os.environ["SEISCOMP_ROOT"], "var", "lib", "archive")
# Prepare station list
staList = staList = sorted(glob(os.path.join(scArchive, year, net, "*")), key=lambda x: (len(x.split(os.sep)[-1]), x))
tmp = empty(10*round(len(staList)/10), dtype=object)
for i,v in enumerate(staList):
    tmp[i] = v
staList = tmp.reshape((round(len(staList)/10), 10))

# Loop over Z component of each station and make plots for statsion operation status 
for j,stations in enumerate(staList):
    numSta = sum([bool(_) for _ in stations])
    staGaps = {}
    ppl.rc.update(
        fontsize=4,
        figurefacecolor="w") 
    fig, axs = ppl.subplots(
        ncols=1,
        nrows=numSta,
        refaspect=(10,1))
    axs.format(
        xlabel="Date",
        ylabel="Stations",
        xformatter="concise",
        xlim=(starttime.datetime, endtime.datetime))
    for i,station in enumerate(list(filter(None, stations))):
        print(station)
        waveformPath = glob(os.path.join(station, "*Z.D"))[0]
        scanner = Scanner(format="MSEED")
        scanner.parse(waveformPath)
        scanner.analyze_parsed_data(starttime=starttime, endtime=endtime)
        axs[i].format(urtitle=station.split(os.sep)[-1])
        axs[i].spines['right'].set_visible(False)
        axs[i].spines['top'].set_visible(False)
        axs[i].set_yticks([])
        axs[i].grid(ls=":")
        line1 = axs[i].hlines(0, starttime.matplotlib_date, endtime.matplotlib_date, "g", linewidth=2, zorder=1, label="data")
        for s,e in scanner._info[list(scanner._info.keys())[0]]["gaps"]:
            line2 = axs[i].hlines(0, s, e, "r", linewidth=2, zorder=2, label="gap")
    fig.legend([line1, line2], ncols=1, frame=False, loc="r")
    fig.save("staOperation_%d.png"%(j+1), transparent=False)
    

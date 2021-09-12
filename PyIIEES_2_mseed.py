#!/home/saeed/Programs/miniconda3/bin/python

import zipfile
import obspy as obs
import os

"""

Script for converting IIEES waveform to miniseed.

ChangeLogs:

04-Sep-2018 > Initial.

"""

inputfile = input("\n+++ Enter IIEES wave file name: [zipfile]\n\n")

root = os.getcwd()
zip_ref = zipfile.ZipFile(inputfile, "r")
zip_ref.extractall("wavesout")
zip_ref.close()

os.chdir("wavesout")
sts = []
streams = obs.read("*BIN*")

for tr in streams:

    tr.stats.network = "BI"
    tr.stats.channel = "SH"+tr.stats.channel[-1]
    sts.append(tr.stats.station)

sts = sorted(set(sts))

for st in sts:

    s = streams.select(station=st)
    s.write("BI.%s.msd"%st, format="mseed")
    
cmd = "mkdir ../mseed"
os.system(cmd)    
cmd = "mv *.msd ../mseed"
os.system(cmd)
os.chdir(root)
cmd = "rm -rf wavesout"
os.system(cmd)

print("\n+++ Conversion done!\n")

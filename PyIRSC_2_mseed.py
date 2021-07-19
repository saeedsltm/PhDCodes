#!/home/saeed/Programs/miniconda3/bin/python

from glob import glob
from obspy import read
from numpy import ma
import os
import zipfile

"""

Script for converting IRSC YFILES to miniseed.

ChangeLogs:

15-Aug-2018 > Initial.

"""
root = os.getcwd()

irsc_zip = input("\n+++ IRSC zip file:\n")
with zipfile.ZipFile(irsc_zip, "r") as zip_ref:
    zipFolder = irsc_zip.split(".zip")[0]
    zip_ref.extractall(zipFolder)

os.chdir(zipFolder)

yfiles = glob('[Yy]*')
stations = sorted(set([i.split('_')[0][1:] for i in yfiles]))

def handle_masked_arr(st):
    for tr in st:
        tr.stats.network = "IR"
        tr.stats.channel = tr.stats.channel.replace("B","S")
        if isinstance(tr.data, ma.masked_array):
            tr.data = tr.data.filled()
    return st

if not os.path.exists('mseed'):
    os.mkdir('mseed')
else:
    cmd = 'rm -r mseed/*'
    os.system(cmd)
    
for station in stations:
    try:
        st = read('*%s*'%(station))
        st = st.merge(fill_value="interpolate")
        st = handle_masked_arr(st)
        st.write(os.path.join('mseed','IR.%s.msd'%(station)), format='mseed')
        print("+++ Working on %s"%(station))
    except:
    	print("+++ Something wrong when merging %s"%(station))

print("\n+++ %d waveforms/stations converted to miniseed."%(len(stations)))
os.chdir(root)

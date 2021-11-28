#!/home/saeed/Programs/miniconda3/bin/python

from obspy import read
from glob import glob
import os

"""

Correct record length of a miniseed file to 512.

- Copy this script to $SEISCOMP_ROOT/var/lib/archive/YYYY/NN/,
- Run the script.

"""

stationList = [_ for _ in glob("*") if len(_) == 4 and "." not in _]

for station in stationList:
    channels = glob(os.path.join(station, "*"))
    for channel in channels:
        mseeds = sorted(glob(os.path.join(channel, "*")))
        for mseed in mseeds:
            print(mseed)
            st = read(mseed, format="MSEED")
            st.write('out.mseed', format='MSEED', reclen=512, encoding='STEIM2')
            cmd = "mv {0} {1}".format("out.mseed", mseed)
            os.system(cmd)

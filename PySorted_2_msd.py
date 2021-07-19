#!/home/saeed/Programs/miniconda3/bin/python

import obspy as obs
import os

"""

Script for seprat Seiscomp3 sorted to msd files.

ChangeLogs:

13-Sep-2018 > Initial.

"""

if not os.path.exists("mseed"): os.mkdir("mseed")
else:
    os.system("rm -rf mseed")
    os.mkdir("mseed")

stream = obs.read('sorted.mseed')
stations = sorted(set([tr.stats.station for tr in stream.traces]))

for station in stations:

    st = stream.select(station=station)
    net = st[0].stats.network
    nam = '%s.%s.msd'%(net,station)
    st.write(os.path.join("mseed", nam), format="mseed")

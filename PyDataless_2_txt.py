#!/home/saeed/Programs/miniconda3/bin/python

import obspy as obs

"""

# Extract station information from dlsv files.

"""
inv = input("\n\n+++ Enter dataless file name:\n")
inv = obs.read_inventory(inv)
    
stations = []

with open('dataless.dat', 'w') as f:
    
    for net in inv:

        for station in net:

            if station.code not in stations:

                stations.append(station.code)

                f.write('%2s %4s %7.3f %7.3f %5d\n'%(net.code, station.code,
                        station.longitude, station.latitude, station.elevation))

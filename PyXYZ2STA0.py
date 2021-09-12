#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll

"""

Script for converting station file to NORDIC format.

NOTE: 

The input file must have the following format:

sta lat lon elv

ChangeLogs:

04-Aug-2017 > Initial.

"""

inp = raw_input('\n\n+++ Enter the input file name with the following format:\n\nsta lat lon elv\n\n')
out = open('new_'+inp,'w')

with open(inp) as f:

    for l in f:

        l = l.split()
        sta = l[0]
        lat = ll.Latitude(float(l[1]))
        lon = ll.Longitude(float(l[2]))
        elv = float(l[3])

        with open(out.name,'a') as g:

            g.write('  %-4s%02d%05.2f%1s %02d%05.2f%1s%00004d\n'%(sta,lat.degree,lat.decimal_minute,lat.get_hemisphere(),lon.degree,lon.decimal_minute,lon.get_hemisphere(),elv))

print '\n+++ File %s is ready.\n'%(out.name)

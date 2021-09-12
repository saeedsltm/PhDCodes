#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll

nlloc_sta = open('station.dat', 'w')

with open('staz.dat') as f:

    for i,l in enumerate(f):

        if i > 1:

            nam = l[:6].strip()
            lat = ll.Latitude(degree=float(l[6:8]), minute=float(l[9:14])).decimal_degree
            lon = ll.Longitude(degree=float(l[14:18]), minute=float(l[19:24])).decimal_degree
            elv = float(l[24:29])

            with open(nlloc_sta.name, 'a') as g:

                line = 'GTSRCE  %-4s  LATLON  %7.3f  %7.3f  0.0  %5.3f\n'%(nam,lat,lon,elv*1e-3)
                g.write(line)

g.close()

#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll

inp = 'travel.dat'
out = open('used.dat', 'w')
neq = 0

with open(inp) as f:

    for l in f:

        try:

            if l[20]=='N' and l[30]=='E':

                lat = ll.Latitude(degree=float(l[18:20]), minute=float(l[21:26])).decimal_degree
                lon = ll.Longitude(degree=float(l[28:30]), minute=float(l[31:36])).decimal_degree
                dep = float(l[37:43])
                neq+=1

                with open(out.name, 'a') as g:

                    line = '%7.3f %7.3f %7.3f\n'%(lat, lon, dep)
                    g.write(line)
                    
        except IndexError: pass

print '\n\n+++ %d events saved into "used.dat" file.\n'%(neq)

#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll

W = input("\n+++ Longitude West:\n")
E = input("\n+++ Longitude East:\n")
S = input("\n+++ Latitude South:\n")
N = input("\n+++ Latitude North:\n")

i=0
c=0
try:
    
    with open("hypoel.sta") as f, open("hypoel_new.sta", "w") as g:

        for l in f:

            if "*" in l: i+=1; continue

            sta = l[:4].strip()
            lat = ll.Latitude(degree=float(l[4:6]), minute=float(l[7:12])).decimal_degree
            lon = ll.Longitude(degree=float(l[14:16]), minute=float(l[17:22])).decimal_degree

            if (S <= lat <= N) and (W <= lon <= E):

                g.write(l)
                g.write(next(f))
                c+=1
                i+=1
        print "\n+++ From %d, %d stations remained."%(i,c)
        
except IOError:
    
    print "\n+++ No 'hypoel.sta' file was found.\n"

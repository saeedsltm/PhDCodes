#!/home/saeed/Programs/miniconda3/bin/python

"""
Script for extracting fault geometry from shape file into GMT
text format.

"""

import geopandas as gp

df = gp.read_file("gem_active_faults.shp")
with open("faults.dat", "w") as f:
    for l,n in zip(df["geometry"], df["name"]):
        x,y = l.xy
        f.write("> %s\n"%(n))
        for i,j in zip(x,y):
            f.write("%7.3f %7.3f\n"%(i,j))

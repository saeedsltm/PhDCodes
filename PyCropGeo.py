#!/home/saeed/Programs/miniconda3/bin/python

import geopandas as gpd
import os, sys

outName = input("\n+++ Region Name:\n")
xMin = float(input("\n+++ Min Longitude:\n"))
xMax = float(input("\n+++ Max Longitude:\n"))
yMin = float(input("\n+++ Min Latitude:\n"))
yMax = float(input("\n+++ Max Latitude:\n"))

useColumns = ['DESCRIPTIO', 'AGE', 'AGE_ERA', 'geometry']

db = gpd.GeoDataFrame.from_file(os.path.join(os.environ["GMTHOME"],"geology","IRANGEO.shp"))
db = db.to_crs(epsg=4326)
db = db.cx[xMin:xMax, yMin:yMax]

dropColumns = set(db.columns) - set(useColumns)
db = db.drop(columns=dropColumns)

db.to_file("%s.shp"%(outName))

print("\n+++ Done!")

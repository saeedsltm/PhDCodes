#!/home/saeed/Programs/miniconda3/bin/python

from shapely.geometry.multipolygon import MultiPolygon
import geopandas as gpd
import os

db = gpd.GeoDataFrame.from_file(os.path.join(os.environ["GMT_STUFF"],"IranSHP","Province.shp"))
nameEn, nameFa = "Ostan_Engl", "Center_Nam"
##db = gpd.GeoDataFrame.from_file(os.path.join(os.environ["GMT_STUFF"],"IranSHP","County.shp"))
##nameEn, nameFa = "Center_Eng", "Center_Nam"
## db = gpd.GeoDataFrame.from_file(os.path.join(os.environ["GMT_STUFF"],"IranSHP","city.shp"))
## column = "Region_Eng"
names = {}
db = db.to_crs(epsg=4326)
for i,nEn,nFa in zip(db["geometry"], db[nameEn], db[nameFa]):
    nEn = "".join(nEn.split())
    names[nFa] = []
    if type(i) == type(MultiPolygon()):
        with open("{0}.dat".format(nEn), "w") as f:
            for m in i:
                f.write(">\n")
                X,Y = m.exterior.coords.xy
                names[nFa].append(m.centroid.xy[0][0])
                names[nFa].append(m.centroid.xy[1][0])
                for x,y in zip(X, Y): f.write("{0:7.3f} {1:7.3f}\n".format(x, y))
    else:
        with open("{0}.dat".format(nEn), "w") as f:
            X, Y = i.exterior.coords.xy
            names[nFa].append(i.centroid.xy[0][0])
            names[nFa].append(i.centroid.xy[1][0])
            for x,y in zip(X, Y): f.write("{0:7.3f} {1:7.3f}\n".format(x, y))
with open("names.dat", "w") as f:
    for name in names:
        x,y = names[name][0], names[name][1]
        f.write("{0:7.3f} {1:7.3f} {2:s}\n".format(x, y, name))

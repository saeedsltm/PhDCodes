#!/home/saeed/Programs/miniconda3/bin/python

from shapely.geometry import LineString
from geopy import distance
from glob import glob
import os, sys
from numpy import array, linspace, sqrt, loadtxt
import pylab as plt
from re import split

"""

Script for prepare a text file for plotting
fault names on profile in a cross section.

outputs:

fault_on_profile.dat

ChangeLogs:

15-Sep-2017 > Initial.

"""

if len(sys.argv) != 8:

    print('\n\n Profile: Ax Ay Bx By elevation[where to plot fault name on profile] dx[shift]\n')
    sys.exit(0)
    
else:

    GMT_V = sys.argv[1]
    Ax = float(sys.argv[2])
    Ay = float(sys.argv[3])
    Bx = float(sys.argv[4])
    By = float(sys.argv[5])
    h  = float(sys.argv[6])
    dx = float(sys.argv[7]) 
    
    fault_on_cross = open('fault_on_profile.dat','w')

    #SET FORMATTED LINE FOR WHICH GMT VERSION
    line_type = {"5":'%7.3f %7.3f 7,Times-Bold,black 90 LT >%s\n',
                 "4":'%7.3f %7.3f 7 90 27 LT @;black;@ >%s\n'}

    for f_dir in ["SSL", "SSR", "THL", "THR", "NOR"]:

        fault_files = glob(os.path.join(os.environ['GMT_STUFF'], "Fault", "IranFaults", f_dir, "*.dat"))

        faults  = []
        names   = []
        memorey = []

        for f in fault_files:

            name = split("[/|.]", f)[-2]
            name = name.replace("North_", "N.")
            name = name.replace("South_", "S.")
            data = loadtxt(f)

            names.append(name)
            faults.append(data)
    
        for fn,fl in zip(names,faults):

            with open(fault_on_cross.name,'a') as f:

                fault   = array(fl)
                profile = array([(i,j) for i,j in zip(linspace(Ax,Bx,100),
                                                      linspace(Ay,By,100))])

                line1  = LineString(fault)
                line2  = LineString(profile)
                points = []
                intersects = line1.intersection(line2)
                
                if not intersects: continue
             
                try:

                    for point in intersects:

                        x = point.xy[0][0]
                        y = point.xy[1][0]
                        d = distance.distance((Ay,Ax),(y,x)).km + dx
                        line = line_type[GMT_V]%(d,h,fn)
                        if fn not in memorey:
                            memorey.append(fn)
                            f.write(line)
     
                except TypeError:

                        x = intersects.xy[0][0]
                        y = intersects.xy[1][0]
                        d = distance.distance((Ay,Ax),(y,x)).km + dx
                        line = line_type[GMT_V]%(d,h,fn)
                        if fn not in memorey:
                            memorey.append(fn)
                            f.write(line)


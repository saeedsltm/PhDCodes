#!/home/saeed/Programs/miniconda3/bin/python

from shapely.geometry import LineString
from geopy import distance
from glob import glob
import os, sys
from numpy import array, linspace, sqrt
import pylab as plt

"""

Script for prepare a text file for plotting
fault names on profile in a cross section.

outputs:

fault_on_profile.dat

ChangeLogs:

15-Sep-2017 > Initial.

"""

if len(sys.argv) != 7:

    print '\n\n Profile: Ax Ay Bx By elevation[where to plot fault name on profile] dx[shift]\n'
    sys.exit(0)
    
else:

    Ax = float(sys.argv[1])
    Ay = float(sys.argv[2])
    Bx = float(sys.argv[3])
    By = float(sys.argv[4])
    h  = float(sys.argv[5])
    dx = float(sys.argv[6]) 
    
    fault_on_cross = open('fault_on_profile.dat','w')

    fault_files = glob(os.path.join(os.environ['GMTHOME'], 'fault', '*.txt'))

    faults  = []
    names   = []
    memorey = []

    for fault_file in fault_files:
        
        with open(fault_file) as f:

            for l in f:

                if '---' in l:

                    faults.append([])

                    line = next(f)
                    name = ' '.join(line.split()[2:])
                    names.append(name)
                    faults[-1].append((float(line.split()[0]),float(line.split()[1])))

                else:

                    faults[-1].append((float(l.split()[0]),float(l.split()[1])))

    for fn,fl in zip(names,faults):

        with open(fault_on_cross.name,'a') as f:

            fault   = array(fl)
            profile = array([(i,j) for i,j in zip(linspace(Ax,Bx,100),
                                                  linspace(Ay,By,100))])

            line1  = LineString(fault)
            line2  = LineString(profile)
            points = []
            intersects = line1.intersection(line2)
         
            try:

                for point in intersects:

                    x = point.xy[0][0]
                    y = point.xy[1][0]
                    d = distance.vincenty((Ay,Ax),(y,x)).km + dx
                    line = '%7.3f %7.3f 5 90 27 LT @;black;@ >%s\n'%(d,h,fn)
                    if line not in memorey:
                        memorey.append(line)
                        f.write(line)
 
            except TypeError:

                    x = intersects.xy[0][0]
                    y = intersects.xy[1][0]
                    d = distance.vincenty((Ay,Ax),(y,x)).km + dx
                    line = '%7.3f %7.3f 5 90 27 LT @;black;@ >%s\n'%(d,h,fn)
                    if line not in memorey:
                        memorey.append(line)
                        f.write(line)


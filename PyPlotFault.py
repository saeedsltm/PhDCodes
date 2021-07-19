from geopy import distance
from scipy.interpolate import spline
from scipy import linspace
import pylab as plt
from scipy.interpolate import UnivariateSpline

faults = []

with open('data') as f:

    for l in f:

        if '---' in l:

            faults.append([])

        else:

            faults[-1].append(tuple(l.split()[:2]))


for fault in faults:

    fault_len = 0
    x = [float(_[0]) for _ in fault]
    y = [float(_[1]) for _ in fault]

    for i,j in zip(range(0,len(fault)-1), range(1,len(fault))):

        Ax = fault[i][0]
        Ay = fault[i][1]
        Bx = fault[j][0]
        By = fault[j][1]

        fault_len += distance.vincenty((Ay,Ax),(By,Bx)).km


xnew = linspace(min(x),max(x),100,1)
spl  = UnivariateSpline(x, y, s=.0001)
ynew = spl(xnew) 

plt.plot(x,y)
plt.plot(xnew,ynew)
plt.show()


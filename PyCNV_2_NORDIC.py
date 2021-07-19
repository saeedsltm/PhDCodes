#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from numpy import arange

nordic_out = open('nordic.out','w')

input_cnv = 'data.cnv'

cen = raw_input('\n+++ Which century? [20 or 19]:\n\n') # which centery to use

with open(input_cnv) as f:

    for l in f:

        if (l[25:26] == 'N' or l[25:26] == 'S') and (l[35:36] == 'E' or l[35:36] == 'W'):

            year= int(cen+(l[:2].replace(' ','0')))
            mon = int(l[2:4])
            day = int(l[4:6])
            hh  = int(l[7:9])
            mm  = int(l[9:11])
            ss  = int(float(l[12:17]))
            mss = float(l[12:17]) - ss
            mss = int(mss*1e6)
            ort = dt(year,mon,day,hh,mm,ss,mss)
            lat = float(l[17:25])
            lon = float(l[26:35])
            dep = float(l[36:43])
            l1  = ' %4d %02d%02d %02d%02d %4.1f L %7.3f %7.3f%5.1f                                    1\n'%(ort.year,ort.month,ort.day,
                                                                                                          ort.hour,ort.minute,ort.second+ort.microsecond*1e-6,
                                                                                                          lat,lon,dep)

            nordic_out.write(l1)
            nordic_out.write(' STAT SP IPHASW D HRMM SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ7\n')

        elif l.strip():

            for c in arange(4,72,12, dtype=int):

                try:

                    sta = l[c-4:c]
                    pha = l[c:c+1]
                    wte = l[c+1:c+2]
                    art = float(l[c+2:c+8])
                    art = ort + td(seconds=art)
                    l4  = ' %4s     %1s   %1s   %02d%02d %5.2f                                                   4\n'%(sta,pha,wte,
                                                                                                                       art.hour,art.minute,art.second+art.microsecond*1e-6)
                    nordic_out.write(l4)
                    
                except ValueError:

                    pass

        else:

            nordic_out.write('\n')

nordic_out.close()

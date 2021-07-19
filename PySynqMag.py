#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from math import sqrt

"""

Script for synq magnitude between two NORDIC files.

ChangeLogs:

07-Apr-2018 > Initial.

"""

ref_file = raw_input('\n+++ Enter refrence NORDIC file:\n\n')
tar_file = raw_input('\n+++ Enter target NORDIC file:\n\n')

origin_time_diff = 60.0 # second
location_diff = 60.0    # km
n = 0

with open(ref_file) as ref , open('synq.out', 'w') as out:

    for ref_l in ref:

        if ref_l.strip() and ref_l[79:80] == '1':

            for i in [6,8,11,13,16]:

                if ref_l[1:20][i] == ' ':

                    ref_l[1:20] = ref_l[1:20][:i]+ref_l[1:20][i].replace(' ','0')+ref_l[1:20][i+1:]

            try:

                ref_date = dt.strptime(ref_l[1:20],'%Y %m%d %H%M %S.%f')
                if ref_date.year > 2900: ref_date.replace(year=ref_date.year-1000)
                ref_lat = float(ref_l[23:30])
                ref_lon = float(ref_l[32:38])

            except ValueError:

                continue

            with open(tar_file) as tar:

                cond = False
                    
                for tar_l in tar:

                    if tar_l.strip() and tar_l[79:80] == '1':

                        for i in [6,8,11,13,16]:

                            if tar_l[1:20][i] == ' ':

                                tar_l[1:20] = tar_l[1:20][:i]+tar_l[1:20][i].replace(' ','0')+tar_l[1:20][i+1:]

                        try:

                            tar_date = dt.strptime(tar_l[1:20],'%Y %m%d %H%M %S.%f')
                            if tar_date.year > 2900: tar_date.replace(year=tar_date.year-1000)
                            tar_lat = float(tar_l[23:30])
                            tar_lon = float(tar_l[32:38])

                        except ValueError:

                            continue

                        diff_ot = ref_date - tar_date
                        diff_ot = abs(diff_ot.total_seconds())

                        diff_loc = sqrt((ref_lat - tar_lat)**2 + (ref_lon - tar_lon)**2)

                        if ref_l[56:59].strip() and diff_ot < origin_time_diff and diff_loc <= location_diff:

                            tar_l = tar_l[:56]+str(float(ref_l[56:59]))+tar_l[59:]
                            cond = True
                            n+=1

                    if cond: out.write(tar_l)
                    
                    if cond and not tar_l.strip(): break

print "\n+++ synq.out is ready with %d number of earthquake.\n"%n
                        

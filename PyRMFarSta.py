#!/home/saeed/Programs/miniconda3/bin/python

import os

"""

Script for removing stations beyond a critical distance from
the main dataset.

ChangeLogs:

03-Aug-2017 > Initial.

"""

inp = raw_input('\n\n+++ Enter NORDIC file name:\n\n')
dis = input('\n+++ Enter maximum event-station distance [stations beyond this value will be removed]:\n\n')
out = open('new_'+inp,'w')

with open(inp) as f:

    for l in f:

        if l.strip() and l[79:80] in (' ','4') and l[70:75].strip() and float(l[70:75]) >= dis:

            continue

        else:

            with open(out.name,'a') as g:

                g.write(l)

print '\n+++ File %s is ready.\n'%('new_'+inp)

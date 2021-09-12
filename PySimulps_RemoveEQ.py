#!/home/saeed/Programs/miniconda3/bin/python

import os

inp = raw_input("\nEnter EQ file [eqks.out/travel.dat]:\n")
eqk = input("\nEnter number of EQ to be removed:\n")

if not inp: inp = "travel.dat"
n = 1

with open(inp) as f, open('tmp.dat', 'w') as g:

    for l in f:

        if not l.strip(): n+=1

        if n == eqk: flag = False
        else: flag = True

        if flag: g.write(l)

os.remove(inp)
os.rename('tmp.dat', inp)
print "\nDone!"

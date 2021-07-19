#!/home/saeed/Programs/miniconda3/bin/python

import sys

"""
Script for Read/Write Station correction from hypoellipse output.
Note:

ChangeLogs:

8-Jul-2020 > Initial.

"""

hypout = sys.argv[1]
    
lable = "station  n  wt  ave   sd     n   wt  ave   sd      n  wt   ave  sd     n   wt   ave  sd    station"
flag = False
sta_corr = {}

# Read Station Corrections
with open("%s.out"%(hypout)) as f:

    for l in f:
        

        if lable in l: flag = True
        if flag and not l.strip(): flag = False

        if flag and lable not in l:

            sta = l[:7].strip().upper()
            NoP = int(l[8:12])
            Pcorr = float(l[16:22])
            NoS = int(l[70:74])
            Scorr = float(l[79:85])

            sta_corr[sta] = {"P":{"N":NoP, "Corr":Pcorr},
                             "S":{"N":NoS, "Corr":Scorr}
                             }

# Write Station Corrections
with open("hypoel.sta") as f, open("hypoel.sta_corr", "w") as g:

    for l in f:

        if l[10] != "0":

            sta = l[:4].strip()

            for station in sta_corr:

                Pcorr = 0
                Scorr = 0

                if station == sta:

                    if sta_corr[sta]["P"]["N"] >= 10: Pcorr = sta_corr[sta]["P"]["Corr"]
                    if sta_corr[sta]["S"]["N"] >= 10: Scorr = sta_corr[sta]["S"]["Corr"]

                    Pcorr = "%4.2f"%(Pcorr)
                    Pcorr = Pcorr.replace("0.", ".")

                    Scorr = "%4.2f"%(Scorr)
                    Scorr = Scorr.replace("0.", ".")

                    l = l[:len(l)-1] + "            %4s%4s\n"%(Pcorr, Scorr)

        g.write(l)


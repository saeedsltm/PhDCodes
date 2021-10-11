#!/home/saeed/Programs/miniconda3/bin/python

from PySTA0RW import Read_Nordic_Sta

def toGrowClust(sta0Dict):
    with open("stlist.dat", "w") as f:
        for sta in sta0Dict["STA"]:
            f.write("%-5s  %7.4f %9.4f\n"%(sta,
                                           sta0Dict["STA"][sta]["LAT"],
                                           sta0Dict["STA"][sta]["LON"]))

sta0 = input("\n+++ Enter station file name with NORDIC format:[Enter=STAION0.HYP]\n")
if not sta0: sta0 = "STAION0.HYP"
sta0Dict = Read_Nordic_Sta()

cmd = input("+++ Choose one of the following as target formats:\n1-GrowClust\n2-HypoDD\n")

if cmd == 1:
    toGrowClust(sta0Dict)

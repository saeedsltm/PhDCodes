#!/home/saeed/Programs/miniconda3/bin/python

from pandas import read_csv, to_datetime
from datetime import datetime as dt
from numpy import abs, sqrt
from PyMyFunc import d2k
from shutil import copy
import os

"""

Script for merging two hypoeelipse file

outputs:

hypoel.sta
hypoel_fin.pha
report.dat

ChangeLogs:

27-Aug-2017 > Initial.
30-Jul-2017 > Improved Performance.
10-Apr-2021 > Add amplitude and period to final output

"""

print("")
print("*"*80)
print(" Script for merging two Hypoellipse files.".center(80, "*"))
print("*"*80)
print("\n+++ All hypoel.* and xyzm.dat must exist in Reference and Targer directories.")

ref_dir = input("+++ Enter Reference directory:\n")
tar_dir = input("+++ Enter Targer directory:\n")

max_dX = float(input("\n+++ Maximum epicentral difference for two common events (km):\n"))
max_dT = float(input("\n+++ Maximum origin time difference for two common events (sec):\n"))

ref = read_csv(os.path.join(ref_dir, "xyzm.dat"), delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])
tar = read_csv(os.path.join(tar_dir, "xyzm.dat"), delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])

# Set reference and target number events to zero
ref_n = 0
tar_n = 0

# Set P & S comon phases to zero
P_c = 0
S_c = 0

# Define Upper function
def upper(s):
    return s.upper()

# Run hypoellipse
def run_hypoellipse():
    with open("runHypoel.sh", "w") as f:
        f.write("#!/bin/bash\nhypoell-loc.sh hypoel << EOF\nn\nEOF")
    os.system("bash runHypoel.sh > /dev/null")

# Read hypoel.out file and return gap and rms values
def get_gap_rms(hypoel_out):
    with open(hypoel_out) as f:
        for line in f:
            if "date    origin" in line:
                l = next(f)
                if "*" in l: return 360, 100
                gap = int(l[60:63])
                rms = float(l[66:72])
    return gap, rms

# Read hypoel.pha file and extract event
def add_phases_to_dict(inp_file, event_n):
    phases = {}
    with open(os.path.join(inp_file, "hypoel.pha")) as f:
        c = 0
        for l in f:
            if not l[0].strip(): c+=1
            if c == event_n and l[0].strip():
                sta = l[:4].strip().upper()
                phases[sta] = {"P":l[:24], "S":l[24:40], "amp":l[40:50]}
    return phases

# Merge station files
def merge_stations():
    inp_ref=os.path.join(ref_dir, "hypoel.sta")
    inp_tar=os.path.join(tar_dir, "hypoel.sta")
    outp="hypoel.sta"
    inp_ref_dic = {}
    inp_tar_dic = {}
    for inp, inp_dic in zip([inp_ref, inp_tar], [inp_ref_dic, inp_tar_dic]):
        with open(inp) as f:
            for l in f:
                if "*" in l: continue
                sta = l[:4].strip().upper()
                info = l[4:27]
                inp_dic[sta] = info
    inp_ref_dic.update(inp_tar_dic)
    print('\n+++ Merged Station file  => %s'%outp)
    with open(outp, "w") as f:
        for sta in sorted(inp_ref_dic.keys(), key=lambda x:(len(x), upper(x), sorted(x))):
            f.write('%4s%23s\n'%(sta, inp_ref_dic[sta]))
            f.write('%4s*     0     1.00\n'%(sta))

# Write non common events from target into final hypoellipse phase file
def write_non_common():
    global TNCE
    commonevents = []
    with open("report.dat") as f:
        for l in f:
            if "Ref" in l: commonevents.append(int(float(l[15:21])))
    c = 0
    with open(hypoel_fin.name, "a") as f, open(os.path.join(tar_dir, "hypoel.pha")) as g:
        for l in g:
            if c not in commonevents: f.write(l); TNCE+=1
            if "    " == l[:4]: c+=1

# Relocate event with(out) new phases from target to check if it has been qualified to be added to the reference
def relocate_common_event(ref_n, tar_n):
    global P_c
    global S_c
    maxRMS = 0.5 # threshold for RMS
    maxGAP = 200 # threshold for GAP
    root = os.getcwd()
    os.system("rm -rf tmp")
    os.mkdir("tmp")
    for files in ["default.cfg", "hypoel.prm", "hypoel.sta"]:
        copy(os.path.join(ref_dir, files), os.path.join("tmp", files))
    copy("hypoel.sta", os.path.join("tmp", "hypoel.sta"))
    good_sta = []
    ref_phases = add_phases_to_dict(inp_file=ref_dir, event_n=ref_n)
    tar_phases = add_phases_to_dict(inp_file=tar_dir, event_n=tar_n)
    merged_event = ref_phases.copy()
    merged_event.update(tar_phases)
    # New P or S phases from target will be identified, for common phases, reference will be replaced by target
    do_reloc_for_stas = []
    for tar_sta in tar_phases.keys():
        if tar_sta not in ref_phases or (tar_sta in ref_phases and not ref_phases[tar_sta]["S"] and tar_phases[tar_sta]["S"]):
            do_reloc_for_stas.append(tar_sta)
    # Initial relocation to get GAP & RMS
    with open(os.path.join("tmp", "hypoel.pha"), "w") as f:
        for sta in ref_phases.keys():
            phase = merged_event[sta]["P"]+merged_event[sta]["S"]+merged_event[sta]["amp"]
            f.write(phase)
            f.write("\n")
        f.write("                 10     ")
    os.chdir("tmp")
    run_hypoellipse()
    # Get initial values of GAP and RMS
    gap_i, rms_i = get_gap_rms(hypoel_out="hypoel.out")
    # Do Relocation for new phases come from target
    for NewSta in do_reloc_for_stas:
        with open("hypoel.pha", "w") as f:
            for sta in ref_phases.keys():
                phase = merged_event[sta]["P"]+merged_event[sta]["S"]+merged_event[sta]["amp"]
                f.write(phase)
                f.write("\n")
            phase = merged_event[NewSta]["P"]+merged_event[NewSta]["S"]+merged_event[NewSta]["amp"]
            f.write(phase)
            f.write("\n")
            f.write("                 10     ")
        run_hypoellipse()
        # Get Final values of GAP and RMS
        gap_f, rms_f = get_gap_rms(hypoel_out="hypoel.out")
        if (gap_f <= gap_i or gap_f < maxGAP) and (rms_f <= rms_i or rms_f <= maxRMS):
            ref_phases[NewSta] = merged_event[NewSta]
            if merged_event[NewSta]["P"][7]!="4": P_c+=1
            if merged_event[NewSta]["S"].strip() and merged_event[NewSta]["S"][15]!="4": S_c+=1
    os.chdir(root)
    return ref_phases

#+++ Start Proccecing
c = 0
TCE = 0  # Total Number of common events
TNCE = 0 # Total Number of non-common events
TRE = 0  # Total Number of reference events
TTE = 0  # Total Number of target events
# Final hypoellipse phase file and make a report file
hypoel_fin = open("hypoel_fin.pha", "w")
report = open("report.dat", "w")
# Merge reference and target stations
merge_stations()
print("\n  Ref &   Tar")
for rx, ry, YYYY_MM_DD_HH_MN_SEC in zip(ref.LON.values, ref.LAT.values, ref.YYYY_MM_DD_HH_MN_SEC.values):
    dX = d2k(sqrt((rx-tar.LON.values)**2 + (ry-tar.LAT.values)**2))
    T1 = to_datetime(YYYY_MM_DD_HH_MN_SEC, format="%Y %m %d %H %M %S.%f")
    T2 = to_datetime(tar.YYYY_MM_DD_HH_MN_SEC.values, format="%Y %m %d %H %M %S.%f")
    dT = abs(T2-T1)
    CE = (dX<int(max_dX))&(dT.total_seconds()<int(max_dT))   
    if any(CE):
        tar_n = CE.nonzero()[0][0]
        ref_n = c
        TCE+=1
        with open(report.name, "a") as k:
            k.write("Ref=%6d Tar=%6d dX=%4.1f dT=%4.1f\n"%(ref_n, tar_n, dX[tar_n], dT.total_seconds()[tar_n]))
        print("%5d & %5d"%(ref_n, tar_n))
        fin_phases = relocate_common_event(ref_n, tar_n)
        with open(hypoel_fin.name, "a") as f:
            for sta in fin_phases.keys():
                phase = fin_phases[sta]["P"]+fin_phases[sta]["S"]+fin_phases[sta]["amp"]
                f.write(phase)
                f.write("\n")
            f.write("                 10     \n") 
    else:
        ref_phases = add_phases_to_dict(inp_file=ref_dir, event_n=c)
        with open(hypoel_fin.name, "a") as f:
            for sta in ref_phases.keys():
                phase = ref_phases[sta]["P"]+ref_phases[sta]["S"]+ref_phases[sta]["amp"]
                f.write(phase)
                f.write("\n")
            f.write("                 10     \n")        
    c+=1
TRE = ref.LON.values.size
TTE = tar.LON.values.size
# Write non common events
write_non_common()
print("\n+++ Total common event(s):",TCE)
with open(report.name, "a") as k:
    k.write("*"*40)
    k.write("\n+++ Total number of reference events: %5d"%(TRE))
    k.write("\n+++ Total number of target events   : %5d"%(TTE))
    k.write("\n+++ Total number of common events   : %5d"%(TCE))
    k.write("\n+++ Total number of new P phase     : %5d"%(P_c))
    k.write("\n+++ Total number of new S phase     : %5d"%(S_c))
if os.path.exists("tmp"):
    os.system("rm -rf tmp")

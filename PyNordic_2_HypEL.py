#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from LatLon import lat_lon as ll
import os, sys
from re import sub, match
sys.path.append(os.environ["PYT_PRG"])
from PySTA0RW import Read_Nordic_Sta

"""
Script for converting NORDIC to HYPOELLIPSE format.

INPUT FILES:
- Sfile in NORDIC.
- Station file in NORDIC (STATION0.HYP)

OUTPUT FILES:
 - hypoel.pha
 - hypoel.sta
 - hypoel.prm
 - defaults.cfg
 
ChangeLogs:

25-Jul-2017 > Now, stations sorts by length, uppercase, alphabetically.
02-Feb-2021 > Rewrite the code completely.
16-Apr-2021 > Add function for detecting deviant travel times.
18-Apr-2021 > Fixed issue when reading magnitude
"""

#___________________SECTION I: Make "hypoel.pha" phase file

# Make string upper case
def upper(s):
    return s.upper()

# Calculate maximum P and S travel time and alert if deviant travel time detected
def AlertDevTT(ot, ar, ph, nDevTT):
    pMaxTT = 200 # t=x/v; x=900km, v=6.0km/s; 166s ~ 200
    sMaxTT = 300 # t=x/v; x=900km, v=3.5km/s; 285s ! 300
    tt = ar - ot
    tt = tt.total_seconds()
    if (ph.upper() == "P" and abs(tt) > pMaxTT) or (ph.upper() == "S" and abs(tt) > sMaxTT):
        with open("deviant_tt.dat", "a") as f: 
            f.write("Check phase: PH=%s, OT=%s, AR=%s, TT=%9.1f\n"%(ph, ot.strftime("%Y-%m-%d %H:%M:%S"), ar.strftime("%Y-%m-%d %H:%M:%S"), tt))
        nDevTT+=1
    return nDevTT
                
# Get origin time
def get_ot(l):
    for i in [3,4,6,8,11,12,13,14,16,17,19]:
        if not l[i].strip():
            l = l[:i]+"0"+l[i+1:]
    flag_24h = False # if hour = 24, one day will be added to datetime
    if l[11:13] == "24": 
        flag_24h = True
        l = l[:11]+"23"+l[13:]
    try:
        ot = dt.strptime(l[1:], "%Y %m%d %H%M %S.%f")
    except ValueError:
        ot = dt.strptime(l[1:16]+"00.00", "%Y %m%d %H%M %S.%f")
        ot = ot + td(seconds=60)
    if flag_24h: ot = ot + td(seconds=3600)
    return ot

def extract_ar(l, ot, nordicFormat1, nordicFormat2):
    flag_24h = False # if hour = 24, one day will be added to datetime
    if l[18:20] == "24": 
        flag_24h = True
        l = l[:18]+"00"+l[20:]
    if bool(nordicFormat1):
        try:
            ar = dt.strptime(l[18:28], "%H%M0%S.%f")
            if flag_24h: ot = ot + td(days=1)
        except ValueError:
            ar = dt.strptime(l[18:22]+"000.00", "%H%M0%S.%f")
            ar = ar + td(seconds=60)
        ar = ar.replace(year=ot.year, month=ot.month, day=ot.day)
        return ar
    elif bool(nordicFormat2):
        try:
            ar = dt.strptime(l[18:28], "%H%M%S.%f")
            if flag_24h: ot = ot + td(days=1)
        except ValueError:
            ar = dt.strptime(l[18:22]+"000.00", "%H%M%S.%f")
            ar = ar + td(seconds=60)
        ar = ar.replace(year=ot.year, month=ot.month, day=ot.day)
        return ar

# Get arrival time
def get_ar(ot, l):
    if l[25] == ".":
        for i in [18,19,20,21,23,24,26,27]:
            if not l[i].strip():
                l = l[:i]+"0"+l[i+1:]
    elif l[24] == ".":
        for i in [18,19,20,21,22,23,26,27]:
            if not l[i].strip():
                l = l[:i]+"0"+l[i+1:]
    elif l[22:28] == "      ":
        for i in [18,19,20,21]:
            if not l[i].strip():
                l = l[:i]+"0"+l[i+1:]
        l = l[:22]+"00.000"+l[28:]
    nordicFormat1 = match("[0-9][0-9][0-9][0-9]0[0-9][0-9].[0-9][0-9]", l[18:28])
    nordicFormat2 = match("[0-9][0-9][0-9][0-9][0-9][0-9].[0-9][0-9][0-9]", l[18:28])
    ar = extract_ar(l, ot, nordicFormat1, nordicFormat2)
    return ar


# Write new event-phase to hypoellipse format
def write_to_hypoel(hypoel_file, event, nDevTT):
    for ot in event:
        for sta in event[ot]:
            if not event[ot][sta]["P_ar"]: continue
            Ponset = event[ot][sta]["P_onset"]
            Sonset = event[ot][sta]["S_onset"]
            Pph = event[ot][sta]["P_ph"]
            Sph = event[ot][sta]["S_ph"]
            pol = event[ot][sta]["P_pol"]
            Pw = event[ot][sta]["P_w"]
            Sw = event[ot][sta]["S_w"]
            Par = event[ot][sta]["P_ar"].strftime("%y%m%d%H%M%S.%f")[:15]
            nDevTT=AlertDevTT(ot, event[ot][sta]["P_ar"], Pph, nDevTT)
            amp = event[ot][sta]["amp"]
            per = event[ot][sta]["per"]
            if amp:
                if amp > 9999: amp = amp * -1e-4
                amp = "%4d"%(float(amp))
            else: amp = "    "
            if per:
                per = "%3.2f"%(float(per)); per = " "+per[2:]
            else:
                per = "   "
            if Sph:
                Sar = event[ot][sta]["S_ar"] - event[ot][sta]["P_ar"]
                Sar = event[ot][sta]["P_ar"].second + Sar.total_seconds()
                nDevTT=AlertDevTT(ot, event[ot][sta]["S_ar"], Sph, nDevTT)                
                if Sar < 100: l = "%-4s%1s%1s%1s%1s %15s       %5.2f%1s%1s %1s   %4s%3s\n"%(sta, Ponset, Pph, pol, Pw, Par, Sar, Sonset, Sph, Sw, amp, per)
                else: l = "%-4s%1s%1s%1s%1s %15s       %5.1f%1s%1s %1s   %4s%3s\n"%(sta, Ponset, Pph, pol, Pw, Par, Sar, Sonset, Sph, Sw, amp, per)
            else:
                l = "%-4s%1s%1s%1s%1s %15s                   %4s%3s\n"%(sta, Ponset, Pph, pol, Pw, Par, amp, per)
            with open(hypoel_file.name, "a") as f:
                f.write(l)
    with open(hypoel_file.name, "a") as f:
        f.write("                 10\n")
    return nDevTT
            
# Make hypoellipse arivaltime file
def mk_phase_file(nordic_inp):
    print('+++ Phase file    => hypoel.pha')
    neq=0
    nDevTT=0
    hypoel_file = open("hypoel.pha", "w")                   
    event = {}
    phase = {"sp":None,
             "P_onset":None,
             "S_onset":None,
             "P_ph":None,
             "S_ph":None,
             "P_w":None,
             "S_w":None,
             "P_pol":None,
             "S_pol":None,
             "P_ar":None,
             "S_ar":None,
             "amp":None,
             "per":None}
    with open(nordic_inp) as f:
        for l in f:
            while l.strip():
                if len(l) == 81 and l[79] == "1":
                    ot = get_ot(l[:20])
                    event[ot] = {}
                if l[79] == " ":
                    sta = l[:5].strip()
                    sp = l[6:9]
                    onset = l[9]
                    ph = l[10]
                    w = sub("[5-9]", "0", l[14].replace(" ", "0"))
                    pol = l[16]
                    ar = get_ar(ot, l[:28])
                    try:
                        amp = float(l[33:40])
                    except:
                        if sta in event[ot]: amp = event[ot][sta]["amp"]
                        else: amp = None
                    try:
                        per = float(l[40:45])
                    except:
                        if sta in event[ot]: per = event[ot][sta]["per"]
                        else: per = None
                    if sta not in event[ot]:
                        event[ot][sta] = phase.copy()
                    event[ot][sta].update({"sp":sp,
                                      "%s_onset"%ph[0].upper():onset,
                                      "%s_ph"%ph[0].upper():ph,
                                      "%s_w"%ph[0].upper():w,
                                      "%s_pol"%ph[0].upper():pol,
                                      "%s_ar"%ph[0].upper():ar,
                                      "amp":amp,
                                      "per":per
                                      })
                l = next(f)
            else:
                nDevTT=write_to_hypoel(hypoel_file, event, nDevTT)
                event = {}
                neq+=1
    hypoel_file.close()
    return neq, nDevTT

#___________________SECTION 2: Make "hypoel.sta" station file, "hypoel.prm" velocity file
def mk_staion_vel_file():
    print('+++ Station file  => hypoel.sta')
    print('+++ Velocity file => hypoel.sta')
    sta0 = Read_Nordic_Sta()

    # Write station file
    with open("hypoel.sta", "w") as f:
        for sta in sorted(sta0["STA"].keys(), key=lambda x:(len(x), upper(x), sorted(x))):
            if "*" in sta: continue
            lat = ll.Latitude(sta0["STA"][sta]["LAT"])
            lon = ll.Longitude(sta0["STA"][sta]["LON"])
            elv = sta0["STA"][sta]["ELV"]
            f.write("%-4s%02d%1s%5.2f %03d%1s%5.2f %0004d\n"%(sta, lat.degree, lat.get_hemisphere(), lat.decimal_minute, lon.degree, lon.get_hemisphere(), lon.decimal_minute,	 elv))
            f.write("%-4s*     0     1.00\n"%(sta))
    # Write velocity file
    with open("hypoel.prm", "w") as f:
        for v,z in zip(sta0["VELO"]["Vp"], sta0["VELO"]["Dep"]):
            f.write("VELOCITY             %4.2f %5.2f %4.2f\n"%(v, z, sta0["CNTL"]["VpVs"]))
    return sta0["CNTL"]["X0"], sta0["CNTL"]["X1"], sta0["CNTL"]["VpVs"]

#___________________SECTION 3: Make "default.cfg" parameters file

def mk_def_file(xnear, xfar, vpvs, cent):
    print('+++ Default file  => default.cfg')
    def_vals = """! default configuration file

! vp/sv
reset test          1    %6.4f

! elevation correction
reset test          2    0.0000
reset test          8    0.0000

! starting depth
reset test          5    8.000

! no focal mechanism plot
reset test          7    999.0

! distance weighting:
! beginning iteration, 
! max distance with weight=1,
! min distance with weight=0 (set by test 12 and 46)
reset test         10    1.00000
reset test         11    %8.4f
reset test         12    %8.4f
reset test         46    -5.00000

! calculate vp/vs
reset test         49    1.00000 

! no azimuthal weighting
reset test         13    99999.0

! residual weighting type 1 or truncation weighting
! (only used for at least 6 phases):
! beginning iteration,
! max residual with weight=1
reset test         14    5.00000
reset test         15    1.00000

! no residual weighting type 2 or boxcar weighting
! beginning iteration,
! max residual with weight=0
reset test         16    10.0000
reset test         17    1.00000

! no residual weighting type 3 or Jeffrey's weighting
reset test         18    99999.0

! maximum number of iterations
reset test         21    20.000

! standard error for arrival times with weight code 0
reset test         29   -0.10

! coda duration magnitude
reset test         31    -0.870
reset test         32    2.0000
reset test         33    0.0000
reset test         40    0.0000
magnitude option   3                                             

! locate with S
reset test         38    2.0000

! factor for weights of S and S-P times
reset test         39    0.5000

! station code: the 4-th character does not indicate component (n or e)
reset test         53    0.0
! century
reset test         55    %5.2f
! locate with critical station
reset test         44    0.0
! search for missing stations
missing stations   1

! ouput type:
! summary records
summary option     2

! fixed:
printer option     0
constants noprint  0
compress option    0
tabulation option -4

! PESI
! pesi che si assegnano alle qualita' 1 2 3 dei picking,
! la qualita' migliore (0) e la peggiore (4) sono 1 e 0 rispettivamente
! per gli altri e 1/(peso)**2 (default values 5, 10, 20)
weight option      5.00 10.0 20.0
ignore summary rec 0
blank source             
header option            earthquake location
"""%(vpvs, xnear,xfar, cent)           
    with open('default.cfg','w') as f:
        f.write(def_vals)

############################## RUN
if not os.path.exists("STATION0.HYP"):
    print("+++ STATION0.HYP file was not found, aborting.")
    sys.exit()
nordic_inp = input("\n+++ Input NORDIC file name:\n")
cent = int(input("\n+++ Century [def:20]:\n").replace("", "20"))
devTT = open("deviant_tt.dat", "w")
neq, nDevTT = mk_phase_file(nordic_inp)
xnear, xfar, vpvs = mk_staion_vel_file()
mk_def_file(xnear, xfar, vpvs, cent)
print("\n+++ %d Events converted."%(neq))
print("+++ %d Deviant TravelTime(s) detected."%(nDevTT))
devTT.close()

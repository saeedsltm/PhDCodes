#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
import pandas as pn
from LatLon import lat_lon as ll
import json, os, sys

"""
Script for perforing a selection on hypo71 outputs

Inputs:
- initial location file in NORDIC format,
- hypo71 phase file,
- hypo71 summary file,
- selection parameter file,

Outputs:
- hypo71 phase file including only selected events,
- hypo71 summary file including only selected events.

LogChange:
14-Dec-2021 > init.

"""

# Read selection input file
def readSelectPar():
    selectPar = None
    if not os.path.exists("select.json"):
        print("+++ Could not find selection parameters file!\n+++ Generating template 'selection.json' ...\n+++ Edit 'selection.json' and run again.")
        with open("select.json", "w") as f:
            f.write("""{
        "startTime": "2000-01-01 00:00:00",
        "endTime": "2100-01-01 00:00:00",
        "latMin": 28.00,
        "latMax": 30.00,
        "lonMin": 50.00,
        "lonMax": 52.00,
        "depMin": 0.0,
        "depMax": 100.0,
        "magMin": 0.0,
        "magMax": 9.0,        
        "noPhaseMin":3,
        "noPhaseMax":999,
        "gapMin": 0,
        "gapMax": 250,
        "dMin": 20.0,
        "rmsMin": 0.0,
        "rmsMax": 1.0,
        "erhMin": 0.0,
        "erhMax": 3.0,
        "erzMin": 0.0,
        "erzMax": 5.0
}""")
        sys.exit()
    else:
        print("+++ Reading selection parameters...")
    with open("select.json") as f:
        selectPar = json.load(f)
        print(json.dumps(selectPar, sort_keys=False, indent=2))
        for k,v in selectPar.items():
            try:
                selectPar[k] = dt.strptime(v, "%Y-%m-%d %H:%M:%S")
            except:
                pass
    return selectPar

# Read input files
def getInputFiles():
    hypo71Sum = input("+++ Hypo71 summary file [default:hypo71.out]:\n")
    hypo71Pha = input("+++ Hypo71 input file [default:hypo71.pha]:\n")
    hypInput = input("+++ Nordic input file [default:hyp.out]:\n")
    if not hypo71Sum:
        hypo71Sum = "hypo71.out"
    if not os.path.exists(hypo71Sum):
        print("+++ Could not find hypo71 summary file: {0}.".format(hypo71Sum))
        sys.exit()
    if not hypo71Pha:
        hypo71Pha = "hypo71.pha"
    if not os.path.exists(hypo71Pha):
        print("+++ Could not find hypo71 phase file: {0}.".format(hypo71Pha))
        sys.exit()
    if not hypInput:
        hypInput = "hyp.out"
    if not os.path.exists(hypInput):
        print("+++ Could not find Nordic phase file: {0}.".format(hypInput))
        sys.exit()        
    return hypo71Sum, hypo71Pha, hypInput
    
# Origin-Time parser
def parseOT(l):
    for i in [2, 4, 7, 8, 9, 10, 12, 13, 15, 16]:
        if not l[i].strip():
            l = l[:i]+"0"+l[i+1:]
    try:
        ot = dt.strptime(l[:17], "%y%m%d %H%M %S.%f")
        return ot
    except ValueError:
        return None 

# Coordinate parser
def parseCoordinate(l):
    latDeg = int(l[18:20])
    latMin = float(l[21:26])
    lonDeg = int(l[28:30])
    lonMin = float(l[31:36])
    lat = ll.Latitude(latDeg, latMin).decimal_degree
    lon = ll.Longitude(lonDeg, lonMin).decimal_degree
    return lat, lon

# Read hypocenter line type 1
def readHypLine1(hypInput):
    mags = []
    with open(hypInput) as f:
        for l in f:
            if len(l) == 81 and l[79] == "1":
                try:
                    mag = float(l[72:75])
                except ValueError:
                    mag = None
                mags.append(mag)
    return mags

# Select best event
def select(selectPar, hypo71Sum, hypInput):
    df = pn.DataFrame(columns=["OT", "LAT", "LON", "DEP", "MAG", "NO", "GAP", "DMIN", "RMS", "ERH", "ERZ"])
    mags = readHypLine1(hypInput)
    with open(hypo71Sum) as f:
        next(f)
        badEvents = 0
        for i,l in enumerate(f):
            OT = parseOT(l)
            if OT:
                LAT, LON = parseCoordinate(l)
                DEP = float(l[36:43])
                try:
                    MAG = float(l[47:50])
                except ValueError:
                    MAG = mags[i]
                NO = int(l[50:53])
                GAP = int(l[54:57])
                DMIN = float(l[57:62])
                RMS = float(l[62:67])
                try:
                    ERH = float(l[67:72])
                    ERZ = float(l[72:77])
                except ValueError:
                    ERH, ERZ = None, None
                row = {"OT":OT,
                       "LAT":LAT,
                       "LON":LON,
                       "DEP":DEP,
                       "MAG":MAG,
                       "NO":NO,
                       "GAP":GAP,
                       "DMIN":DMIN,
                       "RMS":RMS,
                       "ERH":ERH,
                       "ERZ":ERZ}
            else:
                print("+++ Event number {0} skipped!".format(i))
                badEvents += 1
            df = df.append(row, ignore_index=True)
    print("+++ Total number of events: {0}, out of {1}.".format(i-badEvents, i))
    # applying conditions
    condOT = (selectPar["startTime"] < df.OT) & (df.OT <= selectPar["endTime"])
    condLAT = (selectPar["latMin"] < df.LAT) & (df.LAT <= selectPar["latMax"])
    condLON = (selectPar["lonMin"] < df.LON) & (df.LON <= selectPar["lonMax"])
    condDEP = (selectPar["depMin"] < df.DEP) & (df.DEP <= selectPar["depMax"])
    condMAG = (selectPar["magMin"] < df.MAG) & (df.MAG <= selectPar["magMax"])
    condNO = (selectPar["noPhaseMin"] < df.NO) & (df.NO <= selectPar["noPhaseMax"])
    condGAP = (selectPar["gapMin"] < df.GAP) & (df.GAP <= selectPar["gapMax"])
    condDMIN = (selectPar["dMin"] >= df.DMIN)
    condRMS = (selectPar["rmsMin"] < df.RMS) & (df.RMS <= selectPar["rmsMax"])
    condERH = (selectPar["erhMin"] < df.ERH) & (df.ERH <= selectPar["erhMax"])
    condERZ = (selectPar["erzMin"] < df.ERZ) & (df.ERZ <= selectPar["erzMax"])
    df = df[(condOT)&(condLAT)&(condLON)&(condDEP)&(condMAG)&(condNO)&(condGAP)&(condDMIN)&(condRMS)&(condERH)&(condERZ)]
    meanRMS = df["RMS"].mean()
    meanERH = df["ERH"].mean()
    meanERZ = df["ERZ"].mean()
    print("+++ Total number of selected events: {0}".format(len(df)))
    print("+++ Mean of RMS={0:3.2f}, ERH={1:5.2f} and ERZ={2:5.2f}".format(meanRMS, meanERH, meanERZ))
    return df

# Write Hypo71 summary file
def writeHypo71Sum(df, hypo71Sum):
    outSum = "_sel.".join(hypo71Sum.split("."))
    with open(outSum, "w") as f:
        f.write("DATE    ORIGIN    LAT N    LONG E    DEPTH    MAG NO GAP DMIN  RMS  ERH  ERZ QM\n")
        for i in df.index:
            lat = ll.Latitude(df["LAT"][i])
            lon = ll.Longitude(df["LON"][i])
            f.write("{ot:17s} {latDeg:2d}-{latMin:05.2f}  {lonDeg:2d}-{lonMin:05.2f} {dep:6.2f}   {mag:3.1f} {no:3d} {gap:3d}{dmin:5.1f}{rms:5.2f}{erh:5.1f}{erz:5.1f}   \n".format(
                ot=df["OT"][i].strftime("%y%m%d %H%M %S.%f")[:17],
                latDeg=int(lat.degree), latMin=lat.decimal_minute,
                lonDeg=int(lon.degree), lonMin=lon.decimal_minute,
                dep=df["DEP"][i],
                mag=df["MAG"][i],
                no=df["NO"][i],
                gap=df["GAP"][i],
                dmin=df["DMIN"][i],
                rms=df["RMS"][i],
                erh=df["ERH"][i],
                erz=df["ERZ"][i],
                ))
    print("+++ New hypo71 summary file was created > '{0}'.".format(outSum))

# Write point coordinates file
def writePoints(df, hypo71Sum):
    outSum = "points_sel.dat"
    with open(outSum, "w") as f:
        f.write("DATE       ORIGIN     LAT    LONG  DEPTH MAG  NO GAP DMIN  RMS  ERH  ERZ\n")
        for i in df.index:
            f.write("{ot:17s} {lat:7.3f} {lon:7.3f} {dep:6.2f} {mag:3.1f} {no:3d} {gap:3d}{dmin:5.1f}{rms:5.2f}{erh:5.1f}{erz:5.1f}   \n".format(
                ot=df["OT"][i].strftime("%y%m%d %H%M %S.%f")[:17],
                lat=ll.Latitude(df["LAT"][i]).decimal_degree,
                lon=ll.Longitude(df["LON"][i]).decimal_degree,
                dep=df["DEP"][i],
                mag=df["MAG"][i],
                no=df["NO"][i],
                gap=df["GAP"][i],
                dmin=df["DMIN"][i],
                rms=df["RMS"][i],
                erh=df["ERH"][i],
                erz=df["ERZ"][i],
                ))
    print("+++ Points coordinate file was created > '{0}'.".format(outSum))

# Write Hypo71 phase file
def writeHypo71Phase(df, hypo71Pha):
    outPha = "_sel.".join(hypo71Pha.split("."))
    with open(hypo71Pha) as f, open(outPha, "w") as g:
        flag = False
        events = [[]]
        numEvents = 0
        for i,l in enumerate(f):
            if len(l) > 20 and l[4] == l[9] == l[14] == l[17] == ".":            
                flag = True
                g.write(l)
                l = next(f)
            if not flag:
                g.write(l)
            if flag:
                while l[:4].strip():
                    events[-1].append(l)
                    l = next(f)
                else:
                    events.append([])
                    numEvents +=1
    events.pop(-1)
    with open(outPha, "a") as f:
        for i in df.index:
            for j in events[i]:
                f.write(j)
            f.write("                 10\n")
    print("+++ New hypo71 phase file was created > '{}'.".format(outPha))

# write NORDIC phase file
def writeNordicPhaseFile(df, nordicPha):
    outPha = "_sel.".join(nordicPha.split("."))
    with open(nordicPha) as f:
        events = [[]]
        numEvents = 0
        for i,l in enumerate(f):
            events[-1].append(l)
            if not l.strip():
                events.append([])
        events.pop(-1)
    with open(outPha, "w") as f:
        for i in df.index:
            for j in events[i]:
                f.write(j)
    print("+++ New nordic phase file was created > '{}'.".format(outPha))

# Run
selectPar = readSelectPar()
hypo71Sum, hypo71Pha, hypInput = getInputFiles()
df = select(selectPar, hypo71Sum, hypInput)
writeHypo71Sum(df, hypo71Sum)
writePoints(df, hypo71Sum)
writeHypo71Phase(df, hypo71Pha)
writeNordicPhaseFile(df, hypInput)


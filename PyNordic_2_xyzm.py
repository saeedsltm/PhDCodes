#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from math import sqrt

# Make a new event entity
def makeNewEventEntity():
    event = {"Line1": [],
             "LineE": [],
             "Line4": [],
             }
    return event

# Calculate root mean square
def getRMS(a):
    ms = 0
    N = len(a)
    for i in range(N):
        ms += a[i]**2
    ms /= N
    rms = sqrt(ms)
    return rms

# Parse line type "1" in NORDIC file
def parseLin1(l):
    for i in [6, 8, 11, 12, 13, 14, 16, 17, 19]:
        if l[i] == " ":
            l = l[:i]+"0"+l[i+1:]
    ot = dt.strptime(l[1:20], "%Y %m%d %H%M %S.%f")
    lat = float(l[24:30])
    lon = float(l[32:38])
    dep = float(l[39:43])
    mag = 0
    return ot, lat, lon, dep, mag

# Parse line type "E" in NORDIC file
def parseLineE(l):
    gap = float(l[5:8])
    ErX = float(l[25:30])
    ErY = float(l[33:38])
    ErZ = float(l[38:43])
    ErH = sqrt(ErX**2 + ErY**2)
    return gap, ErH, ErZ

# Parse line type "4" in NORDIC file
def parseLine4(l, ot):
    staCode = l[:5].strip()
    phase = l[10].upper()
    wt = int(l[14])
    polarity = l[16]
    for i in [18, 19, 20, 21, 23, 24, 26, 27]:
        if l[i] == " ":
            l = l[:i]+"0"+l[i+1:]
        try:
            at = dt.strptime(l[18:28], "%H%M %S.%f")
        except Exception as e:
            if "second" in str(e):
                at = dt.strptime(l[18:22], "%H%M")
                at = at.replace(minute=at.minute+1)
    at = at.replace(year=ot.year, month=ot.month, day=ot.day)
    residual = float(l[63:68])
    distance = float(l[70:75])
    return staCode, phase, wt, polarity, at, residual, distance

# Write to "xyzm" format
def write2xyzm(event, xyzmFile):
    ot, lat, lon, dep, mag = event["Line1"][0]
    ot = ot.strftime("%Y %m %d %H %M %S.%f")[:21]
    gap, erH, erZ = event["LineE"][0]
    nStUsed = len(
        list(set([line4[0] for line4 in event["Line4"] if line4[2] != 4])))
    nPhaseP = len([line4[1] for line4 in event["Line4"]
                  if (line4[1] == "P" and line4[2] != 4)])
    nPhaseS = len([line4[1] for line4 in event["Line4"]
                  if (line4[1] == "S" and line4[2] != 4)])
    minD = min([line4[6] for line4 in event["Line4"] if line4[2] != 4])
    rms = getRMS([line4[5] for line4 in event["Line4"] if line4[2] != 4])
    xyzmFile.write("{lon:6.3f} {lat:6.3f} {dep:5.1f} {mag:4.1f} {nStUsed:7d} {nPhaseP:7d} {nPhaseS:7d} {minD:5.1f} {gap:3.0f} {rms:4.2f} {erH:6.2f} {erZ:6.2f} {ot:s}\n".format(
        lon=lon, lat=lat, dep=dep, mag=mag, nStUsed=nStUsed, nPhaseP=nPhaseP, nPhaseS=nPhaseS, minD=minD, gap=gap, rms=rms, erH=erH, erZ=erZ, ot=ot
    ))

# Convert NORDIC file to "xyzm.dat"
def nordic2xyzm(nordicFile):
    event = makeNewEventEntity()
    with open(nordicFile) as f, open("xyzm.dat", "w") as g:
        g.write("   LON    LAT DEPTH  MAG NSTUSED NPHASEP NPHASES  MIND GAP  RMS    SEH    SEZ YYYY MM DD HH MN  SEC\n")
        for l in f:
            if l.strip() and len(l.strip()) == 79 and l[79] == "1":
                ot, lat, lon, dep, mag = parseLin1(l)
                event["Line1"].append([ot, lat, lon, dep, mag])
            elif l.strip() and len(l.strip()) == 79 and l[79] == "E":
                gap, ErH, ErZ = parseLineE(l)
                event["LineE"].append([gap, ErH, ErZ])
            elif l.strip() and len(l.strip()) == 79 and l[79] in [" ", "4"]:
                staCode, phase, wt, polarity, at, residual, distance = parseLine4(
                    l, ot)
                event["Line4"].append(
                    [staCode, phase, wt, polarity, at, residual, distance])
            elif not l.strip():
                write2xyzm(event, g)
                event = makeNewEventEntity()

# run package
if __name__ == "__main__":
    nordicFile = input("\n+++ Input NORDIC file name:\n")
    nordic2xyzm(nordicFile)

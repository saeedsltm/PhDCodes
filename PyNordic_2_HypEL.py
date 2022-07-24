#!/home/saeed/Programs/miniconda3/bin/python

from obspy import read_events
from LatLon import lat_lon as ll
import os, sys
from json import load
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

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
18-Apr-2021 > Fixed issue when reading magnitude.
23-Dec-2021 > Fixed issue when there is only S phase without corresponding P phase.
16-Jul-2022 > Completly new script with high improvment in excution time.
"""

def upper(s):
    """make the input string uppercase

    Args:
        s (str): input string

    Returns:
        str: output string
    """
    return s.upper()

class Main():
    def __init__(self, nordicInput):
        self.checkFiles(nordicInput)
        self.catalog = self.readCatalogFile(nordicInput)
        self.stationDict = self.readStationFile("STATION0.HYP")
        self.velocityDict = self.readVelocityFile("STATION0.HYP")
        self.hypoellipseDefaultsDict = self.readHypoellipseDefaults()
        
    def checkFiles(self, nordicInput):
        if not os.path.exists(nordicInput) or not os.path.exists("STATION0.HYP"):
            print("+++ input file or STATION0.HYP not found!")
            sys.exit()
    
    def readCatalogFile(self, nordicInput):
        try:
            catalog = read_events(nordicInput)
            return catalog
        except:
            print("+++ obspy could not load input file!")
            sys.exit()
    
    def readHypoellipseDefaults(self):
        """reading "hypoellipse" defaults parameter file
        """
        with open("hypoDefaults.json") as f:
            hypoDefaultsDict = load(f)
        return hypoDefaultsDict
    
    def readVelocityFile(self, stationFile):
        """reading velocity model from "STATION0.HYP" file 

        Args:
            stationFile (str): station file in "NORDIC" format

        Returns:
            (dict): a dictionary contains velocity model
        """
        emptyLines = 0
        velocityModelDict = {"Vp": [], "Z": [], "VpVs": 1.73, "Moho": 46.0}
        with open(stationFile) as f:
            for l in f:
                if not l.strip():
                    emptyLines += 1
                if emptyLines == 2 and l.strip():
                    Vp, Z = [float(x) for x in l.split()[:2]]
                    velocityModelDict["Vp"].append(Vp)
                    velocityModelDict["Z"].append(Z)
                if emptyLines == 2 and len(l) > 20 and l[21] == "N":
                    _, Z = [float(x) for x in l.split()[:2]]
                    velocityModelDict["Moho"] = Z
                if emptyLines == 3 and l.strip():
                    VpVs = float(l[16:20])
                    velocityModelDict["VpVs"] = VpVs
                    break
        return velocityModelDict

    def readStationFile(self, stationFile):
        """read station information from "STATION0.HYP" file

        Args:
            stationFile (str): station file in "NORDIC" format

        Returns:
            dict: a dictionary contains stations information
        """
        emptyLines = 0
        stations = {}
        with open(stationFile) as f:
            for l in f:
                if not l.strip():
                    emptyLines += 1
                if emptyLines == 1 and l.strip():
                    code = l[:6].strip()
                    lat = ll.Latitude(degree=int(
                        l[6:8]), minute=float(l[8:13])).decimal_degree
                    lon = ll.Longitude(degree=int(
                        l[15:17]), minute=float(l[17:22])).decimal_degree
                    elv = float(l[23:27])
                    stations[code] = {"Lat": lat, "Lon": lon, "Elv": elv}
        return stations

    def non2ws(self, inp):
        """Convert None to white space

        Args:
            inp (str): input as a string on None

        Returns:
            str: input or white space
        """
        if type(inp) == type(None):
            return ""
        else:
            return inp
        
    def extractPickInfo(self, pick):
        """Extract information from an obspy.pick

        Args:
            pick (obspy.pick): an obspy pick object

        Returns:
            tuple: pick information contains, stationCode, phase, polarity, arrival, weight
        """
        sta = pick.waveform_id.station_code
        pha = pick.phase_hint[0]
        pol = self.non2ws(pick.polarity)
        time = pick.time
        try:
            wet = pick.extra["nordic_pick_weight"]["value"]
        except:
            wet = "0"
        return sta, pha, pol, time, wet

    def addPick(self, pick, picksDict, phaseType):
        """Add pick information to phase dictionary

        Args:
            pick (obspy.pick): an obspy pick object
            picksDict (dict): a dictionary contains pick information
            phaseType (str): phase type P or S

        Returns:
            dict: an updated dictionary contains pick information
        """
        sta, pha, pol, time, wet = self.extractPickInfo(pick)
        if sta not in picksDict:
            picksDict[sta] = {phaseType:{"pha":pha, "time":time, "pol":pol, "wet":wet}}
        else:
            picksDict[sta].update({phaseType:{"pha":pha, "time":time, "pol":pol, "wet":wet}})
        return picksDict

    def extractDictInfo(self, picksDict, sta, phaseType):
        """Extract pick information from pick dictionary

        Args:
            picksDict (dict): a dictionary contains pick information
            phaseType (str): phase type P or S

        Returns:
            tuple: pick information contains, stationCode, phase, polarity, arrival, weight
        """
        pha = picksDict[sta][phaseType]["pha"]
        time = picksDict[sta][phaseType]["time"]
        wet = picksDict[sta][phaseType]["wet"]
        pol = picksDict[sta][phaseType]["pol"]
        return pha, pol, time, wet

    def computeArrivalS(self, arrivalP, arrivalS):
        """Compute S arrival

        Args:
            arrivalP (time): arrival time P
            arrivalS (_type_): arrival time S

        Returns:
            float: arrival time S, which is seconds after arrival P
        """
        arrivalDiff = arrivalS - arrivalP
        return arrivalP.second + arrivalP.microsecond*1e-6 + arrivalDiff

    def catalog2hypoellipse(self, outFile):
        print("+++ Conversion starts ...")
        nEq = 0
        with open(outFile, "w") as f:
            for event in tqdm(self.catalog):
                picks = event.picks
                picksDict = {}
                for pick in picks:
                    if "P" in pick.phase_hint:
                        picksDict = self.addPick(pick, picksDict, "P")              
                    if "S" in pick.phase_hint:
                        picksDict = self.addPick(pick, picksDict, "S")
                for sta in picksDict:
                    if len(picksDict[sta]) == 1 and "P" in picksDict[sta]:
                        phaP, polP, timeP, wetP = self.extractDictInfo(picksDict, sta, "P")
                        timeP = timeP.strftime("%y%m%d%H%M%S.%f")[:15]
                        fmt = "{sta:4s} {pha:1s}{pol:1s}{wet:1s} {time:15s}                \n"
                        f.write(fmt.format(sta=sta, pha=phaP, pol=polP, wet=wetP, time=timeP))
                    elif len(picksDict[sta]) == 2:
                        phaP, polP, timeP, wetP = self.extractDictInfo(picksDict, sta, "P")
                        phaS, _, timeS, wetS = self.extractDictInfo(picksDict, sta, "S")
                        timeS = self.computeArrivalS(timeP, timeS)
                        timeP = timeP.strftime("%y%m%d%H%M%S.%f")[:15]
                        fmt = "{sta:4s} {phaP:1s}{polP:1s}{wetP:1s} {timeP:15s}       {timeS:5.1f} {phaS:1s} {wetS:1s}\n"
                        f.write(fmt.format(sta=sta, phaP=phaP, polP=polP, wetP=wetP, timeP=timeP, timeS=timeS, phaS=phaS, wetS=wetS))
                f.write("                 10     \n")
                nEq+=1
        print("+++ {nEq:d} events converted.".format(nEq=nEq))

    def station2hypoellipse(self, outFile):
        """convert stations to "hypoellipse" format

        Args:
            stationDict (dict): a dictionary contains stations information
            outFile (str): name of output file which will be saved in
        """
        with open(outFile, "w") as f:
            for sta in sorted(self.stationDict.keys(), key=lambda x: (len(x), upper(x), sorted(x))):
                if "*" in sta:
                    continue
                lat = ll.Latitude(self.stationDict[sta]["Lat"])
                lon = ll.Longitude(self.stationDict[sta]["Lon"])
                elv = self.stationDict[sta]["Elv"]
                f.write("{station:4s}{latDeg:2.0f}{latHemisphere:1s}{latDec:5.2f} {lonDeg:3.0f}{lonHemisphere:1s}{lonDec:5.2f} {elevation:4.0f}\n".format(
                    station=sta, latDeg=lat.degree, latHemisphere=lat.get_hemisphere(), latDec=lat.decimal_minute, lonDeg=lon.degree, lonHemisphere=lon.get_hemisphere(), lonDec=lon.decimal_minute, elevation=elv
                ))
                f.write("{station:4s}*     0     1.00\n".format(station=sta))
        print("+++ Station file was converted.")


    def velocity2hypoellipse(self, outFile):
        """Convert velocity to "hypoellipse" format

        Args:
            velocityDict (dict): a dictionary contains P velocity and Vp/Vs ratio
            outFile (str): name of output file which will be saved in
        """
        with open(outFile, "w") as f:
            for v, z in zip(self.velocityDict["Vp"], self.velocityDict["Z"]):
                f.write("VELOCITY             {Vp:4.2f} {Z:5.2f} {VpVs:4.2f}\n".format(
                    Vp=v, Z=z, VpVs=self.velocityDict["VpVs"]))
        print("+++ Velocity file was converted.")


    def defaults2hypoellipse(self):
        """Creating hypoellipse defaults file

        Args:
            defaultsDict (dict): a dictionary contains hypoellipse defaults
        """
        with open("default.cfg", "w") as f:
            f.write("reset test         1    {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["VpVs"]))
            f.write("reset test         2    {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["PVelocityForElevationCorrection"]))
            f.write("reset test         8    {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["ElevationOfTopOfComputedModels"]))
            f.write("reset test         5    {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["startingDepth"]))
            f.write("reset test         10   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["distanceWeighting"][0]))
            f.write("reset test         11   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["distanceWeighting"][1]))
            f.write("reset test         12   {0:6.1f}\n".format(
                self.hypoellipseDefaultsDict["distanceWeighting"][2]))
            f.write("reset test         21   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["maximumNumberOfIterations"]))
            f.write("reset test         29   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["standardErrorForArrivalTimesWithWeightCode0"]))
            f.write("reset test         38   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["locateWithS"]))
            f.write("reset test         39   {0:6.2f}\n".format(
                self.hypoellipseDefaultsDict["factorForWeightsOfSAndS_PTimes"]))
            f.write("summary option     {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["summaryOption"]))
            f.write("printer option     {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["printerOption"]))
            f.write("constants noprint  {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["constantsNoPrint"]))
            f.write("compress option    {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["compressOption"]))
            f.write("tabulation option  {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["tabulationOption"]))
            f.write("weight option      {0:4.2f} {0:4.2f} {0:4.2f}\n".format(
                self.hypoellipseDefaultsDict["weightOption"][0], self.hypoellipseDefaultsDict["weightOption"][1], self.hypoellipseDefaultsDict["weightOption"][2]))
            f.write("ignore summary rec {0:1.0f}\n".format(
                self.hypoellipseDefaultsDict["ignoreSummaryRec"]))
            f.write("header option      {0:s}\n".format(
                self.hypoellipseDefaultsDict["headerOption"]))
        print("+++ Defaults file was converted.")




if "__main__" == __name__:
    nordicInput = input("+++ Enter input file in NORDIC format:\n")
    myApp = Main(nordicInput)
    myApp.catalog2hypoellipse("hypoellipse.pha")
    myApp.station2hypoellipse("hypoellipse.sta")
    myApp.velocity2hypoellipse("hypoellipse.prm")
    myApp.defaults2hypoellipse()



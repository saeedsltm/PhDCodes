#!/home/saeed/Programs/miniconda3/bin/python

from obspy import UTCDateTime as utc
from numpy import abs, argmax, pi
from obspy.clients.fdsn import Client
import warnings

warnings.filterwarnings("ignore")
client = Client("http://192.168.213.38:8080")

"""
Script for reading amplitude and period and append them to NORDIC file.

INPUT FILES:
- Sfile in NORDIC.
- Seiscomp archive.
- FDSNW service.

OUTPUT FILES:
 - nordicWithAmp.out
 
ChangeLogs:

05-Apr-2021 > Initial.

"""

#___________________SECTION I: Make "hypoel.pha" phase file

# Make string upper case
def upper(s):
    return s.upper()

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
        ot = utc.strptime(l[1:], "%Y %m%d %H%M %S.%f")
    except ValueError:
        ot = utc.strptime(l[1:16]+"00.00", "%Y %m%d %H%M %S.%f")
        ot = ot + 60.0
    if flag_24h: ot = ot + 3600
    return ot

# get waveform data 
def get_waves(ot):
    recLength = 60.0 # record length in s
    t1 = ot
    t2 = ot + recLength
    st = client.get_waveforms(network="*", station="*", location="*", channel="?HN", starttime=t1, endtime=t2, attach_response=True)
    paz_wa = {"sensitivity": 2800, "zeros": [0j], "gain": 1, "poles": [-6.2832 - 4.7124j, -6.2832 + 4.7124j]}
    pre_filt = (0.005, 0.006, 20.0, 25.0)
    for tr in st:
        paz = {"gain": tr.meta.response.get_paz().normalization_factor,
              "poles": tr.meta.response.get_paz().poles,
              "sensitivity": tr.meta.response.instrument_sensitivity.value,
              "zeros": tr.meta.response.get_paz().zeros}
        tr.taper(.05)
        tr.simulate(paz, paz_simulate=paz_wa, water_level=10, pre_filt=pre_filt)
    return st

# read amplitude and period
def get_amp(st, station, Sar):
    trimLength = 2 # seconds for triming wave before and after S arival time
    try:
        tr = st.select(station=station, component="N")[0]
        tr1 = tr.copy()
        tr2 = tr.copy()    	
        # Cut waveform around S arrival
        tr1 = tr1.trim(Sar-trimLength, Sar+trimLength)
        # Found maximum amplitude
        maxindex = argmax(abs(tr1.data))
        # Found start and end time around maximum and cut waveform
        t1 = tr1.stats.starttime + (maxindex * tr1.stats.delta) - .25
        t2 = tr1.stats.starttime + (maxindex * tr1.stats.delta) + .25
        tr2 = tr2.trim(t1, t2)
        # Found maximum peack to peack amplitude and its period
        amp_max, amp_max_ind = tr2.data.max(), tr2.data.argmax()
        amp_min, amp_min_ind = tr2.data.min(), tr2.data.argmin()
        per = abs(amp_max_ind - amp_min_ind) * tr2.stats.delta
        # Convert meter to nano-meter
        amp = (amp_max - amp_min)*1e9 
        return amp, per
    except:
        return None, None
    
# Get arrival time
def get_ar(ot, l):
    for i in [18,19,20,21,23,24,26,27]:
        if not l[i].strip():
            l = l[:i]+"0"+l[i+1:]
    flag_24h = False # if hour = 24, one day will be added to datetime
    if l[18:20] == "24": 
        flag_24h = True
        l = l[:18]+"23"+l[20:]
    try:
        ar = utc.strptime(l[18:28], "%H%M %S.%f")
        if flag_24h: ar = ar + 3600
    except ValueError:
        ar = utc.strptime(l[18:23]+"00.00", "%H%M %S.%f")
        ar = ar + 60.0
    ar = ar.replace(year=ot.year, month=ot.month, day=ot.day)
    return ar
            
# Make hypoellipse arivaltime file
def read_phase_file(nordic_inp):
    vpvs=1.79
    neq=0
    event = {}
    with open(nordic_inp) as f, open("nordicWithAmp.out", "w") as g:
        for l in f:
            while l.strip():
                g.write(l)
                if len(l) == 81 and l[79] == "1":
                    ot = get_ot(l[:20])
                    event[ot.datetime] = {}
                    st = get_waves(ot)
                    print("+++ Working on: %s"%(ot))
                if l[79] == " ":
                    sta = l[:5].strip()
                    sp = l[6:9]
                    onset = l[9]
                    ph = l[10]
                    w = l[14].replace(" ", "0")
                    pol = l[16]
                    ar = get_ar(ot, l[:28])
                    amp, per = None, None
                    if ph == "P":
                        Sar = ar + (ar - ot) * vpvs
                        amp, per = get_amp(st, sta, Sar)
                    if amp and per:
                        l = l[:7]+"N  IAML "+l[15:33]+"%.1E"%(amp)+"%5.2f"%(per)+"                         "+l[70:]
                        g.write(l)
                l = next(f)
            else:
                event = {}
                neq+=1
                g.write("\n")
    return neq

# Run
inp = input("\n+++ NORDIC input file:\n")
read_phase_file(inp)

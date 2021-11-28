#!/home/saeed/Programs/miniconda3/bin/python

from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy import read_events
from obspy.geodetics.base import degrees2kilometers as d2k
from obspy.core.event.magnitude import Magnitude
from obspy.core.event.origin import OriginUncertainty
from math import log10
import warnings
import os
warnings.filterwarnings("ignore")

"""
Script for estimating magnitude and append to NORDIC file.

INPUT FILES:
- Sfile in NORDIC.
- Seiscomp archive.
- FDSNW service.

OUTPUT FILES:
 - {fileName}_fin.out
 
ChangeLogs:

15-Nov-2021 > Initial.

"""

client = Client("http://localhost:8080")
ou = OriginUncertainty()
ou.min_horizontal_uncertainty = 0
ou.max_horizontal_uncertainty = 0
ou.azimuth_max_horizontal_uncertainty = 0
ou.preferred_description='uncertainty ellipse'

# User defined parameters
pre_filt = [0.001, 0.005, 45, 50]
vpvs = 1.81
s_half_time = 5.0
a = 0.011 # 0.018
b = 2.170 # 2.170 
# WoodAnderson Response
paz_wa = {'sensitivity': 2800, 'zeros': [0j], 'gain': 1,
          'poles': [-6.2832 - 4.7124j, -6.2832 + 4.7124j]}
# Read events sfile
inp = input("\n+++ Enter NORDIC file:\n")
out = "{0}_fin.out".format(inp.split(".")[0])
events = read_events(inp)
# Loop over events
for i,event in enumerate(events):
    print("Progress {0:2.1f}%".format(i/len(events)*100.))
    if not event.preferred_origin().origin_uncertainty: event.preferred_origin().origin_uncertainty = ou
    preferred_origin = event.preferred_origin()
    start_time = preferred_origin.time
    st = client.get_waveforms("*", "*", "", "?H?", start_time, start_time + 80, attach_response=True)    
    st.remove_response(output="VEL", zero_mean=True, taper=True, pre_filt=pre_filt)
    st.simulate(paz_simulate=paz_wa, water_level=10)
    M = []
    for pick in event.picks:
        if "P" in pick.phase_hint.upper():
            station_code = pick.waveform_id.station_code
            pick_time = pick.time
            estim_s_time = start_time + (pick_time - start_time) * vpvs
            traces = st.select(station=station_code)
            traces.trim(estim_s_time-s_half_time, estim_s_time+s_half_time)
            epi_dist = [arrival.distance for arrival in preferred_origin.arrivals if arrival.pick_id == pick.resource_id][0]
            try:
                if epi_dist:
                    tr_n = traces.select(component="N")[0]
                    ampl_n = max(abs(tr_n.data))
                    tr_e = traces.select(component="E")[0]
                    ampl_e = max(abs(tr_e.data))
                    ampl = max(ampl_n, ampl_e)
                    ml = log10(ampl * 1000) + a * d2k(epi_dist) + b
                    M.append(ml)
##                    print("Station={0}, Dis={1}, ML={2}, M={3}".format(station_code, epi_dist, ml, sum(M)/len(M)))
            except IndexError:
                pass
    Mag = Magnitude()
    Mag.mag = sum(M)/len(M)
    Mag.magnitude_type="ML"
    Mag.origin_id = preferred_origin.resource_id
    Mag.creation_info = preferred_origin.creation_info
    event.magnitudes = [Mag]
events.write(out, format="NORDIC")
with open(out) as f, open("tmp.out", "w") as g:
    for l in f:
        if len(l)> 79 and l[79] == "1":
            l = l[:56]+"                "+l[56:63]+l[79:]
        g.write(l)
os.rename("tmp.out", out)
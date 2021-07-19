#!/home/saeed/Programs/miniconda3/bin/python

from obspy.clients.fdsn import Client
from obspy import UTCDateTime as utc
from pathlib import Path
from shutil import make_archive
import warnings
import os, sys
warnings.filterwarnings("ignore")

# Convert seiscomp weight to seisan
wet_map = {1:0, 0:4}

# Rename P and S phases to Pg/Pn and Sg according to epicentral distance
def RenamePhase(pha, dis, cross_dis=160):
    if dis < cross_dis:
        pha = pha+"g"
    else:
        pha = pha+"n"
    pha = pha.replace("Sn", "S")
    return pha

# Get phase info
def get_phase(eventID):
    # Read event info and arrival phases
    cmd3 = "seiscomp exec scbulletin -3 -e -k -E %s -d mysql://sysop:sysop@localhost/seiscomp > tmp.dat"%(eventID)
    os.system(cmd3)
    phases = []
    amplitudes = []
    with open("tmp.dat") as f:
        for line in f:
            # Read event information
            if "Date" in line:
                ot_date = utc.strptime(line.split()[1], "%Y-%m-%d")
            if "Time" in line:
                ot_time = utc.strptime(line.split()[1], "%H:%M:%S.%f")
                ot = ot_date.replace(hour=ot_time.hour, minute=ot_time.minute, second=ot_time.second, microsecond=ot_time.microsecond)
            if "Latitude" in line:
                lat = float(line.split()[1])
                lat_err = float(line.split()[-2])
            if "Longitude" in line:
                lon = float(line.split()[1])
                lon_err = float(line.split()[-2])
            if "Depth" in line:
                dep = float(line.split()[1])
                try:
                    dep_err = float(line.split()[-2])
                except ValueError:
                    dep_err = 999
            if "Agency" in line:
                agency = "SC3"
            if "Residual RMS" in line:
                rms = float(line.split()[2])
            if "Azimuthal gap" in line:
                gap = float(line.split()[2])
            if "preferred" in line:
                mag = float(line.split()[1])            
            # Read phase information
            if "Phase arrivals" in line:
                n_used_pha = int(line.split()[0])
                line = next(f)
                line = next(f)
                while line.strip():
                    l = line.split()
                    sta = l[0]
                    dis = float(l[2])
                    azi = float(l[3])
                    pha = RenamePhase(l[4], dis, cross_dis=200)
                    art = utc.strptime(l[5], "%H:%M:%S.%f")
                    art = ot_date.replace(hour=art.hour, minute=art.minute, second=art.second, microsecond=art.microsecond)
                    res = float(l[6])
                    wet = wet_map[float(l[8])]
                    phases.append([sta, pha, wet, art, res, dis, azi])
                    line = next(f)
            # Read amplitude information
            if "Station magnitudes" in line:
                line = next(f)
                line = next(f)
                while line.strip():
                    l = line.split()
                    sta = l[0]
                    dis = float(l[2])
                    azi = float(l[3])
                    amp = float(l[7])
                    try:
                        per = float(l[8])
                    except IndexError:
                        per = 1
                    if per == 0: per = 1.0
                    amplitudes.append([sta, dis, azi, amp, per])
                    line = next(f)
    return ot, lat, lat_err, lon, lon_err, dep, dep_err, agency, rms, gap, mag, n_used_pha, phases, amplitudes

# Get amplitudes info
def get_amplitude(eventID, prefered_amplitudes):
    # Read amplitiude information
    cmd1 = "seiscomp exec scbulletin -1 -e -k -E %s -d mysql://sysop:sysop@localhost/seiscomp > tmp.dat"%(eventID)
    os.system(cmd1)
    amplitudes = []
    stations = [prefered_amplitude[0] for prefered_amplitude in prefered_amplitudes]
    with open("tmp.dat") as f:
        for line in f:
            if "Stat  Net" in line:
                line = next(f)
                while line.strip():
                    l = line.split()
                    sta = l[0]
                    if sta in stations:
                        indx = stations.index(sta)
                        art = utc.strptime("T".join(l[2:4]), "%y/%m/%dT%H:%M:%S.%f")
                        if float(l[4]):
                            amp = float(l[4])
                        else:
                            amp = prefered_amplitudes[indx][3]
                        if float(l[5]):
                            per = float(l[5])
                        else:
                            per = prefered_amplitudes[indx][4]
                        dis = float(l[7])
                        azi = float(l[8])
                        amplitudes.append([sta, art, amp, per, dis, azi])
                    line = next(f)
    return amplitudes

# Get waveform info
def get_wave(ot):
    # Get waveform
    client = Client("http://localhost:8080")
    start_time = ot - 60
    end_time = ot + 300
    st = client.get_waveforms(network="BI", station="*", location="*", channel="*", starttime=start_time, endtime=end_time)
    # Rename channel from SH -> BH
    for tr in st:
        tr.stats.channel = tr.stats.channel.replace("SH", "BH")
    return st

# Write sfile info
def write_sfile(ot, lat, lat_err, lon, lon_err, dep, dep_err, agency, rms, gap, mag, n_used_pha, n_ava_sta, phases, amplitudes):
    rea_dir = os.path.join(os.environ["SEISAN_TOP"], "REA", "BIN__", str(ot.year), "%02d"%ot.month)
    if not os.path.exists(rea_dir):
        Path(rea_dir).mkdir(parents=True, exist_ok=True)
    sfile = ot.strftime(os.path.join(rea_dir, "%d-%H%M-%SL.S%Y%m"))
    wave_name = ot.strftime("%Y-%m-%d-%H%M-%S") + ".BIN__%003d"%(n_ava_sta)
    ID = ot.strftime("%Y%m%d%H%M%S")
    action = "ACTION:NEW " + utc.now().strftime("%y-%m-%d %H:%M") + " OP:SEIS STATUS:"
    with open(sfile, "w") as f:
        # Line 1
        #        x  Yx  m  dx  H  Mx    Sx  Lx  lat  lon     xxagnPus  rms  mg1typMag  mg2typMag  mg3typMagTTL                                            
        f.write(" %4d %02d%02d %02d%02d %4.1f %1s %7.3f%8.3f%5.1f  %3s%3d%4.1f%4.1f%1s%3s                %1s\n"%(ot.year, ot.month, ot.day, ot.hour, ot.minute, ot.second + ot.microsecond*1e-6, "L", lat, lon, dep, agency, n_used_pha, rms, mag, "L", agency, "1"))
        # Line E
        f.write(" GAP=%3d      %6.2f    %6.1f  %6.1f%5.1f                                    %1s\n"%(gap, 0, lat_err, lon_err, dep_err, "E"))
        # Line 6
        f.write(" %s                                                   %1s\n"%(wave_name, "6"))
        # Line I
        f.write(" %s               ID:%s     %1s\n"%(action, ID, "I"))
        # Line 7
        f.write(" STAT SP IPHASW D HRMM SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ%1s\n"%(7))
        # Line 4
        ######## phase
        for phase in phases:
            sta, pha, wet, art, res, dis, azi = phase
            f.write(" %-5s%1s%1s %1s%-4s%1d %1s %02d%02d%6.2f                                   %5.1f%2s%5.0f %3d%1s\n"%(sta, "B", "Z", "E", pha, wet, " ", art.hour, art.minute, art.second + art.microsecond*1e-6, res, " ", dis, azi, "4"))
        ######## amplitude
        for amplitude in amplitudes:
            sta, art, amp, per, dis, azi = amplitude
            pha = "IAML"
            res = 0
            f.write(" %-5s%1s%1s %1s%4s%1s %1s %02d%02d%6.2f %4s%7.1f %4.2f                         %5.0f %3d%1s\n"%(sta, "B", "Z", " ", pha, " ", " ", art.hour, art.minute, art.second + art.microsecond*1e-6, " ", amp*1e6/2080, per, dis, azi, "4"))

# Save waveform
def write_wave(ot, st, agency):
    wav_dir = os.path.join(os.environ["SEISAN_TOP"], "WAV", "BIN__", str(ot.year), "%02d"%ot.month)
    if not os.path.exists(wav_dir):
        Path(wav_dir).mkdir(parents=True, exist_ok=True)    
    wave_name = ot.strftime("%Y-%m-%d-%H%M-%S") + ".%s__%003d"%(agency, len(st))
    wave = os.path.join(wav_dir, wave_name)
    st.write(wave, format="MSEED")
    zip_name = os.path.join(wav_dir, ot.strftime("%Y-%m-%d-%H%M-%S"))
    make_archive(zip_name, 'zip', wav_dir, wave_name)
    os.remove(wave)

# Convert Seiscomp to Seisan
def sc2sei(eventID, before_ot=60, after_ot=300):
    ot, lat, lat_err, lon, lon_err, dep, dep_err, agency, rms, gap, mag, n_used_pha, phases, prefered_amplitudes = get_phase(eventID)
    amplitudes = get_amplitude(eventID, prefered_amplitudes)
    #st = get_wave(ot)
    n_ava_sta = 0
    write_sfile(ot, lat, lat_err, lon, lon_err, dep, dep_err, agency, rms, gap, mag, n_used_pha, n_ava_sta, phases, amplitudes)
    #write_wave(ot, st, agency)
    os.remove("tmp.dat")

eventID = sys.argv[1]
sc2sei(eventID=eventID, before_ot=60, after_ot=300)

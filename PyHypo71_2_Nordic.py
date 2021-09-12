#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from LatLon import lat_lon as ll
import os

"""

Script for converting Hypo71 input file to NORDIC.

Outputs: 1- nordic.out 2- STATION0.HYP

ChangeLogs:

07-Jan-2021 > Created.

"""

# Input file
inp = input('\n\nInput HYPO71 file name?\n\n')


# File for reporting miss corrected phase time
report_f = open('report.log', 'w')

# seisan resets
RESET ="""RESET TEST(02)=500.0
RESET TEST(07)=-3.0
RESET TEST(08)=2.6
RESET TEST(09)=0.001
RESET TEST(11)=99.0
RESET TEST(13)=5.0
RESET TEST(34)=1.5
RESET TEST(35)=2.5
RESET TEST(36)=0.0
RESET TEST(41)=20000.0
RESET TEST(43)=5.0
RESET TEST(51)=3.6
RESET TEST(50)=1.0
RESET TEST(56)= 1.0
RESET TEST(58)= 99990.0
RESET TEST(40)=0.0
RESET TEST(60)=0.0
RESET TEST(71)=1.0
RESET TEST(75)=1.0
RESET TEST(76)=0.910
RESET TEST(77)=0.00087
RESET TEST(78)=-1.67
RESET TEST(79)=1.0
RESET TEST(80)=3.0
RESET TEST(81)=1.0
RESET TEST(82)=1.0
RESET TEST(83)=1.0
RESET TEST(88)=1.0
RESET TEST(85)=0.1
RESET TEST(91)=0.1

"""

# File for saving STATION0.HYP
with open("STATION0.HYP", "w") as f: f.write(RESET)


# Inserting station info into STATION0.HYP
def get_station(l):
    with open("STATION0.HYP", "a") as f: f.write(l)

# Inserting velocity model info into STATION0.HYP
def get_model(l):
    vp = float(l.split()[0])
    z = float(l.split()[1])
    with open("STATION0.HYP", "a") as f:
        f.write("  %4.2f     %4.1f              \n"%(vp, z))

# Inserting controle parameters info into STATION0.HYP
def get_cnt_line(l):
    trial_d = float(l[:5])
    x_near = float(l[5:10])
    x_far = float(l[10:15])
    vpvs = float(l[15:20])
    with open("STATION0.HYP", "a") as f:
        f.write("%5.0f%5.0f%5.0f%5.2f"%(trial_d, x_near, x_far, vpvs))
      
# Get arrival times
def get_dt(l):
    for i in [0,2,4,6,7,8,9,10,11,13,14]:
        if i != 12 and l[i] == " ": l = l[:i]+"0"+l[i+1:]
    l = l[:12]+l[12].replace(" ", ".")+l[13:]
    try:
        DateTime = dt.strptime(l, "%y%m%d%H%M%S.%f")
    except ValueError: return None
    return DateTime

# Get phase info
def get_phase(l, tmp_dic):
    sta = l[0:4]
    pha = l[4:6].replace("  ","EP").upper()
    pol = l[6:7]
    wt  = l[7:8]
    try:
        tp = get_dt(l[9:24])
    except ValueError:
        with open(report_f.name, 'a') as f:
            f.write('%s > Bad value for date/time [ignored].\n'%(l.strip()))
        return None, tmp_dic
    if sta not in tmp_dic.keys():
        tmp_dic[sta] = {'P':{'pol':' ', 'wt':' ', 'pha':None, 'tp':None},
                        'S':{'pol':' ', 'wt':' ', 'pha':None, 'ts':None}}
    tmp_dic[sta]['P']['pha'] = pha
    tmp_dic[sta]['P']['pol'] = pol
    tmp_dic[sta]['P']['wt']  = wt
    tmp_dic[sta]['P']['tp']  = tp
    if len(l) >= 37 and l[37:38].upper() == 'S':
        tmp_dic[sta]['S']['pha'] = 'ES'
        tmp_dic[sta]['S']['pol'] = ' '
        try:
            tmp_dic[sta]['S']['wt'] = l[39]
        except IndexError:
            tmp_dic[sta]['S']['wt'] = ' '
        y_S = tp.year
        m_S = tp.month
        d_S = tp.day
        H_S = tp.hour
        M_S = tp.minute
        S_S = float(l[31:36])
        if S_S>=60.0:
            S_S = S_S-60.0
            M_S+=1
        if M_S>=60:
            M_S=60-M_S
            H_S+=1
        if H_S>=24:
            H_S=24-H_S
            d_S+=1        
        MS_S = int((S_S - int(S_S))*1e6)
        S_S  = int(S_S)
        try:
            ts = dt(y_S,m_S,d_S,H_S,M_S,S_S,MS_S)
        except ValueError:
            with open(report_f.name, 'a') as f:
                f.write('%s > Bad value for date/time [ignored].\n'%(l.strip()))
            return None, tmp_dic
        tmp_dic[sta]['S']['ts'] = ts
    return tp, tmp_dic

# Read phase file
data_dic = {}
tmp_dic = {}
eq_id = 0
with open(inp) as f:
    for l in f:
        # extract stations
        if len(l) > 27:
            c1 = l[13]; c2 = l[22]
            while c1 == "N" and c2 == "E":
                get_station(l)
                l = next(f)
                if len(l) > 27: c1 = l[13]; c2 = l[22]
                else:
                    with open("STATION0.HYP", "a") as ff: ff.write("\n")
                    break
        # extract velocity model
        if len(l) > 11:
            c1 = l[3]; c2 = l[10]
            while c1 == "." and c2 == ".":
                get_model(l)
                l = next(f)
                if len(l) > 11: c1 = l[3]; c2 = l[10]
                else:
                    with open("STATION0.HYP", "a") as ff: ff.write("\n")
                    break
        # extract Xnear, Xfar, vpvs
        if len(l) > 17:
            c1 = l[4]; c2 = l[9]; c3 = l[17]
            while c1 == "." and c2 == "." and c3 == ".":
                get_cnt_line(l)
                l = next(f)
                if len(l) > 17: c1 = l[4]; c2 = l[9]; c3 = l[17]
                else: break
        # extract phase data
        if len(l) > 23:
            c1 = get_dt(l[9:24])
            while c1:
                tp, tmp_dic = get_phase(l, tmp_dic)
                l = next(f)
                if len(l) > 23 and get_dt(l[9:24]):
                    c1 = get_dt(l[9:24])
                else:
                    data_dic[eq_id] = tmp_dic
                    eq_id+=1
                    tmp_dic = {}
                    break

# add profile name at the ent of STATION0.HYP
with open("STATION0.HYP", "a") as ff: ff.write("\nH71")

# Write into NORDIC format
fid = open('nordic.out', 'w')

for evt in sorted(data_dic):
    if not data_dic[evt].keys(): continue
    hd    = data_dic[evt][list(data_dic[evt].keys())[0]]['P']['tp']
    line1 = hd.strftime(' %Y %m%d %H%M %S.0 L                                                         1\n')
    line7 = ' STAT SP IPHASW D HRMN SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ7\n'
    fid.write(line1)
    fid.write(line7)
    for sta in data_dic[evt]:
        pha   = data_dic[evt][sta]['P']['pha']
        wt    = data_dic[evt][sta]['P']['wt']
        pol   = data_dic[evt][sta]['P']['pol']            
        hd    = data_dic[evt][sta]['P']['tp']
        t     = '%02d%02d %02d.%02d                                                    '%(hd.hour,hd.minute,hd.second,hd.microsecond*1e-4)
        line4 = ' '+sta+' SZ EP'+'   '+wt+' '+pol+' '+t+'\n'
        fid.write(line4)
        pha   = data_dic[evt][sta]['S']['pha']
        wt    = data_dic[evt][sta]['S']['wt']
        pol   = data_dic[evt][sta]['S']['pol']            
        hd    = data_dic[evt][sta]['S']['ts']
        if hd:
            t    = '%02d%02d %02d.%02d                                                    '%(hd.hour,hd.minute,hd.second,hd.microsecond*1e-4)
            line4 = ' '+sta+' SN ES'+'   '+wt+' '+pol+' '+t+'\n'
            fid.write(line4)
    fid.write('\n')
fid.close()

print('\n+++ Total Number of EQs =',len(data_dic))
print("+++ Check 'report.dat' file for bad phase/event.")

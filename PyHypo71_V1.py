#!/home/saeed/Programs/miniconda3/bin/python

import os
import sys
from PySTA0RW import Read_Nordic_Sta
from LatLon import lat_lon as ll
import numpy as np
from numpy import mean
# ~ from string import upper
from glob import glob
from datetime import datetime as dt
from LatLon import lat_lon as ll
from random import gammavariate, choice, seed

"""

Script for running hypo71PC module.

ChangeLogs:

25-Jul-2017 > Initial.

"""

#_______________SIMULATE MAGNITUDES

def get_mag():

    seed(1)
    mag = [gammavariate(2,2) for _ in range(500)]
    mag = [_/max(mag) for _ in mag]
    mag = [_*5.0 for _ in mag]

    return mag

random_mag = get_mag()

#_______________CONVERT HYPO71.OUT TO xyzm.dat

def write_xyzm(hypo71_out):

    with open(hypo71_out) as f, open("xyzm.dat", "w") as g:

        g.write('     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC\n')

        next(f)
        
        for i,l in enumerate(f):

            ot = l[:17]
            for i in [0,1,2,7,9]:
                if not ot[i].strip():
                    ot = ot[:i]+"0"+ot[i+1:]
            if float(l[12:17])>=60.0: ot = ot[:12]+"59.99"
            try:
                ot = dt.strptime(ot, "%y%m%d %H%M %S.%f")
            except ValueError:
                print("Error while converting event in xyzm format >> ",l)
                continue
            ort = ot.strftime('  %Y %m %d %H %M %S.%f')[:24]

            lat = ll.Latitude(degree=float(l[18:20]), minute=float(l[21:26])).decimal_degree
            lon = ll.Longitude(degree=float(l[28:30]), minute=float(l[31:36])).decimal_degree
            dep = float(l[38:43])
            mag = choice(random_mag)
            nop = float(l[51:53])
            nst = nop
            mds = float(l[53:56])
            gap = float(l[57:60])
            rms = float(l[63:67])
            try:
                seh = float(l[68:72])
            except ValueError: seh = 99.9
            try:
                sez = float(l[73:77])
            except ValueError: sez = 99.9
            

            fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
            fmt = fmt + ort+'\n'

            # lon lat dep mag phusd no_st mds gap rms seh sez

            g.write(fmt%(lon, lat, dep, mag, nop, nst, mds, gap, rms, seh, sez))
            
#_______________PREPARE HYPO71 INPUTS AND RUN

def add_phase_file(hypo71_inp, hypo71pha):

    with open(hypo71_inp) as f, open(hypo71pha, "a") as g:

        for l in f:

            if l.strip() and l[5].upper()=="P":

                for i in [9, 11, 13, 15, 17, 19]:

                    if not l[i].strip():

                        l = l[:i]+"0"+l[i+1:]
                    if l[19:24]=="0    ": l = l[:19]+"00.00"+l[24:]
            g.write(l)

#_______________RUN HYPO71 WITH STATION CORRECTION

def do_sta_corr(pha_file, prt_file):

    print("+++ Running Hypo71 with station correction...\n")

    station_corr = {}
    output = "hypo71_.pha"

    with open(prt_file) as f:

        flag = False

        for l in f:

            if "STATION   NRES" in l:

                flag = True
                l = next(f)

            if flag:

                sta_code = l[4:9].strip()
                num_p = float(l[8:15])
                avr_res = float(l[25:31])
                if num_p: station_corr[sta_code] = avr_res

    with open(pha_file) as f, open(output, "w") as g:

        for l in f:

            if l[:6].strip() and l[2:6].strip() in station_corr.keys():

                res = "%5.2f"%(station_corr[l[2:6].strip()])
                res = res.replace("-0.", " -.")
                res = res.replace("0.", " .")
                l = "%27s%s\n"%(l[:27], res)

            g.write(l)

    os.rename(output, pha_file)

#_______________HYPO71 MAIN
        
def run_hyp71(hypo71_inp='norhyp.out', nordic_sta_file='STATION0.HYP', vel_model=None, used_STA0_VEL=True, run_id='hypo71'):

    trial_dep = float(input("\n+++ Trial Depth [km]:\n"))
    misfit_rms = []
    used_sta   = []
    nordic_sta = Read_Nordic_Sta(nordic_sta_file)
    hypo71pha  = '%s.pha'%(run_id)
    hypo71inp  = '%s.inp'%(run_id)
    hypo71prt  = '%s.prt'%(run_id)
    hypo71out  = '%s.out'%(run_id)

    if used_STA0_VEL:

        vel_model = np.array([nordic_sta['VELO']['Vp'],
                              nordic_sta['VELO']['Dep']]).T

    with open(hypo71_inp) as f:

        for l in f:

            if l[:4].strip(): used_sta.append(l[:4].strip())

    #_______________REMOVE NOT USED STATION FROM STA-LIST

    used_sta = list(set(used_sta))
    tmp      = nordic_sta.copy()

    for sta in list(nordic_sta['STA']):

        if sta not in used_sta:

            del tmp['STA'][sta]

    nordic_sta = tmp.copy()

    resets = ['RESET TEST(01)=0.1',
              'RESET TEST(02)=10.',
              'RESET TEST(03)=1.5',
              'RESET TEST(04)=0.05',
              'RESET TEST(05)=5.',
              'RESET TEST(06)=4.',
              'RESET TEST(11)=40.']     

    #-Generate HYP71 phase file (resets+model+phase)

    with open(hypo71pha, 'w') as f:

        f.write('HEAD                     GENERATED USING "PyHypo71" CODE\n')

        for r in resets:

            f.write(r+'\n')

        f.write('\n')
                
        for sta in sorted(nordic_sta['STA'].keys(),key=lambda x:(len(x),x.upper(),sorted(x))):

            lon = ll.Longitude(nordic_sta['STA'][sta]['LON'])
            lat = ll.Latitude(nordic_sta['STA'][sta]['LAT'])
            elv = nordic_sta['STA'][sta]['ELV']
            pcr = nordic_sta['STA'][sta]['PCR']
            scr = nordic_sta['STA'][sta]['SCR']

            if pcr!=None and scr!=None:
                
                f.write('  %-4s%2d%5.2f%1s %2d%5.2f%1s%4d %+5.2f %+5.2f\n'%(sta,
                                                                          lat.degree,lat.decimal_minute,lat.get_hemisphere(),
                                                                          lon.degree,lon.decimal_minute,lon.get_hemisphere(),
                                                                          elv, pcr,scr))
            elif pcr!=None and scr==None:
                
                f.write('  %-4s%2d%5.2f%1s %2d%5.2f%1s%4d %+5.2f\n'%(sta,
                                                                   lat.degree,lat.decimal_minute,lat.get_hemisphere(),
                                                                   lon.degree,lon.decimal_minute,lon.get_hemisphere(),
                                                                   elv, pcr))
            elif pcr==None and scr!=None:
                
                f.write('  %-4s%2d%5.2f%1s %2d%5.2f%1s%4d %5s %+5.2f\n'%(sta,
                                                                          lat.degree,lat.decimal_minute,lat.get_hemisphere(),
                                                                          lon.degree,lon.decimal_minute,lon.get_hemisphere(),
                                                                          elv, '     ',scr))
            elif pcr==None and scr==None:
                
                f.write('  %-4s%2d%5.2f%1s %2d%5.2f%1s%4d\n'%(sta,
                                                            lat.degree,lat.decimal_minute,lat.get_hemisphere(),
                                                            lon.degree,lon.decimal_minute,lon.get_hemisphere(),
                                                            elv))
        f.write('\n')
            
        for v,d in zip(vel_model[:,0], vel_model[:,1]):

            f.write('  %5.3f %6.3f\n'%(v,d))

        f.write('\n')
        f.write('  %2.0f  75. 400.%5.2f    4    0    0    1    1    0    0 0111\n'%(trial_dep, nordic_sta['CNTL']['VpVs']))

    #os.system('cat %s >> %s'%(hypo71_inp,hypo71pha))
    add_phase_file(hypo71_inp, hypo71pha)

    with open('%s'%(hypo71inp),'w') as f:

        f.write('%s\n%s\n%s\n\n\n\n'%(hypo71pha,hypo71prt,hypo71out))

    #-Run HYP71, AND THEN WITH STATION CORRECTION
    print("\n+++ Running Hypo71...")
    cmd = 'hypo71 < %s > /dev/null'%(hypo71inp)
    os.system(cmd)

    do_sta_corr(hypo71pha, hypo71prt)
    cmd = 'hypo71 < %s > /dev/null'%(hypo71inp)
    os.system(cmd)
    
    cc=0
    with open(hypo71out) as f:

        for l in f:

            # get RMS
            if cc and l[62:67].strip() and '*' not in l: misfit_rms.append(float(l[62:67]))
            cc+=1

#    for i in [hypo71pha,hypo71inp]:
#
#        if os.path.exists(i): os.remove(i)
            
    write_xyzm(hypo71out)
    return mean(misfit_rms)

#___________________RUN/EXAMPLE

if __name__ == "__main__":
    
    if len(sys.argv) < 2: print("\n\n+++ Usage: PyHypo71.py hypo71_inp_phase\n")
    else: run_hyp71(sys.argv[1])

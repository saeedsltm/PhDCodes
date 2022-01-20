#!/home/saeed/Programs/miniconda3/bin/python

import os
import sys
from LatLon import lat_lon as ll
from numpy import array, genfromtxt, sqrt
from datetime import datetime as dt
from glob import glob

class main():

    def __init__(self):

        pass

    #_______________Make "station.dat" using "STATION0.HYP" file.

    def make_station_file(self):

        self.ans = int(input('\n+++ Convert NLloc to hyp [1] or hyp to NLloc [2]:\n\n'))

        if self.ans == 1:

            if not os.path.exists('station.dat'):

                print('\n+++ No "station.dat" file found in current directory!\n')

                sys.exit(0)
                
        elif self.ans == 2:
            
            if not os.path.exists('STATION0.HYP'):

                print('\n+++ No "STATION0.HYP" file found in current directory!\n')

                sys.exit(0)

        else:

            sys.exit(0)



        # define a dictionary to save station information

        sta_dic = {}
        


        # ++++++++++ 1- NLloc to hyp

        if self.ans == 1:

            out = open('STATION0.HYP','w')

            tmp_sta  = genfromtxt("station.dat", dtype=str)
            
            sta_name = tmp_sta[:,1]
            sta_lat  = array(tmp_sta[:,3],dtype=float)
            sta_lon  = array(tmp_sta[:,4],dtype=float)
            sta_dep  = array(tmp_sta[:,5],dtype=float)*-1000.0
            sta_elv  = array(tmp_sta[:,6],dtype=float)*1000.0

            for i,j in enumerate(sta_name):

                sta_dic[j] = {'lat':sta_lat[i], 'lon':sta_lon[i], 'dep':sta_dep[i], 'elv':sta_elv[i]}

            for s in sorted(sta_dic):
                
                lon = ll.Longitude(sta_dic[s]['lon'])
                lat = ll.Latitude(sta_dic[s]['lat'])
                elv = sta_dic[s]['elv']
                dep = sta_dic[s]['dep']

                stc = '%-4s'%(s) 
                lon = '%2d%05.2f%1s'%(lon.degree,lon.decimal_minute,lon.get_hemisphere())
                lat = '%2d%05.2f%1s'%(lat.degree,lat.decimal_minute,lat.get_hemisphere())
                
                if elv:
                    
                    elv = '%4d'%(elv)
                    
                elif dep:
                    
                    elv = '%4d'%(dep)

                l   = "  "+stc+lat+' '+lon+elv+'\n'
                
                out.write(l)

            out.close()

            print('\n\n+++ Output file "STATION0.HYP" has been created.\n')
            

        # ++++++++++ 2- hyp to NLloc
        
        elif self.ans == 2:

            with open('STATION0.HYP') as f:

                for l in f:

                    if l.strip() and len(l)>=23 and l[13:14] in 'NS' and l[22:23] in 'WE':

                        cod = l[2:6]
                        lat = ll.Latitude(degree=float(l[6:8]), minute=float(l[8:13])).decimal_degree
                        lon = ll.Longitude(degree=float(l[14:17]), minute=float(l[17:22])).decimal_degree
                        
                        try:

                            elv = float(l[23:27])*0.001

                        except ValueError:

                            elv = 0.0

                        if elv < 0.0:

                            dep = abs(elv)
                            elv = 0.0

                        else:

                            dep = 0.0

                        sta_dic[cod] = {'lat':lat, 'lon':lon, 'dep':dep, 'elv':elv}
                            
            nlloc_sta = open('station.dat','w')

            for i in sta_dic:

                line = "GTSRCE %4s LATLON %7.3f %7.3f %5.3f %5.3f\n"%(i,sta_dic[i]['lat'],sta_dic[i]['lon'],sta_dic[i]['dep'],sta_dic[i]['elv'])
                nlloc_sta.write(line)

            nlloc_sta.close()

            print('\n\n+++ Output file "station.dat" has been created.\n')

        else:

            sys.exit(0)


#___________________ MAKE NLLOC VELOCITY MODEL FILE

    def make_vel_model(self):

        if not os.path.exists('STATION0.HYP'):

            print('\n+++ No "STATION0.HYP" file found in current directory!\n')

            sys.exit(0)

        output = open('model.dat','w')
                
        sta_zero = [[]]

        with open('STATION0.HYP') as f:

            for l in f:

                if not l.strip():

                    sta_zero.append([])

                if l.strip():

                    sta_zero[-1].append(l.strip())

        vel = [float(i.split()[0]) for i in sta_zero[2]]
        dep = [float(i.split()[1]) for i in sta_zero[2]]

        vpvs = float(input('\n+++ Vp/Vs:\n\n'))

        output.write('# model layers (LAYER depth, Vp_top, Vp_grad, Vs_top, Vs_grad, p_top, p_grad)\n')

        for v,d in zip(vel,dep):
            
            output.write('LAYER %6.2f %4.2f 0.00 %4.2f 0.00 2.70 0.00\n'%(d,v,v/vpvs))

        print('\n\n+++ Output file "model.dat" has been created.\n')
  

#___________________ CONVERT NLLOC OBS FILE TO NORDIC


    def nlloc2nor(self):

        nlloc_inp  = input('\n+++ Enter NLloc observation file:\n\n')

        if not nlloc_inp:

            sys.exit(0)
            
        nlloc_file = os.path.join(nlloc_inp)
        hypo_file  = open(os.path.join('nllochyp.out'),'w')

        with open(nlloc_file) as f:

            line1_flag = False
            line7_flag = False
            start_flag = False
                
            for l in f:

                if '# EQEVENT:' in l:

                    line1_flag = True
                    line7_flag = True
                    
                    if start_flag:

                        hypo_file.write('\n')
                        start_flag = False

                elif '#' not in l:

                    start_flag = True

                    if line1_flag and line7_flag:

                        y  = int(l[34:38])
                        m  = int(l[38:40])
                        d  = int(l[40:42])
                        H  = int(l[43:45])
                        M  = int(l[45:47])
                        S  = 0
                        MS = 0

                        ot     = dt(y,m,d,H,M,S,MS)
                        line_1 = ' %4d %02d%02d %02d%02d %4.1f L                                                         1\n'\
                                 %(ot.year,ot.month,ot.day,ot.hour,ot.minute,ot.second)
                        line_7 = ' STAT SP IPHASW D HRMN SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ7\n'

                        hypo_file.write(line_1)
                        hypo_file.write(line_7)

                        line1_flag = False
                        line7_flag = False
                
                    line       = l.strip().split()
                    sta_name   = line[0]
                    Instrument = ' '
                    comp       = ' '
                    Quality_Indicator = ' '
                    Phase_ID   = line[4]+'   '
                    Weighting_Indicator = 0
                    
                    if line[4] == 'P':
                        
                        First_Motion = line[5]
                        
                    else:
                        
                        First_Motion = ' '
                        
                    print(line)
                    arival_t = dt(int(line[6][0:4]),int(line[6][4:6]),int(line[6][6:8]),
                                  int(line[7][0:2]),int(line[7][2:4]),int(line[8].split('.')[0]),
                                  int(line[8].split('.')[1])*100)
                    line_4 = ' %-5s%1s%1s %1s%-4s%1d %1s %02d%02d %5.1f                                                   4\n'\
                             %(sta_name,Instrument,comp,Quality_Indicator,Phase_ID,Weighting_Indicator,First_Motion,arival_t.hour,arival_t.minute,arival_t.second+arival_t.microsecond*1e-6)
                    hypo_file.write(line_4)

        hypo_file.write('\n')
        hypo_file.close()

        print('\n\n+++ Output file "nlloc.hyp" has been created.\n')

#___________________ CONVERT NLLOC HYP FILE TO NORDIC
        
    def nlloc2nordic(self, nlloc_hyp, output):

        output = open(output,'a')

        with open(nlloc_hyp) as f:

            ph_l_f = False # set phase line flage to "False"

            for line in f:

                if 'GEOGRAPHIC' in line:

                    l = line.split()

                    y = float(l[2])
                    m = float(l[3])
                    d = float(l[4])
                    H = float(l[5])
                    M = float(l[6])
                    S = float(l[7])
                    X = float(l[11])
                    Y = float(l[9])
                    Z = float(l[13])

                if 'QUALITY' in line:

                    l = line.split()

                    rms = float(l[8])

                    ot  = ' %4d %02d%02d %02d%02d %4.1f L'%(y,m,d,H,M,S)

                if 'STATISTICS' in line:

                    l = line.split()

                    X_err = sqrt(float(l[8]))
                    Y_err = sqrt(float(l[14]))
                    Z_err = sqrt(float(l[18]))
                    cXY   = float(l[10])
                    cXZ   = float(l[12])
                    cYZ   = float(l[16])

                if 'STAT_GEOG' in line and int(Z) == 0:

                    l = line.split()
                    Z = float(l[6])

                if 'QML_OriginQuality' in line:

                    l = line.split()

                    gap = float(l[14])
                    nst = float(l[8])

                    # fill header line and write to file

                    lt1 = ot+' '+'%7.3f %7.3f%5.1f  TES%3d %3.1f 1.0L                   1\n'%(Y,X,Z,nst,rms)
                    lte = ' GAP=%3d      %6.2f    %6.1f  %6.1f%5.1f%12.4E%12.4E%12.4EE\n'%(gap,0.0,Y_err,X_err,Z_err,cXY,cXZ,cYZ)
                    lt7 = ' STAT SP IPHASW D HRMN SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ7\n'

                    output.write(lt1)
                    output.write(lte)
                    output.write(lt7)

                if 'PHASE ID' in line:

                    ph_l_f = True

                if 'END_PHASE' in line and ph_l_f:

                    ph_l_f = False
                    output.write('\n')
                    
                if ph_l_f and 'PHASE ID' not in line:

                    l = line.split()

                    STAT = l[0].strip()
                    PHAS = l[4].strip()
                    if PHAS == "IAML": continue
                    W    = 0
                    D    = l[5].strip()
                    HRMN = l[7].strip()
                    SEC  = float(l[8])
                    AIN  = float(l[23])
                    RES  = float(l[16])
                    DIS  = float(l[21])
                    CAZ  = float(l[22])
                    if abs(RES) >9.0: RES = RES/abs(RES)*9.9

                    lt4 = ' %-5s    %-2s  0 %-1s %-4s %5.2f                            %4.0f   %5.2f10%5d %3d4\n'%(STAT,PHAS,D,HRMN,SEC,AIN,RES,DIS,CAZ)
                    output.write(lt4)

        output.close()

#####################

start = main()

print("\n***** NLloc Tools *****\n\n")

ans = int(input("+++ Select one of the following options:\n\n1- Station file conversion.\n\n2- Data file conversion.\n\n3- Make Velocity Model file.\n\n"))


if ans == 1:

    start.make_station_file()

if ans == 2:

    new_ans = int(input('\n+++ Select one of the following options:\n\n1- Convert NLLOC observation file.\n\n2- Convert NLLOC "*.hyp" file.\n\n'))

    if new_ans == 1:

        start.nlloc2nor()

    if new_ans == 2:

        inp = input('\n+++ Enter NLLOC hypocenter directory [loc]:\n\n')
        
        open('nlloc.out','w')
        
        hypfiles = glob(os.path.join(inp, "*grid0.loc.hyp"))[:-1]
        c=0
        for hypfile in hypfiles:

            start.nlloc2nordic(nlloc_hyp=hypfile, output='nlloc.out')

            c+=1
        print("\n\n+++ %d files have been converted."%(c))
        print('+++ Output file "nlloc.out" has been created.\n')

if ans == 3:

    start.make_vel_model()

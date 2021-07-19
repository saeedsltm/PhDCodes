#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll
from datetime import datetime as dt
import os, sys
from PySTA0RW import Read_Nordic_Sta
import pylab as plt
from initial_mpl import init_plotting_isi
from numpy import arange,array,unique

"""
Script for makeing a simple statistical plot for NORDIC file.

Note:

ChangeLogs:

28-Jul-2017 > Initial.

"""

def mean(data):

    data = [float(_) for _ in data]
    return sum(data)/float(len(data))

class Main():

    #___________________GET INPUT FILE

    def __init__(self, nordic_inp='select.out', include_l4=True):

        if not os.path.exists('STATION0.HYP'):

            print '\n\n+++ No "STATION0.HYP" file was found!\n'
            sys.exit(0)
           
        self.nordic_inp = nordic_inp
        self.par_dic    = {}
        self.sta_dic    = Read_Nordic_Sta('STATION0.HYP')
        self.logfile    = open('norstat.log','w')
        self.include_l4 = include_l4 
        self.stat_wt    = []
        self.stat_tt    = []
        self.stat_dl    = []
        self.stat_rs    = []
        self.stat_dp    = []

    #___________________MAKE DATA-PHASE FILE

    def make_phase_file(self, verbose=True):

        if not os.path.exists(self.nordic_inp):

            print '\n\n+++ No "%s" file was found!\n'%(self.nordic_inp)
            sys.exit(0)
            
        self.approved_sta = []
        single_event_dic  = {'data':[]}
        self.num_eq       = 0
        wt_mapper_dic     = {' ':0,
                             '0':0,
                             '1':1,
                             '2':2,
                             '3':3,
                             '4':4} 

        with open(self.nordic_inp) as f:

            for l in f:

                if l[79:80] == '1':

                    flag = True

                    ort = self.get_ort(l)

                    try:
                        
                        lat = float(l[23:30])
                        lon = float(l[30:38])
                        dep = float(l[38:43])

                    except ValueError:

                        msg  = '+++ CHECK LAT,LON,DEP  > '+l
                        self.logfile.write(msg)
                        flag = False

                        continue

                    try:

                        mag = float(l[55:59])

                    except ValueError:

                        msg = '+++ No MAG REPORTED    > '+l
                        self.logfile.write(msg)
                        mag = 0.0

                    single_event_dic['ORT'] = ort
                    single_event_dic['LAT'] = ll.Latitude(lat)
                    single_event_dic['LON'] = ll.Longitude(lon)
                    single_event_dic['DEP'] = dep
                    single_event_dic['MAG'] = mag

                if l.strip() and l[10:11].upper() in ('P','S') and l[79:80] in (' ','4'):

                    if not self.include_l4 and l[14:15] == '4': continue

                    sta = l[1:5].strip()
                    pha = l[10:11]
                    pol = l[16:17]
                    wet = wt_mapper_dic[str(int('0'+l[14:15]))]
                    
                    try:

                        dis = float(l[70:75])
                        res = float(l[63:68])

                    except ValueError:

                        msg  = '+++ NO DIST,RES        > '+l
                        self.logfile.write(msg)
                        
                        continue
                    
                    art = self.get_art(l, ort)
                    dlt = art - ort
                    dlt = dlt.total_seconds()

                    if sta in self.sta_dic['STA'].keys() and sta not in self.approved_sta:

                        self.approved_sta.append(sta)

                    if dlt < 0.0:

                        msg  = '+++ NEGATIVE TT        > '+l
                        self.logfile.write(msg)

                    else:

                        single_event_dic['data'].append([sta,pha,pol,wet,dlt,dis,res])

                if flag and not l.strip():

                    self.num_eq+=1
                    self.get_data(single_event_dic, self.num_eq)
                    single_event_dic = {'data':[]}
                    
        self.logfile.close()
        
    def get_ort(self, l):

        ot_year  = int(l[1:5])
        ot_month = int(l[6:8])
        ot_day   = int(l[8:10])
        ot_hour  = int(l[11:13])
        ot_min   = int(l[13:15])
        ot_sec   = float(l[15:20])
        ot_msec  = int((ot_sec - int(ot_sec))*1e6)

        if ot_sec >= 60:

            ot_sec = ot_sec - 60
            ot_min+=1

        if ot_min >= 60:

            ot_min = ot_min - 60
            ot_hour+=1

        if ot_hour >= 24:

            ot_hour = ot_hour - 24
            ot_day+=1
                
        ort = dt(ot_year,ot_month,ot_day,ot_hour,ot_min,int(ot_sec),ot_msec)

        return ort

    def get_art(self,l,ort):

        at_year  = ort.year
        at_month = ort.month
        at_day   = ort.day
        at_hour  = int(l[18:20])
        at_min   = int(l[20:22])
        at_sec   = float(l[23:28])
        at_msec  = int((at_sec - int(at_sec))*1e6)

        if at_sec >= 60:

            at_sec = at_sec - 60
            at_min+=1

        if at_min >= 60:

            at_min = at_min - 60
            at_hour+=1

        if at_hour >= 24:

            at_hour = at_hour - 24
            at_day+=1

        art = dt(at_year,at_month,at_day,at_hour,at_min,int(at_sec),at_msec)

        return art
             
    def get_data(self, single_event_dic, n):

        wt = [i[3] for i in single_event_dic['data']]
        tt = [i[4] for i in single_event_dic['data']]
        dl = [i[5] for i in single_event_dic['data']]
        rs = [i[6] for i in single_event_dic['data']]

        for v in wt: self.stat_wt.append(v)
        for v in tt: self.stat_tt.append(v)
        for v in dl: self.stat_dl.append(v)
        for v in rs: self.stat_rs.append(v)

        self.stat_dp.append(-single_event_dic['DEP'])

    def stat_plotter(self):

        init_plotting_isi(6,6)

        ax1 = plt.subplot(2,2,1)
        labels, counts = unique(self.stat_wt, return_counts=True)
        ax1.bar(labels, counts, align='center', color='grey')
        ax1.set_xticks(labels)
        ax1.set_xlabel('Wieght')
        ax1.set_ylabel('Number of event [#]')
        ax1.grid(True)

        ax2 = plt.subplot(2,2,2)
        ax2.plot(self.stat_dl,self.stat_tt,color='k',marker='o',linestyle='')
        ax2.set_xlabel('Distance [km]')
        ax2.set_ylabel('Travel time [sec]')
        ax2.grid(True)

        ax3 = plt.subplot(2,2,3)
        self.stat_wt = array(self.stat_wt)
        self.stat_tt = array(self.stat_tt)
        self.stat_dl = array(self.stat_dl)
        self.stat_rs = array(self.stat_rs)
        for w,c in zip(range(5),['grey','y','g','b','y']):
            data = self.stat_rs[self.stat_wt==w]
            if not data.size: continue
            binw = .10
            bins = arange(min(data), max(data) + binw, binw)
            ax3.hist(data, bins=bins, color=c, label='W=%s'%(str(w)))
        ax3.set_xlim(-2.0,2.0)
        ax3.set_xlabel('Time Residual [sec]')
        ax3.set_ylabel('Number of event [#]')
        ax3.legend(loc=1)
        ax3.grid(True)

        ax4 = plt.subplot(2,2,4)
        data = self.stat_dp
        binw = 2.0
        bins = arange(min(data), max(data) + binw, binw)
        ax4.hist(data, bins=bins, orientation='horizontal', color='grey')
        ax4.set_xlabel('Number of event [#]')
        ax4.set_ylabel('Depth [km]')
        ax4.set_ylim(-50,0)
        ax4.grid(True)
        
        plt.tight_layout()
        plt.show()
        plt.close()
        
#___________________RUN/EXAMPLE
        
start = Main()
start.nordic_inp=raw_input('\n\n+++ Enter NORDIC file name:\n\n')
include_l4=raw_input('\n\n+++ Include phases with weight 4 [y] or Not [n]:\n\n')
if include_l4.upper()=='N': start.include_l4 = False
start.make_phase_file()
start.stat_plotter()

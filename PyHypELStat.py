#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.pyplot as plt
from numpy import array, abs, arange, loadtxt, deg2rad, pi, mean, sqrt, arctan2, cos, sin
from initial_mpl import init_plotting_isi
from scipy.stats import norm
from matplotlib import ticker
from matplotlib.colors import LogNorm
from pandas import read_csv

"""

Script for make a simple statistical plot for HYPOELLIPSE output.

ChangeLogs:

03-Aug-2017 > Initial.
26-Aug-2017 > Fixed for second >= 60.0 in Origin Time.

"""

class Main():

    def __init__(self, inp='hypoel.out'):

        self.input     = inp
        self.logfile   = open('report.log','w')
        self.hist_file = open('hist.dat','w')
        self.xyzm_file = open('xyzm.dat','w')
        self.slct_file = open('select.pha','w')
        self.max_p_res = 1.0
        self.max_s_res = 2.0
        self.max_dep   =  30
        self.minds_max =  50
        self.reduced_v = float(input('\n\n+++ Reduced Velocity?\n\n'))
        self.n_slt_evt = 0

#********************************************************

        # output selected events based on the followings:

        self.max_gap = 250
        self.max_seh =  5
        self.max_sez =  5
        self.max_rms = .5
        self.min_nob =   3
        self.min_dis = 500

#********************************************************

        with open(self.hist_file.name, 'a') as f:
 
            f.write('   P_EST   P_WET   P_RES  S_EST   S_WET   S_RES   P_DIST  P_AZIM   P_OBS     LON     LAT   DEPTH\n')

        with open(self.xyzm_file.name,'a') as f:

            f.write('     LON     LAT   DEPTH     MAG    PHUSD   NO_ST   MIND     GAP     RMS     SEH     SEZ  YYYY MM DD HH MN SEC\n')

    def d2k(self, degrees, radius=6371):

        return degrees * (2.0 * radius * pi / 360.0)

    def get_num_usd_sta(self, p_sta, s_sta, p_wet, s_wet):

        P_STA = [sta for sta,w in zip(p_sta, p_wet) if w != 4]
        S_STA = [sta for sta,w in zip(s_sta, s_wet) if w != 4]

        return len(set(P_STA+S_STA))

    #___________________WRITTER

    def writter(self):

        eid    = list(self.data_dic.keys())[0]
        p_sta  = self.data_dic[eid]['P-PHAS']['STA']
        p_pol  = self.data_dic[eid]['P-PHAS']['POL']
        p_wet  = self.data_dic[eid]['P-PHAS']['WET']
        p_res  = self.data_dic[eid]['P-PHAS']['RES']
        p_ste  = self.data_dic[eid]['P-PHAS']['STE']
        p_dis  = self.data_dic[eid]['P-PHAS']['DIS']
        p_azi  = self.data_dic[eid]['P-PHAS']['AZI']
        p_tobs = self.data_dic[eid]['P-PHAS']['TOBS']
        p_tcal = self.data_dic[eid]['P-PHAS']['TCAL']
        s_sta  = self.data_dic[eid]['S-PHAS']['STA']
        s_pol  = self.data_dic[eid]['S-PHAS']['POL']
        s_wet  = self.data_dic[eid]['S-PHAS']['WET']
        s_res  = self.data_dic[eid]['S-PHAS']['RES']
        s_ste  = self.data_dic[eid]['S-PHAS']['STE']
        s_tobs = self.data_dic[eid]['S-PHAS']['TOBS']
        s_tcal = self.data_dic[eid]['S-PHAS']['TCAL']

        lat = self.data_dic[eid]['LAT']
        lon = self.data_dic[eid]['LON']
        dep = self.data_dic[eid]['DEP']
        mag = self.data_dic[eid]['MAG']
        nop = self.data_dic[eid]['NOP']
        nst =  p_sta+s_sta
        nst = self.get_num_usd_sta(p_sta, s_sta, p_wet, s_wet)
        mds = self.data_dic[eid]['MDS']
        gap = self.data_dic[eid]['GAP']
        rms = self.data_dic[eid]['RMS']
        seh = self.data_dic[eid]['SEH']
        sez = self.data_dic[eid]['SEZ']
        ort = eid.strftime('  %Y %m %d %H %M %S.%f')[:24]

        with open(self.hist_file.name, 'a') as f:
 
            fmt = '%8.2f'*12
            fmt+='\n'

            for p0,p1,p2,p3,p4,p5,p6 in zip(p_sta,p_ste,p_wet,p_res,p_dis,p_azi,p_tobs):

                for s0,s1,s2,s3,s4 in zip(s_sta,s_ste,s_wet,s_res,s_tobs):

                    if p0 == s0:

                        f.write(fmt%(p1,p2,p3,s1,s2,s3,p4,p5,p6,lon,lat,dep))

                if p0 not in s_sta:
                    
                    f.write(fmt%(p1,p2,p3,-99,-99,-99,p4,p5,p6,lon,lat,dep))


        with open(self.xyzm_file.name,'a') as f:

            fmt = '%8.3f%8.3f%8.1f%8.1f%8d%8d%8.1f%8d%8.3f%8.1f%8.1f'
            fmt = fmt + ort+'\n'

            # lon lat dep mag phusd no_st mds gap rms seh sez

            f.write(fmt%(lon, lat, dep, mag, nop, nst, mds, gap, rms, seh, sez))

#********************************************************

        c1 = gap<=self.max_gap
        c2 = seh<=self.max_seh
        c3 = sez<=self.max_sez
        c4 = rms<=self.max_rms
        c5 = nop>=self.min_nob
        c6 = mds<=self.min_dis
        
        if c1 and c2 and c3 and c4 and c5 and c6:

            self.n_slt_evt+=1
            
            with open(self.slct_file.name, 'a') as f:

                for p1,p2,p3,p4 in zip(p_sta,p_pol,p_wet,p_tobs):

                    for s1,s2,s3 in zip(s_sta,s_wet,s_tobs):

                        if p1 == s1:

                            p_obs = eid+td(seconds=p4)
                            s_obs = eid+td(seconds=s3)
                            s_p   = s_obs-p_obs
                            s_p   = s_p.total_seconds()
                            p_sec = p_obs.second + p_obs.microsecond*1e-6
                            s_sec = p_sec + s_p
                            p_obs = p_obs.strftime('%y%m%d%H%M%S.%f')[:15]
                            f.write('%-4s P%1s%1d %15s      %6.2f S %1d\n'%(p1.upper(),p2,p3,p_obs,s_sec,s2))

                    if p1 not in s_sta:
                        
                        p_obs = eid+td(seconds=p4)
                        p_obs = p_obs.strftime('%y%m%d%H%M%S.%f')[:15]
                        f.write('%-4s P%1s%1d %15s                \n'%(p1.upper(),p2,p3,p_obs))

                f.write('                 10  5.0\n')


    #___________________EXTRACT EVENT INFO

    def get_station(self):

        sta_cod = []
        sta_lon = []
        sta_lat = []

        with open('hypoel.sta') as f:

            for l in f:

                if '*' in l: continue

                cod = l[:4]

                if cod.strip().upper() in self.used_sta:

                    lat = float(l[4:6]) + float(l[7:12])/60.
                    lon = float(l[14:16]) + float(l[17:22])/60.

                    sta_cod.append(cod)
                    sta_lon.append(lon)
                    sta_lat.append(lat)

        return array(sta_lon), array(sta_lat)

    #___________________EXTRACT EVENT INFO

    def get_event_loc(self, l):

        ort = '-'.join((l[1:5],l[5:7],l[7:9]))+' %02d%02d%05.2f'%(float(l[10:12]),float(l[12:14]),float(l[15:20]))
        try:
            ort = dt.strptime(ort,'%Y-%m-%d %H%M%S.%f')
        except ValueError:
            self.logfile.write('+++ WRONG DATE/TIME > '+l)
            ort = '-'.join((l[1:5],l[5:7],l[7:9]))+' %02d%02d%05.2f'%(float(l[10:12]),float(l[12:14])+1,float(l[15:20])-60.)
            ort = dt.strptime(ort,'%Y-%m-%d %H%M%S.%f')
        if ort.year>2090: ort=ort.replace(year=ort.year-100)
        lat = float(l[20:23])+float(l[24:29])/60.0
        lon = float(l[29:33])+float(l[34:39])/60.0
        dep = float(l[40:46])
        mag = float(l[48:53].replace(" ", "0"))
        nos = float(l[53:56])
        mds = float(l[56:59])
        gap = float(l[60:63])
        if "*" in l[65:72]: rms = 0.2 # This is very rare to occure.
        else: rms = float(l[65:72])

        return ort,lat,lon,dep,mag,nos,mds,gap,rms

    #___________________EXTRACT EVENT ERROR

    def get_event_err(self, l):

        seh = float(l[1:7])
        sez = float(l[7:12])

        return seh,sez

    #___________________EXTRACT EVENT PHASE DATA

    def get_event_pha(self, l):

        sta = l[1:6].strip()
        if 'P' in l[12:14].strip(): pha='P'
        elif 'S' in l[12:14].strip(): pha='S'
        pol = l[14]
        if not l[15:16].strip():
            wet = 0.0
        else:
            wet = float(l[15:16])
        res = float(l[30:36])
        try:
            ste = float(l[40:45])
        except ValueError:
            ste = 99.0
        if pha == 'P':
            dis = float(l[44:52])
            azi = float(l[53:57])
        else:
            dis = 0
            azi = 0
        try:
            tob = float(l[73:79])
        except ValueError: return [None]*10
        tca = float(l[79:85])

        return sta,pha,pol,wet,res,ste,dis,azi,tob,tca

    #___________________READING INPUT FILE

    def get_data(self):

        #_________SET HINTS & FLAGS

        hint_loc = 'date    origin'
        hint_err = 'seh  sez q sqd'
        hint_pha = 'stn c pha remk'
        hint_sta = ' sd    station'
        flag_loc = False
        flag_err = False
        flag_pha = False
        flag_sta = False

        with open(self.input) as f:

            self.data_dic = {}
            self.used_sta = []

            for l in f:

                if "could not locate event" in l: print("+++ Wanring Hypoellipse could not locate an event! >", l[26:].strip())

                if hint_loc in l: flag_loc = True
                if hint_err in l: flag_err = True
                if hint_pha in l: flag_pha = True
                if hint_sta in l: flag_sta = True

                if flag_loc and not l.strip(): flag_loc = False
                if flag_err and not l.strip() or '***>' in l: flag_err = False
                if flag_pha and not l.strip():
                    self.writter()
                    self.data_dic = {}
                    flag_pha = False
                if flag_sta and not l.strip(): flag_sta = False

                if flag_loc and hint_loc not in l and l[23]=='n' and l[33]=='e':

                    event_line = l

                    ort,lat,lon,dep,mag,nos,mds,gap,rms = self.get_event_loc(l)
                    self.data_dic[ort] = {'LAT':lat, 'LON':lon, 'DEP':dep,
                                          'MAG':mag, 'NOP':nos, 'MDS':mds,
                                          'GAP':gap, 'RMS':rms}

                    if dep >= self.max_dep:

                        self.logfile.write(event_line.strip()+' > DEPTH >= MAX_DEP\n')

                if flag_err and hint_err not in l:

                    seh, sez = self.get_event_err(l)
                    self.data_dic[ort].update({'SEH':seh, 'SEZ':sez})
                    self.data_dic[ort].update({'P-PHAS':{'STA':[],'POL':[],'WET':[],'RES':[],
                                                         'STE':[],'DIS':[],'AZI':[],'TOBS':[],
                                                         'TCAL':[]},
                                               'S-PHAS':{'STA':[],'POL':[],'WET':[],'RES':[],
                                                         'STE':[],'DIS':[],'AZI':[],'TOBS':[],
                                                         'TCAL':[]}})

                    if seh >= self.max_seh or sez>= self.max_sez:

                        self.logfile.write(event_line.strip()+' > H/Z ERROR >= MAX H/Z ERROR\n')

                if flag_pha and hint_pha not in l:

                    sta,pha,pol,wet,res,ste,dis,azi,tobs,tcal = self.get_event_pha(l)

                    if pha == 'P':

                        if abs(res) >= self.max_p_res:

                            self.logfile.write(l.strip()+' > RESIDUAL >= MAX_P_RESIDUAL\n')

                        self.data_dic[ort]['P-PHAS']['STA'].append(sta)
                        self.data_dic[ort]['P-PHAS']['POL'].append(pol)
                        self.data_dic[ort]['P-PHAS']['WET'].append(wet)
                        self.data_dic[ort]['P-PHAS']['RES'].append(res)
                        self.data_dic[ort]['P-PHAS']['STE'].append(ste)
                        self.data_dic[ort]['P-PHAS']['DIS'].append(dis)
                        self.data_dic[ort]['P-PHAS']['AZI'].append(azi)
                        self.data_dic[ort]['P-PHAS']['TOBS'].append(tobs)
                        self.data_dic[ort]['P-PHAS']['TCAL'].append(tcal)

                    if pha == 'S':

                        if abs(res) >= self.max_s_res:

                            self.logfile.write(l.strip()+' > RESIDUAL >= MAX_S_RESIDUAL\n')

                        self.data_dic[ort]['S-PHAS']['STA'].append(sta)
                        self.data_dic[ort]['S-PHAS']['POL'].append(pol)
                        self.data_dic[ort]['S-PHAS']['WET'].append(wet)
                        self.data_dic[ort]['S-PHAS']['RES'].append(res)
                        self.data_dic[ort]['S-PHAS']['STE'].append(ste)
                        self.data_dic[ort]['S-PHAS']['DIS'].append(dis)
                        self.data_dic[ort]['S-PHAS']['AZI'].append(azi)
                        self.data_dic[ort]['S-PHAS']['TOBS'].append(tobs)
                        self.data_dic[ort]['S-PHAS']['TCAL'].append(tcal)

                if flag_sta and hint_sta not in l:

                    self.used_sta.append(l[2:7].strip().upper())

        self.logfile.close()


    def plot(self):

        init_plotting_isi(17.5,13)
        #plt.rc('text', usetex=True)
        plt.rc('font', family='Times New Roman')
        plt.rcParams['axes.labelsize'] = 8
        #hedr = loadtxt(self.xyzm_file.name)
        hedr = read_csv(self.xyzm_file.name, delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])
        #data = loadtxt(self.hist_file.name)
        data = read_csv(self.hist_file.name, delim_whitespace=True)

        sta_lon, sta_lat = self.get_station()

        #__________PLOT P-RESIDUAL HISTOGRAM

        ax = plt.subplot(3,3,1)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        c1 = (data.P_WET.values==0)&(abs(data.P_RES.values)<=self.max_p_res)
        c2 = (data.P_WET.values==1)&(abs(data.P_RES.values)<=self.max_p_res)
        c3 = (data.P_WET.values==2)&(abs(data.P_RES.values)<=self.max_p_res)
        c4 = (data.P_WET.values==3)&(abs(data.P_RES.values)<=self.max_p_res)
        c5 = (data.P_WET.values==4)&(abs(data.P_RES.values)<=self.max_p_res)
        h1 = data.P_RES.values[c1]
        h2 = data.P_RES.values[c2]
        h3 = data.P_RES.values[c3]
        h4 = data.P_RES.values[c4]
        h5 = data.P_RES.values[c5]
        b  = arange(min(data.P_RES.values), max(data.P_RES.values) + .2, .2)
        ax.hist((h1,h2,h3,h4,h5),bins=b,label=('0','1','2','3','4'), rwidth=0.8, edgecolor='r')
        ax.set_xlim(-self.max_p_res,self.max_p_res)
        ax.legend(loc=1,title='w',fontsize=6)
        ax.set_xlabel('P residual (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #_____PLOT THE PDF

        mu, std = norm.fit(data.P_RES.values[abs(data.P_RES.values)<=self.max_s_res])
        title = "P-Residual: mu = %.2f,  std = %.2f" % (mu, std)
        ax.set_title(title)

        #__________PLOT S-RESIDUAL HISTOGRAM

        ax = plt.subplot(3,3,2)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        c1 = (data.S_WET.values==0)&(abs(data.S_RES.values)<=self.max_s_res)
        c2 = (data.S_WET.values==1)&(abs(data.S_RES.values)<=self.max_s_res)
        c3 = (data.S_WET.values==2)&(abs(data.S_RES.values)<=self.max_s_res)
        c4 = (data.S_WET.values==3)&(abs(data.S_RES.values)<=self.max_s_res)
        c5 = (data.S_WET.values==4)&(abs(data.S_RES.values)<=self.max_s_res)
        h1 = data.S_RES.values[c1]
        h2 = data.S_RES.values[c2]
        h3 = data.S_RES.values[c3]
        h4 = data.S_RES.values[c4]
        h5 = data.S_RES.values[c5]
        b  = arange(min(data.S_RES.values), max(data.S_RES.values) + .4, .4)
        ax.hist((h1,h2,h3,h4,h5),bins=b,label=('0','1','2','3','4'), rwidth=0.8, edgecolor='r')
        ax.set_xlim(-self.max_s_res,self.max_s_res)
        ax.legend(loc=1,title='w',fontsize=6)
        ax.set_xlabel('S residual (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #_____PLOT THE PDF

        mu, std = norm.fit(data.S_RES.values[abs(data.S_RES.values)<=self.max_s_res])
        title = "S-Residual: mu = %.2f,  std = %.2f" % (mu, std)
        ax.set_title(title)

        #__________PLOT RMS

        ax = plt.subplot(3,3,3)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        h = hedr.RMS.values
        b  = arange(min(h), max(h) + .05, .05)
        ax.hist(h,bins=b, rwidth=0.8, color='grey', edgecolor='r')
        ax.set_xlim(0,self.max_rms)
        ax.set_xlabel('RMS (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT DEPTH HIST

        ax = plt.subplot(3,3,4)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        h = hedr.DEPTH.values
        w = 2
        b = arange(min(h), max(h) + w, w)
        ax.hist(h,b,orientation='horizontal', rwidth=0.8, color='grey', edgecolor='r')
        ax.set_xlabel('Number of Event')
        ax.set_ylabel('Depth (km)')
        ax.set_ylim(0, self.max_dep)
        ax.invert_yaxis()
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT H-ERROR HIST

        ax = plt.subplot(3,3,5)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        h = hedr.SEH.values
        w = 0.25
        b = arange(min(h), max(h) + w, w)
        ax.hist(h,bins=b, rwidth=0.8, color='grey', edgecolor='r')
        ax.set_xlabel('Horizontal Error (km)')
        ax.set_ylabel('Number of Event')
        ax.set_xlim(0,self.max_seh)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT Z-ERROR HIST

        ax = plt.subplot(3,3,6,sharex=ax,sharey=ax)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        h = hedr.SEZ.values
        w = 0.25
        b = arange(min(h), max(h) + w, w)
        ax.hist(h,bins=b, rwidth=0.8, color='grey', edgecolor='r')
        ax.set_xlabel('Depth Error (km)')
        ax.set_ylabel('Number of Event')
        ax.set_xlim(0,self.max_sez)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT REDUCED TRAVEL-TIME

        ax = plt.subplot(3,3,7)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        x = data.P_DIST.values[(data.P_WET.values<4)&(data.DEPTH.values<=self.max_dep)]
        y = data.P_OBS.values[(data.P_WET.values<4)&(data.DEPTH.values<=self.max_dep)] - x/self.reduced_v
        z = data.DEPTH.values[(data.P_WET.values<4)&(data.DEPTH.values<=self.max_dep)]
        sc = ax.scatter(x, y, c=z, s=10, facecolors='none', cmap=plt.cm.jet, edgecolors='k', alpha=.7)
        cb = plt.colorbar(sc)
        cb.set_label('Depth (km)')
        tick_locator = ticker.MaxNLocator(nbins=6)
        cb.locator = tick_locator
        cb.update_ticks()
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('$t-x/v_{r};v_{r}=%.1f$'%self.reduced_v)
        if max(abs(ax.get_ylim()))>10: ax.set_ylim(-10,10)
        ax.set_xlim(0, max(ax.get_xlim()))
        if max(abs(ax.get_xlim()))>600: ax.set_xlim(0,600)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT MDIS-DEP

        ax = plt.subplot(3,3,8)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        x = hedr.DEPTH.values
        y = hedr.MIND.values
        z = hedr.GAP.values
        sc = ax.scatter(x, y, c=z, s=10, facecolors='none', cmap=plt.cm.jet, edgecolors='k', alpha=.7)
        cb = plt.colorbar(sc)
        cb.set_label('Azimuthal Gap ($\circ$)')
        tick_locator = ticker.MaxNLocator(nbins=6)
        cb.locator = tick_locator
        cb.update_ticks()
        ax.set_xlabel('Depth (km)')
        ax.set_ylabel('Minimum Distance (km)')
        ax.set_xlim(0, self.max_dep)
        ax.set_ylim(0, self.minds_max)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT H-ERROR VS GAP

        ax = plt.subplot(3,3,9)
        (i.set_linewidth(0.6) for i in ax.spines.items())
        x = hedr.GAP.values
        y = hedr.SEH.values
        z = hedr.PHUSD.values
        c = plt.cm.get_cmap('jet', int(max(z)))
        sc = ax.scatter(x, y, c=z, cmap=c, s=10, vmax=25, facecolors='none', norm=LogNorm(), edgecolors='k', alpha=.7)
        cb = plt.colorbar(sc, format='%d')
        cb.set_label('Number of used station')
        tick_locator = ticker.MaxNLocator(nbins=6)
        cb.locator = tick_locator
        cb.update_ticks()
        ax.set_xlabel('Azimuthal Gap ($\circ$)')
        ax.set_ylabel('Horizontal Error (km)')
        ax.set_xlim(0, 360)
        ax.set_ylim(0,self.max_seh)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)
        
        plt.tight_layout(pad=.3, w_pad=0.01, h_pad=0.01)
        plt.savefig('stat_1.png')
        plt.close()

        #__________PLOT POLAR

        init_plotting_isi(16,12)
        #plt.rc('text', usetex=True)
        plt.rc('font', family="Times New Roman")
        x_center = mean(hedr.LON.values)
        y_center = mean(hedr.LAT.values)
        dx       = hedr.LON.values-x_center
        dy       = hedr.LAT.values-y_center

        #__________PLOT AZIMUTHAL GAP

        ax = plt.subplot(1,2,1,projection='polar')
        (i.set_linewidth(0.6) for i in ax.spines.items())
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        azgap = hedr.GAP.values
        theta = arctan2(dx,dy)
        radii = self.d2k(sqrt(dx**2 + dy**2))
        sc    = ax.scatter(theta, radii, c=azgap, s=10, facecolors='none', cmap=plt.cm.jet, edgecolors='k', alpha=.7)
        clb   = plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.1, orientation='horizontal')
        clb.ax.set_title('Azimuthal Gap ($\circ$)')
        tick_locator = ticker.MaxNLocator(nbins=6)
        clb.locator  = tick_locator
        clb.update_ticks()
        
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.set_title('Event distribution relative to centroid. Lon=%.2f, Lat=%.2f'%(x_center,y_center),y=1.08)

        #__________PLOT STATION-DIST

        ax = plt.subplot(1,2,2,projection='polar')
        (i.set_linewidth(0.6) for i in ax.spines.items())
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        x_center = mean(sta_lon)
        y_center = mean(sta_lat)
        dx       = sta_lon - x_center
        dy       = sta_lat - y_center
        theta = arctan2(dx,dy)
        radii = self.d2k(sqrt(dx**2 + dy**2))
        ax.plot(theta, radii, color='r', marker='^', linestyle='', mec='k', mew=.1, zorder=100)


        theta1 = deg2rad(data.P_AZIM.values)
        radii1 = data.P_DIST.values
        dx     = data.LON.values - x_center
        dy     = data.LAT.values- y_center
        theta2 = arctan2(dx,dy)
        radii2 = self.d2k(sqrt(dx**2 + dy**2))
        alpha  = theta2-theta1
        u      = radii2*cos(alpha)
        v      = radii2*sin(alpha)
        r3     = sqrt((radii1+u)**2 + v**2)
        beta   = arctan2(v,radii1+u)
        t3     = theta1+beta

        ax.plot(t3, r3, color='g', marker='^', linestyle='', mec='k', mew=.1,)
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.set_title('Station Distance-Azimuth', y=1.08)

        plt.tight_layout(pad=.3, w_pad=0.01, h_pad=0.01)
        plt.savefig('stat_2.png')
        plt.close()

#__________________START

import warnings
warnings.filterwarnings("ignore")

start = Main()
start.get_data()
start.plot()

print('\n+++ Selection criteria:\n')
print('Max Gap   =',start.max_gap)
print('Max SEH   =',start.max_seh)
print('Max SEZ   =',start.max_sez)
print('Max RMS   =',start.max_rms)
print('Min NOB   =',start.min_nob)
print('Min DIS   =',start.min_dis)
print('\n+++ Number of selected events is %d and saved in "select.pha" file.\n'%start.n_slt_evt)

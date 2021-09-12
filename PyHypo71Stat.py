#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from LatLon import lat_lon as ll
from pandas import read_csv
import matplotlib.pyplot as plt
from numpy import arange, std, float16
from initial_mpl import init_plotting_isi
from scipy.stats import norm
from matplotlib import ticker
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

class Hypo71():

    def __init__(self):

        self.max_p_res = 0.75
        self.max_s_res = 0.75
        self.max_rms = 0.5
        self.max_dep = 30.0
        self.max_ErZ = 10.0
        self.max_ErH = 10.0
        self.PRT_File = "hypo71.prt"
        self.DB = open("EQs.dat", "w")
        with open(self.DB.name, "a") as f:
            f.write("OriginTime Lat Lon Dep PhN DsM Gap RMS ErH ErZ Sta Dis Azm PPh Pol Ptt Prs Pwt SPh Stt Srs Swt\n")

    def DateTimeParser(self, DateTime):

        for i in [1,2,3,5,8,10]:

            if DateTime[i] == " ": DateTime = DateTime[:i]+"0"+DateTime[i+1:]
            
        DateTime = dt.strptime(DateTime[1:],"%y%m%d %H%M %S.%f")
        
        return DateTime

    def EventInfoParser(self, EventInfo):

        l = EventInfo

        Lat = ll.Latitude(degree=float(l[19:21]), minute=float(l[22:27])).decimal_degree
        Lon = ll.Longitude(degree=float(l[29:31]), minute=float(l[32:37])).decimal_degree
        Dep = float(l[38:44])
        PhN = int(l[52:54])
        DsM = int(l[54:57])
        Gap = int(l[58:61])
        RMS = float(l[64:68])
        ErH = float(l[68:73])
        ErZ = float(l[73:78])

        return Lat, Lon, Dep, PhN, DsM, Gap, RMS, ErH, ErZ

    def PhaseInfoParser(self, PhaseInfo):

        l = PhaseInfo
        
        Sta = l[1:5].strip()    # Station Code 
        Dis = float(l[5:11])    # Station Distance
        Azm = int(l[12:15])     # Station Azimuth
        Ain = int(l[16:19])     # Incident Angle
        PPh = l[21]             # P-Phase Type
        Pol = l[22].strip()     # Polarity
        Ptt = float(l[35:41])   # P-Phase Travel Time
        Prs = float(l[53:59])   # P-Phase Timme Residual
        Pwt = float(l[61:65])   # P-Phase Wieght
        if l[100].strip():
            SPh = l[100]            # S-Phase Type
            Stt = float(l[109:115]) # S-Phase Travel Time
            Srs = float(l[115:121]) # S-Phase Timme Residual
            Swt = float(l[122:127]) # S-Phase Wieght
        else:
            SPh = None
            Stt = None
            Srs = None
            Swt = None

        return Sta, Dis, Azm, PPh, Pol, Ptt, Prs, Pwt, SPh, Stt, Srs, Swt


    def DBWriter(self, OriginTime, EventInfo, PhaseInfo):

        with open(self.DB.name, "a") as f:

            f.write(OriginTime.strftime("%s.%f"))
            f.write(" %6.3f %6.3f %5.2f %2d %3d %3d %4.2f %5.2f %5.2f "%EventInfo)
            if PhaseInfo[8]:
                f.write("%4s %5.1f %3d %1s %1s %4.1f %4.1f %1s %1s %4.1f %4.1f %1s\n"%PhaseInfo)
            else:
                f.write("%4s %5.1f %3d %1s %1s %4.1f %4.1f %1s %1s %4s %4s %1s\n"%PhaseInfo)


    def PRTReader(self):

        with open(self.PRT_File) as f:

            hdr_flg = "DATE    ORIGIN"
            pha_flag = "STN  DIST"
            pha_start = False

            for line in f:

                if hdr_flg in line:

                    l = next(f)

                    OriginTime = self.DateTimeParser(l[:18])
                    EventInfo = self.EventInfoParser(l)
                    
                if pha_flag in line: pha_start = True
                if pha_start and (line.startswith("1") or not line.strip()): pha_start = False
                if pha_start and pha_flag not in line:
                    PhaseInfo = self.PhaseInfoParser(line)
                    self.DBWriter(OriginTime, EventInfo, PhaseInfo)


    def Statistic(self):

        db = read_csv(self.DB.name, delim_whitespace=True)

        init_plotting_isi(19,13)
        #plt.rc('text', usetex=True)
        plt.rc('font', family='Times New Roman')
        plt.rcParams['axes.labelsize'] = 8

        #__________PLOT P-RESIDUAL HISTOGRAM

        ax = plt.subplot(3,3,1)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        P_Residual = db.Prs.values
        sigma = std(P_Residual)
        ax.text(0.7, 0.85, "$\sigma=%.2f$\n$N=%d$"%(sigma, P_Residual.size), ha='left', va='center', transform=ax.transAxes)

        b  = arange(P_Residual.min(), P_Residual.max() + .1, .1)
        ax.hist(P_Residual, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666")
        ax.set_xlim(-self.max_p_res, self.max_p_res)
        ax.set_xlabel('P residual (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT S-RESIDUAL HISTOGRAM

        ax = plt.subplot(3,3,2)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        S_Residual = float16(db.Srs[db.Srs!="None"].values)
        sigma = std(S_Residual)
        ax.text(0.7, 0.85, "$\sigma=%.2f$\n$N=%d$"%(sigma, S_Residual.size), ha='left', va='center', transform=ax.transAxes)

        b  = arange(S_Residual.min(), S_Residual.max() + .1, .1)
        ax.hist(S_Residual, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666")
        ax.set_xlim(-self.max_s_res, self.max_s_res)
        ax.set_xlabel('S residual (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT RMS HISTOGRAM

        ax = plt.subplot(3,3,3)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        RMS = db.RMS.values

        b  = arange(RMS.min(), RMS.max() + .05, .05)
        ax.hist(RMS, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666")
        ax.set_xlim(0, self.max_rms)
        ax.set_xlabel('RMS (s)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT Depth HISTOGRAM

        ax = plt.subplot(3,3,4)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        Dep = -db.Dep.values

        b  = arange(Dep.min(), Dep.max() + 3, 3)
        ax.hist(Dep, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666", orientation='horizontal')
        ax.set_ylim(-self.max_dep, 0.0)
        ax.set_xlabel('Number of Event')
        ax.set_ylabel('Depth (km)')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT ErH HISTOGRAM

        ax = plt.subplot(3,3,5)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        ErH = db.ErH.values

        b  = arange(ErH.min(), ErH.max() + 1, 1)
        ax.hist(ErH, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666")
        ax.set_xlim(0, self.max_ErH)
        ax.set_xlabel('Error H (km)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)
        
        #__________PLOT ErZ HISTOGRAM

        ax = plt.subplot(3,3,6)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        ErZ = db.ErZ.values

        b  = arange(ErZ.min(), ErZ.max() + 1, 1)
        ax.hist(ErZ, bins=b, rwidth=0.8, edgecolor='#525266', color="#ff6666")
        ax.set_xlim(0, self.max_ErZ)
        ax.set_xlabel('Error Z (km)')
        ax.set_ylabel('Number of Event')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT TravelTime

        ax = plt.subplot(3,3,7)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        Ptt = db.Ptt.values
        Dis = db.Dis.values
        Dep = db.Dep.values

        sc = ax.scatter(Dis, Ptt, s=5, c=Dep, edgecolor="k", linewidths=.25, cmap=plt.cm.jet_r)
        divider = make_axes_locatable(ax)
        cax     = divider.append_axes("right", size="5%", pad=0.02)
        cb      = plt.colorbar(sc, format='%d', cax=cax)

        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.set_label('Depth (km)', size=7, labelpad=1)
        cb.outline.set_linewidth(0.5)
        
##        ax.set_xlim(0, self.max_ErZ)
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('P-Phase Travel Time (s)')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)


        #__________PLOT Depth VS Min-Distance

        ax = plt.subplot(3,3,8)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        DsM = db.DsM.values
        Gap = db.Gap.values
        Dep = db.Dep.values

        sc = ax.scatter(Dep, DsM, s=5, c=Gap, edgecolor="k", linewidths=.25, cmap=plt.cm.jet_r)
        divider = make_axes_locatable(ax)
        cax     = divider.append_axes("right", size="5%", pad=0.02)
        cb      = plt.colorbar(sc, format='%d', cax=cax)

        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.set_label('Gap (deg)', size=7, labelpad=1)
        cb.outline.set_linewidth(0.5)
        
##        ax.set_xlim(0, self.max_ErZ)
        ax.set_xlabel('Depth (km)')
        ax.set_ylabel('Min-Distance (km)')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)

        #__________PLOT Gap VS Horizontal Error

        ax = plt.subplot(3,3,9)
        (i.set_linewidth(0.6) for i in ax.spines.itervalues())
        ax.set_facecolor("#fcfaf4")

        ErH = db.DsM.values
        Gap = db.Gap.values
        ErZ = db.ErZ.values

        sc = ax.scatter(Gap, ErH, s=5, c=ErZ, edgecolor="k", linewidths=.25, cmap=plt.cm.jet_r)
        divider = make_axes_locatable(ax)
        cax     = divider.append_axes("right", size="5%", pad=0.02)
        cb      = plt.colorbar(sc, format='%d', cax=cax)

        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.set_label('Error Z (km)', size=7, labelpad=1)
        cb.outline.set_linewidth(0.5)

        
##        ax.set_xlim(0, self.max_ErZ)
        ax.set_xlabel('Gap (deg)')
        ax.set_ylabel('Error H (km)')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis = 'x', nbins=5)
        ax.locator_params(axis = 'y', nbins=5)
        
        
        plt.tight_layout(pad=.3, w_pad=0.01, h_pad=0.01)
        plt.savefig('Statistic.png', dpi=300)
        plt.close()


##
exp = Hypo71()
exp.PRTReader()
exp.Statistic()

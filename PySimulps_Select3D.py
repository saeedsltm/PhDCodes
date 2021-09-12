#!/home/saeed/Programs/miniconda3/bin/python

from numpy import array, linspace, genfromtxt, datetime64, save, savetxt, load, loadtxt, flip, histogram2d, sum
from datetime import datetime as dt
from datetime import timedelta as td
from LatLon import lat_lon as ll
from glob import glob
import os, sys
from PyMyFunc import k2d, d2k, get_ot
from initial_mpl import init_plotting_isi
import pylab as plt
from matplotlib import ticker
from matplotlib import colors
from pandas import read_csv
from scipy.ndimage import zoom
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PyGetFaults import draw_fault_simple, draw_fault_names, draw_border
from PyMyFunc import d2k

#___________________

class event_parser():

    def __init__(self):

        if not os.path.exists('select3D.par'):

            print('\n+++ No parameter file "select3D.par" was found. creating a new one and using defaults ...')

            with open('select3D.par', 'w') as f:

                f.write("""#
# Parameter file for selecting best event using Hypoellipse
# output file (hypoel.out) and station file (hypoel.sta).
# 
#__________DEFINE STUDY REGION
#
lon_min = 50.00              # Minimum Longitude
lon_max = 54.00              # Maximum Longitude
lat_min = 34.50              # Minimum Latitude
lat_max = 36.50              # Maximum Latitude
dep_min = 0.0                # Minumum Depth 
dep_max = 40.0               # Maxumum Depth
begin_d = 2000               # begining date
end_d   = 2100               # ending date
#
#__________CELL CONFIGURATION
#
nx = 10                      # Number of cells in x.
ny = 10                      # Number of cells in y.
nz = 10                      # Number of cells in z.
me = 10                      # Maximum number of event inside each cell.
#
#__________SELECTION CRITERIA (BEST EVENTS)
#
min_mag = 0.0                # Minimum magnitude.
max_mag = 9.0                # Maximum magnitude.
max_gap = 180                # Maximum azimuthal gap (deg).
max_rms = 0.5                # Maximum rms (sec).
max_her = 10                 # Maximum horizontal error (km).
max_zer = 10                 # Maximum depth error (km).
max_dis = 99                 # Maximum distance between nearest station-event (km).
min_sta =  5                 # Minimum number of used stations.
min_pph =  5                 # Minimum number of used P phase.
min_sph =  1                 # Minimum number of used S phase.
sort_id = 5                  # Sort events and select based on: 4=rms, 5=gap, 7=her, 9=nmp.
#
#__________SELECTION CRITERIA (BEST STATIONS)
#
cen_lat = 35.5               # Latitude of central study region.
cen_lon = 52.0               # Longitude of central study region.
cen_rot = 0.0                # Rotation of central study region.
lon_dx = 100                 # Maximum distance between the furthest station and longitude border (km).
lat_dy = 100                 # Maximum distance between the furthest station and latitude border (km).
min_rc = 10                  # Minimum number of phases (P&S) recorded by station.
#__________Plotting Options
LogN   = 1                   # Scale colorbar logarithmic (1) or simple (0).
#""")

        else:

            print('\n+++ Reading parameter file "select3D.par" ...')   
    
        self.evt = event
        self.out_sum = open('sum.dat', 'w')
        self.out_fin = open('travel.dat', 'w')
        self.out_fin_sm2000 = open('travel_sm2000.dat', 'w')
        self.out_h71 = open('select3D.pha', 'w')
        self.out_sta = open('staz.dat', 'w')
        self.out_sta_sm2000 = open('staz_sm2000.dat', 'w')
        self.out_usd = open('used.dat', 'w')
        self.nll_sta = open('station.dat', 'w')
        self.sel_par = genfromtxt('select3D.par')
        self.nei = 0
        self.neo = 0

        #__________DEFINE STUDY REGION

        self.lon_min = self.sel_par[0][2]
        self.lon_max = self.sel_par[1][2]
        self.lat_min = self.sel_par[2][2]
        self.lat_max = self.sel_par[3][2]
        self.dep_min = self.sel_par[4][2]
        self.dep_max = self.sel_par[5][2]
        self.begin_d = dt(int(self.sel_par[6][2]),1,1)
        self.end_d = dt(int(self.sel_par[7][2]),1,1)

        #__________CELL CONFIGURATION
        
        self.nx = int(self.sel_par[8][2])
        self.ny = int(self.sel_par[9][2])
        self.nz = int(self.sel_par[10][2])
        self.me = int(self.sel_par[11][2])

        #__________SELECTION CRITERIA (BEST EVENTS)

        self.min_mag = self.sel_par[12][2]
        self.max_mag = self.sel_par[13][2]
        self.max_gap = self.sel_par[14][2]
        self.max_rms = self.sel_par[15][2]
        self.max_her = self.sel_par[16][2]
        self.max_zer = self.sel_par[17][2]
        self.max_dis = self.sel_par[18][2]
        self.min_sta = int(self.sel_par[19][2])
        self.min_pph = int(self.sel_par[20][2])
        self.min_sph = int(self.sel_par[21][2])
        self.sort_id = int(self.sel_par[22][2])

        #__________SELECTION CRITERIA (BEST STATIONS)

        self.cen_lat = self.sel_par[23][2]
        self.cen_lon = self.sel_par[24][2]
        self.cen_rot = self.sel_par[25][2]
        self.lon_dx = self.sel_par[26][2]
        self.lat_dy = self.sel_par[27][2]
        self.min_rc = int(self.sel_par[28][2])
        self.sta_dic = {}
        self.sorting_c = {4:'RMS', 5:'Azimuthal Gap', 7:'Horizontal Error', 9:'Min Nmber of used station'}

        #__________Plotting Options
        
        self.LogN = int(self.sel_par[29][2])
        
    #___________________ GET EARTHQUAKE PARAMETER LIKE LAT,LON,DEP...    

    def eq_stat(self):

        header = 'date    origin'

        for i,line in enumerate(self.evt):

            if header in line:

                l = self.evt[i+1]

                yy = int(l[1:5])
                mm = int(l[5:7])
                dd = int(l[7:9])
                HH = int(l[10:12])
                MM = int(l[12:14])
                SS = int(float(l[15:20]))
                MS = int((float(l[15:20]) - SS)*1e6)

                ort = get_ot(yy,mm,dd,HH,MM,SS,MS)
                lat = ll.Latitude(degree=float(l[21:23]), minute=float(l[24:29])).decimal_degree
                lon = ll.Longitude(degree=float(l[31:33]), minute=float(l[34:39])).decimal_degree
                dep = float(l[40:46])
                mag = float(l[50:53].replace(' ','0'))
                nearest_st = int(l[56:59])
                az_gap = int(l[60:63])
                rms = float(l[65:72])

                break
            
        return ort, lat, lon, dep, mag, nearest_st, az_gap, rms

    #___________________ GET EARTHQUAKE ERROR HYPOCENTRAL ESTIMATION

    def eq_err(self):

        # Get number of stations, P-phase and S-phase
        hed_begin, hed_begin_f = "stn c pha", False
        hed_end, hed_end_f = "", False
        stas = []
        ST_num, P_num, S_num = 0, 0, 0

        for i,line in enumerate(self.evt):
            
            if hed_begin in line: hed_begin_f = True
            if hed_begin_f and hed_end == line.strip(): hed_end_f = True
            
            if hed_begin_f and hed_begin not in line and not hed_end_f:
                
                stas.append(line[1:5])
                if line[15] != "4" and line[13].upper() == "P": P_num+=1
                if line[15] != "4" and line[13].upper() == "S": S_num+=1
        
        ST_num = len(list(set(stas)))

        # Get Horizontal and Depth error
        header = 'seh  sez q sqd'

        for i,line in enumerate(self.evt):

            if header in line:

                l = self.evt[i+1]

                h_err = float(l[3:7])
                z_err = float(l[8:12])

                break
            
        return h_err, z_err, ST_num, P_num, S_num

    #___________________ WRITE INTO SUMMARY FILE

    def write_summary(self):

        # ort,lat,lon,dep,mag,rms,az_gap,nearest_st,h_err,z_err,h_err, z_err,ST_num,P_num,S_num

        ort, lat, lon, dep, mag, nearest_st, az_gap, rms = self.eq_stat()
        h_err, z_err, ST_num, P_num, S_num = self.eq_err()

        with open(self.out_sum.name, 'a') as f:

            line = '%-26s'%ort.isoformat()
            line+=' %6.3f %6.3f %5.2f %3.1f %5.3f %3d %3d %4.2f %5.2f %3d %3d %3d\n'%(lat,lon,dep,mag,rms,az_gap,nearest_st,h_err,z_err,ST_num,P_num,S_num)
            f.write(line)

    #___________________ SPLIT EVENTS INTO CELLS

    def split_evt_into_cell(self):

        eq_sum = genfromtxt('sum.dat',dtype=object)
        eq_sum[:,0] = array(eq_sum[:,0], dtype='datetime64')
        eq_sum[:,1:] = array(eq_sum[:,1:], dtype=float)

        x_pnts = linspace(self.lon_min, self.lon_max, self.nx, endpoint=True)
        y_pnts = linspace(self.lat_min, self.lat_max, self.ny, endpoint=True)
        z_pnts = linspace(self.dep_min, self.dep_max, self.nz, endpoint=True)

        for z in range(z_pnts.size-1):

            for y in range(y_pnts.size-1):

                for x in range(x_pnts.size-1):

                    c_ot  = (eq_sum[:,0]>=self.begin_d)&(eq_sum[:,0]<=self.end_d)
                    c_lon = (x_pnts[x]<=eq_sum[:,2])&(eq_sum[:,2]<x_pnts[x+1])
                    c_lat = (y_pnts[y]<=eq_sum[:,1])&(eq_sum[:,1]<y_pnts[y+1])
                    c_dep = (z_pnts[z]<=eq_sum[:,3])&(eq_sum[:,3]<z_pnts[z+1])
                    c_mag = (self.min_mag<=eq_sum[:,4])&(eq_sum[:,4]<self.max_mag)
                    c_rms = eq_sum[:,5]<=self.max_rms
                    c_gap = eq_sum[:,6]<=self.max_gap
                    c_mds = eq_sum[:,7]<=self.max_dis
                    c_her = eq_sum[:,8]<=self.max_her
                    c_zer = eq_sum[:,9]<=self.max_zer
                    c_nos = eq_sum[:,10]>=self.min_sta
                    c_noP = eq_sum[:,11]>=self.min_pph
                    c_noS = eq_sum[:,12]>=self.min_sph

                    ct = (c_ot&c_lon&c_lat&c_dep&c_mag&c_rms&c_gap&c_mds&c_her&c_zer&c_nos&c_noP&c_noS)

                    eqs_in_cell = array(eq_sum[ct])

                    if eqs_in_cell.size:
                      
                        output = '%003d-%003d-%003d.npy'%(x,y,z)
                        save(output, eqs_in_cell)
                    
    #___________________ SPLIT EVENTS INTO CELLS

    def extract_from_cell(self):

        output = open('select3D.cat', 'w')

        npy_files = glob('*.npy')

        for npy_file in npy_files:

            cell = load(npy_file, allow_pickle=True)
            sort_index = cell[:,1:].argsort(0)[:,self.sort_id]

            with open(output.name, 'a') as f:

                for i,j in enumerate(sort_index):

                    if i <= self.me:

                        ort = cell[j][0].isoformat()
                        evt = array(cell[j], dtype=str)
                        f.write('%-26s %6.3f %6.3f %5.2f %3.1f %5.3f %3d %3d %4.2f %5.2f %3d\n'%(ort,float(evt[1]),float(evt[2]),float(evt[3]),float(evt[4]),float(evt[5]),
                                                                                                 float(evt[6]),float(evt[7]),float(evt[8]),float(evt[9]),float(evt[10])))
                        
            os.remove(npy_file)

    #___________________EXTRACT EVENT PHASE DATA FROM HYPOELLIPSE PHASE LINE

    def read_hypoellipse_phase_line(self, l):

        sta = l[1:6].strip()
        if 'P' in l[12:14].strip(): pha='P'
        elif 'S' in l[12:14].strip(): pha='S'
        pol = l[14]
        if not l[15:16].strip():
            wet = 0
        else:
            wet = int(l[15:16])
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
        tob = float(l[73:79])
        tca = float(l[79:85])

        return sta,pha,pol,wet,res,ste,dis,azi,tob,tca
    
    #___________________ WRITE BEST EVENTS INTO HYPO71 FORMAT

    def wrire_phase(self, sel_cat):

        sel_orts = sel_cat[:,0]
        eq_stat = self.eq_stat()
        ort = eq_stat[0]
        lat = ll.Latitude(eq_stat[1])
        lon = ll.Longitude(eq_stat[2])
        dep = eq_stat[3]
        mag = eq_stat[4]

        self.phase_dic ={'P-PHAS':{'STA':[],'POL':[],'WET':[],'RES':[],
                                   'STE':[],'DIS':[],'AZI':[],'TOBS':[],
                                    'TCAL':[]},
                         'S-PHAS':{'STA':[],'POL':[],'WET':[],'RES':[],
                                   'STE':[],'DIS':[],'AZI':[],'TOBS':[],
                                   'TCAL':[]}}
        if ort in sel_orts:

            self.neo+=1

            header = '-- travel times and delays --'

            for i,line in enumerate(self.evt):

                if header in line:

                    phase_lines = self.evt[i+2:len(self.evt)-1]

                    for l in phase_lines:

                        sta,pha,pol,wet,res,ste,dis,azi,tobs,tcal = self.read_hypoellipse_phase_line(l)

                        if pha == 'P':

                            self.phase_dic['P-PHAS']['STA'].append(sta)
                            self.phase_dic['P-PHAS']['POL'].append(pol)
                            self.phase_dic['P-PHAS']['WET'].append(wet)
                            self.phase_dic['P-PHAS']['RES'].append(res)
                            self.phase_dic['P-PHAS']['STE'].append(ste)
                            self.phase_dic['P-PHAS']['DIS'].append(dis)
                            self.phase_dic['P-PHAS']['AZI'].append(azi)
                            self.phase_dic['P-PHAS']['TOBS'].append(tobs)
                            self.phase_dic['P-PHAS']['TCAL'].append(tcal)

                        if pha == 'S':

                            self.phase_dic['S-PHAS']['STA'].append(sta)
                            self.phase_dic['S-PHAS']['POL'].append(pol)
                            self.phase_dic['S-PHAS']['WET'].append(wet)
                            self.phase_dic['S-PHAS']['RES'].append(res)
                            self.phase_dic['S-PHAS']['STE'].append(ste)
                            self.phase_dic['S-PHAS']['DIS'].append(dis)
                            self.phase_dic['S-PHAS']['AZI'].append(azi)
                            self.phase_dic['S-PHAS']['TOBS'].append(tobs)
                            self.phase_dic['S-PHAS']['TCAL'].append(tcal)
                    
                    break

            p_sta  = self.phase_dic['P-PHAS']['STA']
            p_pol  = self.phase_dic['P-PHAS']['POL']
            p_wet  = self.phase_dic['P-PHAS']['WET']
            p_tobs = self.phase_dic['P-PHAS']['TOBS']
            s_sta  = self.phase_dic['S-PHAS']['STA']
            s_wet  = self.phase_dic['S-PHAS']['WET']
            s_tobs = self.phase_dic['S-PHAS']['TOBS']

            with open(self.out_fin.name, 'a') as f, open(self.out_fin_sm2000.name, 'a') as g:

                lb = 0

                header = ort.strftime('%y%m%d %H%M %S.%f')[:17]
                header+=' %2d%1s%5.2f  %2d%1s%5.2f %6.2f  %5.2f\n'%(lat.degree,lat.get_hemisphere(),lat.decimal_minute,
                                                                    lon.degree,lon.get_hemisphere(),lon.decimal_minute,
                                                                    dep,mag)
                f.write(header)
                g.write(header)

                for p1,p2,p3,p4 in zip(p_sta,p_pol,p_wet,p_tobs):

                    f.write('%4sEP%1s%1d%6.2f'%(p1.upper(),p2,p3,p4))
                    g.write('%4s  P%1d%6.3f'%(p1.upper(),p3,p4))


                    lb+=1
                    if lb==6:
                        f.write('\n')
                        g.write('\n')
                        lb=0

                    if p1.upper() not in self.sta_dic: self.sta_dic[p1.upper()] = 0
                    else: self.sta_dic[p1.upper()]+=1
               
                for s1,s2,s3 in zip(s_sta,s_wet,s_tobs):

                    p_tobs_ind = p_sta.index(s1)
                    p_tt = p_tobs[p_tobs_ind]
                    Ts_p = s3 - p_tt

                    f.write('%4sESP%1d%6.2f'%(s1.upper(),s2,Ts_p))
                    g.write('%4s  S%1d%6.3f'%(s1.upper(),s2,s3))

                    lb+=1
                    if lb==6:
                        f.write('\n')
                        g.write('\n')
                        lb=0

                    if s1.upper() not in self.sta_dic: self.sta_dic[s1.upper()] = 0
                    else: self.sta_dic[s1.upper()]+=1
                    
                if lb==0:
                    f.write('\n')
                    g.write('\n')
                else: 
                    f.write('\n\n')
                    g.write('\n\n')

            # Now in Hyp71 Format
            
            with open(self.out_h71.name, 'a') as f:

                for p1,p2,p3,p4 in zip(p_sta,p_pol,p_wet,p_tobs):

                    for s1,s2,s3 in zip(s_sta,s_wet,s_tobs):

                        if p1 == s1:

                            p_obs = ort+td(seconds=p4)
                            s_obs = ort+td(seconds=s3)
                            s_p   = s_obs-p_obs
                            s_p   = s_p.total_seconds()
                            p_sec = p_obs.second + p_obs.microsecond*1e-6
                            s_sec = p_sec + s_p
                            p_obs = p_obs.strftime('%y%m%d%H%M%S.%f')[:15]
                            f.write('%-4s P%1s%1d %15s      %6.2f S %1d\n'%(p1.upper(),p2,p3,p_obs,s_sec,s2))

                    if p1 not in s_sta:
                        
                        p_obs = ort+td(seconds=p4)
                        p_obs = p_obs.strftime('%y%m%d%H%M%S.%f')[:15]
                        f.write('%-4s P%1s%1d %15s                \n'%(p1.upper(),p2,p3,p_obs))

                f.write('                 10            \n')

    #___________________ WRITE Hypoellipse Station File

    def write_station_hypoel(self, hypoel_sta_file, st, lat, lon, elv):

        with open(hypoel_sta_file.name, 'a') as f:

            f.write('%4s%2d%1s%5.2f  %2d%1s%5.2f%5d\n'%(st,
                                                        lat.degree,lat.get_hemisphere(),lat.decimal_minute,
                                                        lon.degree,lon.get_hemisphere(),lon.decimal_minute,
                                                        elv))
            f.write('%4s*     0     1.00\n'%st)

    #___________________ WRITE NLLOC Station File

    def write_station_nlloc(self, nlloc_sta_file, st, lat, lon, elv):

        with open(nlloc_sta_file.name, 'a') as f:

            f.write('GTSRCE  %4s  LATLON   %6.3f  %6.3f  0.0  %5.3f\n'%(st, lat.decimal_degree, lon.decimal_degree, elv/1000.))


    #___________________ WRITE SELECTED STATIONS INTO SIMULPS FORMAT

    def wrire_station(self):

        hypoel_sta_file = open('select3D.sta','w')

        self.cen_lat = ll.Latitude(self.cen_lat)
        self.cen_lon = ll.Longitude(self.cen_lon)

        st_nam = []
        st_lat = []
        st_lon = []
        st_elv = []
      
        with open('hypoel.sta') as f:

            for l in f:

                if '*' not in l:

                    if l[:4].strip().upper() not in st_nam:

                        st_nam.append(l[:4].strip().upper())
                        st_lat.append(ll.Latitude(degree=float(l[4:6]), minute=float(l[7:12])).decimal_degree)
                        st_lon.append(ll.Longitude(degree=float(l[14:16]), minute=float(l[17:22])).decimal_degree)
                        st_elv.append(float(l[22:27]))

        st_nam = array(st_nam)
        st_lat = array(st_lat)
        st_lon = array(st_lon)
        st_elv = array(st_elv)

        c_lat = (st_lat>=self.lat_min-k2d(self.lat_dy))&(st_lat<=self.lat_max+k2d(self.lat_dy))
        c_lon = (st_lon>=self.lon_min-k2d(self.lon_dx))&(st_lon<=self.lon_max+k2d(self.lon_dx))
        c_tot = (c_lat&c_lon)

        st_nam = st_nam[c_tot]
        st_lat = st_lat[c_tot]
        st_lon = st_lon[c_tot]
        st_elv = st_elv[c_tot]

        self.num_used_st = 0
      
        with open('tmp', 'w') as f, open('tmp2', 'w') as g:

            # Write in SIMUL2000
            g.write(' %2d %5.2f  %2d %5.2f  %1d 0\n'%(self.cen_lat.degree,self.cen_lat.decimal_minute,
                                                      self.cen_lon.degree,self.cen_lon.decimal_minute,
                                                      self.cen_rot))
            g.write('%4d\n'%len(self.sta_dic))
            
            # Write in SIMUL14
            f.write(' %2d %5.2f  %2d %5.2f  %1d 1\n'%(self.cen_lat.degree,self.cen_lat.decimal_minute,
                                                      self.cen_lon.degree,self.cen_lon.decimal_minute,
                                                      self.cen_rot))
            f.write('%4d\n'%len(self.sta_dic))

            for i,st in enumerate(st_nam):

                if st in self.sta_dic and self.sta_dic[st] >= self.min_rc:

                    lat = ll.Latitude(st_lat[i])
                    lon = ll.Longitude(st_lon[i])
                    elv = st_elv[i]

                    line = '  %4s%2d%1s%5.2f  %2d%1s%5.2f%5d%5.2f%5.2f%3d\n'%(st,
                                                                            lat.degree,lat.get_hemisphere(),lat.decimal_minute,
                                                                            lon.degree,lon.get_hemisphere(),lon.decimal_minute,
                                                                            elv,0,0,0)
                    line2 = '%-6s%9.5f%10.5f%6.3f%5.2f%5.2f%3d\n'%(st,lat.decimal_degree,lon.decimal_degree,elv*1e-3,0.0,0.0,0)
                    
                    f.write(line)
                    g.write(line2)

                    self.write_station_hypoel(hypoel_sta_file, st, lat, lon, elv)
                    self.write_station_nlloc(self.nll_sta, st, lat, lon, elv)
                    self.num_used_st+=1

        with open('tmp') as f, open('tmp2') as g:

            with open(self.out_sta.name, 'w') as ff, open(self.out_sta_sm2000.name, 'w') as gg:

                # Write in SIMUL2000
                for i,l in enumerate(g):

                    if i == 1:

                        l = '%4d\n'%self.num_used_st

                    gg.write(l)

                # Write in SIMUL14
                for i,l in enumerate(f):

                    if i == 1:

                        l = '%4d\n'%self.num_used_st

                    ff.write(l)

        os.remove('tmp')
        os.remove('tmp2')

    #___________________ WRITE USED EVENTS

    def write_used_evts(self):

        select3d = genfromtxt('select3D.cat', dtype=str)
        savetxt(self.out_usd.name,array(select3d[:,1:4],dtype=float), fmt='%7.3f')

    #___________________ PLOT RESULT


    def plot_result(self):

        cond_x1 = self.lon_min
        cond_x2 = self.lon_max
        cond_y1 = self.lat_min
        cond_y2 = self.lat_max
        cond_z1 = self.dep_min
        cond_z2 = self.dep_max

        x_edge = linspace(cond_x1, cond_x2, self.nx)
        y_edge = linspace(cond_y1, cond_y2, self.ny)
        z_edge = linspace(cond_z1, cond_z2, self.nz)

        ini = read_csv("xyzm.dat", delim_whitespace=True)
        ini = ini[(ini.LON.values>=cond_x1)&(ini.LON.values<=cond_x2)&(ini.LAT.values>=cond_y1)&(ini.LAT.values<=cond_y2)]
        cat = array(loadtxt('select3D.cat', dtype=str)[:,1:4], dtype=float)
        cat = cat[(cat[:,1]>=cond_x1)&(cat[:,1]<=cond_x2)&(cat[:,0]>=cond_y1)&(cat[:,0]<=cond_y2)]

        init_plotting_isi(18,25)
        plt.rc('font', family='Times New Roman')
        plt.rcParams['xtick.labelsize'] = 7
        plt.rcParams['ytick.labelsize'] = 7
        plt.rcParams['axes.labelsize']  = 9

#        faults = get_faults()
##        tehran = get_tehran()
#        bushehr = get_bushehr()

        w = 1
        
        #if self.LogN == 1: norm = LogNorm()
        #else: norm = None 
   
        axl1 = plt.axes([.08,.53,.59,.28])
        axl1.tick_params(axis='x', which='both', bottom=False, top=False,  labelbottom=False)
#        axl1.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        d, X, Y = histogram2d(ini.LON.values, ini.LAT.values, bins=[x_edge, y_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        D1 = D.max()
        im = axl1.imshow(D, origin = "lower", interpolation = "none", extent=[x_edge[0], x_edge[-1], y_edge[0], y_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D1))
        divider = make_axes_locatable(axl1)
        cax = divider.append_axes("bottom", size="4%", pad=0.02)
        cb = plt.colorbar(im, cax=cax, orientation='horizontal')
        tick_locator = ticker.MaxNLocator(nbins=4)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.set_label('Number of event (#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axl1.locator_params(axis='x', nbins=5)
        axl1.locator_params(axis='y', nbins=5)
        axl1.set_ylabel('Latitude (deg)')
        axl1.set_aspect("auto")
#        for f in faults: axl1.plot(faults[f]["LON"], faults[f]["LAT"], color="k", lw=1)
#        for t in bushehr: axl1.plot(bushehr[t]["LON"], bushehr[t]["LAT"], color="r", lw=2)
        draw_fault_simple(axl1)
        draw_fault_names(axl1)
        draw_border(axl1, "Bushehr")
        axl1.set_xlim(x_edge[0], x_edge[-1]) 
        axl1.set_ylim(y_edge[0], y_edge[-1])
#        axl1.plot(52.110, 35.955, mfc="darkred", mec="k", marker="^", mew=.5, ms=8)
#        axl1.plot(50.962, 36.376, mfc="yellow", mec="k", marker="^", mew=.5, ms=8)
        axl1.plot(50.886, 28.829, mfc="w", mec="k", marker="p", mew=1, ms=13)
        
        axl2 = plt.axes([.08,.815,.61,.15], sharex=axl1)
        axl2.tick_params(axis='x', which='both', bottom=False, top=True,  labelbottom=False, labeltop=True)
        axl2.xaxis.set_label_position('top') 
        axl2.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.1)
        d, X, Y = histogram2d(ini.LON.values, ini.DEPTH.values, bins=[x_edge, z_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        D2 = D.max()
        im = axl2.imshow(D, origin = "lower", interpolation = "none", extent=[x_edge[0], x_edge[-1], z_edge[0], z_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D2))
        divider = make_axes_locatable(axl2)
        cax = divider.append_axes("right", size="3%", pad=0.02)
        cb = plt.colorbar(im, cax=cax)
        #tick_locator = ticker.MaxNLocator(nbins=4)
        #cb.locator   = tick_locator
        #cb.update_ticks()
        cb.set_label('(#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axl2.set_ylim(z_edge[0], z_edge[-1])
        axl2.set_xlabel('Longitude (deg)')
        axl2.set_ylabel('Depth (km)')
        axl2.set_aspect("auto")


        axl3 = plt.axes([.677,.542,.185,.268], sharey=axl1)
        axl3.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
        axl3.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.1)
        d, X, Y = histogram2d(ini.DEPTH.values, ini.LAT.values, bins=[z_edge, y_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        D3 = D.max()
        im = axl3.imshow(D, origin = "lower", interpolation = "none", extent=[z_edge[0], z_edge[-1], y_edge[0], y_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D3))
        divider = make_axes_locatable(axl3)
        cax = divider.append_axes("right", size="6%", pad=0.02)
        cb = plt.colorbar(im, cax=cax)
        #tick_locator = ticker.MaxNLocator(nbins=4)
        #cb.locator   = tick_locator
        #cb.update_ticks()
        cb.set_label('(#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axl3.set_xlim(z_edge[0], z_edge[-1])
        axl3.set_xlabel('Depth (km)')
        axl3.set_aspect("auto")


        axr1=plt.axes([.08,.032,.59,.28], sharex=axl1, sharey=axl1)
        axr1.tick_params(axis='x', which='both', bottom=False, top=False,  labelbottom=False)
#        axr1.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        d, X, Y = histogram2d(cat[:,1], cat[:,0], bins=[x_edge, y_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        im = axr1.imshow(D, origin = "lower", interpolation = "none", extent=[x_edge[0], x_edge[-1], y_edge[0], y_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D1))
        divider = make_axes_locatable(axr1)
        cax = divider.append_axes("bottom", size="4%", pad=0.02)
        cb = plt.colorbar(im, cax=cax, orientation='horizontal')
        tick_locator = ticker.MaxNLocator(nbins=4)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.set_label('Number of event (#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axr1.locator_params(axis='x', nbins=5)
        axr1.locator_params(axis='y', nbins=5)
        axr1.set_ylabel('Latitude (deg)')
        axr1.set_aspect("auto")
#        for f in faults: axr1.plot(faults[f]["LON"], faults[f]["LAT"], color="k", lw=1)
#        for t in bushehr: axr1.plot(bushehr[t]["LON"], bushehr[t]["LAT"], color="r", lw=2)
        draw_fault_simple(axr1)
        draw_fault_names(axr1)
        draw_border(axr1, "Bushehr")
        axr1.set_xlim(x_edge[0], x_edge[-1]) 
        axr1.set_ylim(y_edge[0], y_edge[-1]) 
#        axr1.plot(52.110, 35.955, mfc="darkred", mec="k", marker="^", mew=.5, ms=8)
#        axr1.plot(50.962, 36.376, mfc="yellow", mec="k", marker="^", mew=.5, ms=8)
        axr1.plot(50.886, 28.829, mfc="w", mec="k", marker="p", mew=1, ms=13)
        
        axr2=plt.axes([.08,.317,.61,.15], sharex=axl2, sharey=axl2)
        axr2.tick_params(axis='x', which='both', bottom=False, top=True,  labelbottom=False, labeltop=True)
        axr2.xaxis.set_label_position('top') 
        axr2.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.1)
        d, X, Y = histogram2d(cat[:,1], cat[:,2], bins=[x_edge, z_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        im = axr2.imshow(D, origin = "lower", interpolation = "none", extent=[x_edge[0], x_edge[-1], z_edge[0], z_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D2))
        divider = make_axes_locatable(axr2)
        cax = divider.append_axes("right", size="3%", pad=0.02)
        cb = plt.colorbar(im, cax=cax)
        #tick_locator = ticker.MaxNLocator(nbins=4)
        #cb.locator   = tick_locator
        #cb.update_ticks()
        cb.set_label('(#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axr2.set_ylim(z_edge[0], z_edge[-1])
        axr2.set_xlabel('Longitude (deg)')
        axr2.set_ylabel('Depth (km)')
        axr2.set_aspect("auto")

        axr3=plt.axes([.677,.045,.185,.27], sharex=axl3, sharey=axl3)
        axr3.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
        axr3.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.1)
        d, X, Y = histogram2d(cat[:,2], cat[:,0], bins=[z_edge, y_edge])
        D = zoom(d.T, 5, prefilter=False)+1.0
        im = axr3.imshow(D, origin = "lower", interpolation = "none", extent=[z_edge[0], z_edge[-1], y_edge[0], y_edge[-1]], cmap=plt.cm.jet, norm=colors.LogNorm(1, D3))
        divider = make_axes_locatable(axr3)
        cax = divider.append_axes("right", size="5%", pad=0.02)
        cb = plt.colorbar(im, cax=cax)
        #tick_locator = ticker.MaxNLocator(nbins=4)
        #cb.locator   = tick_locator
        #cb.update_ticks()
        cb.set_label('(#)', fontsize=6, labelpad=1)
        cb.outline.set_linewidth(0.5)
        axr3.set_xlim(z_edge[0], z_edge[-1])
        axr3.set_xlabel('Depth (km)')
        axr3.set_aspect("auto")

        plt.savefig('select3d.png', dpi=500)
        plt.close()
#        cmd = "gmt psconvert select3d.ps -A -Tg  -E900 -Qt4"
#        os.system(cmd)
#        os.remove('select3d.ps')

#___________________START

#_____01- READ HYPOELLIPSE OUTPUT FILE AND MAKE A SUMMARY FILE

print('\n+++ Reading Hypoellise output file (hypoel.out) and make a summary file ...')

hint_st = 'earthquake location'
hint_ed = '-- magnitude data --'

flag_st = False

with open('hypoel.out') as f:

    event = []
    ep = event_parser()

    for l in f:

        if hint_st in l:

            flag_st = True
            
        elif flag_st and hint_ed in l:

            ep.nei+=1
            ep.evt = event
            ep.write_summary()
            
            flag_st = False
            event = []

        if flag_st:

            event.append(l)

#_____02- READ SUMMARY FILE AND SPLIT EVENTS INTO GENERATED CELLS

print('\n+++ Splitting events into cells ...')

ep.split_evt_into_cell()
ep.extract_from_cell()

#_____03- READ FROM EVENTS INSIDE EACH CELL AND WRITE IN SIMULPS AND HYPO71 FORMATS.

print('\n+++ Writting best events in SIMULPS and HYPO71 formats ...')

sel_cat = genfromtxt('select3D.cat',dtype=object)
sel_cat[:,0] = array(sel_cat[:,0], dtype='datetime64')
sel_cat[:,1:] = array(sel_cat[:,1:], dtype=float)
        
hint_st = 'earthquake location'
hint_ed = '-- magnitude data --'

flag_st = False

with open('hypoel.out') as f:

    event = []
##    ep = event_parser()

    for l in f:

        if hint_st in l:

            flag_st = True
            
        elif flag_st and hint_ed in l:

            ep.evt = event
            ep.wrire_phase(sel_cat)
            
            flag_st = False
            event = []

        if flag_st:

            event.append(l)

#_____04- MAKE STATION AND USED EVENT FILES

print('\n+++ Writting station file in SIMULPS format ...')

ep.wrire_station()
ep.write_used_evts()

print('\n+++ Summary:\n')
print('Number of earthquake in input file                 :%6d'%(ep.nei))
print('Number of selected earthquakes in output file      :%6d'%(ep.neo))
print('Number of selected stations in output file         :%6d'%(ep.num_used_st))
print('Number of cells in x,y,z directions                :%4d,%4d,%4d'%(ep.nx,ep.ny,ep.nz))
print('Maximum Number of earthquake allowded in each cell :%4d'%(ep.me))
print('Best event sortting criteria was based on          : %s'%(ep.sorting_c[ep.sort_id]))
print('Files have been created successfully               : travel.dat,used.dat,staz.dat\n')

#_____05- PLOT RESULTS

print('+++ Plot results ...')

ep.plot_result()

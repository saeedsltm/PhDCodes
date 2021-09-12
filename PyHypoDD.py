#!/home/saeed/Programs/miniconda3/bin/python

import os,sys
from glob import glob
from PyNordicRW import Read_Nordic, Write_Nordic
from PySTA0RW import Read_Nordic_Sta
from obspy import UTCDateTime as utc
from numpy import mean, pi, sqrt, array, diff
from matplotlib import pyplot as plt
from initial_mpl import init_plotting_isi

def k2d(kilometer, radius=6371):

    return kilometer / (2.0 * radius * pi / 360.0)

def d2k(degrees, radius=6371):

    return degrees * (2.0 * radius * pi / 360.0)

class Main():

    def __init__(self):

        self.inp        = input('\n+++ Enter NORDIC file:\n\n')

        print('\n+++ Reading input file(s). Seting initial values...\n')

        self.outdir     = 'output'       
        self.nordic_pha = Read_Nordic(self.inp)
        self.nordic_sta = Read_Nordic_Sta('STATION0.HYP')
        self.used_sta   = []

    def clear(self):

        if not os.path.exists(os.path.join(start.outdir)): os.mkdir(os.path.join(start.outdir))
        for _ in glob(os.path.join(start.outdir, '*')): os.remove(_)
       
        #______MAP NORDIC WEIGHTS TO HYPODD.

        self.w_dic = {' ':1.00,
                      0:1.00,
                      1:0.75,
                      2:0.50,
                      3:0.25,
                      4:0.00,}
       
    def mk_input_file(self):

        print('+++ Preparing hypoDD phase & station files...\n')

        self.hypodd_pha = open(os.path.join(self.outdir,'phase.dat'),'w')
        self.hypodd_sta = open(os.path.join(self.outdir,'station.dat'),'w')
        self.ph2dt_inp  = open(os.path.join(self.outdir,'ph2dt.inp'),'w')
        self.hypoDD_inp = open(os.path.join(self.outdir,'hypoDD.inp'),'w')
        
        #______PARAMETERS FOR "ph2dt", WILL BE SAVED INTO "ph2dt.inp".
        
        self.MAXDIST = 200.0 # Maximum distance (in km) between event pair and station.
        self.MAXSEP  =  10.0 # Maximum distance (radius in km) for searching neighboring events.
        self.MAXNGH  =  10   # Maximum number of neighbors per event.
        self.MINLNKS =   8   # Minimum number of links required to define a neighbor.
        self.MINOBS  =   4   # Minimum number of observations to be selected for each event pair.
        self.MAXOBS  =   99  # Maximum number of observations to be selected for each event pair.

        #______PARAMETERS FOR "hypoDD", WILL BE SAVED INTO "hypoDD.inp".

        self.DIST    = 200.0 # Minimum dist (km) between cluster centroid and station

        #______SET NEW VALUES TO ABOVE PARAMETERS.

        tmp1 = []
        tmp2 = []
        tmp3 = []

        for evt in self.nordic_pha:

            evlon = self.nordic_pha[evt]['HEADER']['L1']['Lon']
            evlat = self.nordic_pha[evt]['HEADER']['L1']['Lat']
            
            if (type(evlon),type(evlat)) != (str,str):

                tmp2.append([evlon,evlat])

                for sta in self.nordic_pha[evt]['PHASE']:

                    if sta in self.nordic_sta['STA']:

                        stlon = self.nordic_sta['STA'][sta]['LON']
                        stlat = self.nordic_sta['STA'][sta]['LAT']

                        tmp1.append(sqrt((stlon-evlon)**2 + (stlat-evlat)**2))
 
        for i in tmp2:

            tmp3.append([])

            for j in tmp2:

                if i!=j:
                    
                    tmp3[-1].append(sqrt((i[0]-j[0])**2 + (i[1]-j[1])**2))

        tmp3 = [mean(_) for _ in tmp3]

        print('+++ Mean distance between each event to all recorded stations  (km):', int(d2k(mean(tmp1))))
        print('+++ Mean distance between each event to all other events       (km):', int(d2k(mean(tmp3))))
        print('')
        
        for evt in self.nordic_pha:

            try:

                h      = self.nordic_pha[evt]['HEADER']['L1']
                OT     = utc(h['Year'],h['Month'],h['Day'],h['Hour'],h['Min'],h['Sec'])
                ID     = str(int(float(evt)*10.))[7:]
                header = '# %4d %02d %02d %02d %02d %5.2f %7.3f %7.3f %5.1f 0.00 0.00 0.00 %4.1f %s\n'%(h['Year'],h['Month'],h['Day'],
                                                                                                         h['Hour'],h['Min'],h['Sec'],
                                                                                                         h['Lat'],h['Lon'],h['Dep'],
                                                                                                         h['RMS'],ID)
                self.hypodd_pha.write(header)

                for sta in self.nordic_pha[evt]['PHASE']:

                    if sta not in self.used_sta:

                        try:

                            self.used_sta.append(sta)

                            slon = self.nordic_sta['STA'][sta]['LON']
                            slat = self.nordic_sta['STA'][sta]['LAT']
                            selv = self.nordic_sta['STA'][sta]['ELV']

                        except KeyError:

                            print('+++ Warning! %-4s Not in STATION0.HYP, But in NORDIC.'%(sta))

                        self.hypodd_sta.write('%-7s %7.3f %7.3f %4.0f\n'%(sta,slat,slon,selv))

                    for pha in self.nordic_pha[evt]['PHASE'][sta]['P']:

                        d    = self.nordic_pha[evt]['PHASE'][sta]['P'][pha]
                        AT   = utc(h['Year'],h['Month'],h['Day'],d['Hour'],d['Min'],d['Sec'])
                        w    = int('0'+str(d['WI']))
                        w    = self.w_dic[w]
                        data = '%-4s %7.3f %5.2f %1s\n'%(sta,AT-OT,w,'P')
                        if (AT-OT)>=0: self.hypodd_pha.write(data)

                    for pha in self.nordic_pha[evt]['PHASE'][sta]['S']:

                        d    = self.nordic_pha[evt]['PHASE'][sta]['S'][pha]
                        AT   = utc(h['Year'],h['Month'],h['Day'],d['Hour'],d['Min'],d['Sec'])
                        w    = int('0'+str(d['WI']))
                        w    = self.w_dic[w]
                        data = '%-4s %7.3f %5.2f %1s\n'%(sta,AT-OT,w,'S')
                        if (AT-OT)>=0: self.hypodd_pha.write(data)
                
            except (TypeError,ValueError):

                print('+++ Something wronge with > ',evt)
                    
        self.hypodd_pha.close()
        self.hypodd_sta.close()

        print('\n+++ Preparing "ph2dt" & "hypoDD" input files...\n')

        self.ph2dt_inp.write("""* ph2dt.inp - input control file for program ph2dt
* Input station file:
station.dat 
* Input phase file:
phase.dat  
*IFORMAT: input format (0 = ph2dt-format, 1 = NCSN format)
*IPHASE: phase (1 = P; 2 = S).
*MINWGHT: min. pick weight allowed [0]
*MAXDIST: max. distance in km between event pair and stations [200]
*MAXSEP: max. hypocentral separation in km [10]
*MAXNGH: max. number of neighbors per event [10]
*MINLNKS: min. number of links required to define a neighbor [8]
*MINOBS: min. number of links per pair saved [8]
*MAXOBS: max. number of links per pair saved [20]
*MINWGHT MAXDIST MAXSEP MAXNGH MINLNKS MINOBS MAXOBS
   0      %3d      %3d     %3d     %3d    %3d     %3d"""%(self.MAXDIST,self.MAXSEP,self.MAXNGH,self.MINLNKS,self.MINOBS,self.MAXOBS))

        self.NLAY  = len(self.nordic_sta['VELO']['Vp'])
        self.RATIO = self.nordic_sta['CNTL']['VpVs']
        self.TOP   = ' '.join([str(_) for _ in self.nordic_sta['VELO']['Dep']])
        self.VEL   = ' '.join([str(_) for _ in self.nordic_sta['VELO']['Vp']])

        self.hypoDD_inp.write("""* Make hypoDD.INP from NORDIC inputs.
*--- input file selection
* cross correlation diff times: (not used)

*
*catalog P & S diff times:
dt.ct
*
* event file:
event.dat
*
* station file:
station.dat
*
*--- output file selection
* original locations:
hypoDD.loc
* relocations:
hypoDD.reloc
* station information:
hypoDD.sta
* residual information:
*hypoDD.res

* source paramater information:
*hypoDD.src

*
*--- data type selection: 
* IDAT:  0 = synthetics; 1= cross corr; 2= catalog; 3= cross & cat 
* IPHA: 1= P; 2= S; 3= P&S
* DIST:max dist (km) between cluster centroid and station 
* IDAT   IPHA   DIST
    2     3     %3d
*
*--- event clustering:
* OBSCC:    min # of obs/pair for crosstime data (0= no clustering)
* OBSCT:    min # of obs/pair for network data (0= no clustering)
* OBSCC  OBSCT    
     0     8        
*
*--- solution control:
* ISTART:       1 = from single source; 2 = from network sources
* ISOLV:        1 = SVD, 2=lsqr
* NSET:         number of sets of iteration with specifications following
*  ISTART  ISOLV  NSET
    2        2      4 
*
*--- data weighting and re-weighting: 
* NITER:                last iteration to use the following weights
* WTCCP, WTCCS:         weight cross P, S 
* WTCTP, WTCTS:         weight catalog P, S 
* WRCC, WRCT:           residual threshold in sec for cross, catalog data 
* WDCC, WDCT:           max dist (km) between cross, catalog linked pairs
* DAMP:                 damping (for lsqr only) 
*       ---  CROSS DATA ----- ----CATALOG DATA ----
* NITER WTCCP WTCCS WRCC WDCC WTCTP WTCTS WRCT WDCT DAMP
*  5      -9     -9   -9   -9   1.0   0.5  -9    -9   20
*  5      -9     -9   -9   -9   1.0   0.5   5     8   20
  5      -9     -9   -9   -9   1.0   1.0  -9    -9   55
  5      -9     -9   -9   -9   1.0   0.8   10   20   50
  5      -9     -9   -9   -9   1.0   0.8   9    15   45
  5      -9     -9   -9   -9   1.0   0.8   8    10   40
*
*--- 1D model:
* NLAY:         number of model layers  
* RATIO:        vp/vs ratio 
* TOP:          depths of top of layer (km) 
* VEL:          layer velocities (km/s)
* NLAY  RATIO 
   %1d     %5.2f
*Loma Prieta model 2 (North America). Depth to top, velocity
* TOP 
%s
* VEL
%s
*
*--- event selection:
* CID:  cluster to be relocated (0 = all)
* ID:   ids of event to be relocated (8 per line)
* CID    
    0      
* ID"""%(self.DIST,self.NLAY,self.RATIO,self.TOP,self.VEL))
        
        self.ph2dt_inp.close()
        self.hypoDD_inp.close()
        print('\n+++ Finito\n')

    def hypoDD2NORDIC(self,inp='hypoDD.reloc'):

        print('+++ Writting hypoDD in NORDIC format [only X,Y,Z will be changed]...\n')

        output = 'hypoDD.out'
        outdic = {}

        x_org  = []
        y_org  = []
        z_org  = []

        x_rlc  = []
        y_rlc  = []
        z_rlc  = []

        with open(inp) as f:

            for l in f:

                ID  = '%0000009.1f'%(float(l[:9])*.1)
                lon = float(l.split()[2])
                lat = float(l.split()[1])
                dep = float(l.split()[3])
                erx = float(l.split()[7])
                ery = float(l.split()[8])
                erz = float(l.split()[9])

                yer = float(l.split()[10])
                mon = float(l.split()[11])
                day = float(l.split()[12])
                hor = float(l.split()[13])
                mnt = float(l.split()[14])
                sec = float(l.split()[15])

                x_rlc.append(lon)
                y_rlc.append(lat)
                z_rlc.append(dep)
        
                for evt in self.nordic_pha:

                    if ID in evt:

                        x_org.append(self.nordic_pha[evt]['HEADER']['L1']['Lon'])
                        y_org.append(self.nordic_pha[evt]['HEADER']['L1']['Lat'])
                        z_org.append(self.nordic_pha[evt]['HEADER']['L1']['Dep'])
                        
                        self.nordic_pha[evt]['HEADER']['L1']['Year'] = yer
                        self.nordic_pha[evt]['HEADER']['L1']['Month'] = mon
                        self.nordic_pha[evt]['HEADER']['L1']['Day'] = day
                        self.nordic_pha[evt]['HEADER']['L1']['Hour'] = hor
                        self.nordic_pha[evt]['HEADER']['L1']['Min'] = mnt
                        self.nordic_pha[evt]['HEADER']['L1']['Sec'] = sec

                        self.nordic_pha[evt]['HEADER']['L1']['Lon'] = lon
                        self.nordic_pha[evt]['HEADER']['L1']['Lat'] = lat
                        self.nordic_pha[evt]['HEADER']['L1']['Dep'] = dep

                        self.nordic_pha[evt]['HEADER']['LE']['LOE'] = erx*1e-3
                        self.nordic_pha[evt]['HEADER']['LE']['LAE'] = ery*1e-3
                        self.nordic_pha[evt]['HEADER']['LE']['DEE'] = erz*1e-3
                        self.nordic_pha[evt]['HEADER']['LE']['CXY'] = 1.0
                        self.nordic_pha[evt]['HEADER']['LE']['CXZ'] = 1.0
                        self.nordic_pha[evt]['HEADER']['LE']['CYZ'] = 1.0

                        outdic[evt] = self.nordic_pha[evt]
                
                        break

        Write_Nordic(inp_dic=outdic, output=output)

        return array(x_org), array(y_org), array(z_org), array(x_rlc), array(y_rlc), array(z_rlc)

    def hypoDD2ZMAP(self, inp='hypoDD.reloc'):

        with open(inp) as f, open('zmap.out', 'w') as g:

            for l in f:

                lon = float(l.split()[2])
                lat = float(l.split()[1])
                dep = float(l.split()[3])
                mag = float(l.split()[16])

                yer = float(l.split()[10])
                mon = float(l.split()[11])
                day = float(l.split()[12])
                hor = float(l.split()[13])
                mnt = float(l.split()[14])
                sec = float(l.split()[15])

                g.write('%7.3f %7.3f %4d %2d %2d %5.2f %5.1f %2d %2d\n'%(lon, lat, yer, mon, day, mag, dep, hor, mnt))
                
#___________________START

ans   = int(input('\n+++ Make hypoDD input files [1] or Convert hypoDD reloc file to NORDIC [2]:\n\n'))

start = Main()

if ans == 1:

    start.clear()
    start.mk_input_file()
        
if ans == 2:

    #_____Convert to Zmap

    start.hypoDD2ZMAP(inp=os.path.join(start.outdir,'hypoDD.reloc'))

    #_____Plot Results

    init_plotting_isi(18,11)

    x_org, y_org, z_org, x_rlc, y_rlc, z_rlc = start.hypoDD2NORDIC(inp=os.path.join(start.outdir,'hypoDD.reloc'))

    ax1 = plt.axes([.05,.5,.40,.45])

    ax1.plot(x_org, y_org, color='k', marker='x', linestyle='', ms=.5)
    ax1.set_title('Initial')

    ax2 = plt.axes([.55,.5,.40,.45],sharex=ax1,sharey=ax1)
    ax2.set_title('HypoDD')

    ax2.plot(x_rlc, y_rlc, color='k', marker='x', linestyle='', ms=.5)

    ax3 = plt.axes([.08,.09,.24,.34])
    ax3.plot(x_org, x_rlc, color='k', marker='x', linestyle='', ms=1)
    ax3.set_xlabel('Initial Lon (Deg)')
    ax3.set_ylabel('HypoDD Lon (Deg)')
    ax3.locator_params(axis = 'x', nbins = 6)
    ax3.locator_params(axis = 'y', nbins = 6)
    bmin = min(array(ax3.get_xbound(),ax3.get_ybound()))
    bmax = max(array(ax3.get_xbound(),ax3.get_ybound()))
    ax3.set_xlim([bmin,bmax])
    ax3.set_ylim([bmin,bmax])
    ax3.plot(ax3.get_xbound(),ax3.get_ybound())
    ax3.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
    
    ax4 = plt.axes([.39,.09,.24,.34])
    ax4.plot(y_org, y_rlc, color='k', marker='x', linestyle='', ms=1)
    ax4.set_xlabel('Initial Lat (Deg)')
    ax4.set_ylabel('HypoDD Lat (Deg)')
    ax4.locator_params(axis = 'x', nbins = 6)
    ax4.locator_params(axis = 'y', nbins = 6)
    bmin = min(array(ax4.get_xbound(),ax4.get_ybound()))
    bmax = max(array(ax4.get_xbound(),ax4.get_ybound()))
    ax4.set_xlim([bmin,bmax])
    ax4.set_ylim([bmin,bmax])
    ax4.plot(ax4.get_xbound(),ax4.get_ybound())
    ax4.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
    
    ax5 = plt.axes([.70,.09,.24,.34])
    ax5.plot(z_org, z_rlc, color='k', marker='x', linestyle='', ms=1)
    ax5.set_xlabel('Initial Dep (km)')
    ax5.set_ylabel('HypoDD Dep (km)')
    ax5.locator_params(axis = 'x', nbins = 6)
    ax5.locator_params(axis = 'y', nbins = 6)
    bmin = min(array(ax5.get_xbound(),ax5.get_ybound()))
    bmax = max(array(ax5.get_xbound(),ax5.get_ybound()))
    ax5.set_xlim([bmin,bmax])
    ax5.set_ylim([bmin,bmax])
    ax5.plot(ax5.get_xbound(),ax5.get_ybound())
    ax5.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
    
    plt.savefig('hypoDD.png', dpi=300)
    plt.close()

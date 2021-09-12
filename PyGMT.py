#!/home/saeed/Programs/miniconda3/bin/python

from gmtpy import GMT
import os, sys
from glob import glob
from numpy import genfromtxt, arange, linspace, array, savetxt, ones, ones_like, loadtxt, pi, sqrt, ceil, append, meshgrid, delete
sys.path.append(os.path.join('utility'))
from PyNordicRW import Read_Nordic
from PyExtHyp import extract_hyp, extract_class, extract_sta_cor, mk_gmt_inp
from commands import getstatusoutput as gso
from obspy.imaging.beachball import MomentTensor as mt
from obspy.imaging.beachball import mt2plane as mt2p

"""
Script for makeing a GMT map. It produces Seismicity map,
Path coverage, Focal mechanism, depth cross sections.

LogChange:

2018-Apr -> Intial.


"""

def k2d(kilometer, radius=6371):

    return kilometer / (2.0 * radius * pi / 360.0)

def d2k(degrees, radius=6371):

    return degrees * (2.0 * radius * pi / 360.0)

#___________________DEFINED GMT DEFAULTS HERE

font_fram  = {'ANNOT_FONT_PRIMARY':'Times-Bold','ANNOT_FONT_SIZE_PRIMARY':6,
              'ANNOT_FONT_SIZE_SECONDARY':6,'HEADER_FONT':'Times-Roman',
              'LABEL_FONT':'Times-Roman','LABEL_FONT_SIZE':6,
              'HEADER_FONT_SIZE':6,'HEADER_OFFSET':'0.5c','FRAME_WIDTH':'.1c',
              'TICK_LENGTH':'.1c','BASEMAP_TYPE':'fancy', 'MAP_SCALE_HEIGHT':'.1c'}

font_crs   = {'ANNOT_FONT_PRIMARY':'Times-Roman','ANNOT_FONT_SIZE_PRIMARY':5,
              'ANNOT_FONT_SIZE_SECONDARY':5,'HEADER_FONT':'Times-Roman',
              'LABEL_FONT':'Times-Roman','LABEL_FONT_SIZE':5,'LABEL_OFFSET':'.05c',
              'HEADER_FONT_SIZE':5,'HEADER_OFFSET':'0.5c','TICK_LENGTH':'.07c','TICK_PEN':'.3p',
              'BASEMAP_TYPE':'fancy', 'FRAME_PEN':'.7p'}

#___________________READ REQUIRED FILES AND DIRECTORIES

print "\n\n+++ Please note the follwings before starting:\n"
print "1- You'll be asked for a project name [let's call it project_name]."
print "2- You need to put the 'NORDIC' file inside the following address:"
print "\n=> ./dbase/event/project_name.\n"
print "3- Rename the 'NORDIC' file to 'hyp.out' or run the command 'hyp' using 'NORDIC' file as input."
print "4- Make sure you've edited the file './par/project_name/topo.par' according to your study area."

project_name = raw_input('\n\n+++ Enter the project name:\n\n')
#project_name = 'baladeh'

print "\n+++ Reading input files ..."

mk_gmt_inp(project_name)

topo_par = genfromtxt(os.path.join('par',project_name,'topo.par'), delimiter='=', comments='#', dtype=str)
topo_dic = {}

for i in topo_par:

    try:

        topo_dic[i[0].strip()] = float(i[1])

    except ValueError:

        topo_dic[i[0].strip()] = i[1].strip()

#____FAULT

flt_norm   = os.path.join(os.environ['GMTHOME'],'fault','normal.txt')
flt_revr   = os.path.join(os.environ['GMTHOME'],'fault','reverse.txt')
flt_lest   = os.path.join(os.environ['GMTHOME'],'fault','strike-slip_l.txt')
flt_rist   = os.path.join(os.environ['GMTHOME'],'fault','strike-slip_r.txt')
flt_letr   = os.path.join(os.environ['GMTHOME'],'fault','thrust_l.txt')
flt_ritr   = os.path.join(os.environ['GMTHOME'],'fault','thrust_r.txt')
flt_thlt   = os.path.join(os.environ['GMTHOME'],'fault','tehran_lt.txt')
flt_thrt   = os.path.join(os.environ['GMTHOME'],'fault','tehran_rt.txt')
flt_minr   = os.path.join('dbase','fault','iran','minor.txt')
fault_n    = os.path.join('dbase','fault','faults_name.dat')
quak_cpt   = os.path.join('dbase','grd','quak.cpt')
teh_bord   = os.path.join('dbase', 'fault','border','tehran.poly')

#____INPUT FILES (DATA & TOPOGRAPHY)

event      = os.path.join('dbase','event',project_name,'gmtxyz.out')
class_evt  = glob(os.path.join('dbase','event',project_name,'class*'))
hyp        = os.path.join('dbase','event',project_name,'hyp.out')
statn      = os.path.join('dbase','event',project_name,'gmtstxy.out')
sta_cor    = os.path.join('dbase','event',project_name,'sta_cor.out')
foc_inp    = os.path.join('dbase','event',project_name,'psmeca.out')

grd_dirc   = os.path.join('dbase','grd')
grd_main   = os.path.join(grd_dirc,topo_dic['GRDFILE'])
grd_smpl   = os.path.join(grd_dirc,'grd_smpl')
grd_grad   = os.path.join(grd_dirc,'grd_grad')

cpt_name   = topo_dic['GMT_CPT']
map_scl    = topo_dic['PROJSCL']
cpt_file   = os.path.join(grd_dirc,'colors.cpt')
leg        = os.path.join('dbase','legend','eq.leg')
tmp_file   = os.path.join('dbase','event',project_name,'tmp.dat')

#****************************** DEFINE MAIN CLASS

class main():

    def __init__(self):

        global leg
        global map_scl
        global states
        global cities

        states = os.path.join('dbase', 'city','states.dat')
        cities = os.path.join('dbase', 'city','cities.dat')

        #______CHECK OUTPUT DIRECTORY

        if not os.path.exists(os.path.join('figures',project_name)):

            os.mkdir(os.path.join('figures',project_name))

        print "+++ Initializing map ..." 

        self.gmt  = GMT(config=font_fram,version='4.5.13')
        
        self.R    = (topo_dic['LON_MIN'], topo_dic['LON_MAX'], topo_dic['LAT_MIN'], topo_dic['LAT_MAX'])
        self.dx   = round((self.R[1]- self.R[0])/6.,1)
        self.dy   = round((self.R[3]- self.R[2])/6.,1)
        self.P    = map_scl
        self.B    = 'a%ff%f/a%ff%fWSne'%(2*self.dx,self.dx,2*self.dy,self.dy)
        self.S    = 'f%f/%f/38/%fk+lKm'%(self.R[0]+.15*(self.R[1]-self.R[0]),self.R[2]+.07*(self.R[3]-self.R[2]),topo_dic['SC_LEN'])
        self.NS   = '%.2f %.2f 22 90 34 BL @;black;@\343'%(self.R[0]+.05*(self.R[1]-self.R[0]),self.R[2]+.08*(self.R[3]-self.R[2]))
        self.NT   = '%.2f %.2f 10 0  19 CT @;black;@ N'%(self.R[0]+.04*(self.R[1]-self.R[0]),self.R[2]+.08*(self.R[3]-self.R[2]))
        self.POSX = 1
        self.POSY = 1
        self.EC   = {'A':'green', 'B':'yellow', 'C':'orange', 'D':'grey', 'E':'black', 'T':'gray'}
        self.ebm  = topo_dic['EQINBIN']
        leg       = open(leg,'w')

        extract_sta_cor(project_name)

        self.evlat, self.evlon, self.evdep, self.evmag, self.evno, self.evgap, self.evdmin,\
                    self.evrms, self.everh, self.everz, self.elipse = extract_hyp(hyp)
        

        #_________MAKE A SIMPLE FRAM AND PLOT BASIC MAP

        self.gmt.psbasemap(R=self.R, J=self.P, B=self.B, X=self.POSX, Y=self.POSY, config={'PLOT_DEGREE_FORMAT':'+D'})

        if topo_dic['TOPORES'].upper() == 'L':

            self.gmt.grdraster('8', R=self.R, I='0.5m', G=grd_smpl, out_discard=True)
            self.gmt.grdgradient(grd_smpl, A='45', G=grd_grad, N='t.9', out_discard=True)
            self.gmt.grd2cpt(grd_grad, L='-1000/5500', S='-1000/5500/500', Z=True, C=cpt_name, out_filename=cpt_file)
            self.gmt.grdimage(grd_smpl, R=True, J=True, C=cpt_file, I=grd_grad)
            
        if topo_dic['TOPORES'].upper() == 'H':
            
            os.system('gmt grdcut %s -R%f/%f/%f/%f -G%s'%(grd_main, self.R[0],self.R[1],self.R[2],self.R[3], grd_smpl)) 
            self.gmt.grdgradient(grd_smpl, A='45', G=grd_grad, N='t.9', out_discard=True)
            self.gmt.grd2cpt(grd_grad, L='0/4000', S='-2000/5500/500', Z=True, C=cpt_name, out_filename=cpt_file)
            self.gmt.grdimage(grd_smpl, R=True, J=True, C=cpt_file, I=grd_grad)

        self.gmt.pscoast(R=True, J=True, S='90/180/255', D='f', C='90/180/225', L=self.S, W='.5p,midnightblue', N='a/.5p,black,-')

    #__________**********CONVERT TO PNG

    def ps2png(self, inp_dir, den=300, bg='white'):

        print '+++ Convert to "png" format ...'

        ps = glob(os.path.join(inp_dir,'*.ps'))

        for p in ps:

            p = p.replace("'","\\'")

            out = p.split('.ps')[0]+'.png'
            cmd = 'convert -density %d -background %s -trim %s %s'%(den, bg, p, out)
            os.system(cmd)

    #__________**********PLOT TYPT A, SEISMICITY
        
        
    def plot_type_A(self):

        """

        In this type user has the follwing options:

        a) Plot event with a constance size or scaled by magnitude.
        b) Plot error elipse.
        c) Plot station distribution.
        d) Plot cross sections.

        """

        print '+++ Start Plotting Type "A" ...'

        self.name = 'seismicity'
        self.D    = 0.05
        self.INC  = 0.10
        
        #_________ PLOT EVENTS WITH ERORR ELIPSSES, STATIONS AND FAULTS.     


        evmag = array([-999.0 if i is None else i for i in self.evmag])

        #_________PLOT EVENTS

        #__NO MAG

        if eval(topo_dic['PLT_EVT']) and not eval(topo_dic['MAG_FLG']):

            print '+++ Start Plotting Type "A" > Seismicity ...'

            tmp = array([self.evlon, self.evlat, self.evdep*-1.0, ones_like(self.evlon)]).T
            self.gmt.psxy(in_rows=tmp, R=True, J=True, S='c%fc'%(self.D), G='white' ,W='.1,red')

            #__PLOT CLASS EVENTS
             
            if topo_dic['PLT_EVC'] == 'True':

                for c in class_evt:

                    color = self.EC[c[-1]]

                    self.gmt.psxy(in_filename=c, R=True, J=True, S='c%fc'%(self.D), G=color ,W='.1,red')

        #_________SCALED BY MAG
                    
        if eval(topo_dic['PLT_EVT']) and eval(topo_dic['MAG_FLG']):

            print '+++ Start Plotting Type "A" > Seismicity ...'

            leg.write('G 0.1c\n')
            leg.write('H 6 Times-Roman --Magnitude--\n')
            leg.write('G 0.3c\n')
        
            m0 = -999.0
            
            for m in (0,2,4,6,7):

                tmp1 = self.evlon[(self.evmag>=m0) & (self.evmag<m)]
                tmp2 = self.evlat[(self.evmag>=m0) & (self.evmag<m)]
                tmp3 = self.evdep[(self.evmag>=m0) & (self.evmag<m)]
                tmp4 = self.evmag[(self.evmag>=m0) & (self.evmag<m)] 

                tmp = array([tmp1,tmp2,tmp3,tmp4])
                tmp.resize(len(tmp),len(tmp[0]))
                tmp = tmp.T

                if m0 == -999.0:

                    self.gmt.psxy(in_rows=tmp, R=True, J=True, S='s%fc'%(self.D*2), G='grey', W='.1,red')
                    if tmp.size: leg.write('S 0.3c s %fc white 0.25p 0.7c No Mag\n'%(self.D*2))
                    
                    m0     = -2.0
                    self.D+=self.INC

                elif m0==0.0:

                    self.gmt.psxy(in_rows=tmp, R=True, J=True, S='c%fc'%(self.D), G='grey', W='.1,red')
                    leg.write('S 0.3c c %fc white 0.25p 0.7c M <= %d\n'%(self.D,m))
                    self.D+=self.INC
                    
                elif 0<m0<6:

                    self.gmt.psxy(in_rows=tmp, R=True, J=True, S='c%fc'%(self.D), G='grey', W='.1,red')
                    leg.write('S 0.3c c %fc white 0.25p 0.7c %d <= M < %d\n'%(self.D,m0,m))
                    self.D+=self.INC

                else:

                    self.gmt.psxy(in_rows=tmp, R=True, J=True, S='c%fc'%(self.D), G='grey', W='.1,red')
                    leg.write('S 0.3c c %fc white 0.25p 0.7c M >= 6\n'%(self.D))
                    self.D+=self.INC
                    
                leg.write('G 0.1c\n')
                m0+=2
            
            #__PLOT CLASSIFIED EVENTS

            if topo_dic['PLT_EVC'] == 'True':

                extract_class(project_name)

                print '+++ Start Plotting Type "A" > Seismicity > Classified Events ...'

                leg.write('G 0.1c\n')
                leg.write('H 6 Times-Roman --Classes--\n')
                leg.write('G 0.3c\n')

                for c in class_evt[::-1]:

                    self.D    = 0.05
                    self.INC  = 0.10
                    evtens    = loadtxt(c)
                    if evtens.ndim == 1: evtens = evtens.reshape((1, evtens.size))
                    color     = self.EC[c[-1]]

                    leg.write('S 0.3c s 0.25c %s 0.25p 0.7c Class %s\n'%(color,c[-1]))
                    leg.write('G 0.1c\n')
                    
                    m0 = -999.0
                    
                    for m in (0,2,4,6,7):

                        if m0 == -999.0:

                            eqs = evtens[(evtens[:,-1]>=m0) & (evtens[:,-1]<m)]
                            self.gmt.psxy(in_rows=eqs, R=True, J=True, S='s%fc'%(self.D*2), G=color ,W='.1,red')
                            m0     = -2.0
                            self.D+=self.INC

                        elif m0<6:

                            eqs = evtens[(evtens[:,-1]>=m0) & (evtens[:,-1]<m)]
                            self.gmt.psxy(in_rows=eqs, R=True, J=True, S='c%fc'%(self.D), G=color ,W='.1,red')
                            self.D+=self.INC

                        else:

                            eqs = evtens[(evtens[:,-1]>=m0) & (evtens[:,-1]<m)]
                            self.gmt.psxy(in_rows=eqs, R=True, J=True, S='c%fc'%(self.D), G=color ,W='.1,red')
                            self.D+=self.INC

                        m0+=2

        #__PLOT CROSS SECTION

        if eval(topo_dic['PLT_EVT']) and eval(topo_dic['PLT_CRS']):

            print '+++ Start Plotting Type "A" > Cross Sections ...'

            tmp = array([start.evlon, start.evlat, start.evdep, ones_like(start.evlon)]).T
            savetxt('evts_T',tmp,fmt='%7.3f')

            crs  = genfromtxt(os.path.join('par',project_name,'cross.dat'), comments='#', dtype=None).tolist()
            foc  = genfromtxt(os.path.join('par',project_name,'faultoncross.dat'), comments='#', dtype=None, delimiter=',').tolist()

            crs  = array(crs)
            if crs.ndim == 1: crs = crs.reshape((1,crs.size))
            lab  = open('labels.dat','w')
            
            cls  = sorted(glob(os.path.join('dbase','event', project_name, 'class*')))

            cls.append('evts_T')
            cls = cls[::-1]
                
            with open('tmp','w') as f:

                for i in crs:

                    depth_min  = float(i[8])
                    depth_max  = float(i[9])
                    depth_inc  = int((depth_max - depth_min)/5.)
                    eq_bin_max = float(i[10])
                    x_len_in_c = 6.0

                    self.gmt_crs  = GMT(config=font_crs,version='4.5.13')

                    #_____PLOT TOPOGRAPHY

                    os.system('project %s -C%s/%s -E%s/%s -G.5 -Dd -Q  > tmp.xy'%(grd_smpl, i[1], i[2], i[4], i[5]))
                    os.system("grdtrack tmp.xy -G%s | awk '{print $3, $4}' > tmp.dh"%grd_smpl)

                    dm = loadtxt('tmp.dh').tolist()

                    dm.append([dm[-1][0], min(dm[0])])
                    dm.insert(0, [dm[0][0], min(dm[-1])])

                    dm = array(dm)
                        
                    h = ceil(max(dm[:,1]) - min(dm[:,1]))
                    h = h - (h % 18)
                    d = ceil(max(dm[:,0]) - min(dm[:,0]))
                    d = d - (d % 10)
                    R = gso("minmax -I.01 tmp.dh")[1][1:]
                    J = ('X%fc'%x_len_in_c,'1.0c')
                    B = '/a%d:Elevation (m):Wse'%(round(h/3,1))
                    G = 'khaki'
                    X = '10'
                    Y = '10'
                    self.gmt_crs.psxy(in_rows=dm, R=R, J=J, B=B, G=G, W='2,gray', X=X, Y=Y)

                    #_____PLOT FAULT'S NAMES ON CROSS-SECTION

                    cmd = 'PyFaultOnProfile.py %s %s %s %s %d 0'%(i[1], i[2], i[4], i[5],float(R.split('/')[2]))
                    os.system(cmd)
                    self.gmt_crs.pstext('fault_on_profile.dat', R=True, J=True, N='')
                    
                    #_____PLOT EQS IN DEPTH
                    
                    dis_h = float(R.split('/')[1])
                    dis_z = depth_max-depth_min
                    scl_z = x_len_in_c * (dis_z / dis_h)
                    R  = (0, dis_h, depth_min, depth_max)
                    J  = ('X%fc'%x_len_in_c,'-%fc'%scl_z)
                    B  = 'a%d:Profile %s - distance (km):/a%df%d:Depth (km):WneS'%(round(d/4,1), i[0]+i[3], depth_inc, depth_inc/2.)
                    S  = 'c'
                    
                    X  = 0
                    Y  = -scl_z*.41
                    A  = ('a'+i[1], i[2], i[4], i[5], i[6], i[7], i[8], i[9]+'f')
                    cc = True
                    
                    for evts in [cls[1],cls[3]]:
                        
                        tmp = loadtxt(evts)
                        if tmp.ndim == 1: tmp = tmp.reshape((1, tmp.size))
                        tmp[:,3][tmp[:,3]==-999.0] = 1.0

                        if not eval(topo_dic['MAG_FLG']):

                            tmp[:,3] = ones_like(tmp[:,3])

                        G   = self.EC[evts[-1]]
                        W   = '1,black'
                        if topo_dic['PLT_EVC'] == 'False': W='2,red'
                        L   = 5
                    
                        with open('crs_data.dat','w') as d:

                            for x,y,z,m in zip(tmp[:,0], tmp[:,1], tmp[:,2], tmp[:,3]*topo_dic['EQ_CRS']):

                                d.write('%7.3f %7.3f %7.3f %f\n'%(x,y,z,m))
                           
                        if cc:

                            self.gmt_crs.pscoupe('crs_data.dat', R=R, J=J, B=B, s=S, A=A, G=G, L=L, W=W, X=X, Y=Y)

                        else:

                            self.gmt_crs.pscoupe('crs_data.dat', R=R, J=J, s=S, A=A, G=G, L=L, W=W, X=X, Y=Y)
                            
                        X  = 0
                        Y  = 0

                        #_____PLOT HISTOGRAM

                        os.system("awk '{print $3}' Aa*_map > hist.dat && rm Aa*")
                        eq_arr = loadtxt('hist.dat')
                        
                        if eq_arr.size > 1:

                            if evts[-1] == 'T':

                                num_eq  = eq_arr.size
                                max_dep = max(eq_arr)
                                d = ceil(max(eq_arr) - min(eq_arr))
                                d = d - (d % 10)
                                t = eq_arr.size
                                t = t - (t % 10)
                                
                            if cc:

                                self.gmt_crs.pshistogram('hist.dat', R=(depth_min, depth_max,0, eq_bin_max), A='', J=('X2.0c',J[1]),
                                                         B='a%ff%d/a%ff%f:Events (#):wN'%(depth_inc,depth_inc/2.,
                                                                                          round(eq_bin_max/4.,1),
                                                                                          round(eq_bin_max/8.,1)),
                                                         W=2, L='', G=self.EC[evts[-1]], X=2.4)
                            else:

                                self.gmt_crs.pshistogram('hist.dat', R=(depth_min, depth_max,0, eq_bin_max), A='', J=('X2.0c',J[1]),
                                                         W=2, L='', G=self.EC[evts[-1]], X=2.4)
                                
                            X = -2.4                           

                        cc = False
                    
                    if topo_dic['PLT_TYP'] in ['C', 'E']: self.plot_foc_on_cs(R, J, A, X, i[11])    
                    self.gmt_crs.save(os.path.join('figures',project_name,project_name+'_crs_'+i[0]+i[3]+'.ps'))

                    #_____PLOT CROSS ON HORIZONTAL MAP

                    A1 = i[1]+' '+i[2]+" 5 0 19 CT @;black;@ "+i[0]
                    A2 = i[4]+' '+i[5]+" 5 0 19 CT @;black;@ "+i[3]
                    
                    lab.write(A1+'\n')
                    lab.write(A2+'\n')
                         
                    f.write('%7.3f %7.3f\n'%(float(i[1]), float(i[2])))
                    f.write('%7.3f %7.3f\n'%(float(i[4]), float(i[5])))
                    f.write('---\n')
            
            lab.close()
            self.gmt.psxy('tmp', R=True, J=True, m='---', W='4,blue')
            self.gmt.pstext('labels.dat', R=True, J=True, W='white,o1,blue')      

        #_________PLOT ERROR ELLIPSE
                
        if topo_dic['PLT_ELP'] == 'True':
            
            print '+++ Start Plotting Type "A" > Seismicity > Error Elipses ...'

            savetxt('tmp', self.elipse, fmt='%7.2f %7.2f %7.2f %7.2f %7.2f')
            self.gmt.psxy('tmp', R=True, J=True, S='E', W='2,red')


        #___________________ PLOT LEGEND & SCALE

        leg.close()

        if eval(topo_dic['PLT_CRS']) or eval(topo_dic['MAG_FLG']):

            x_shift = int(topo_dic['PROJSCL'][1:-1])*1.02

            self.gmt.pslegend(in_filename=leg.name, R=True, J=True, G='gray90', D='x%fc/0c/2c/4c/BL'%(x_shift), C='0.1c/0.1c',L=1,F=True,
                              config={'FRAME_PEN':1,'ANNOT_FONT_PRIMARY':'Palatino-Bold','ANNOT_FONT_SIZE_PRIMARY':6})
        
    #__________**********PLOT TYPT B, STATION CORRECTION
        
        
    def plot_type_B(self):

        """

        In this type user has the follwing options:

        a) Plot station corrections.

        """

        print '+++ Start Plotting Type "B" > Station Corrections ...'

        self.name = 'station_correction'

        #___________________ PLOT STATION CORRECTIONS

        if os.path.exists('tmp'): os.remove('tmp')

        sta_c = genfromtxt(sta_cor, dtype=None)
        data  = []
        
        for i in sta_c:

            data.append(list(i))

        data = array(data)
        tmp  = array(data[:,:3], dtype=float)

        for i in data:

            with open('tmp','a') as f:

                f.write(i[0]+' '+i[1]+" 4 0 19 CT @;black;@ "+i[3].strip()+'\n')

        self.gmt.pstext('tmp', R=True, J=True, D='0/-0.15c', W='white,o1,blue')

        self.gmt.psxy(in_rows=tmp[tmp[:,2]>=0], R=True, J=True, S='+', G='blue', W='1,blue')
        self.gmt.psxy(in_rows=tmp[tmp[:,2]<0] , R=True, J=True, S='+', G='red', W='1,red')
        
        with open('tmp','w') as f:

            f.write('G 0.1c\n')
            f.write('H 6 Times-Roman -Station Correction-\n')
            f.write('G 0.3c\n')
            f.write('S 0.3c + 0.20c blue 0.25p 0.5c +0.20 sec (blue)\n')
            f.write('G 0.3c\n')
            f.write('S 0.3c + 0.20c red  0.25p 0.5c -0.20 sec (red)\n')

        self.x_shift = int(topo_dic['PROJSCL'][1:-1])*1.02    
        self.gmt.pslegend('tmp', R=True, J=True, G='gray90', D='x%fc/0c/2c/1.5c/BL'%(self.x_shift), C='0.1c/0.1c',L=1,F=True,
                          config={'FRAME_PEN':1,'ANNOT_FONT_PRIMARY':'Palatino-Bold','ANNOT_FONT_SIZE_PRIMARY':5})

            
    #__________PlotFocalMechanismOnMapView
        
        
    def plot_type_C(self):

        """

        In this type user has the follwing options:

        a) Plot focal mechanism.

        """

        print '+++ Start Plotting Type "C" > FOCAL MECHANISM ...'

        f_nor = []
        f_rev = []
        f_str = []

        if topo_dic['FOC_TYP'] == 'd':

            for evt in genfromtxt(foc_inp, dtype=str):

                MT = mt(array(evt[3:9], dtype=float), float(evt[9]))
                PL = mt2p(MT)

                if 60 <= PL.rake <= 120 and 20 <= PL.dip <= 80:

                    f_rev.append(evt)

                elif -120 <= PL.rake <= -60 and 20 <= PL.dip <= 80:

                    f_nor.append(evt)

                else:

                    f_str.append(evt)

            f_nor = array(f_nor)
            f_rev = array(f_rev)
            f_str = array(f_str)

            self.gmt.psmeca(in_rows=f_nor, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="green", N="")
            self.gmt.psmeca(in_rows=f_rev, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="red",  N="")
            self.gmt.psmeca(in_rows=f_str, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="blue",  N="")
        
        if topo_dic['FOC_TYP'] == 'a':

            for evt in genfromtxt(foc_inp, dtype=str):

                rake = float(evt[5])
                dip = float(evt[4])

                if 60 <= rake <= 120 and 20 <= dip <= 80:

                    f_rev.append(evt)

                elif -120 <= rake <= -60 and 20 <= dip <= 80:

                    f_nor.append(evt)

                else:

                    f_str.append(evt)

            f_nor = array(f_nor)
            f_rev = array(f_rev)
            f_str = array(f_str)

            self.gmt.psmeca(in_rows=f_nor, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="green", N="")
            self.gmt.psmeca(in_rows=f_rev, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="red",  N="")
            self.gmt.psmeca(in_rows=f_str, R=True, J=True, C="1,black,solid,P.04", S="a%f/7p/5p"%(topo_dic['BB_MPV']), L=.5, G="blue",  N="")
        
        with open('tmp','w') as f:

            f.write('G 0.1c\n')
            f.write('H 6 Times-Roman -Focal Mechanism-\n')
            f.write('G 0.2c\n')
            f.write('S 0.3c s 0.20c blue 0.25p 0.5c Strike-slip\n')
            f.write('G 0.2c\n')
            f.write('S 0.3c s 0.20c red  0.25p 0.5c Revers\n')
            f.write('G 0.2c\n')
            f.write('S 0.3c s 0.20c green  0.25p 0.5c Normal\n')
            
        #___________________ PLOT LEGEND & SCALE

        if topo_dic['PLT_TYP'] == 'C':

            self.x_shift = int(topo_dic['PROJSCL'][1:-1])*1.02

            self.name = 'focal_mechanism'

            self.gmt.pslegend('tmp', R=True, J=True, G='gray90', D='x%fc/0c/2c/1.8c/BL'%(self.x_shift), C='0.1c/0.1c',L=1, F=True,
                              config={'FRAME_PEN':1,'ANNOT_FONT_PRIMARY':'Palatino-Bold','ANNOT_FONT_SIZE_PRIMARY':6})

        if topo_dic['PLT_TYP'] == 'E':

            self.x_shift = int(topo_dic['PROJSCL'][1:-1])*1.02
            self.y_shift = int(topo_dic['PROJSCL'][1:-1])*.16

            self.name = 'seismicity_focal_mechanism'

            self.gmt.pslegend('tmp', R=True, J=True, G='gray90', D='x%fc/0c/2c/1.8c/BL'%(self.x_shift), C='0.1c/0.1c',L=1, F=True,
                              config={'FRAME_PEN':1,'ANNOT_FONT_PRIMARY':'Palatino-Bold','ANNOT_FONT_SIZE_PRIMARY':6}, Y=self.y_shift)
            
    #__________Change BeachBall Position In Cross Section

    def change_bb_pos(self, Afile, R, J, C, dx=1, dy=1):

        """
        Input:
        Afile: a GMT output file of psmeca, starts with Aa or Ad,...
        dx = maximum change in x direction for each beachball (km).
        dy = maximum change in y direction for each beachball (km).

        Output:
        new Afile will be created and will be replaced.
        
        """
        
        d = genfromtxt(Afile)
        if d.ndim == 1: d = d.reshape(1, d.size)
        if not d.size: return []
  
        xmin, xmax = R[0], R[1]
        ymin, ymax = R[2], R[3]

        nx,ny = meshgrid(arange(xmin, xmax, dx), arange(ymin, ymax, dy))

        nx = nx.flatten()
        ny = ny.flatten()

        dic = dict((key, value) for (key, value) in zip(range(nx.size), -ones(nx.size)))

        for px, py, c in zip(d[:,0], d[:,1], range(d[:,0].size)):

            r = sqrt((nx-px)**2 + (ny-py)**2)
            r = r.flatten().argsort()

            for i in r:

                if i not in dic.values():

                    dic[c] = i
                    break

        for i in range(d[:,0].size):

            d[i][10] = nx[dic[i]]
            d[i][11] = ny[dic[i]]

        d = delete(d,[6,7,8,12],1)
        savetxt('tmp.dat', d, fmt='%.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %d')
        self.gmt_crs.psmeca(in_filename='tmp.dat', R=R, J=J, C="1,black,solid,P.01", S="a%f/4p/1p"%(topo_dic['BB_CRS']), L='.001c', G=C, N="")
        os.remove('tmp.dat')

    #__________PlotFocalMechanismOnCrossSection
        
    def plot_foc_on_cs(self, R, J, A, X, ADJ_FC):

        ADJ_FC = eval(ADJ_FC.strip())  

        if ADJ_FC != True:

            if topo_dic['FOC_TYP'] == 'd':
            
                self.gmt_crs.pscoupe(in_filename=foc_inp, R=R, J=J, A=A, S="a%f/4p/.1c"%(topo_dic['BB_CRS']), G="brown", L='.01c', W='.01c,black', X=X)

                os.system(" rm Ad*")

            if topo_dic['FOC_TYP'] == 'a':

                self.gmt_crs.pscoupe(in_filename=foc_inp, R=R, J=J, A=A, S="a%f/4p/.1c"%(topo_dic['BB_CRS']), G="brown", L='0.01p', W='0.01c,black', X=X)

                os.system(" rm Aa*")

        if  ADJ_FC == True:

            if topo_dic['FOC_TYP'] == 'd':

                f_all = genfromtxt(foc_inp)

                self.gmt_crs.pscoupe(in_rows=f_all, R=R, J=J, A=A, S="a%f/1p/.1c"%(.001), G="red", L='.01c', W='.01c,black', X=X)
                Afile = glob('Ad*[!map]')[0]
                self.change_bb_pos(Afile, R, J, C='brown', dx=4, dy=4)
                os.system(" rm Ad*")
                
            if topo_dic['FOC_TYP'] == 'a':

                f_all = genfromtxt(foc_inp)

                self.gmt_crs.pscoupe(in_rows=f_all, R=R, J=J, A=A, S="a%f/1p/.1c"%(.001), G="red", L='.01c', W='.01c,black', X=X)
                Afile = glob('Aa*[!map]')[0]
                self.change_bb_pos(Afile, R, J, C='brown', dx=4, dy=4)
                os.system(" rm Aa*")

    #__________**********PLOT TYPT D, RAY-PATH
        
        
    def plot_type_D(self):

        """

        In this type user has the follwing options:

        a) Plot ray-path.

        """

        print '+++ Start Plotting Type "D" > RAY-PATH ...'

        self.name = 'ray-path'
 
        rays = os.path.join('dbase','event',project_name,'gmtpath.out')
        evts = loadtxt(os.path.join('dbase','event',project_name,'gmtxy.out'))
        stas = os.path.join('dbase','event',project_name,'gmtstxy.out')

        evts[:,2]*=.1

        self.gmt.psxy(rays, R=True, J=True, m='>'  , W='.001p,red')
        self.gmt.psxy(in_rows=evts, R=True, J=True, S='c.1c'  , G='white', W='1,green')
        self.gmt.psxy(stas, R=True, J=True, S='t.3c', G='white', W='5,blue')

      
    #__________********** PLOT FEATURES, FAULTS, STATIONS
        

    def plot_features(self):

        print "+++ Finalizing map ..."


        #_________PLOT TEHRAN BORDER

        if topo_dic['PLT_TYP'] == 'E':

            self.gmt.psxy(teh_bord, R=True, J=True, W='3,red', Y=-self.y_shift)
            
        else:

            self.gmt.psxy(teh_bord, R=True, J=True, W='3,red')
            
        #___________________ PLOT FAULTS

        if topo_dic['PLT_FLT'] == 'True':

            self.gmt.psxy(flt_norm, R=True, J=True, m='---', S='f10p/0.05ct:0.5', W=4)
            self.gmt.psxy(flt_revr, R=True, J=True, m='---', S='f30p/0.05cb:0.5', W=4)
            self.gmt.psxy(flt_lest, R=True, J=True, m='---', S='f30p/0.1cls:.5', W=4)
            self.gmt.psxy(flt_rist, R=True, J=True, m='---', S='f30p/0.1crs:.5', W=4)
            self.gmt.psxy(flt_letr, R=True, J=True, m='---', S='f10p/0.05clt:0.5', W=4)
            self.gmt.psxy(flt_ritr, R=True, J=True, m='---', S='f10p/0.05crt:0.5', W=4)
            self.gmt.psxy(flt_thlt, R=True, J=True, m='---', S='f5p/0.05clt:0.05', W=4)
            self.gmt.psxy(flt_thrt, R=True, J=True, m='---', S='f5p/0.05crt:0.05', W=4)
##            self.gmt.psxy(flt_minr, R=True, J=True, m='---', W=3)

            self.gmt.pstext(fault_n, R=True, J=True, G='black', S='.5p,white,-')

        #___________________ PLOT STATIONS

        if topo_dic['PLT_STA'] == 'True':

            if os.path.exists('tmp'): os.remove('tmp')

            self.gmt.psxy(statn, R=True, J=True, S='t0.1', G='white', W='6,black')

        if topo_dic['PLT_STN'] == 'True':

            for i in loadtxt(statn, dtype=str):

                with open('tmp','a') as f:

                    f.write(i[0]+' '+i[1]+" 5 0 19 CT @;black;@ "+i[2]+'\n')

            self.gmt.pstext('tmp', R=True, J=True, D='0/-0.05', W='white,o1,black')
            
        #___________________ PLOT FEATURS

        features = genfromtxt(os.path.join('par',project_name,'feature.dat'), dtype=str, delimiter=',')
        if features.ndim == 1: features = features.reshape((1, features.size))

        for i in features:

            self.gmt.pstext(in_rows=array([[' '.join(list(i)[2:])]]), R=True, J=True, D='0/.3c')

            if i[0].strip().upper() != 'NONE':

                xy = array([[i[2],i[3]]], dtype=float)
                ss = '%s%.2f'%(i[0].strip(),float(i[1]))

                self.gmt.psxy(in_rows=xy, R=True, J=True, S=ss, G='white', W='1,blue')    

        #___________________ PLOT STATES, CITIES
      
        with open(states) as f:

            for l in f:

                self.gmt.pstext(in_rows=array([[l]]), R=True, J=True, D='0/.2c', G='black', S='.5p,white,-')

                xy = array([[l.split()[0],l.split()[1]]], dtype=float)
                ss = 's0.2c'

                self.gmt.psxy(in_rows=xy, R=True, J=True, S=ss, G='white', W='6,black')

        with open(cities) as f:

            for l in f:

                #self.gmt.pstext(in_rows=array([[l]]), R=True, J=True, D='0/.15c', G='black', S='.5p,white,-')

                xy = array([[l.split()[0],l.split()[1]]], dtype=float)
                ss = 's0.15c'

                #self.gmt.psxy(in_rows=xy, R=True, J=True, S=ss, G='white', W='4,black')
              
        #___________________ SAVE FIGURE

        #self.gmt.pscoast(R=True, J=True, S='90/180/255', D='f', C='90/180/225', L=self.S, W='.5p,midnightblue', N='a/.5p,black,-')

        print "+++ Saving map(s) into file(s) ..."
        
        self.gmt.save(os.path.join('figures',project_name,project_name+'_'+self.name+'.ps')) 


if os.path.exists('tmp'): os.remove('tmp')

#___________________PLOT
        
import warnings
warnings.filterwarnings("ignore")

start = main()

if topo_dic['PLT_TYP'] == 'A':

    start.plot_type_A()

if topo_dic['PLT_TYP'] == 'B':

    start.plot_type_B()

if topo_dic['PLT_TYP'] == 'C':

    start.plot_type_C()

if topo_dic['PLT_TYP'] == 'D':

    start.plot_type_D()

if topo_dic['PLT_TYP'] == 'E':

    start.plot_type_A()
    start.plot_type_C()
    
start.plot_features()
start.ps2png(inp_dir=os.path.join('figures',project_name), den=300, bg='white')

for _ in ['crs_data.dat', 'evts_T', 'hist.dat', 'tmp.dh', 'tmp.xy', 'labels.dat', 'tmp', 'fault_on_profile.dat']:

    if os.path.exists(_): os.remove(_)
                    
print '\n+++ Ho Finito!'


#!/home/saeed/Programs/miniconda3/bin/python

from obspy.imaging.beachball import beach
from obspy.imaging.beachball import mt2axes
from obspy.imaging.beachball import MomentTensor
from obspy import UTCDateTime as utc
import pylab as plt
from numpy import pi, sin, cos, sqrt, ravel
import os
from initial_mpl import init_plotting_isi

"""

Script for make a simple plot of beachball using Nordic file.

ChangeLogs:

06-Feb-2018 > Initial.
05-Jul-2018 > works now if magnitude is not provided (mag=0).
"""

inp_file = input('\n+++ NORDIC file name:\n\n')

if not os.path.exists('figs'):

    os.mkdir('figs')

print('')

def get_qulity(gap, nsta):
    
    # gap: Azimuthal Gap of the event, nsta: Number of used stations
    #
    # Q-A   0 <= gap  < 150 & 9 <= nsta <= 999
    # Q-B   0 <= gap =< 180 &  6 <= nsta <= 9

    if (gap<=150)&(nsta>=9): return "A"
    elif (gap<=180)&(6<=nsta<=9): return "B"
    else: return "O"

    
def sdr2mt(s, d, r):

    """ Convert Strike, Dip, Rake to MT """

    s*=pi/180.0
    d*=pi/180.0
    r*=pi/180.0

    m11 = -sin(d)*cos(r)*sin(2*s) - sin(2*d)*(sin(s)**2)*sin(r)
    m22 =  sin(d)*cos(r)*sin(2*s) - sin(2*d)*(cos(s)**2)*sin(r)
    m33 = sin(2*d)*sin(r)

    m12 = sin(d)*cos(r)*cos(2*s) + 0.5*sin(2*d)*sin(2*s)*sin(r)
    m13 = -cos(2*d)*sin(r)*sin(s) - cos(d)*cos(s)*cos(r)
    m23 =  cos(2*d)*sin(r)*cos(s) - cos(d)*sin(s)*cos(r)

    return m11,m22,m33,m12,m13,m23


def plot_fm(ax=None, ot=None, sta_dic=None, fp=None, mag=None, n=1, plot_sta_nm=False):

    """

    Plot beachball and stations on focal sphere.

    Inputs:

    sta_dic = A dictionary contains station information {'STA':{'AZ':val,'AIN':val,'POL':val}}
    fp      = A list containing fault plan solution [stike, dip, rake] 


    """
    on = ot.strftime('%Y-%m-%dT%H_%M')
    ot = ot.strftime('%Y-%m-%dT%H:%M:%S')
   
    stk = fp[0]
    dip = fp[1]
    rke = fp[2]

    mt      = MomentTensor(sdr2mt(stk, dip, rke),26)
    T, N, P = mt2axes(mt)

    #title = 'OT=%s\nStrike=%d, Dip=%d, Rake=%d'%(ot,stk,dip,rke)
    title = 'No.%d; M=%.1f'%(n+1, mag)
    d         = 100.0
    beachball = beach(fm=[stk,dip,rke], linewidth=0.5, facecolor='grey', )

    ax.add_collection(beachball)

    c1, c2 = 0, 0
    
    for s in sorted(sta_dic):

        AZ  = sta_dic[s]['AZ']
        AIN = sta_dic[s]['AIN']
        POL = sta_dic[s]['POL']

        if AIN > 90.0:

            AIN-=180.0
            AZ+=180.0
            
        r = abs(d*sqrt(2)*sin((AIN/2.0)*pi/180.0))

        x = r*sin(AZ*pi/180.0)
        y = r*cos(AZ*pi/180.0)

        if POL == 'C' or POL == '+' or POL == 'U':

            ax.plot(x, y, marker='o', mfc = 'k', mec = 'k', ms=3, zorder=100, linestyle='')
            if c1 == 0:
                ax.plot(x, y, marker='o', mfc = 'k', mec = 'k', ms=3, zorder=1, label='Compression', linestyle='')
                c1+=1
            
            if plot_sta_nm: ax.text(x,y-7,s,fontsize=10, ha='center',bbox=dict(facecolor='w', edgecolor='k', boxstyle='round,pad=.2'), zorder=100)

        if POL == 'D' or POL == '-':

            ax.plot(x, y, marker='o', mfc = 'w', mec = 'k', mew=0.7, ms=3, zorder=100, linestyle='')
            if c2 == 0:
                ax.plot(x, y, marker='o', mfc = 'w', mec = 'k', mew=0.7, ms=3, zorder=1, label='Dilatation', linestyle='')
                c2+=1
            
            if plot_sta_nm: ax.text(x,y-7,s,fontsize=10, ha='center',bbox=dict(facecolor='w', edgecolor='k', boxstyle='round,pad=.2'), zorder=100)
                    
        ax.set_xlim(-d-8,d+8)
        ax.set_ylim(-d-8,d+8)
        ax.set_xticks([])
        ax.set_yticks([])

    for i,j in zip([P,T],['P','T']):

        AZ  = i.strike
        AIN = i.dip

        r = abs(d*sqrt(2)*sin((AIN/2.0)*pi/180.0))
        x = r*sin(AZ*pi/180.0)
        y = r*cos(AZ*pi/180.0)

    ax.set_aspect('equal')
    ax.set_title(title, fontsize=8)
    
data_dic = {}


with open(inp_file) as f:

    flag = False

    for l in f:

        if l[79:80] == '1' and l[1:20].strip() and l[38:43]:

            flag = True

            year   = int(l[1:5].strip())
            month  = int(l[6:8].strip())
            day    = int(l[8:10].strip())
            hour   = int(l[11:13].strip())
            minute = int(l[13:15].strip())
            second = float(l[16:20])
            lon    = float(l[31:38])
            lat    = float(l[23:30])
            depth  = float(l[38:43])
            nsta   = float(l[48:51])
            try:
                mag    = float(l[56:59])
            except ValueError: mag = 0.0 

            if second >= 60:

                second = second - 60
                minute+=1

            if minute >= 60:

                minute = minute - 60
                hour+=1

            if hour >= 24:

                hour = hour - 24
                day+=1

            ot = utc(year, month, day, hour, minute, second)

            if ot.isoformat() not in data_dic:

                data_dic[ot.isoformat()] = {'ot':ot ,'lon':lon, 'lat':lat, 'depth':depth,'focal':[],'sta_dic':{}, 'mag':mag, 'nsta':nsta}

            if l[79:80] == '1' and not l[38:43].strip():

                flag = False

        if flag and l[79:80] == 'F':

            strike = float(l[1:10])
            dip    = float(l[11:20])
            rake   = float(l[21:30])

            data_dic[ot.isoformat()]['focal'].append(strike)
            data_dic[ot.isoformat()]['focal'].append(dip)
            data_dic[ot.isoformat()]['focal'].append(rake)

        if flag and l[79:80] == 'E':

            gap = float(l[5:8])
            data_dic[ot.isoformat()]['gap'] = gap

        if flag and (l[79:80] == '4' or l[79:80] == ' ') and l[16:17].strip() and l[56:60].strip() and l[75:79].strip():

            sn = l[1:5].strip()
            po = l[16:17]
            ai = float(l[56:60])
            az = float(l[75:79])
            
            data_dic[ot.isoformat()]['sta_dic'][sn] = {}
            data_dic[ot.isoformat()]['sta_dic'][sn]['AZ']=az
            data_dic[ot.isoformat()]['sta_dic'][sn]['AIN']=ai
            data_dic[ot.isoformat()]['sta_dic'][sn]['POL']=po

#___________________PREPARE FOR PLOT
            
inp = []
i   = 1
header = "YEAR\tMO\tDY\tHH\tMM\tSEC\tLAT\tLON\tDEP\tMAG\tSTR\tDIP\tRAK\tPAZ\tPPL\tTAZ\tTPL\tQ\n"

with open('psmeca.dat', 'w') as f:

    f.write(header)
    
    for evt in sorted(data_dic.keys()):
        
        if len(data_dic[evt]['focal']):

            inp.append([data_dic[evt]['ot'],data_dic[evt]['sta_dic'],data_dic[evt]['focal'],data_dic[evt]['mag'], False])

            yer = data_dic[evt]['ot'].year
            mon = data_dic[evt]['ot'].month
            day = data_dic[evt]['ot'].day
            hor = data_dic[evt]['ot'].hour
            mnu = data_dic[evt]['ot'].minute
            sec = data_dic[evt]['ot'].second
            lon = data_dic[evt]['lon']
            lat = data_dic[evt]['lat']
            dep = data_dic[evt]['depth']
            mag = data_dic[evt]['mag']
            gap = data_dic[evt]['gap']
            npol = len([data_dic[evt]['sta_dic'][sn]['POL'] for sn in data_dic[evt]['sta_dic'].keys()])
            stk = data_dic[evt]['focal'][0]
            dip = data_dic[evt]['focal'][1]
            rak = data_dic[evt]['focal'][2]
            mt  = MomentTensor(sdr2mt(stk, dip, rak), 26)
            T, N, P = mt2axes(mt)
            Paz = P.strike
            Ppl = P.dip
            Taz = T.strike
            Tpl = T.dip
            Q = get_qulity(gap, npol)
           
            f.write('%d\t%2d\t%2d\t%2d\t%2d\t%4.1f\t%7.3f\t%7.3f\t%5.1f\t%4.1f\t%4d\t%4d\t%4d\t%4d\t%4d\t%4d\t%4d\t%1s\n'%(yer, mon, day, hor, mnu, sec,
                                                                                                                            lat, lon, dep, mag,
                                                                                                                            stk, dip, rak,
                                                                                                                            Paz, Ppl, Taz, Tpl,
                                                                                                                            Q))
            i+=1

ans = input('\n+++ Enter number of Rows, Columns for each figure [comma seprated, def=5x5]:\n\n')

if ans:

    n       = int(ans.split(',')[0])
    m       = int(ans.split(',')[1])

else:

    n       = 5
    m       = 5


num_fig = len(inp) // (n * m) 
r       = len(inp) % (n * m) 
c       = 0
i       = 0

for i in range(num_fig):

    print('+++ Saveing plot number:',(i+1))

    init_plotting_isi(17.5,21)
#    plt.rc('text', usetex=True)
    plt.rc('font', family='Times New Roman')
    plt.rcParams['axes.labelsize'] = 6
                
    fig, ax_array = plt.subplots(n, m)

    for ax in ravel(ax_array):

        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plot_fm(ax, inp[c][0], inp[c][1], inp[c][2], inp[c][3], c, inp[c][4])
        c+=1

    plt.tight_layout()
    plt.savefig(os.path.join('figs','foc_res%d.png'%(i+1)),dpi=300) 
    plt.close()   

if r:

    print('\n+++ Saveing final plot ...')

    init_plotting_isi(17.5,21)
#    plt.rc('text', usetex=True)
    plt.rc('font', family='Times New Roman')
    plt.rcParams['axes.labelsize'] = 6
                
    fig, ax_array = plt.subplots(n, m)

    for ax in ravel(ax_array):

        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        try:
                 
            plot_fm(ax, inp[c][0], inp[c][1], inp[c][2], inp[c][3], c, inp[c][4])
            c+=1

        except IndexError:

            pass

    plt.tight_layout()
    plt.savefig(os.path.join('figs','foc_res%d.png'%(i+2)),dpi=300)
    plt.close()

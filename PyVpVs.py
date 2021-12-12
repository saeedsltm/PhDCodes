#!/home/saeed/Programs/miniconda3/bin/python

import os
import sys
from PyNordicRW import Read_Nordic
from datetime import datetime as dt
import operator
from numpy import array, sqrt
from scipy.stats import linregress
import pylab as plt
from statsmodels.formula.api import ols
from initial_mpl import init_plotting_isi
from PyMyFunc import get_ot

"""

Script for calculating Vp/Vs.

ChangeLogs:

22-Aug-2017 > Initial.

"""

init_plotting_isi(7,6)
plt.rcParams['axes.labelsize'] = 7
plt.rc('text', usetex=True)
plt.rc('font', family='Times New Roman')
plt.rcParams['xtick.labelsize'] = 5
plt.rcParams['ytick.labelsize'] = 5

phase_dic = {}

def outlier(x, y, r=0.5):

    regression = ols("data ~ x", data=dict(data=y, x=x)).fit()
    test       = regression.outlier_test()
    outliers_ind   = list((i for i,t in enumerate(test.iloc[:,2]) if t < r))
    good_id        = list(set(range(len(x)))-set(outliers_ind))

    return good_id, outliers_ind


def vpvs(d):

    for evt in sorted(d.keys()):
        
        a        = d[evt]
        ot_year  = a['HEADER']['L1']['Year']
        ot_month = a['HEADER']['L1']['Month']
        ot_day   = a['HEADER']['L1']['Day']
        ot_hour  = a['HEADER']['L1']['Hour']
        ot_min   = a['HEADER']['L1']['Min']
        ot_sec   = a['HEADER']['L1']['Sec']
        ot_msec  = int((ot_sec - int(ot_sec))*1e6)

        ot = get_ot(ot_year, ot_month, ot_day, ot_hour, ot_min, ot_sec, ot_msec)

        if not phase_dic.has_key(ot):

            phase_dic[ot] = {}
                    
        for i in a['PHASE']:

            if not phase_dic[ot].has_key(i):

                phase_dic[ot][i] = {'P':None, 'S':None}
                    
            otday    = ot_day

            for Pphase in a['PHASE'][i]['P']:
            
                try:

                    ar_hour = a['PHASE'][i]['P'][Pphase]['Hour']
                    ar_min  = a['PHASE'][i]['P'][Pphase]['Min']
                    ar_sec  = a['PHASE'][i]['P'][Pphase]['Sec']
                    ar_msec = int((ar_sec - int(ar_sec))*1e6)

                except (TypeError, ValueError):
                   
                    break
                       
                ar    = get_ot(ot_year, ot_month, otday, ar_hour, ar_min, ar_sec, ar_msec)  
                delta = ar - ot
                delta = delta.total_seconds()

                if delta > 0.0 and a['PHASE'][i]['P'][Pphase]['WI'] != 4:

                    phase_dic[ot][i]['P'] = delta
                    
            otday = ot_day
            
            for Sphase in a['PHASE'][i]['S']:

                ar_hour = a['PHASE'][i]['S'][Sphase]['Hour']
                ar_min  = a['PHASE'][i]['S'][Sphase]['Min']
                ar_sec  = a['PHASE'][i]['S'][Sphase]['Sec']
                ar_msec = int((ar_sec - int(ar_sec))*1e6)
              
                ar    = get_ot(ot_year, ot_month, otday, ar_hour, ar_min, ar_sec, ar_msec)
                delta = ar - ot
                delta = delta.total_seconds()
                
                if delta > 0.0 and a['PHASE'][i]['S'][Sphase]['WI'] != 4:

                    phase_dic[ot][i]['S'] = delta

            if not phase_dic[ot][i]['S'] or not phase_dic[ot][i]['P']:

                del phase_dic[ot][i]


    # Pepare for plot
    
    p_time = []
    s_time = []

    for ev in sorted(phase_dic):

        if phase_dic[ev]:

            sorted_ev = sorted(phase_dic[ev].items(), key=operator.itemgetter(1))

            x = sorted_ev[0][1]['P']
            y = sorted_ev[0][1]['S']
                
            for p in sorted_ev:

                p_time.append(p[1]['P'] - x)
                s_time.append(p[1]['S'] - y)
    
    googd_id, outliers_ind = outlier(p_time,s_time)
    god_p = []
    god_s = []
    out_p = []
    out_s = []
    
    for _ in googd_id:

        god_p.append(p_time[_])
        god_s.append(s_time[_])

    for _ in outliers_ind:

        out_p.append(p_time[_])
        out_s.append(s_time[_])

    slope, intercept, r_value, p_value, std_err = linregress(god_p, god_s)

    y = slope*array(god_p) + intercept

    ax = plt.subplot(111)
    
    ax.plot(god_p, god_s, linestyle='', marker='o', ms=3, mfc='none', mec='r', mew=.5)
    ax.plot(god_p, y, linestyle=':', lw=1, ms=0, color='k')
    ax.scatter(out_p,out_s, marker='x', c='k', s=5, linewidth=1.0, zorder=100)
    ax.set_xlim(0, max(p_time))
    ax.set_ylim(0, max(s_time))
    ax.set_xlabel('$Pj-Pi (sec)$')
    ax.set_ylabel('$Sj-Si$ (sec)')
    ax.set_title('$Vp/Vs=%4.2f; N=%d; CC=%.2f; StdErr=%.2f$'%(slope,len(god_p),r_value, std_err), fontsize=5)
    ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
    plt.tight_layout()
    plt.savefig('Vp_Vs_%4.2f.png'%(slope),dpi=300)
    plt.close()
    print('\n+++ Vp/Vs=%.2f\n'%(slope))


inp = input('\n\n+++ Enter NORDIC file name:\n\n')
print('')
vpvs(Read_Nordic(inp))

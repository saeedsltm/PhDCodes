#!/home/saeed/Programs/miniconda3/bin/python

import matplotlib.pyplot as plt
import os, sys, glob
from re import split
from initial_mpl import init_plotting_isi
from numpy import genfromtxt, where
from adjustText import adjust_text
import warnings
warnings.filterwarnings("ignore")

#__________________EXTRACT DATA

damp_files = sorted(glob.glob('damp_*'),key=lambda x:float(x.split('_')[1].split('.dat')[0]))
#damp_files = sorted(glob.glob('damp_*'),key=lambda x:int(split("_|\.",x)[-2]))

data_var = []
vp_var = []
vpvs_var = []
wet_rms = []
dampings = []
preferred_iter = int(input("\nPrefered Iteration:\n"))
preferred_damp_vp = input("\nIndex and Value from of prefered Vp damping from 'damping.dat file':\n")
preferred_damp_vpvs = input("\nIndex and Value from of prefered VpVs damping from 'damping.dat file':\n")

preferred_damp_vp = [int(preferred_damp_vp.split(",")[0]), float(preferred_damp_vp.split(",")[1])]
preferred_damp_vpvs = [int(preferred_damp_vpvs.split(",")[0]), float(preferred_damp_vpvs.split(",")[1])]

texts = []

dmps = genfromtxt('damping.dat', dtype=float)

for damp_file in damp_files:

    dampings.append(float(split("_|.dat", damp_file)[-2]))
    
    with open(damp_file) as f:

        for l in f:

            if 'INITIAL DATA VARIANCE' in l:

                data_var.append([])
                vp_var.append([0])
                vpvs_var.append([0])
                wet_rms.append([])
                data_var[-1].append(float(next(f)))

            elif 'DATA VARIANCE' in l:
               
                [data_var[-1].append(float(i)) for i in next(f).split()]
                    
            elif 'Vp VARIANCE' in l:
               
                [vp_var[-1].append(float(i)) for i in next(f).split()]

            elif 'VpVs VARIANCE' in l:
               
                [vpvs_var[-1].append(float(i)) for i in next(f).split()]

            elif 'WEIGHTED-RMS' in l:
               
                [wet_rms[-1].append(float(i)) for i in next(f).split()]

dampings = sorted(dampings)

#__________________FIGURE 1

init_plotting_isi(16,7)
plt.rcParams['axes.labelsize'] = 8

ax = plt.subplot(121)
ax.set_facecolor("#f2f2f2")
(i.set_linewidth(0.6) for i in ax.spines.items())

title = 'TOC ($V_p$)'
ax.set_title(title)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

iter1_d  = []
iter1_m  = []
lin_prop = [[(.6,.6,.6),':'],[(.6,.6,.6),'-.'],[(.6,.6,.6),'--'],[(.6,.6,.6),'-'],                 
            [(.2,.2,.2),':'],[(.2,.2,.2),'-.'],[(.2,.2,.2),'--'],[(.2,.2,.2),'-'],
            [(0.,0.,.0),':'],[(.0,.0,.0),'-.'],[(.0,.0,.0),'--'],[(.0,.0,.0),'-']]

for d,m,dmp,lin in zip(data_var,vp_var,dmps[:,0],lin_prop):

    plt.plot(m,d,lw=1,mew=.1,mec='k',marker='o',markersize=2.5,label="%d"%dmp, zorder=1)
#    plt.scatter(m,d,s=1,c='grey',zorder=2)
    iter1_d.append(d[1])
    iter1_m.append(m[1])

ax.plot(iter1_m,iter1_d,lw=1,mew=.1,mfc='w',marker='o',ms=2,c='k',zorder=3)

ax.annotate('Iter=0',
            xy=(vp_var[0][0], data_var[0][0]), xycoords='data',
            xytext=(1, 1), textcoords='offset points',
            horizontalalignment='left', verticalalignment='bottom')
ax.annotate('Iter=1',
            xy=(vp_var[0][1], data_var[0][1]), xycoords='data',
            xytext=(1, 1), textcoords='offset points',
            horizontalalignment='left', verticalalignment='bottom')

ax.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.legend(loc=1,ncol=2, fontsize=6)
xbond = ax.get_xlim()
ybond = ax.get_ylim()
xlen = xbond[1] -xbond[0]
ylen = ybond[1] -ybond[0]
ax.set_xlim(0-.05*xlen,xbond[1]+.05*xlen)
ax.set_ylim(ybond[0]-.05*ylen,ybond[1]+.05*ylen)
ax.annotate(r'$\Theta$=%d, Iter=%d'%(preferred_damp_vp[1],preferred_iter),
            xy=(vp_var[preferred_damp_vp[0]][preferred_iter], data_var[preferred_damp_vp[0]][preferred_iter]), xycoords='data',
            xytext=(30, 2), textcoords='offset points',
            ha='left', va='bottom', arrowprops=dict(arrowstyle="fancy", connectionstyle="arc3,rad=.3", color='gray'))

ax = plt.subplot(122)
ax.set_facecolor("#f2f2f2")
(i.set_linewidth(0.6) for i in ax.spines.items())

title = 'TOC ($V_{p}/V_{s}$)'
ax.set_title(title)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

iter1_d = []
iter1_m = []

for d,m,dmp in zip(data_var,vpvs_var,dmps[:,1]):

    plt.plot(m,d,lw=1,mew=.1,mec='k',marker='o',markersize=2.5,label="%d"%dmp,zorder=1)
#    plt.scatter(m,d,s=1,c='grey',zorder=2)
    iter1_d.append(d[1])
    iter1_m.append(m[1])

ax.plot(iter1_m,iter1_d,lw=1,mew=.1,mfc='w',marker='o',ms=2,c='k',zorder=3)

ax.annotate('Iter=0',
            xy=(vpvs_var[0][0], data_var[0][0]), xycoords='data',
            xytext=(1, 1), textcoords='offset points',
            horizontalalignment='left', verticalalignment='bottom')
ax.annotate('Iter=1',
            xy=(vpvs_var[0][1], data_var[0][1]), xycoords='data',
            xytext=(1, 1), textcoords='offset points',
            horizontalalignment='left', verticalalignment='bottom')

ax.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.legend(loc=1,ncol=2, fontsize=6)
xbond = ax.get_xlim()
ybond = ax.get_ylim()
xlen = xbond[1] -xbond[0]
ylen = ybond[1] -ybond[0]
ax.set_xlim(0-.05*xlen,xbond[1]+.05*xlen)
ax.set_ylim(ybond[0]-.05*ylen,ybond[1]+.05*ylen)
ax.annotate(r'$\Theta$=%d, Iter=%d'%(preferred_damp_vpvs[1],preferred_iter),
            xy=(vpvs_var[preferred_damp_vpvs[0]][preferred_iter], data_var[preferred_damp_vpvs[0]][preferred_iter]), xycoords='data',
            xytext=(30, 2), textcoords='offset points',
            ha='left', va='bottom', arrowprops=dict(arrowstyle="fancy", connectionstyle="arc3,rad=.3", color='gray'))

# Adding inset axes for first iteration of Vp and Vp/Vs

plt.rcParams['xtick.labelsize'] = 4
plt.rcParams['ytick.labelsize'] = 4
plt.rcParams['axes.labelsize']  = 4

### Vp       
ax_inset = plt.axes([.285, .45, .2, .2])
ax_inset.set_title("First Iteration", fontsize=6, pad=1.25)
ax_inset.set_facecolor("#ffffff")
x, y = [], []
for i,j in zip(vp_var, data_var): x.append(i[1]); y.append(j[1])
ax_inset.plot(x, y, lw=1,mew=.15,mfc='w',marker='o',ms=2,c='k',zorder=3)
ax_inset.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax_inset.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax_inset.locator_params(axis='x', nbins=5)
ax_inset.locator_params(axis='y', nbins=5)
ax_inset.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

### Vp/Vs       
ax_inset = plt.axes([.785, .45, .2, .2])
ax_inset.set_title("First Iteration", fontsize=6, pad=1.25)
ax_inset.set_facecolor("#ffffff")
x, y = [], []
for i,j in zip(vpvs_var, data_var): x.append(i[1]); y.append(j[1])
ax_inset.plot(x, y, lw=1,mew=.15,mfc='w',marker='o',ms=2,c='k',zorder=3)
ax_inset.set_xlabel('Model variance (km/s)$^2$',labelpad=.1)
ax_inset.set_ylabel('Data variance (s)$^2$',labelpad=.1)
ax_inset.locator_params(axis='x', nbins=5)
ax_inset.locator_params(axis='y', nbins=5)
ax_inset.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))


plt.tight_layout(pad=.3, w_pad=0.5, h_pad=0.5)   
plt.savefig('TOC.png', dpi=500, quality=100)
plt.close()

#__________________FIGURE 2

init_plotting_isi(12,6)
plt.rcParams['axes.labelsize'] = 7

ans  = preferred_damp_vp[1]
data = wet_rms[dampings.index(ans)]

ax = plt.subplot(111)
ax.set_facecolor("#f2f2f2")
(i.set_linewidth(0.6) for i in ax.spines.items())
ax.axvline(x=preferred_iter, linestyle=":", color="r")
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

ax.plot(data,linewidth=.5,marker='o',markersize=2,mfc='y',mec='k',color='k')
for i,j in enumerate(data):
    ax.annotate('%.4f'%j,
                xy=(i, j), xycoords='data',
                xytext=(0, 1), textcoords='offset points',rotation=5,
                horizontalalignment='left', verticalalignment='bottom', fontsize=6)
ax.set_xlabel('Iteration',labelpad=.1)
ax.set_ylabel('Weighted RMS (s)',labelpad=.1)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
xbond = ax.get_xlim()
ybond = ax.get_ylim()
xlen = xbond[1] -xbond[0]
ylen = ybond[1] -ybond[0]
ax.set_xlim(xbond[0]-.01*xlen, xbond[1]+.08*xlen)
ax.set_ylim(ybond[0]-.05*ylen, ybond[1]+.11*ylen)

x     = range(len(data))
label = range(len(data))

ax.set_xticks(x)
ax.set_xticklabels(label)

plt.tight_layout(pad=.3, w_pad=0.5, h_pad=0.5)   
plt.savefig('WT-RMS.png', dpi=500, quality=100)
plt.close()



import numpy as np
import pylab as plt
import os
from LatLon import lat_lon as ll
from initial_mpl import init_plotting_isi

"""

This script will use hypoellipse program to test
variation in hypocenter for random generated
velocity models.

input files: 

    hypoel.pha, hypoel.sta, hypoel.prm, default.cfg 

outputs:

result.png which is statistics. 

ChangeLogs:

23-Sep-2018 > Initial.

"""

#__________________Create "tmp" folder

if os.path.exists('tmp'):

    cmd = 'rm -rf tmp'
    os.system(cmd)
    os.mkdir('tmp')

else:

    os.mkdir('tmp')

#__________________Check for parameter file, read it into a dict

if not os.path.exists('variation.par'):

    with open('variation.par', 'w') as f:

        f.write('VEL_PERC = 5  # % Error for velocity values in layers.\n')
        f.write('THI_PERC = 5  # % Error for thikness values in depths.\n')
        f.write('NUM_MOD  = 10 # Number of random generated models.\n')
 
par_dic = {}
par = np.genfromtxt('variation.par', dtype=str, delimiter='=')
for item, val in par:
    par_dic[item.strip()] = np.float64(val.strip())

#__________________Read original model from "hypoel.prm"
    
model = np.float64(np.genfromtxt('hypoel.prm', dtype=str)[:,1:])

#__________________Generate random model, save into "tmp" folder

def gen_rand_model(model):

    v_perc = par_dic['VEL_PERC'] * 1e-2
    t_perc = par_dic['THI_PERC'] * 1e-2

    np.random.seed(1)
    v_perc = np.random.uniform(-v_perc,v_perc)
    np.random.seed(1)
    t_perc = np.random.uniform(-t_perc,t_perc)
    
    vel = model[:,0]+model[:,0] * v_perc
    thi = model[:,1]+model[:,1] * t_perc

    model[:,0] = vel
    model[:,1] = thi

    with open(os.path.join('tmp','hypoel.prm'), 'w') as f:

        for v,h,r in model:

            f.write('VELOCITY             %4.2f %5.2f %4.2f\n'%(v,h,r))

#__________________Copy "hypoel.*" files

def copy_hypoel():

    cmd = 'cp hypoel.* default.cfg tmp/'
    os.system(cmd)

#__________________Read "hypoel.sum" file

def read_sum(outname):

    with open('hypoel.sum') as f, open(outname, 'w') as g:

        for l in f:

            lat = (float(l[16:18]), float(l[19:21])+ float(l[21:23]))
            lon = (float(l[24:26]), float(l[27:29])+ float(l[29:31]))
            dep = float(l[31:36])
            lat = ll.Latitude(degree=lat[0], minute=lat[1]).decimal_degree
            lon = ll.Longitude(degree=lon[0], minute=lon[1]).decimal_degree

            g.write('%7.3f %7.3f %5.2f\n'%(lon,lat,dep/100.))
            
#__________________Get initial location results
                                         
root = os.getcwd()
copy_hypoel()
cmd = 'hypoell-loc.sh hypoel'
os.system(cmd)
read_sum('ini')

#__________________Relocate using new generated model

for i in range(int(par_dic['NUM_MOD'])):
    
    gen_rand_model(model)
    os.chdir('tmp')
    cmd = 'hypoell-loc.sh hypoel'
    os.system(cmd)
    read_sum(str(i))
    os.chdir(root)

#__________________Plot results

init_plotting_isi(6,5)
plt.rc('text', usetex=True)
plt.rc('font', family='Times New Roman')
plt.rcParams['xtick.labelsize'] = 4
plt.rcParams['ytick.labelsize'] = 4
plt.rcParams['axes.labelsize']  = 4
        
ax = plt.subplot(111)
ini = np.genfromtxt('ini')
X = []
Y = []

for i in range(int(par_dic['NUM_MOD'])):

    inp = np.genfromtxt('tmp/%d'%(i))
    dif = ini - inp
    dh = np.sqrt(dif[:,0]**2 + dif[:,1]**2)
    dz = np.abs(dif[:,2])
    X.append(dz)
    Y.append(dh)
X = np.array(X).flatten()
Y = np.array(Y).flatten()

ax.plot(X, Y, marker='o', mfc='r', mec='grey', mew=.3, ms=3, ls='', alpha=.75)
ax.plot(ax.get_xbound(),ax.get_xbound(), color='orange', lw=.7)
ax.set_ylim(ax.get_xbound())
ax.set_xlabel('Real Depth Error (km)')
ax.set_ylabel('Real Horizontal Error (km)')
ax.locator_params(axis='x', nbins=7)
ax.locator_params(axis='y', nbins=6)
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.set_title('%d events from %d random generated models'%(X.size, int(par_dic['NUM_MOD'])), fontsize=4)

plt.tight_layout()
plt.savefig('result.png', dpi=300)

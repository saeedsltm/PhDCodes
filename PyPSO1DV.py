#!/home/saeed/Programs/miniconda3/bin/python
from numpy import array, append, abs, diff, delete, load, ones_like, savetxt, genfromtxt, mean, std
from pyswarm import pso
import os, sys
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import sample
from string import ascii_letters
from shutil import copy
from initial_mpl import init_plotting_isi
sys.path.append('PYT_PRG')
from PyHyp71 import run_hyp71

print ''
print '============================================='
print '*** Calculate 1D Velocity Model using PSO ***'
print '============================================='
print '\n+++ Start PSO, Please wait...\n'

#___________________CHECK FOR PARAMETER FILE

if not os.path.exists('ParPSO.dat'):

    with open('ParPSO.dat', 'w') as f:

        f.write("""#
# parameters for calculating 1D velocity model
# using Particle Swarm Optimization (PSO).
#
#################################################
#
############################ Parameters for PSO
#
SWARMSIZE     = 100     # Number of paticels (here velocity model) per iteration.
OMEGA         = 0.50    # Low inertia weights (~0) favor exploitation (local search or high convergence), high inertia weights favor exploration (global search or low convergence).
PHIP          = 1.0     # Cognitive parameter.
PHIG          = 2.0     # Social parameter.
MAXITER       = 50      # Maximum number of iteration.
MINSTEP       = 1e-7    # Minimum change between two subsequent best particles.
MINFUNC       = 1e-7    # Minimum change between two subsequent best misfits.
NUMPCPU       = 4       # Number of CPUs used for parrallel computations.
DEBUG         = False   # Report while processing.
OBJFUNC       = Hyp71   # Choose objective function between "Hyp71" (Hypo71 program) or "HypE" (Hypoellipse program).
#
############################ Parameters for 1D velocity model and plotting results.
#
LB            = 3.80, 5.60, 6.10, 0.00, 5.00, 9.01 # Lower band for Vp and Depth.
UB            = 4.10, 6.00, 6.40, 0.01, 9.00,12.00 # Lower band for Vp and Depth.
VpVs          = 1.81    # Vp/Vs.
PLTVELMIN     = 3.0     # Minimum velocity used when plotting.
PLTVELMAX     = 7.0     # Maximum velocity used when plotting.
PLTVELMIN     = -20.0   # Minimum depth used when plotting.
PLTVELMIN     = 2.0     # Maximum depth used when plotting.
PLTTRUEVEL    = True    # Plot [True] or do not [False] true velocity model.
VELTRUE       = 4.4, 4.6, 5.0, 5.20, 5.60 # True velocity [km/s].
DEPTRUE       = 0.0, 4.0, 6.0,  8.0, 10.0 # True depth [km].
LOWVEL        = False   # If "True" low velocity model is permitted otherwise [False] no.
#""")

    print '\n\n+++ No parameter file was found. New "ParPSO.dat" was created.\n    Please edit default values and run again.\n'
    sys.exit()
   
#___________________READ USER PARAMETERS

up = genfromtxt('ParPSO.dat',delimiter='=', dtype=str) # user parameters

swarmsize = int(up[0][1])
omega = float(up[1][1])
phip = float(up[2][1])
phig = float(up[3][1])
maxiter = int(up[4][1])
minstep = float(up[5][1])
minfunc = float(up[6][1])
numcpu = int(up[7][1])
debug = eval(up[8][1].strip())
objfunc = up[9][1].strip()
lb = array([float(_) for _ in up[10][1].split(',')])
ub = array([float(_) for _ in up[11][1].split(',')])
vpvs = float(up[12][1])
vel_min = float(up[13][1])
vel_max = float(up[14][1])
dep_min = float(up[15][1])
dep_max = float(up[16][1])
plttruevel = eval(up[17][1].strip())
vel_true = array([float(_) for _ in up[18][1].split(',')])
dep_true = array([float(_) for _ in up[19][1].split(',')])
lowvel = eval(up[20][1].strip())

#___________________WRITE HYPOELLIPSE VELOCITY MODEL FILE

def write_hypoel_prm(x,vpvs,name):

    model = x.reshape((2,x.size/2)).T

    with open('%s.prm'%name,'w') as f:

        for l in model:

            f.write('VELOCITY             %4.2f  %4.2f %4.2f\n'%(l[0],l[1],vpvs))
       
#___________________DEFINE OBJECTIVE FUNCTION
            
def objcfunc(x, *args):

    name = ''.join(sample(ascii_letters,5))

    # Hypoellipse
    
    if objfunc == 'HypE':

        copy('hypoel.pha','%s.pha'%name)
        copy('hypoel.sta','%s.sta'%name)

        write_hypoel_prm(x,vpvs,name)
        os.system('hypoell-loc.sh %s'%name)

        herr = []
        with open('%s.out'%name) as f:

            for l in f:

                if 'average rms of all events' in l:
                
                    res = float(l.split()[-1])

    # Hyp71
    
    elif objfunc == 'Hyp71':

        vel = x[:x.size/2]
        dep = x[x.size/2:]
        vel_model = array([vel,dep]).T
        res = run_hyp71(hypo71_inp='hypoel.pha', vel_model=vel_model, used_STA0_VEL=False, run_id=name)

    for _ in glob('%s*'%name): os.remove(_)

    # Result

    return res

def conditions(x,*args):
    
    n = args[0]
    d = diff(x[:n])

    return [sum(d-abs(d))]

#___________________RUN PSO

if lowvel:

    res = pso(objcfunc, lb=lb, ub=ub, swarmsize=swarmsize, omega=omega, phip=phip, phig=phig,
              maxiter=maxiter, minstep=minstep, minfunc=minfunc, processes=numcpu,
              particle_output=True, debug=debug)

else:

    res = pso(objcfunc, f_ieqcons=conditions, lb=lb, ub=ub, swarmsize=swarmsize, omega=omega, phip=phip,
              phig=phig, maxiter=maxiter, minstep=minstep, minfunc=minfunc, processes=numcpu,
              particle_output=True, args=(len(ub)/2,), debug=debug)

#___________________DRAW ANIMATION AND SAVE RESULTS

init_plotting_isi(12,8)
plt.rc('text', usetex=True)
plt.rc('font', family='Times New Roman')

ax = plt.subplot(1,1,1)
ax.set_xlabel('Velocity (km/s)')
ax.set_ylabel('Depth (km)')
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.locator_params(axis='x', nbins=5)
ax.locator_params(axis='y', nbins=5)

xdata, ydata = [], []
ln, = plt.plot([], [], marker='o', ms=2, linewidth=1, color='grey', animated=True, label='Calculated')

if plttruevel:
    
    x = array([])
    y = array([])

    for i,j in zip(vel_true,vel_true): x = append(x,array([i,j]))
    for i,j in zip(dep_true,dep_true): y = append(y,array([i,j]))

    y = append(-y[1:],dep_min)

    ax.plot(x, y, marker='', linewidth=1.5, color='red', label='True')

def init():
    ax.set_xlim(vel_min, vel_max)
    ax.set_ylim(dep_min, dep_max)
    return ln,

def update(frame):

    part = load('p_%d.npy'%(frame+1))
     
    X = part[:,:len(lb)/2]
    Y = part[:,len(lb)/2:]

    tmpx = []
    tmpy = []
    for i,j in zip(X.T,X.T):
        tmpx.append(i)
        tmpx.append(j)
    tmpx=array(tmpx)
    for i,j in zip(Y.T,Y.T):
        tmpy.append(-i)
        tmpy.append(-j)
    tmpy.pop(0)
    tmpy.append(ones_like(tmpy[0])*dep_min)
    tmpy=array(tmpy)
    
    ln.set_data(tmpx,tmpy)
    ax.set_title('Iteration=%d'%(frame+1))
    return ln,
    
ani = FuncAnimation(plt.gcf(), update, frames=res[-1], init_func=init, blit=True)

ax.legend(loc=1, fontsize=6)
ani.save('History.gif', writer='imagemagick', fps=3)
savetxt('res.dat',res[0].reshape((2,res[0].size/2)).T, header='fitness=%f'%(res[1]), fmt='%5.2f')
plt.close()

#___________________DRAW STATISTIC PLOT

init_plotting_isi(16,7)
plt.rc('text', usetex=True)
plt.rc('font', family='Times New Roman')
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
plt.rcParams['axes.labelsize']  = 7

ax = plt.subplot(1,2,1)
ax.set_xlabel('Iteration')
ax.set_ylabel('Average RMS (sec)')
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.locator_params(axis='x', nbins=7)
ax.locator_params(axis='y', nbins=6)
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

fps = glob('fp_*npy')
fps = sorted(fps, key=lambda x: int(x.split('_')[1].split('.')[0]))
X,Y = [], []

for i,fp in enumerate(fps):

    fp = load(fp)
    fp_mean = mean(fp)
    fp_std = std(fp)

    x = i+1
    y = fp_mean
    e = fp_std
    if i==0: ax.errorbar(x, y, yerr=e, color='k', capthick=.5, capsize=2, elinewidth=.5, label='StdDev', zorder=1)
    else: ax.errorbar(x, y, yerr=e, color='k', capthick=.5, capsize=2, elinewidth=.5, zorder=1)
    X.append(x)
    Y.append(y)

ax.plot(X, Y, marker='o', ms=2, mfc='w', mec='r',mew=1, linestyle='--', linewidth=1, color='grey', label='Mean', zorder=2)
ax.legend(loc=1, fontsize=4)

ax = plt.subplot(1,2,2)
ax.set_xlabel('Velocity (Km/s)')
ax.set_ylabel('Depth (km)')
ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
ax.locator_params(axis='x', nbins=7)
ax.locator_params(axis='y', nbins=6)
ax.tick_params(axis='both', which='major', labelsize=6)

vel_l = array([(i,j) for i,j in zip(lb[:ub.size/2],lb[:ub.size/2])]).flatten()
vel_u = array([(i,j) for i,j in zip(ub[:ub.size/2],ub[:ub.size/2])]).flatten()
dep_l = array([(i,j) for i,j in zip(ub[ub.size/2:],ub[ub.size/2:])]).flatten()
dep_u = array([(i,j) for i,j in zip(lb[ub.size/2:],lb[ub.size/2:])]).flatten()
dep_l = delete(dep_l,0,0)
dep_u = delete(dep_u,0,0)
dep_l = append(dep_l, -dep_min)
dep_u = append(dep_u, -dep_min)

ax.plot(vel_l, -dep_l, linewidth=1, linestyle=':', color='k', label='Lower band')
ax.plot(vel_u, -dep_u, linewidth=1, linestyle='--', color='k', label='Upper band')

final_model = res[0].reshape((2,res[0].size/2)).T
finvel = array([(i,j) for i,j in zip(final_model[:,0],final_model[:,0])]).flatten()
findep = array([(i,j) for i,j in zip(final_model[:,1],final_model[:,1])]).flatten()
findep = delete(findep,0,0)
findep = append(findep, -dep_min)

ax.plot(finvel, -findep, linewidth=1, color='r', label='Calculated Model')
ax.legend(loc=1, fontsize=4)
ax.set_xlim(vel_min, vel_max)

plt.tight_layout(True)
plt.savefig('Stat.png', dpi=300)

for _ in glob('*npy'): os.remove(_)

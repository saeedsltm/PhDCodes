#!/home/saeed/Programs/miniconda3/bin/python

from fstpso import FuzzyPSO
from numpy import array, append, delete, genfromtxt, loadtxt, mean, savetxt, std
from multiprocess import Pool
from string import ascii_letters as al
from random import sample
import os, sys
from glob import glob
from subprocess import getstatusoutput as gso
import pylab as plt
from initial_mpl import init_plotting_isi

"""

Calculate 1D velocity model using FST-PSO method
for more ifo look at > https://github.com/aresio/fst-pso.

input files: 

    hypoel.pha, hypoel.sta, hypoel.prm, default.cfg 

outputs:

log.out which includes all updated models.
result.png which is statistics. 

ChangeLogs:

25-Jul-2018 > Initial.
03-Nov-2018 > Add multiprocessing capability.
06-Nov-2018 > Add option for plotting results only.

"""

#___________________Read input parameter file

if not os.path.exists('fst-pso.par'):

    with open('fst-pso.par', 'w') as f:

        f.write("""#################################################
#
# Parameter file for FST-PSO program.
#
#################################################
#
VEL_MIN  = 4.2, 4.9, 5.5, 6.0, 6.5               # Lower bound for velocity model.
VEL_MAX  = 4.8, 5.5, 6.1, 6.6, 7.1               # Upper bound for velocity model.
DEP_MIN  = 0.0, 2.0, 6.0,10.0,16.0               # Lower bound for Depth layering.
DEP_MAX  = 0.1, 6.0,10.0,14.0,20.0               # Upper bound for Depth layering.
VpVS_R   = 1.73                                  # Vp/Vs ratio.
NUM_RUN  = 10                                    # Number of FST-PSO runs.
NUM_MD   = 0                                     # Number of models. If Set to 0 then FST-PSO will do it automaticlly.
NUM_IT   = 0                                     # Number of iteration. If Set to 0 then FST-PSO will do it automaticlly.
MDTP     = -25.0                                 # Minimum depth to plot.
RUN_PL   = 3                                     # Multiprocessing mode, 0:Disable,N Number of Processors."""
                )
                
fst_pso_par = dict(genfromtxt('fst-pso.par', dtype=str, skip_header=6, delimiter='=', autostrip=True))
for key in fst_pso_par.copy(): fst_pso_par[key.strip()] = fst_pso_par.pop(key)

for key in fst_pso_par.keys():

    fst_pso_par[key] = array(fst_pso_par[key].split(','), dtype=float)
            
#___________________Define main class

class Main():

    def __init__(self, plot_flag):

        if not plot_flag:

            with open('best_model.dat', 'w'): pass

        self.run_id = 1

        self.vpvs = fst_pso_par['VpVS_R']
        self.vel_min = fst_pso_par['VEL_MIN']
        self.vel_max = fst_pso_par['VEL_MAX']
        self.dep_min = fst_pso_par['DEP_MIN']
        self.dep_max = fst_pso_par['DEP_MAX']
        self.num_md = fst_pso_par['NUM_MD']
        self.num_it = fst_pso_par['NUM_IT']
        self.mdtp = fst_pso_par['MDTP']
        
        self.low_bnd = array([self.vel_min, self.vel_max]).T.tolist()
        self.upr_bnd = array([self.dep_min, self.dep_max]).T.tolist()
        self.search_space = self.low_bnd + self.upr_bnd

    def write_hypoel_prm(self, x, vpvs, name):

        model = x.reshape((2, x.size//2)).T

        with open('%s.prm'%name, 'w') as f:

            for l in model:

                f.write('VELOCITY             %4.2f %5.2f %4.2f\n'%(l[0],l[1],vpvs))

    def write_fst_pso_result(self, result):

        with open('best_model.dat', 'a') as f:

            f.write(' '.join('%7.2f'%(e) for e in result[0].X))
            f.write('\n')

    def write_best_model(self, best_model, best_std):

        with open('best_model.dat', 'a') as f:

            f.write('Best Model (Average of all models and StdDev):\n')
            f.write(' '.join('%7.2f'%(e) for e in best_model))
            f.write('\n')
            f.write(' '.join('%7.2f'%(e) for e in best_std))
            f.write('\n')
            
    def hypoel_obj_f(self, new_model):

        hypoel_id = ''.join(sample(al, 5))
        r = self.vpvs
        self.write_hypoel_prm(array(new_model), r, hypoel_id)

        cmd = "cp hypoel.sta %s.sta"%(hypoel_id)
        os.system(cmd)
        cmd = "cp hypoel.pha %s.pha"%(hypoel_id)
        os.system(cmd)        
        cmd = "hypoell-loc.sh %s  > /dev/null << EOF\nn\nEOF"%(hypoel_id)
        os.system(cmd)
        cmd = "awk '/average rms of all events/' %s.out"%(hypoel_id)
        # based on rms
        ##rms = float(gso(cmd)[1].split()[-1])
        ##cmd = "rm %s* "%(hypoel_id)
        ##os.system(cmd)
        ##return rms
        # based on location quality (wigthed average in percentage), 2.5 * (a*4 + b*3 + c*2 + d*1)/10.0
        cmd = "grep 'percentage' %s.out | awk '{print 2.5*($2*4+$3*3+$4*2+$5*1)/10.0}'"%(hypoel_id)
        quality = float(gso(cmd)[1])
        cmd = "rm *%s*"%(hypoel_id)
        os.system(cmd)
        return 100.0 - quality
       


    def parallel_fitness_function(self, particles, arg):
        
        N = int(fst_pso_par['RUN_PL'])
        p = Pool(N)
        all_results = p.map(self.hypoel_obj_f, particles)
        p.close()
        
        return all_results

    def run_fst_pso(self):
        
        FP = FuzzyPSO(logfile='log.dat')
        FP.disable_fuzzyrule_minvelocity()
        FP.set_search_space(self.search_space)
        if self.num_md != 0:
            FP.set_swarm_size(self.num_md)
        if fst_pso_par['RUN_PL'] != 0.0:
            FP.set_parallel_fitness(self.parallel_fitness_function, skip_test=True)
            if self.num_it !=0:
                result = FP.solve_with_fstpso(max_iter=self.num_it, dump_best_fitness='best_fitness_%d'%(self.run_id))
            else:
                result = FP.solve_with_fstpso(dump_best_fitness='best_fitness_%d'%(self.run_id))
        else:
            FP.set_fitness(self.hypoel_obj_f, skip_test=True)
            if self.num_it !=0:
                result = FP.solve_with_fstpso(max_iter=self.num_it, dump_best_fitness='best_fitness_%d'%(self.run_id))
            else:
                result = FP.solve_with_fstpso(dump_best_fitness='best_fitness_%d'%(self.run_id))
        self.write_fst_pso_result(result)

    def plot_results(self):
        
        init_plotting_isi(16,7)
        #plt.rc('text', usetex=True)
        plt.rc('font', family='Times New Roman')
        plt.rcParams['xtick.labelsize'] = 6
        plt.rcParams['ytick.labelsize'] = 6
        plt.rcParams['axes.labelsize']  = 7
        
        best_fits = [loadtxt(best_fitness) for best_fitness in glob('best_fitness_*')]
        best_model = mean(loadtxt('best_model.dat'), axis=0)
        bm_std = std(loadtxt('best_model.dat'), axis=0)
        self.write_best_model(best_model, bm_std)
        self.write_hypoel_prm(best_model, self.vpvs, 'hypoel.prm')

        ax = plt.subplot(121)
        ax.set_facecolor("#fafafa")

        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        for best_fit in best_fits: ax.plot(range(1,best_fit.size+1), 100-best_fit, lw=.9)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Hypocenter quality improvment - (WA%)')
        ax.locator_params(axis='x', nbins=7)
        ax.locator_params(axis='y', nbins=6)
        #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))


        ax = plt.subplot(122)
        ax.set_facecolor("#fafafa")
        
        ax.set_xlabel('Velocity (Km/s)')
        ax.set_ylabel('Depth (km)')
        ax.grid(True, linestyle=':', linewidth=.5, color='k', alpha=.3)
        ax.locator_params(axis='x', nbins=7)
        ax.locator_params(axis='y', nbins=6)
        ax.tick_params(axis='both', which='major', labelsize=6)

        vel_l = array([(i,j) for i,j in zip(self.vel_min,self.vel_min)]).flatten()
        vel_u = array([(i,j) for i,j in zip(self.vel_max,self.vel_max)]).flatten()
        dep_u = array([(i,j) for i,j in zip(self.dep_min,self.dep_min)]).flatten()
        dep_l = array([(i,j) for i,j in zip(self.dep_max,self.dep_max)]).flatten()
        dep_l = delete(dep_l,0,0)
        dep_u = delete(dep_u,0,0)
        dep_l = append(dep_l, -self.mdtp)
        dep_u = append(dep_u, -self.mdtp)

        ax.plot(vel_l, -dep_l, linewidth=1, linestyle=':', color='k', label='Lower band')
        ax.plot(vel_u, -dep_u, linewidth=1, linestyle='--', color='k', label='Upper band')

        final_model = best_model.reshape((2, best_model.size//2)).T
        finvel = array([(i,j) for i,j in zip(final_model[:,0],final_model[:,0])]).flatten()
        findep = array([(i,j) for i,j in zip(final_model[:,1],final_model[:,1])]).flatten()
        findep = delete(findep,0,0)
        findep = append(findep, -self.mdtp)

        ax.plot(finvel, -findep, linewidth=1, color='r', label='Best model')

        c=0
        for i in range(finvel.size//2):
            ax.fill_between([finvel[c]-bm_std[i], finvel[c]+bm_std[i]], -findep[c+1], -findep[c], color='r', alpha=.2)
            c+=2
        c=0
        for j in range(finvel.size//2,finvel.size-1):
            ax.fill_between([finvel[c+1], finvel[c+2]], -findep[c+1]-bm_std[j], -findep[c+1]+bm_std[j], color='r', alpha=.2)
            c+=2

        ax.legend(loc=1, fontsize=4)

        plt.savefig('fst-pso_result.png', dpi=500, bbox_inches="tight")
        plt.close()

#___________________Run

ans = input("\n++++ New run [n] or Only plot results [p]:\n\n")

if ans.upper() == "N":

    instance = Main(plot_flag=False)
    for i in range(int(fst_pso_par['NUM_RUN'])):
    
        instance.run_id = i
        instance.run_fst_pso()

    instance.plot_results()
    sys.exit()

else:

    instance = Main(plot_flag=True)
    instance.plot_results()
    sys.exit()

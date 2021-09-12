#!/home/saeed/Programs/miniconda3/bin/python

import matplotlib.pyplot as plt
from matplotlib import ticker
from initial_mpl import init_plotting_isi
from mpl_toolkits.axes_grid1 import make_axes_locatable
from numpy import array, loadtxt, mean, meshgrid, unique, flip, rot90
from glob import glob
import os, sys

#___________________SET FLAG FOR RECOVERY PLOT

ans  = input('\n\n+++ Process for:\n    1-Real case.\n    2-Synthetic test.\n\n')
flag = False

#___________________PLOT SYNTHETICS(INITIAL/FINAL) FOR Vp/VpVs-PERT

for inp_res in ['vp-pert', 'vpvs-pert']:

    pert = glob(os.path.join('..', 'OUTDIR', inp_res, 'lay-*.xyz'))
    pert = sorted(pert, key=lambda x:x.split('/')[-1].split('-')[1].split('.')[0])
    tmp  = []

    if os.path.exists(os.path.join('..','mod.synth')): model_file = os.path.join('..','mod.synth')

    elif os.path.exists(os.path.join('..','model.out')):

        model_file = os.path.join('..','model.out')
        flag = True

        if ans == 2:

            pert_ini = glob(os.path.join('..', '..', 'CREA-SYNTH-MOD', 'OUTDIR', inp_res, 'lay-*.xyz'))
            pert_ini = sorted(pert_ini, key=lambda x:x.split('/')[-1].split('-')[1].split('.')[0])
    
        
    else:

        print '\n\n+++ No input model [mod.synth/model.out] file was found!\n'
        sys.exit(0)
       
    with open(os.path.join(model_file)) as f:

        for i,l in enumerate(f):

            tmp.append(l.split())

            if i==0:

                line = l.split()

                nx = int(line[1])
                ny = int(line[2])
                nz = int(line[3])

            if '  0  0  0' in l: break
            
    nx-=2
    ny-=2
    nz-=2

    dep =  array(tmp[-2][1:-1],dtype=float)

    subplt_x = 3
    if nz%subplt_x == 0: subplt_y = nz/subplt_x
    else: subplt_y = nz/subplt_x + 1

    init_plotting_isi(16,12)
    plt.rcParams['xtick.labelsize'] = 6
    plt.rcParams['ytick.labelsize'] = 6
    plt.rcParams['axes.labelsize']  = 7

    labels = {'vp-pert':'Vp [% of perturbation]',
              'vpvs-pert':'VpVs [% of perturbation]'}


    for c,inp_file in enumerate(pert):

        x = unique(loadtxt(inp_file)[:,3])
        y = unique(loadtxt(inp_file)[:,4])
        z = loadtxt(inp_file)[:,2]
        z = z.reshape(ny,nx)
        if ans == 2: z = flip(z,0)

        X,Y = meshgrid(x, y)
       
        ax = plt.subplot(subplt_x,subplt_y,c+1)
        [_.set_linewidth(0.6) for _ in ax.spines.itervalues()]
        ax.set_aspect('equal')
        ax.xaxis.set_ticks_position('top')
        ax.set_xlim(x.min(),x.max())
        ax.set_ylim(y.min(),y.max())
        
        ax.locator_params(axis='x', nbins=5)
        ax.locator_params(axis='y', nbins=5)

        if ans == 1:
            im = ax.imshow(z, cmap=plt.cm.seismic_r, interpolation='bicubic', extent=[x.min(),x.max(),y.min(),y.max()], vmin=-15., vmax=+15., zorder=1)
        if ans == 2:
            im = ax.pcolormesh(X,Y,z, cmap=plt.cm.seismic_r,  vmin=-5., vmax=+5., zorder=1)
        sc = ax.scatter(X,Y, s=5, color='k', marker='+', linewidth=.25, zorder=2)

        divider = make_axes_locatable(ax)
        cax     = divider.append_axes("bottom", size="5%", pad=0.02)
        cb      = plt.colorbar(im, format='%.0f', cax=cax, orientation="horizontal")

        tick_locator = ticker.MaxNLocator(nbins=5)
        cb.locator   = tick_locator
        cb.update_ticks()
        cb.ax.set_title(labels[inp_res], size=6, y=-6.)
        cb.outline.set_linewidth(0.5)

        bbox=dict(boxstyle="square", ec='olivedrab', fc='white', alpha=.7)
        ax.text(0.04, 0.09,'depth=%d'%(dep[c]), ha='left', va='center', transform=ax.transAxes, bbox=bbox, fontsize=6)

    plt.tight_layout(pad=1.1, w_pad=0.05, h_pad=0.9)           
    plt.savefig('%s.tiff'%(inp_res),dpi=300)
    plt.close()

#___________________PLOT Vp & Vp/Vs RECOVERTY IN %

    if flag and ans ==2: 

        subplt_x = 3
        if nz%subplt_x == 0: subplt_y = nz/subplt_x
        else: subplt_y = nz/subplt_x + 1

        init_plotting_isi(16,12)
        plt.rcParams['xtick.labelsize'] = 6
        plt.rcParams['ytick.labelsize'] = 6
        plt.rcParams['axes.labelsize']  = 7

        labels = {'vp-pert':'Vp [% of recovery]',
                  'vpvs-pert':'VpVs [% of recovery]'}


        for c,inp_file,inp_file_ini in zip(range(len(pert)), pert, pert_ini):

            x = unique(loadtxt(inp_file)[:,3])
            y = unique(loadtxt(inp_file)[:,4])

            z = loadtxt(inp_file)[:,2]
            z = z.reshape(ny,nx)
            z = flip(z,0)

            z_ini = loadtxt(inp_file_ini)[:,2]
            z_ini = z_ini.reshape(ny,nx)
            z_ini = flip(z_ini,0)
            z = z/z_ini*100.
            
            X,Y = meshgrid(x, y)
           
            ax = plt.subplot(subplt_x,subplt_y,c+1)
            [_.set_linewidth(0.6) for _ in ax.spines.itervalues()]
            ax.set_aspect('equal')
            ax.xaxis.set_ticks_position('top')
            ax.set_xlim(x.min(),x.max())
            ax.set_ylim(y.min(),y.max())
            
            ax.locator_params(axis='x', nbins=5)
            ax.locator_params(axis='y', nbins=5)

            im = ax.pcolormesh(X,Y,z, cmap=plt.cm.jet,  vmin=0., vmax=100., zorder=1)
            sc = ax.scatter(X,Y, s=5, color='k', marker='+', linewidth=.25, zorder=2)

            divider = make_axes_locatable(ax)
            cax     = divider.append_axes("bottom", size="5%", pad=0.02)
            cb      = plt.colorbar(im, format='%.0f', cax=cax, orientation="horizontal")

            tick_locator = ticker.MaxNLocator(nbins=5)
            cb.locator   = tick_locator
            cb.update_ticks()
            cb.ax.set_title(labels[inp_res], size=6, y=-7.)
            cb.outline.set_linewidth(0.5)

            bbox=dict(boxstyle="square", ec='olivedrab', fc='white', alpha=.7)
            ax.text(0.04, 0.09,'depth=%d'%(dep[c]), ha='left', va='center', transform=ax.transAxes, bbox=bbox, fontsize=6)

        plt.tight_layout(pad=1.1, w_pad=0.05, h_pad=0.9)           
        plt.savefig('%s_perc.tiff'%(inp_res),dpi=300)
        plt.close()

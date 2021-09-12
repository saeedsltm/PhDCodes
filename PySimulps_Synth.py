#!/home/saeed/Programs/miniconda3/bin/python

import os, sys
from shutil import move, copy, rmtree
from glob import glob
from random import gauss
from datetime import datetime as dt
from datetime import timedelta as td
from LatLon import lat_lon as ll
sys.path.append(os.environ["PYT_PRG"])
from PyMyFunc import k2d
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', 
                    filename='run.log', filemode='w', level=logging.DEBUG)

"""

Script for doing synthetic test with Simulps.

ChangeLogs:

27-Aug-2017 > Initial.
16-Mar-2020 > Add noise to Origin Time and Hypocenter.

"""

#___________________SELECT TESTING MODE

logging.info('Program started.')

test_mode = input('\n\n+++ Choose test mode: Checkerbord [c], Image input [i], Spike [s]:\n\n')
Vperc = input('+++ Percntage of velocity perturbations for Vp and Vp/Vs:\n\n').split(",")
ot_hc_noise = input('+++ Origin Time and Hypocenter noise level (sigma in km):\n\n').split(",")
P_S_sigma = input('+++ Noise level for P and S travel times (sigma in sec):\n\n').split(",")

root_dir  = os.getcwd()

logging.info('Fetched initial parameters from user successfully.')

def main():

    #_________PREPARE INPUT FILES FOR PLOTTING SYNTHETIC MODEL

    with open('crea.inp','w') as f:

        f.write('mod.synth\n')
        f.write('../../SELECTION/staz.dat\n2\n')

    cmd = 'crea-tomo-lay-x-plot.sh < crea.inp > /dev/null'
    os.system(cmd)

    print('+++ Extarcting from Synthetic model...')

    logging.info('Velocity model was extracted and prepared for plotting successfully.')

    #_________PLOT SYNTHETIC MODEL

    input('+++ Edit GMT scripts in the following sub-dirs, then press any key to continue\n   -PLOT-VERIFICA\n   -PLOT-PERT:\n\n')

    os.chdir('PLOT')
    print('+++ Plotting Synthetic model (H)...')
    os.system('./plotHLayerPert.sh > /dev/null')
    print('+++ Plotting Synthetic model (V)...')
    os.system('./plotVLayerPert.sh > /dev/null')
    os.chdir(root_dir)

    logging.info('Plotting Velocity model was successfull.')

    #_________CREAT SYNTHETIC TRAVEL TIMES

    os.chdir('CREA-SYNTH-TRAV')

    cmd = './com2mario-synth > /dev/null'
    print('+++ Running SIMULPS14 (FWD)...')
    os.system(cmd) 

    print('+++ Adding random noise to dataset...')

    p_sigma = float(P_S_sigma[0])
    s_sigma = float(P_S_sigma[1])

    input_traveltimes = "synth.dat"
    noisy_traveltime = "trav+noise.thu"

    with open(input_traveltimes) as f, open(noisy_traveltime, "w") as g:

        for l in f:

            if l[46:50] == "0.00":
            
                # Add noise to Origin Time
                ot = l[:17]
                for i in [2,4,7,9,12]:
                    ot = ot[:i]+ot[i].replace(" ", "0")+ot[i+1:]
                ot = dt.strptime(ot, "%y%m%d %H%M %S.%f") + td(seconds=gauss(0, float(ot_hc_noise[0])))
                ot = ot.strftime("%y%m%d %H%M %S.%f")[:-4]

                # Add noise to Lat/Lon/Dep
                lat = ll.Latitude(degree=float(l[18:20]), minute=float(l[21:26])) + k2d(gauss(0, float(ot_hc_noise[1])))
                lon = ll.Longitude(degree=float(l[28:30]), minute=float(l[31:36])) + k2d(gauss(0, float(ot_hc_noise[1])))
                dep = abs(float(l[38:43]) + gauss(0, float(ot_hc_noise[1])))
                l = "%17s %2dN%5.2f  %2dE%5.2f  %5.2f   0.00\n"%(ot, lat.degree, lat.decimal_minute, lon.degree, lon.decimal_minute, dep)

            for pos in [5, 19, 33, 47, 61, 75]:

                # Add noise to Travel Times
                if l.strip() and l[:4]!="0   " and len(l)>=pos:

                    if l[pos] == "P":
                        
                        l = l[:pos+3]+"%6.2f"%(float(l[pos+3:pos+9])+gauss(0, p_sigma))+l[pos+9:]

                    if l[pos] == "S":
                        
                        l = l[:pos+3]+"%6.2f"%(float(l[pos+3:pos+9])+gauss(0, s_sigma))+l[pos+9:]
            g.write(l)
             
    logging.info('Synthetic travel times generated successfull.')
    os.chdir(root_dir)

    #_________DO INVERSION

    print('+++ Running SIMULPS14 (INV)...')

    os.chdir('INV-SINT-SHOT')

    cmd = './com2mario > /dev/null'
    os.system(cmd)

    logging.info('Inversion was done successfull.')

    #_________PREPARE INPUT FILES FOR PLOTTING FINAL MODEL

    print('+++ Extarcting from Final model...')

    with open('crea.inp','w') as f:

        f.write('model.out\n')
        f.write('../../SELECTION/staz.dat\n2\n')

    cmd = 'crea-tomo-lay-x-plot.sh < crea.inp > /dev/null'
    os.system(cmd)

    logging.info('Velocity model was extracted and prepared for plotting successfully.')

    #_________RESOLUTION TEST

    print('+++ Performing Resolution Test...')

    copy('model.out',os.path.join('RISOLUZIONE','mod3d.out'))
    os.chdir('RISOLUZIONE')

    with open(os.path.join('mod3d.out')) as f:

        tot_line = sum(1 for _ in f)

    with open(os.path.join('mod3d.out')) as f:

        for l in f:

            nx = int(l[4:7])
            ny = int(l[7:10])
            nz = int(l[10:13])
            break

    vpvs_start = int(tot_line-(ny*nz*(1+nx//20)))+(nx//20)
    vs_start = int(tot_line-2*(ny*nz*(1+nx//20)))+(nx//20)

    with open('tmp','w') as f:

        with open('mod3d.out') as g:

            for i,l in enumerate(g):

                if i<vs_start or i>=vpvs_start: f.write(l)

    move('tmp','mod3d.out')

    cmd = './com2mario > /dev/null'
    os.system(cmd)

    for d in ['vp','vpvs']:

        for _ in glob(os.path.join(d,'lay-*')): os.remove(_)
        for _ in glob(os.path.join(d,'spr-*')): os.remove(_)
        for _ in glob(os.path.join(d,'ris-*')): os.remove(_)
        for _ in glob(os.path.join(d,'nodi','*')): os.remove(_)
    
    for ind,kind in zip([1,2],['vp','vpvs']):

        with open('resol2xyz_v2_14.inp','w') as f:

            f.write('\n../../../SELECTION/staz.dat') 
            f.write('\n../../../START/mod.thu\n1\n%d\n1\n0\n'%(ind))

        cmd = 'resol2xyz_v2_14 < resol2xyz_v2_14.inp > /dev/null' 
        os.system(cmd)

        for i in glob('lay-0*'): move(i,kind)
        for i in glob('spr-0*'): move(i,kind)
        for i in glob('ris-0*'): move(i,kind)

        with open('resol2xyz_v2_14.inp','w') as f:

            f.write('\n../../../SELECTION/staz.dat') 
            f.write('\n../../../START/mod.thu\n1\n%d\n3\n'%(ind))

        cmd = 'resol2xyz_v2_14 < resol2xyz_v2_14.inp > /dev/null' 
        os.system(cmd)

        for i in glob('nodo-*'): move(i,os.path.join(kind,'nodi'))

    os.chdir('vp')
    os.system('./plot-lay-smearing-v3.sh > /dev/null')
    os.system('./plot-sez-smearing-v3.sh > /dev/null')
    os.chdir(os.path.join('..','vpvs'))
    os.system('./plot-lay-smearing-v3.sh > /dev/null')
    os.system('./plot-sez-smearing-v3.sh > /dev/null')
    os.chdir(os.path.join('..','..'))

    logging.info('Resolution test was performed successfull.')

    #_________PLOT FINAL MODEL

    os.chdir('PLOT')
    print('+++ Plotting Final model (H)...')
    os.system('./plotHLayerPert.sh > /dev/null')
    print('+++ Plotting Final model (V)...')
    os.system('./plotVLayerPert.sh > /dev/null')    
    
    os.chdir(root_dir)

    logging.info('Plotting final Velocity model was successfull.')

#********************
#********************
#********************
    
#___________________IF IMAGE MODE HAS BEEN SELECTED...
   
if test_mode.upper() == 'I':

    logging.info('Image mode has been selected.')

    #_________MAKE 3D MODEL USING AN IMAGE FILE

    check = os.path.exists('model_par.dat')
    if not check: 
        logging.error('Image file was not found.')
        sys.exit(0)
    
    os.system('PySimulps_MK3DVEL.py')
    logging.info('Synthetic model was created successfully.')

    move('synth.out', os.path.join('CREA-SYNTH-MOD','mod_orig.synth'))
    os.chdir('CREA-SYNTH-MOD')

    ans = input('\n+++ Edit "model_par.dat" file and run again; OR, press any key to continue:\n\n')

    copy('mod_orig.synth', 'mod.synth')
    copy('mod.synth', 'tmp')
    
    with open(os.path.join('mod_orig.synth')) as f:

        tot_line = sum(1 for _ in f)

    with open(os.path.join('mod_orig.synth')) as f:

        for l in f:

            nx = int(l[4:7])
            ny = int(l[7:10])
            nz = int(l[10:13])
            break

    vpvs_start = int(tot_line-(ny*nz*(1+nx//20)))+(nx//20)
    logging.info('Vp/Vs starts at line %d.'%vpvs_start)

    with open('mod.synth','a') as f:

        with open('tmp') as g:  

            for i,l in enumerate(g):

                if i>=vpvs_start: f.write(l)

    logging.info('Synthetic velocity model files were generated successfully.')
    main()

#___________________IF CHECKERBOARD MODE HAS BEEN SELECTED...

elif test_mode.upper() == 'C':

    logging.info('Checkerboard model has been selected.')

    os.chdir('CREA-SYNTH-MOD')

    for i,j,Vper in zip([1,2],['vp.synth','vpvs.synth'], [float(Vperc[0]), float(Vperc[1])]):

        with open('p2synthmod_v2.inp','w') as f:

            f.write("""# file input x p2synthmod.inp
# modello iniziale 1D da perturbare
"../../START/mod.thu"
# modello finale perturbato
mod.synth
# quale modello contiene il file
# 1=Vp; 2=Vp+Vp/Vs; 3=Vp+Qp
2
# quale modello perturbo
# 1=modello sopra (upper) 2=modello sotto (down)
%d
# percentuale di anomalia da aggiungere o togliere all'1D
# rispetto al valore iniziale
%d
# quanti nodi perturbo per ciascun modello 
# (lo fa in entrambi i modelli se voluto)
# (se metti -9 crea il ceckerboard test)
# coordinate NX NY NZ (non cartesiane ma come numero tra 1 e NX 1 e NY 1 e NZ) dei nodi da perturbare 
# contando anche i nodi  1 e NX che sono i nodi esterni a X=-100 X=100
#                        1 e NY che sono i nodi esterni a Y=-100 Y=100
#                        1 e NZ che sono i nodi esterni a Z=-100 Z=100
# tieni conto che aumentando NY si va verso NORD!! NY=0 viene plottato alla base inferiore dello strato
# tieni conto che aumentando NX si va verso DX come e normale fare
-9
9 9 4
9 8 4"""%(i,Vper))

        with open('tmp','w') as f:

            f.write('p2synthmod_v2.inp\n')
            f.write('../../SELECTION/staz.dat\n\n')

        cmd = 'p2synthmod_v2 < tmp > /dev/null'
        os.system(cmd)
        move('mod.synth',j)

    print('\n+++ Generating file parameter for Synthetic model...')

    with open(os.path.join('vp.synth')) as f:

        tot_line = sum(1 for _ in f)

    with open(os.path.join('vp.synth')) as f:

        for l in f:

            _, nx, ny, nz = l.split()

            nx = int(nx)
            ny = int(ny)
            nz = int(nz)
            break

    vpvs_start = int(tot_line-(ny*nz*(1+nx//20)))+(nx//20)

    logging.info('Vp/Vs starts at line %d.'%vpvs_start)

    with open('mod_orig.synth','w') as f:

        with open('vp.synth') as g:

            for i,l in enumerate(g):

                if i<vpvs_start: f.write(l)

        with open('vpvs.synth') as g:

            for i,l in enumerate(g):

                if i>=vpvs_start: f.write(l)

    copy('mod_orig.synth', 'mod.synth')
    copy('mod.synth', 'tmp')

    with open('mod.synth','a') as f:

        with open('tmp') as g:  

            for i,l in enumerate(g):

                if i>=vpvs_start: f.write(l)

    for i in ['tmp', 'vp.synth', 'vpvs.synth', 'p2synthmod_v2.inp']: os.remove(i) 

    logging.info('Synthetic velocity model files were generated successfully.')
    main()

#___________________IF SPIKE MODE HAS BEEN SELECTED...
   
if test_mode.upper() == 'S':

    logging.info('Spike mode has been selected.')

    #_________MAKE 3D MODEL USING AN IMAGE FILE
    
    os.system('PySimulps_SpikeModel.py')
    logging.info('Synthetic velocity model files were generated successfully.')
    os.chdir('CREA-SYNTH-MOD')
    main()


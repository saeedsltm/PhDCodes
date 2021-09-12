#!/home/saeed/Programs/miniconda3/bin/python

"""

Script for evaluation of inversion parameters.

ChangeLogs:

01-May-2020 > Initial.

"""

from fstpso import FuzzyPSO
import numpy as np
from multiprocess import Pool
import os
from shutil import copy
from string import ascii_letters as al
from random import sample

#_________Read Inversion Parameters
inversionVar = []
inversionVarDic = {}
with open("CP.dat") as f:

    for l in f:

        keys = [_.strip() for _ in l.split("=")[0].split(",")]
        vals = eval(l.split("=")[1])

        for key, val in zip(keys, vals):

            inversionVarDic[key] = val
            inversionVar.append(val)

#_________Read Input Files
inputFiles = {}
for key, val in np.loadtxt("INP.dat", dtype=str)[:,:3:2]:

    inputFiles[key] = val

#_________Read Model Files
def readModel(m):
    
    inpModel = np.array([])
    with open(m) as f:

        flag = False

        for l in f:

            if "  0  0  0" in l: flag = True
            if flag:
                _ = np.array(l.split(), dtype=float)
                inpModel = np.append(inpModel, _)

    return inpModel

#_________Write Inversion Parameters            
def writeParam(p):
    
    with open("CNTL", "w") as f:

        l = "  %5d    %1d    %1d    %1d    %1d    %1d    %1d      *** NEQS NSHT NBLS WTSHT KOUT KOUT2 KOUT3\n"%(
            p[0],p[1],p[2],p[3],p[4],p[5],p[6])
        f.write(l)
        l = "   %3d   %.1f  %.2f  %.2f %+.1f   %.1f  %.2f   %.2f *** NITLOC WTSP EIGTOL RMSCUT ZMIN DXMAX RDERR ERCOF\n"%(
            p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14])
        f.write(l)
        l = "   %3d   %.2f %.2f    %1d   %4d   %4d  %3d   %.2f *** NHITCT DVPMX DVSMX idmp VPDMP VSDMP dldmp STL \n"%(
            p[15],p[16],p[17],p[18],p[19],p[20],p[21],p[22])
        f.write(l)
        l = "    %1d    %1d    %1d %.3f    %1d  %.2f    %1d      *** IRES I3D NITMAX SNRMCT IHOMO RMSTOP IFIX \n"%(
            p[23],p[24],p[25],p[26],p[27],p[28],p[29])
        f.write(l)
        l = "  %5.f  %5.f   %.3f  %.3f   %.1f                *** DEL1 DEL2 RES1 RES2 RES3\n"%(
            p[30],p[31],p[32],p[33],p[34])
        f.write(l)
        l = "    %1d    %1d   %.3f   %.3f                     *** NDIP ISKIP SCALE1 SCALE2 \n"%(
            p[35],p[36],p[37],p[38])
        f.write(l)
        l = "  %.1f %.3f    %1d    %1d                     *** XFAC TLIM NITPB1 NITPB2 \n"%(
            p[39],p[40],p[41],p[42])
        f.write(l)
        l = "    %1d    %1d    %1d                          *** IUSEP IUSES INVDEL \n"%(
            p[43],p[44],p[45])
        f.write(l)
        l = "    %3d  %3d  %3d                          *** IUSEQ DAMPQ QVARMAX\n"%(
            p[46],p[47],p[48])
        f.write(l)

#_________Write Inversion Input Files
def writeInputs():
    
    copy(inputFiles["STNS"] ,"STNS")
    copy(inputFiles["MOD"] ,"MOD")
    copy(inputFiles["EQKS"] ,"EQKS")
   
#_________Define Fitness Function
def fitness(p):

    root = os.getcwd() 
    runDir = ''.join(sample(al, 5))
    os.mkdir(runDir)
    os.chdir(runDir)

    writeParam(p)
    writeInputs()

    cmd = "simulps_ingv > /dev/null"
    os.system(cmd)

    inputModel = readModel(inputFiles["TARM"])
    outModel = readModel("model.out")

    fitness = np.linalg.norm(outModel-inputModel)/inputModel.size

    os.chdir(root)
    cmd = "rm -rf %s"%(runDir)
    os.system(cmd)

    return fitness

#_________Parallel Fitness
def parallel_fitness_function(particles, arg):
    
    N = 4
    p = Pool(N)
    particles_results = p.map(fitness, particles)
    p.close()
    
    return particles_results

#_________Run FST-PSO
FP = FuzzyPSO(logfile='log.dat')
FP.set_search_space(inversionVar)
FP.set_swarm_size(5*len(inversionVar))
FP.set_parallel_fitness(parallel_fitness_function, skip_test=True)
result =  FP.solve_with_fstpso()
print("Best solution:", result[0])
print("Whose fitness is:", result[1])
writeParam(result[0].X)

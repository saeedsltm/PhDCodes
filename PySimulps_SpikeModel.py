#!/home/saeed/Programs/miniconda3/bin/python

import math
import os
from shutil import copy

"""
This script is used to generate Spike test for SIMULPS.

ChangeLog:
Init: > 20 May 2020


"""

if not os.path.exists("SpikeTestPar.dat"):

    with open("SpikeTestPar.dat", "w") as f:

        f.write("""# Define Spike Geometry & Perturbation in %. Note that yMax is Lower Corner.
xMin = -75
xMax = +75
yMin = -80
yMax = +80
zMin = +20
zMax = +30
pert = +5
""")

else:

    with open("SpikeTestPar.dat") as f:

        l = next(f)
        l = next(f)
        xMin = float(l.split("=")[-1]); l = next(f)     
        xMax = float(l.split("=")[-1]); l = next(f)
        yMin = float(l.split("=")[-1]); l = next(f)
        yMax = float(l.split("=")[-1]); l = next(f)
        zMin = float(l.split("=")[-1]); l = next(f)
        zMax = float(l.split("=")[-1]); l = next(f)
        pert = float(l.split("=")[-1])

   
# Input/Output Files
parModel = "../START/modthu_v2.inp"
initModel = "../START/mod.thu"
finModel = "CREA-SYNTH-MOD/mod.synth"
orgModel = "CREA-SYNTH-MOD/mod_orig.synth"

# Get Required Parameters 
with open(parModel) as f:

    for i,l in enumerate(f):

        if "#POSIZIONE NODI LUNGO X" in l:

            x_rng = [float(x) for x in next(f).split()]

        if "#POSIZIONE NODI LUNGO Y" in l:

            y_rng = [float(y) for y in next(f).split()]

        if "#POSIZIONE NODI LUNGO Z" in l:

            z_rng = [float(z) for z in next(f).split()]            

nx = len(x_rng)
ny = len(y_rng)
nz = len(z_rng)

xMinInds = x_rng.index(xMin)
xMaxInds = x_rng.index(xMax)
yMinInds = y_rng.index(yMin)
yMaxInds = y_rng.index(yMax)
zMinInds = z_rng.index(zMin)
zMaxInds = z_rng.index(zMax)

x_seg = nx
y_seg = math.ceil(nx/20)
z_seg = y_seg * ny

with open(initModel) as f:

    for i,l in enumerate(f):

        if "  0  0  0" in l:

            vpStart = i+1

# Finding required lins for changing Vp
vpStart = vpStart
YvpLines = []

for z in range(zMinInds, zMaxInds+1):
    
    zStart = z * z_seg + vpStart

    yStart = yMinInds * y_seg + zStart
    yStop = (yMaxInds - yMinInds + 1) * y_seg + yStart

    YvpLines.append([yStart, yStop])

# Finding required lins for changing VpVs
vpvsStart = vpStart + z_seg * nz
YvpvsLines = []

for z in range(zMinInds, zMaxInds+1):
    
    zStart = z * z_seg + vpvsStart

    yStart = yMinInds * y_seg + zStart
    yStop = (yMaxInds - yMinInds + 1) * y_seg + yStart

    YvpvsLines.append([yStart, yStop])

    
xStart = xMinInds
xStop = xMaxInds
pert = 1.0 + pert * .01

# Write to newFile
with open(initModel) as f, open(finModel, "w") as g:

    for i,l in enumerate(f):

        newV = l
        
        #Vp
        for yStart, yStop in YvpLines:
            
            if yStart <= i <= yStop:

                V = [ float(v) for v in l.split() ]
                new = [ v*pert for v in V[xStart:xStop] ]
                newV = V[:xStart]+new+V[xStop:]
                newV = "".join(["%5.2f"%v for v in newV])+"\n"


        #VpVs
        for yStart, yStop in YvpvsLines:
            
            if yStart <= i <= yStop:

                V = [ float(v) for v in l.split() ]
                new = [ v*pert for v in V[xStart:xStop] ]
                newV = V[:xStart]+new+V[xStop:]
                newV = "".join(["%5.2f"%v for v in newV])+"\n"
                
        g.write(newV)

copy(finModel, orgModel)

# Append VpVs again to newFile
with open(orgModel) as f, open(finModel, "a") as g:

    for i,l in enumerate(f):
        
        if i >= vpvsStart :
            
            g.write(l)

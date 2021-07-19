#!/home/saeed/miniconda3/bin/python

from scipy import append, linspace, insert, misc, rot90, c_, r_, flip
from numpy import array, genfromtxt, zeros
from PyMyFunc import scale_data, d2k, k2d
import matplotlib.pyplot as plt
from initial_mpl import init_plotting_isi
import os, sys

"""

Script for make synthetic 3D velocity model,
used for Simulps. This module will be called
by PySimulps_Synth.py, so no need to run ind
-ependently.

ChangeLogs:

27-Aug-2017 > Initial.

"""

if not os.path.exists('model_par.dat'):

    print('\n\n+++ No "model_par.dat" file was found!')
    print('+++ Creating new "model_par.dat" file...')
    print('+++ Done!')
    print('+++ Edit "model_par.dat" file and run again.\n')
    model_file = open('model_par.dat','w')
    model_file.write("""

#__________________DEFINE REGION
#
LON_MIN  = 50.00
LON_MAX  = 54.00
LAT_MIN  = 35.00
LAT_MAX  = 37.00
#__________________DEFINE NODE SPACEING ()
#
X_NODES  = -200,200,17 # RIGHT,LEFT,NUM
Y_NODES  = -100,100,13 # BOTTOM,TOP,NUM
Z_NODES  =  0.00,  5.00, 10.00, 15.00, 20.00, 28.00, 36.00
#__________________DEFINE NODE BOUNDRAY
#
X_EDGE   = -500,500 # RIGHR,LEFT
Y_EDGE   = -500,500 # BOTTOM,TOP
Z_EDGE   = -100,200
#__________________DEFINE INITIAL VELOCITY MODEL
#
MODEL_V  =  5.00,  5.40,  5.95,  6.15,  6.23,  6.33,  6.60,  7.00,  8.10
MODEL_R  =  1.73,  1.73,  1.73,  1.73,  1.73,  1.73,  1.73,  1.73,  1.73
#__________________DEFINE PERTURBATION
#
MIN_PRT  = -5.0
MAX_PRT  = +5.0
#""")

    sys.exit(0)

par_dic = {}

inp = genfromtxt('model_par.dat',delimiter='=',dtype=str,comments='#')

for i in inp:

    try:
        
        par_dic[i[0].strip()] = float(i[1])

    except ValueError:

        par_dic[i[0].strip()] = array(i[1].split(','),dtype=float)

input_img = input('\n\n+++ Enter image file name:\n\n')

#___________________NODES IN X,Y,Z

x_nodes = par_dic['X_NODES']
y_nodes = par_dic['Y_NODES']
z_nodes = par_dic['Z_NODES']

num_nod_x = x_nodes.size
num_nod_y = y_nodes.size
num_nod_z = z_nodes.size

#___________________PERTURBATION BOUNDARY (%)

pert_min = par_dic['MIN_PRT']
pert_max = par_dic['MAX_PRT']

#___________________WRITE NODE VALUES

def node_writter(nodes, file_obj):
    
    i=0
    for i_20 in range(nodes.size//20):
        c=0
        while c<20:
            file_obj.write('%6.1f'%(nodes[i]))
            i+=1
            c+=1
        else:
            file_obj.write('\n')
    while i<nodes.size:
        file_obj.write('%6.1f'%(nodes[i]))
        i+=1

#___________________READ IMAGE INTO ARRAY

import imageio
from PIL import Image
       
fi = imageio.imread(input_img, pilmode='L')#, pilmode='L'
fi = Image.fromarray(fi).resize((num_nod_x, num_nod_y), resample=Image.BICUBIC)
fi = scale_data(array(fi.getdata()), [pert_min, pert_max])
fi = fi.reshape((num_nod_y, num_nod_x))

xmin = par_dic['LON_MIN']
xmax = par_dic['LON_MAX']
ymin = par_dic['LAT_MIN']
ymax = par_dic['LAT_MAX']

init_plotting_isi(10,10)

plt.imshow(fi, cmap=plt.cm.seismic_r, extent=[xmin, xmax, ymin, ymax])
plt.colorbar(label='Perturbation [%]')
plt.show()

#___________________WRITE INTO "synth.out" FILE IN SIMULPS FORMAT.

with open('synth.out','w') as f:

    vp      = par_dic['MODEL_V']
    vr      = par_dic['MODEL_R']
   
    f.write('%4.1f%3d%3d%3d  2\n'%(1, x_nodes.size, y_nodes.size, z_nodes.size))
   
    node_writter(x_nodes, f)        
    f.write('\n')
    node_writter(y_nodes, f)
    f.write('\n')
    node_writter(z_nodes, f)
    f.write('\n  0  0  0\n')

    #__________Vp

    polarite = +1
    
    for z,vp in zip(z_nodes,vp):

        v2 = zeros((y_nodes.size, x_nodes.size)) + vp
        v1 = vp + fi*vp/100.*polarite

        v2 = v1

        v = v2
        
        for y in range(v.shape[0]):

            x=0

            for x_20 in range(v.shape[1]//20):
                c=0
                while c<20:
                    f.write('%5.2f'%(v[y][x]))
                    x+=1
                    c+=1
                else:
                    f.write('\n')
            while x<v.shape[1]:
                f.write('%5.2f'%(v[y][x]))
                x+=1
                
            f.write('\n')

        polarite*=-1

    #__________VpVs

    polarite = +1

    for z,vr in zip(z_nodes,vr):

        v2 = zeros((y_nodes.size, x_nodes.size)) + vr
        v1 = vr + fi*vr/100.*polarite
        v2 = v1

        v = v2
        
        for y in range(v.shape[0]):

            x=0

            for x_20 in range(v.shape[1]//20):
                c=0
                while c<20:
                    f.write('%5.2f'%(v[y][x]))
                    x+=1
                    c+=1
                else:
                    f.write('\n')
            while x<v.shape[1]:
                f.write('%5.2f'%(v[y][x]))
                x+=1
                
            f.write('\n')

        polarite*=-1

print('\n+++ Output file "synth.out" is ready.\n')

#!/home/saeed/Programs/miniconda3/bin/python

from numpy import append, loadtxt, histogram2d, where, zeros, cos
from numpy import argmin, abs, gradient, pi, sqrt, arctan, arctan2, sin
from netCDF4 import Dataset
import os, sys
from pandas import read_csv, to_datetime
from scipy.ndimage import zoom
from PyMyFunc import d2k, k2d
from fiona import collection
from descartes import PolygonPatch
from adjustText import adjust_text
import proplot as plt

"""

Script for detect quarry from initial dataset.

outputs:

quarry.pha
earthq.pha
quarry.log

ChangeLogs:

27-Aug-2017 > Initial.
30-Jul-2017 > Improved Performance.
30-Jul-2017 > Now it works year by year.
30-Jul-2017 > A better view.
10-Apr-2021 > Improved figure quality using proplot.

"""

#___________________CHECK FOR REQUIRED FILES

if not os.path.exists('xyzm.dat') or not os.path.exists('hypoel.pha'):
    print('\n\n+++ Required input files "hypoel.pha" or "xyzm.dat" not found!\n')
    sys.exit(0)

#___________________READ DATASET

data = read_csv("xyzm.dat", delim_whitespace=True, parse_dates=[['YYYY', 'MM', "DD", "HH", "MN", "SEC"]])
data_dt = to_datetime(data.YYYY_MM_DD_HH_MN_SEC.values, format="%Y %m %d %H %M %S.%f")

#___________________DEFINE MAIN FUNCTION

def detect_quarry(xmin=50., xmax=54., ymin=35., ymax=37., nx=20, ny=20, alpha=5):

    #__________COUNT NUMBER OF EVENTS PER CELL
    def generator(year, day=True):       
        c1 = (data.LON.values>=xmin)&(data.LON.values<=xmax)
        c2 = (data.LAT.values>=ymin)&(data.LAT.values<=ymax)
        c3 = data_dt.year==year
        explo_start = 4 # start Hour of explosion (GMT)
        explo_end = 12 # end Hour of explosion (GMT)
        if day:
            c4 = (data_dt.hour>=explo_start)&(data_dt.hour<=explo_end)
            c = (c1)&(c2)&(c3)&(c4)
            x = data.LON.values[c]
            y = data.LAT.values[c]
            h, x_ ,y = histogram2d(x, y, bins=[nx,ny], range=[[xmin,xmax],[ymin,ymax]])
        else:
            c4 = (data_dt.hour<explo_start)|(data_dt.hour>explo_end)
            c = (c1)&(c2)&(c3)&(c4)
            x = data.LON.values[c]
            y = data.LAT.values[c]
            h, x, y = histogram2d(x, y, bins=[nx,ny], range=[[xmin,xmax],[ymin,ymax]])        
        return h.T, x, y

    #__________WRITE OUT QUARRY
    def write_quarry(quarry_index_list):
        with open('hypoel.pha') as f_inp, open(quarry_file.name, 'a') as f_qua:
            evt = []
            c   = 0
            for l in f_inp:
                evt.append(l)
                if not l[:10].strip():
                    if c in quarry_index_list:
                        for i in evt:
                            f_qua.write(i)
                    c+=1
                    evt = []

    #__________WRITE OUT EARTHQUAKE
    def exclude_quarry(quarry_index_list_total, year):
        with open('hypoel.pha') as f_inp, open(earthq_file.name, 'a') as f_ear:
            evt = []
            c   = 0
            for l in f_inp:
                evt.append(l)
                if not l[:10].strip():
                    if c not in quarry_index_list_total:
                        for i in evt:
                            if i[:10].strip(): evt_year = to_datetime(i[9:11].replace(" ", "0"), format="%y").year
                            if year != evt_year: break
                            f_ear.write(i)
                    c+=1
                    evt = []            

    #__________PLOT HILLSHADE
    def hillshade(array, azimuth, angle_altitude):
        x, y = gradient(array)
        slope = pi/2. - arctan(sqrt(x*x + y*y))
        aspect = arctan2(-x, y)
        azimuthrad = azimuth*pi / 180.
        altituderad = angle_altitude*pi / 180.
        shaded = sin(altituderad) * sin(slope)\
         + cos(altituderad) * cos(slope)\
         * cos(azimuthrad - aspect)
        return 255*(shaded + 1)/2

    #__________GET ELEVATION
    def getElv(nc_file):
        f = Dataset(my_example_nc_file, mode='r')
        latbounds = [ ymin , ymax ]
        lonbounds = [ xmin , xmax ]  
        lats = f.variables['lat'][:] 
        lons = f.variables['lon'][:]
        latli = argmin( abs( lats - latbounds[0] ) )
        latui = argmin( abs( lats - latbounds[1] ) ) 
        lonli = argmin( abs( lons - lonbounds[0] ) )
        lonui = argmin( abs( lons - lonbounds[1] ) )  
        elvs = f.variables['z'][ latli:latui , lonli:lonui ] 
        f.close()
        return elvs

    #__________PLOT RESULT
    start_srch = int(input("\n+++ Begining Year?\n"))
    end_srch = int(input("\n+++ Ending Year?\n"))
    print("")
    for year in range(start_srch, end_srch+1):
        print("+++ Working on Year:%5d"%(year))
        #__________PREPARE OUTPUT FILES
        out_dir = os.path.join("Results", str(year))
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        quarry_file = open(os.path.join(out_dir, 'quarry.pha'), 'w')
        earthq_file = open(os.path.join(out_dir, 'earthq.pha'), 'w')
        report_file = open(os.path.join(out_dir, 'quarry.log'), 'w')
        #__________PLOT DAY/NIGHT RATION
        with plt.rc.context():
            fig, axs = plt.subplots()
        axs.format(xlabel='Longitude', ylabel='Latitude', xformatter="%.1f", yformatter="%.1f", fontsize=2)
        colorbar_kw = {"title":"Day/Night", "length":.6, "width":.07, "labelsize":4, "ticklabelsize":5, "labelweight":"bold", "formatter":"%d"}
        ax = axs[0]
        ax.grid(linestyle=":")
        my_example_nc_file = os.path.join(os.environ['GMT_STUFF'], 'Grd', 'Calborz.grd')
        elvs = getElv(nc_file=my_example_nc_file)
        hs_array = hillshade(elvs, 315, 45)
        h_d, x, y = generator(year, day=True)
        h_n, x, y = generator(year, day=False)
        h_d[h_d==0] = 1
        h_n[h_n==0] = 1
        h_r = h_d/h_n
        H_r = zoom(h_r, 5, prefilter=False)
        extent = [xmin, xmax, ymin, ymax]
        im = ax.imshow(H_r, origin="lower", interpolation="none", extent=extent, cmap="Fire", colorbar="ur", colorbar_kw=colorbar_kw)
        #__________PLOT TOPO
        c1 = (data.LON.values>=xmin)&(data.LON.values<=xmax)
        c2 = (data.LAT.values>=ymin)&(data.LAT.values<=ymax)
        c3 = data_dt.year==year
        c = (c1)&(c2)&(c3) 
        lon = data.LON.values[c]
        lat = data.LAT.values[c]
        ax.plot(lon, lat, marker='.', ms=3, mfc='none', mec='w', mew=.5, linestyle='', alpha=.2, zorder=1)
        extent = [xmin, xmax, ymin, ymax]
        ax.imshow(hs_array, origin='lower', extent=extent, alpha=.1, cmap="gist_gray_r")
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymin,ymax)
        
        #__________SEARCH FOR REGIONS WITH EXPLOSION/BLASTS
        rx,ry = where(h_r.T>=alpha)
        quarry_index_list_total = zeros(0)
        for i,j in zip(rx, ry):
            xlim = [x[i],x[i+1]]
            ylim = [y[j],y[j+1]]
            for _ in xlim: ax.vlines(_,ylim[0], ylim[1], linewidth=.5, color='r')
            for _ in ylim: ax.hlines(_,xlim[0], xlim[1], linewidth=.5, color='r')
            cond_x = (data.LON.values>=xlim[0])&(data.LON.values<=xlim[1])
            cond_y = (data.LAT.values>=ylim[0])&(data.LAT.values<=ylim[1])
            cond_d = data_dt.year==year
            qua_ind = where((cond_x)&(cond_y)&(cond_d))[0]
            write_quarry(qua_ind)
            quarry_index_list_total = append(quarry_index_list_total, qua_ind)
        exclude_quarry(quarry_index_list_total, year)
        with open(report_file.name, 'a') as f:
            f.write('+++ Initial number of events                  : %d\n'%(len(data)))
            f.write('+++ Number of selected region includes quarry : %d\n'%(rx.size))
            f.write('+++ Number of explosions/blasts/shots         : %d\n'%(quarry_index_list_total.size))
            f.write('+++ Total number of seismic earthquakes       : %d\n'%(len(data)-quarry_index_list_total.size))
            f.write('+++ File including explosions/blasts/shots    : quarry.pha\n')
            f.write('+++ File including seismic earthquakes        : earthq.pha\n')

        #__________ADD IRAN-Province SHAPEFILE
        texts = []
        Province = os.path.join(os.environ["GMT_STUFF"], "Province", "Layer", "IRN_adm2.shp")
        with collection(Province, "r") as inp:
            inp = inp.filter(bbox=(xmin, ymin, xmax, ymax))
            for f in inp:
                ax.add_patch(PolygonPatch(f['geometry'], fc='none', ec='k', alpha=0.5, linestyle=':'))
        Cities = os.path.join(os.environ["GMT_STUFF"], "Province", "Layer", "IRN_adm1.shp")
        with collection(Cities, "r") as inp:
            inp = inp.filter(bbox=(xmin, ymin, xmax, ymax))
            for f in inp:
                ax.add_patch(PolygonPatch(f['geometry'], fc='none', ec='k', alpha=0.5, linestyle='-'))
        ProvName = os.path.join(os.environ["GMT_STUFF"], "Province", "Center", "Province.csv")
        ProvName = read_csv(ProvName, delimiter=',')
        ProvName = ProvName[(ProvName.ycoord >= ymin) &
                            (ProvName.ycoord <= ymax) &
                            (ProvName.xcoord >= xmin) &
                            (ProvName.xcoord <= xmax)]
        for lon, lat, name in zip(ProvName["xcoord"], ProvName["ycoord"], ProvName["Region_Eng"]):
            ax.plot(lon, lat, marker="s", ms=1.5, mfc="w", mec="k", mew=.5)
            text = ax.text(lon, lat, name, ha='center', color='k', clip_on=True,
                           fontsize=4, bbox=dict(boxstyle="square", ec='none', 
                           fc='#feffee',alpha=.3, pad=0.02))
            texts.append(text)
        adjust_text(texts, ax=ax)
            
        #__________SAVE FIGURE 
        out_name = os.path.join(out_dir, "quaary_map.png")
        fig.save(out_name, transparent=False)
        plt.close()

#__________START
if __name__ == "__main__":
    if len(sys.argv) < 7:
        print('\n\n+++ Usage: PyDetectQuarry.py [xmin=50., xmax=54., ymin=35., ymax=37., nx=20, ny=20, alpha=5]')
        print('+++ Running with default values for central Alborz...\n')
        detect_quarry(xmin=50., xmax=54., ymin=35., ymax=37., nx=20, ny=20, alpha=5)
    if len(sys.argv) == 8:
        xmin = float(sys.argv[1])
        xmax = float(sys.argv[2])
        ymin = float(sys.argv[3])
        ymax = float(sys.argv[4])
        nx   = int(sys.argv[5])
        ny   = int(sys.argv[6])
        alpha = float(sys.argv[7])
        detect_quarry(xmin, xmax, ymin, ymax, nx, ny, alpha)
print('\n+++ Check "quarry.log" for more information.\n')

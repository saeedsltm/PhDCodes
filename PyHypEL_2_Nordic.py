#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from LatLon import lat_lon as ll
from math import cos, radians
from random import gammavariate, choice, seed

"""
Script for converting HYPOELLIPSE main output to NORDIC format.

Note:

In his script, i've tested writting in a more efficent way. There
is no need to save all the data in a list (so the RAM is free),
and consiquently the speed of conversion is significantlly improved,
specially for large datasets.

ChangeLogs:

11-Jul-2017 > Initial.
24-Nov-2018 > fixed some bugs about formatted line4.
06-Oct-2019 > Auto-fill magnitude is set based on gamma dist.

NOTE: 
     1- ERROR CONVERSION IS NOT TESTED YET.
     2- Magnitudes set to 0. 

"""

inp    = input('\n\n+++ HYPOELIPSE output file [hypoel.out]:\n\n')
ans    = input('\n\n+++ Enable auto-gen magnitude [y/n]:\n\n')
output = open('nordic.out','w')
num_eq = 0

def get_mag():

    seed(1)
    mag = [gammavariate(2,2) for _ in range(500)]
    mag = [_/max(mag) for _ in mag]
    mag = [_*5.0 for _ in mag]

    return mag

random_mag = get_mag() 

#___________________CALCULATE ORIGINI TIME AS A PYTHON DATETIME OBJECT

def get_ot(l):

    ot_year  = int(l[1:5])
    ot_month = int(l[5:7])
    ot_day   = int(l[7:9])
    ot_hour  = int(l[10:12])
    ot_min   = int(l[12:14])
    ot_sec   = float(l[15:19])
    ot_msec  = int((ot_sec - int(ot_sec))*1e6)

    if ot_sec >= 60:

        ot_sec = ot_sec - 60
        ot_min+=1

    if ot_min >= 60:

        ot_min = ot_min - 60
        ot_hour+=1

    if ot_hour >= 24:

        ot_hour = ot_hour - 24
        ot_day+=1
            
    ot = dt(ot_year,ot_month,ot_day,ot_hour,ot_min,int(ot_sec),ot_msec)
    if ot.year>2090: ot = ot.replace(year=ot.year-100)

    return ot

#___________________WRITTER FUNC FOR LINE TYPE 1

def writter_L1(l,str_flag):

    global ort
    global gap
    global data
    global num_eq

    num_eq+=1

    ort    = get_ot(l)
    if ort.year > 2900: ort.replace(year=ort.year-1000) 
    lat    = ll.Latitude(degree=float(l[20:23]),minute=float(l[24:29])).decimal_degree
    lon    = ll.Longitude(degree=float(l[30:33]),minute=float(l[34:39])).decimal_degree
    dep    = float(l[39:45])
    nos    = float(l[53:56])
    gap    = float(l[59:63])
    rms    = float(l[65:72])
    if ans.upper()=="Y": mag = choice(random_mag)
    else: mag = 0.0
    data   = {}

    fmt    = ' %4d %2d%2d %2d%2d %4.1f L %7.3f%8.3f%5.1f  HPE%3d %3.1f %3.1fL                   1'
    line   = (ort.year,ort.month,ort.day,ort.hour,ort.minute,ort.second+ort.microsecond*1e-6,lat,lon,dep,nos,rms,mag)

    if str_flag:

        output.write('\n')

    else:

        str_flag = True
        
    output.write(fmt%(line)+'\n')

    return str_flag

#___________________WRITTER FUNC FOR LINE TYPE E

def writter_LE(err_ot,err_x,err_y,err_z,seh_x,seh_y,seh_z):

    fmt    = ' GAP=%3d                                                                       E'
    line   = (gap)
    output.write(fmt%(line)+'\n')
    output.write(' STAT SP IPHASW D HRMN SECON CODA AMPLIT PERI AZIMU VELO AIN AR TRES W  DIS CAZ7\n')

#___________________WRITTER FUNC FOR LINE TYPE 4
    
def writter_L4(l):

    sta = l[1:5].strip().upper()
    com = l[6:7].upper()
    pha = l[13:14]
    pol = l[14:15]
    wgt = int(l[15:16].replace(' ','0'))
    ain = float(l[57:60])
    res =float(l[30:36]) 

    if sta not in data:

        data[sta] = {'P':{}, 'S':{}}

    data[sta][pha]['art'] = ort + td(seconds=float(l[73:79]))

    try:

        data[sta][pha]['dis'] = float(l[44:51])
        data[sta][pha]['azm'] = float(l[52:56])
        
        
    except ValueError:
        
        data[sta][pha]['dis'] = data[sta]['P']['dis']
        data[sta][pha]['azm'] = data[sta]['P']['azm']

    art = data[sta][pha]['art']
    azm = data[sta][pha]['azm']
    dis = data[sta][pha]['dis']
   
    fmt    = ' %-5sS%1s E%-2s  %1d %1s %2d%2d%6.2f                            %4.0f  0%5.1f10%5.0f %3d '
    line   = (sta,com,pha,wgt,pol,art.hour,art.minute,art.second+art.microsecond*1e-6,ain,res,dis,azm)
    output.write(fmt%(line)+'\n')

#___________________CHANGE FLAG TRUE/FALSE

def chn_flag(flag):

    if flag: return False
    else: return True
    
#___________________READING INPUT FILE
    
with open(inp) as f:

    #_________SET HINTS & FLAGS

    hint_1   = 'date    origin'
    hint_E   = 'horizontal and'
    hint_4   = 'stn c pha remk'
    flag_1   = False
    flag_E   = False
    flag_4   = False
    flag_tmp = False
    str_flag = False
    
    #_________START READING LINE BY LINE

    for l in f:

        if hint_1 in l: flag_1 = True
        if hint_E in l: flag_E = True
        if hint_4 in l: flag_4 = True

        #_________LINE TYPE 1

        if l.strip() and flag_1 and hint_1 not in l:

            str_flag = writter_L1(l,str_flag)
            writter_LE(err_ot,err_x,err_y,err_z,seh_x**2,seh_y**2,seh_z**2)

            flag_1 = False

        #_________LINE TYPE E

        if l.strip() and flag_E and hint_E not in l:

            flag_tmp = chn_flag(flag_tmp)

            if flag_tmp:
                
                seh_x = float(l[12:19])
                seh_y = float(l[37:44])
                seh_z = float(l[62:69])
                continue

            else:

                az_x   = float(l[12:19])
                az_y   = float(l[37:44])
                err_x  = seh_x * cos(radians(az_x))
                err_y  = seh_y * cos(radians(az_y))
                err_z  = seh_z

                flag_E = False

        if 'se of orig =' in l: err_ot = float(l[13:20])

        #_________LINE TYPE 4
    

        if l.strip() and flag_4 and hint_4 not in l:

            writter_L4(l)

        if flag_4 and hint_4 not in l and not l.strip():

            flag_4 = False

#___________________CLOSE FILE
            
output.write('\n')            
output.close()            

print('\n+++ %d events converted.'%(num_eq))
print('+++ "nordic.out" is ready.')

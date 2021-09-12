#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt
from datetime import timedelta as td
from os import path
from sys import exit

if not  path.exists('travel.dat'):

    print '\n\n+++ No "travel.dat" file was found!\n\n'
    exit(0)
    
def writter(data):

    hdr = data[0]
    ort = hdr[:17]
    for _ in [0,2,4,7,9,12,13]: ort=ort[:_]+ort[_].replace(' ','0')+ort[_+1:]
    ort = dt.strptime(ort,'%y%m%d %H%M %S.%f')

    phases_dic = {}

    for ln in range(1,len(data)):

        line   = data[ln]
        n      = 14
        phases = [line[i:i+n] for i in range(0, len(line), n)]

        for phase in phases:

            if phase.strip():

                sta = phase[:4]
                pha = phase[5]
                pol = phase[6]
                wet = phase[7].replace(' ','0')
                ott = float(phase[8:14])
               
                if not phases_dic.has_key(sta):

                    phases_dic[sta] = {'P':{}, 'S':{}}

                phases_dic[sta][pha]['POL'] = pol
                phases_dic[sta][pha]['WET'] = wet
                phases_dic[sta][pha]['OTT'] = ott

    with open(output.name,'a') as f:
        
        for sta in sorted(phases_dic.keys()):

            if phases_dic[sta]['P'] and phases_dic[sta]['S']:
                po = phases_dic[sta]['P']['POL']
                pw = phases_dic[sta]['P']['WET']
                sw = phases_dic[sta]['S']['WET']
                pt = ort + td(seconds=phases_dic[sta]['P']['OTT'])
                st = phases_dic[sta]['S']['OTT']
                st = pt.second + pt.microsecond*1e-6 + st
                pt = pt.strftime('%y%m%d%H%M%S.%f')[:15]
                line = '%-4sEP%1s%1s %15s%12.2fES %1s\n'%(sta.strip(),po,pw,pt,st,sw)
                f.write(line)

            else:
                try:
                    po = phases_dic[sta]['P']['POL']
                except KeyError:
                    po = ' '
                try:
                    pw = phases_dic[sta]['P']['WET']
                except KeyError:
                    pw = '0'
                pt = ort + td(seconds=phases_dic[sta]['P']['OTT'])
                pt = pt.strftime('%y%m%d%H%M%S.%f')[:15]
                line = '%-4sEP%1s%1s %15s\n'%(sta.strip(),po,pw,pt)
                f.write(line)
        f.write('                 10  5.0\n')
                
data    = []
output  = open("hypoel.pha", "w")
num_evt = 0

with open('travel.dat') as f:

    for l in f:

        if not l.strip() or (len(l.strip())==1 and l[0]=='0'):

            writter(data)
            data = []
            num_evt+=1

        else: data.append(l)

print "\n\n+++ %d Events converted to HYPO71 format (%s).\n\n"%(num_evt,output.name)


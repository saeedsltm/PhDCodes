#!/home/saeed/Programs/miniconda3/bin/python

from datetime import datetime as dt

num_p = 0
num_rp = 0
num_s = 0
num_rs = 0
num_q = 0
st = []
ed = []

with open('hypoel.pha') as f:

    for l in f:

        if l[5].upper() == 'P':

            ot = l[9:24]
            ot = ot.replace(' ','0')
            try:
                ot = dt.strptime(ot,'%y%m%d%H%M%S.%f')
            except ValueError:
                continue
            st.append(ot)
            ed.append(ot)
            st = [min(st)]
            ed = [max(ed)]

        if len(l) == 25:

            if l[5].upper() == 'P' and l[7]!='4': num_p+=1
            if l[5].upper() == 'P' and l[7]=='4': num_rp+=1
            
        if len(l) == 41:

            if l[5].upper() == 'P' and l[7]!='4': num_p+=1
            if l[5].upper() == 'P' and l[7]=='4': num_rp+=1
            if l[37].upper() == 'S' and l[40]!='4': num_s+=1
            if l[37].upper() == 'S' and l[40]=='4': num_rs+=1

        if l[:10] == ' '*10: num_q+=1

with open('HypStatistic.dat', 'w') as f:

    f.write('### Sumary on hypoel.pha file.\n')
    f.write('Start-Time      : %s\n'%st[0].strftime('%Y-%m-%d'))
    f.write('End-Time        : %s\n'%ed[0].strftime('%Y-%m-%d'))
    f.write('Number of quakes:%6d\n'%num_q)
    f.write('Number of Pphase:%6d and rejected Pphase:%6d\n'%(num_p, num_rp))
    f.write('Number of Sphase:%6d and rejected Sphase:%6d\n'%(num_s, num_rs))

print('\n+++ HypStatistic.dat is ready.\n')

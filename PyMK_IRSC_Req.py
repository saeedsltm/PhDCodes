#!/home/saeed/Programs/miniconda3/bin/python

from obspy import UTCDateTime as utc

output  = open('irsc_req.dat','w')
inp_evt = raw_input('\n\n+++ Input "IRSC" catalog with "ZMAP" format:\n\n')
inp_sta = raw_input('\n\n+++ Input station file with "SEISAN" format:\n\n')


with open(inp_evt) as f1:

    for l1 in f1:

        l = l1.split()

        lon = float(l[0])
        lat = float(l[1])
        ort = utc(int(l[2]), int(l[3]), int(l[4]), int(l[7]), int(l[8]))
        mag = float(l[5])
        rel = 10

        ot = ort.strftime('%Y-%m-%d %H:%M:%S')
        st = ort - 10.0
        st = st.strftime('%Y-%m-%d %H:%M:%S')

        with open(inp_sta) as f2:

            for l2 in f2:

                nm = l2[:6].strip()

                for c in ['E', 'N', 'Z']:

                    fl = '%4s, %1s, %22s, %6.2f, %6.2f, %4.1f, %22s, %d\n'%(nm, c, ot, lat, lon, mag, st, rel)

                    output.write(fl)

output.close()

print '\n+++ Finito!'

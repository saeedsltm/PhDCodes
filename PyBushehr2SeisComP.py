#!/home/saeed/Programs/miniconda3/bin/python

from obspy import read
from glob import glob
import os, sys


"""

Convert and move Parsian and Guralp waveform to SeisComP archive.

- Copy this script to Bushehr root directory,
- Correct folder names and move waves inside each folder,
- Run the script.

"""

sdsarchive=os.path.join(os.environ["SEISCOMP_ROOT"], "var", "lib", "archive")
listDir = filter(os.path.isdir, os.listdir(os.getcwd()))

for d in listDir:
    # PARSIAN
    if d.upper().startswith("N") or d.upper().startswith("P"):
        files = sorted(glob(os.path.join(d, "archive", "*SYNC")))
        cmd = "seiscomp exec scart -I %s.mseed %s"%(d, sdsarchive)
        bad_files = 0
        for i,f in enumerate(files):
            print(f, "%3.1f"%(100*i/len(files))+"%")
            try:
                st = read(f)
                for tr in st:
                    tr.stats.network = "BP"
                    tr.stats.station = f.split(os.sep)[0].upper()
                    tr.stats.channel = tr.stats.channel.replace("BN", "BH")
                st.write("%s.mseed"%(d), format="mseed")
                os.system(cmd)
                os.remove("%s.mseed"%(d))
            except TypeError:
                bad_files+=1
        print("\n\n +++ Number of corrupted files: %d"%(bad_files))
    # GURALP
    if d.upper().startswith("T"):
        for com in ["e2", "n2", "z2"]:
            digitizerCode = d[1:5]
            files = sorted(set([f[:-9]+"*.gcf" for f in glob(os.path.join(d, digitizerCode+com, "*gcf"))]))
            cmd = "seiscomp exec scart -I %s.mseed %s"%(d, sdsarchive)
            bad_files = 0
            for i,f in enumerate(files):
                print(f, "%"+"%3.1f"%(100*i/len(files)))
                try:
                    st = read(f)
                    for tr in st:
                        tr.stats.network = "BP"
                        tr.stats.station = d.split("-")[-1].upper()
                        tr.stats.channel = tr.stats.channel.replace("HH", "BH")
                    st.write("%s.mseed"%(d), format="mseed")
                    os.system(cmd)
                    os.remove("%s.mseed"%(d))
                except (TypeError, ValueError):
                    bad_files+=1
            print("\n\n +++ Number of corrupted files: %d"%(bad_files))

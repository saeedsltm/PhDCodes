#!/home/saeed/Programs/miniconda3/bin/python

from LatLon import lat_lon as ll
from PySTA0RW import Read_Nordic_Sta, Write_Nordic_Sta

"""
Script for updating STATION0.HYP using input file.

NOTE: 

The input file must have the save format as STATION0.HYP.

ChangeLogs:

04-Aug-2017 > Initial.
"""

inp = raw_input('\n\n+++ Input station file with NORDIC format?\n\n')

ref_sta = Read_Nordic_Sta()
tar_sta = Read_Nordic_Sta(inp)
ref_sta['STA'].update(tar_sta['STA'])
Write_Nordic_Sta(ref_sta)

print '\n+++ File STATION0_NEW.OUT is ready.\n'

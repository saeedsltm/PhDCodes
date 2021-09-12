#!/home/saeed/Programs/miniconda3/bin/python

import os,sys

# Rename Components "E" -> "SE", "N" -> "SN", "Z" -> "SZ"
# Rename Sn -> Sg
# Rename Pn -> Pg if distance < CRITICAL_DISTANCE
# Rename Pg -> Pn if distance > CRITICAL_DISTANCE
# Rename AMP > IAML
# Rename "E    " -> "IAML"

inp = input("\n+++ NORDIC file name:\n")
CRITICAL_DISTANCE=140 # Pg to Pn distance
cmd = """awk '{gsub(" E  E", " SE E");gsub(" N  E", " SN E");gsub(" Z  E", " SZ E");gsub("ESn", "ESg");gsub("AMP  ", " IAML");gsub("E    ", " IAML"); print $0}' %s > tmp1"""%(inp)
os.system(cmd)
cmd = """awk -v CD=${CRITICAL_DISTANCE} '{if (substr($0,11,2)=="Pg" && substr($0,71,5)*1>CD) gsub("Pg ", "Pn ") ;print $0}' tmp1 > tmp2"""
os.system(cmd)
cmd = """awk -v CD=${CRITICAL_DISTANCE} '{if (substr($0,11,2)=="Pn" && substr($0,71,5)*1<CD) gsub("Pn ", "Pg ") ;print $0}' tmp2 > tmp3"""
os.system(cmd)
os.rename("tmp3", "hyp_corr.out")
os.remove("tmp1")
os.remove("tmp2")
print("\n+++ 'hyp_corr.out' is ready.")

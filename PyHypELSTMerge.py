#!/home/saeed/Programs/miniconda3/bin/python

from string import upper

inp1=raw_input("\n+++ Input refrence Hypoellipse station file name:\n")
inp2=raw_input("\n+++ Input target Hypoellipse station file name:\n")
outp="hypoel_merged.sta"

inp1_dic = {}
inp2_dic = {}


for inp, inp_dic in zip([inp1, inp2], [inp1_dic, inp2_dic]):

    with open(inp) as f:

        for l in f:

            if "*" in l: continue

            sta = l[:4].strip().upper()
            info = l[4:27]

            inp_dic[sta] = info

inp1_dic.update(inp2_dic)

print '\n+++ Merged Station file  => %s'%outp

with open(outp, "w") as f:
    
    for sta in sorted(inp1_dic.keys(), key=lambda x:(len(x),upper(x),sorted(x))):

        f.write('%4s%23s\n'%(sta, inp1_dic[sta]))
        f.write('%4s*     0     1.00\n'%(sta))

#!/home/saeed/Programs/miniconda3/bin/python

'''

This script reads NORDIC file and remove those events
in which they have less than 4 valid phases (valid phase
is a phase with weight less than 4).

Use this scrip before running SIMULPS.

'''

inp = raw_input('\n\n+++ Input NORDIC file:\n\n')
out = open('filtered_%s'%inp, 'w')

evt = []

with open(inp) as f:

    for l in f:

        evt.append(l)

        if not l.strip():
            
            n = 0
            
            for i in evt:

                if i[79:80] in ['4', ' '] and i[14]!='4': n+=1

            if n>=4:

                with open(out.name, 'a') as g:

                    for i in evt:

                        g.write(i)
    
            evt = []

print '\n+++ Finito!\n'

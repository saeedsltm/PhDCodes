"""

Script for adding amplitude line to existing event.

"""

inp = raw_input("\n+++ Nordic file:\n")
out = inp.split('.')[0]

with open(inp) as f, open('%s_corrected.out'%out,'w') as g:

    for l in f:

        g.write(l)

        if l.strip() and l[79] in [' ', '4'] and l[34:45].strip():

            nl = l[:9]+' IAML'+l[14:]
            g.write(nl)

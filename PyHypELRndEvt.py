#!/home/saeed/Programs/miniconda3/bin/python

"""
Script for extracting events randomly from hypoel.pha file.

ChangeLogs:

28-Feb-2021 > Initial.

"""

from random import sample

inp = input("\n++ Hypoellipse phase-file name [enter for 'hypoel.pha']:\n")
if not inp: inp = "hypoel.pha"
k = input("\n++ How many random events?\n")
events = [[]]

with open(inp) as f:
    for l in f:
        while l[0].strip():
            events[-1].append(l)
            l = next(f)
        else:
            events.append([])
    
events = filter(lambda x: len(x), events)
events = [_ for _ in events]
selected = sample(events, int(k))

with open("hypoel_random.pha", "w") as f:
    for event in selected:
        for l in event: f.write(l)
        f.write("                 10     \n")

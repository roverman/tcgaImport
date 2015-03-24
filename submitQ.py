#!/usr/bin/env python
import os
f = open("to_update.txt", "r")
for line in f.read().split("\n"):
    if line.startswith("MISSING: ") or line.startswith("UPDATE: "):
        #print "qsub ./update.sh " + line[9:]
        os.system("qsub -v basename='" + line[9:] + "' update.sh")


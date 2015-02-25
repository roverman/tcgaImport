import sys
import pandas as pd

if len(sys.argv) < 3:
    print "Not enough argument"
    exit()
print sys.argv[1]
print sys.argv[2]
if sys.argv[1].endswith(".tsv"):
    df = pd.read_csv(sys.argv[1], sep="\t", header=0, index_col=0)
    handle = open(sys.argv[2],"r")
    keys = handle.readline().split("\t")
    rNum=1
    for line in handle:
        arr = line.rstrip().split("\t")
        if not arr[0] in df:
            print "Difference: " + arr[0] + "is not found!"
        else :
            for i in range(1, len(arr)):
                if not keys[i] in df[arr[0]]:
                    print "Difference: " + keys[i] + " is not found!"
                else:
                    if isinstance(arr[i], float):
                        val = float(arr[i])
                    else:
                        print arr[i] 
                        val = float('nan')
                        if val != df[arr[0]][keys[i]]:
                            print "Difference at row " + arr[0] + " column " + keys[i] + ": " + str(df[arr[0]][keys[i]]) + "\t" + str(val)
                rNum += 1
    handle.close()
elif sys.argv[1].endswith(".bed"):
    s = set()
    handle = open(sys.argv[1], "r")
    for line in handle:
        s.add(line.rstrip())
    handle.close()
    handle = open(sys.argv[2], "r")
    for line in handle:
        if not line.rstrip() in s:
            print "Difference :" + line.rstrip()
    handle.close()


print "Comparison is finished!"
    
    


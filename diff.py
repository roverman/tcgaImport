import sys
import pandas as pd

if len(sys.argv) < 3:
    print "Not enough argument"
    exit()
#print sys.argv[1]
#print sys.argv[2]
if sys.argv[1].endswith(".tsv"):
    df = pd.read_csv(sys.argv[1], sep="\t", header=0, index_col=0)
    #print df
    handle = open(sys.argv[2],"r")
    keys = handle.readline().rstrip().split("\t")
    rNum=1
    for line in handle:
        arr = line.rstrip().split("\t")
        if not arr[0] in df.index:
            print "Difference: " + arr[0] + "is not found!"
        else :
            for i in range(1, len(arr)):
                if not keys[i] in df.columns:
                    print "Difference: " + keys[i] + " is not found!"
                else:
                    if arr[i] == "NA":
                        val = "nan"
                    else:
                        val = round(float(arr[i]), 4)
                    if val != df[keys[i]][arr[0]]:
                        print "Difference at row " + arr[0] + " column " + keys[i] + ": " + str(df[keys[i]][arr[0]]) + "\t" + str(val)
                        sys.exit()
                rNum += 1
    handle.close()
elif sys.argv[1].endswith(".bed"):
    d = dict()
    handle = open(sys.argv[1], "r")
    for line in handle:
        arr = line.rstrip().split("\t")
        if len(arr) < 5: continue
        key = arr[0] + "\t" + arr[1] + "\t" + arr[2] + "\t" + arr[3]
        if key in d: 
            print key
        else:
            d[key] = arr[4]
    handle.close()
    handle = open(sys.argv[2], "r")
    for line in handle:
        arr = line.rstrip().split("\t")
        if len(arr) < 5: continue
        key = arr[0] + "\t" + arr[1] + "\t" + arr[2] + "\t" + arr[3]
        if not key in d:
            print "Difference: " + key + " is not found"
        else:
            if float(arr[4]) != float(d[key]):
                print "Difference: " + key + " " + d[key] + " " + arr[4]
    handle.close()


print "Comparison is finished!"
    
    


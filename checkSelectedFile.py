import synapseclient
import os
import pandas as pd

syn = synapseclient.login()
folder = "out2"
project="syn2812961"
files = {x["file.name"]: x["file.id"] for x in syn.chunkedQuery("select name from file where benefactorId=='%s"%project + "' and fileType != 'clinicalMatrix' and fileType != 'maf'")}
for f in os.listdir(folder):
    if f.endswith(".json") or f.endswith(".bed") or f.endswith(".maf"):
        continue
    df1 = pd.read_csv(folder + "/" + f, sep="\t", index_col=0, na_values=['null']).astype('float')
    df1 = df1.ix[:, sorted(df1.columns)]
    df2 = pd.read_csv(syn.get(files[f]).path, sep="\t", index_col=0, na_values=['null']).astype('float')
    df2 = df2.ix[:, sorted(df2.columns)]
    missingGene = ",".join(df2.index - df1.index)
    maxdiff = (df1.ix[:,:] - df2.ix[df1.index,:]).abs().max().max()
    print "%s\t%s\t%g\n"%(f, missingGene, maxdiff)
    fout = open(f + ".diff.log", "w")
    for index in df2.index:
        for col in df2.columns:
            if not index in df1.index or not col in df1.columns:
                fout.write("Missing index " + index + " , missing columns " + col +"\n")
                continue
            diff = abs(df1.ix[index, col] - df2.ix[index, col])
            if diff > 0.1:
                fout.write(index + "\t" + col + "\t" + str(df1.ix[index, col]) + "\t" + str(df2.ix[index, col]) + "\n")
    fout.close()

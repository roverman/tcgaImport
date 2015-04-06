import synapseclient
import os
import pandas as pd

syn = synapseclient.login()
folder = "out"
old_folder = 'old_out/'
project="syn2812961"
files = {x["file.name"]: x["file.id"] for x in syn.chunkedQuery("select name from file where benefactorId=='%s'"%project)}
print 'file\tabs(maxdiff)\tmaxdiff%\tfileSize new\tfileSize old\tnew dim\told dim\tmissing_Genes_in_new\tnew_Genes_in_new'
for f in os.listdir(folder):
    if f.endswith(".json") or f.endswith(".bed") or f.endswith(".maf"):
        continue
    if os.path.isfile(old_folder+f):
        df_old = pd.read_csv(old_folder+f, sep="\t", index_col=0, na_values=['null']).astype('float')
        pass
    else:
        try:
            df_old = pd.read_csv(syn.get(files[f], downloadLocation='old_out/').path, sep="\t", index_col=0, na_values=['null']).astype('float')
        except KeyError:
            print f, '\tDoes not exist in local or Synapse'
            continue
    df_new = pd.read_csv(folder + "/" + f, sep="\t", index_col=0, na_values=['null']).astype('float')
    dim_new =df_new.shape
    dim_old = df_old.shape

    df_new = df_new.ix[:, sorted(df_new.columns)]
    df_old = df_old.ix[:, sorted(df_old.columns)]

    missingGenes = ",".join(df_old.index - df_new.index)[:100]
    newGenes = ",".join(df_new.index - df_old.index)[:100]
    absmaxdiff = (df_new - df_old.ix[df_new.index,:]).abs().max().max()
    maxdiffpercent = ((df_new - df_old.ix[df_new.index,:])/df_new).abs().max().max()
    print "%s\t%g\t%g\t%0.2fMb\t%0.2fMb\t%s\t%s\t%s\t%s"%(f, absmaxdiff, maxdiffpercent,  
                                            os.stat(folder + "/" + f).st_size/1024.**2, 
                                            os.stat(old_folder+f).st_size/1024.**2, 
                                            `dim_new`, `dim_old`,
                                            missingGenes, newGenes,)

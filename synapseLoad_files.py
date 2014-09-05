#!/usr/bin/env python
import os
import sys
import json
import re
from glob import glob
import synapseclient
from synapseclient import Activity, File
import hashlib
from argparse import ArgumentParser

def get_md5(path):
    md5 = hashlib.md5()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''): 
                md5.update(chunk)
        md5str = md5.hexdigest()
    return md5str

def log(message):
    sys.stderr.write(message + "\n")

def find_child(syn, project, name):
    query = "select id from entity where parentId=='%s' and name=='%s'" % (project, name)
    for res in syn.query(query)['results']:
        return res['entity.id']
    return None
    
def getParentFolder(syn, project, meta):
    fid = find_child(syn, project, meta['annotations']['acronym'])
    if fid is None:
        return None
    pid = find_child(syn, fid, meta['platform'])
    return pid

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("src", help="Scan directory", default=None)
    parser.add_argument("--project", help="Project", default=None)
    parser.add_argument("--skip-md5", help="Skip MD5", action="store_true", default=False)
    parser.add_argument("--push", help="Push", action="store_true", default=False)
    parser.add_argument("--acronym", help="Limit to one Acronym", default=None)

    args = parser.parse_args()
    syn = synapseclient.login()
    
    for a in glob(os.path.join( args.src, "*.json")):
        log( "Loading:" + a )
        with open(a) as handle:
            meta = json.load(handle)
        dpath = re.sub(r'.json$', '', a)
        #Skip the rest of the loop if data file is empty or we are not doing the current acronyms
        if os.stat(dpath).st_size==0 or (args.acronym != meta['annotations']['acronym'] and args.acronym is not None):
            continue
        
        parentId= getParentFolder(syn, args.project, meta)
        #Determine if we are updating an existing file and if we should update based on md5
        query = "select id from entity where parentId=='%s' and name=='%s'" % (parentId, meta['name'])
        res = list(syn.chunkedQuery(query))
        if len(res) != 0:
            tmp_ent = syn.get(res[0]['entity.id'], downloadFile=False)
            upload = (tmp_ent.md5 != meta['md5'])
            log( "\tFound: %s and upload (MD5 doesn't match)= %s" %(tmp_ent.id, upload))
        else:
            log("Not found:" + meta['name'])
            upload = True
        #Prepare the entity for upload
        if upload and args.push: 
            entity = File(dpath, name=meta['name'], parentId=parentId, annotations=meta['annotations'])
            if 'provenance' in meta:
                #Fix labels for urls
                for u in meta['provenance']['used']:
                    if 'name' not in u and 'url' in u:
                        u['name'] = u['url']
                prov = Activity(data=meta['provenance'])
                prov.executed('https://github.com/Sage-Bionetworks/tcgaImport')

            else:
                prov=None
            log('\tUploading:%s' %entity.name)
            entity = syn.store(entity, activity=prov)
            log('\tCreated/Updated: **** %s ****' %entity.id)



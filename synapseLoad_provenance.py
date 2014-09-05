#!/usr/bin/env python
import os
import sys
import json
import re
from glob import glob
import synapseclient
import hashlib
from argparse import ArgumentParser

def log(message):
    sys.stderr.write(message + "\n")
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("src", help="Scan directory", default=None)
    parser.add_argument("--project", help="Project", default=None)
    parser.add_argument("--acronym", help="Limit to one Acronym", default=None)

    args = parser.parse_args()
    
    syn = synapseclient.login()
    
    for a in glob(os.path.join( args.src, "*.json")):
        log( "Loading:" + a )
        with open(a) as handle:
            meta = json.loads(handle.read())
        if args.acronym is None or args.acronym == meta['annotations']['acronym']:
            dpath = re.sub(r'.json$', '', a)
            query = "select id from entity where benefactorId=='%s' and name=='%s'" % (args.project, meta['name'])
            res = syn.query(query)
            #print meta['@id'], res
            if res['totalNumberOfResults'] != 0:
                log( "Found " + res['results'][0]['entity.id'] )                    
                ent_id = res['results'][0]['entity.id']
                if 'provenance' in meta:
                    used_refs = meta['provenance']['used']
                    for u in used_refs:
                        if 'name' not in u and 'url' in u:
                            u['name'] = u['url']
                        
                    if len(used_refs):
                        activity = synapseclient.Activity(meta['provenance']['name'])
                        if 'description' in meta['provenance']:
                            activity['description'] = meta['provenance']['description']
                        activity['used'] = used_refs
                        activity.executed('https://github.com/Sage-Bionetworks/tcgaImport')
                        #print json.dumps(activity, indent=4)
                        #print ent
                        #prov = syn.getProvenance(ent)
                        #print json.dumps(prov, indent=4)
                        syn.setProvenance(ent_id, activity)
                        #sys.exit(0)

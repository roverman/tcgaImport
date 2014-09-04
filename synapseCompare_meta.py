#!/usr/bin/env python

import synapseclient
import tcgaImport
from argparse import ArgumentParser
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("basename", nargs="?", default=None)
    parser.add_argument("-o", "--output", help="Output File", default=None)
    parser.add_argument("--project", help="Project", default=None)

    args = parser.parse_args()


    if args.basename is not None:
        basename_list = [args.basename]
    else:
        basename_list = []
        for plat in tcgaImport.platform_list():
            logging.info("Queueing: %s" % (plat))
            basename_list += tcgaImport.archive_list(plat)
        basename_list.extend(tcgaImport.clinicnal_archive_list())
        basename_list.extend(tcgaImport.mutation_archive_list())

    handle = open(args.output, "w") if args.output is not None else  sys.stdout
    syn = synapseclient.login()

    for basename in basename_list:
        logging.info("Checking: %s" % (basename))
        basename_platform_alias = tcgaImport.get_basename_platform(basename)
        logging.info(basename_platform_alias)
        conf = tcgaImport.getBaseBuildConf(basename, basename_platform_alias, "./")
        request = conf.buildRequest()
        
        for subtypeName, subtypeData in tcgaImport.tcgaConfig[basename_platform_alias].dataSubTypes.items():
            filename = subtypeData['nameGen'](basename)
            entity_id = None
            for row in syn.query("select id from entity where benefactorId=='%s' and name=='%s'" % (args.project, filename))['results']:
                entity_id = row['entity.id']

            if entity_id is not None:
                prov = syn.getProvenance(entity_id)
                #Filter out only used not executed items
                prov = [x for x in prov['used'] if not x.get('wasExecuted', False)]
                logging.info("Provenance: %s" % (prov))
                found_count = 0
                for req_elem in request['provenance']['used']:
                    found = False
                    for elem in prov:
                        if req_elem['url'] == elem['url']:
                            found = True
                    if found:
                        found_count += 1
                    else:
                        logging.info("Not Found: %s" % (req_elem['url']))
                logging.info("Found %s of %s (%s)" % (found_count, len(prov), len(request['provenance']['used'])) )
                if found_count == len(prov) and found_count == len(request['provenance']['used']):
                    handle.write("READY: %s\n" % (basename)) 
                else:
                    handle.write("UPDATE: %s\n" % (basename))
                     #We have already notified that basename needs to be updated skip rest of subtypes
                    break
            else:
                handle.write("MISSING: %s\n" % (basename)) 
                #We have already notified that basename is missing skip rest of subtypes
                break

    handle.close()

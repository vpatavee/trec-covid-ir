import csv
import os
import json
from collections import defaultdict


def metadata2dict(path_to_metadata, patn_to_document_parses):
    """
    Convert metadata to dict for each of use
    Return dict
    key = cord_uid
    value = dict - keys = "path", "abstract", "title"
    
    One path to pdf_json_files or pmc_json_files for cord_uid, relatve path from patn_to_document_parses
    Look into pmc_json_files first, if not found look into pdf_json_files
    If mulitple found, choose first
    Return None is not found
    Can multiple cord_uid, keep first found pmc
    
    discard uid with no file
    
    """

    metadata_dict = defaultdict(list)
    seen_pmc = set()

    with open(path_to_metadata) as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:

            cord_uid = row['cord_uid']
            if cord_uid in seen_pmc:
                continue
            
            title = row['title']
            abstract = row['abstract']
            # authors = row['authors'].split('; ')
            pdf = row['pdf_json_files'].split('; ')
            pmc = row['pmc_json_files'].split('; ')
            path = None
            
            if pmc:
                path = pmc[0]
                seen_pmc.add(cord_uid)
            elif pdf:
                path = pdf[0]
            
            if path is None:
                continue
            
            info = {
                "path": path,
                "abstract" : abstract,
                "title" : title
                
            }
            
            metadata_dict[cord_uid] = info
    return metadata_dict
            
            



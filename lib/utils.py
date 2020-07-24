import csv
import os
import json
from collections import defaultdict
import random
import re
import pandas as pd
from xml.etree import ElementTree

regex_hyphen = re.compile(r'[-_]')
regex_punct = re.compile(r'[^\w]')
wh_list = [
    "WDT",
    "WP",
    "WP$",
    "WRB"
]


def metadata2dict(path_to_metadata, patn_to_document_parses, small=False, cache=True):
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
    path_to_metadata_dict = path_to_metadata.replace("csv", "json")
    if cache and os.path.exists(path_to_metadata_dict):
        print("Loading metadata_dict from cache")
        with open(path_to_metadata_dict, "r") as f:
            metadata_dict = json.load(f)    
        if small:
            return {k:metadata_dict[k] for k in random.sample(list(metadata_dict.keys()), k=100)}
        else:
            return metadata_dict
    
    metadata_dict = dict()
    possible_path_pmc = defaultdict(set)
    possible_path_pdf = defaultdict(set)

    with open(path_to_metadata) as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            cord_uid = row['cord_uid']
            title = row['title']
            abstract = row['abstract']
            # authors = row['authors'].split('; ')
            
            # to be determined in choose_best_path which path will be used
            for e in row['pmc_json_files'].split('; '):
                if e.strip():
                    possible_path_pmc[cord_uid].add(e.strip())
                    
            for e in row['pdf_json_files'].split('; '):
                if e.strip():
                    possible_path_pdf[cord_uid].add(e.strip())             
            

            # keep first seen
            if cord_uid not in metadata_dict:
                info = {
                    "path": None,
                    "abstract" : abstract,
                    "title" : title

                }
                metadata_dict[cord_uid] = info
            
            if small and len(metadata_dict) == 100:
                break
                
    path_to_file = "/".join(path_to_metadata.split("/")[:-1]) + "/"
    choose_best_path(metadata_dict, possible_path_pmc, possible_path_pdf, path_to_file)
    
    with open(path_to_metadata_dict, "w") as f:
        json.dump(metadata_dict, f) 
        
    return metadata_dict

def choose_best_path(metadata_dict, possible_path_pmc, possible_path_pdf, path_to_file):
    to_be_removed = list()
    
    for uid, info in metadata_dict.items():
        for fname in list(possible_path_pmc[uid]):
             with open(path_to_file + fname, "r") as f:
                bodies = json.load(f)["body_text"]
                text = "".join([body["text"].strip() for body in bodies]).strip()
                if text and len(text) > 3:
                    info["path"] = fname
                    break
        if info["path"] is None:
            for fname in list(possible_path_pdf[uid]):
                with open(path_to_file + fname, "r") as f:
                    bodies = json.load(f)["body_text"]
                    text = "".join([body["text"].strip() for body in bodies]).strip()
                    if text and len(text) > 3:
                        info["path"] = fname
                        break   
        if info["path"] is None:
            to_be_removed.append(uid)
                    
    for e in to_be_removed:
        metadata_dict.pop(e, None)


def read_topics_set_to_df(path_to_topic):
    tree = ElementTree.parse(path_to_topic)
    topics = list()
    for topic in tree.getroot():
        d = dict()
        d["number"] = topic.attrib["number"]
        for field in topic:
            d[field.tag] = field.text
        topics.append(d)

    return pd.DataFrame(topics)
            
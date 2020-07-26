import csv
import os
import json
from collections import defaultdict
import random
import numpy as np
import re
import pandas as pd
from xml.etree import ElementTree
import subprocess
import spacy

nlp = spacy.load('en_core_web_sm')

regex_hyphen = re.compile(r'[-_]')
regex_punct = re.compile(r'[^\w]')
wh_list = [
    "WDT",
    "WP",
    "WP$",
    "WRB"
]

def create_report(topics_df, sim, idx2uid, report_name):
    """
     topicid Q0 docid rank score run-tag
    """
    lines = list()
    template = "{} Q0 {} {} {} run0baseline"
    max_sim_idx = np.argsort(sim, axis=1)[:, :-1001:-1]
    
    for i, row in enumerate(max_sim_idx):
        tid = topics_df.iloc[i]["number"]
        for j, idx in enumerate(row):
            docid = idx2uid[idx]
            rank = j + 1
            score = sim[i,idx]
            lines.append(template.format(tid, docid, rank, score))
    
    report = "\n".join(lines)
    with open(report_name, "w") as f:
        f.write(report)
        
def evaluate(report):
    trev_eval_folder = "/home/pmeemeng/patavee/trec_eval/"
    trec = trev_eval_folder + "trec_eval"
    arg = '-c -m ndcg_cut.20 -m P.20 -m bpref -m map {}qrels-covid_d4_j3.5-4.txt'.format(trev_eval_folder)
    cmd = [trec] + arg.split() + [report]
    p = subprocess.check_output(cmd, universal_newlines=True)
    eval_res = dict()
    for line in p.strip().split("\n"):
        metric, _, score = line.split("\t")
        eval_res[metric.strip()] = score
    print(eval_res)
    with open( report + ".eval.json", "w") as f:
        json.dump(eval_res, f)
    
    
        
        
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


def get_clean_query(query):
    """
    return list if query tokens
    """
    cleaned_query = list()
    query = re.sub(regex_hyphen, "", query)
    query = re.sub(regex_punct, " ", query)
    for tok in nlp(query):
        if tok.tag_ in wh_list or tok.is_stop:
            continue
        cleaned_query.append(tok.orth_.lower())
    return  cleaned_query
            
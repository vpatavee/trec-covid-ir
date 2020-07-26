import pysolr
import sys
from utils import regex_hyphen, regex_punct, metadata2dict
import json
import re

#  bin/solr create -c cord-19-2020-06-19-nested

def index_solr(path_to_data, metadata_dict, solr):
    
    solr_payloads = list()
    for uid, info in metadata_dict.items():
        with open(path_to_data + info["path"], "r") as f:    
            bodies = json.load(f)["body_text"]
            
        abstract = ""
        if info["abstract"].strip():
            abstract = info["abstract"]
            abstract = abstract.lower()
            abstract = re.sub(regex_hyphen, "", abstract)
            abstract = re.sub(regex_punct, " ", abstract)

        all_text = ""
        for body in bodies:
            text = body["text"]
            text = text.lower()
            text = re.sub(regex_hyphen, "", text)
            text = re.sub(regex_punct, " ", text)
            all_text += text + " "
            
        title = ""
        if info["title"].strip():
            title = info["title"].lower()
            title = re.sub(regex_hyphen, "", title)
            title = re.sub(regex_punct, " ", title)
        

        solr_payload = {
            "id": uid,
            "abstract": abstract,
            "body": all_text,
            "title": title
        }
            
        solr_payloads.append(solr_payload)
        if len(solr_payloads) == 100:
            solr.add(solr_payloads)
            solr_payloads = list()
            
    if solr_payloads:
        solr.add(solr_payloads)
    print("finished indexing")
    
def index_solr_nest(path_to_data, metadata_dict, solr):
    solr_payloads = list()
    for uid, info in metadata_dict.items():
        with open(path_to_data + info["path"], "r") as f:    
            bodies = json.load(f)["body_text"]
            
        abstract = ""
        if info["abstract"].strip():
            abstract = info["abstract"].lower()
            abstract = re.sub(regex_hyphen, "", abstract)
            abstract = re.sub(regex_punct, " ", abstract)
            
        title = ""
        if info["title"].strip():
            title = info["title"].lower()
            title = re.sub(regex_hyphen, "", title)
            title = re.sub(regex_punct, " ", title)
        

        solr_payload = {
            "id": uid,
            "abstract": abstract,
            "body": list(),
            "title": title
        }


        for section_id, body in enumerate(bodies):
            section_name = body['section'].lower()
            section_name = re.sub(regex_hyphen, "", section_name)
            section_name = re.sub(regex_punct, " ", section_name)
            
            text = body["text"].lower()
            text = re.sub(regex_hyphen, "", text)
            text = re.sub(regex_punct, " ", text)
            
            section = {
                "id":"{}:{}".format(uid, str(section_id)),
                "title": section_name,
                "body": text
            }
            
            solr_payload["body"].append(section)
            
            
        solr_payloads.append(solr_payload)
        if len(solr_payloads) == 100:
            solr.add(solr_payloads)
            solr_payloads = list()
            
    if solr_payloads:
        solr.add(solr_payloads)
    print("finished indexing")    
    
    
if __name__ == "__main__":
    
    mode = sys.argv[1]
    path_to_data = sys.argv[2]
    core_name = sys.argv[3]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    
    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
    
    
    solr = pysolr.Solr('http://0.0.0.0:8983/solr/' + core_name, timeout=10, always_commit=True )
    ping = json.loads(solr.ping())
    if ping["status"] != "OK":
        print("solr conection error", ping)
        
    if mode == "-f": # flat
        index_solr(path_to_data, metadata_dict, solr)
    elif mode == "-n": # nest e.g. python solr.py -n ../../CORD-19/2020-06-19/  cord-19-2020-06-19-nested
        index_solr_nest(path_to_data, metadata_dict, solr)
    else:
        print("mode must be flat or nest")
        exit()
    
    
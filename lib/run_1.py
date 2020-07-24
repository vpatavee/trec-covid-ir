from utils import metadata2dict, regex_hyphen, regex_punct
import re
import json
import os
from collections import Counter
import sys
import numpy as np
from gensim.models import KeyedVectors


def create_tf(path_to_document_parses, metadata_dict, path_output):

    
    for uid, info in metadata_dict.items():
        list_of_words = list()
        with open(path_to_document_parses + info["path"], "r") as f:
            bodies = json.load(f)["body_text"]
            for body in bodies:
                text = body["text"]         
                text = re.sub(regex_hyphen, "", text)
                text = re.sub(regex_punct, " ", text)
                text = text.lower().strip()
                list_of_words.extend(text.split())
                
            text = info["abstract"]
            text = re.sub(regex_hyphen, "", text)
            text = re.sub(regex_punct, " ", text)   
            text = text.lower().strip()
            list_of_words.extend(text.split())
            
        if not list_of_words:
            print("no text", uid)
            continue
        counter = Counter(list_of_words)
        
        with open(path_output + uid + "_tf.json", "w") as f:
            json.dump(counter, f)    


def create_idf(metadata_dict, path_output):
    index = list()
    for uid, fname in metadata_dict.items():

        with open(path_output + uid + "_tf.json", "r") as f:
            tf = json.load(f)
            index.extend(list(tf.keys()))

    idf = Counter(index)
    with open(path_output + "idf.json", "w") as f:
        json.dump(idf, f)           

def create_emb(path_output, wv):
    oov = set()
    with open(path_output + "idf.json", "r") as f:
        idf = json.load(f)   

    ltc = dict()

    for uid, fname in metadata_dict.items():
        with open(path_output + uid + "_tf.json", "r") as f:
            tf = json.load(f)

        vect = np.zeros(300)
        for tok, freq in tf.items():
            if tok in wv:
                vect += (1 + np.log(freq)) * np.log(len(idf) / idf[tok]) * wv[tok]
            else:
                oov.add(tok)
            
        vect = vect / np.linalg.norm(vect)
        ltc[path_to_pmc_json_tf + fname] = list(vect)
        
    with open(path_output + "ltc.json", "w") as f:
        json.dump(idf, f)   
        
    print("oov", list(oov))
    with open(path_output + "oov.json", "w") as f:
        json.dump({"oov": list(oov)}, f)      
        

if __name__ == "__main__":
    path_to_data = sys.argv[1]
    path_to_process = sys.argv[2]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    
    wv = KeyedVectors.load("../tmp/wv_300_15_cleaned_uncased_trained_2020-06-19.model")
    

    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
    create_tf(path_to_data, metadata_dict, path_to_process)
    print("finished create tf")
    create_idf(metadata_dict, path_to_process)
    print("finished create idf")
    create_emb(path_to_process, wv)
    print("finished create emb")
    print("process_done!")
    
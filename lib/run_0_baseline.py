from utils import metadata2dict, regex_hyphen, regex_punct, read_topics_set_to_df, wh_list
import re
import json
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import Counter
import sys
import numpy as np
from gensim.models import KeyedVectors
from sklearn.feature_extraction import DictVectorizer

import spacy
nlp = None


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
        fname = path_output + uid + "_tf.json"
        if os.path.exists(fname):
            with open(fname, "r") as f:
                tf = json.load(f)
                index.extend(list(tf.keys()))

    idf = Counter(index)
    with open(path_output + "idf.json", "w") as f:
        json.dump(idf, f)           

def process():
    path_to_data = sys.argv[2]
    path_to_process = sys.argv[3]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    
    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
     

    create_tf(path_to_data, metadata_dict, path_to_process)
    print("finished create tf")
    create_idf(metadata_dict, path_to_process)
    print("finished create idf")
    
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
    
    
def query():

    path_to_data = sys.argv[2]
    path_to_process = sys.argv[3]
    path_to_topics = sys.argv[4]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"

    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)        
    topics_df = read_topics_set_to_df(path_to_topics)

    v = DictVectorizer()
    idx2uid = list()
    list_of_tfidf = list()
    
    with open(path_to_process + "idf.json", "r") as f:
        idf = json.load(f)  
    
    print("finished load data")
    
    for uid, info in metadata_dict.items():
        
        fname = path_to_process + uid + "_tf.json"
        if os.path.exists(fname):
            with open(fname, "r") as f:
                tf = json.load(f) 
                
            for token in tf:
                tf[token] = (1 + np.log(tf[token])) * np.log(len(idf) / idf[token]) 
            list_of_tfidf.append(tf)
            idx2uid.append(uid)
            
    doc_vectors = v.fit_transform(list_of_tfidf)
    assert doc_vectors.shape[0] == len(idx2uid)
    print("finished vectorize document")
    
    list_of_query = list()
    for q in topics_df["query"]:
        cleaned_query = get_clean_query(q)
        cleaned_query = list(set(cleaned_query))
        list_of_query.append(Counter(cleaned_query))
    
    query_vectors =  v.transform(list_of_query)
    assert query_vectors.shape[0] == len(topics_df)
    print("finished vectorize query")
    
    sim = cosine_similarity(query_vectors, doc_vectors)
    assert sim.shape[0] == len(topics_df), len(idx2uid)
    assert sim.shape[1] ==  len(idx2uid)
    
    create_report(topics_df, sim, idx2uid)
    print("finished create report")

    
def create_report(topics_df, sim, idx2uid):
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
    with open("report_run_0.txt", "w") as f:
        f.write(report)
            

if __name__ == "__main__":
    if sys.argv[1] == "-p":
        process() # -p path_to_data path_to_save_processed e.g. python run_0_baseline.py -p ../../CORD-19/2020-06-19/ ../tmp/run0/
    elif sys.argv[1] == "-q":
        nlp = spacy.load("en_core_web_sm")
        query() # -q path_to_data path_to_save_processed  patn_to_topics e.g. python run_0_baseline.py -q ../../CORD-19/2020-06-19/ ../tmp/run0/ ../topics-rnd4.xml
    else:
        print("invalid usage")
        exit()
        

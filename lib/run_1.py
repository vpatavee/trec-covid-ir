from utils import metadata2dict, regex_hyphen, regex_punct, read_topics_set_to_df
import re
import json
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import Counter
import sys
import numpy as np
from gensim.models import KeyedVectors
from run_0_baseline import create_tf, create_idf, get_clean_query, create_report
import spacy


def create_emb(path_output, wv, metadata_dict):
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
        if np.linalg.norm(vect) != 0:
            vect = vect / np.linalg.norm(vect)

        ltc[uid] = list(vect)
        
    with open(path_output + "ltc.json", "w") as f:
        json.dump(ltc, f)   
        
    print("oov", list(oov))
    with open(path_output + "oov.json", "w") as f:
        json.dump({"oov": list(oov)}, f)      

        
def process():
    path_to_data = sys.argv[2]
    path_to_process = sys.argv[3]
   
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    print("loading metadata dict")
    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
    print("creating doc vector")
    create_emb(path_to_process, wv, metadata_dict)
     
    # already done in run_0_baseline.py
    # create_tf(path_to_data, metadata_dict, path_to_process)
    # print("finished create tf")
    # create_idf(metadata_dict, path_to_process)
    # print("finished create idf")
    

def query():
    
    path_to_data = sys.argv[2]
    path_to_process = sys.argv[3]
    path_to_topics = sys.argv[4]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"

    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)        
    topics_df = read_topics_set_to_df(path_to_topics)


    idx2uid = list()
    
    print("loadint ltc")
    with open(path_to_process + "ltc.json", "r") as f:
        ltc = json.load(f)  
        
    doc_vectors = np.zeros([len(ltc), 300])
    for i, (uid, vect) in enumerate(ltc.items()):
        doc_vectors[i, :] = vect
        idx2uid.append(uid)
        
    query_vectors = np.zeros([len(topics_df), 300])

    for i, q in enumerate(topics_df["query"]):
        cleaned_query = get_clean_query(q)

        for tok in list(set(cleaned_query)):
            if tok in wv:
                query_vectors[i, :] += wv[tok]
            else:
                print("query oov",i , tok)
                
        if np.linalg.norm(query_vectors[i, :]) != 0:
            query_vectors[i, :] = query_vectors[i, :] /  np.linalg.norm(query_vectors[i, :])
        
        
    sim = cosine_similarity(query_vectors, doc_vectors)
    assert sim.shape[0] == len(topics_df), len(idx2uid)
    assert sim.shape[1] ==  len(idx2uid)
    
    create_report(topics_df, sim, idx2uid, "report_run_1.txt")
    print("finished create report")        
        

            
        
if __name__ == "__main__":
#     wv_path = "../tmp/wv_300_15_cleaned_uncased_trained_2020-06-19.model"
#     wv = KeyedVectors.load(wv_path)
    
    gg_wv_path = "/home/pmeemeng/dev/efs/patavee/GoogleNews-vectors-negative300.bin"
    wv = KeyedVectors.load_word2vec_format(gg_wv_path, binary=True)
    
    
    if sys.argv[1] == "-p":
        process() # -p path_to_data path_to_save_processed e.g. python run_1.py -p ../../CORD-19/2020-06-19/ ../tmp/run0/
    elif sys.argv[1] == "-q":
        nlp = spacy.load("en_core_web_sm")
        query() # -q path_to_data path_to_save_processed  patn_to_topics e.g. python run_1.py -q ../../CORD-19/2020-06-19/ ../tmp/run0/ ../topics-rnd4.xml
    else:
        print("invalid usage")
        exit()
        
        
# if __name__ == "__main__":
#     path_to_data = sys.argv[1]
#     path_to_process = sys.argv[2]
    
#     path_to_metadata = path_to_data + "metadata.csv"
#     path_to_document_parses = path_to_data + "document_parses/"
    
#     wv = KeyedVectors.load("../wv/wv_300_15_cleaned_uncased_trained_2020-06-19.model")
    

#     metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
#     create_tf(path_to_data, metadata_dict, path_to_process)
#     print("finished create tf")
#     create_idf(metadata_dict, path_to_process)
#     print("finished create idf")
#     create_emb(path_to_process, wv)
#     print("finished create emb")
#     print("process_done!")
    
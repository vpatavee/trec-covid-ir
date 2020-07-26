# simple solr on abstract (boost) and body

from utils import metadata2dict, regex_hyphen, regex_punct, read_topics_set_to_df, get_clean_query, create_report, evaluate
import re
import json
import os
import sys
import numpy as np
import pysolr
 

def query(solr, topics_df, metadata_dict, report_name):
    idx2uid = list(metadata_dict.keys())
    uid2idx = {doc:idx for idx, doc in enumerate(idx2uid)}
    sim = np.zeros([len(topics_df), len(idx2uid)])
    
    for i, q in enumerate(topics_df["query"]):
        cleaned_query = get_clean_query(q)
        q = prepare_query_body_title_abstract(cleaned_query)
#         print(q)

        solr_query_param = {
            "fl": "id,score",
            "rows": 1000
        }
        results = solr.search(q, **solr_query_param).docs
        
        if len(results) != 1000:
            print(q)
            
            
        for result in results:
            sim[i, uid2idx[result["id"]]] = result["score"]
            
    create_report(topics_df, sim, idx2uid, report_name)
    evaluate(report_name)

    

def prepare_query_body_title_abstract(cleaned_query):
    query = ""
    words = " ".join(cleaned_query)
    

    return "body:({}) abstract:({}) title:({})".format(words, words, words)
      
        

if __name__ == "__main__":
    """
    Preq: solr index must be created.
    
    python run_2_simple_solr.py -q ../../CORD-19/2020-06-19/ cord-19-2020-06-19 ../tmp/topics-rnd4.xml
    
    """
    
    report_name = "../prepare_query_body_title_abstract.txt"
                

    if sys.argv[1] != "-q":
        print("solr run only has -q mode")
        exit()
    
    path_to_data = sys.argv[2]
    core_name = sys.argv[3]
    path_to_topics = sys.argv[4]    
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    
    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
    topics_df = read_topics_set_to_df(path_to_topics)
    
    
    solr = pysolr.Solr('http://0.0.0.0:8983/solr/' + core_name, timeout=10, always_commit=True )
    ping = json.loads(solr.ping())
    

    if ping["status"] != "OK":
        print("solr conection error", ping)
        
    query(solr, topics_df, metadata_dict, report_name)

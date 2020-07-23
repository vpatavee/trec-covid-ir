
from utils import metadata2dict
import re
import json
from collections import Counter
import sys

def create_tf(path_to_document_parses, metadata_dict, path_output):
    regex_hyphen = re.compile(r'[-_]')
    regex_punct = re.compile(r'[^\w]')
    
    for uid, fname in metadata_dict.items():
        list_of_words = list()
        with open(path_to_document_parses + fname["path"], "r") as f:
            bodies = json.load(f)["body_text"]
            for body in bodies:
                text = body["text"]
                text = text.lower().strip()
                text = re.sub(regex_hyphen, "", text)
                text = re.sub(regex_punct, " ", text)
                list_of_words.extend(text.split())
        counter = Counter(list_of_words)
        
        with open(path_output + uid + "_tf.json", "w") as f:
            json.dump(counter, f)    
            

if __name__ == "__main__":
    path_to_data = sys.argv[1]
    path_to_process = sys.argv[2]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    

    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)
    create_tf(path_to_data, metadata_dict, path_to_process)
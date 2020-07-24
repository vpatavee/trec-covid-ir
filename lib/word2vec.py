import json
import time
import sys
from utils import metadata2dict
import os 
import re
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
from gensim.models import Word2Vec


"""
-remove - and _ 
-replace everything but alphanumeric with space
-lower case
"""

regex_hyphen = re.compile(r'[-_]')
regex_punct = re.compile(r'[^\w]')

class Corpus(object):
    def __init__(self, metadata_dict, path_to_document_parses):
        self.metadata_dict = metadata_dict
        self.path_to_document_parses = path_to_document_parses
        
    def __iter__(self):
        for uid, info in self.metadata_dict.items():
             with open(self.path_to_document_parses + info["path"], "r") as f:    
                bodies = json.load(f)["body_text"]
                if info["abstract"].strip():
                    text = info["abstract"]
                    text = text.lower()
                    text = re.sub(regex_hyphen, "", text)
                    text = re.sub(regex_punct, " ", text)
                    yield text.split()
                    
                for body in bodies:
                    text = body["text"]
                    text = text.lower()
                    text = re.sub(regex_hyphen, "", text)
                    text = re.sub(regex_punct, " ", text)
                    yield text.split()
                    


class Callback(CallbackAny2Vec):
    def __init__(self, model_name):
        self.time = time.time()
        self.epoch = 0
        self.model_name = model_name
        self.loss = 0

    def on_epoch_end(self, model):
        now = time.time()
        loss = model.get_latest_training_loss()
        print('Epoch {}: Time {:.2f} s, Loss {:.2f}'.format(self.epoch, now-self.time, loss - self.loss))
        model.save("{}.{}".format(self.model_name, self.epoch))
        self.epoch += 1
        self.time = time.time()
        self.loss = loss
        

if __name__ == "__main__":
    path_to_data = sys.argv[1]
    
    path_to_metadata = path_to_data + "metadata.csv"
    path_to_document_parses = path_to_data + "document_parses/"
    
    metadata_dict = metadata2dict(path_to_metadata, path_to_document_parses)

    corpus = Corpus(metadata_dict, path_to_data)

    # model
    rev = path_to_data.split("/")[-2]
    model_name = "wv_300_15_cleaned_uncased_trained_" + rev + ".model"
    print("model_name", model_name)
    model = Word2Vec(
        corpus,
        sg=1,
        min_count=1,
        size=300,
        window=15,
        workers=64,
        iter=5,
        compute_loss=True,
        callbacks=[Callback(model_name)]
    )

    model.wv.save("../tmp/" + model_name)


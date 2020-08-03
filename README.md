# trec-covid-ir-round-5



## Score

1. Clone [trec_eval](https://github.com/usnistgov/trec_eval)
2. Make
```
cd trec_eval
make
```
3. Test by get a submission from [round 4](https://ir.nist.gov/covidSubmit/archive/archive-round4.html) and  compare the result with score report. For example,
```
wget https://ir.nist.gov/covidSubmit/archive/round4/covidex.r4.duot5.lr.gz
gunzip covidex.r4.duot5.lr.gz
wget https://ir.nist.gov/covidSubmit/data/qrels-covid_d4_j3.5-4.txt
./trec_eval -c -m ndcg_cut.20 -m P.20 -m bpref -m map qrels-covid_d4_j3.5-4.txt covidex.r4.duot5.lr > result.txt
```

compare the `result.txt` with [report](https://ir.nist.gov/covidSubmit/archive/round4/covidex.r4.duot5.lr.pdf). If everything goes well, then do the same thing for your runs.


Get Round 4 topics set

`wget https://ir.nist.gov/covidSubmit/data/topics-rnd4.xml`


## py

We have a pair of process script and query script with run name e.g. `run_1_process.py`. 

query file will save file in the submission format, ready to run `score.py`.

process script takes the following argument: path_to_data, path_to_output (store the process results e.g. doc vectors)

query script takes the following argument: path_to_processed_document_parses, path_to_topics

For examples:


```
mkdir tmp/run1
cd py
python run_0_baseline.py -p ../../CORD-19/2020-06-19/ ../tmp/run0/
python query
```

How to create word2vec.py

`python word2vec.py ../../CORD-19/2020-06-19/`


## Revision Logs


### Run 0

Process: Simple TFIDF + log
Query: binary 
```
[pmeemeng@ip-10-66-39-234 trec_eval]$ ./trec_eval -c -m ndcg_cut.20 -m P.20 -m bpref -m map qrels-covid_d4_j3.5-4.txt report_run_0.txt
map                     all     0.0433
bpref                   all     0.2491
P_20                    all     0.1544
ndcg_cut_20             all     0.1342
```


```
./trec_eval -c -m ndcg_cut.20 -m P.20 -m bpref -m map ../trec-covid-ir-round-5/qrels-covid_d4_j0.5-4.txt  ../scibert/anserini_scibert_rerank.txt
```

### Run 1

Process: Use Word2vec, convert to vectors document level all text, ltc, clean, uncase

Query: Convert query using Word2vec, nnc, use cosine sim, query remove stop words, wh words, clean, uncase


Word2vec: Trained on Kaggle CORD-19 Dataset, all pdf and pmc. Not use abstract from metadata, uncase

clean with 
```
regex_hyphen = re.compile(r'[-_]')
regex_punct = re.compile(r'[^\w]')

```


model params

```
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
```


Result
```
$ ./trec_eval -c -m ndcg_cut.20 -m P.20 -m bpref -m map qrels-covid_d4_j3.5-4.txt report_run_1.txt
map                     all     0.0339
bpref                   all     0.2161
P_20                    all     0.1444
ndcg_cut_20             all     0.1269
```

Result GG Word2vec
```
map                     all     0.0026
bpref                   all     0.0465
P_20                    all     0.0211
ndcg_cut_20             all     0.0191

```


## Run2

basic solr

setup solr
```
docker pull solr
docker run -d -p 8983:8983 -t solr
docker exec -it solr /bin/bash
bin/solr create -c <corename> 

```
result

```
map                     all     0.0717
bpref                   all     0.2781
P_20                    all     0.2378
ndcg_cut_20             all     0.2240
```

## Run 3

{'map': '0.0511', 'bpref': '0.1721', 'P_20': '0.2211', 'ndcg_cut_20': '0.2084'}

paragraph level solr
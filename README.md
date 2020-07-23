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


## Search

In search folder, we have process script and query script, each follow by run name / iteration. 
query file will save file in the submission format, ready to run `score.py`.

process script takes the following argument: path_to_document_parses, path_to_processed_document_parses

query script takes the following argument: path_to_processed_document_parses, path_to_topics


## Revision Logs

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
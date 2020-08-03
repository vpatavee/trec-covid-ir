# TREC-COVID Challenge

TREC-COVID Challenge is an Information Retrieval (IR) challenge for COVID-19 research papers.

In a nutshell, we are given the massive researh papers about COVID-19 and a set of topics i.e. 
where is COVID-19 origin? The goal is to retrieve the documents that have answers for each topic.
For formal task definition, dataset, evaluation and so on, visit the [official website](https://ir.nist.gov/covidSubmit).

TREC-COVID Challenge is series of rounds. As of 8/2/2020, there five rounds. Each round comes with
new topics and new research papers. In this repo, I will use [round 4 dataset](https://ir.nist.gov/covidSubmit/data.html),
where the human judgement is available. The dataset consists of

1. The COVID-19 research papers dataset called [CORD-19](https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases.html). Use 2020-07-16 version. To understand the datast, read [FAQ](https://github.com/allenai/cord19/blob/master/README.md).

2. Topics, download [here](https://ir.nist.gov/covidSubmit/data/topics-rnd4.xml).

3. Human judgements, download [here](https://ir.nist.gov/covidSubmit/qrels4.html).

For those who are not familiar with Information Retrieval, check out this [textbook](https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf). For those who are familiar with IR but not TREC, visit the [official website](https://trec.nist.gov/overview.html).


## In this Repos

**Literature Review**

As described in task definition, we can solve TREC-COVID challenge in three different ways; automatic, feedback and manual.
Automatic is purely unsupervised. Feedback makes use of previous human judgements to improve the performance. Manual
requries human efforts to create or modify queries from given topics.

Here is [list](https://ir.nist.gov/covidSubmit/archive/archive-round4.html) of reports which breifly describe what techniques 
people has used. Most efforts use the Lucene based search engine e.g. Elasticsearch, Solr or Anserini to 
retrieve documents. Then use Deep Learning based approaches i.e. BERT, DeepRank etc to rerank the retrieve documents.


In this repos, we will explore new techniques to improve the performance. We may have to reproduce some approaches that people made and start improving from that point. 



## Evaluation

Standard TREC evaluation can be found [here](https://trec.nist.gov/pubs/trec22/appendices/measures.pdf). The original C Codes are available [here](https://github.com/usnistgov/trec_eval). Python version is also available [here](https://github.com/cvangysel/pytrec_eval).



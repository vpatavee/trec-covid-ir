# trec-covid-ir-round-5



## Score

TODO: Figure out how to run [trec_eval](https://github.com/usnistgov/trec_eval)

For now, run `python score.py <result> <qrel>`

## Search

In search folder, we have process script and query script, each follow by run name / iteration. 
query file will save file in the submission format, ready to run `score.py`.

process script takes the following argument: path_to_document_parses, path_to_processed_document_parses

query script takes the following argument: path_to_processed_document_parses, path_to_topics


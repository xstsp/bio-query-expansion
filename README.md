# bio-query-expansion
Code for my thesis "Query expansion for biomedical document retrieval"

The main task of this work is to provide an efficient way for expansion of user questions with relevant terms as a means of improving the document retrieval accuracy. We have implemented a system that identifies domain-related special terms within a text, using our pre-defined vocabulary and uses the new corpus of sentences as training input to a word2vec model. Then, using the trained word embeddings, we perform query expansion and evaluate on a test set of questions.

To achieve this, we need to define three discrete and independent phases:
* Special-terms vocabulary creation
* Model training
* Question expansion

![method](/var/method.png)


## Vocabulary creation
```model/vocabulary-31.py```

Creates a new vocabulary of special terms from elasticsearch docs and stores in Redis.

The existing vocabulary (redis dump) can be found here: https://github.com/xstsp/bio-exp-storage/blob/master/dump.rdb.gz

To use this dump:
* Download the file and unzip it using ```sudo gunzip dump.rdb.gz```.
* Copy dump.rdb in ```/var/lib/redis/```
* Start redis server


## Model training
```model/model_creation.py```

Trains word2vec model using Gensim. Sentences already replaced with vocabulary terms, come from local files.
A sample trained model is available here (BIG FILE- 130MB): https://github.com/xstsp/bio-exp-storage/blob/master/trained_model.tar.gz

To use this file:
* Download and run ```tar -xvzf trained_model.tar.gz```
* Move the files in *trained_models/*
* Check that ```PROD_MODEL = 'prod_model'  ``` in *conf.py*


## Question expansion
```api/controllers.py```

Requests for expansion can be issued via REST calls to /search endpoint. uwsgi serves the python application and can be run with:

```uwsgi --http-socket localhost:3031 --wsgi-file run.py  --master --processes 4 --threads 2```

Send requests from command line:

```curl -H "Content-Type: application/json" -X POST -d @data.json localhost:3031/search```

sample JSON input:
```
{
	"query": "What is the Quiescent Phenotype ECs?",
	"scenario": "exp"
}
```
* *Need to set Elastic IPs to an existing cluster*

## Model evaluation
```results/dataset.py```

Runs 500 questions from BIOASQ and stores results from elastisearch in json file.

```results/remove_maxid.py```

Postprocessing of results. Should be run after dataset.py

```results/eval_script.py```

Calculates precision, recall, f1, MAP for the latest results.



### Configuration
```conf.py```


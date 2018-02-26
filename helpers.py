from __future__ import print_function
from pymongo import MongoClient
from results import es_search
import os
import conf as con
import json
import nltk
import gensim
import logging
import requests
import redis
import re
import itertools


class Vocabulary:
    def __init__(self, hash_name, redis_con):
        self.redis_con = redis_con
        self.hash = hash_name

    def __iter__(self):
        for k, v in self.redis_con.hgetall(self.hash).items():
            yield k, v

    def get(self):
        for k, v in self.redis_con.hscan_iter(self.hash, count=10000):
            yield k, v


# taken from model-creation, maybe not used
def handle_tokens(tokens):
    ret = []
    for token in tokens:
        # remove special chars from start/end
        ntoks = [t for t in re.split('(^[^a-zA-Z0-9]*|[^a-zA-Z0-9]*$)', token) if (len(t) > 0)]
        #
        ntoks = [re.sub('\d', 'D', tok) for tok in ntoks]
        ntoks2 = []
        for ntok in ntoks:
            ntoks2.extend(re.split('([\(\)\[\]\{\},])', ntok))
        ret.extend(ntoks2)

    toks = [r for r in ret if (len(r.strip()) > 0)]
    return toks


def replace_text_from_voc(words):
    text = ' '.join(words)

    # get the longest match - start from lengthiest ngram
    # len of words is big, 10 is enough
    max_range = len(words) if len(words) > 10 else 10

    for n_size in range(max_range, 1, -1):
        # create unique ngrams
        ngrams = {w for w in nltk.ngrams(words, n_size)}
        # transform ngram tuples to strings of words
        r_get_list = [' '.join([j for j in ngram]) for ngram in ngrams]
        # get mappings from vocabulary
        try:
            r_res = redis_con.hmget(con.VOC_NAME, r_get_list)
        except:
            continue

        # at least one term found in redis vocabulary
        if any(r_res):
            replace = {k[0]: k[1] for k in zip(r_get_list, r_res) if k[1]}

            temp = "|".join(replace.keys())
            pattern = re.compile(temp)
            text = pattern.sub(lambda m: replace[m.group(0)], text)
    return [w for w in text.split()]


def get_trained_model(model_type):
    # select between our model or pre-trained from bioASQ
    if model_type == con.EXPANDED:
        model_name = con.PROD_MODEL
        model_path = os.path.join(con.TRAINED_MODELS_PATH, model_name)
        try:
            model = gensim.models.Word2Vec.load(model_path)
        except IOError as e:
            # no model found - continue without expansion
            logging.info(e)
            model = None
    else:
        model_name = con.BIO_TRAINED_MODEL
        model_path = os.path.join(con.TRAINED_MODELS_PATH, model_name)
        try:
            model = gensim.models.KeyedVectors.load_word2vec_format(model_path)
        except IOError as e:
            # no model found - continue without expansion
            logging.info(e)
            model = None
    return model

# load model on startup
g_model = get_trained_model(con.EXPANDED)


def redis_connect():
    redis_conn = redis.StrictRedis(host='localhost', port=6379, db=con.REDIS_DB, charset="utf-8", decode_responses=True)
    return redis_conn

# global variable for vocabulary store
redis_con = redis_connect()


def mongo_connect():
    client = MongoClient('localhost', 27017)
    db = client[con.MONGO_DB]
    scores = db[con.MONGO_COLL]
    return scores

# global variable for questions scores store
mongo_scores = mongo_connect()


def get_vocabulary(name):
    path = os.path.join(con.TRAINED_MODELS_PATH, name)
    with open(path, 'r') as voc:
        return json.load(voc)


def get_q_id(query):
    qwords = sentence_tokenizer(query)
    q_id = '_'.join(qwords)
    return q_id


def sentence_tokenizer(sentence):
    sub_sen = re.sub(con.PUNCT, " ", sentence).lower().split()
    words = [x for x in sub_sen if x not in con.STOPWORDS]
    return words


def expand_query(qwords, scenario):
    avg_sim = 0
    if g_model and scenario == con.EXPANDED:
        logging.info('expanding query...')
        tokens = replace_text_from_voc(qwords)
        similar_terms, avg_sim = get_similar_from_model(tokens)
        logging.info('...done')
        # print(similar_terms)
        if con.EXTRA == 'explosion':
            # create all combinations of similar terms
            # and return generator
            return itertools.product(*similar_terms), avg_sim
        else:
            return similar_terms, avg_sim
    else:
        # query contains only the original terms
        return qwords, avg_sim


def get_similar_from_model(words):
    # set a meaningful value to evaluate "similarity"
    threshold = con.THRESHOLD

    avg_sim = []
    final_list = []
    for word in words:
        # keep the actual word
        curl = [word]
        try:
            similar = g_model.wv.most_similar(word)
            # print('similar to ' + word + ' : ')
            # print(similar)
            curl.extend([x[0] for x in similar if x[1] > threshold])
            s = sum([x[1] for x in similar])
            avg_sim.append(s / len(similar) if similar else 0)
        except KeyError as e:
            # term not found in vocabulary
            logging.info(e)
        except AttributeError:
            # no model found
            break

        curl = [redis_con.hget(con.REVERSE_VOC_NAME, x) if str(x).startswith(con.VOC_PREFIX) else x for x in curl]
        # in case redis return None
        curl = [x for x in curl if x is not None]

        final_list.append(curl)

    avg_similarity = sum(avg_sim) / len(avg_sim) if avg_sim else 0
    return final_list, avg_similarity


def query_search(query, scenario):
    # TODO: add celery tasks to support multiple queries

    qwords = sentence_tokenizer(query)
    meta = dict()
    # keep the query as key for metadata
    q_id = '_'.join(qwords)
    meta['orig_count'] = len(qwords)

    # data = mongo_scores.find_one({'q_id': q_id})
    # if data:
    #     # print('found in cache!')
    #     res = dict({'q_id': q_id,
    #                 'documents': data['docs'],
    #                 'meta': data['meta']})
    #     return res

    explosion = []

    if scenario != con.ELK:
        xquery_gen, meta['avg_similarity'] = expand_query(qwords, scenario)
        if con.EXTRA == 'explosion':
            for xq in xquery_gen:
                # stemming might be necessary here due to many generated phrases
                explosion.append(' '.join([i for i in xq]))
        else:
            for xq in xquery_gen:
                explosion.extend(xq)
    else:
        # explosion.append(' '.join(qwords))
        # consider the original query instead of split words
        explosion.append(query)

    logging.info(explosion)
    meta['explosion_size'] = len(explosion)
    logging.info(meta['explosion_size'])

    logging.info('searching elastic...')

    es = es_search.SearchElastic(explosion)
    try:
        es_res = es.run_search()
    except Exception as e:
        logging.info(e)

    logging.info('...done')

    res_docs = []
    for i in range(50):
        try:
            # add better handling
            res_docs.append(es_res[u'hits'][u'hits'][i]['_source']['pmid'])
        except:
            logging.info('Finished early...')
            break

    res = dict({'q_id': q_id,
                'documents': res_docs,
                'meta': meta})
    # mongo_scores.insert_one(res)
    return res


def search_bioxq_http(query, scenario):

    url = con.URL + scenario
    os.environ['NO_PROXY'] = '127.0.0.1'
    post_data = {'query': query, 'scenario': scenario}
    try:
        read = requests.post(url, json=post_data)
        read.raise_for_status()
        return read
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return {'error': e}


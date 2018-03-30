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
import math
import multiprocessing


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
    max_range = 10 if len(words) > 10 else len(words)
    for n_size in range(max_range, 1, -1):
        # create unique ngrams
        ngrams = {w for w in nltk.ngrams(words, n_size)}
        # transform ngram tuples to strings of words
        r_get_list = [' '.join([j for j in ngram]) for ngram in ngrams]
        del ngrams
        # get mappings from vocabulary
        try:
            r_res = redis_con.hmget(con.VOC_NAME, r_get_list)
        except:
            continue

        # at least one term found in redis vocabulary
        if any(r_res):
            replace = {k[0]: k[1] for k in zip(r_get_list, r_res) if k[1]}
            del r_get_list
            del r_res
            # temp = "|".join(replace.keys())
            # pattern = re.compile(temp)
            # text = pattern.sub(lambda m: replace[m.group(0)], text)
            for k, v in replace.items():
                text = text.replace(k, v)
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

if g_model:
    print('model loaded')
else:
    print('not loaded')


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


def get_from_elastic(in_list):
    logging.info('searching elastic...')
    es = es_search.SearchElastic(in_list)
    try:
        es_res = es.run_search()
    except Exception as e:
        logging.info(e)

    logging.info('...done')

    res_docs = []
    for i in range(50):
        try:
            # add better handling
            res_docs.append((es_res[u'hits'][u'hits'][i]['_source']['pmid'],
                             es_res[u'hits'][u'hits'][i]['_score']))
        except:
            logging.info('Finished early...')
            break
    return res_docs


class MultiElastic(object):
    def __init__(self, big_list):
        # use all cores
        self.jobs = 5
        self.list = big_list

    def parallelize(self):
        pool = multiprocessing.Pool(self.jobs)
        # logging.info("Children processes running : {}".format(multiprocessing.active_children()))
        try:
            for output in pool.imap(get_from_elastic, self.list, chunksize=2):
                yield output
        except MemoryError as e:
            pool.close()
            pool.join()
            logging.info("Out of memory - exited - {}".format(e))

        except Exception as e:
            logging.error(e)
        finally:
            pool.close()
            pool.join()
            logging.info("All processes joined successfully")


def query_search(query, scenario):
    # TODO: add celery tasks to support multiple queries
    # for query in queries:
    qwords = sentence_tokenizer(query)
    print(qwords)
    meta = dict()
    # keep the query as key for metadata
    q_id = '_'.join(qwords)
    meta['orig_count'] = len(qwords)

    explosion = []

    if scenario != con.ELK:
        xquery_gen, meta['avg_similarity'] = expand_query(qwords, scenario)
        # meta['xquery'] = xquery
        if con.EXTRA == 'explosion':
            for xq in xquery_gen:
                # logging.info(xq)
                explosion.append(' '.join([i for i in xq]))
        else:
            for xq in xquery_gen:
                explosion.extend(xq)
    else:
        #explosion.append(' '.join(qwords))
        explosion.append(query)

    logging.info(explosion)
    meta['explosion_size'] = len(explosion)
    logging.info(meta['explosion_size'])

    size = 80
    # need to break queries into batches
    if len(explosion) > size:
        res_docs = get_batches_from_elastic(explosion, size)
    else:
        res_docs = get_single_from_elastic(explosion)

    res = dict({'q_id': q_id,
                'documents': res_docs,
                'meta': meta})

    return res


def get_single_from_elastic(lis):
    return [i[0] for i in get_from_elastic(lis)]


def get_batches_from_elastic(lista, size):
    logging.info('Batch mode: {}'.format(len(lista)))
    split = list_to_batches(lista, size)
    logging.info('Split to {} batches'.format(len(split)))
    full_ret = []
    me = MultiElastic(split)
    for batch in me.parallelize():
        logging.info('extending: {}'.format(batch))
        full_ret.extend(batch)
    # rank all results
    sfull = sorted(full_ret, key=lambda x: x[1], reverse=True)
    rem_dups(sfull)
    return [i[0] for i in sfull[:50]]


def list_to_batches(ll, size):
    batches = math.ceil(len(ll) / size)
    parts = []
    for i in range(batches):
        start = i * size
        end = start + size
        parts.append(ll[start:end])
        # print(parts)
    return parts


def rem_dups(l):
    for item in l:
        for z in reversed([i for i, x in enumerate(l) if x[0] == item[0]][1:]):
            l.pop(z)


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


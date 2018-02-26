from __future__ import print_function

import pickle
import time

from doc_iters import *
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)


def get_document_voc_terms(data):
    """
    Reads metadata such as 'keywords' from the given document
    """
    doc_terms = set()
    try:
        if 'MeshHeadings' in data and data['MeshHeadings']:
            doc_terms.update({k['text'] for k in data['MeshHeadings']})
        if 'Chemicals' in data and data['Chemicals']:
            doc_terms.update({k['NameOfSubstance'] for k in data['Chemicals']})
        if 'Keywords' in data and data['Keywords']:
            doc_terms.update({k for k in data['Keywords']})
    except KeyError as e:
        # term is not present in current doc
        logging.info(e)

    # do not keep single-word terms
    return {' '.join(sentence_tokenizer(d)) for d in doc_terms if re.search('[^a-zA-Z0-9]', d)}

# delete existing vocabularies, if any
logging.info(redis_con.delete(con.VOC_NAME))
logging.info(redis_con.delete(con.REVERSE_VOC_NAME))

t0 = time.time()

docs = ElasticDocs()
# docs = DocTerms(it)

full_set = set()
doc_count = 0
for doc in docs:
    special_terms = get_document_voc_terms(doc)
    full_set.update(special_terms)
    doc_count += 1
    if doc_count % 500000 == 0:
        logging.info('{} documents in {} secs'.format(str(doc_count),
                                                      str(time.time() - t0)))

logging.info("Full set created: {} documents, {} terms, in {} secs".format(str(doc_count),
                                                                           str(len(full_set)),
                                                                           str(time.time() - t0)))

# keep terms for backup
tt = time.time()
try:
    fname = os.path.join(con.TRAINED_MODELS_PATH, 'full_set')
    with open(fname, 'wb') as stream:
        pickle.dump(full_set, stream)
    logging.info('pickled in {} secs'.format(str(time.time() - tt)))
except:
    logging.info('pickling failed')

t1 = time.time()
vocabulary = {}
reverse_voc = {}
batch = 0
for i, term in enumerate(full_set):
    val = con.VOC_PREFIX + str(i)
    vocabulary[term] = val
    reverse_voc[val] = term

    # write to Redis in batches
    if i % 400000 == 0 and i != 0:
        batch += 1
        logging.info('Batch {}: {} total terms, {} terms in voc batch, {} secs elapsed'.format(str(batch),
                                                                                               str(i),
                                                                                               str(len(vocabulary)),
                                                                                               str(time.time() - t1)))

        t2 = time.time()
        # if vocabulary and reverse_voc contain terms:
        ret_voc = redis_con.hmset(con.VOC_NAME, vocabulary)
        ret_rev = redis_con.hmset(con.REVERSE_VOC_NAME, reverse_voc)

        if ret_rev and ret_voc:
            logging.info('Batch written in: {} secs'.format(str(time.time() - t2)))
            vocabulary = {}
            reverse_voc = {}
        # redis write failed - fallback to json file
        else:
            try:
                fname = '_'.join([os.path.join(con.TRAINED_MODELS_PATH, con.VOC_NAME), str(batch)])
                with open(fname, 'w') as stream:
                    json.dump(vocabulary, stream)

                fname = '_'.join([os.path.join(con.TRAINED_MODELS_PATH, con.REVERSE_VOC_NAME) + str(batch)])
                with open(fname, 'w') as stream:
                    json.dump(reverse_voc, stream)
            except:
                logging.info('json write failed')

            vocabulary = {}
            reverse_voc = {}

t2 = time.time()
batch += 1
# write the remaining terms
ret_voc = redis_con.hmset(con.VOC_NAME, vocabulary)
ret_rev = redis_con.hmset(con.REVERSE_VOC_NAME, reverse_voc)

if ret_rev and ret_voc:
    logging.info('Batch written in: {} secs'.format(str(time.time() - t2)))
    vocabulary = {}
    reverse_voc = {}
# redis write failed - fallback to json file
else:
    try:
        fname = '_'.join([os.path.join(con.TRAINED_MODELS_PATH, con.VOC_NAME), str(batch)])
        with open(fname, 'w') as stream:
            json.dump(vocabulary, stream)

        fname = '_'.join([os.path.join(con.TRAINED_MODELS_PATH, con.REVERSE_VOC_NAME) + str(batch)])
        with open(fname, 'w') as stream:
            json.dump(reverse_voc, stream)
    except:
        logging.info('json write failed')

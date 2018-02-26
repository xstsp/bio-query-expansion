from __future__ import print_function
import time

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import conf as con
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

es = Elasticsearch([
        '127.0.0.1'
    ],
    verify_certs=True,
    timeout=150,
    max_retries=10,
    retry_on_timeout=True
)
index = 'pubmed_abstracts_0_1'
doc_type = 'abstract_0_1'

scroll = scan(
    client=es,
    index=index,
    query=None,
    scroll=u'5m',
    raise_on_error=True,
    preserve_order=False, size=1000,
    request_timeout=45,
    clear_scroll=True
)


class DocTerms(object):
    def __init__(self, elastic_iter):
        self.elastic = elastic_iter

    @staticmethod
    def get_document_voc_terms(data):
        """
        Reads metadata such as 'keywords' from the given document
        """
        doc_terms = set()
        try:
            if 'MeshHeadings' in data and data['MeshHeadings']:
                doc_terms.update({k['text'].lower() for k in data['MeshHeadings']})
            if 'Chemicals' in data and data['Chemicals']:
                doc_terms.update({k['NameOfSubstance'].lower() for k in data['Chemicals']})
            if 'Keywords' in data and data['Keywords']:
                doc_terms.update({k.lower() for k in data['Keywords']})
        except KeyError as e:
            # term is not present in current doc
            logging.info(e)

        return doc_terms

    def __iter__(self):
        for doc in self.elastic:
            try:
                special_terms = self.get_document_voc_terms(doc['_source'])
                yield special_terms
            except:
                logging.error('elastic exception')
                continue

t0 = time.time()

# delete existing vocabularies, if any
print(redis_con.delete(con.VOC_NAME))
print(redis_con.delete(con.REVERSE_VOC_NAME))

terms_set = DocTerms(scroll)

vocabulary = {}
reverse_voc = {}
doc_count = 0
for terms in terms_set:
    for term in terms:
        # do not keep single-word terms
        if re.search('[^a-zA-Z0-9]', term):
            try:
                # if term exists
                val = vocabulary[term]
            except KeyError:
                val = con.VOC_PREFIX + str(len(vocabulary))
                vocabulary[term] = val
                reverse_voc[val] = term

    # print progress
    if doc_count % 800000 == 0:
        print('Currently in {} documents, {} terms, {} secs elapsed'.format(str(doc_count),
                                                                            str(len(vocabulary)),
                                                                            str(time.time() - t0)))

    doc_count += 1


if vocabulary and reverse_voc:
    ret_voc = redis_con.hmset(con.VOC_NAME, vocabulary)
    ret_rev = redis_con.hmset(con.REVERSE_VOC_NAME, reverse_voc)

    if ret_rev and ret_voc:
        print('Vocabulary created in: {} secs'.format(str(time.time() - t0)))
        print('Searched in {} documents'.format(str(doc_count)))

    # redis write failed - fallback to json file
    else:
        fname = os.path.join(con.TRAINED_MODELS_PATH, con.VOC_NAME)
        with open(fname, 'w') as stream:
            json.dump(vocabulary, stream)

        fname = os.path.join(con.TRAINED_MODELS_PATH, con.REVERSE_VOC_NAME)
        with open(fname, 'w') as stream:
            json.dump(reverse_voc, stream)

else:
    logging.error('Vocabulary creation failed')

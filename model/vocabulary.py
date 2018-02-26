from __future__ import print_function
import time
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

diri = con.ABSTRACTS_PATH
file_names = [os.path.join(diri, fname) for fname in os.listdir(diri) if(fname.endswith('.json'))]


class DocTerms(object):
    def __init__(self, file_names):
        self.file_names = file_names
        # self.stats = defaultdict(int)

    @staticmethod
    def get_document_voc_terms(data):
        """
        Reads metadata such as 'keywords' from the given document
        """
        doc_terms = set()
        try:
            if 'MeshHeadings' in data and data['MeshHeadings']:
                upd = {k['text'].lower() for k in data['MeshHeadings']}
                doc_terms.update(upd)
                # self.stats['mesh'] += len(upd)
            # if 'SupplMeshName' in data and data['SupplMeshName']:
                # self.stats['supl'] += 1
            if 'Chemicals' in data and data['Chemicals']:
                upd = {k['NameOfSubstance'].lower() for k in data['Chemicals']}
                doc_terms.update(upd)
                # self.stats['chem'] += len(upd)
            if 'Keywords' in data and data['Keywords']:
                upd = {k.lower() for k in data['Keywords']}
                doc_terms.update(upd)
                # self.stats['keyw'] += len(upd)
        except KeyError as e:
            # term is not present in current doc
            logging.info(e)

        return doc_terms

    def __iter__(self):
        for file_name in self.file_names:
            try:
                # logging.info(file_name)
                data = json.load(open(file_name, 'r'))
                terms = self.get_document_voc_terms(data)
                yield terms
            except IOError as e:
                logging.info(e)
                continue

t0 = time.time()

# delete existing vocabularies, if any
print(redis_con.delete(con.VOC_NAME))
print(redis_con.delete(con.REVERSE_VOC_NAME))

terms_set = DocTerms(file_names)

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
    if len(vocabulary) % 100000 == 0:
        print('Currently in {} terms, {} secs elapsed'.format(str(len(vocabulary)),
                                                              str(time.time() - t0)))
        # print('Processed: {} mesh, {} supl, {} chemicals, {} keywords'.format(stats['mesh'],
        #                                                                       stats['supl'],
        #                                                                       stats['chem'],
        #                                                                       stats['keyw']))
    doc_count += 1


if vocabulary and reverse_voc:
    ret_voc = redis_con.hmset('vocabulary', vocabulary)
    ret_rev = redis_con.hmset('reverse_voc', reverse_voc)

    if ret_rev and ret_voc:
        print('Vocabulary created in: {} secs'.format(str(time.time() - t0)))
        print('Searched in {} documents'.format(str(doc_count)))

        # print('Processed: {} mesh, {} supl, {} chemicals, {} keywords'.format(stats['mesh'],
        #                                                                       stats['supl'],
        #                                                                       stats['chem'],
        #                                                                       stats['keyw']))
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


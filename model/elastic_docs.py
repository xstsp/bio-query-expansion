from __future__ import print_function

import time

from doc_iters import *
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)


class MySentences(object):

    def __init__(self, iterator):
        self.iter = iterator

    def __iter__(self):
        for doc in self.iter:
            text = doc['AbstractText']
            #text = 'achieved by co-seeding with MSCs. (Hence), MSCs, "can" be appropriate! perivascular cells! for tissue-engineered constructs.'

            # pre-processing, stopwords removal etc
            words = sentence_tokenizer(text)
            # TODO: tokens may contain multiple duplicates. remove dups or train use full set?
            yield words

t0 = time.time()

#it = ElasticDocs()
it = FileSystemDocs()
text = MySentences(it)  # a memory-friendly iterator
abstracts = []
for i, mm in enumerate(text):
    abstracts.append(mm)
    if i % 1000000 == 0 and i != 0:
        try:
            fname = '_'.join([os.path.join(con.TRAINED_MODELS_PATH, 'abstracts_chunk'), str(i)])
            with open(fname, 'w') as stream:
                json.dump(abstracts, stream)
            abstracts = []
            print('json written for batch {}'.format(str(i)))
        except:
            print('json write failed for batch {}'.format(str(i)))

print('Finished in: {} secs'.format(str(time.time() - t0)))






from __future__ import print_function
import time
from doc_iters import *
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class MySentences(object):

    def __init__(self, iterator):
        self.iter = iterator

    def __iter__(self):
        for text in self.iter:

            # pre-processing, stopwords removal etc
            words = sentence_tokenizer(text)
            tokens = replace_text_from_voc(words)
            yield tokens

t0 = time.time()

# it = ElasticDocs()
# it = FileSystemDocs()
it = FileSystemTerms()
sentences = MySentences(it)  # a memory-friendly iterator

# TODO: look into gensim's parameters
model = gensim.models.word2vec.Word2Vec(
    sentences,
    size=100,
    workers=10,
    min_count=5,
    window=5,
    iter=10,
    negative=10
)

print('Model created in: {} secs'.format(str(time.time() - t0)))

fname = os.path.join(con.TRAINED_MODELS_PATH, con.TRAINED_MODEL)
model.save(fname)



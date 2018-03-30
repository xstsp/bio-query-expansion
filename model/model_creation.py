from doc_iters import *
from helpers import *
import time

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

t0 = time.time()

# it = ElasticDocs()
# it = FileSystemDocs()
# it = FileSystemTerms()
# sentences = MySentences(it)

# files = [os.path.join(diri, fname) for fname in os.listdir(diri)]
files = [os.path.join(con.EVALUATION_PATH, fname) for fname in os.listdir(con.EVALUATION_PATH)]
sentences = ListFromFile(files)

model = gensim.models.word2vec.Word2Vec(
    sentences,
    size=200,
    workers=10,
    min_count=10,
    window=5,
    iter=10,
    negative=10
)

logging.info('Model created in: {} secs'.format(str(time.time() - t0)))

fname = os.path.join(con.TRAINED_MODELS_PATH, con.TRAINED_MODEL)
model.save(fname)



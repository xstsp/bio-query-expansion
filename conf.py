import os
import sys
import string
import re
import nltk
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINED_MODELS_PATH = os.path.join(ROOT_DIR, 'trained_models')
TEST_FILES_PATH = os.path.join(ROOT_DIR, 'test_files')
ABSTRACTS_PATH = os.path.join(ROOT_DIR, 'sample_abstract_data')
EVALUATION_PATH = os.path.join(ROOT_DIR, 'evaluation')
TEST_REP = os.path.join(ROOT_DIR, 'test_rep')
# punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
PUNCT = re.compile("|".join([re.escape(i) for i in string.punctuation]))

try:
    STOPWORDS = nltk.corpus.stopwords.words('english')
except LookupError:
    # download required nltk packages
    subprocess.run(["python", "-m", "nltk.downloader", "punkt", "stopwords"])
    STOPWORDS = nltk.corpus.stopwords.words('english')

VOC_NAME = 'vocabulary-6'
REVERSE_VOC_NAME = 'reverse_voc-6'
# VOC_TERMS = {'MeshHeadings': 'text', 'SupplMeshName': '', 'Chemicals': 'NameOfSubstance', 'Keywords': ''}
VOC_PREFIX = 'v_t_'
TRAINED_MODEL = 'test_model'
PROD_MODEL = 'prod_model'
# default embeddings model
BIO_TRAINED_MODEL = 'pruned.word2vec.txt'

REDIS_DB = 2
MONGO_COLL = 'scores'
MONGO_DB = 'queries'

THRESHOLD = 0.8

URL = 'http://127.0.0.1:777/'

# scenarios
EXPANDED = 'exp'
ELK = 'elk'
BIOASQ = 'bio'

SCENARIO = EXPANDED
#SCENARIO = ELK

EXTRA = 'explosion'
#EXTRA = None

MAX_ID = 27957702

sys.path.extend([ROOT_DIR])


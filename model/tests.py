import json
import os
import unittest

from gensim.models import word2vec

import model
from helpers import *


class TestModel(unittest.TestCase):
    def setUp(self):
        self.json_path = con.TEST_FILES_PATH
        self.abs_path = con.ABSTRACTS_PATH
        self.vocabulary = get_vocabulary(con.VOC_NAME)
        self.test_query = "What is the Quiescent Phenotype ECs?"
        self.test_response = {"docs": ["quiescent",
                                   "phenotype",
                                   "ecs",
                                   "mscs",
                                   "poly",
                                   "bone",
                                   "endothelial cells",
                                   "mesenchymal stem cells",
                                   "constructs",
                                   "scaffolds",
                                   "vascular",
                                   "perivascular",
                                   "osteogenic"]}

    def test_get_gold_data_from_file(self):
        data = model.Dataset.read_from_bioasq_json(os.path.join(self.json_path, 'BioASQ-SampleDataB.json'))
        self.assertEqual(len(data), 14)

    def test_get_gold_data_from_dir(self):
        l = model.Dataset.get_bioasq_questions(self.json_path, )
        self.assertEqual(len(l['questions']), 114)

    def test_find_word_in_voc(self):
        word = 'platelet-derived growth factor'
        mapped = self.vocabulary[word]
        self.assertEqual(mapped, 'v_t_24')

    def test_find_term_in_abstract(self):
        # open abstracts
        # search for term
        diri = con.ABSTRACTS_PATH
        file_names = [os.path.join(diri, fname) for fname in os.listdir(diri) if (fname.endswith('.json'))]

        # term = 'platelet-derived growth factor'
        term = 'quiescent phenotype'
        f = False
        for file_name in file_names:
            print(file_name)
            dato = json.load(open(file_name, 'r'))
            text = dato['AbstractText'].lower()
            if text.find(term) == -1:
                continue
            f = True
            break
        self.assertEqual(f, True)

    def test_get_abstracts(self):
        diri = con.ABSTRACTS_PATH
        file_names = [os.path.join(diri, fname) for fname in os.listdir(diri) if (fname.endswith('.json'))]
        ab = []
        for file_name in file_names:
            print(file_name)
            dato = json.load(open(file_name, 'r'))
            ab.append(dato['AbstractText'])
        with open('abstracts', 'w') as wrt:
            json.dump(ab, wrt)

    def test_load_model(self):
        model = word2vec.Word2Vec.load(os.path.join(con.TRAINED_MODELS_PATH, con.MODEL_NAME))
        print(model.wv.vocab.keys())

    def test_load_trained_model(self):
        model = get_trained_model('bio')
        sim = model.most_similar('king')
        self.assertEqual(sim, '[]')

    def test_query_cleansing(self):
        query = "What is the Quiescent Phenotype implants [3]? (based on the actula )"
        test = ['quiescent', 'phenotype', 'implants', '3', 'based', 'actula']
        ret = sentence_tokenizer(query)
        self.assertEqual(test, ret)

    def test_query(self):
        doc, meta = query_search(self.test_query, con.EXPANDED)
        self.assertEqual(doc, self.test_response)

    def test_query_http(self):
        ret = search_bioxq(self.test_query, con.EXPANDED)
        self.assertEqual(ret.status_code, 200)

if __name__ == "__main__":
    unittest.main()


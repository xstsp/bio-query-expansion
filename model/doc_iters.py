from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import os
import conf as con
import json


class ElasticDocs:
    """
    Implements iterator which returns documents from elasticsearch cluster
    """
    def __init__(self):
        es = Elasticsearch(['127.0.0.1'],     # elastic servers
                           verify_certs=True,
                           timeout=150,
                           max_retries=10,
                           retry_on_timeout=True
                           )
        index = 'pubmed_abstracts_0_1'
        # doc_type = 'abstract_0_1'

        self.scroll = scan(
                client=es,
                index=index,
                query=None,
                scroll=u'5m',
                raise_on_error=True,
                preserve_order=False, size=1000,
                request_timeout=45,
                clear_scroll=True
        )

    def __iter__(self):
        for doc in self.scroll:
            yield doc['_source']


class FileSystemDocs:
    """
    Implements iterator which returns documents from local filesystem
    """
    def __init__(self):
        diri = con.ABSTRACTS_PATH
        self.file_names = [os.path.join(diri, fname) for fname in os.listdir(diri) if (fname.endswith('.json'))]

    def __iter__(self):
        for doc in self.file_names:
            data = json.load(open(doc, 'r'))
            yield data


class FileSystemTerms:
    """
    Implements iterator which returns sentences from local filesystem
    """
    def __init__(self):
        self.file_names = ['/home/user/thesis/abstracts/abstracts_chunk_1000000']

    def __iter__(self):
        for doc in self.file_names:
            for i, tex in enumerate(json.load(open(doc, 'r'))):
                yield tex


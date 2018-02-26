from elasticsearch import Elasticsearch


class SearchElastic:
    def __init__(self, phrases):
        self.es = Elasticsearch([
                '127.0.0.1'
            ],
            verify_certs=True,
            timeout=30,
            max_retries=10,
            retry_on_timeout=False
        )

        self.index = 'pubmed_abstracts_0_1'
        self.doc_type = 'abstract_0_1'
        self.phrases = phrases

    # matches the ngrams of the phrases
    def create_body(self):
        the_shoulds = []
        for phr in self.phrases:
            the_shoulds.append(
                {
                    "match": {
                        "AbstractText": {
                            "query": phr
                        }
                    }
                }

            )
        bod = {
            "from": 0,
            "size": 50,
            "query": {
                "bool": {
                    "should": the_shoulds,
                    "minimum_should_match": 1
                }
            }
        }
        return bod

    def run_search(self):
        res = self.es.search(index=self.index,
                             doc_type=self.doc_type,
                             body=self.create_body())
        return res


if __name__ == "__main__":
    phrases = [
        'investigate whether hospital readmission',
        'all rights reserved',
        'assessment of the proximal rectus femoris tendons',
    ]

    es = SearchElastic(phrases)
    es_res = es.run_search()

    for i in range(10):
        try:
            print(es_res[u'hits'][u'hits'][i]['_source']['AbstractTitle'])
            print(es_res[u'hits'][u'hits'][i]['_source']['pmid'])
            print(es_res[u'hits'][u'hits'][i]['_score'])
        except:
            break




















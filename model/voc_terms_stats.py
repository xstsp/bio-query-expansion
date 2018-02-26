import heapq
import time
from collections import defaultdict

from helpers import *


def get_nlargest_voc_terms():
    t0 = time.time()
    voc = Vocabulary('vocabulary-6', redis_con)

    res = heapq.nlargest(1000, voc, key=lambda x: len(x[0].split()))
    print([(len(i[0].split()), i[1]) for i in res])

    print('Finished in: {} secs'.format(str(time.time() - t0)))


def get_nsmallest_voc_terms():
    t0 = time.time()
    voc = Vocabulary('vocabulary-6', redis_con)

    res = heapq.nsmallest(100, voc, key=lambda x: len(x[0].split()))
    print([(len(i[0].split()), i[1]) for i in res])

    print('Finished in: {} secs'.format(str(time.time() - t0)))


def get_total_number_of_voc_ngrams():
    t0 = time.time()
    voc = Vocabulary('vocabulary-6', redis_con)
    occs = defaultdict(int)
    for i, (key, v) in enumerate(voc):
        occs[len(key.split())] += 1

    print('Terms: {}'.format(str(i)))
    for k, val in occs.items():
        print('{} {}-grams'.format(str(val), str(k)))

    print('Finished in: {} secs'.format(str(time.time() - t0)))


def get_scan_total_number_of_voc_ngrams():
    t0 = time.time()
    voc = Vocabulary('vocabulary-6', redis_con)
    occs = defaultdict(int)
    for (k, v) in voc.get():
        occs[len(k.split())] += 1

    for k, val in occs.items():
        print('{} {}-grams'.format(str(val), str(k)))

    print('Finished in: {} secs'.format(str(time.time() - t0)))


if __name__ == "__main__":
    get_nsmallest_voc_terms()
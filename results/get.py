from helpers import *
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix


def calculate_scores(docs, gold):
    precision = get_precision(docs, gold)
    recall = get_recall(docs, gold)
    fscore = get_fscore(docs, gold)
    return fscore, recall, precision


def get_precision(docs, gold):
    return precision_score(docs, gold)


def get_recall(docs, gold):
    return recall_score(docs, gold)


def get_fscore(docs, gold):
    return f1_score(docs, gold)


for doc in mongo_scores.find({}):
    docs = doc['docs']
    gold = doc['groundtruth']

    # fscore, recall, precision = calculate_scores(sorted(docs), sorted(gold))

    dset = {s for s in docs}
    gset = {s for s in gold}

    newd = []

    # print(sorted(docs), sorted(gold))

    for g in gset:
        found = True if g in dset else False
        newd.append(found)

    print(newd)


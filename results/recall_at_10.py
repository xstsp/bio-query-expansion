import json
import os
import conf as con
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix


def get_recall(response, gold):
    tp = 0
    fp = 0
    fn = 0

    for i in response:
        if i in gold:
            tp += 1
        else:
            fp += 1

    for i in gold:
        if i not in response:
            fn += 1

    if (fn + tp) != 0:
        o = tp / (tp + fn)
        return o

scenario = con.SCENARIO
if scenario == con.EXPANDED and con.EXTRA:
    scenario = 'xpl'
total = os.listdir(os.path.join(con.EVALUATION_PATH, scenario))
print('scenario: {}'.format(scenario))

total_recall = 0

i = 0
size = 10
trim = 0
asis = 0
empty = 0
_sys = os.path.join(con.EVALUATION_PATH, '100-08', '_'.join(['system_rem', str(1)])) + '.json'
_gold = os.path.join(con.EVALUATION_PATH, '100-08', '_'.join(['gold', str(1)])) + '.json'
print('file: {}'.format(_sys))
print('file: {}'.format(_gold))


with open(_sys, 'r') as sys:
    resp = json.load(sys)
with open(_gold, 'r') as gol:
    gold = json.load(gol)

for quests, i in enumerate(gold['questions']):
    for j in resp['questions']:
        if j['documents'] == []:
            # print('empty: {}'.format(j['id']))
            empty += 1
            continue
        if i['id'] == j['id']:
            gdocs = i['documents']
            rdocs = j['documents']

            if len(gdocs) > size:
                t = get_recall(rdocs[:size], gdocs[:size])
                trim += 1
            else:
                t = get_recall(rdocs[:10], gdocs)
                asis += 1
            if t: total_recall += t

print('Recall at {}: {}'.format(quests, total_recall))
print('Trimmed: {}'.format(trim))
print('As is: {}'.format(asis))
print('empty: {}'.format(empty))

# print('exited: {}'.format(exit_code))
print("avg recall: {} ".format(total_recall / (quests+1)))

# TODO: Take the size of gold list into account when calculating scores (es will return predefined number of files)
# -> maybe set a threshold to es _score

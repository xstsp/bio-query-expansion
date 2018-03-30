import time
import copy
import conf as con
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Questions:
    def __init__(self):
        self.scenario = con.SCENARIO
        if self.scenario == con.EXPANDED and con.EXTRA:
            self.scenario = 'xpl'
        self.path = os.path.join(con.EVALUATION_PATH, self.scenario, '_'.join(['system', str(0)])) + '.json'
        print("file: {}".format(self.path))

    def __iter__(self):
        with open(self.path, 'r') as from_file:
            data = json.load(from_file)
        for i in data['questions']:
            yield i

t0 = time.time()

# path = os.path.join(con.TEST_FILES_PATH, 'test.json')
dataset = Questions()

print('scenario: {}'.format(con.SCENARIO))
system_json = {'questions': []}
num = 0
max_id = 0
count = 0
removed = 0
rem_q = 0
dup_q = 0
dup_docs = 0
for question in dataset:
    docs = question['documents']
    orig_len = len(docs)
    clean_len = len(docs)
    if not question['documents']:
        print('Empty list found: {}'.format(question['id']))
        clean = []
    else:
        try:
            # remove bigger than maxid
            clean = [q for q in docs if int(q) <= con.MAX_ID]
            # removed some docs
            if clean < docs:
                removed += len(docs) - len(clean)
                rem_q += 1
                # print('YES {} {}'.format(removed, rem_q))
                clean_len = len(clean)

            # remove duplicates
            for v in clean:
                [clean.pop(x) for x in sorted([i for i, x in enumerate(clean) if x == v][1:], reverse=True)]

            if clean_len > len(clean):
                dup_q += 1
                dup_docs += clean_len - len(clean)
                # print('TRUE {} {}'.format(dup_docs, dup_q))

        except ValueError as e:
            print(e)
        except:
            print('EXCEPT')

    question['documents'] = clean
    count += 1
    system_json['questions'].append(question)

print('processed {} questions'.format(count))
print('bigger than maxID: {}'.format(removed))
print('reduced questions: {}'.format(rem_q))
print('duplicates found in: {}'.format(dup_q))
print('total duplicates: {}'.format(dup_docs))

print('Finished in: {} secs'.format(str(time.time() - t0)))


if con.SCENARIO == con.EXPANDED and con.EXTRA:
    wfolder = 'xpl'
else:
    wfolder = con.SCENARIO
write_to = os.path.join(con.EVALUATION_PATH, wfolder, '_'.join(['system', 'rem', str(0)]))
with open(write_to + '.json', 'w') as w:
    json.dump(system_json, w)

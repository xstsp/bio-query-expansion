import time

import conf as con
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Questions:
    def __init__(self, file_name):
        self.path = os.path.join(con.TEST_FILES_PATH, file_name)
        self.scenario = con.SCENARIO
        if self.scenario == con.EXPANDED and con.EXTRA:
            self.scenario = 'xpl'
        print("file: {}".format(self.path))

    @staticmethod
    def read_question_from_json(question):
        d = dict()
        d['body'] = question['body']
        # optionally, drop the url and just keep the docid
        d['documents'] = [doc.split('/')[-1] for doc in question['documents']]
        d['id'] = question['id']
        return d

    def __iter__(self):
        with open(self.path, 'r') as from_file:
            data = json.load(from_file)
        for i in data['questions']:
            yield self.read_question_from_json(i)


t0 = time.time()

# path = os.path.join(con.TEST_FILES_PATH, 'test.json')
quest_list = Questions('test.json')

scenario = con.SCENARIO
scores = dict()

# create one dict for gold and one for system. save both files to contain the same IDs
logging.info('scenario: {}'.format(scenario))
system_json = {'questions': []}
golden_json = {'questions': []}
num = 0
logging.info('File {}'.format(file_count))
for q in quest_list:
    num += 1
    logging.info('Question {}: {}'.format(num, q['body']))
    sys_res = query_search(q['body'], scenario)
    sys_res['id'] = q['id']
    system_json['questions'].append(sys_res)
    golden_json['questions'].append({'id': q['id'], "documents": q['documents']})

if scenario == con.EXPANDED and con.EXTRA:
    wfolder = 'xpl'
else:
    wfolder = scenario
write_to = os.path.join(con.EVALUATION_PATH, wfolder, '_'.join(['system', str(0)]))
with open(write_to + '.json', 'w') as w:
    json.dump(system_json, w)
write_to = os.path.join(con.EVALUATION_PATH, wfolder, '_'.join(['gold', str(0)]))
with open(write_to + '.json', 'w') as w:
    json.dump(golden_json, w)

logging.info('Finished in: {} secs'.format(str(time.time() - t0)))

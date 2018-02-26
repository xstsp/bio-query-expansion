import time

import conf as con
from helpers import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Questions:
    def __init__(self, file_path, read_from_dir=False):
        self.path = file_path
        # if True read all files from dir, else only given file
        self.read_from_dir = read_from_dir

    @staticmethod
    def read_from_bioasq_json(file_path):
        clean = []
        with open(file_path, 'r') as j:
            data = json.load(j)
        for q in data['questions']:
            d = dict()
            d['body'] = q['body']
            # optionally, drop the url and just keep the docid
            d['gold'] = [doc.split('/')[-1] for doc in q['documents']]
            d['id'] = q['id']
            clean.append(d)
        return clean

    def get_bioasq_questions(self):
        jpath = self.path
        gold = []
        # read all files from directory
        if self.read_from_dir:
            for fil in [os.path.join(jpath, f) for f in os.listdir(jpath)]:
                data = self.read_from_bioasq_json(fil)
                gold.extend(data)
        # read single file
        else:
            data = self.read_from_bioasq_json(jpath)
            gold.extend(data)
        full = dict()
        full['questions'] = gold
        yield full

    def __iter__(self):
        jpath = self.path
        # read all files from directory
        for fil in [os.path.join(jpath, f) for f in os.listdir(jpath)]:
            data = self.read_from_bioasq_json(fil)
            yield data


t0 = time.time()

# path = os.path.join(con.TEST_FILES_PATH, 'test.json')
dataset = Questions(con.TEST_FILES_PATH, read_from_dir=True)

scenario = con.SCENARIO
scores = dict()

# create one dict for gold and one for system. save both files to contain the same IDs
logging.info('scenario: {}'.format(scenario))
for file_count, quest_list in enumerate(dataset):
    system_json = {'questions': []}
    golden_json = {'questions': []}
    logging.info('File {}'.format(file_count))
    for num, q in enumerate(quest_list):
        logging.info('Question {}: {}'.format(num, q['body']))
        sys_res = query_search(q['body'], scenario)

        # mongo_scores.update_one({"q_id": data['q_id']}, {"$set": {"groundtruth": q['groundtruth']}})
        # logging.info('saved: ' + data['q_id'])

        sys_res['body'] = q['body']
        sys_res['id'] = q['id']
        system_json['questions'].append(sys_res)
        golden_json['questions'].append({'id': q['id'], "documents": q['gold'], "body": q['body']})

    wfolder = 'xpl' if scenario == con.EXPANDED and con.EXTRA else scenario

    write_to = os.path.join(con.EVALUATION_PATH, wfolder, '_'.join(['system', str(file_count)]))
    with open(write_to + '.json', 'w') as w:
        json.dump(system_json, w)
    write_to = os.path.join(con.EVALUATION_PATH, wfolder, '_'.join(['golden', str(file_count)]))
    with open(write_to + '.json', 'w') as w:
        json.dump(golden_json, w)

logging.info('Finished in: {} secs'.format(str(time.time() - t0)))

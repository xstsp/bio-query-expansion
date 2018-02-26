import time

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
            d['qterms'] = len(q['body'].split())
            d['qgold'] = len(q['documents'])
            d['body'] = q['body']
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
        yield gold

    def __iter__(self):
        jpath = self.path
        # read all files from directory
        for fil in [os.path.join(jpath, f) for f in os.listdir(jpath)]:
            data = self.read_from_bioasq_json(fil)
            yield data


t0 = time.time()

# path = os.path.join(con.TEST_FILES_PATH, 'test.json')
dataset = Questions(con.TEST_FILES_PATH, read_from_dir=True)


total_questions = 0
total_gold = 0
total_qterms = 0
max_qterms = 0
max_gold = 0
for file_count, quest_list in enumerate(dataset, start=1):
    # print('File {}'.format(file_count))
    for num, q in enumerate(quest_list, start=1):
        total_gold += q['qgold']
        total_qterms += q['qterms']
        if q['qgold'] > max_gold:
            max_gold = q['qgold']
            max_gbody = q['body']
        if q['qterms'] > max_qterms:
            max_qterms = q['qterms']
            max_body = q['body']
    logging.info('questions for file {}: {}'.format(file_count, num))
    total_questions += num

logging.info('total_questions: {}'.format(total_questions))
logging.info('total_gold: {}'.format(total_gold))
logging.info('avg_gold: {}'.format(total_gold/total_questions))
logging.info('max_gold: {}'.format(max_gold))
logging.info('max_gold_body: {}'.format(max_gbody))
logging.info('total_qterms: {}'.format(total_qterms))
logging.info('avg_qterms: {}'.format(total_qterms/total_questions))
logging.info('max_qterms: {}'.format(max_qterms))
logging.info('max_terms_body: {}'.format(max_body))
print('Finished in: {} secs'.format(str(time.time() - t0)))

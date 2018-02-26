import os
import conf as con
from subprocess import PIPE, Popen


def run_command(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderror = p.communicate()
    ret_code = p.returncode
    if ret_code != 0:
        return stderror, ret_code
    else:
        return stdout, ret_code

scenario = con.SCENARIO
if scenario == con.EXPANDED and con.EXTRA:
    scenario = 'xpl'
total = os.listdir(os.path.join(con.EVALUATION_PATH, scenario))
print('scenario: {}'.format(scenario))

total_precision = 0
total_recall = 0
total_f1 = 0
total_map = 0
total_gmap = 0
for i in range(len(total) // 2):
    _sys = os.path.join(con.EVALUATION_PATH, scenario, '_'.join(['system', str(i)])) + '.json'
    _gold = os.path.join(con.EVALUATION_PATH, scenario, '_'.join(['golden', str(i)])) + '.json'
    print('file: {}'.format(_sys))
    # print('file: {}'.format(_gold))

    # evaluation tool from https://github.com/BioASQ/Evaluation-Measures
    cmd = ['java', '-Xmx10G', '-cp', '$CLASSPATH:../bioasq-eval/Evaluation-Measures/flat/BioASQEvaluation/dist/BioASQEvaluation.jar', 'evaluation.EvaluatorTask1b', '-phaseA', '-e', '3', _gold, _sys]

    output, exit_code = run_command(cmd)
    print('Precision, Recall, F1, MAP, GMAP')
    # hack to keep only documents scoring
    output = output.decode('utf-8').split()[5:10]
    total_precision += float(output[0])
    total_recall += float(output[1])
    total_f1 += float(output[2])
    total_map += float(output[3])
    total_gmap += float(output[4])
    print(output)

print("total: {} {} {} {} {}".format(total_precision,
                                 total_recall,
                                 total_f1,
                                 total_map,
                                 total_gmap))

print("avg: {} {} {} {} {}".format(total_precision / (i+1),
                                 total_recall / (i+1),
                                 total_f1 / (i+1),
                                 total_map / (i+1),
                                 total_gmap / (i+1)))

# TODO: Take the size of gold list into account when calculating scores (es will return predefined number of files)

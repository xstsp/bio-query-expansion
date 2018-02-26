import time
import nltk
import random
import redis
import re
import conf as con

t0 = time.time()
text = '''Pulmonary arterial hypertension (PAH) is a rare disease with prevalence estimated between 15 and 50 cases per million people1. PAH prevalence is two-to-four times higher in women than in men2,3, and the disease can affect people of any age, even children. The early symptoms of PAH include mild dyspnea, fatigue, and dizziness, which can also be associated with various other diseases. Further, accurate diagnosis of PAH requires an invasive right-heart catheterization2. As a result, PAH diagnosis is often delayed and, by the time patients are diagnosed with PAH, the disease is progressed to the occurrence of pulmonary vascular remodeling and right ventricle (RV) remodeling3.

In PAH, elevated pulmonary vascular resistance causes stress to the RV, and RV failure is the major cause of death in patients with PAH4. The narrowing and occlusion of pulmonary vessels, as well as the elevation of pulmonary vascular resistance are due to multiple factors, including vasoconstriction and the thickening of pulmonary vascular walls. Currently approved drugs for PAH treatment primarily cause vasodilation, but these have limited influence on the structural changes in the vessel walls.

Increased pulmonary vascular wall thickness and the narrowing and, in some cases occlusion, of the pulmonary arterial lumens are due to the growth of pulmonary arterial cells such as smooth muscle cells, endothelial cells, and fibroblasts, which form various lesions including medial hypertrophy; eccentric intimal proliferation; concentric, non-laminar intimal thickening; concentric, laminar intimal thickening; fibrinoid necrosis; occlusive intimal proliferation; and plexiform legions. Figure 1 exhibits some pulmonary vascular lesions in PAH with narrow or occluded blood vessel lumens that would significantly limit blood flow. Thus, therapeutic strategies to inhibit cell-growth signaling should prevent the formation and delay the progression of pulmonary vascular remodeling.

One report suggested that screening for JCV in the CSF of natalizumab-treated patients might be able to identify patients with an increased risk of developing PML and that discontinuing treatment in these patients might prevent clinical illness.34

On January 20, 2012, the FDA approved a product label change for natalizumab to identify anti-JCV antibody status as a risk factor for PML. The parallel approval of the Stratify JCV test will enable neurologists to determine the JC virus infection status of patients to aid in treatment decisions. The assay will be offered through Quest’s Focus Diagnostics laboratory in the U.S.'''
lis = [x for x in text.split()]

voc = redis.StrictRedis(host='localhost', port=6379, db=2, charset="utf-8", decode_responses=True)
print(voc.delete('vocabulary'))
print(voc.delete('reverse_voc'))

'''for _ in range(50):
    rand = random.randrange(1, 40, 1)
    #print(rand)
    yo = nltk.ngrams(text, rand)
    for i in yo:
        rv = voc.hsetnx('redtest', i, str(rand))


print('hsetnx: Vocabulary created in: {} secs'.format(str(time.time() - t0)))
'''
t0 = time.time()
vocabulary = {}
reverse_voc = {}
#random.seed(123456)
for i in range(10000):
    rand = random.randrange(1, 40, 1)
    yo = nltk.ngrams(lis, rand)
    for term in yo:
        try:
            # if term exists
            val = vocabulary[term]
        except KeyError:
            val = con.VOC_PREFIX + str(len(vocabulary))
            vocabulary[term] = val
            reverse_voc[val] = term

t0 = time.time()
voc.hmset('vocabulary', vocabulary)
voc.hmset('reverse_voc', reverse_voc)
# vocabulary = {}
# reverse_voc = {}

print('hmset: Vocabulary created in: {} secs'.format(str(time.time() - t0)))

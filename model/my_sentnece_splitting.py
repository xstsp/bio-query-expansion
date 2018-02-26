#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Dimitris'

import re
from pprint import pprint
from nltk.tokenize import sent_tokenize


def first_alpha_is_upper(sent):
    specials = [
        '__EU__','__SU__','__EMS__','__SMS__','__SI__',
        '__ESB','__SSB__','__EB__','__SB__','__EI__',
        '__EA__','__SA__','__SQ__','__EQ__','__EXTLINK',
        '__XREF','__URI', '__EMAIL','__ARRAY','__TABLE',
        '__FIG','__AWID','__FUNDS'
    ]
    for special in specials:
        sent = sent.replace(special,'')
    for c in sent:
        if c.isalpha():
            if c.isupper():
                return True
            else:
                return False
    return False


def ends_with_special(sent):
    sent = sent.lower()
    ind = [item.end() for item in re.finditer('[\W\s]sp.|[\W\s]nos.|[\W\s]figs.|[\W\s]sp.[\W\s]no.|[\W\s][vols.|[\W\s]cv.|[\W\s]fig.|[\W\s]e.g.|[\W\s]et[\W\s]al.|[\W\s]i.e.|[\W\s]p.p.m.|[\W\s]cf.|[\W\s]n.a.', sent)]
    if len(ind)==0:
        return False
    else:
        ind = max(ind)
        if len(sent) == ind:
            return True
        else:
            return False


def split_sentences2(text):
    sents = [l.strip() for l in sent_tokenize(text)]
    ret = []
    i = 0
    while i < len(sents):
        sent = sents[i]
        while (
            ((i + 1) < len(sents)) and
            (
                ends_with_special(sent)        or
                not first_alpha_is_upper(sents[i+1])
                # sent[-5:].count('.') > 1       or
                # sents[i+1][:10].count('.')>1   or
                # len(sent.split()) < 2          or
                # len(sents[i+1].split()) < 2
            )
        ):
            sent += ' ' + sents[i + 1]
            i += 1
        ret.append(sent.replace('\n', ' ').strip())
        i += 1
    return ret


def get_sents(ntext):
    sents = []
    for subtext in ntext.split('\n'):
        subtext = re.sub('\s+', ' ', subtext.replace('\n', ' ')).strip()
        if len(subtext) > 0:
            ss = split_sentences2(subtext)
            sents.extend([s for s in ss if(len(s.strip()) > 0)])
    if len(sents[-1]) == 0:
        sents = sents[:-1]
    return sents

example_text = u'''
Pulmonary arterial hypertension (PAH) is a rare disease with prevalence estimated between 15 and 50 cases per million people1. PAH prevalence is two-to-four times higher in women than in men2,3, and the disease can affect people of any age, even children. The early symptoms of PAH include mild dyspnea, fatigue, and dizziness, which can also be associated with various other diseases. Further, accurate diagnosis of PAH requires an invasive right-heart catheterization2. As a result, PAH diagnosis is often delayed and, by the time patients are diagnosed with PAH, the disease is progressed to the occurrence of pulmonary vascular remodeling and right ventricle (RV) remodeling3.

In PAH, elevated pulmonary vascular resistance causes stress to the RV, and RV failure is the major cause of death in patients with PAH4. The narrowing and occlusion of pulmonary vessels, as well as the elevation of pulmonary vascular resistance are due to multiple factors, including vasoconstriction and the thickening of pulmonary vascular walls. Currently approved drugs for PAH treatment primarily cause vasodilation, but these have limited influence on the structural changes in the vessel walls.

Increased pulmonary vascular wall thickness and the narrowing and, in some cases occlusion, of the pulmonary arterial lumens are due to the growth of pulmonary arterial cells such as smooth muscle cells, endothelial cells, and fibroblasts, which form various lesions including medial hypertrophy; eccentric intimal proliferation; concentric, non-laminar intimal thickening; concentric, laminar intimal thickening; fibrinoid necrosis; occlusive intimal proliferation; and plexiform legions. Figure 1 exhibits some pulmonary vascular lesions in PAH with narrow or occluded blood vessel lumens that would significantly limit blood flow. Thus, therapeutic strategies to inhibit cell-growth signaling should prevent the formation and delay the progression of pulmonary vascular remodeling.

One report suggested that screening for JCV in the CSF of natalizumab-treated patients might be able to identify patients with an increased risk of developing PML and that discontinuing treatment in these patients might prevent clinical illness.34

On January 20, 2012, the FDA approved a product label change for natalizumab to identify anti-JCV antibody status as a risk factor for PML. The parallel approval of the Stratify JCV test will enable neurologists to determine the JC virus infection status of patients to aid in treatment decisions. The assay will be offered through Quest’s Focus Diagnostics laboratory in the U.S.
'''

pprint(get_sents(example_text))

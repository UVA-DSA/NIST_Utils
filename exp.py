'''
The main file for creation and execution of behavior trees
'''

import py_trees
import behaviours as be
from py_trees.blackboard import Blackboard
import pandas as pd
from scipy import spatial
from sklearn.cluster import KMeans
import numpy as np
from pandas import DataFrame
from annotator import annotator
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
import text_clf_utils as utils
import pickle
import textwrap
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from ranking_func import rank
from tqdm import tqdm as tqdm

'''
To map from RAA data to standard format. 
Dictionaries of values for interventions and symptoms. 
'''
# param
intermapping= {
    '12-lead ecg':['cardiac monitor'],
    'albuterol':['albuterol'],
    'aspirin':['aspirin'],
    'assist ventilation (bvm)':['bag valve mask ventilation'],
    'capnography (1) first reading':['capnography'],
    'capnography (2) seco':['capnography'],
    'capnography (2) second reading':['capnography'],
    'capnography (3) final reading':['capnography'],
    'cardiac monitor':['cardiac monitor'],
    'nasopharyngeal airway insertio':['nasopharyngeal airway'],
    'cpap':['cpap'],
    'dexamethasone (decadron)':['dexamethasone'],
    'dextrose 10%':['dextrose'],
    'dextrose 25%':['dextrose'],
    'dextrose 50%':['dextrose'],
    'dextrose 5% in 0.45% ns':['dextrose'],
    'duoneb':['albuterol','ipratropium'],
    'fentanyl':['fentanyl'],
    'glucagon':['glucagon'],
    'glutose':['oral glucose'],
    'hospital':['transport'],
    'hospital contact':['transport'],
    'intubation':['endotracheal tube'],
    'ipratropium (atrovent)':['ipratropium'],
    'iv':['normal saline'],
    'magnesium sulfate':['morphine sulfate'],
    'midazolam (versed)':['midazolam'],
    'naloxone (narcan)':['narcan'],
    'nitroglycerine':['nitroglycerine'],
    'normal saline':['normal saline'],
    'ondansetron (zofran)':['ondansetron'],
    'oral glucose':['oral glucose'],
    'oxygen':['oxygen'],
    'restraints':['physical restraint'],
    'suction':['suction the oropharynx','suction the nasopharynx'],
}

EKGdic = {
     '':'',
     'AV_Block_1st_Deg':'AV_Block-1st_Degree',
     'AV_Block_1st_Degree':'AV_Block-1st_Degree',
     'AV_Block_2nd_Degree_Type_1':'AV_Block_2nd_Degree_Type_1',
     'AV_Block_2nd_Degree_Type_2':'AV_Block_2nd_Degree_Type_2',
     'AV_Block_3rd_Degree':'AV_Block_3rd_Degree',
     'Asystole':'Asystole',
     'Artifact':'Artifact',
     'Atrial_Fibrill':'Atrial_Fibrillation',
     'Atrial_Fibrillation':'Atrial_Fibrillation',
     'Atrial_Flutter':'Atrial_Flutter',
     'Juncti':'Junctional_Rhythm',
     'Junctiona':'Junctional_Rhythm',
     'Junctional':'Junctional_Rhythm',
     'Other_(Not_Listed)':'Other_(Not_Listed)',
     'P': 'Paced_Rhythm',
     'PEA':'Pulseless_Electrical_Activity',
     'Pac':'Paced_Rhythm',
     'Paced_Rhythm':'Paced_Rhythm',
     'Premature_Ventricular_Contractions':'Premature_Ventricular_Contractions',
     'Right_Bundle_Branch_Block':'Right_Bundle_Branch_Block',
     'Left_Bundle_Branch_Block':'Left_Bundle_Branch_Block',
     'STEMI_Anterior_Ischemia':'STEMI_Anterior_Ischemia',
     'STEMI_Lateral_Ischemia':'STEMI_Lateral_Ischemia',
     'STEMI_Inferior_Ischemia':'STEMI_Inferior_Ischemia',
     'S':'Sinus_Rhythm',
     'Si':'Sinus_Rhythm',
     'Sin':'Sinus_Rhythm',
     'Sinu':'Sinus_Rhythm',
     'Sinus':'Sinus_Rhythm',
     'Sinus_':'Sinus_Rhythm',
     'Sinus_Arrhythmia':'Sinus_Arrhythmia',
     'Sinus_Bradycardia':'Sinus_Bradycardia',
     'Sinus_R':'Sinus_Rhythm',
     'Sinus_Rh':'Sinus_Rhythm',
     'Sinus_Rhy':'Sinus_Rhythm',
     'Sinus_Rhyth':'Sinus_Rhythm',
     'Sinus_Rhythm':'Sinus_Rhythm',
     'Sinus_Rhythm,Sinus_Tachycardia':'Sinus_Rhythm,Sinus_Tachycardia',
     'Sinus_T':'Sinus_Tachycardia',
     'Sinus_Tach':'Sinus_Tachycardia',
     'Sinus_Tachyc':'Sinus_Tachycardia',
     'Sinus_Tachycardi':'Sinus_Tachycardia',
     'Sinus_Tachycardia':'Sinus_Tachycardia',
     'Supravent':'Supraventricular_Tachycardia',
     'Supraventricular_Tachycardia':'Supraventricular_Tachycardia',
     'Ventricular_Fibrillation':'Ventricular_Fibrillation',
     'Ventricular_Tachycardia_(With_Pulse)':'Ventricular_Tachycardia',
     'Non_STEMI_Lateral_Ischemia':'Non_STEMI_Lateral_Ischemia'
}

pool = set(['Medical - Abdominal Pain',
            'Medical - Altered Mental Status',
            'Medical - Seizure',
            'Medical - Respiratory Distress/Asthma/COPD/Croup/Reactive Airway',
            'General - Behavioral/Patient Restraint',
            'Medical - Overdose/Poisoning - Opioid',
            'Medical - Diabetic - Hypoglycemia',
            'Medical - Chest Pain - Cardiac Suspected'])
            
FN2H = {
 '': 1,
 'aspirin': 2,
 'albuterol': 2,
 'bag valve mask ventilation': 4,
 'capnography': 2,
 'cardiac monitor': 2,
 'cpap': 4,
 'dexamethasone': 2,
 'dextrose': 4,
 'endotracheal tube':4,
 'fentanyl': 1,
 'glucagon': 3,
 'ipratropium': 2,
 'midazolam': 4,
 'morphine sulfate': 1,
 'narcan': 4,
 'nasopharyngeal airway': 4,
 'nitroglycerine': 3,
 'normal saline': 1,
 'ondansetron': 1,
 'oral glucose': 2,
 'oxygen': 3,
 'physical restraint': 3,
 'transport': 1,
 'suction the oropharynx': 3,
 'suction the nasopharynx': 3
}

FP2H = {
 '': 1,
 'aspirin': 2,
 'bag valve mask ventilation': 2,
 'cardiac monitor': 1,
 'cpap': 3,
 'dexamethasone': 2,
 'dextrose': 2,
 'midazolam': 4,
 'narcan': 2,
 'nitroglycerin': 2,
 'normal saline': 2,
 'ondansetron': 1,
 'oral glucose': 2,
 'oxygen': 1,
 'physical restraint': 2,
 'transport': 1,
 'fentanyl': 4,
 'endotracheal tube': 4
}
            
# start
# read labeled cases
docu = '/Users/sileshu/Desktop/EMSdata/RAA_1000_test.xlsx'
df = pd.read_excel(docu)
su = 0
protocol = {}
narratives = df['Narrative']
vitals = df['Vitals']
inters = df['Interventions']
gt = []
pts = set()
for item in df['HAYDON LABEL']:
    if not pd.isnull(item):
        gt.append(item)
        pts.add(item)
        
interventions = []
for item in inters:
    inter = item.strip('{}').split('}{')
    inter = [i.split(':')[-1].strip().lower() for i in inter]
    c_int = []
    for j in inter:
        if j in intermapping:
            c_int += intermapping[j]
    interventions.append(c_int)
    
chunked_narratives = [textwrap.wrap(narrative, len(narrative) / 10) for narrative in narratives]

EKGset = set()
pred_int = []
# extract concept and calculate similarity

def pre_tick_handler(behaviour_tree):
    blackboard = Blackboard()
    blackboard.tick_num += 1
for i,chunks in enumerate(tqdm(chunked_narratives[:5])):
    temp_int = []
    if not pd.isnull(vitals[i]):
        vt = vitals[i].strip('{}').split('}{')
        vt = [it.split(':')[-1] for it in vt]
        for idx,it in enumerate(vt):
            if 'EKG-' in it:
                temp = it.split('EKG-')
                temp[1] = temp[1].replace(' ','_')
                temp[1] = temp[1].replace('-','_')
                if ',' in temp[1]:
                    t = temp[1].split(',')
                    t = [EKGdic[i] for i in t]
                    vt[idx] = temp[0] + 'EKG-' + ','.join(t)
                else:
                    vt[idx] = temp[0] + 'EKG-' + EKGdic[temp[1]]
                if len(temp[1]) > 0:
                    EKGset.add(temp[1])
        vt = [ite for l in vt for ite in l.strip().split(' ')]
        for idx in xrange(len(vt)):
            if idx < len(vt) and '-' not in vt[idx]:
                vt.pop(idx)
        for idx,it in enumerate(vt):
            temp = it.split('-')
            vt[idx] = (temp[0],temp[1])
    chunked_vt = list(np.array_split(vt, len(chunks)))
    blackboard = Blackboard()
    root = py_trees.composites.Sequence("Root_1")
    IG = be.InformationGathering()
    TC = be.TextCollection()
    V = be.Vectorize()
    PS = be.ProtocolSelector()
    root.add_children([TC,IG,V,PS,be.protocols])
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.setup(15)
    for idx, item in enumerate(chunks):
        blackboard.text = [item]
        blackboard.inC = list(chunked_vt[idx])
        behaviour_tree.tick_tock(
            sleep_ms=50,
            number_of_iterations=1,
            pre_tick_handler=None,
       post_tick_handler=None
        )
        res = []
        for key in blackboard.feedback:
            if blackboard.feedback[key] > 0.1:
                res.append((key, blackboard.feedback[key]))
        temp_int.append(res)
        print blackboard.candi[0]
        print res
    pred_int.append(temp_int)

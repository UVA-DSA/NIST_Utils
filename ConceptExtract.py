from pymetamap import MetaMap
from pandas import Series, DataFrame
from collections import defaultdict
import pandas as pd
import numpy as np
import re
import collections
import nltk
from nltk.corpus import stopwords
import re
from nltk import ngrams
import negation_detection
from nltk.tokenize import sent_tokenize

class PatientStatus(object):
    def __init__(self, name, binary, value = '', content = ''):
        self.name = name
        self.binary = binary
        self.value = value
        self.content = content
        self.tick = 0
        self.score = 0

class ConceptExtractor(object):
    def __init__(self, List_route):
        '''
        list_route: route of the list file
        extend list: a .csv file, two colum: required concepts and its cuis.
        status: a dict, keys are concepts, values are corresponding informations. 
                Indicates the default status of the patient.
        self.CUIs: list of the requied CUIs
        self.CUI2Concept: mapping the CUIs to the concepts
        self.Status: dict to store the information
        self.mm: MetaMap object
        self.R_range: range of value retrival in the text, default: 14
        self.pattern: pattern of the requied value
        '''
        extended_concept_list = pd.read_csv(List_route)
        self.seeds = list()
        self.CUIs = [item for item in extended_concept_list['CUI']]
        self.CUI2Concept = defaultdict(list)
        for idx,item in enumerate(extended_concept_list['Required Concept']):
            if item > 0:
                temp = item.lower()
                self.seeds.append(temp)
                self.CUI2Concept[self.CUIs[idx]].append(temp)
            else:
                self.CUI2Concept[self.CUIs[idx]].append(temp)
        self.R_range = 14
        self.pattern = "\d+\.?\d*"
        self.Log = list()
        #self.ex_extend_cons = []
        #self.raw_ex_cons = []
        
    def StatusInit(self):
        '''
        if don't have a defined initial status, this function can generate a default status from the concept list
        all the binary status are defined as False initially
        '''
        self.Status = dict()
        for item in self.seeds:
            if item == 'breath' or item == 'pulse' or item == 'conscious':
                self.Status[item] = PatientStatus(item, True)
            else:
                self.Status[item] = PatientStatus(item, False)
                
    def SpecificInit(self, item):
        '''
        init a specific item in the dictionary
        '''
        if item == 'breath' or item == 'pulse' or item == 'conscious':
            self.Status[item] = PatientStatus(item, True)
        else:
            self.Status[item] = PatientStatus(item, False)
                
            
    
    def ConceptExtract(self, sent_text):
        '''
        sent_text: a list of sent text
        '''
        mm = MetaMap.get_instance('/Users/sileshu/Downloads/public_mm/bin/metamap16',version = 2016)
        self.concepts,_ = mm.extract_concepts(sent_text,word_sense_disambiguation=True,\
                                     ignore_stop_phrases=True)
        self.scores,_ = mm.extract_concepts(sent_text,mmi_output=False,word_sense_disambiguation=True,\
                                     ignore_stop_phrases=True)
                                     
    def ConceptWrapper(self,concepts):
        '''
        this method is developed especially for transforming the information in vital column of RAA dataset
        concepts: a list contains items with following format: (concept, valueStr)
        
        wrap rules:
        confidence: 1000. if mmi score is not used, 50. if mmi score is used.
        trigger: same as the vital name in RAA data
        tick: 1
        '''
        pool = set(['Pulse', 'Resp', 'BP', 'GCS', 'Glucose', 'SPO2', 'Pain', 'EKG'])
        self.Status = dict()
        self.vtLog = dict()
        for item in pool:
            self.vtLog[item] = []
        for item in concepts:
            if item[0] not in pool:
                continue
            if item[1] == '0' or item[1] == '0/0' or item[1] == '':
                self.Status[item[0]] = PatientStatus(item[0], False, item[1], item[0])
            else:
                self.Status[item[0]] = PatientStatus(item[0], True, item[1], item[0])
                self.vtLog[item[0]].append(item[1])
            self.Status[item[0]].score = 1000.
            self.Status[item[0]].tick = 1
            content = '('+self.Status[item[0]].name+';'+str(self.Status[item[0]].binary)+';'+\
            str(self.Status[item[0]].value)+';'+self.Status[item[0]].content+';'+\
            str(self.Status[item[0]].score)+';'+str(self.Status[item[0]].tick)+')'
            self.Log.append(content)
            
        
    def FirstExtract(self, sent_text, tick_num):
        for concept in self.concepts:
            if concept[1] == 'AA':
                continue
            normalized_trigger_name = concept[6].split('-')[3].strip('"').lower()
            # last part of "trigger" field, 1 means negation is detected
            negation = concept[6].split('-')[-1].rstrip(']') == '0' # negation = False if negation is detected
            CUI = concept[4]
            #score = float(concept[2])
            score = float(self.scores[CUI])
            posi_info = concept[8].replace(';',',').strip('[]').split('],[')
            preferred_name = concept[3].lower()
            for i in range(len(posi_info)):
                if CUI in self.CUIs:
                    if ',' in posi_info[i]:
                        position = posi_info[i].split(',')[-1].split('/')
                        position = [item.strip('[]') for item in position]
                    else:
                        position = posi_info[i].split('/')
                        position = [item.strip('[]') for item in position]
                    beginPt = int(position[0])
                    length = int(position[1])
                    if beginPt+length+self.R_range > len(sent_text[0]):
                        latter_strPiece = sent_text[0][beginPt+length:len(sent_text[0])]
                    else:
                        latter_strPiece = sent_text[0][beginPt+length:beginPt+length+self.R_range]
                    if beginPt-self.R_range < 0:
                        former_strPiece = sent_text[0][0:beginPt]
                    else:
                        former_strPiece = sent_text[0][beginPt-self.R_range:beginPt]
                    mapped_concepts = self.CUI2Concept[CUI]
                    for mapped_concept in mapped_concepts:
                        if mapped_concept in self.Status:
                            self.Status[mapped_concept].tick = tick_num
                            self.Status[mapped_concept].binary = negation
                            self.Status[mapped_concept].content = normalized_trigger_name
                            self.Status[mapped_concept].score = score
                            if mapped_concept == 'age':
                                value = re.findall(self.pattern,former_strPiece)
                            else:
                                value = re.findall(self.pattern,latter_strPiece)
                            if len(value) > 0:
                                if mapped_concept == 'blood pressure':
                                    if len(value) >= 2:
                                        self.Status[mapped_concept].value = (value[0]+'/'+value[1])
                                    else:
                                        self.Status[mapped_concept].value = (value[0])
                                elif mapped_concept == 'spo2':
                                    self.Status[mapped_concept].value = (value[0]+'%')
                                else:
                                    self.Status[mapped_concept].value = value[0]
                            else:
                                self.Status[mapped_concept].value = normalized_trigger_name
                            # make log
                            content = '('+self.Status[mapped_concept].name+';'+str(self.Status[mapped_concept].binary)+';'+\
                            str(self.Status[mapped_concept].value)+';'+self.Status[mapped_concept].content+';'+\
                            str(self.Status[mapped_concept].score)+';'+str(self.Status[mapped_concept].tick)+')'
                            self.Log.append(content)
                            
    def DisplayStatus(self):
        for item in self.Status:
            if len(self.Status[item].content) > 0:
                content = '('+self.Status[item].name+';'+str(self.Status[item].binary)+';'+\
                str(self.Status[item].value)+';'+self.Status[item].content+';'+\
                str(self.Status[item].score)+';'+str(self.Status[item].tick)+')'
                print content


class CEWithoutMM(object):
    def __init__(self, List_route):
        # stop words
        stop_words = set(stopwords.words('english'))
        stop_words.update(['zero','one','two','three','four','five','six','seven','eight','nine','ten','may','also','across','among','beside','however','yet','within','h','c']) 
        self.re_stop_words = re.compile(r"\b(" + "|".join(stop_words) + ")\\W", re.I)
        # table generation
        self.seeds = list()
        self.mapping = collections.defaultdict(list)
        fo = open(List_route)
        for line in fo:
            temp = line.strip('\r\n').strip().split('\t')
            self.seeds.append(temp[0])
            for i in temp:
                self.mapping[i].append(temp[0])
                
    def StatusInit(self):
        '''
        if don't have a defined initial status, this function can generate a default status from the concept list
        all the binary status are defined as False initially
        '''
        self.Status = dict()
        for item in self.seeds:
            if item == 'breath' or item == 'pulse' or item == 'conscious':
                self.Status[item] = PatientStatus(item, True)
            else:
                self.Status[item] = PatientStatus(item, False)
                
    def SpecificInit(self, item):
        '''
        init a specific item in the dictionary
        '''
        if item == 'breath' or item == 'pulse' or item == 'conscious':
            self.Status[item] = PatientStatus(item, True)
        else:
            self.Status[item] = PatientStatus(item, False)
                
    def ConceptWrapper(self,concepts):
        '''
        this method is developed especially for transforming the information in vital column of RAA dataset
        concepts: a list contains items with following format: (concept, valueStr)
        
        wrap rules:
        confidence: 1000. if mmi score is not used, 50. if mmi score is used.
        trigger: same as the vital name in RAA data
        tick: 1
        '''
        pool = set(['Pulse', 'Resp', 'BP', 'GCS', 'Glucose', 'SPO2', 'Pain', 'EKG'])
        for item in concepts:
            if item[0] not in pool:
                continue
            if item[1] == '0' or item[1] == '0/0' or item[1] == '':
                self.Status[item[0]] = PatientStatus(item[0], False, item[1], item[0])
            else:
                self.Status[item[0]] = PatientStatus(item[0], True, item[1], item[0])
            self.Status[item[0]].score = 1000.
            self.Status[item[0]].tick = 1
        
    
    def cleanPunc(self, sentence):
        cleaned = re.sub(r'[?|!|\'|"|#]',r'',sentence)
        cleaned = re.sub(r'[.|,|)|(|\|/]',r' ',cleaned)
        cleaned = cleaned.strip()
        cleaned = cleaned.replace("\n"," ")
        return cleaned

    def keepAlpha(self, sentence):
        alpha_sent = ""
        for word in sentence.split():
            alpha_word = re.sub('[^a-z A-Z]+', ' ', word)
            alpha_sent += alpha_word
            alpha_sent += " "
        alpha_sent = alpha_sent.strip()
        return alpha_sent
        
    def removeStopWords(self, sentence):
        return self.re_stop_words.sub(" ", sentence)
        
    def CE(self, text, tick_num):
        '''
        naive version: ignore the value field
        score: always 1000.
        neg: coreNLP
        '''
        sent_tokenize_list = sent_tokenize(text)
        for sent in sent_tokenize_list:
            sent = sent.strip().lower()
            if len(sent) == 0:
                continue
            txt = self.cleanPunc(sent)
            txt = self.keepAlpha(txt)
            txt = self.removeStopWords(txt)
            words = txt.split()
            bigram = ngrams(words,2)
            trigram = ngrams(words,3)
            for i in words:
                if i in self.mapping:
                    try:
                        neg = negation_detection.predict(sent, i)
                        if neg != None:
                            for j in self.mapping[i]:
                                self.Status[j].bianry = neg
                                self.Status[j].score = 1000.
                                self.Status[j].content = i
                                self.Status[j].tick = tick_num
                    except:
                        continue
                            
            for i in bigram:
                temp = ' '.join(i)
                if temp in self.mapping:
                    try:
                        neg = negation_detection.predict(sent, temp)
                        if neg != None:
                            for j in self.mapping[temp]:
                                self.Status[j].bianry = neg
                                self.Status[j].score = 1000.
                                self.Status[j].content = temp
                                self.Status[j].tick = tick_num
                    except:
                        continue
                            
            for i in trigram:
                temp = ' '.join(i)
                if temp in self.mapping:
                    try:
                        neg = negation_detection.predict(sent, temp)
                        if neg != None:
                            for j in self.mapping[temp]:
                                self.Status[j].bianry = neg
                                self.Status[j].score = 1000.
                                self.Status[j].content = temp
                                self.Status[j].tick = tick_num
                    except:
                        continue
        
        
    def DisplayStatus(self):
        for item in self.Status:
            if len(self.Status[item].content) > 0:
                content = '('+self.Status[item].name+';'+str(self.Status[item].binary)+';'+\
                str(self.Status[item].value)+';'+self.Status[item].content+';'+\
                str(self.Status[item].score)+';'+str(self.Status[item].tick)+')'
                print content
        
                       
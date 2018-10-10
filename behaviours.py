import py_trees
from pandas import Series, DataFrame
import pandas as pd
from scipy import spatial
import re
from py_trees.blackboard import Blackboard
import ConceptExtract as CE
import time

# dummy leaves
class PROTOCOLi_Check(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'PROTOCOLi_Check'):
        super(PROTOCOLi_Check, self).__init__(name)

class PROTOCOLi_Action(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'PROTOCOLi_Action'):
        super(PROTOCOLi_Action, self).__init__(name)
        
class ProtocolSelector(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'ProtocolSelector'):
        super(ProtocolSelector, self).__init__(name)
# action leaves
class InformationGathering(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'InformationGathering'):
        super(InformationGathering, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        '''
        create a ConceptExtractor and initialize the patient status
        the list here is the complete list
        '''
        '''
        self.ce1 = CE.ConceptExtractor("Concept_List_1.csv")
        self.ce1.StatusInit()
        self.ce2 = CE.ConceptExtractor("Concept_List_2.csv")
        self.ce2.StatusInit()
        '''
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("/Users/sileshu/Desktop/BT/concept_list(s&s).csv")
        self.ce.StatusInit()
        blackboard.Status = self.ce.Status
        blackboard.ConcLog = []
        return True
        
    def update(self):
        blackboard = Blackboard()
        '''
        self.ce1.ConceptExtract(blackboard.text)
        blackboard.concepts = self.ce1.concepts
        self.ce1.FirstExtract(blackboard.text, blackboard.tick_num)
        blackboard.status1 = self.ce1.Status
        self.ce2.concepts = blackboard.concepts
        self.ce2.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.status2 = self.ce2.Status
        self.ce1.DisplayStatus()
        self.ce2.DisplayStatus()
        '''
        self.ce.ConceptExtract(blackboard.text)
        blackboard.concepts = self.ce.concepts
        self.ce.FirstExtract(blackboard.text, blackboard.tick_num)
        blackboard.Status = self.ce.Status
        self.ce.DisplayStatus()
        blackboard.ConcLog += self.ce.Log
        return py_trees.Status.SUCCESS
        
class Vectorize(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Vectorize'):
        super(Vectorize, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        '''
        create a ConceptExtractor and initialize the patient status
        the list here is the complete list
        '''
        '''
        self.ce1 = CE.ConceptExtractor("Concept_List_1.csv")
        self.ce1.StatusInit()
        self.ce2 = CE.ConceptExtractor("Concept_List_2.csv")
        self.ce2.StatusInit()
        '''
        blackboard = Blackboard()
        PC = dict()
        '''
        PC = {
        'BLSCPR':['breath','pulse'],
        'BleedingControl':['bleed'],
        'Burn':['burn'],
        'ChestPain':['pain','12-lead ecg','pain region','mi','pain quality'],
        'GeneralTraumaManagement':['pain severity','pain','open chest wound','wound','contusion','evisceration','abrasion'],
        'RespiratoryDistress':['spo2','breath','etco2']
        }
        '''
        pro_df = pd.read_excel('/Users/sileshu/Desktop/BT/ODEMSA_Protocols.xlsx')
        for line in pro_df.iterrows():
            line_ss = [i.strip().lower() for i in line[1]['Signs&Symptoms'].split(';')]
            name = line[1]['Protocol']
            PC[name] = line_ss
        self.PV = dict()
        for item in PC:
            vec = list()
            for i in blackboard.Status:
                vec.append(float(i in PC[item]))
            self.PV[item] = vec
        return True
        
    
    def update(self):
        blackboard = Blackboard()
        '''
        self.ce1.ConceptExtract(blackboard.text)
        blackboard.concepts = self.ce1.concepts
        self.ce1.FirstExtract(blackboard.text, blackboard.tick_num)
        blackboard.status1 = self.ce1.Status
        self.ce2.concepts = blackboard.concepts
        self.ce2.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.status2 = self.ce2.Status
        self.ce1.DisplayStatus()
        self.ce2.DisplayStatus()
        '''
        
        # mm confidence encoding
        TV = []
        for item in blackboard.Status:
            if blackboard.Status[item].binary:
                TV.append(blackboard.Status[item].score)
        
        #TV = [blackboard.Status[item].score for item in blackboard.Status]
        '''
        # one-hot encoding
        TV = [int(blackboard.Status[item].binary) for item in blackboard.Status]
        '''
        maxsim = 0
        result = ''
        blackboard.ranking = []
        for key in self.PV:
            sim = 1 - spatial.distance.cosine(TV,self.PV[key])
            print key,sim
            blackboard.ranking.append((key,sim))
            if sim > maxsim:
                maxsim = sim
                result = key
        blackboard.protocol = result
        return py_trees.Status.SUCCESS

    


class TextCollection(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'TextCollection'):
        super(TextCollection, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        #level = raw_input("Please type in your certification(EMT,A,I/P): \n")
        level = 'I/P'
        blackboard = Blackboard()
        #blackboard.action = []
        blackboard.level = level
        blackboard.tick_num = 0
        blackboard.protocol = "Universal Patient Care"
        self.text = ''
        self.sent_text = []
        return True
    
    def initialise(self):
        self.sent_text = []

    
    def update(self):
        '''
        if (not q.empty()) and len(self.text) <= 100:
            self.text += q.get()
        if len(self.text) > 100:
            self.sent_text.append(self.text)
            self.text = ''
        blackboard = Blackboard()
        blackboard.text = self.sent_text
        '''
        '''
        self.sent_text.append(raw_input("input_text:\n"))
        
        blackboard = Blackboard()
        blackboard.text = self.sent_text
        '''
        return py_trees.Status.SUCCESS

		
class Arbiter(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Arbiter'):
        super(Arbiter, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        c1, c2 = 0, 0
        for item in blackboard.status1:
            if len(blackboard.status1[item].content) > 0:
                c1 += 1
        for item in blackboard.status2:
            if len(blackboard.status2[item].content) > 0:
                c2 += 1
        if c1 <= 2:
            blackboard.action = "Keep Performing Vital Assessments"
            blackboard.protocol = "Universal Patient Care"
        elif c2 < 1 and c1 < 5:
            blackboard.action = "Keep Performing SAMPLE History or Pain/Trauma Assessments"
            blackboard.protocol = "Universal Patient Care"
        
        return py_trees.Status.SUCCESS
    

# protocols' condition
class BLSCPR_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'BLSCPR_Condition'):
        super(BLSCPR_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("BLSCPR.csv")
        self.ce.StatusInit()
        blackboard.BLSCPR_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.BLSCPR_Status = self.ce.Status
        if blackboard.status1['pulse'].binary == False and \
        blackboard.status1['breath'].binary == False:
            blackboard.Protocol = "BLS CPR"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class Bleeding_Control_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Bleeding_Control_Condition'):
        super(Bleeding_Control_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("BleedingControl.csv")
        self.ce.StatusInit()
        blackboard.BC_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.BC_Status = self.ce.Status
        if blackboard.status1['bleed'].binary == True:
            blackboard.Protocol = "Bleeding Control"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE


class Burn_Injury_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Burn_Injury_Condition'):
        super(Burn_Injury_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("Burn.csv")
        self.ce.StatusInit()
        blackboard.Burn_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        if blackboard.fentanyl[0] > 0:
            self.ce.SpecificInit('fentanyl')
        if blackboard.ondansetron[0] > 0:
            self.ce.SpecificInit('ondansetron')
        if blackboard.ketamine[0] > 0:
            self.ce.SpecificInit('ketamine')
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.Burn_Status = self.ce.Status
        if blackboard.status1['wound'].binary == True and blackboard.status2['burn'].binary == True:
            blackboard.protocol = "Burn Injury"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class GeneralTraumaGuideline_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'GeneralTraumaGuideline_Condition'):
        super(GeneralTraumaGuideline_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("GeneralTrauma.csv")
        self.ce.StatusInit()
        blackboard.GT_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        if blackboard.fentanyl[0] > 0:
            self.ce.SpecificInit('fentanyl')
        if blackboard.ondansetron[0] > 0:
            self.ce.SpecificInit('ondansetron')
        if blackboard.ketamine[0] > 0:
            self.ce.SpecificInit('ketamine')
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.GT_Status = self.ce.Status
        if blackboard.status1['wound'].binary == True and blackboard.status2['burn'].binary == False:
            blackboard.protocol = "General Trauma Guideline"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class RespiratoryDistress_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'RespiratoryDistress_Condition'):
        super(RespiratoryDistress_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("Respiratory.csv")
        self.ce.StatusInit()
        blackboard.Res_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.Res_Status = self.ce.Status
        if blackboard.status1['breath'].binary == False:
            blackboard.protocol = "Respiratory Distress"
            return py_trees.Status.SUCCESS
        if len(blackboard.status1['breath'].value) > 0:
            if int(blackboard.status1['breath'].value) > 30 or int(blackboard.status1['breath'].value) < 10:
                blackboard.protocol = "Respiratory Distress"
                return py_trees.Status.SUCCESS
        if len(blackboard.status1['spo2'].value) > 0:
            if int(blackboard.status1['spo2'].value.replace('%','')) < 70:
                blackboard.protocol = "Respiratory Distress"
                return py_trees.Status.SUCCESS
        if len(blackboard.status1['etco2'].value) >0:
            if int(blackboard.status1['etco2'].value) > 45 or int(blackboard.status1['etco2'].value) < 35:
                blackboard.protocol = "Respiratory Distress"
                return py_trees.Status.SUCCESS
        return py_trees.Status.FAILURE
        
class ChestPain_Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'ChestPain_Condition'):
        super(ChestPain_Condition, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.ce = CE.ConceptExtractor("ChestPain.csv")
        self.ce.StatusInit()
        blackboard.CP_Status = self.ce.Status
        return True
    
    def update(self):
        blackboard = Blackboard()
        self.ce.concepts = blackboard.concepts
        if blackboard.fentanyl[0] > 0:
            self.ce.SpecificInit('fentanyl')
        if blackboard.ondansetron[0] > 0:
            self.ce.SpecificInit('ondansetron')
        if blackboard.nitroglycerin[0] > 0:
            self.ce.SpecificInit('nitroglycerin')
        self.ce.SecondExtract(blackboard.text, blackboard.tick_num)
        blackboard.CP_Status = self.ce.Status
        if blackboard.status1['pain'].binary == True and \
        ('chest' in blackboard.status1['pain'].content or \
         'chest' in blackboard.status2['pain region'].content or\
         'chest' in blackboard.status2['pain region'].value):
            blackboard.protocol = "Chest Pain"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
            
# ChestPain
class ECG(py_trees.behaviour.Behaviour):
    def __init__(self, name = '12-Lead ECG'):
        super(ECG, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.CP_Status['12-lead ecg'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
    
class MI(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'STEMI?'):
        super(MI, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.CP_Status['mi'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
    
class Transport(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Transport'):
        super(Transport, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        blackboard.action = self.name
        return py_trees.Status.SUCCESS
    
class Aspirin(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Aspirin'):
        super(Aspirin, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.CP_Status['aspirin'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            blackboard.action = self.name
            return py_trees.Status.FAILURE

class Advanced(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Advanced EMT?'):
        super(Advanced, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.level = blackboard.level
        return True
    
    def update(self):
        blackboard = Blackboard()
        if self.level == "A" or self.level == "I/P":
            blackboard.action = 'IV access'
            return py_trees.Status.SUCCESS
        else:
            print "don't have enough certification"
            return py_trees.Status.FAILURE

class IV(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'IV access?'):
        super(IV, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.CP_Status['iv/io/vascular access'].binary == True or\
        blackboard.Burn_Status['iv/io/vascular access'].binary == True or\
        blackboard.GT_Status['iv/io/vascular access'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
    
class Nausea(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Nausea/Vommiting?'):
        super(Nausea, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.CP_Status['nausea'].binary == True or \
        blackboard.Burn_Status['nausea'].binary == True or \
        blackboard.GT_Status['nausea'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class ondansetron(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'ondansetron'):
        super(ondansetron, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        blackboard.ondansetron = [0,0.]
        return True
    
    def update(self):
        blackboard = Blackboard()
        # usage detection
        if blackboard.CP_Status['ondansetron'].binary == True or\
        blackboard.Burn_Status['ondansetron'].binary == True or\
        blackboard.GT_Status['ondansetron'].binary == True:
            blackboard.ondansetron[0] += 1
            blackboard.ondansetron[1] = time.time()
        if blackboard.ondansetron[0] == 0:
            blackboard.action = 'ondansetron 4mg ODT'
            return py_trees.Status.FAILURE
        elif blackboard.ondansetron[0] == 1 and (time.time() - blackboard.ondansetron[1] > 600):
            blackboard.action = 'ondansetron 4mg ODT'
            return py_trees.Status.FAILURE
        else:
            return py_trees.Status.SUCCESS
    
class IP(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'I/P?'):
        super(IP, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        self.level = blackboard.level
        return True
    
    def update(self):
        if self.level == "I/P":
            return py_trees.Status.SUCCESS
        else:
            print "don't have enough certification"
            return py_trees.Status.FAILURE

    
class Fentanyl_IV(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Fentanyl_IV'):
        super(Fentanyl_IV, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        blackboard.fentanyl = [0,0.]
        return True
    
    def update(self):
        blackboard = Blackboard()
        # fentanyl usage detection
        if blackboard.CP_Status['fentanyl'].binary == True or\
        blackboard.Burn_Status['fentanyl'].binary == True or\
        blackboard.GT_Status['fentanyl'].binary == True:
            blackboard.fentanyl[0] += 1
            blackboard.fentanyl[1] = time.time()
        # fentanyl usage under different conditions
        if blackboard.fentanyl[0] == 0:
            if len(blackboard.status1['age'].value) > 0:
                if int(blackboard.status1['age'].value) >= 65:
                    blackboard.action = '0.5 microgram/kg Fentanyl IV'
                elif int(blackboard.status1['age'].value) < 65:
                    blackboard.action = '1 microgram/kg Fentanyl IV'
            else:
                blackboard.action = '1 microgram/kg Fentanyl IV'
            return py_trees.Status.FAILURE
        elif blackboard.fentanyl[0] == 1 and (time.time() - blackboard.fentanyl[1] > 600):
            if len(blackboard.status1['age'].value) > 0:
                if int(blackboard.status1['age'].value) >= 65:
                    blackboard.action = '0.5 microgram/kg Fentanyl IV'
                elif int(blackboard.status1['age'].value) < 65:
                    blackboard.action = '1 microgram/kg Fentanyl IV'
            else:
                blackboard.action = '1 microgram/kg Fentanyl IV'
            return py_trees.Status.FAILURE
        else:
            return py_trees.Status.SUCCESS
        
class Fentanyl_IN(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Fentanyl_IN'):
        super(Fentanyl_IN, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        blackboard.fentanyl = [0,0.]
        return True
    
    def update(self):
        blackboard = Blackboard()
        # fentanyl usage detection
        if blackboard.CP_Status['fentanyl'].binary == True or\
        blackboard.Burn_Status['fentanyl'].binary == True or\
        blackboard.GT_Status['fentanyl'].binary == True:
            blackboard.fentanyl[0] += 1
            blackboard.fentanyl[1] = time.time()
        # fentanyl usage under different conditions
        if blackboard.fentanyl[0] == 0 or \
        (blackboard.fentanyl[0] == 1 and (time.time() - blackboard.fentanyl[1] > 600)):
            blackboard.action = '2 microgram/kg Fentanyl IN'
            return py_trees.Status.FAILURE
        else:
            return py_trees.Status.SUCCESS
    
class Nitro(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'nitroglycerin'):
        super(Nitro, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        blackboard.nitroglycerin = [0,0.]
        return True
    
    def update(self):
        blackboard = Blackboard()
        # usage detection
        if blackboard.CP_Status['nitroglycerin'].binary == True:
            blackboard.nitroglycerin[0] += 1
            blackboard.nitroglycerin[1] = time.time()
        if len(blackboard.status1['blood pressure'].value) > 0:
            if int(blackboard.status1['blood pressure'].value.split('/')[0]) > 100:
                if blackboard.nitroglycerin[0] == 0:
                    blackboard.action = "nitroglycerin 0.4mg"
                    return py_trees.Status.FAILURE
                elif blackboard.nitroglycerin[0] > 0 and\
                ((time.time() - blackboard.nitroglycerin[1]) > 300):
                    blackboard.action = "nitroglycerin 0.4mg"
                    return py_trees.Status.FAILURE
        return py_trees.Status.SUCCESS
    
class NotStarted(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'NS'):
        super(NotStarted, self).__init__(name)
    
    def update(self):
        return py_trees.Status.SUCCESS
		
# General Trauma
class Evisceration(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Evisceration'):
        super(Evisceration, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.GT_Status['evisceration'].binary == True:
            blackboard.action = "cover with moist sterile dressing"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class OpenChestWound(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'OpenChestWound'):
        super(OpenChestWound, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.GT_Status['open chest wound'].binary == True:
            blackboard.action = "cover with occlusive dressing"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class shock(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'shock'):
        super(shock, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.GT_Status['shock'].binary == True:
            blackboard.action = "needle chest decompression"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
			

# Respiratory
class MDI(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'MDI'):
        super(MDI, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Res_Status['mdi'].binary == True:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
        
class CPAP(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'CPAP'):
        super(CPAP, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Res_Status['cpap'].binary == True:
            return py_trees.Status.SUCCESS
        elif len(blackboard.status1['blood pressure'].value) > 0:
            if int(blackboard.status1['blood pressure'].value.split('/')[0]) < 90 or blackboard.status1['conscious'] == False:
                return py_trees.Status.SUCCESS
        elif len(blackboard.status1['spo2'].value) > 0:
            if int(blackboard.status1['spo2'].value.replace('%','')) < 90:
                blackboard.action = self.name
                return py_trees.Status.FAILURE
        return py_trees.Status.SUCCESS
        
class AdministerOxygen(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'AdministerOxygen'):
        super(AdministerOxygen, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Res_Status['administer oxygen'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            blackboard.action = self.name
            return py_trees.Status.FAILURE
        
class AlbuterolSulfate(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'AlbuterolSulfate'):
        super(AlbuterolSulfate, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Res_Status['albuterol sulfate'].binary == True:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
        
class Methylprednisolone(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Methylprednisolone'):
        super(Methylprednisolone, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Res_Status['methylprednisolone'].binary == True:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
			
# Burn
class ElectricalBurn(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Electrical Burn?'):
        super(ElectricalBurn, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if 'electric' in blackboard.status2['burn'].value or\
        'electric' in blackboard.status2['burn'].content:
            blackboard.action = "Search for additional injury"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class ChemicalBurn(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Chemical Burn?'):
        super(ChemicalBurn, self).__init__(name)

    def update(self):
        blackboard = Blackboard()
        if 'chemical' in blackboard.status2['burn'].value or\
        'chemical' in blackboard.status2['burn'].content:
            blackboard.action = "Irrigate with water/brush the powder off"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class ThermalBurn(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Thermal Burn?'):
        super(ThermalBurn, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if 'thermal' in blackboard.status2['burn'].value or\
        'thermal' in blackboard.status2['burn'].content:
            blackboard.action = "Assess for carbon monoxide exposure"
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
        
        
class SpiRestriction(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Spinal motion restriction'):
        super(SpiRestriction, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.Burn_Status['spinal motion restriction'].binary == True:
            blackboard.action = self.name
        return py_trees.Status.SUCCESS

class Ketamine(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Ketamine'):
        super(Ketamine, self).__init__(name)
        
    def setup(self, unused_timeout = 15):
        blackboard = Blackboard()
        blackboard.ketamine = [0,0]
        return True
    
    def update(self):
        blackboard = Blackboard()
        # usage detection
        if blackboard.Burn_Status['ketamine'].binary == True or\
        blackboard.GT_Status['ketamine'].binary == True:
            blackboard.ketamine[0] += 1
            blackboard.ketamine[1] = time.time()
        if blackboard.fentanyl[0] >= 2 and blackboard.status['pain'].binary == True:
            if blackboard.ketamine[0] == 0:
                blackboard.action = "ketamine 0.5mg/kg IV"
                return py_trees.Status.SUCCESS
            elif blackboard.ketamine[0] == 1 and (time.time() - blackboard.ketamine[1] > 600):
                blackboard.action = "ketamine 0.5mg/kg IV"
                return py_trees.Status.SUCCESS
            else:
                return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.SUCCESS
			
# Bleeding Control
class Unstable(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'unstable?'):
        super(Unstable, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.BC_Status['unstable'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class Move(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Move to tourniquet'):
        super(Move, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        blackboard.action = self.name
        return py_trees.Status.SUCCESS
    
class Pressure(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Direct pressure to the bleeding site'):
        super(Pressure, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        blackboard.action = self.name
        return py_trees.Status.SUCCESS
    
class Control(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'Controlled?'):
        super(Control, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.status1['bleed'].binary == True:
            return py_trees.Status.FAILURE
        else:
            return py_trees.Status.SUCCESS
			
# BLSCPR
class DNR(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'DNR?'):
        super(DNR, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.BLSCPR_Status['dnr'].binary == True:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
        
class CPR(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'CPR'):
        super(CPR, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.BLSCPR_Status['cpr'].binary == True or \
        blackboard.BLSCPR_Status['aed'].binary == True or\
        blackboard.BLSCPR_Status['defibrillation'].binary == True:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class AirwayManagement(py_trees.behaviour.Behaviour):
    def __init__(self, name = 'AirwayManagement'):
        super(AirwayManagement, self).__init__(name)
    
    def update(self):
        blackboard = Blackboard()
        if blackboard.BLSCPR_Status['bvm'].binary == True or\
        blackboard.BLSCPR_Status['opa'].binary == True:
            blackboard.action = self.name
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE
			
# sub-trees
BLSCPR_Action = py_trees.composites.Selector("BLSCPR_Action")
BLSCPR_S1 = py_trees.composites.Sequence("Sequence_1")
BLSCPR_S2 = py_trees.composites.Sequence("Sequence_2")
BLSCPR_NS_1 = NotStarted()
BLSCPR_NS_2 = NotStarted()
BLSCPR_DNR = DNR()
BLSCPR_CPR = CPR()
BLSCPR_AM = AirwayManagement()
BLSCPR_Action.add_children([BLSCPR_S1,BLSCPR_S2,BLSCPR_NS_1])
BLSCPR_S1.add_children([BLSCPR_DNR,BLSCPR_NS_2])
BLSCPR_S2.add_children([BLSCPR_CPR,BLSCPR_AM])

BC_Action = py_trees.composites.Sequence("BleedControl_Action")
BC_S1 = py_trees.composites.Sequence("Sequence_1")
BC_S2 = py_trees.composites.Sequence("Sequence_2")
BC_SE = py_trees.composites.Selector("Selector")
BC_NS = NotStarted()
BC_US = Unstable()
BC_Move_1 = Move()
BC_Move_2 = Move()
BC_Pressure = Pressure()
BC_Control = Control()
BC_Action.add_children([BC_SE,BC_NS])
BC_SE.add_children([BC_S1,BC_S2])
BC_S1.add_children([BC_US,BC_Move_1])
BC_S2.add_children([BC_Pressure,BC_Control,BC_Move_2])

# composite
Burn_Action = py_trees.composites.Sequence("Burn_Action")
B_S1 = py_trees.composites.Sequence("Sequence")
B_S2 = py_trees.composites.Sequence("Sequence")
B_S3 = py_trees.composites.Sequence("Sequence")
B_S4 = py_trees.composites.Sequence("Sequence")
B_SE1 = py_trees.composites.Selector("Selector")
B_SE2 = py_trees.composites.Selector("Selector")
B_SE3 = py_trees.composites.Selector("Selector")
B_SE4 = py_trees.composites.Selector("Selector")
# behaviour
B_NS_1 = NotStarted()
B_NS_2 = NotStarted()
B_NS_3 = NotStarted()
B_SPI = SpiRestriction()
B_EB = ElectricalBurn()
B_CB = ChemicalBurn()
B_TB = ThermalBurn()
B_IV = IV()
B_NAU_1 = Nausea()
B_NAU_2 = Nausea()
B_OD_1 = ondansetron()
B_OD_2 = ondansetron()
B_IP = IP()
B_FEN_IV = Fentanyl_IV()
B_FEN_IN = Fentanyl_IN()
B_A = Advanced()
B_KET = Ketamine()
# tree
Burn_Action.add_children([B_SPI,B_SE1,B_A,B_IP,B_SE2])
B_SE1.add_children([B_EB,B_CB,B_TB,B_NS_1])
B_SE2.add_children([B_S1,B_S2])
B_S1.add_children([B_IV,B_FEN_IV,B_KET,B_SE3])
B_SE3.add_children([B_S3,B_NS_2])
B_S3.add_children([B_NAU_1,B_OD_1])
B_S2.add_children([B_FEN_IN,B_SE4])
B_S4.add_children([B_NAU_2,B_OD_2])
B_SE4.add_children([B_S4,B_NS_3])

Respiratory_Action = py_trees.composites.Selector("Respiratory_Action")
R_S1 = py_trees.composites.Sequence("Sequence")
R_S2 = py_trees.composites.Sequence("Sequence")
R_SE = py_trees.composites.Selector("Selector")
R_MDI = MDI()
R_CPAP = CPAP()
R_AO = AdministerOxygen()
R_AS = AlbuterolSulfate()
R_A = Advanced()
R_IV = IV()
R_METH = Methylprednisolone()
R_NS_1 = NotStarted()
R_NS_2 = NotStarted()
Respiratory_Action.add_children([R_S1,R_NS_1])
R_S1.add_children([R_MDI,R_CPAP,R_AO,R_AS,R_SE])
R_S2.add_children([R_A,R_IV,R_METH])
R_SE.add_children([R_S2,R_NS_2])

# composites
GTM_Action = py_trees.composites.Sequence("GeneralTraumaManagement_Action")
GT_S1 = py_trees.composites.Sequence("Sequence_1")
GT_S2 = py_trees.composites.Sequence("Sequence_2")
GT_S3 = py_trees.composites.Sequence("Sequence_3")
GT_S4 = py_trees.composites.Sequence("Sequence_4")
GT_S5 = py_trees.composites.Sequence("Sequence_5")
GT_SE1 = py_trees.composites.Selector("Selector_1")
GT_SE2 = py_trees.composites.Selector("Selector_2")
GT_SE3 = py_trees.composites.Selector("Selector_3")
GT_SE4 = py_trees.composites.Selector("Selector_4")
# behaviours
GT_SPI = SpiRestriction()
GT_Evi = Evisceration()
GT_OCW = OpenChestWound()
GT_Sh = shock()
GT_A = Advanced()
GT_IV = IV()
GT_NAU_1 = Nausea()
GT_NAU_2 = Nausea()
GT_OD_1 = ondansetron()
GT_OD_2 = ondansetron()
GT_IP = IP()
GT_FEN_IV = Fentanyl_IV()
GT_FEN_IN = Fentanyl_IN()
GT_NS_1 = NotStarted()
GT_NS_2 = NotStarted()
GT_NS_3 = NotStarted()
GT_KET = Ketamine()
# tree
GTM_Action.add_children([GT_SPI,GT_SE1,GT_S1])
GT_SE1.add_children([GT_Evi,GT_OCW,GT_NS_1])
GT_S1.add_children([GT_A,GT_Sh,GT_IP,GT_SE2])
GT_SE2.add_children([GT_S2,GT_S3])
GT_S2.add_children([GT_IV,GT_FEN_IV,GT_KET,GT_SE3])
GT_SE3.add_children([GT_S4,GT_NS_2])
GT_S4.add_children([GT_NAU_1,GT_OD_1])
GT_S3.add_children([GT_FEN_IN,GT_SE4])
GT_SE4.add_children([GT_S5,GT_NS_3])
GT_S5.add_children([GT_NAU_2,GT_OD_2])

# chestpain action
# composites
ChestPain_Action = py_trees.composites.Sequence("ChestPain_Action")
CP_S1 = py_trees.composites.Sequence("Sequence_1")
CP_S2 = py_trees.composites.Sequence("Sequence_2")
CP_S3 = py_trees.composites.Sequence("Sequence_3")
CP_S4 = py_trees.composites.Sequence("Sequence_4")
CP_S5 = py_trees.composites.Sequence("Sequence_5")
CP_S6 = py_trees.composites.Sequence("Sequence_6")
CP_S7 = py_trees.composites.Sequence("Sequence_7")
CP_SE0 = py_trees.composites.Selector("Selector_0")
CP_SE1 = py_trees.composites.Selector("Selector_1")
CP_SE2 = py_trees.composites.Selector("Selector_2")
CP_SE3 = py_trees.composites.Selector("Selector_3")
CP_SE4 = py_trees.composites.Selector("Selector_4")
# behaviours
CP_ECG = ECG()
CP_MI = MI()
CP_TRANS = Transport()
CP_AS = Aspirin()
CP_NI = Nitro()
CP_A = Advanced()
CP_IV = IV()
CP_NAU_1 = Nausea()
CP_NAU_2 = Nausea()
CP_NAU_3 = Nausea()
CP_OD_1 = ondansetron()
CP_OD_2 = ondansetron()
CP_OD_3 = ondansetron()
CP_IP = IP()
CP_FEN_IV = Fentanyl_IV()
CP_FEN_IN = Fentanyl_IN()
CP_NS_1 = NotStarted()
CP_NS_2 = NotStarted()
CP_NS_3 = NotStarted()
CP_NS_4 = NotStarted()
# build sub-tree: chestpain action
ChestPain_Action.add_children([CP_ECG,CP_SE0])
CP_SE0.add_children([CP_S1,CP_S2,CP_NS_4])
CP_S1.add_children([CP_MI,CP_TRANS])
CP_S2.add_children([CP_AS,CP_NI,CP_A,CP_SE1,CP_IP,CP_SE2])
CP_SE1.add_children([CP_S3,CP_NS_1])
CP_S3.add_children([CP_NAU_1,CP_OD_1])
CP_SE2.add_children([CP_S4,CP_S6])
CP_S4.add_children([CP_IV,CP_FEN_IV,CP_SE3])
CP_SE3.add_children([CP_S5,CP_NS_2])
CP_S5.add_children([CP_NAU_2,CP_OD_2])
CP_S6.add_children([CP_FEN_IN,CP_SE4])
CP_SE4.add_children([CP_S7,CP_NS_3])
CP_S7.add_children([CP_NAU_3,CP_OD_3])
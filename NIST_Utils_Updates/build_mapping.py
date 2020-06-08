import pandas as pd

# read doc
df = pd.read_excel('/Users/sileshu/Desktop/EMSdata/RAA Data_protocol.xlsx')

impressions = []
chief_complain = []
intermapping = {}
impremapping = {}
for item in df.iterrows():
    # get interventions
    inter = item[1]['Interventions'].strip('{}').split('}{')
    inter = [i.split(':')[-1].strip().lower() for i in inter]
    # filter the cases only have 2 interventions
    if len(inter) <= 2 and 'hospital contact' in inter:
        continue
    # get impressions and CCs
    impression = item[1]['Impression'].strip('{}').split('}{')
    chief_complain = item[1]['ChiefComplaint'].strip('{}').split('}{')
    cc = []
    for i in chief_complain:
        temp = i.split('-')
        temp = [i.strip() for i in temp]
        if temp[0] == 'Cardiac':
            cc.append(temp[1])
        else:
            cc.append(temp[0])
        
    # build mapping between interventions/impressions and protocol
    # keys: interventions or impressions
    # values: a dict whose keys are protocols and values are count numbers
    for inte in inter:
        if inte in intermapping:
            if item[1]['Protocol'] in intermapping[inte]:
                intermapping[inte][item[1]['Protocol']] += 1
            else:
                intermapping[inte][item[1]['Protocol']] = 1
        else:
            intermapping[inte] = {item[1]['Protocol']:1}
            
    for impre in impression:
        if impre in impremapping:
            if item[1]['Protocol'] in impremapping[impre]:
                impremapping[impre][item[1]['Protocol']] += 1
            else:
                impremapping[impre][item[1]['Protocol']] = 1
        else:
            impremapping[impre] = {item[1]['Protocol']:1}
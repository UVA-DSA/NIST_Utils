def annotator(cc, calltype, interventions, impressions):
    '''
    cc: cheif complaint, str
    calltype: calltype, str
    interventions: interventions, list
    impressions: impressions, list, consider the last one
    '''
    res = ''
    cc2protocol = {
     '<Patient Refused Care / AMA>':'General Patient Care',
     'Abdominal Pain':'Abdominal Pain',
     'Allergic Reaction':'Allergic Reaction/Anaphylaxis',
     'Altered Consciousness':'Altered Mental Status',
     'Atraumatic Bleeding Describe Type and Area':'General Trauma Management',
     'Back Pain':'General Pain Management',
     'Behavioral':'Behavioral/Patient Restraint/Acute Phychological Agitation',
     'Burns':'Burns/Thermal',
     'COPD':'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
     'CVA/TIA':'Stroke/TIA',
     'Cardiac Arrest':'BLSCPR',
     'Chest Pain':'Chest Pain',
     'Convulsions/Seizures':'Seizure',
     'Diabetic':'Diabetic/Hypoglycemia',
     'GI Bleed/Problem':'General Trauma Management',
     'General Illness':'General Patient Care',
     'Hallucinations':'Altered Mental Status',
     'Headache':'General Patient Care',
     'Heat/Cold Exposure':'Heat Stroke/Hyperthermia',
     'OB/GYN':'???',
     'Other (MUST add detail note)':'General Patient Care',
     'Pain':'General Pain Management',
     'Palpitations':'Altered Mental Status',
     'Poisoning/Overdose':'Overdose/Poisoning/Toxic Ingestion',
     'Psychiatric Problems':'Behavioral/Patient Restraint/Acute Phychological Agitation',
     'Psychiatric/ Behavioral Problems':'Behavioral/Patient Restraint/Acute Phychological Agitation',
     'Respi':'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
     'Respiratory':'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
     'Respiratory Arrest':'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
     'Seizures/Convulsions':'Seizure',
     'Shock':'BLSCPR',
     'Trauma':'General Trauma Management'}
    calltype2protocol = {
     'Traumatic Injury':'General Trauma Management',
     'Diabetic Problems':'???',
     'Back Pain':'General Pain Management',
     'Fall(s)':'General Trauma Management',
     'Syncope/Unconscious':'Altered Mental Status',
     'Breathing Problems':'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
     'Cardiac/Resp Arrest':'Pulmonary Edema/CHF',
     'Heart Problems':'Ventricular Fibrillation/Pulseless Ventricular Tachycardia',
     'Headache':'General Patient Care',
     'Allergic Reaction':'Allergic Reaction/Anaphylaxis',
     'Assault/Rape':'???',
     'Pregnancy/Childbirth':'???',
     'Seizure/Convulsion':'Seizure',
     'Shooting/Stabbing':'General Trauma Management',
     'Hemorhage/Lacerations':'General Trauma Management',
     'Stroke/CVA':'Stroke/TIA',
     'Abdominal Pain':'Abdominal Pain',
     'Helicopter Landing':'General Trauma Management',
     'MVA':'General Trauma Management',
     'Chest Pain':'Chest Pain',
     'Overdose/Poisoning':'Overdose/Poisoning/Toxic Ingestion',
     'Sick Person':'General Patient Care',
     'Psychiatric/Suicide Attempt':'Behavioral/Patient Restraint/Acute Phychological Agitation',
     'Unknown Problem':'???',
     'Burn(s)':'Burns/Thermal'
    }
    impression2protocol = {u'Abuse of Alcohol - Withdrawal - PCR': u'Alcohol Related Emergencies',
 u'Abuse of Sedative, Hypnotic or Anxiolytic - PCR': u'Overdose/Poisoning/Toxic Ingestion',
 u'Behavioral - Depression - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Behavioral - Violent - PCR': u'Behavioral/Patient Restraint/Acute Phychological Agitation',
 u'Bleeding or Hematoma from Procedure/Medical Device - PCR': u'General Trauma Management',
 u'Burn - Second degree - PCR': u'Burns/Thermal',
 u'CV - Chest Pain - Angina - PCR': u'Chest Pain',
 u'CV - Chest Pain - Myocardial Infarction - PCR': u'Chest Pain',
 u'CV - Chest Pain - Presumed Cardiac - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'CV - Chest Pain - STEMI of Anterior Wall - PCR': u'Chest Pain',
 u'CV - Chest Pain - STEMI of other sites - PCR': u'Chest Pain',
 u'CV - Congestive Heart Failure (CHF) - PCR': u'Pulmonary Edema/CHF',
 u'Environment - Heat Exhaustion - PCR': u'Heat Stroke/Hyperthermia',
 u'Environment - Heatstroke - PCR': u'Heat Stroke/Hyperthermia',
 u'Environment - Poisoning/Drug Ingestion - PCR': u'Overdose/Poisoning/Toxic Ingestion',
 u'Environment - Stings/Venomous Bites - PCR': u'Allergic Reaction/Anaphylaxis',
 u'GI/GU - Abdominal Pain Acute Onset - PCR': u'Chest Pain',
 u'GI/GU - Constipation - PCR': u'Abdominal Pain',
 u'GI/GU - GERD (Reflux) - PCR': u'Chest Pain',
 u'GI/GU - Hematemesis (vomiting blood) - PCR': u'General Trauma Management',
 u'GI/GU - Obesity - PCR': u'Altered Mental Status',
 u'Infectious - Bronchitis - Acute - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Injury - Ankle - PCR': u'General Trauma Management',
 u'Injury - Elbow - PCR': u'General Trauma Management',
 u'Injury - Eye and/or Orbit - PCR': u'General Trauma Management',
 u'Injury - Forearm - PCR': u'General Trauma Management',
 u'Injury - Hip - PCR': u'General Trauma Management',
 u'Injury - Lower leg - PCR': u'General Trauma Management',
 u'Injury - Lung Hemothorax - Traumatic - PCR': u'General Trauma Management',
 u'Injury - Lung Pneumothorax - Traumatic - PCR': u'General Trauma Management',
 u'Injury - Nose - PCR': u'General Trauma Management',
 u'Injury - Pelvis - PCR': u'General Trauma Management',
 u'Injury - Shoulder or Upper Arm - PCR': u'General Trauma Management',
 u'Injury - Thigh (upper leg) - PCR': u'General Trauma Management',
 u'Injury - Thorax (upper chest) - PCR': u'General Trauma Management',
 u'Intracranial - Stroke (CVA) Hemorrhagic - PCR': u'Head Trauma',
 u'Maltreatment - Adult Physical Abuse Suspected - PCR': u'General Trauma Management',
 u'Neuro - Hemiplegia - PCR': u'Stroke/TIA',
 u'Neuro - Seizure - PCR': u'Seizure',
 u'Neuro - Status Epilepticus - PCR': u'Seizure',
 u'Neuro - TIA (transient ischemic attack) - PCR': u'Stroke/TIA',
 u'OB - Spontaneous Abortion (Miscarriage) - PCR': u'General Patient Care',
 u'Respiratory - Asthma Exacerbation - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Respiratory - Bronchospasm Acute Onset - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Respiratory - COPD Exacerbation - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Respiratory - Hemoptysis - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Respiratory - Pneumothorax (Spontaneous) - PCR': u'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway',
 u'Sickle Cell Anemia/Crisis - PCR': u'Altered Mental Status'}
    
    if cc not in cc2protocol:
        res = calltype2protocol[calltype]
    else:
        res = cc2protocol[cc]
    if impressions[-1] in impression2protocol:
        res = impression2protocol[impressions[-1]]
    if 'aspirin' in interventions:
        res = 'Chest Pain'
    if 'nitroglycerin' in interventions:
        res = 'Chest Pain'
    if 'morphine' in interventions:
        res = 'Chest Pain'
    if 'albuterol' in interventions:
        res = 'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway'
    if 'ipratopium (atrovent)' in interventions:
        res = 'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway'
    if 'dexamethasone' in interventions:
        res = 'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway'
    if 'magnesium sulfate' in interventions:
        res = 'Respiratory distress/Asthma/COPD/Pneumonia/Reactive airway'
    if 'glutose' in interventions:
        res = 'Seizure'
    if 'intraosseus' in interventions:
        res = 'Ventricular Fibrillation/Pulseless Ventricular Tachycardia'
    if 'diphenhydramine (benadryl)' in interventions:
        res = 'Allergic Reaction/Anaphylaxis'
    if 'occlusive dressing' in interventions:
        res = 'General Trauma Management'
    if 'oropharyngeal airway insertion' in interventions:
        res = 'Ventricular Fibrillation/Pulseless Ventricular Tachycardia'
    if 'rosc' in interventions:
        res = 'Ventricular Fibrillation/Pulseless Ventricular Tachycardia'
        
    return res

import re
import pandas as pd

ID_LINE = 'TTDDRUID'
NAME_LINE = 'DRUGNAME'
DISEASE_PHASE_LINE = 'INDICATI'
EMPTY_LINE = '\n'
MIN_MATCHING_SCORE = 80

def convert_id_format(df):
    new_ids = list()
    
    for i in df['ID']: 
        id = re.sub("[^0-9a-zA-Z]+", ":", i)
        new_ids.append(id)
    
    df['ID'] = new_ids
    return df

def load_phenotype_matcher():
    matches = pd.read_csv('././data/matched_phenotypes.csv', header = 0, delimiter = ';')
    trusted_matches = matches[matches['score'] > MIN_MATCHING_SCORE]
    
    matched_phenotype_ids = convert_id_format(trusted_matches)
    
    print(f'Loaded {trusted_matches.shape[0]} phenotypes with matching IDs scoring higher than:\n{trusted_matches.head(10)}')
    return trusted_matches
        
def load_drug_disease_entries():
    
    with open('././data/P1-05-Drug_disease.txt') as f:
        entry_lines = f.readlines()[22:]
        
    drug_disease_pairs = list()
    current_drug_disease_pair = dict()
    
    for line in entry_lines:
        
        if line.startswith(ID_LINE):
            found_str = re.search('\t(.*)\n', line)
            current_drug_disease_pair['DRUG_ID'] = found_str.group(1)
        elif line.startswith(NAME_LINE): 
            found_str = re.search('\t(.*)\n', line)
            current_drug_disease_pair['DRUG_NAME'] = found_str.group(1)
        elif line.startswith(DISEASE_PHASE_LINE): 
            found_str1 = re.search('\t(.*)\[', line)
            found_str2 = re.search('\](.*)', line)
            current_drug_disease_pair['DISEASE_NAME'] = found_str1.group(1) 
            current_drug_disease_pair['PHASE'] = found_str2.group(1) 
            
            drug_disease_pairs.append(current_drug_disease_pair.copy())
        elif line.startswith(EMPTY_LINE): 
            current_drug_disease_pair = dict()
            
    return pd.DataFrame.from_dict(drug_disease_pairs, orient='columns')
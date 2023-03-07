
import re
import pandas as pd

ID_LINE = 'TTDDRUID'
NAME_LINE = 'DRUGNAME'
DISEASE_PHASE_LINE = 'INDICATI'
EMPTY_LINE = '\n'

def convert_id_format(df):
    new_ids = list()
    
    for i in df['DISEASE_ID']: 
        id = re.sub("[^0-9a-zA-Z]+", ":", i)
        new_ids.append(id)
    
    df['DISEASE_ID'] = new_ids
    return df

def load_phenotype_matcher():
    """
        Matches originate from submitting a task on https://sorta.molgeniscloud.org/menu/main/sorta?threshold=100
    """
    matches = pd.read_csv('././data/matched_phenotypes.csv', header = 0, delimiter = ';')
    trusted_matches = matches[matches['score'] == 100]
    
    # Change formatting
    trusted_matches['DISEASE_ID'] = trusted_matches['ontologyTermIRI'].str.split('/obo/').str[1]
    trusted_matches['Name'] = trusted_matches['Name'].str.strip()
    matched_phenotype_ids = convert_id_format(trusted_matches)
    
    print(f'Loaded {matched_phenotype_ids.shape[0]} phenotypes with matching IDs scoring 100:\n{matched_phenotype_ids.head(10)}')
    return matched_phenotype_ids

def reformat_disease_name(name):
    new_name = re.sub("[^0-9a-zA-Z]+", " ", name)
    return new_name.lower().strip()

def reformat_disease_names(df):
    reformatted_df = df.copy()
    reformatted_df['DISEASE_NAME'] = df.apply(lambda row: reformat_disease_name(row['DISEASE_NAME']), axis=1)
    return reformatted_df
        
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

def join_disease_name_with_id(names_df, ids_df):
    joined_df = pd.merge(names_df, ids_df, left_on='DISEASE_NAME', right_on='Name', how='left')
    left_outer_joined_df = joined_df[joined_df['DISEASE_ID'].notna()][['DRUG_ID', 'DRUG_NAME', 'DISEASE_ID', 'DISEASE_NAME', 'PHASE']]
    print(f'Total of {left_outer_joined_df.shape[0]} disease names mapped to their IDs:\n{left_outer_joined_df.head(10)}')
    return left_outer_joined_df

def filter_drug_disease_pairs(drug_disease_edges, drug_target_edges):
    print('filter')
    
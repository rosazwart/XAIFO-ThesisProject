import re
import pandas as pd

def convert_id_format(df):
    new_ids = list()
    
    for i in df['DISEASE_ID']: 
        id = re.sub("[^0-9a-zA-Z]+", ":", i)
        new_ids.append(id)
    
    df['DISEASE_ID'] = new_ids
    return df

def load_phenotype_matcher():
    """
        Matches originate from submitting a task on https://sorta.molgeniscloud.org/menu/main/sorta?threshold=100 matching disease name with phenotype ontology terms.
        :return Dataframe with matched phenotype IDs scoring 100
    """
    matches = pd.read_csv('././data/matched_phenotypes.csv', header = 0, delimiter = ';')
    trusted_matches = matches[matches['score'] == 100]
    
    # Change formatting
    formatted_matches = trusted_matches.copy()
    formatted_matches['DISEASE_ID'] = trusted_matches['ontologyTermIRI'].str.split('/obo/').str[1]
    formatted_matches['Name'] = trusted_matches['Name'].str.strip()
    matched_phenotype_ids = convert_id_format(formatted_matches)
    
    print(f'Loaded {matched_phenotype_ids.shape[0]} phenotypes with matching IDs scoring 100:\n{matched_phenotype_ids.head(3)}')
    return matched_phenotype_ids
import pandas as pd
from tqdm import tqdm

from target_id_mapper import db_mapper, IdMapper, DEFAULT_TO_DB

def load_drug_targets():
    """
        Load drug-target interactions entries from tsv file.
        :return: Dataframe containing drug-target interactions
    """
    drug_targets = pd.read_csv('././data/drug.target.interaction.tsv', header=0, sep='\t', index_col=False)
    print(f'Loaded {drug_targets.shape[0]} drug-target interactions:\n{drug_targets.head(3)}')
    return drug_targets

def get_organisms(df):
    """
        Get list of all organism names present in given dataframe.
        :param df: Dataframe containing column `ORGANISM`
    """
    organisms = df['ORGANISM'].unique()
    print(f'There are {organisms.shape[0]} organisms:\n{organisms}')
    return organisms

def get_single_id(id):
    """
        Get from list of IDs split by `|`, one ID.
        :return Single ID value
    """
    split_id = id.split('|')
    if len(split_id) > 1:
        return split_id[0]
    else:
        return id
    
def add_new_ids(df, mapped_ids):
    """
        Add new IDs of entries in given dataframe based on their mappings.
        :param df: Dataframe containing column names `ACCESSION` and `NEW_ID`
        :param mapped_ids: Mappings of IDs containing list of dictionaries with keys `from` and `to`
    """
    for mapped_id in tqdm(mapped_ids):
        accession_id = mapped_id['from']
        new_id = mapped_id['to']
        df.loc[df['ACCESSION'] == accession_id, 'NEW_ID'] = new_id
        
    df = df[df['NEW_ID'].notna()]
    return df

def fetch_id_mappings(entries: pd.DataFrame, map_to_db):
    """
        Get ID mappings of IDs present in given dataframe. Mappings are based on given database to which the IDs need to be mapped.
        :param entries: Dataframe containing column name `ACCESSION`
        :param map_to_db: Name of database to which the given IDs need to be mapped
    """
    if (entries.shape[0] > 0):
        id_entries_to_map = entries.copy()
        id_entries_to_map['ACCESSION'] = entries.apply(lambda row: get_single_id(row['ACCESSION']), axis=1)
        
        mapper = IdMapper(ids_to_map=id_entries_to_map['ACCESSION'].to_list(), to_db=map_to_db)
        if hasattr(mapper, 'results'):
            return mapper.results
        else:
            return []
    else:
        return []

def get_mapped_ids(drug_targets):
    """
        Get mapped IDs for all included databases.
        :param drug_targets: Dataframe that contains column name `ORGANISM` and `ACCESSION`
    """
    all_mapped_id_results = []
    all_taxon_names = list(db_mapper.keys())
    
    for taxon in all_taxon_names:
        relevant_entries = drug_targets[drug_targets['ORGANISM'].str.contains(taxon)]
        id_mappings = fetch_id_mappings(relevant_entries, db_mapper[taxon])
        all_mapped_id_results = all_mapped_id_results + id_mappings

    # Map entity ids of leftover organisms to default database
    other_relevant_entries = drug_targets[~drug_targets['ORGANISM'].isin(all_taxon_names)]
    other_id_mappings = fetch_id_mappings(other_relevant_entries, DEFAULT_TO_DB)
    all_mapped_id_results = all_mapped_id_results + other_id_mappings
                
    return all_mapped_id_results


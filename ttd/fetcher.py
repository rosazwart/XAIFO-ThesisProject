"""
    @description: This module adds drugs and their targets based on information from DrugCentral and TTD to data acquired from the Monarch Initiative.
    @author: Modified version of Jupyter Notebook https://github.com/PPerdomoQ/rare-disease-explainer/blob/c2fe63037c9e6fa680850090790597470cddbb12/Notebook_2.ipynb 
"""

import pandas as pd
import numpy as np
from tqdm import tqdm

import util.constants as constants

from util.common import extract_colvalues, register_info, dataframe2tuplelist
from ttd.idmapper import db_mapper, IdMapper, DEFAULT_TO_DB

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
        
    return df[df['NEW_ID'].notna()]

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

def format_drugtarget_associations(drug_targets: pd.DataFrame):
    """
        Format dataframe with drug target interactions such that it complies with formatting of associations `constants.assoc_tuple_values`.
        :param drug_targets: Dataframe with all drug target interactions
        :return Dataframe with correct column names and order
    """
    print(f'There are {drug_targets.shape[0]} drug-target associations with columns {drug_targets.columns}.')
    drug_targets.drop_duplicates(inplace=True)
    print(f'There are {drug_targets.shape[0]} drug-target associations without duplicates.')
    
    for i, row in drug_targets.iterrows():
        drug_targets.loc[i,'id'] = f'TTD{i}'
        
        drug_targets.loc[i,'subject_id'] = str(row['STRUCT_ID'])
        drug_targets.loc[i,'subject_label'] = row['DRUG_NAME']
        drug_targets.loc[i,'subject_iri'] = np.nan
        drug_targets.loc[i,'subject_category'] = constants.DRUG
        drug_targets.loc[i,'subject_taxon_id'] = np.nan
        drug_targets.loc[i,'subject_taxon_label'] = np.nan
        
        drug_targets.loc[i,'object_id'] = row['TARGET_ID']
        drug_targets.loc[i,'object_label'] = np.nan
        drug_targets.loc[i,'object_iri'] = np.nan
        drug_targets.loc[i,'object_category'] = np.nan
        drug_targets.loc[i,'object_taxon_id'] = np.nan
        drug_targets.loc[i,'object_taxon_label'] = np.nan
        
        drug_targets.loc[i,'relation_id'] = 'CustomRO:TTD'
        drug_targets.loc[i,'relation_label'] = 'targets'
        drug_targets.loc[i,'relation_iri'] = np.nan

    drugtarget_associations_df = drug_targets[list(constants.assoc_tuple_values)]
    drugtarget_associations_df.to_csv(f'{constants.OUTPUT_FOLDER}/ttd_associations.csv', index=None)
    register_info('All TTD associations are saved into ttd_associations.csv')
    
    return dataframe2tuplelist(drugtarget_associations_df) 

def get_drugtarget_associations(gene_nodes: pd.DataFrame):
    """
        Get all drug target interaction associations
        :param gene_nodes: Dataframe containing existing nodes
        :return List of tuples complying with `constants.assoc_tuple_values`
    """
    # Nodes fetched from Monarch Initiative
    gene_ids = extract_colvalues(gene_nodes, 'id')
    register_info(f'A total of {len(gene_ids)} gene IDs has been extracted')
    
    # Data for drug-target interactions
    drug_targets = load_drug_targets()
    # Collect correct target IDs
    all_mapped_ids = get_mapped_ids(drug_targets)
    
    # Create dataframe to hold new IDs
    mapped_drug_targets = drug_targets.copy()
    mapped_drug_targets['NEW_ID'] = np.nan
    mapped_drug_targets = add_new_ids(mapped_drug_targets, all_mapped_ids)
    register_info(f'For a total of {mapped_drug_targets.shape[0]} drug-target interactions, new mapped IDs are found.')
    
    matched_drug_targets = mapped_drug_targets[mapped_drug_targets['NEW_ID'].isin(gene_ids)]
    register_info(f'Retrieved {matched_drug_targets.shape[0]} drug-target interactions with matched gene IDs:\n{matched_drug_targets.head(4)}')
    
    # Prepare dataframe with correct columns/column names
    relevant_matched_drug_targets = matched_drug_targets.rename({'NEW_ID': 'TARGET_ID'}, axis=1)[['DRUG_NAME', 'STRUCT_ID', 'TARGET_ID']]

    drugtargets_associations = format_drugtarget_associations(relevant_matched_drug_targets)
    return drugtargets_associations
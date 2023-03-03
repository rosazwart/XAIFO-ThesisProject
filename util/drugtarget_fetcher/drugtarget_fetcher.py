"""
    @description: This module adds drugs and their targets based on information from DrugCentral and TTD to data acquired from the Monarch Initiative.
    @author: Modified version of Jupyter Notebook https://github.com/PPerdomoQ/rare-disease-explainer/blob/c2fe63037c9e6fa680850090790597470cddbb12/Notebook_2.ipynb 
"""

import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

from id_mapper import db_mapper, IdMapper, DEFAULT_TO_DB

GENE = 'gene'

def load_nodes():
    nodes = pd.read_csv('././runs/run4/monarch_nodes.csv', header=0)
    print(f'Loaded {nodes.shape[0]} nodes:\n{nodes.head(3)}')
    return nodes

def extract_gene_ids(nodes: pd.DataFrame):
    gene_nodes = nodes.loc[nodes['semantic'] == GENE]
    gene_ids = gene_nodes['id'].to_list()
    print(f'Collected {len(gene_ids)} gene ids')
    return gene_ids

def get_prefix(gene_id):
    return gene_id.split(':')[0]

def retrieve_gene_prefixes(genes: pd.DataFrame):
    prefix_genes = genes.copy()
    prefix_genes['id'] = genes.apply(lambda row: get_prefix(row['id']), axis=1)
    
    unique_prefixes = prefix_genes['id'].unique()
    for prefix in unique_prefixes:
        relevant_entries = prefix_genes.loc[prefix_genes['id'] == prefix]
        taxons = relevant_entries['taxon_id'].unique()
        print(f'Gene ID prefix {prefix} is used for taxons {taxons}')

def load_drug_targets():
    drug_targets = pd.read_csv('././data/drug.target.interaction.tsv', header=0, sep='\t', index_col=0)
    print(f'Loaded {drug_targets.shape[0]} drug-target interactions:\n{drug_targets.head(3)}')
    return drug_targets

def get_organisms(df):
    organisms = df['ORGANISM'].unique()
    print(f'There are {organisms.shape[0]} organisms:\n{organisms}')
    return organisms

def get_single_id(id):
    split_id = id.split('|')
    if len(split_id) > 1:
        return split_id[0]
    else:
        return id
    
def add_new_ids(df, mapped_ids):
    for mapped_id in tqdm(mapped_ids):
        accession_id = mapped_id['from']
        new_id = mapped_id['to']
        df.loc[df['ACCESSION'] == accession_id, 'NEW_ID'] = new_id
        
    df = df[df['NEW_ID'].notna()]
    return df

def fetch_id_mappings(entries: pd.DataFrame, map_to_db):
    if (entries.shape[0] > 0):
        id_entries_to_map = entries.copy()
        id_entries_to_map['ACCESSION'] = entries.apply(lambda row: get_single_id(row['ACCESSION']), axis=1)
        
        mapper = IdMapper(ids_to_map=id_entries_to_map, to_db=map_to_db)
        if hasattr(mapper, 'results'):
            return mapper.results
        else:
            return []
    else:
        return []

def get_mapped_ids(drug_targets):
    all_mapped_id_results = []
    all_taxon_names = list(db_mapper.keys())
    
    for taxon in all_taxon_names:
        relevant_entries = drug_targets[drug_targets['ORGANISM'].str.contains(taxon)]
        id_mappings = fetch_id_mappings(relevant_entries, db_mapper[taxon])
        all_mapped_id_results = all_mapped_id_results + id_mappings

    relevant_entries = drug_targets[~drug_targets['ORGANISM'].isin(all_taxon_names)]
    id_mappings = fetch_id_mappings(relevant_entries, DEFAULT_TO_DB)
    all_mapped_id_results = all_mapped_id_results + id_mappings
                
    return all_mapped_id_results

if __name__ == "__main__":
    nodes = load_nodes()
    gene_ids = extract_gene_ids(nodes)
    
    drug_targets = load_drug_targets()
    
    mapped_drug_targets = drug_targets.copy()
    mapped_drug_targets['NEW_ID'] = np.nan
    
    all_mapped_ids = get_mapped_ids(drug_targets)
    
    mapped_drug_targets = add_new_ids(mapped_drug_targets, all_mapped_ids)
    print(mapped_drug_targets.shape[0])
    
    matched_drug_targets = mapped_drug_targets[mapped_drug_targets['NEW_ID'].isin(gene_ids)]
    print(f'Retrieved {matched_drug_targets.shape[0]} drug-target interactions with matched gene IDs:\n{matched_drug_targets.head(4)}')
    
    
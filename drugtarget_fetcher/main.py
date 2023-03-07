"""
    @description: This module adds drugs and their targets based on information from DrugCentral and TTD to data acquired from the Monarch Initiative.
    @author: Modified version of Jupyter Notebook https://github.com/PPerdomoQ/rare-disease-explainer/blob/c2fe63037c9e6fa680850090790597470cddbb12/Notebook_2.ipynb 
"""

import pandas as pd
import numpy as np
import os

import drugtarget_fetcher as drugtarget_fetcher

GENE = 'gene'

INPUT_FOLDER = 'data'
OUTPUT_FOLDER = 'output'

def load_monarch_nodes():
    data_path = os.path.join(OUTPUT_FOLDER, 'monarch_nodes.csv')
    nodes = pd.read_csv(data_path, header=0)
    print(f'Loaded {nodes.shape[0]} nodes:\n{nodes.head(3)}')
    return nodes

def extract_gene_ids(nodes: pd.DataFrame):
    """
        Retrieve list of all gene IDs given a dataframe with nodes.
        :param nodes: Dataframe containing nodes
        :return List of gene IDs
    """
    gene_nodes = nodes.loc[nodes['semantic'] == GENE]
    gene_ids = gene_nodes['id'].to_list()
    print(f'Collected {len(gene_ids)} gene ids')
    return gene_ids

def get_prefix(gene_id):
    """
        Given a gene ID, extract prefix followed by `:`.
        :param gene_id: Gene ID containing `:` splitting prefix with suffix
        :return: Prefix of given gene ID
    """
    return gene_id.split(':')[0]

def retrieve_gene_prefixes(genes: pd.DataFrame):
    """
        List all prefix values present in given dataframe containing genes.
        :param genes: Dataframe containing genes that needs to have column names `id`, `taxon_id`
    """
    prefix_genes = genes.copy()
    prefix_genes['id'] = genes.apply(lambda row: get_prefix(row['id']), axis=1)
    
    unique_prefixes = prefix_genes['id'].unique()
    for prefix in unique_prefixes:
        relevant_entries = prefix_genes.loc[prefix_genes['id'] == prefix]
        taxons = relevant_entries['taxon_id'].unique()
        print(f'Gene ID prefix {prefix} is used for taxons {taxons}')

if __name__ == "__main__":
    # Nodes fetched Monarch Initiative
    nodes = load_monarch_nodes()
    gene_ids = extract_gene_ids(nodes)
    
    # Data for drug-target interactions
    drug_targets = drugtarget_fetcher.load_drug_targets()
    
    # Create dataframe to hold new IDs
    mapped_drug_targets = drug_targets.copy()
    mapped_drug_targets['NEW_ID'] = np.nan
    
    all_mapped_ids = drugtarget_fetcher.get_mapped_ids(drug_targets)
    
    mapped_drug_targets = drugtarget_fetcher.add_new_ids(mapped_drug_targets, all_mapped_ids)
    print(f'For a total of {mapped_drug_targets.shape[0]} drug-target interactions, new mapped IDs are found.')
    
    matched_drug_targets = mapped_drug_targets[mapped_drug_targets['NEW_ID'].isin(gene_ids)]
    print(f'Retrieved {matched_drug_targets.shape[0]} drug-target interactions with matched gene IDs:\n{matched_drug_targets.head(4)}')
    
    relevant_matched_drug_targets = matched_drug_targets.rename({'NEW_ID': 'TARGET_ID'}, axis=1)[['DRUG_NAME', 'STRUCT_ID', 'TARGET_ID']]
    
    relevant_matched_drug_targets.to_csv('output/drug_target_edges.csv', index=False, encoding = 'utf-8-sig')
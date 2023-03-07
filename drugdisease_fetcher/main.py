import os
import pandas as pd

import drugdisease_fetcher as drugdisease_fetcher

INPUT_FOLDER = 'data'
OUTPUT_FOLDER = 'output'

DISEASE = 'disease'
PHENOTYPE = 'phenotype'

def load_monarch_nodes():
    data_path = os.path.join(OUTPUT_FOLDER, 'monarch_nodes.csv')
    nodes = pd.read_csv(data_path, header=0)
    print(f'Loaded {nodes.shape[0]} nodes:\n{nodes.head(3)}')
    return nodes

def load_drug_target_edges():
    data_path = os.path.join(OUTPUT_FOLDER, 'drug_target_edges.csv')
    edges = pd.read_csv(data_path, header=0)
    print(f'Loaded {edges.shape[0]} edges:\n{edges.head(3)}')
    return edges

def get_all_drugs(df):
    all_drugs = drug_target_edges['DRUG_NAME'].unique()
    print(f'There are {len(all_drugs)} unique drug names:\n{all_drugs[0:3]}')
    return all_drugs

def get_all_diseases(df):
    all_diseases = df.loc[df['semantic'] == DISEASE]
    return all_diseases

def get_all_phenotypes(df):
    all_phenotypes = df.loc[df['semantic'] == DISEASE]
    return all_phenotypes

if __name__ == "__main__":
    drug_disease_pairs = drugdisease_fetcher.load_drug_disease_entries()
    print(drug_disease_pairs.head(10))
    
    phenotype_matches = drugdisease_fetcher.load_phenotype_matcher()
    
    monarch_nodes = load_monarch_nodes()
    drug_target_edges = load_drug_target_edges()
    
    drug_disease_edges = drugdisease_fetcher.reformat_disease_names(drug_disease_pairs)
    drug_disease_edges = drugdisease_fetcher.join_disease_name_with_id(drug_disease_edges, phenotype_matches)
    
    print(get_all_diseases(monarch_nodes)['label'].unique())
    print(get_all_phenotypes(monarch_nodes))
    #filtered_drug_disease_edges = drugdisease_fetcher.filter_drug_disease_pairs(drug_disease_edges, drug_target_edges, monarch_nodes)
    
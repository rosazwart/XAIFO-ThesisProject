import pandas as pd

import util.constants as constants

from util.loaders import get_input_data_path, load_monarch_associations_from_csv
from builder.kg import KnowledgeGraph

import analyzer.graphstructure as graphstructure
import monarch.fetcher as monarch_fetcher
import ttd.fetcher as ttd_fetcher
import drugcentral.fetcher as drugcentral_fetcher
import builder.cypherqueries as cypher_querybuilder

def analyze_prev_data():
    data_path = get_input_data_path('graph_nodes_v2022-01-11.csv')
    nodes = pd.read_csv(data_path)
    print('Loaded nodes with attributes:', nodes.columns.values)
    
    data_path = get_input_data_path('graph_edges_v2022-01-11.csv')
    edges = pd.read_csv(data_path)
    print('Loaded edges with attributes:', edges.columns.values)
    
    edge_colmapping = {
        'relations': 'property_label',
        'subject': 'subject_id',
        'object': 'object_id'
    }
    
    node_colmapping = {
        'node_id': 'id',
        'semantics': 'semantic_groups'
    }
    
    graphstructure.getConcepts(nodes, node_colmapping)
    graphstructure.getRelations(edges, edge_colmapping)
    graphstructure.getConnectionSummary(edges, nodes, 
                                        edge_colmapping, node_colmapping,
                                        'prev_concepts.png', 'prev_triplets.csv')

def analyze_new_data(kg: KnowledgeGraph):
    edges, nodes = kg.generate_dataframes()
    
    edge_colmapping = {
        'relations': 'relation_label',
        'subject': 'subject',
        'object': 'object'
    }
    
    node_colmapping = {
        'node_id': 'id',
        'semantics': 'semantic'
    }
    
    kg.analyze_graph()
    graphstructure.getConcepts(nodes, node_colmapping)
    graphstructure.getRelations(edges, edge_colmapping)
    graphstructure.getConnectionSummary(edges, nodes, 
                                        edge_colmapping, node_colmapping,
                                        'concepts.png', 'triplets.csv')


def build_kg(load_csv: bool = False):
    if load_csv:
        monarch_associations = load_monarch_associations_from_csv()
    else:
        nodes_list = [
            'MONDO:0010679',
            'HGNC:2928'
        ]
        monarch_associations = monarch_fetcher.get_monarch_associations(nodes_list)
        
    kg = KnowledgeGraph(monarch_associations)
    
    gene_nodes = kg.get_extracted_nodes([constants.GENE])
    ttd_associations = ttd_fetcher.get_drugtarget_associations(gene_nodes)
    
    kg.add_edges_and_nodes(ttd_associations)
    
    drug_nodes = kg.get_extracted_nodes([constants.DRUG])
    diso_pheno_nodes = kg.get_extracted_nodes([constants.DISEASE, constants.PHENOTYPE])
    drugcentral_associations = drugcentral_fetcher.get_drugdisease_associations(drug_nodes, diso_pheno_nodes)
    
    kg.add_edges_and_nodes(drugcentral_associations)
    
    analyze_new_data(kg)
    
    kg_edges, kg_nodes = kg.generate_dataframes()
    cypher_querybuilder.build_queries(kg_nodes, kg_edges, True)
    
    # TODO: still some duplicates for substance that treats and targets?

if __name__ == "__main__":
    build_kg(load_csv=True)
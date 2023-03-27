import pandas as pd

import util.constants as constants

from util.loaders import load_associations_from_csv
from builder.kg import KnowledgeGraph

import analyzer.graphstructure as graphstructure
import monarch.fetcher as monarch_fetcher
import ttd.fetcher as ttd_fetcher
import drugcentral.fetcher as drugcentral_fetcher
import builder.cypherqueries as cypher_querybuilder
import ols.fetcher as ols_fetcher

def analyze_data_from_kg(kg: KnowledgeGraph, concepts_filename, triplets_filename):
    edges, nodes = kg.generate_dataframes()
    
    edge_colmapping = {
        'relations': 'relation_label',
        'relationids': 'relation_id',
        'subject': 'subject',
        'object': 'object'
    }
    
    node_colmapping = {
        'node_id': 'id',
        'semantics': 'semantic'
    }
    
    kg.analyze_graph()
    graphstructure.getConcepts(nodes, node_colmapping)
    relations_df = graphstructure.getRelations(edges, edge_colmapping)
    graphstructure.getConnectionSummary(edges, nodes, 
                                        edge_colmapping, node_colmapping,
                                        concepts_filename, triplets_filename)
    
    ols_fetcher.analyze_ontology_relations(relations_df)
    
def build_prev_kg():
    monarch_associations = load_associations_from_csv('prev_monarch_associations.csv')
    ttd_associations = load_associations_from_csv('prev_ttd_associations.csv')
    drugcentral_associations = load_associations_from_csv('prev_drugcentral_associations.csv')
    
    kg = KnowledgeGraph(monarch_associations)
    kg.add_edges_and_nodes(ttd_associations)
    kg.add_edges_and_nodes(drugcentral_associations)
    
    analyze_data_from_kg(kg, 'prev_concepts.png', 'prev_triplets.csv')

def build_kg(load_csv: bool = False):
    if load_csv:
        monarch_associations = load_associations_from_csv('monarch_associations.csv')
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
    
    analyze_data_from_kg(kg, 'concepts.png', 'triplets.csv')
    
    kg_edges, kg_nodes = kg.generate_dataframes()
    cypher_querybuilder.build_queries(kg_nodes, kg_edges, True)
    
    # TODO: still some duplicates for substance that treats and targets?

if __name__ == "__main__":
    #build_kg(load_csv=True)
    build_prev_kg()
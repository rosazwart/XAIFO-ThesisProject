import util.constants as constants

from util.common import today
from util.loaders import load_associations_from_csv, create_output_folder
from builder.kg import AssocKnowledgeGraph, RestructuredKnowledgeGraph

import analyzer.graphstructure as graphstructure
import monarch.fetcher as monarch_fetcher
import ttd.fetcher as ttd_fetcher
import drugcentral.fetcher as drugcentral_fetcher
import builder.cypherqueries as cypher_querybuilder
import ols.fetcher as ols_fetcher

from typing import Union

def analyze_data_from_kg(kg: Union[AssocKnowledgeGraph, RestructuredKnowledgeGraph], concepts_filename, triplets_filename, ontologies: bool = False):
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
    
    if ontologies:
        ols_fetcher.analyze_ontology_relations(relations_df)
    
def build_prev_kg():
    file_date = input('Enter date of files (monarch, ttd, drugcentral) in format yyyy-mm-dd:')
    
    monarch_associations = load_associations_from_csv(f'prev_monarch_associations_{file_date}.csv')
    ttd_associations = load_associations_from_csv(f'prev_ttd_associations_{file_date}.csv')
    drugcentral_associations = load_associations_from_csv(f'prev_drugcentral_associations_{file_date}.csv')
    
    kg = AssocKnowledgeGraph(monarch_associations)
    kg.add_edges_and_nodes(ttd_associations)
    kg.add_edges_and_nodes(drugcentral_associations)
    
    analyze_data_from_kg(kg, 'prev_concepts.png', 'prev_triplets.csv')
    
    kg.save_graph('prev_kg')
    

def build_kg(load_csv: bool = False):
    # --- Add associations from Monarch Initiative ---
    
    if load_csv:
        file_date = input('Enter date of file with all monarch associations in format yyyy-mm-dd:')
        monarch_associations = load_associations_from_csv(f'monarch_associations_{file_date}.csv')
    else:
        nodes_list = [
            'MONDO:0007739',    # Huntington disease
            'HGNC:4851' # HTT, causal gene Huntington disease
        ]
        monarch_associations = monarch_fetcher.get_monarch_associations(nodes_list)
        
    kg = AssocKnowledgeGraph(monarch_associations)
    
    # --- Add associations from TTD ---
    
    gene_nodes = kg.get_extracted_nodes([constants.GENE])
    ttd_associations = ttd_fetcher.get_drugtarget_associations(gene_nodes)
    
    kg.add_edges_and_nodes(ttd_associations)
    
    # --- Add associations from DrugCentral ---
    
    drug_nodes = kg.get_extracted_nodes([constants.DRUG])
    diso_pheno_nodes = kg.get_extracted_nodes([constants.DISEASE, constants.PHENOTYPE])
    drugcentral_associations = drugcentral_fetcher.get_drugdisease_associations(drug_nodes, diso_pheno_nodes)
    
    kg.add_edges_and_nodes(drugcentral_associations)
    
    # Initial knowledge graph
    analyze_data_from_kg(kg, 'concepts.png', 'triplets.csv')
    
    kg_edges, kg_nodes = kg.generate_dataframes()
    cypher_querybuilder.build_queries(kg_nodes, kg_edges, True)
    
    # Restructured knowledge graph
    new_kg = RestructuredKnowledgeGraph(kg)
    analyze_data_from_kg(new_kg, 'new_concepts.png', 'new_triplets.csv')
    
    new_kg_edges, new_kg_nodes = new_kg.generate_dataframes()
    cypher_querybuilder.build_queries(new_kg_nodes, new_kg_edges, True)
    
    new_kg.save_graph('new_kg')

if __name__ == "__main__":
    create_output_folder()
    
    kg_mode = input('Enter which KG needs to be built (choose 1 for original, choose 2 for restructured):')
    
    assert kg_mode == '1' or kg_mode == '2'
    
    if kg_mode == '1':
        build_prev_kg()
    else:
        from_csv = input('Load already fetched nodes and edges from Monarch Initiative stored in csv file? (choose yes or no):')
        
        assert from_csv == 'yes' or from_csv == 'no'
        
        if from_csv == 'yes':
            load_csv = True
        else:
            load_csv = False
        
        build_kg(load_csv=load_csv)

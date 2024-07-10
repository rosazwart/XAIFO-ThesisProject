import util.constants as constants
from util.loaders import load_associations_from_csv, create_output_folder
from builder.kg import AssocKnowledgeGraph, RestructuredKnowledgeGraph

import analyzer.graphstructure as graphstructure
import ols.fetcher as ols_fetcher
import ttd.fetcher as ttd_fetcher
import drugcentral.fetcher as drugcentral_fetcher

from typing import Union

FILENAME = 'hd_monarch_associations_2024-06-24.csv'

def analyze_kg(kg: Union[AssocKnowledgeGraph, RestructuredKnowledgeGraph], concepts_filename, triplets_filename, ontologies: bool = False):
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
    """
    """
    monarch_assoc = load_associations_from_csv('prev_hd_monarch_associations_2024-06-24.csv')
    ttd_assoc = load_associations_from_csv('prev_hd_ttd_associations_2024-07-09.csv')
    drugcentral_assoc = load_associations_from_csv('prev_hd_drugcentral_associations_2024-07-09.csv')

    kg = AssocKnowledgeGraph(monarch_assoc)
    kg.add_edges_and_nodes(ttd_assoc)
    kg.add_edges_and_nodes(drugcentral_assoc)

    analyze_kg(kg, 'prev_hd_concepts.png', 'prev_hd_triplets.csv')

    kg.save_graph(filename_prefix='prev_hd_kg')

def build_restr_kg():
    """
    """
    monarch_assoc = load_associations_from_csv('hd_monarch_associations_2024-06-24.csv')

    kg = AssocKnowledgeGraph(monarch_assoc)

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
    analyze_kg(kg, 'all_hd_concepts.png', 'all_hd_triplets.csv')

    # Restructuring
    restr_kg = RestructuredKnowledgeGraph(kg)
    analyze_kg(restr_kg, 'restr_hd_concepts.png', 'restr_hd_triplets.csv')

    restr_kg.save_graph('restr_hd_kg')

if __name__ == "__main__":
    create_output_folder()

    kg_mode = input('Enter which KG needs to be built (choose 1 for original, choose 2 for restructured):')
    assert kg_mode == '1' or kg_mode == '2'

    if kg_mode == '1':
        build_prev_kg()
    else:
        build_restr_kg()
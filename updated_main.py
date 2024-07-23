import util.constants as constants
from util.loaders import load_associations_from_csv, create_output_folder, OUTPUT_FOLDER
from builder.kg import AssocKnowledgeGraph, RestructuredKnowledgeGraph

import analyzer.graphstructure as graphstructure
import ols.fetcher as ols_fetcher
import ttd.fetcher as ttd_fetcher
import drugcentral.fetcher as drugcentral_fetcher

from typing import Union

DISEASE_PREFIX = 'hd'
FILENAME = f'{DISEASE_PREFIX}_monarch_associations_2024-06-24.csv'

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
    graphstructure.get_concepts(nodes, node_colmapping)
    relations_df = graphstructure.get_relations(edges, edge_colmapping)
    graphstructure.get_connection_summary(edges, nodes, edge_colmapping, node_colmapping, concepts_filename, triplets_filename, DISEASE_PREFIX)
    
    if ontologies:
        ols_fetcher.analyze_ontology_relations(relations_df)

def build_prev_kg():
    """
    """
    monarch_assoc = load_associations_from_csv(f'prev_{DISEASE_PREFIX}_monarch_associations_2024-07-18.csv', foldernames=[OUTPUT_FOLDER, DISEASE_PREFIX])
    ttd_assoc = load_associations_from_csv(f'prev_{DISEASE_PREFIX}_ttd_associations_2024-07-19.csv', foldernames=[OUTPUT_FOLDER, DISEASE_PREFIX])
    drugcentral_assoc = load_associations_from_csv(f'prev_{DISEASE_PREFIX}_drugcentral_associations_2024-07-19.csv', foldernames=[OUTPUT_FOLDER, DISEASE_PREFIX])

    kg = AssocKnowledgeGraph(monarch_assoc)
    kg.add_edges_and_nodes(ttd_assoc)
    kg.add_edges_and_nodes(drugcentral_assoc)

    analyze_kg(kg, f'prev_{DISEASE_PREFIX}_concepts.png', f'prev_{DISEASE_PREFIX}_triplets.csv')

    kg.save_graph(DISEASE_PREFIX, f'prev_{DISEASE_PREFIX}_kg')

def build_restr_kg():
    """
    """
    monarch_assoc = load_associations_from_csv(FILENAME, foldernames=['localfetcher', OUTPUT_FOLDER])

    kg = AssocKnowledgeGraph(monarch_assoc)

    # --- Add associations from TTD ---
    
    gene_nodes = kg.get_extracted_nodes([]) # constants.GENE
    ttd_associations = ttd_fetcher.get_drugtarget_associations(gene_nodes, disease_prefix=DISEASE_PREFIX)
    
    kg.add_edges_and_nodes(ttd_associations)
    print(f'Added {len(ttd_associations)} drug-target associations')

    # --- Add associations from DrugCentral ---
    
    drug_nodes = kg.get_extracted_nodes([constants.DRUG])
    diso_pheno_nodes = kg.get_extracted_nodes([constants.DISEASE, constants.PHENOTYPE])
    drugcentral_associations = drugcentral_fetcher.get_drugdisease_associations(drug_nodes, diso_pheno_nodes)
    
    kg.add_edges_and_nodes(drugcentral_associations)
    print(f'Added {len(drugcentral_associations)} drug-phenotype/disease associations')

    # Initial knowledge graph
    analyze_kg(kg, f'all_{DISEASE_PREFIX}_concepts.png', f'all_{DISEASE_PREFIX}_triplets.csv')

    # Restructuring
    restr_kg = RestructuredKnowledgeGraph(kg)
    analyze_kg(restr_kg, f'restr_{DISEASE_PREFIX}_concepts.png', f'restr_{DISEASE_PREFIX}_triplets.csv')

    restr_kg.save_graph(DISEASE_PREFIX, f'restr_{DISEASE_PREFIX}_kg')

if __name__ == "__main__":
    create_output_folder(subfoldername=DISEASE_PREFIX)

    kg_mode = input('Enter which KG needs to be built (choose 1 for original, choose 2 for restructured):')
    assert kg_mode == '1' or kg_mode == '2'

    if kg_mode == '1':
        build_prev_kg()
    else:
        build_restr_kg()
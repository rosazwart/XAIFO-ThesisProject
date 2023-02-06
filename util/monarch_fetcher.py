"""
Sources: 
    - https://hynek.me/articles/hashes-and-equality/
"""

import requests

class Node:
    def __init__(self, response_dict: dict, node_role: str):
        self.id = response_dict[node_role]['id']
        self.semantic_groups = response_dict[node_role]['category']
        self.label = response_dict[node_role]['label']
        self.iri = response_dict[node_role]['iri']
        self.taxon = response_dict[node_role]['taxon']
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
class Edge:
    def __init__(self, response_dict: dict):
        self.id = response_dict['id']
        self.subject = response_dict['subject']['id']
        self.object = response_dict['object']['id']
        self.relation = {
            'id': response_dict['relation']['id'],
            'iri': response_dict['relation']['iri'],
            'label': response_dict['relation']['label']
        }
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)

class GraphCreator:
    def __init__(self, all_associations: list):
        self.all_edges = set()
        self.all_nodes = set()
        
        self.generate_edges_and_nodes(all_associations)
        
        all_category_pairs = list(set([node.semantic_groups[0] for node in self.all_nodes]))
        print(f'The graph contains {len(all_category_pairs)} different semantic groups: {all_category_pairs}')
        
        print(f'For the graph, a total of {len(self.all_edges)} edges and {len(self.all_nodes)} nodes have been generated.')
        
    def find_relation_labels(self, substring_relation_label):
        all_relations = list(set([edge.relation['label'] for edge in self.all_edges if (edge.relation['label'] and substring_relation_label in edge.relation['label'])]))
        print(f'All  with substring "{substring_relation_label}": {all_relations}')
    
    def generate_edges_and_nodes(self, associations: dict):
        for association in associations:
            self.all_edges.add(Edge(association))
            self.all_nodes.add(Node(association, 'subject'))
            self.all_nodes.add(Node(association, 'object'))
            
    def get_filtered_nodes(self, extract_semantic_groups: list):
        filtered_nodes = set()
        
        for node in self.all_nodes:
            intersection = [semantic_group for semantic_group in node.semantic_groups if semantic_group in extract_semantic_groups]
            if (len(intersection)):
                filtered_nodes.add(node)
        
        print(f'Extracted a total of {len(filtered_nodes)} nodes that belong to at least one of {extract_semantic_groups}')
        return filtered_nodes
        

class MonarchFetcher:
    def __init__(self):
        self.base_url = 'https://api.monarchinitiative.org/api'
        
        self.relation_ids = {
            'ortholog genes': ['RO:HOM0000017', 'RO:HOM0000020']
        }
        
    def get_from_to_associations(self, node: str, max_rows: int = 2000):
        """
        Get all out and in edges from given node. 
        :param node: identifier of node
        :return: responses of retrieving out and in associations, respectively
        """
        params = {
            'unselect_evidence': True,
            'rows': max_rows
        }
        
        response_from = requests.get(f'{self.base_url}/association/from/{node}', params=params)
        response_to = requests.get(f'{self.base_url}/association/to/{node}', params=params)
        
        return response_from.json(), response_to.json()
    
    def get_filtered_associations_on_entities(self, all_associations: list, include_semantic_groups: list):
        """
        """
        filtered_associations = list()

        for association in all_associations:
            subject_intersection = [semantic_group for semantic_group in association['subject']['category'] if semantic_group in include_semantic_groups]
            object_intersection = [semantic_group for semantic_group in association['object']['category'] if semantic_group in include_semantic_groups]
            
            if (len(subject_intersection) or len(object_intersection)):
                filtered_associations.append(association)
                
        return filtered_associations
    
    def get_filtered_associations_on_relations(self, all_associations, include_relation_ids_group):
        """
        Get all relations that comply with given relations.
        :param all_associations: list of associations
        :return: filtered association list
        """
        filtered_associations = list()
        
        for association in all_associations:
            if (association['relation']['id'] in self.relation_ids[include_relation_ids_group]):
                filtered_associations.append(association)
                
        return filtered_associations
    
    def unpack_response(self, response_values):
        unpacked_associations = list()
        
        if ('associations' in response_values.keys()):   
            for response in response_values['associations']:
                unpacked_associations.append(response)
                
        return unpacked_associations
        
    def get_neighbour_associations(self, id_list):
        """ 
        Return the first layer of neighbours from a list of node identifiers.
        :param id_list: list of entities represented by their identifiers
        :return: list of direct neighbours
        """
        
        all_seed_nodes = set(id_list)
        all_associations = []
        
        for seed_node in all_seed_nodes:
            response_assoc_out, response_assoc_in = self.get_from_to_associations(seed_node)
            # print(f"For seed {seed_node}, {len(response_assoc_out['associations'])} 'from seed' associations and {len(response_assoc_in['associations'])} 'to seed' associations have been found.")
            
            # actual associations are stored inside response dictionary, so unpack these
            all_associations = all_associations + self.unpack_response(response_assoc_out) + self.unpack_response(response_assoc_in)
            
        return all_associations
    
    def get_seed_first_neighbour_associations(self, id_list: list):
        """
            Get a list of all associations with all first neighbours of given seeds.
            :param id_list: list of entities represented by their identifiers
            :return: object with nodes and edges 
        """
        
        # Retrieve the first layer of neighbours
        direct_neighbours_associations = self.get_neighbour_associations(id_list)
        print(f'{len(direct_neighbours_associations)} directly neighbouring associations of seeds')
        
        return direct_neighbours_associations
    
    def get_neighbour_ids(self, id_list: list, associations: list, include_semantic_groups: list):
        ortholog_ids = set()
        
        for association in associations:
            subject_node_id = association['subject']['id']
            object_node_id = association['object']['id']
            
            subject_intersection = [semantic_group for semantic_group in association['subject']['category'] if semantic_group in include_semantic_groups]
            object_intersection = [semantic_group for semantic_group in association['object']['category'] if semantic_group in include_semantic_groups]
            
            if not(subject_node_id in id_list) and len(subject_intersection):
                ortholog_ids.add(subject_node_id)
            
            if not(object_node_id in id_list) and len(object_intersection):
                ortholog_ids.add(object_node_id)
            
        return ortholog_ids
        
    def get_orthopheno_associations(self, id_list: list, depth: int):
        """
        :param id_list: list of entities represented by their identifiers
        """
        
        seed_list = id_list
        all_ortho_pheno_associations = []
        
        for d in range(depth):   
            print('At depth', d+1)
            
            # Retrieve the first layer of neighbours
            direct_neighbours_associations = self.get_neighbour_associations(seed_list)
            print(f'{len(direct_neighbours_associations)} directly neighbouring associations of seeds')
            
            # Filter to only include associations related to orthology
            filtered_associations = self.get_filtered_associations_on_relations(direct_neighbours_associations, 'ortholog genes')
            
            # Retrieve all orthologs of genes included in given list of ids
            ortholog_id_list = self.get_neighbour_ids(seed_list, filtered_associations, ['gene'])
            print(f'{len(ortholog_id_list)} orthologous genes of the given seeds')
            
            # Retrieve the first layer of neighbours of orthologs
            direct_neighbours_orthologs_associations = self.get_neighbour_associations(ortholog_id_list);
            print(f'{len(direct_neighbours_orthologs_associations)} directly neighbouring associations of orthologs')
            
            # Filter to only include associations related to phenotype
            filtered_orthologs_associations = self.get_filtered_associations_on_entities(direct_neighbours_orthologs_associations, ['phenotype'])
            print(f'{len(filtered_orthologs_associations)} phenotype associations of orthologs')
            
            all_ortho_pheno_associations = all_ortho_pheno_associations + filtered_orthologs_associations
            
            
            # Get direct neighbours of seeds
            neighbour_id_list = self.get_neighbour_ids(seed_list, direct_neighbours_associations, ['gene'])
            print(f'{len(neighbour_id_list)} direct neighbours of seeds being a gene')
            seed_list = neighbour_id_list
        
        return all_ortho_pheno_associations
    
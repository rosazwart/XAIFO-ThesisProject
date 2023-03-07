from util.common import register_info

import util.constants as constants

import pandas as pd

class Node:
    """
        Initialize nodes using this class, carrying information about the id of the entity,
        the semantic groups that are associated with the entity, the label of the entity as well as
        the iri link. The taxon attribute is used to specify whether the entity belongs to a certain taxon
        relevant to GENE entities.
        :param assoc_tuple: tuple of information about association
    """
    def __init__(self, assoc_tuple: tuple, node_role: str):
        self.id = assoc_tuple[constants.assoc_tuple_values.index(f'{node_role}_id')]
        self.semantic_groups = assoc_tuple[constants.assoc_tuple_values.index(f'{node_role}_category')]
        self.label = assoc_tuple[constants.assoc_tuple_values.index(f'{node_role}_label')]
        self.iri = assoc_tuple[constants.assoc_tuple_values.index(f'{node_role}_iri')]
        self.taxon = assoc_tuple[constants.assoc_tuple_values.index(f'{node_role}_taxon_id')]
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        # https://hynek.me/articles/hashes-and-equality/
        return hash(self.id)
    
    def to_dict(self):
        """
            Convert Node object to a dictionary of values relevant to the node.
            :return: dictionary with node information
        """
        node_dict = {
            'id': self.id,
            'label': self.label,
            'iri': self.iri,
            'semantic': self.semantic_groups,
            'taxon_id': self.taxon
        }
        
        return node_dict
    
class Edge:
    """
        Initialize edges using this class, carrying information about the id of the association,
        the ids of the subject and object and the id, label and iri link of the relation.
        :param assoc_tuple: tuple of information about association
    """
    def __init__(self, assoc_tuple: tuple):
        self.id = assoc_tuple[constants.assoc_tuple_values.index('id')]
        self.subject = assoc_tuple[constants.assoc_tuple_values.index('subject_id')]
        self.object = assoc_tuple[constants.assoc_tuple_values.index('object_id')]
        self.relation = {
            'id': assoc_tuple[constants.assoc_tuple_values.index('relation_id')],
            'iri': assoc_tuple[constants.assoc_tuple_values.index('relation_iri')],
            'label': assoc_tuple[constants.assoc_tuple_values.index('relation_label')]
        }
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        """
            Convert Edge object to a dictionary of values relevant to the edge.
            :return: dictionary with edge information
        """
        edge_dict = {
            'id': self.id,
            'subject': self.subject,
            'object': self.object,
            'relation_id': self.relation['id'],
            'relation_label': self.relation['label'],
            'relation_iri': self.relation['iri']
        }
        
        return edge_dict

class KnowledgeGraph:
    """
        Initialize a knowledge graph by giving a list of associations that is converted into
        a set of Edge objects and Node objects. 
        :param all_associations: list of dictionaries from responses, by default an empty list
    """
    def __init__(self, all_associations: list = []):
        self.all_edges = set()  # all unique edges in knowledge graph
        self.all_nodes = set()  # all unique nodes in knowledge graph
        
        self.add_edges_and_nodes(all_associations)
        self.analyze_graph()
        
    def generate_dataframes(self):
        """
            Generate dataframes that contain all edges and nodes.
            :return: dataframe with all edges and dataframe with all nodes
        """
        edges = pd.DataFrame.from_records([edge.to_dict() for edge in self.all_edges])
        nodes = pd.DataFrame.from_records([node.to_dict() for node in self.all_nodes])
        return edges, nodes
        
    def analyze_graph(self):
        """
            Analyze the current graph by looking at all semantic groups found in the nodes as well as how many nodes and edges
            are contained in the graph.
        """
        # Find all semantic groups
        all_semantic_groups = set()
        for node in self.all_nodes:
            all_semantic_groups.add(node.semantic_groups)
        register_info(f'The graph contains {len(all_semantic_groups)} different semantic groups: {all_semantic_groups}')
        
        # Show total number of edges and nodes
        register_info(f'For the graph, a total of {len(self.all_edges)} edges and {len(self.all_nodes)} nodes have been generated.')
        
    def find_relation_labels(self, substring_relation_label):
        """ 
            Find all relations that have a label that contains the given substring. 
            :param substring_relation_label: substring that needs to be contained by the relation label
            :return: dictionary of relations where key represents id of relation and values labels of relations
        """
        found_relations = {}
        
        for edge in self.all_edges:
            relation_id = edge.relation['id']
            relation_label = edge.relation['label']
            if (relation_label and substring_relation_label in relation_label):
                found_relations[relation_id] = relation_label
        register_info(f'All {len(found_relations)} relations with substring "{substring_relation_label}":\n {found_relations}')
        
        return found_relations
    
    def add_edges_and_nodes(self, associations: list):
        """
            Add new edges and nodes to the graph given a list of association dictionaries.
            :param associations: list of association dictionaries
        """
        for association in associations:
            self.all_edges.add(Edge(association))
            self.all_nodes.add(Node(association, 'subject'))
            self.all_nodes.add(Node(association, 'object'))
            
    def get_extracted_nodes(self, extract_semantic_groups: list):
        """
            Get all nodes that belong to at least one of the given semantic group(s).
            :param extract_semantic_groups: list of semantic group names
        """
        extracted_nodes = set()
        
        for node in self.all_nodes:
            intersection = [semantic_group for semantic_group in node.semantic_groups if semantic_group in extract_semantic_groups]
            if (len(intersection) > 0):
                extracted_nodes.add(node)
        register_info(f'Extracted a total of {len(extracted_nodes)} nodes that belong to at least one of {extract_semantic_groups}')
        
        return extracted_nodes
    
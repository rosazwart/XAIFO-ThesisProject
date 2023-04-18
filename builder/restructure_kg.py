from builder.kg import KnowledgeGraph, Node, Edge
import util.constants as constants
from util.common import register_info

import pandas as pd
import numpy as np
import hashlib

class NewNode:
    """
        Initialize nodes using this class, carrying information about the id
        of the entity, the semantic groups that are associated with the entity,
        and the label.
        :param old_node: Node instance
    """
    def __init__(self, id, label, iri, semantic):
        self.id = id
        self.label = label
        self.iri = iri
        self.semantic_groups = semantic
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        """
            Convert NewNode object to a dictionary of values relevant to the
            node.
            :return: dictionary with node information
        """
        node_dict = {
            'id': self.id,
            'label': self.label,
            'iri': self.iri,
            'semantic': self.semantic_groups
        }
        
        return node_dict
    
class NewEdge:
    def __init__(self, id, subject, object, relation_id, relation_label, relation_iri):
        self.id = id
        self.subject = subject
        self.object = object
        self.relation = {
            'id': relation_id,
            'iri': relation_iri,
            'label': relation_label
        }
        
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        """
            Convert NewEdge object to a dictionary of values relevant to the edge.
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
    
class RestructuredKnowledgeGraph:
    """
        Initialize a knowledge graph restructuring by giving a KnowledgeGraph entity
        containing a set of Edge and Node objects.
        :param old_kg: KnowledgeGraph instance
    """
    def __init__(self, old_kg: KnowledgeGraph):
        self.all_edges = set()
        self.all_nodes = set()
            
        self.restructure_kg(old_kg)
        
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
        
    def generate_edge_id(self, relation_id, subject, object):
        strings_tuple = (relation_id, subject, object)
        hasher = hashlib.md5()
        for string_value in strings_tuple:
            hasher.update(string_value.encode())
        return hasher.hexdigest()
        
    def add_edge(self, edge: NewEdge):
        """
            Add a NewEdge object to set of edges.
        """
        self.all_edges.add(edge)
    
    def add_node(self, node: NewNode):
        """
            Add a NewNode object to set of nodes.
        """
        self.all_nodes.add(node)
        
    def transform_node(self, node: Node, edges_df: pd.DataFrame):
        """
            Find out to which semantic group the node belongs.
        """
        return node.semantic_groups
        
    def add_concept_taxon(self, node: Node):
        if not pd.isnull(node.taxon_id) and node.semantic_groups == constants.GENE:
            gene_node = node
            taxon_node = NewNode(id=gene_node.taxon_id, label=gene_node.taxon_label, iri=np.nan, semantic=constants.TAXON)
            
            taxon_edge_id = self.generate_edge_id(constants.FOUND_IN['id'], gene_node.id, taxon_node.id)
            taxon_edge = NewEdge(taxon_edge_id, gene_node.id, taxon_node.id, constants.FOUND_IN['id'], constants.FOUND_IN['label'], constants.FOUND_IN['iri'])
            
            self.add_node(taxon_node)
            self.add_node(gene_node)
            
            self.add_edge(taxon_edge)
            
    def restructure_kg(self, old_kg: KnowledgeGraph):
        edges_df, _ = old_kg.generate_dataframes()
        
        for node in old_kg.all_nodes:
            node.semantic_groups = self.transform_node
            
            # Add TAXON nodes
            self.add_concept_taxon(node)
            
            # 
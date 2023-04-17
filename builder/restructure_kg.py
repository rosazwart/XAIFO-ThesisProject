from builder.kg import KnowledgeGraph, Node, Edge
import util.constants as constants

import pandas as pd
import numpy as np

class NewNode:
    """
        Initialize nodes using this class, carrying information about the id
        of the entity, the semantic groups that are associated with the entity,
        and the label.
        :param old_node: Node instance
    """
    def __init__(self, old_node: Node):
        self.id = old_node.id
        self.label = old_node.label
        self.iri = old_node.iri
        self.semantic_groups = old_node.semantic_groups
        
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
    
class RestructuredKnowledgeGraph:
    """
        Initialize a knowledge graph restructuring by giving a KnowledgeGraph entity
        containing a set of Edge and Node objects.
        :param old_kg: KnowledgeGraph instance
    """
    def __init__(self, old_kg: KnowledgeGraph):
        self.all_edges = set()
        self.all_nodes = set()
        
        # Add TAXON nodes
        self.add_concept_taxon(old_kg)
        
        
    def add_concept_taxon(self, old_kg: KnowledgeGraph):
        for node in old_kg.all_nodes:
            if pd.isnull(node.taxon):
                print(node.taxon)
    
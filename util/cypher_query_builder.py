import pandas as pd

def store_queries(queries: list, file_name: str ='queries.txt'):
    """
        Store into txt file in which the queries are separated with semi-colons.
    """
    query_chain = ';\n'.join(queries)
    
    with open('output/{}'.format(file_name), 'w') as f:
        f.write(query_chain)
        
    print('Generated query list in file', file_name)

def create_load_csv_to_node_query(semantic_group_name: str, file_name: str, headers: list):
    """
        Create a query that loads a csv and appends a new node label. Also include necessary constraints.
        :param semantic_group_name: name of semantic group
        :param file_name: name of csv file that needs to be loaded
        :param headers: list of headers representing properties of nodes, on first element of this list a uniqueness constraint is applied
        
        Query example:
            CREATE CONSTRAINT entityIdConstraint FOR (e:Entity) REQUIRE e.id IS UNIQUE
        
            LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
            CREATE (e:Entity {id: row.id, label: row.label, semantic: row.semantic, taxon: row.taxon_label})
    """
    
    property_assigns = list()
    for header in headers:
        property_assigns.append('{}: row.{}'.format(header, header))
    all_properties = ', '.join(property_assigns)
    
    node_entity_label = semantic_group_name.title().replace(' ', '')
    node_entity_instance = semantic_group_name[0].lower()
    node_entity = '{}:{}'.format(node_entity_instance, node_entity_label)
    
    query_stmt = f"""
        CREATE CONSTRAINT {semantic_group_name.replace(' ', '')}IdConstraint FOR ({node_entity}) REQUIRE {node_entity_instance}.{headers[0]} IS UNIQUE;
        LOAD CSV WITH HEADERS FROM 'file:///{file_name}' AS row
        CREATE ({node_entity} {{{all_properties}}})
    """
    
    return query_stmt

def build_queries_for_edges(all_edges: pd.DataFrame):
    """
        https://stackoverflow.com/questions/47298574/how-to-create-a-relationship-between-2-nodes-where-the-nodes-labels-properties
    
        Query example:
        MATCH (n1 {name: {nameParamN1}}), (n2 {name: {nameParamN2}})
        CALL apoc.create.relationship(n1, {relationParam}, {}, n2)
        YIELD rel
        RETURN rel
        
        ('CALL apoc.create.relationship([{labelParamN1}], {name: {nameParamN1}}, {relationParam}, [{labelParamN2}], {name: {nameParamN2}})',
        {labelParamN1: labelParamN1, nameParamN1: nameParamN1, labelParamN2: labelParamN2, nameParamN2: nameParamN2, relationParam: relation})
    """
    


def build_queries_for_nodes(all_nodes: pd.DataFrame):
    """
        Build nodes with different labels such that the Neo4j graph contains differently labeled nodes.
        :param all_nodes: dataframe containing all nodes
    """
    
    all_semantic_groups = all_nodes['semantic'].unique()
    all_queries = list()
    for semantic_group in all_semantic_groups:
        semantic_grouped_nodes = all_nodes.loc[all_nodes['semantic'] == semantic_group].drop(columns=['semantic'])
        
        file_name = 'nodes_{}.csv'.format(semantic_group.replace(' ', '_'))
        semantic_grouped_nodes.to_csv('output/{}'.format(file_name), index=False)
        print('All nodes related to', semantic_group, 'are stored into', file_name)
        
        headers = list(semantic_grouped_nodes.columns.values)
        query_stmt = create_load_csv_to_node_query(semantic_group, file_name, headers)
        all_queries.append(query_stmt)
    
    store_queries(all_queries, 'node_queries.txt')
    
def get_unique_triplets(all_edges_with_nodes: pd.DataFrame):
    """

    """
    print(all_edges_with_nodes[['subject_semantic', 'relation_id', 'object_semantic']])
    
    
def join_nodes_edges(all_nodes: pd.DataFrame, all_edges: pd.DataFrame):
    """
        
    """
    
    all_edges.rename(columns={'id': 'edge_id'}, inplace=True)
    all_nodes.rename(columns={'id': 'node_id', 'label': 'node_label', 'semantic': 'node_semantic'}, inplace=True)
    
    relevant_info_edges = all_edges[['edge_id', 'subject', 'object', 'relation_id', 'relation_label']]
    relevant_info_nodes = all_nodes[['node_id', 'node_label', 'node_semantic']]
    
    # Merge all information of subject nodes
    joined_subjects = relevant_info_edges.merge(relevant_info_nodes, left_on='subject', right_on='node_id', how='inner')
    joined_subjects.rename(columns={'node_id': 'subject_id', 'node_label': 'subject_label', 'node_semantic': 'subject_semantic'}, inplace=True)
    
    # Merge all information of object nodes
    joined_objects = joined_subjects.merge(relevant_info_nodes, left_on='object', right_on='node_id', how='inner')
    joined_objects.rename(columns={'node_id': 'object_id', 'node_label': 'object_label', 'node_semantic': 'object_semantic'}, inplace=True)
    
    all_edges_with_nodes = joined_objects.drop(columns=['subject', 'object'])
    
    all_edges_with_nodes.dropna(inplace=True)
    all_edges_with_nodes.reset_index(drop=True, inplace=True)
    
    return all_edges_with_nodes
    

def build_queries(all_nodes: pd.DataFrame, all_edges: pd.DataFrame):
    """
    """
    build_queries_for_edges(all_edges)
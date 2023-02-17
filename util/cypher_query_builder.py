from util.common_util import register_info

import pandas as pd

def store_queries(queries: list, file_name: str ='queries.txt'):
    """
        Store given list of queries into a txt file in which the queries are separated with semi-colons.
        :param queries: list of cypher queries
        :param file_name: file name of the file in which the queries are stored
    """
    query_chain = ';\n'.join(queries)
    
    with open('output/{}'.format(file_name), 'w') as f:
        f.write(query_chain)
    
    register_info(f'Generated query list in file {file_name}')

def create_load_csv_to_edge_query(file_name: str, colname_edge_id: str, colname_relation_label: str, colname_subject_id: str, colname_object_id: str):
    """
        Create a query that loads a csv and appends relationships.
        :param file_name: indicates where all edge entries can be found
        :param colname_x: name of column from which information needs to be taken
        :return: query statement
    """
    query_stmt = f"""
        LOAD CSV WITH HEADERS FROM 'file:///{file_name}' AS row
        MATCH (n1 {{id: row.{colname_subject_id}}}), (n2 {{id: row.{colname_object_id}}})
        
        WITH n1, n2, row
        CALL apoc.create.relationship(n1, row.{colname_relation_label}, {{id: row.{colname_edge_id}}}, n2) 
        YIELD rel
        RETURN rel
    """
    
    return query_stmt

def build_queries_for_edges(all_edges: pd.DataFrame):
    """
        Collect all queries that are needed to create all relationships in Neo4j given all edges.
        :param all_edges: dataframe of all found edges
        :return: list of queries
    """
    # Drop all rows with a NaN value in its row
    all_edges.dropna(inplace=True)
    all_edges.reset_index(drop=True, inplace=True)
    
    file_name = 'query_edges.csv'.format(all_edges)
    all_edges.to_csv('output/{}'.format(file_name), index=False)
    
    register_info(f'All edges are stored into {file_name}')
    
    query_stmt = create_load_csv_to_edge_query(file_name, 'id', 'relation_label', 'subject', 'object')
    return [query_stmt]

def create_load_csv_to_node_constraint_query(semantic_group_name: str, colname_id: str):
    """ 
        Create a query that appends constraints for a given node label. This avoids any duplicate nodes based on their id.
        :param semantic_group_name: name of semantic group that will be a label in Neo4j
        :param colname_id: information on which duplicate nodes are checked are found in this column
        :return: query statement
    """
    node_entity_label = semantic_group_name.title().replace(' ', '')
    node_entity_instance = semantic_group_name[0].lower()
    node_entity = '{}:{}'.format(node_entity_instance, node_entity_label)
    
    query_stmt = f"""
        CREATE CONSTRAINT {semantic_group_name.replace(' ', '')}IdConstraint FOR ({node_entity}) REQUIRE {node_entity_instance}.{colname_id} IS UNIQUE;
    """
    
    return query_stmt

def create_load_csv_to_node_query(file_name: str, headers: list, colname_semantic_label: str):
    """
        Create a query that appends nodes with labels depending on their semantic group.
        :param file_name: indicates where all node entries can be found
        :param headers: list of all names of the columns in which relevant data can be found
        :param semantic_label: name of column in which the semantic group is found of entity 
        :return: query statement
    """
    property_assigns = list()
    for header in headers:
        property_assigns.append('{}: row.{}'.format(header, header))
    all_properties = ', '.join(property_assigns)
    
    query_stmt = f"""
        LOAD CSV WITH HEADERS FROM 'file:///{file_name}' AS row
        CALL apoc.merge.node([row.{colname_semantic_label}], {{{all_properties}}})
        YIELD node
        RETURN node
    """
    
    return query_stmt

def build_queries_for_nodes(all_nodes: pd.DataFrame, include_constraints: bool):
    """
        Collect all queries that are needed to create all nodes in Neo4j given all nodes.
        :param all_nodes: dataframe of all found nodes
        :param include_constraints: whether node constraints need to be included in the queries as well
        :return: list of queries 
    """
    all_queries = list()
    
    if include_constraints:
        # constraint queries
        all_semantic_groups = all_nodes['semantic'].unique()
        for semantic_group in all_semantic_groups:
            query_stmt = create_load_csv_to_node_constraint_query(semantic_group, col_name_id='id')
            all_queries.append(query_stmt)
    
    # load nodes queries
    header_filter = ['semantic', 'semantic_label', 'taxon_id', 'taxon_label']
    
    all_nodes['semantic_label'] = all_nodes.apply(lambda x: x['semantic'].title().replace(' ', ''), axis=1)
    headers = list(all_nodes.columns.values)
    headers = [header_name for header_name in headers if header_name not in header_filter]
    
    file_name = 'query_nodes.csv'.format(all_nodes)
    all_nodes.to_csv('output/{}'.format(file_name), index=False)
    
    register_info(f'All nodes are stored into {file_name}')
    
    query_stmt = create_load_csv_to_node_query(file_name, headers, 'semantic_label')    
    all_queries.append(query_stmt)
    
    return all_queries

def build_queries(all_nodes: pd.DataFrame, all_edges: pd.DataFrame, include_constraints=False):
    """
        Set up the queries in a txt file and csv files for all nodes and edges on order to create the graph in Neo4j.
        :param all_nodes: dataframe of all found nodes
        :param all_edges: dataframe of all found edges
        :param include_constraints: whether node constraints need to be included in the queries as well which is not needed when query chain has already been performed before
    """
    all_queries = list()
    
    all_queries.extend(build_queries_for_nodes(all_nodes, include_constraints))
    all_queries.extend(build_queries_for_edges(all_edges))
    store_queries(all_queries, 'queries.txt')
    
    register_info('--- Instructions ---\n Place the generated csv files into the import file of the database. Then, copy paste the queries from the txt file into the Neo4j browser.')
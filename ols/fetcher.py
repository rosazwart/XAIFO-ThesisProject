import ols.logger as logger
import ols.unpacker as unpacker

def get_relation_properties(relations_df):
    """
        For each relation found in the dataset, get its properties provided by OLS. 
        :param relations_df: Dataframe that contains relations in the dataset
        :return List of relations that are represented by a dictionary with keys `uri` (id), `iri` (link), 
        `label`, `description`, `ancestors`, `descendants`, `parents`
    """
    all_relations = []
    
    for _, row in relations_df.iterrows():
        current_relation = {}
        
        relation_id = row['relation_id']
        current_relation['uri'] = relation_id
        
        # Prefix of relation ID represents id of ontology
        prefix_id = relation_id.split(':')[0].lower()
        
        # Ignore custom relation IDs
        if 'custom' not in prefix_id:
            # Retrieve IRI formatted ID of current relation
            iri = unpacker.get_iri_id(ontology=prefix_id, uri=relation_id)
            if iri:
                current_relation = unpacker.get_properties(ontology=prefix_id, iri=iri, relation_entry=current_relation)
                        
        all_relations.append(current_relation)
    
    return all_relations

def search_relation_based_on_uri(uri, all_relations):
    """
        Search relation that has given URI formatted ID from given all relations.
        :param uri: ID in URI format
        :param all_relations: List of all relations with their properties in dictionaries
        :return The dictionary of found relation or `None`
    """
    for relation_properties in all_relations:
        if 'uri' in relation_properties and relation_properties['uri'] == uri:
            return relation_properties
    return None

def report_parents_overlap_analysis(relation1, relation2, overlapping):
    logger.register_info(f'The relations:')
    logger.register_info(f'-Relation with ID {relation1["uri"]} and label {relation1["label"]}')
    logger.register_info(f'-Relation with ID {relation2["uri"]} and label {relation2["label"]}')
    logger.register_info(f'have overlapping parents:')
    for overlapping_parent in overlapping:
        parent_uri = overlapping_parent
        prefix_id = parent_uri.split(':')[0].lower()
        parent_iri = unpacker.get_iri_id(ontology=prefix_id, uri=parent_uri)
        parent_properties = {
            'uri': parent_uri
        }
        parent_properties = unpacker.get_properties(prefix_id, parent_iri, parent_properties)
        logger.register_info(f'- Relation with ID {parent_properties["uri"]} and label {parent_properties["label"]} describing {parent_properties["description"]}')
    logger.register_info('\n')

def find_parent_overlap(relations):
    for relation_properties1 in relations:
        if 'parents' in relation_properties1:
            parents1 = relation_properties1['parents']
            
            for relation_properties2 in relations:
                if 'uri' in relation_properties2:
                    if relation_properties1['uri'] != relation_properties2['uri']:
                        if 'parents' in relation_properties2:
                            parents2 = relation_properties2['parents']
                            parent_overlap = list(set(parents1).intersection(parents2))
                            if len(parent_overlap) > 0:
                                report_parents_overlap_analysis(relation_properties1, relation_properties2, parent_overlap)

def report_ancestors_analysis(relation, related_relations, role):
    if len(related_relations):
        logger.register_info(f'For relation with URI {relation["uri"]} and label "{relation["label"]}" with definitions {relation["description"]}, {role} have been found that also exist in the same relations set:')
        for related_relation in related_relations:
            logger.register_info(f'- Relation with URI {related_relation["uri"]} and label "{related_relation["label"]}" with definitions {related_relation["description"]}')
        logger.register_info('\n')

def analyze_ontology_relations(relations_df):
    all_relations = get_relation_properties(relations_df)
    
    for relation_properties in all_relations:
        ancestors_present = []
        
        if 'ancestors' in relation_properties:
            for ancestor_id in relation_properties['ancestors']:
                ancestor = search_relation_based_on_uri(ancestor_id, all_relations)
                if ancestor:
                    ancestors_present.append(ancestor)
            report_ancestors_analysis(relation_properties, ancestors_present, 'ancestors')
    
    # Find direct parent overlap
    find_parent_overlap(all_relations)
                
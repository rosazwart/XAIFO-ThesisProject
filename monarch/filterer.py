import monarch.constants as constants

relation_ids_filters = {'orthologous': ['RO:HOM0000017', 'RO:HOM0000020']}

def get_associations_on_entities(all_associations: list, semantic_groups_filter: list, include: bool = True):
    """
        Get a filtered list of associations in which each association includes at least one entity that belongs to
        one of the given semantic groups.
        :param all_associations: list of tuples storing associations that need to be filtered
        :param semantic_groups_filter: list of semantic groups that needs to be included or excluded
        :param include: indicates whether given semantic groups need to be included (`True`) or excluded (`False`)
        :return: list of filtered associations
    """
    filtered_associations = list()

    for association in all_associations:
        all_semantic_groups = [association[constants.assoc_tuple_values.index('subject_category')], association[constants.assoc_tuple_values.index('object_category')]]
        intersection = [semantic_group for semantic_group in all_semantic_groups if semantic_group in semantic_groups_filter]
        
        if (include and len(intersection) > 0) or (not include and len(intersection) == 0):
            filtered_associations.append(association)
            
    return filtered_associations
    
def get_associations_on_relations(all_associations: list, include_relation_ids_group: str):
    """
        Get a filtered list of associations in which each association includes one of the given relations.
        :param all_associations: list of tuples storing associations that need to be filtered
        :param include_relation_ids_group: name of group of relation ids that needs to be included, see `relation_ids_filters` for available names
        :return: list of filtered associations
    """
    filtered_associations = list()
    
    for association in all_associations:
        if (association[constants.assoc_tuple_values.index('relation_id')] in relation_ids_filters[include_relation_ids_group]):
            filtered_associations.append(association)
            
    return filtered_associations
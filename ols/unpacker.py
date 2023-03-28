import ols.requester as requester

def get_iri_id(ontology, uri):
    """
        Get ID in IRI format given the ID in URI format and ontology ID.
        :param ontology: ID of ontology
        :param uri: ID in URI format
    """
    iri = None
    
    response_values = requester.get_iri(ontology=ontology, uri=uri)
    response_results = response_values['response']
    
    numberFound = response_results['numFound']
    if numberFound == 1:
        iri = response_results['docs'][0]['iri']
    elif numberFound > 1:
        for resultEntry in response_results['docs']:
            if 'obo_id' in resultEntry and resultEntry['obo_id'] == uri:
                iri = resultEntry['iri']
    
    return iri

def get_ids_from_link(links, class_name):
    """
        Get OBO IDs of ontology entries of given class group (ancestors, descendants, parents, children of entry). 
        :param links: Dictionary of links of all available class groups from entry
        :param class_name: Name of the group related to entry such as its ancestors, descendants, parents, children
        :return List of IDs that belong to given class group
    """
    ids = []
    
    if class_name in links:
        link = links[class_name]['href']
        
        response_values = requester.get_values(link)
        response_properties = response_values['_embedded']['properties']
        
        for property_values in response_properties:
            id = property_values['obo_id']
            if id:
                ids.append(id)
        
    return ids

def get_properties(ontology, iri, relation_entry):
    """
        Get properties of entry with given IRI ID of given ontology.
        :param ontology: ID of ontology
        :param iri: ID in IRI format
        :param relation_entry: Relation represented as a dictionary with key `uri`
        :return Dictionary representing properties of a relations with keys `uri`, `iri`,
        `label`, `description`, `ancestors`, `descendants`, `parents`
    """
    response_values = requester.get_term(ontology=ontology, iri=iri)
    if '_embedded' in response_values:
        response_properties = response_values['_embedded']['properties']
        
        if (len(response_properties) > 0):
            properties = response_properties[0]
            
            label = properties['label']
            uri = properties['obo_id']
            
            annotations =  properties['annotation']
            description = None
            if 'definition' in annotations:
                description =annotations['definition']
            
            links = properties['_links']
            ancestors = get_ids_from_link(links, 'ancestors')
            descendants = get_ids_from_link(links, 'descendants')
            parents = get_ids_from_link(links, 'parents')
            
            relation_entry = {
                'uri': uri,
                'iri': iri,
                'label': label,
                'description': description,
                'ancestors': ancestors,
                'descendants': descendants,
                'parents': parents
            }
            
    return relation_entry
    
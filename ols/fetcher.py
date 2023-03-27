import pandas as pd

import ols.requester as requester

def get_ids(links, class_name='ancestors'):
    """
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

def get_relation_properties(relations_df):
    """
    """
    relations_properties = []
    
    for _, row in relations_df.iterrows():
        relation_properties = {}
        
        relation_id = row['relation_id']
        relation_properties['uri'] = relation_id
        
        prefix_id = relation_id.split(':')[0].lower()
        
        if 'custom' not in prefix_id:
            response_values = requester.get_iri(ontology=prefix_id, uri=relation_id)
            response_results = response_values['response']
            
            numberFound = response_results['numFound']
            iri = None
            if numberFound == 1:
                iri = response_results['docs'][0]['iri']
            elif numberFound > 1:
                for resultEntry in response_results['docs']:
                    if 'obo_id' in resultEntry and resultEntry['obo_id'] == relation_id:
                        iri = resultEntry['iri']
                
            if iri:
                response_values = requester.get_term(ontology=prefix_id, iri=iri)
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
                        ancestors = get_ids(links, 'ancestors')
                        descendants = get_ids(links, 'descendants')
                        
                        relation_properties['iri'] = iri
                        relation_properties['uri'] = uri
                        relation_properties['label'] = label
                        relation_properties['description'] = description
                        relation_properties['ancestors'] = ancestors
                        relation_properties['descendants'] = descendants
                        
        relations_properties.append(relation_properties)
    
    return relations_properties

def search_in_properties(uri, all_relations):
    for relation_properties in all_relations:
        if 'uri' in relation_properties and relation_properties['uri'] == uri:
            return relation_properties
    return None

def report_ancestors_overlap_analysis(relation1, relation2, overlapping):
    print(relation1, relation2, overlapping)

def find_overlap(relations):
    for relation_properties1 in relations:
        if 'ancestors' in relation_properties1:
            ancestors1 = relation_properties1['ancestors']
            
            for relation_properties2 in relations:
                if 'uri' in relation_properties2:
                    if relation_properties1['uri'] != relation_properties2['uri']:
                        if 'ancestors' in relation_properties2:
                            ancestors2 = relation_properties2['ancestors']
                            ancestor_overlap = set(ancestors1).intersection(ancestors2)
                            if len(ancestor_overlap) > 0:
                                report_ancestors_overlap_analysis(relation_properties1, relation_properties2, ancestor_overlap)
            

def report_ancestors_analysis(relation, related_relations, role):
    if len(related_relations):
        print(f'For relation with URI {relation["uri"]} and label "{relation["label"]}" with definitions {relation["description"]}, {role} have been found that also exist in the same relations set:')
        for related_relation in related_relations:
            print(f'- Relation with URI {related_relation["uri"]} and label "{related_relation["label"]}" with definitions {related_relation["description"]}')
        print('\n')

def analyze_ontology_relations(relations_df):
    all_relations = get_relation_properties(relations_df)
    
    for relation_properties in all_relations:
        ancestors_present = []
        
        if 'ancestors' in relation_properties:
            for ancestor_id in relation_properties['ancestors']:
                ancestor = search_in_properties(ancestor_id, all_relations)
                if ancestor:
                    ancestors_present.append(ancestor)
            report_ancestors_analysis(relation_properties, ancestors_present, 'ancestors')
        
    
        #if 'descendants' in relation_properties:
        #    descendants_present = []
        #    for descendant_id in relation_properties['descendants']:
        #        descendant = search_in_properties(descendant_id, all_relations)
        #        if descendant:
        #            descendants_present.append(descendant)
        #    report_analysis(relation_properties, descendants_present, 'descendants')
    
    # Find direct parent overlap
    find_overlap(all_relations)
                
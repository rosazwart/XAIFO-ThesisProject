from util.common import register_error

import requests
import time

BASE_URL = 'http://www.ebi.ac.uk/ols/api'
RETRIES = 2

def get_values(url):
    """
    
    """
    for i in range(RETRIES):
        try:
            response = requests.get(url, headers={'accept': 'application/json'})
            return response.json()
        except Exception as e:
            if (i < RETRIES - 1):
                time.sleep(3)
                print('Retry', i)
                continue
            else:
                register_error(f'Response values could not get data from API url {url} in response {response} due to {e}')
                return {}

def get_term(ontology, iri):
    """
    """
    for i in range(RETRIES):
        try:
            response = requests.get(f'http://www.ebi.ac.uk/ols/api/ontologies/{ontology}/properties?iri={iri}', headers={'accept': 'application/json'})
            return response.json()
        except Exception as e:
            if (i < RETRIES - 1):
                time.sleep(3)
                print('Retry', i)
                continue
            else:
                register_error(f'Response values could not get acquired for relation with iri {iri} of ontology {ontology} resulting in response {response} due to {e}')
                return {}

def get_iri(ontology, uri):
    """
    """
    params = {
        'obo_id': uri,
        'ontology': ontology
    }
    
    for i in range(RETRIES):
        try:
            response = requests.get(f'http://www.ebi.ac.uk/ols/api/select?q={uri}', headers={'accept': 'application/json'}, params=params)
            return response.json()
        except Exception as e:
            if (i < RETRIES - 1):
                time.sleep(3)
                print('Retry', i)
                continue
            else:
                register_error(f'Response values could not get acquired for relation with uri {uri} of ontology {ontology} resulting in response {response} due to {e}')
                return {}
from util.common import register_error

import requests
import time

BASE_URL = 'http://www.ebi.ac.uk/ols/api'
RETRIES = 2

def get_values(url):
    """
        Get values provided by given URL.
        :param url: Link of information source calling on API
        :return Response values of API call
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
        Get properties of given IRI and ontology ID.
        :param ontology: ID of ontology
        :param iri: ID of relation in IRI format
        :return Response values of API call https://www.ebi.ac.uk/ols/docs/api#:~:text=Properties%20and%20individuals 
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
        Get IRI of given URI and ontology ID.
        :param ontology: ID of ontology
        :param uri: ID of relation in URI format
        :return: Response values of API call https://www.ebi.ac.uk/ols/docs/api#:~:text=results%20page%20number-,Select%20terms,-We%20provide%20an
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
from monarch.logger import register_error

import requests
import time

BASE_URL = 'https://api.monarchinitiative.org/api'
RETRIES = 2

def get_associations(direction: str, node: str, params: dict):
    """
    """
    for i in range(RETRIES):
        try:
            response = requests.get(f'{BASE_URL}/association/{direction}/{node}', params=params)
            return response.json()
        except Exception as e:
            if (i < RETRIES - 1):
                time.sleep(3)
                print('Retry', i)
                continue
            else:
                register_error(f'Response values could not get acquired at node {node} for {direction} associations (params: {params}) resulting in response {response} due to {e}')
                return {}

def get_in_out_associations(node: str, params: dict, max_rows: int = 2000):
    """
        Get all out and in edges of given node. 
        :param node: identifier of node
        :param max_rows: maximum number of rows to get
        :return: responses of getting out and in associations, respectively (return empty objects when request fails and record error in log file)
    """
    params['rows'] = max_rows
    
    response_out = get_associations('from', node, params)
    response_in = get_associations('to', node, params)
    
    return response_out, response_in
from util.common_util import register_error

import requests

BASE_URL = 'https://api.monarchinitiative.org/api'

def get_in_out_associations(node: str, params: dict, max_rows: int = 2000):
    """
        Get all out and in edges of given node. 
        :param node: identifier of node
        :param max_rows: maximum number of rows to get
        :return: responses of getting out and in associations, respectively (return empty objects when request fails and record error in log file)
    """
    params['rows'] = max_rows
    try:
        response_out = requests.get(f'{BASE_URL}/association/from/{node}', params=params)
        response_in = requests.get(f'{BASE_URL}/association/to/{node}', params=params)
        return response_out.json(), response_in.json()
    except Exception as e:
        register_error(f'Response values could not get acquired at node {node} with responses {response_in} and {response_out} due to {e}')
        return {}, {}
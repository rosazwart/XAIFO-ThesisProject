import requests

class MonarchFetcher:
    def __init__(self):
        self.base_url = 'https://api.monarchinitiative.org/api'
        
    def getFromToAssociations(self, node: str, rows: int = 100) -> list:
        param_values = {
            'unselect_evidence': True,
            'rows': rows
        }
        
        response_from = requests.get(f'{self.base_url}/association/from/{node}', params=param_values)
        response_to = requests.get(f'{self.base_url}/association/to/{node}', params=param_values)
        
        return response_from.json(), response_to.json()
        
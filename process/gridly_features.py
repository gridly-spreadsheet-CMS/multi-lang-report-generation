import requests
import json
import csv
from io import StringIO

BASE_URL = 'https://eu-central-1.api.gridly.com/v1'

class GridlyFeature:
    def __init__(self, view_id, api_key):
        self.view_id = view_id
        self.api_key = api_key

    def get_columns_from_view(self):
        url = f'''{BASE_URL}/{self.view_id}'''
        headers = {
            'Authorization': f'ApiKey {self.api_key}'
        }
        response = requests.request('GET', url, headers=headers)

        return [col['id'] for col in response.json()['columns']]
    

    def import_file(self, file_path, import_request):
        headers = {
            'Authorization': f'ApiKey {self.api_key}'
        }

        data = {
            'importRequest': json.dumps(import_request),
        }

        files = {'file': open(file_path, 'rb')}

        url = f'''{BASE_URL}/views/{self.view_id}/import'''

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code != 202:
            raise Exception(f'''Error: {response.text}''')
        else:
            return 'Done!'
        
    def export_file(self, export_file_path):
        headers = {
            'Authorization': f'ApiKey {self.api_key}'
        }
        url = f'''{BASE_URL}/views/{self.view_id}/export'''
        
        response = requests.get(url=url, headers=headers)

        reader = csv.reader(StringIO(response.text))

        with open(export_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(reader)

            





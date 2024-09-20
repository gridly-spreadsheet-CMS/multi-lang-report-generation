import logging

import os, sys
sys.path.insert(1, '/'.join(os.path.realpath(__file__).split('/')[0:-2]))

from constants.configs import *
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackClient:
    def __init__(self):
        token = os.getenv('SLACK_APP_TOKEN')
        self.client = WebClient(token=token)
    

    def post_message(self, channel_id, message):
        try:
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            return response
        except SlackApiError as e:
            logging.error(f"Error posting message: {e.message}")
            return None
        
    def delete_message(self, channel_id, ts):
        try:
            response = self.client.chat_delete(
                channel=channel_id,
                ts=ts
            )
            return response['ok']
        except SlackApiError as e:
            logging.error(f"Error deleting message: {e.message}")
            return False
        
    def upload_file(self, channel_id, file_path, title=None):
        title = title if title else os.path.basename(file_path)  
   
        try:
            with open(file_path, "rb") as file_content:
                response = self.client.files_upload_v2(
                    channel=channel_id,
                    file=file_content,
                    title=title                )
            
            return response['file']['id'] 
        
        except SlackApiError as e:
            logging.error(f"Error uploading file: {e.message}")
            return None

    def delete_file(self, file_id):
        try:
            response = self.client.files_delete(
                file=file_id
            )
            return response['ok']
        
        except SlackApiError as e:
            logging.error(f"Error deleting file: {e}")
            return False
    
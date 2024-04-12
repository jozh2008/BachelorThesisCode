#!/usr/bin/env python3
from pprint import pprint
from bioblend import galaxy


class GalaxyWorkflow:
    def __init__(self, server: str, api_key: str) -> None:
        self.gi = galaxy.GalaxyInstance(url=server, key=api_key)
        self.api_key = api_key
        self.server = server
        self.history_id = "d699459f4303a1df"
    
    def get_dataset_url(self, history_id, dataset_id):
        dataset_details = self.gi.histories.show_dataset(history_id, dataset_id)
        pprint(dataset_details)
        return dataset_details['download_url']

    def get_all_histories(self):
        try:
            histories = self.gi.histories.get_histories()
            pprint(histories)
            return histories
        except ConnectionError as e:
            print("Error connecting to Galaxy instance:", e)
            return None
        
    def get_datasets_in_history(self):
        try:
            
            datasets =self.gi.histories.show_history(history_id=self.history_id, contents=True)
            pprint(datasets)
            return datasets
        except ConnectionError as e:
            print("Error connecting to Galaxy instance:", e)
            return None



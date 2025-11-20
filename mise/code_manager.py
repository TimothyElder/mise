import csv
import os

class CodeManager:
    def __init__(self, codes=None):
        # Initialize the codes dictionary
        self.codes = codes if codes is not None else {}
        
    def add_code(self, name, description):
        if name in self.codes:
            raise ValueError(f"Code '{name}' already exists.")
        
        self.codes[name] = description

    def delete_code(self, name):
        if name not in self.codes:
            raise KeyError(f"Code '{name}' does not exist.")
        del self.codes[name]

    def update_code(self, name, new_description):
        if name not in self.codes:
            raise KeyError(f"Code '{name}' does not exist.")
        
        self.codes[name] = new_description

    def get_all_codes(self, keys = False, values = False):
        
        return self.codes

    def save_codes(self, filepath): 
        """Save code dictionary to specified filepath and type
        Provides several options"""
        _, ext = os.path.splitext(filepath)
        
        if ext.lower() == ".json":
            save_codes_to_json(self, filepath)
        
        elif ext.lower() == ".csv":
            save_codes_to_csv(self, filepath)

        elif ext.lower() == ".pkl":
            save_codes_to_pickle(self, filepath)

        else:
            raise ValueError(f"Unsupported file type: {ext}. Must be 'csv', 'pkl', or 'json'")

    def load_codes(filepath):
        _, ext = os.path.splitext(filepath)

        with open('dict.csv') as csv_file:
            reader = csv.reader(csv_file)
            mydict = dict(reader)

        return(mydict)


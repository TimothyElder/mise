import json
import csv
import os
from mise.data_manager import Code
from mise.utils.file_io import save_codes_to_json, save_codes_to_csv, save_codes_to_pickle

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
            save_codes_to_pickle(self.filepath)

        else:
            raise ValueError(f"Unsupported file type: {ext}. Must be 'csv', 'pkl', or 'json'")

    def load_codes(filepath):
        _, ext = os.path.splitext(filepath)

        with open('dict.csv') as csv_file:
            reader = csv.reader(csv_file)
            mydict = dict(reader)

        

        
    



"""
Attributes
	1.	codes:
	•	A collection (e.g., list, DataFrame, or dictionary) that stores all codes.
	•	This will be the main attribute holding the data.
	2.	data_source (optional):
	•	The file path or database connection for saving/loading codes.
	•	Useful for persistence.

Methods
	1.	Initialization:
	•	Load existing codes from a data source if applicable.
	•	Initialize an empty collection if no data source exists.
	2.	Add Code:
	•	Create a new Code object, validate it (e.g., check for duplicates), and add it to the codes collection.
	3.	Delete Code:
	•	Remove a code by its name or ID.
	4.	Update Code:
	•	Modify an existing code’s name or description.
	5.	Get All Codes:
	•	Retrieve the full list of codes, optionally in a specific format (e.g., list, DataFrame).
	6.	Save Codes:
	•	Persist the current collection of codes to a file or database.
	7.	Load Codes:
	•	Populate the codes collection from a saved data source.
"""
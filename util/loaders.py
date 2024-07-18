import os
import pandas as pd

from util.constants import INPUT_FOLDER, OUTPUT_FOLDER
from util.common import register_info, dataframe2tuplelist

def get_input_data_path(file_name):
    return os.path.join(INPUT_FOLDER, file_name)

def create_output_folder(subfoldername: str):
    cwd_path = os.getcwd()
    output_path = os.path.join(cwd_path, OUTPUT_FOLDER)
    
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    else:
        print('Output folder located at', output_path, 'already exists, so it does not have to be created')

    sub_output_path = os.path.join(output_path, subfoldername)
    if not os.path.isdir(sub_output_path):
        os.makedirs(sub_output_path)
    else:
        print('Output folder located at', sub_output_path, 'already exists, so it does not have to be created')

def load_associations_from_csv(file_name, foldernames: list | None = None):
    """
        :return List of tuples containing monarch associations from csv file
    """

    if foldernames:
        curr_path = os.getcwd()
        for foldername in foldernames:
            curr_path = os.path.join(curr_path, foldername)
        file_path = os.path.join(curr_path, file_name)
        associations = pd.read_csv(file_path)
        associations = dataframe2tuplelist(associations)
    else:
        data_path = os.path.join(OUTPUT_FOLDER, file_name)
        associations = pd.read_csv(data_path)
        associations = dataframe2tuplelist(associations)
    
    register_info(f'Loaded {len(associations)} associations')
    return associations
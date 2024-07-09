import sys
from util.loaders import load_associations_from_csv
from util.constants import assoc_tuple_values, OUTPUT_FOLDER
from prev.monarch_constants import prefix2category
from util.common import tuplelist2dataframe, today

def convert_concepts(node_id: str):
    """
    """
    prefix, _ = node_id.split(':')
    return prefix2category(prefix)

if __name__ == "__main__":
    filename = 'hd_monarch_associations_2024-06-24.csv'
    monarch_assoc = load_associations_from_csv(file_name=filename, foldernames=['localfetcher', 'output'])

    converted_monarch_assoc = []
    for monarch_assoc_tuple in monarch_assoc:
        monarch_assoc_list = list(monarch_assoc_tuple)

        node_subject_id = monarch_assoc_list[assoc_tuple_values.index('subject_id')]
        node_subject_category_index = assoc_tuple_values.index('subject_category')

        node_object_id = monarch_assoc_list[assoc_tuple_values.index('object_id')]
        node_object_category_index = assoc_tuple_values.index('object_category')

        monarch_assoc_list[node_subject_category_index] = convert_concepts(node_id=node_subject_id)
        monarch_assoc_list[node_object_category_index] = convert_concepts(node_id=node_object_id)

        converted_monarch_assoc.append(tuple(monarch_assoc_list))

    tuplelist2dataframe(converted_monarch_assoc).to_csv(f'{OUTPUT_FOLDER}/prev_{filename}', index=False)

    
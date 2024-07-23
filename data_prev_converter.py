import sys
from util.loaders import load_associations_from_csv, create_output_folder
from util.constants import assoc_tuple_values, OUTPUT_FOLDER
from prev.monarch_constants import prefix2category
from util.common import tuplelist2dataframe, today

DISEASE_PREFIX = 'hd'
FILENAME = f'{DISEASE_PREFIX}_monarch_associations_2024-06-24.csv'

def convert_concepts(node_id: str):
    """
    """
    prefix, _ = node_id.split(':')
    return prefix2category(prefix)

def remove_tuplelist_duplicates(tuplelist: list):
    return [t for t in (set(tuple(i) for i in tuplelist))]

def get_nodes(assoc: list):
    """
    """
    nodes = set()

    for assoc_tuple in assoc:
        node_subject_id = assoc_tuple[assoc_tuple_values.index('subject_id')]
        node_object_id = assoc_tuple[assoc_tuple_values.index('object_id')]

        node_subject_category = assoc_tuple[assoc_tuple_values.index('subject_category')]
        node_object_category = assoc_tuple[assoc_tuple_values.index('object_category')]

        node_subject_label = assoc_tuple[assoc_tuple_values.index('subject_label')]
        node_object_label = assoc_tuple[assoc_tuple_values.index('object_label')]

        nodes.add(tuple([node_subject_id, node_subject_category, node_subject_label]))
        nodes.add(tuple([node_object_id, node_object_category, node_object_label]))

    nodes_tuplelist = list(nodes)
    remove_tuplelist_duplicates(nodes_tuplelist)

    return nodes_tuplelist

if __name__ == "__main__":
    create_output_folder(subfoldername=DISEASE_PREFIX)

    monarch_assoc = load_associations_from_csv(file_name=FILENAME, foldernames=['localfetcher', 'output'])

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

    tuplelist2dataframe(converted_monarch_assoc).to_csv(f'{OUTPUT_FOLDER}/{DISEASE_PREFIX}/prev_{FILENAME}', index=False)

    monarch_nodes = get_nodes(assoc=converted_monarch_assoc)
    tuplelist2dataframe(monarch_nodes, column_values=tuple(['id', 'semantic_groups', 'name'])).to_csv(f'prev/monarch/prev_{FILENAME.replace("associations", "nodes")}', index=False)

    
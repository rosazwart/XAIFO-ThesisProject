from data_loader import get_all_assoc_df
from association_getter import get_monarch_associations


if __name__ == "__main__":
    all_assoc_df = get_all_assoc_df(dir_name='deprecated_data')

    seeds = [
        'MONDO:0007739',    # Huntington disease
        'HGNC:4851' # HTT, causal gene Huntington disease
    ]

    all_assoc = get_monarch_associations(assoc_df=all_assoc_df, nodes_list=seeds,
                                         disease_file_name_ref='hd')
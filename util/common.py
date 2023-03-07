import logging
logging.basicConfig(level=logging.INFO, filename='monarchfetcher.log', filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from util.constants import assoc_tuple_values

def register_info(message):
    """
        Print message into console as well as given logger.
        :param current_logger: logger with configuration
        :param message: message that needs to be printed and logged
    """
    print(message)
    logging.info(message)
    
def register_error(message):
    """
        Log given error.
        :param message: message that needs to be printed and logged
    """
    print(message)
    logging.error(message)

def draw_graph(edges, source_colname, target_colname, file_name):
    """
        Draw a graph from a pandas dataframe given the column names of the source and target of the edges.
        :param source_colname: name of column that includes source of edge
        :param target_colname: name of column that includes target of edge
        :param file_name: name of file in which image of graph is stored (in `output` folder)
    """
    G = nx.from_pandas_edgelist(edges, source=source_colname, target=target_colname)
    
    nx.draw(G, with_labels=True, node_size=800, font_size=6)
    
    plt.savefig(file_name)
    
def tuplelist2dataframe(tuple_list: list):
    """

    """
    df = pd.DataFrame.from_records(tuple_list, columns=list(assoc_tuple_values))
    register_info(f'Created a dataframe with {df.shape[0]} entries and column values {df.columns.values}')
    return df

def dataframe2tuplelist(df: pd.DataFrame):
    """

    """
    tuple_list = list(df.itertuples(index=False, name=None))
    register_info(f'Created a list of tuples with {len(tuple_list)} entries')
    return tuple_list
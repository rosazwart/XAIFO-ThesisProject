"""
    Source: https://github.com/PPerdomoQ/rare-disease-explainer/blob/main/edge2vec3.py
"""

import argparse
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np   
import math
from scipy import stats
from gensim.models import Word2Vec

'''
use existing matrix to run edge2vec
'''
 
def read_graph(edgeList,weighted=False, directed=False):
    '''
    Reads the input network in networkx.
    '''
    if weighted:
        G = nx.read_edgelist(edgeList, nodetype=str, data=(('type',int),('weight',float),('id',int)), create_using=nx.DiGraph())
    else:
        G = nx.read_edgelist(edgeList, nodetype=str,data=(('type',int),('id',int)), create_using=nx.DiGraph())
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1.0

    if not directed:
        G = G.to_undirected()

    #print(G.edges(data = True))
    return G
 
def read_edge_type_matrix(file):
    '''
    load transition matrix
    '''
    matrix = np.loadtxt(file, delimiter=' ')
    return matrix


def simulate_walks_2(G, num_walks, walk_length,matrix,is_directed,p,q):
    '''
    generate random walk paths constrainted by transition matrix
    '''
    walks = []
    nodes = list(G.nodes())
    print('Walk iteration:')
    for walk_iter in range(num_walks):
        print(str(walk_iter+1), '/', str(num_walks))
        random.shuffle(nodes) 
        for node in nodes:
            # print "chosen node id: ",nodes
            walks.append(edge2vec_walk_2(G, walk_length, node,matrix,is_directed,p,q))  
    return walks

def edge2vec_walk_2(G, walk_length, start_node,matrix,is_directed,p,q): 
    # print "start node: ", type(start_node), start_node
    '''
    return a random walk path
    '''
    walk = [start_node]  
    while len(walk) < walk_length:# here we may need to consider some dead end issues
        cur = walk[-1]
        cur_nbrs =sorted(G.neighbors(cur)) #(G.neighbors(cur))
        random.shuffle(cur_nbrs)
        if len(cur_nbrs) > 0:
            if len(walk) == 1:
                rand = int(np.random.rand()*len(cur_nbrs))
                next =  cur_nbrs[rand]
                walk.append(next) 
            else:
                prev = walk[-2]
                #print('Prev:', prev)
                #print('Cur:', cur)
                pre_edge_type = G[prev][cur]['type']
                distance_sum = 0
                for neighbor in cur_nbrs:
                    neighbor_link = G[cur][neighbor] 
                    # print "neighbor_link: ",neighbor_link
                    neighbor_link_type = neighbor_link['type']
                    # print "neighbor_link_type: ",neighbor_link_type
                    neighbor_link_weight = neighbor_link['weight']
                    trans_weight = matrix[pre_edge_type-1][neighbor_link_type-1]
                    
                    if G.has_edge(neighbor,prev) or G.has_edge(prev,neighbor):#undirected graph
                        
                        distance_sum += trans_weight*neighbor_link_weight/p #+1 normalization
                    elif neighbor == prev: #decide whether it can random walk back
                        distance_sum += trans_weight*neighbor_link_weight
                    else:
                        distance_sum += trans_weight*neighbor_link_weight/q

                '''
                pick up the next step link
                ''' 

                rand = np.random.rand() * distance_sum
                threshold = 0 
                for neighbor in cur_nbrs:
                    neighbor_link = G[cur][neighbor] 
                    # print "neighbor_link: ",neighbor_link
                    neighbor_link_type = neighbor_link['type']
                    # print "neighbor_link_type: ",neighbor_link_type
                    neighbor_link_weight = neighbor_link['weight']
                    trans_weight = matrix[pre_edge_type-1][neighbor_link_type-1]
                    
                    if G.has_edge(neighbor,prev)or G.has_edge(prev,neighbor):#undirected graph
                        
                        threshold += trans_weight*neighbor_link_weight/p 
                        if threshold >= rand:
                            next = neighbor
                            break;
                    elif neighbor == prev:
                        threshold += trans_weight*neighbor_link_weight
                        #print('Activated')
                        if threshold >= rand:
                            next = neighbor
                            break;        
                    else:
                        threshold += trans_weight*neighbor_link_weight/q
                        if threshold >= rand:
                            next = neighbor
                            break;
		 
                walk.append(next) 
                #print('Next:', next)
        else:
            break #if only has 1 neighbour 
 
        # print "walk length: ",len(walk),walk
        # print "edge walk: ",len(edge_walk),edge_walk 
    return walk  
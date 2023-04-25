"""
    Source: https://github.com/PPerdomoQ/rare-disease-explainer/blob/main/transition3.py
"""

import argparse
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np   
import math
from scipy import stats
from scipy import spatial

'''
first version: unweighted, undirected network
use edge random walk to generate edge transction matrix based on EM algorithm
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

    # print (G.edges(data = True))
    print("Number of edges is {}".format(G.number_of_edges()))
    print("Number of nodes is {}".format(G.number_of_nodes()))
    return G
 
def initialize_edge_type_matrix(type_num):
    '''
    initialize a transition matrix with equal values
    '''
    initialized_val = 1.0/(type_num*type_num)
    matrix = [ [ initialized_val for i in range(type_num) ] for j in range(type_num) ]
    return matrix


def simulate_walks_1(G, num_walks, walk_length,matrix,is_directed,p,q):
    '''
    generate random walk paths constrainted by transition matrix
    '''
    walks = []
    links = list(G.edges(data = True))
    #print(links[0])
    print('Walk iteration:')
    for walk_iter in range(num_walks):
        print(str(walk_iter+1), '/', str(num_walks))
        random.shuffle(links)
        count = 1000
        for link in links:
            # print "chosen link id: ",link[2]['id']
            walks.append(edge2vec_walk(G, walk_length, link,matrix,is_directed,p,q)) 
            count = count - 1
            if count == 0 and len(links)>1000:#control the pairwise list length
                break
    return walks

def edge2vec_walk(G, walk_length, start_link,matrix,is_directed,p,q): 
    '''
    return a random walk path
    '''
    # print "start link: ", type(start_link), start_link
    walk = [start_link] 
    result = [str(start_link[2]['type'])]
    # print "result ",result
    while len(walk) < walk_length:# here we may need to consider some dead end issues
        cur = walk[-1]
        start_node = cur[0]
        end_node = cur[1]
        cur_edge_type = cur[2]['type']

        '''
        find the direction of link to go. If a node degree is 1, it means if go that direction, there is no other links to go further
        if the link are the only link for both nodes, the link will have no neighbours (need to have teleportation later)
        '''
        '''
        consider the hub nodes and reduce the hub influence
        '''
        if is_directed: # directed graph has random walk direction already
            direction_node = end_node
            left_node = start_node
        else:# for undirected graph, first consider the random walk direction by choosing the start node
            start_direction = 1.0/G.degree(start_node)
            end_direction = 1.0/G.degree(end_node)
            prob = start_direction/(start_direction+end_direction)
            # print "start node: ", start_node, " degree: ", G.degree(start_node)
            # print "end node: ", end_node, " degree: ", G.degree(end_node)

            # print cur[0], cur[1]
            rand = np.random.rand() 
            # print "random number ",rand
            # print "probability for start node: ",prob

            if prob >= rand:
                # print "yes"
                direction_node = start_node
                left_node = end_node
            else:
                direction_node = end_node
                left_node = start_node
        # print "directed node: ",direction_node
        # print "left_node node: ",left_node
        '''
        here to choose which link goes to. There are three conditions for the link based on node distance. 0,1,2
        '''
        neighbors = G.neighbors(direction_node) 
        # print G.has_edge(1,3)
        # print G.has_edge(3,1)
        '''
        calculate sum of distance, with +1 normalization
        '''
        distance_sum = 0
        for neighbor in neighbors:
            # print "neighbors:", neighbor
            neighbor_link = G[direction_node][neighbor]#get candidate link's type
            # print "neighbor_link: ",neighbor_link
            neighbor_link_type = neighbor_link['type']
            # print "neighbor_link_type: ",neighbor_link_type
            neighbor_link_weight = neighbor_link['weight']
            trans_weight = matrix[cur_edge_type-1][neighbor_link_type-1]
            if G.has_edge(neighbor,left_node) or G.has_edge(left_node,neighbor): 
                distance_sum += trans_weight*neighbor_link_weight/p  
            elif neighbor == left_node: #decide whether it can random walk back
                distance_sum += trans_weight*neighbor_link_weight
            else:
                distance_sum += trans_weight*neighbor_link_weight/q

        '''
        pick up the next step link
        '''
        # random.shuffle(neighbors)
        rand = np.random.rand() * distance_sum
        threshold = 0
        # next_link_end_node = 0 
        neighbors2 = G.neighbors(direction_node) 
        for neighbor in neighbors2:
            # print "current threshold: ", threshold
            neighbor_link = G[direction_node][neighbor]#get candidate link's type
            neighbor_link_type = neighbor_link['type']
            neighbor_link_weight = neighbor_link['weight']
            trans_weight = matrix[cur_edge_type-1][neighbor_link_type-1]
            if G.has_edge(neighbor,left_node) or G.has_edge(left_node,neighbor): 
                threshold += trans_weight*neighbor_link_weight/p
                if threshold >= rand:
                    next_link_end_node = neighbor
                    break;
            elif neighbor == left_node:
                threshold += trans_weight*neighbor_link_weight
                if threshold >= rand:
                    next_link_end_node = neighbor
                    break;
            else:
                threshold += trans_weight*neighbor_link_weight/q
                if threshold >= rand:
                    next_link_end_node = neighbor
                    break;

        # print "distance_sum: ",distance_sum
        # print "rand: ", rand, " threshold: ", threshold
        # print "next_link_end_node: ",next_link_end_node

        if distance_sum > 0: # the direction_node has next_link_end_node
            next_link = G[direction_node][next_link_end_node]
            # next_link = G.get_edge_data(direction_node,next_link_end_node)
            
            next_link_tuple = tuple()
            next_link_tuple += (direction_node,)
            next_link_tuple += (next_link_end_node,)
            next_link_tuple += (next_link,)
            # print type(next_link_tuple)
            # print next_link_tuple
            walk.append(next_link_tuple)
            result.append(str(next_link_tuple[2]['type']))
            # print "walk length: ",len(walk),walk
        else:
            break
    # print "path: ",result
    return result  


def update_trans_matrix(walks,type_size,evaluation_metric):
    '''
    E step, update transition matrix
    '''
    #here need to use list of list to store all edge type numbers and use KL divergence to update
    matrix = [ [ 0 for i in range(type_size) ] for j in range(type_size) ]
    repo = dict()
    for i in range(type_size):#initialize empty list to hold edge type vectors
        repo[i] = []

    for walk in walks:
        curr_repo = dict()#store each type number in current walk
        for edge in walk:
            edge_id = int(edge) - 1 
            if edge_id in curr_repo:
                curr_repo[edge_id] = curr_repo[edge_id]+1
            else:
                curr_repo[edge_id] = 1

        for i in range(type_size):
            
            # print "curr_repo[i]: ",curr_repo[i],type(curr_repo[i])
            if i in curr_repo:
                repo[i].append(curr_repo[i]) 
            else:
                repo[i].append(0) 
    
    for i in range(type_size):
        # print "repo ",i, ": ",repo[i],type(repo[i])
        for j in range(type_size):  
            if evaluation_metric == 1:
                sim_score = wilcoxon_test(repo[i],repo[j])  
                matrix[i][j] = sim_score
                # print "each pair of edge type sim_score: ", sim_score
            elif evaluation_metric == 2:
                sim_score = entroy_test(repo[i],repo[j])  
                matrix[i][j] = sim_score
            elif evaluation_metric == 3:
                sim_score = spearmanr_test(repo[i],repo[j])  
                matrix[i][j] = sim_score
            elif evaluation_metric == 4:
                sim_score = pearsonr_test(repo[i],repo[j])  
                matrix[i][j] = sim_score 
            else:
                raise ValueError('not correct evaluation metric! You need to choose from 1-4')  

    return matrix

'''
different ways to calculate correlation between edge-types
'''
#pairwised judgement
def wilcoxon_test(v1,v2):# original metric: the smaller the more similar 
    check = int(sum([a_i - b_i for a_i, b_i in zip(v1, v2)]))
    if check == 0:
        result = 0
    else: 
        result = stats.wilcoxon(v1, v2).statistic
    print('w', result)
    return 1/(math.sqrt(result)+1)

def entroy_test(v1,v2):#original metric: the smaller the more similar
    check = int(sum([a_i - b_i for a_i, b_i in zip(v1, v2)]))
    if check == 0:
        result = 0
    else: 
        result = stats.wilcoxon(v1, v2).statistic
    print('e' ,result)
    return result

def spearmanr_test(v1,v2):#original metric: the larger the more similar 
    if v1 == v2:
        result = 0.0
    else: 
        result = stats.wilcoxon(v1, v2).statistic

    return sigmoid(result)

def pearsonr_test(v1,v2):#original metric: the larger the more similar
    check = int(sum([a_i - b_i for a_i, b_i in zip(v1, v2)]))
    if check == 0:
        result = 0
    else: 
        result = stats.wilcoxon(v1, v2).statistic
    print('p', result)
    return sigmoid(result)

def cos_test(v1,v2): 
    return 1 - spatial.distance.cosine(v1, v2)

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def standardization(x):
    return (x+1)/2

def relu(x):
    return (abs(x) + x) / 2
    
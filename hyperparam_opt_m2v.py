# IMPORTANT: Run with `xaifo` environment
# TODO: error with `xaifognn` environment

import pandas as pd
import networkx as nx
import numpy as np

from torch_geometric.nn.models import MetaPath2Vec
from torch_geometric.data import HeteroData

import torch
from torch.utils.data import DataLoader

from deepsnap.dataset import GraphDataset
from deepsnap.batch import Batch

from gnn.linkpred_model import LinkPredModel, train, test

from ray import tune
from ray.tune.schedulers import ASHAScheduler

def train_m2v(epoch, model, loader, optimizer, log_steps=10):
    model.train()

    total_loss = 0
    for i, (pos_rw, neg_rw) in enumerate(loader):
        optimizer.zero_grad()
        loss = model.loss(pos_rw.to(torch_device), neg_rw.to(torch_device))
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        if (i + 1) % log_steps == 0:
            print((f'Epoch: {epoch}, Step: {i + 1:05d}/{len(loader)}, '
                   f'Loss: {total_loss / log_steps:.4f}'))
            total_loss = 0

@torch.no_grad()
def get_embedding(node_type, data, model):
    model.eval()
    z = model(node_type, batch=data.y_index_dict[node_type]).detach().numpy()
    return z

def optim(args):
    nodes = args['nodes']
        
    node_semantics = nodes[['semantic', 'semantic_id']].drop_duplicates().set_index('semantic_id').to_dict()
    node_semantics_dict = node_semantics['semantic']
    
    edges = args['edges']
    
    # Node embedding using Metapath2Vec
    edges_m2v = edges.copy()
    edges_m2v.replace({'class_head': node_semantics_dict, 'class_tail': node_semantics_dict}, inplace=True)
    edges_m2v['relation'].fillna('na', inplace=True)
    
    # TODO: to avoid index error, how to solve
    if args['dataset_nr'] == 1:
        node_type_first = 'ORTH'
    else:
        node_type_first = 'genotype'

    matching_indices = edges_m2v.index[edges_m2v['class_head'] == node_type_first].tolist()

    index_1 = 0
    index_2 = matching_indices[0]

    temp_row = edges_m2v.iloc[index_1].copy()
    edges_m2v.iloc[index_1] = edges_m2v.iloc[index_2]
    edges_m2v.iloc[index_2] = temp_row
    
    metapath_df = edges_m2v[['class_head', 'relation', 'class_tail']].drop_duplicates().reset_index().drop(columns=['index'])
    
    metapaths = list()
    metapath_array = metapath_df.to_records(index=False)
    metapath_array = list(metapath_array)
    for metapath_triplet in metapath_array:
        triplet = tuple(metapath_triplet)
        metapaths.append(triplet)
        
    data = HeteroData()
    for metapath in metapaths:
        src_node_type, rel_type, dst_node_type = metapath
        metapath_edges = edges_m2v.loc[(edges_m2v['class_head'] == src_node_type) & (edges_m2v['relation'] == rel_type) & (edges_m2v['class_tail'] == dst_node_type)]
        metapath_edge_head = metapath_edges['index_head'].values.tolist()
        metapath_edge_tail = metapath_edges['index_tail'].values.tolist()
        
        metapath_edge_index = [metapath_edge_head, metapath_edge_tail]
        metapath_edge_index = torch.LongTensor(metapath_edge_index)
        
        data[src_node_type, rel_type, dst_node_type].edge_index = metapath_edge_index
    
    node_types = list(node_semantics_dict.values())
    for node_type in node_types:
        all_nodes = nodes.loc[(nodes['semantic'] == node_type)]
        node_index_list = all_nodes['index_id'].values.tolist()
        node_index = torch.LongTensor(node_index_list)
        
        data[node_type].y_index = node_index
        
    model = MetaPath2Vec(data.edge_index_dict, embedding_dim=args['dimensions_m2v'],
                        metapath=metapaths, walk_length=args['walk_length'], context_size=args['context_size'],
                        walks_per_node=args['num_walks'], num_negative_samples=1,
                        sparse=True).to(args['device'])

    loader = model.loader(batch_size=128, shuffle=True, num_workers=6)
    optimizer = torch.optim.SparseAdam(list(model.parameters()), lr=args['lr_m2v'])
    
    for epoch in range(1, args['epoch_m2v']):
        train_m2v(epoch, model, loader, optimizer)
        print(f'Epoch: {epoch}')
        
    data_node_types = data.collect('y_index')
    index_emb_dict = {}

    for data_node_type in list(data_node_types.keys()):
        indices = np.array(data[data_node_type].y_index) 
        emb = get_embedding(data_node_type, data, model)
        
        for index, embedding in zip(indices, emb):
            index_emb_dict[index] = [embedding]
            
    metapath2vec_embedding = pd.DataFrame.from_dict(index_emb_dict, orient='index').sort_index()
    metapath2vec_embedding['Node'] = metapath2vec_embedding.index
    metapath2vec_embedding.rename(columns={0: 'Embedding'}, inplace=True)
    metapath2vec_embedding = metapath2vec_embedding[['Node', 'Embedding']]
    
    # Build graph with nodes and their embedding as node feature
    G = nx.DiGraph()
    for ind, node in metapath2vec_embedding.iterrows(): 
        G.add_node(int(node['Node']), node_feature=torch.Tensor(node['Embedding']))
    for ind, edge in edges.iterrows(): 
        G.add_edge(int(edge['index_head']), int(edge['index_tail']))
        
    # Split graph dataset into train, test and validation sets
    dataset = GraphDataset(G, task='link_pred', edge_train_mode="all")
    
    datasets = {}
    datasets['train'], datasets['val'], datasets['test']= dataset.split(transductive=True, split_ratio=[0.8, 0.1, 0.1])
    
    # Set up link prediction model
    input_dim = datasets['train'].num_node_features
    
    model = LinkPredModel(input_dim, args['hidden_dim'], args['output_dim'], args['layers'], args['aggr'], args['dropout'], args['device']).to(args['device'])
    optimizer = torch.optim.SGD(model.parameters(), lr=args['lr'], momentum=0.9, weight_decay=5e-4)
    
    # Generate dataloaders
    dataloaders = {split: DataLoader(ds, collate_fn=Batch.collate([]), batch_size=1, shuffle=(split=='train')) for split, ds in datasets.items()}
    
    best_model, best_x, perform = train(model, dataloaders, optimizer, args, ho = False)
    
    best_train_roc = test(best_model, dataloaders['train'], args)
    best_val_roc = test(best_model, dataloaders['val'], args)
    best_test_roc = test(best_model, dataloaders['test'], args)
    
    log = "Train: {:.4f}, Val: {:.4f}, Test: {:.4f}"
    print(log.format(best_train_roc, best_val_roc, best_test_roc))
    
    tune.report(val_auc=best_val_roc, train_auc = best_train_roc, test_auc = best_test_roc)

if __name__ == "__main__":
    torch_device = 'cpu'
    print('Using device:', torch_device)
    
    # Set parameters
    dataset_nr = input('Enter dataset number (1 or 2):')
    assert dataset_nr == 1 or 2
    
    # Load data
    edge_df = pd.read_csv(f'output/indexed_edges_{dataset_nr}.csv')
    node_df = pd.read_csv(f'output/indexed_nodes_{dataset_nr}.csv')
    
    # Set hyperparameter search space
    search_args = {
        'device': torch_device, 
        "hidden_dim" : tune.choice([64, 128, 256]),
        'output_dim': tune.choice([64, 128, 256]),
        "epochs" : tune.choice([100, 150, 200]),
        'type_size' : len(set(edge_df['type'])),
        'epoch_m2v' : tune.choice([5, 10]),
        'num_walks': tune.choice([2, 5, 10]),
        'walk_length' : tune.choice([10, 25, 35]),
        'context_size': tune.choice([3, 7]),
        'dimensions_m2v' : tune.choice([32, 64, 128]),
        'lr_m2v' : tune.loguniform(1e-4, 1e-1),
        'edges': edge_df, 
        'nodes': node_df,
        'dataset_nr': dataset_nr,
        'lr': tune.loguniform(1e-4, 1e-1), 
        'aggr': tune.choice(['mean', 'sum']), 
        'dropout': tune.choice([0, 0.1, 0.2]), 
        'layers': tune.choice([2, 4, 6])
    }

    scheduler = ASHAScheduler(
        max_t=10,
        grace_period=1,
        reduction_factor=2)

    result = tune.run(
        tune.with_parameters(optim),
        resources_per_trial = {"cpu": 8}, #change this value according to the gpu units you would like to use
        config = search_args,
        metric = "val_auc",
        mode = "max",
        num_samples = 30, #select the maximum number of models you would like to test
        scheduler = scheduler, 
        resume = False, 
        local_dir = "output")
    
    best_trial = result.get_best_trial("val_auc")
    print("Best trial config: {}".format(best_trial.config))
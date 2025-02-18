import torch
from torch.nn import Parameter
from torch import nn
import torch.nn.functional as F

class Interaction_GraphConvolution(nn.Module):
    def __init__(self, in_features, out_features):
        super(Interaction_GraphConvolution, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Parameter(torch.FloatTensor(in_features, out_features))
        self.bias = Parameter(torch.FloatTensor(out_features))
        self.reset_parameters()
        
    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, mode='fan_in', nonlinearity='relu')
        nn.init.zeros_(self.bias)  

    def forward(self, node_features, adjacency_matrix, mask_father, mask_hadamard):
        weight_features = torch.mm(node_features.float(), self.weight) + self.bias
        
        num_nodes = weight_features.size(0)
        features_expanded = weight_features.unsqueeze(2).expand(-1, -1, num_nodes)
        features_transpose_expanded = weight_features.unsqueeze(0).expand(num_nodes, -1, -1).transpose(1, 2)
        all_hadamard = torch.mul(features_expanded, features_transpose_expanded)

        masked_hadamard = all_hadamard * mask_hadamard

        adjacency_matrix = adjacency_matrix.unsqueeze(0)
        masked_hadamard = masked_hadamard.transpose(0, 1).transpose(0, 2)
        same_father_nodes = torch.matmul(adjacency_matrix, masked_hadamard)
        same_father_nodes = same_father_nodes.transpose(0, 2).transpose(0, 1)
        same_father_nodes *= mask_father
        
        sum_hadamard = same_father_nodes.sum(dim=2)

        return sum_hadamard

    def __repr__(self):
        return self.__class__.__name__ + ' (' \
               + str(self.in_features) + ' -> ' \
               + str(self.out_features) + ')'
import torch
import numpy as np
from torch.utils.data import DataLoader
from torch.utils.data.sampler import Sampler
from dataset import SupportSet, QuerySet

def load_support(args):
    s_set = SupportSet()

    num_classes = args['num_classes']
    num_support = args['num_support']
    num_query = args["num_query"]
    dataset = 's'

    sampler = RelationBatchSampler(s_set.y, num_classes, num_support, num_query, dataset)
    support_loader = DataLoader(s_set, batch_sampler=sampler,
                                 pin_memory=True if torch.cuda.is_available() else False)
    return support_loader
    
def load_query(args):
    q_set = QuerySet()

    num_classes = args['num_classes']
    num_support = args['num_support']
    num_query = args["num_query"]
    dataset = 'q'
    
    sampler = RelationBatchSampler(q_set.y, num_classes, num_support, num_query, dataset)
    query_loader = DataLoader(q_set, batch_sampler=sampler,
                                 pin_memory=True if torch.cuda.is_available() else False)
    return query_loader

def load_dataset(s_x, s_y, q_x, num_query):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    x_support, x_query = s_x, q_x
    y_support = s_y
    _classes = torch.unique(y_support.cpu(),sorted=False).to(device)
    support_idx = torch.stack(list(map(lambda c: y_support.eq(c).nonzero(as_tuple=False).squeeze(1), _classes)))
    xs = torch.cat([x_support[idx_list] for idx_list in support_idx])

    query_idx = torch.arange(num_query)
    xq = []
    for i in query_idx:
        xq.append(x_query[i])

    xq = torch.stack(xq)

    return xs, xq

class RelationBatchSampler(Sampler):
    def __init__(self, labels, num_classes, num_support, num_query, dataset, data_source=None):
        super().__init__(data_source)
        self.labels = labels
        self.num_classes = num_classes
        self.num_support = num_support
        self.num_query = num_query
        self.dataset = dataset

        self.classes, self.counts = torch.unique(self.labels, return_counts=True)
        self.classes = torch.LongTensor(self.classes)

        self.indexes = np.empty((len(self.classes), max(self.counts)), dtype=int) * np.nan
        self.indexes = torch.Tensor(self.indexes)
        for idx, label in enumerate(self.labels):
            label_idx = np.argwhere(self.classes == label).item()
            self.indexes[label_idx, np.where(np.isnan(self.indexes[label_idx]))[0][0]] = idx

    def __iter__(self):
        nc = self.num_classes
        classes_idxs = torch.arange(nc)

        if (self.dataset == 's'):
            ns = self.num_support
            batch_s = torch.LongTensor(ns * nc)
            for i, c in enumerate(self.classes[classes_idxs]):
                s_s = slice(i * ns, (i + 1) * ns)
                label_idx = torch.arange(len(self.classes)).long()[self.classes == c].item()
                batch_s[s_s] = self.indexes[label_idx][:ns]
            yield batch_s
        
        else:
            nq = self.num_query
            batch_q = torch.LongTensor(nq)
            for i in range(nq):
                s_q = slice(i, (i + 1))
                batch_q[s_q] = self.indexes[i][0]
            yield batch_q
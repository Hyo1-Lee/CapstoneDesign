import os
import torch
import numpy as np

from dataloader import load_dataset
from relationnet import RelationNetwork, Embedding

device = 'cuda' if torch.cuda.is_available() else 'cpu'
BASEDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Inference():
    args ={
        "manual_seed":7,
        "num_classes": 11,
        "num_support": 5,
        "num_query" : 3,
        "threshold":0.8
    }
    model = None
    embedding = None

    def __init__(self):
        np.random.seed(self.args['manual_seed'])
        torch.manual_seed(self.args['manual_seed'])
        torch.cuda.manual_seed(self.args['manual_seed'])
        
        checkpoint = torch.load(os.path.abspath(BASEDIR + '/relation/weight/model_best.pth'))

        in_channel = 3
        feature_dim = 64 * 3 * 3

        self.embedding = Embedding(in_channel).to(device)
        self.model = RelationNetwork(feature_dim).to(device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.embedding.load_state_dict(checkpoint['embedding_state_dict'])

    @torch.no_grad()
    def test(self, support, query, model, embedding):
        num_class = self.args['num_classes']
        num_support = self.args['num_support']
        num_query = self.args['num_query']
        threshold = self.args['threshold']

        model.eval()
        embedding.eval()

        support_data = next(iter(support))
        query_data = next(iter(query))

        s_x, s_y, q_x = support_data[0].to(device), support_data[1].to(device), query_data[0].to(device)
        x_support, x_query = load_dataset(s_x, s_y, q_x, num_query)

        support_vector = embedding(x_support)
        query_vector = embedding(x_query)

        _size = support_vector.size()

        support_vector = support_vector.view(num_class, num_support, _size[1], _size[2], _size[3]).sum(dim=1)
        support_vector = support_vector.repeat(num_query, 1, 1, 1)
        query_vector = torch.stack([x for x in query_vector for _ in range(num_class)])
        _concat = torch.cat((support_vector, query_vector), dim=1)
        y_pred = model(_concat).view(-1, num_class)
        y_pred,_ = torch.sort(y_pred, dim = 0)
        y_pred = y_pred[:5,:]
        mean = torch.mean(y_pred, dim=0)
        # print(mean)
        y_hat = mean.argmax()
        
        if mean[int(y_hat)] < threshold:
            print("It is not registered.")
            return 1
        elif list(range(num_class,0,-1))[int(y_hat)] == 1:
            print("It is background.")
            return 1
        else:
            print("class is:" ,list(range(num_class,0,-1))[int(y_hat)])
        return list(range(num_class,0,-1))[int(y_hat)]

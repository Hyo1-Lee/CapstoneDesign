import torch.nn as nn
from conv_block import ConvBlock

class Embedding(nn.Module):
    def __init__(self, in_channel=3, z_dim=64):
        super().__init__()
        self.block1 = ConvBlock(in_channel, z_dim, 3, max_pool=2)
        self.block2 = ConvBlock(z_dim, z_dim, 3, max_pool=2)
        self.block3 = ConvBlock(z_dim, z_dim, 3, max_pool=None, padding=1)
        self.block4 = ConvBlock(z_dim, z_dim, 3, max_pool=None, padding=1)

    def forward(self, x):
        out = self.block1(x)
        out = self.block2(out)
        out = self.block3(out)
        out = self.block4(out)

        return out

class RelationNetwork(nn.Module):
    def __init__(self, feature_dim):
        super().__init__()
        if feature_dim == 64:
            self.layer1 = ConvBlock(128, 64, 3, max_pool=2, padding=1)
            self.layer2 = ConvBlock(64, 64, 3, max_pool=2, padding=1)
        else:
            self.layer1 = ConvBlock(128, 64, 3, max_pool=2)
            self.layer2 = ConvBlock(64, 64, 3, max_pool=2)

        self.fc1 = nn.Linear(feature_dim, 8)
        self.fc2 = nn.Linear(8, 1)

        self.relu = nn.ReLU(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.view(out.size(0), -1)
        out = self.relu(self.fc1(out))
        out = self.sigmoid(self.fc2(out))

        return out
import os
import torch
from torch.utils.data import Dataset
import cv2
import numpy as np

BASEDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
q_dir = BASEDIR + '/data/query/'
s_dir = BASEDIR + '/data/support/'

def transform(image):
    image = cv2.resize(image, (84, 84), interpolation=cv2.INTER_LINEAR)

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    image = (image.astype(np.float32) / 255.0 - mean) / std
    
    image = np.transpose(image, (2, 0, 1))
    image = torch.from_numpy(image)
    
    return image
	
class SupportSet(Dataset):
    def __init__(self):
        super().__init__()
        self.x, self.y = self.make_support()

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def make_support(self):
        x = []
        y = []

        for root, _, files in os.walk(s_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        img = cv2.imread(os.path.join(root, file), cv2.IMREAD_COLOR)
                        img = transform(img)
                        x.append(img)
                        y.append(int(root.split('/')[-1]) - 1)

        y = torch.LongTensor(y)
        return x, y

class QuerySet(Dataset):
    def __init__(self):
        super().__init__()

        self.x, self.y = self.make_query()

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def make_query(self):
        x = []
        y = []

        for root, _, files in os.walk(q_dir):
             for i, file in enumerate(files):
                    if file.endswith('.jpg'):
                        img = cv2.imread(os.path.join(root, file), cv2.IMREAD_COLOR)
                        img = transform(img)
                        x.append(img)
                        y.append(i) 

        y = torch.LongTensor(y)
        return x, y

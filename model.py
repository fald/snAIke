import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x) # No need for an activation function here, just use the raw value.
        return x

    def save(self, filename="model.pth", model_folder_path="./model"):
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        torch.save(self.state_dict(), os.path.join(model_folder_path, filename))
        
    def load(self, filename="model.pth", model_folder_path="./model"):
        pass
    
    
class QTrainer:
    def __init__(self, model, alpha=0.001, gamma=0.9, optimizer=optim.Adam, loss_fn=nn.MSELoss):
        self.model = model
        self.alpha = alpha
        self.gamma = gamma
        self.optimizer = optimizer(self.model.parameters(), lr=self.alpha)
        # Loss function
        self.criterion = loss_fn()
        
        
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
        if os.path.exists(os.path.join(model_folder_path, filename)):
            self.load_state_dict(torch.load(os.path.join(model_folder_path, filename)))
    
    
class QTrainer:
    def __init__(self, model, alpha=0.001, gamma=0.9, optimizer=optim.Adam, loss_fn=nn.MSELoss):
        self.model = model
        self.alpha = alpha
        self.gamma = gamma
        self.optimizer = optimizer(self.model.parameters(), lr=self.alpha)
        # Loss function
        self.criterion = loss_fn()
        
    def train_step(self, state, action, reward, next_state, done):
        # Should be able to handle single or multiple inputs.
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # If multiple inputs, size is (n, x) with n = batch size
        # otherwise, size is (x)
        
        if len(state.shape) == 1:
            # Want to append a dimension, using torch.unsqueeze
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            # we also want to convert the single done value to a tuple
            done = (done, )
            
        # 1. Predicted Q-vals with curr state
        prediction = self.model(state)
        
        # 2. Q_new = R + gamma * max(Next predicted Q val)
        # clone the predictions, then get the argmax of the action to get the correct index (we want our action noted, not the 3-tuple)
        # Only if not done, otherwise we want the reward
        # Bellman eqn stuff from theory - though apparently I'm retarded.
        target = prediction.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new += self.gamma * torch.max(self.model(next_state[idx]))
                
            target[idx][torch.argmax(action).item()] = Q_new
            
        # Apply loss function
        # Empty gradient
        self.optimizer.zero_grad()
        loss = self.criterion(target, prediction)
        loss.backward() # apply backprop and gradients
        
        self.optimizer.step()
        
    
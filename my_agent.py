import torch
import random
import numpy as np
from collections import deque
from snake_game_ai import BLOCK_SIZE, SnakeGameAI, Direction, Point
from model import Linear_QNetwork, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
ALPHA = 0.001 # Learning rate
RANDOM_MAX = 20
# >= 0
RANDOM_MIN = 5

class Agent:
    def __init__(self, model_vals=(11, 256, 3)):
        self.number_of_games = 0
        self.epsilon = 0 # Random control
        self.gamma = 0.9 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        # Model vals are just the input, hidden, and output sizes.
        self.model = Linear_QNetwork(*model_vals)
        self.trainer = QTrainer(self.model, alpha=ALPHA, gamma=self.gamma)
    
    def get_state(self, game):
        head = game.head
        point_left = Point(head.x - BLOCK_SIZE, head.y)
        point_right = Point(head.x + BLOCK_SIZE, head.y)
        point_up = Point(head.x, head.y - BLOCK_SIZE)
        point_down = Point(head.x, head.y + BLOCK_SIZE) # Some DS3 disrespect.
        
        # Only 1 can be true
        dir_left = game.direction == Direction.LEFT
        dir_right = game.direction == Direction.RIGHT
        dir_up = game.direction == Direction.UP
        dir_down = game.direction == Direction.DOWN 
        
        # The state of the game, woo.
        # 11 vars: 
        #   danger straight, left, and right (3)
        #   current direction in absolute terms (4)
        #   food location, in absolute terms (4)
        state = [
            # Danger ahead
            (dir_right and game.check_collision(point_right)) 
            or (dir_left and game.check_collision(point_left))
            or (dir_up and game.check_collision(point_up))
            or (dir_down and game.check_collision(point_down)),
            
            # Danger to the rel right
            (dir_left and game.check_collision(point_up))
            or (dir_down and game.check_collision(point_left))
            or (dir_up and game.check_collision(point_right))
            or (dir_right and game.check_collision(point_down)),
            
            # Danger to the rel left
            (dir_right and game.check_collision(point_up))
            or (dir_down and game.check_collision(point_right))
            or (dir_up and game.check_collision(point_left))
            or (dir_left and game.check_collision(point_down)),
            
            # Current direction
            dir_left,
            dir_right,
            dir_up,
            dir_down,
            
            # Food location
            game.food.x < game.head.x, # Food to the left
            game.food.x > game.head.x, # Food to the right
            game.food.y < game.head.y, # Food above
            game.food.y > game.head.y, # Food below 
        ]
        
        return np.array(state, dtype=int) # dtype=int helps with bools to be 0 or 1
    
    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))
        
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
            
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)
    
    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)
    
    def get_action(self, state):
        # Random moves - exploration, versus the exploitation of a trained model.
        self.epsilon = max(RANDOM_MAX - self.number_of_games, RANDOM_MIN) / 100.0
        final_move = [0, 0, 0] # Ahead, right, left
        if random.random() < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state_0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1 # Decided
            
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    
    while True:
        # Get old state
        state_old = agent.get_state(game)
        
        # Get move based on the state
        final_move = agent.get_action(state_old)
        
        # Perform the move and get the new state
        rewards, game_over, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        
        # Train the short memory - one step
        agent.train_short_memory(state_old, final_move, rewards, state_new, game_over)
        
        # Remember who you are
        agent.remember(state_old, final_move, rewards, state_new, game_over)
        
        if game_over:
            # train the long (or 'replay' or 'experience replay') memory
            # plot the results
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.model.save()
            
            print('Game: {}\t\tScore: {}\tRecord: {}'.format(agent.number_of_games, score, record))

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.number_of_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == "__main__":
    train()
    
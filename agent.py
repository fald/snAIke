import torch
import random
import numpy as np
from collections import deque
from snake_game_ai import SnakeGameAI, Direction, Point

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
ALPHA = 0.001 # Learning rate


class Agent:
    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # Random control
        self.gamma = 0 # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        # TODO: Model and trainer
    
    def get_state(self, game):
        pass
    
    def remember(self, state, action, reward, next_state, game_over):
        pass
        
    def train_long_memory(self):
        pass
    
    def train_short_memory(self, state, action, reward, next_state, game_over):
        pass
    
    def get_action(self, state):
        pass


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
            # train the long (or 'replay' or 'experienced replay') memory
            # plot the results
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                # TODO: agents.model.save()
            
            print('Game: {} Score: {}\nRecord: {}'.format(agent.number_of_games, score, record))
            # TODO: plot


if __name__ == "__main__":
    train()
    
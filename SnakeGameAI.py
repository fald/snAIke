import pygame
from enum import Enum
import random
from collections import namedtuple
# import numpy as np

pygame.init()
font = pygame.font.Font("fonts/arial.ttf", 25)

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    
Point = namedtuple('Point', 'x, y')

# rgb easy colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
RED_2 = (120, 0, 0)
# GREEN = (0, 255, 0)
BLUE = (50, 50, 255)
BLUE_2 = (0, 0, 128)

BLOCK_SIZE = 20
SPEED = 20
# I'm special.
BACKGROUND_COLOR = BLACK
SNAKE_COLOR = BLUE
SNAKE_COLOR_OUTER = BLUE_2
FOOD_COLOR = RED
FOOD_COLOR_OUTER = RED_2
TEXT_COLOR = WHITE
# Less than half the BLOCK_SIZE
SNAKE_OUTLINE_SIZE = 3
FOOD_OUTLINE_SIZE = 4
WIDTH, HEIGHT = 640, 480

# Reward tweaking.
FAIL_REWARD = -10
FAIL_REWARD_GROWTH = 0
FOOD_REWARD = 10
FOOD_REWARD_GROWTH = 0
# Is surviving good? Not without improvement.
IDLE_REWARD = -0.1
IDLE_REWARD_GROWTH = -0.01
# In frames per snake length.
CUTOFF_POINT = 100


class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        
        # No need to recalculate this every frame - not sure how much that little optimization would be worth, but I assume jack shit.
        self.bounds = {
            'upper': 0,
            'lower': self.h - BLOCK_SIZE,
            'left': 0,
            'right': self.w - BLOCK_SIZE
        }
        # Initialize game state 
        self.reset()
    
    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def play_step(self, action):
        # Close game if needs be
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
                
        self.frame_iteration += 1
        
        # Move snake
        self._move_snake(action)
        self.snake.insert(0, self.head) # Should be in move?

        reward = 0
        
        # Check collision
        if self._check_collision() or (self.frame_iteration > CUTOFF_POINT * len(self.snake)): # Gives more time before death on each collection.
            reward += FAIL_REWARD * (FAIL_REWARD_GROWTH * self.score)
            game_over = True
            return game_over, self.score
        else:
            reward += IDLE_REWARD * self.frame_iteration
            game_over = False
        
        # Check food
        if self.food == self.head:
            reward += FOOD_REWARD * (FOOD_REWARD_GROWTH * self.score) # first one's free, baby.
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
        
        # Update screen and clock
        self._update_screen()
        self.clock.tick(SPEED)
        
        return reward, game_over, self.score
    
    def _place_food(self):
        # Randomly place food on the screen
        # 0 - w - 1, 0 - h - 1
        x = random.randint(0, (self.w - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        # If intersects with snake, try again
        if self.food in self.snake:
            self._place_food()
    
    def _check_collision(self, point=None):
        if point is None:
            point = self.head
        # Check if snake hits itself
        if point in self.snake[1:]:
            return True
        # Check if snake hits wall
        if point.x > self.bounds['right'] or point.x < self.bounds['left'] or point.y > self.bounds['lower'] or point.y < self.bounds['upper']:
            return True
        return False
    
    def _move_snake(self, action):
        # action = [straight, right, left], sum(action) = 1, this isn't weighted like it will/might be in the agent's eyes.
        # At least this is a better way than I did in the user-input version!
        clockwise_directions = (Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP)
        curr_index = clockwise_directions.index(self.direction)
        # Can use np.array_equal here, but I'm not sure if it's worth it.
        if action[1]:
            self.direction = clockwise_directions[(curr_index + 1) % 4]
        elif action[2]:
            self.direction = clockwise_directions[(curr_index - 1) % 4]
        
        x = self.head.x
        y = self.head.y
        match self.direction:
            case Direction.UP:
                y -= BLOCK_SIZE
            case Direction.DOWN:
                y += BLOCK_SIZE
            case Direction.LEFT:
                x -= BLOCK_SIZE
            case Direction.RIGHT:
                x += BLOCK_SIZE
        self.head = Point(x, y)
        
    def _update_screen(self):
        # Clear screen
        self.display.fill(BACKGROUND_COLOR)
        
        # Draw snek
        # Different for head?
        for point in self.snake:
            pygame.draw.rect(self.display, SNAKE_COLOR_OUTER, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, SNAKE_COLOR, 
                             pygame.Rect(point.x + SNAKE_OUTLINE_SIZE, point.y + SNAKE_OUTLINE_SIZE, 
                                         BLOCK_SIZE - 2 * SNAKE_OUTLINE_SIZE, BLOCK_SIZE - 2 * SNAKE_OUTLINE_SIZE))
        
        # Draw food
        pygame.draw.rect(self.display, FOOD_COLOR_OUTER, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, FOOD_COLOR, 
                         pygame.Rect(self.food.x + FOOD_OUTLINE_SIZE, self.food.y + FOOD_OUTLINE_SIZE, 
                                     BLOCK_SIZE - 2 * FOOD_OUTLINE_SIZE, BLOCK_SIZE - 2 * FOOD_OUTLINE_SIZE))
        
        # Draw score and finalize the update
        text = font.render("Score: " + str(self.score), True, TEXT_COLOR)
        self.display.blit(text, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    game = SnakeGameAI(WIDTH, HEIGHT)
    
    while True:
        game_over, score = game.play_step()
        if game_over:
            print("Final score: " + str(score))
            game.reset()

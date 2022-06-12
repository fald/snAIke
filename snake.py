import pygame
from enum import Enum
import random
from collections import namedtuple

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
RED2 = (120, 0, 0)
# GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLUE2 = (0, 0, 128)

BLOCK_SIZE = 20
SPEED = 20


class SnakeGame:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)]
        
        self.score = 0
        self.food = None
        self._place_food()
    
    def play_step(self):
        pass
    
    def _place_food(self):
        pass
    
    def _check_collision(self):
        pass
    
    def _move_snake(self):
        pass
    
    def _update_screen(self):
        pass


if __name__ == "__main__":
    pass

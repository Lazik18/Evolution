import sys
import os
import pygame
import numpy as np

pygame.init()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')

map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))

SIZE_CELL = 25
SIZE_OBJ = 23


class Cat:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)

    def update(self):
        pygame.draw.rect(screen, (42, 141, 156), self.rect, 0)


class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)

    def update(self):
        pygame.draw.rect(screen, (31, 52, 56), self.rect, 0)


class Food:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)

    def update(self):
        pygame.draw.rect(screen, (230, 103, 97), self.rect, 0)


screen = pygame.display.set_mode((700, 500))
all_obj = []

for i in range(0, map_img.get_width()):
    for j in range(0, map_img.get_height()):
        if map_img.get_at([i, j]) == pygame.color.Color(0, 0, 0):
            obj = Wall(i * SIZE_CELL, j * SIZE_CELL)
        elif map_img.get_at([i, j]) == pygame.color.Color(255, 0, 0):
            obj = Food(i * SIZE_CELL, j * SIZE_CELL)
        elif map_img.get_at([i, j]) == pygame.color.Color(0, 0, 255):
            obj = Cat(i * SIZE_CELL, j * SIZE_CELL)
        all_obj[i].append(obj)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_LEFT:
        #         rect.move_ip(-40, 0)
        #     elif event.key == pygame.K_RIGHT:
        #         rect.move_ip(40, 0)
        #     elif event.key == pygame.K_UP:
        #         rect.move_ip(0, -40)
        #     elif event.key == pygame.K_DOWN:
        #         rect.move_ip(0, 40)

    screen.fill(pygame.color.Color(80, 80, 80))
    for i in range(0, map_img.get_width()):
        for j in range(0, map_img.get_height()):
            all_obj[i][j].update()

    pygame.display.flip()

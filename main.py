import random
import sys
import os
import pygame

pygame.init()
random.seed()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')

map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))

SIZE_CELL = 10
SIZE_OBJ = 8
SIZE_POPULATION = 5

all_gen = []
for i in range(1, 6):
    file = open('gen/gen' + str(i) + '.txt', 'r')
    s = []
    for line in file:
        s += list(map(int, line.split(' ')))
    all_gen.append(s)
    file.close()
all_gen *= SIZE_POPULATION
random.shuffle(all_gen)


# 0 поворот налево на 45 +
# 1 поворот направо на 45 +
# 2 посмотреть (1 - пусто; 2 - еда; 3 - моб; 4 - стена; 5 - яд)+
# 3 преобразовать яд в еду
# 4 съесть
# 5 перейти вперед
# 6-63 переход на такое кол-во клеток по таблице
class Mob:
    def __init__(self, x, y, gen):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)
        self.id = 1
        self.orientation = random.randint(0, 7)
        self.gen = gen
        self.counter = 0
        self.look = [x // SIZE_CELL, y // SIZE_CELL]
        self.sees = None
        self.direction(0)
        self.energy = 20

    def update(self):
        if self.gen[self.counter] == 0:
            self.direction(-1)
            self.energy -= 1
        elif self.gen[self.counter] == 1:
            self.direction(+1)
            self.energy -= 1
        elif self.gen[self.counter] == 2:
            self.looking()
            self.energy -= 1
        pygame.draw.rect(screen, (42, 141, 156), self.rect, 0)

    def direction(self, arg: int):
        self.orientation = (self.orientation + arg) % 8
        if self.orientation == 0:
            self.look = [self.look[0], self.look[1] + 1]
        elif self.orientation == 1:
            self.look = [self.look[0] + 1, self.look[1] + 1]
        elif self.orientation == 2:
            self.look = [self.look[0] + 1, self.look[1]]
        elif self.orientation == 3:
            self.look = [self.look[0] + 1, self.look[1] - 1]
        elif self.orientation == 4:
            self.look = [self.look[0], self.look[1] - 1]
        elif self.orientation == 5:
            self.look = [self.look[0] - 1, self.look[1] - 1]
        elif self.orientation == 6:
            self.look = [self.look[0] - 1, self.look[1]]
        elif self.orientation == 7:
            self.look = [self.look[0] - 1, self.look[1] + 1]

    def looking(self):
        if type(self.sees) is None:
            self.counter += 1
        elif type(self.sees) == Food:
            self.counter += 2
        elif type(self.sees) == Mob:
            self.counter += 3
        elif type(self.sees) == Wall:
            self.counter += 4
        elif type(self.sees) == Poison:
            self.counter += 5


class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)
        self.id = 2

    def update(self):
        pygame.draw.rect(screen, (31, 52, 56), self.rect, 0)


class Food:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)
        self.id = 3

    def update(self):
        pygame.draw.rect(screen, (230, 103, 97), self.rect, 0)


class Poison:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)
        self.id = 4

    def update(self):
        pygame.draw.rect(screen, (118, 255, 122), self.rect, 0)


screen = pygame.display.set_mode((700, 625))
all_obj = []

for i in range(0, map_img.get_width()):
    s = []
    for j in range(0, map_img.get_height()):
        obj = None
        if map_img.get_at([i, j]) == pygame.color.Color(0, 0, 0):
            obj = Wall(i * SIZE_CELL, j * SIZE_CELL)
        elif map_img.get_at([i, j]) == pygame.color.Color(255, 0, 0):
            r = random.randint(1, 10)
            if r == 1:
                obj = Poison(i * SIZE_CELL, j * SIZE_CELL)
            else:
                obj = Food(i * SIZE_CELL, j * SIZE_CELL)
        elif map_img.get_at([i, j]) == pygame.color.Color(0, 0, 255):
            obj = Mob(i * SIZE_CELL, j * SIZE_CELL, all_gen[0])
            all_gen.pop(0)
        s.append(obj)
    all_obj.append(s)

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
            if all_obj[i][j]:
                if type(all_obj[i][j]) == Mob:

                    all_obj[i][j].sees = all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]]

                all_obj[i][j].update()

    pygame.display.flip()

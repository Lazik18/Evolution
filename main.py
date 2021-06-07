import random
import sys
import os
import pygame

pygame.init()
random.seed()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))

# ======Константы======
SIZE_CELL = 12
SIZE_OBJ = 10
SIZE_POPULATION = 5
# Команды:
MOB_TURN_LEFT = 0  # 0 поворот налево на 45
MOB_TURN_RIGHT = 1  # 1 поворот направо на 45
MOB_LOOK = 2  # 2 посмотреть (1 - пусто; 2 - еда; 3 - моб; 4 - стена; 5 - яд)
MOB_TRANSFORM = 3  # 3 преобразовать яд в еду
MOB_EAT = 4  # 4 съесть
MOB_GO_FORWARD = 5  # 5 перейти вперед
# =====================

# ====== Распределение генов ======
all_gen = []  # Массив всех генотипов
for i in range(1, 6):
    file = open('gen/gen' + str(i) + '.txt', 'r')
    s = []
    for line in file:
        s += list(map(int, line.replace('\t', ' ').split(' ')))
    all_gen.append(s)
    file.close()
all_gen *= SIZE_POPULATION
random.shuffle(all_gen)
# =================================


# ====== Глобальные функции ======
def get_object(x: int, y: int):
    return all_obj[x][y]

def set_object(x: int, y: int, new_obj):
    all_obj[x][y] = new_obj
# ================================


class Mob:
    def __init__(self, x, y, gen):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)
        self.orientation = random.randint(0, 7)
        self.gen = gen
        self.counter = 0
        self.sees = None
        self.energy = 20
        self.life = 0
        self.in_loop = 0

    def update(self):
        if self.gen[self.counter] == MOB_TURN_LEFT:
            self.turn(-1)
        elif self.gen[self.counter] == MOB_TURN_RIGHT:
            self.turn(1)
        elif self.gen[self.counter] == MOB_LOOK:
            self.look()
        elif self.gen[self.counter] == MOB_TRANSFORM:
            self.transform()
        elif self.gen[self.counter] == MOB_EAT:
            self.eat()
        elif self.gen[self.counter] == MOB_GO_FORWARD:
            self.forward()
        else:
            self.nothing(self.gen[self.counter])
        pygame.draw.rect(screen, (150, 120, 240), self.rect, 0)
        self.in_loop = 0
        self.energy -= 1
        if self.energy <= 0:
            set_object((self.rect.x // SIZE_CELL) - 1, (self.rect.y // SIZE_CELL) - 1, None)
            del self

    def turn(self, arg: int):
        self.orientation = (self.orientation + arg) % 8

    def look(self):
        self.in_loop += 1
        x, y = self.get_look()
        front = get_object(x, y)
        temp_count = self.counter
        can_see = [None, Food, Mob, Wall, Poison]
        for o in range(0, len(can_see)):
            if type(front) is can_see[o]:
                temp_count += (o + 1)
                break
        self.counter = temp_count % len(self.gen)

    def transform(self):
        x, y = self.get_look()
        front = get_object(x, y)
        if type(front) == Poison:
            set_object(x, y, Food(x, y))
        self.nothing(1)

    def eat(self):
        x, y = self.get_look()
        front = get_object(x, y)
        if type(front) == Food:
            set_object(x, y, None)
            self.energy += 10
            self.nothing(1)
        elif type(front) == Poison:
            del self

    def forward(self):
        x, y = self.get_look()
        front = get_object(x, y)
        if type(front) is None:
            set_object(x, y, Mob())
            #se
        self.nothing(1)

    def nothing(self, arg: int):
        if self.in_loop <= 15:
            self.in_loop += 1
            temp_count = self.counter + arg
            self.counter = temp_count % len(self.gen)
        else:
            self.counter = (self.counter + 1) % len(self.gen)

    def get_look(self):
        x, y = (self.rect.x // SIZE_CELL) - 1, (self.rect.y // SIZE_CELL) - 1

        if self.orientation == 0:
            return x, y + 1
        elif self.orientation == 1:
            return x + 1, y + 1
        elif self.orientation == 2:
            return x + 1, y
        elif self.orientation == 3:
            return x + 1, y - 1
        elif self.orientation == 4:
            return x, y - 1
        elif self.orientation == 5:
            return x - 1, y - 1
        elif self.orientation == 6:
            return x - 1, y
        elif self.orientation == 7:
            return x - 1, y + 1


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


class Poison:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 1, y + 1, SIZE_OBJ, SIZE_OBJ)

    def update(self):
        pygame.draw.rect(screen, (118, 255, 122), self.rect, 0)


screen = pygame.display.set_mode((700, 625))
clock = pygame.time.Clock()
current_ticks = 10
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

        elif event.type == pygame.MOUSEWHEEL:
            current_ticks += (event.y * 10)
            if current_ticks < 1:
                current_ticks = 1

    screen.fill(pygame.color.Color(80, 80, 80))
    for i in range(0, map_img.get_width()):
        for j in range(0, map_img.get_height()):
            if all_obj[i][j]:
                if all_obj[i][j] is not None:
                    all_obj[i][j].update()

    pygame.display.flip()
    clock.tick(current_ticks)

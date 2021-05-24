import random
import sys
import os
import pygame

pygame.init()
random.seed()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')

map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))

SIZE_CELL = 12
SIZE_OBJ = 10
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


MOB_TURN_LEFT = 0
MOB_TURN_RIGHT = 1
MOB_LOOK = 2
MOB_TRANSFORM = 3
MOB_EAT = 4
MOB_GO_FORWARD = 5

# 0 поворот налево на 45 +
# 1 поворот направо на 45 +
# 2 посмотреть (1 - пусто; 2 - еда; 3 - моб; 4 - стена; 5 - яд)+
# 3 преобразовать яд в еду +
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

    def __str__(self):
        return "> id: %s\n> look: %s\tsees: %s\n> energy: %s\n> command: %s\ngen: %s" % (self.id, self.look, self.sees, self.energy, self.gen[self.counter], self.gen)

    def next_counter(self):
        temp_count = self.counter
        if self.gen[self.counter] < 6:
            if self.gen[self.counter] != MOB_LOOK
                temp_count += 1

            else:
                can_see = [None, Food, Mob, Wall, Poison]
                for o in range(5):
                    if type(self.sees) == can_see[o]:
                        temp_count += (o+1)
                        break

        else:
            temp_count += self.gen[self.counter]

        if temp_count > len(self.gen):
            temp_count = self.gen[0]
        self.counter = temp_count

    def update(self):
        pygame.draw.rect(screen, (42, 141, 156), self.rect, 0)
        self.look = self.get_look()

    def get_look(self):
        x, y = self.rect.x//SIZE_CELL, self.rect.y//SIZE_CELL

        if self.orientation == 0:
            return [x, y + 1]
        elif self.orientation == 1:
            return [x + 1, y + 1]
        elif self.orientation == 2:
            return [x + 1, y]
        elif self.orientation == 3:
            return [x + 1, y - 1]
        elif self.orientation == 4:
            return [x, y - 1]
        elif self.orientation == 5:
            return [x - 1, y - 1]
        elif self.orientation == 6:
            return [x - 1, y]
        elif self.orientation == 7:
            return [x - 1, y + 1]

    def direction(self, arg: int):
        self.orientation = (self.orientation + arg) % 8



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

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            try:
                obj = all_obj[event.pos[0] // SIZE_CELL][event.pos[1] // SIZE_CELL]

                if event.button == 1:
                    print('click (x: %s y: %s)' % (event.pos[0]//SIZE_CELL, event.pos[1]//SIZE_CELL))
                    print(obj)

            except IndexError:
                pass

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
                if type(all_obj[i][j]) is Mob:

                    #Альтернативный метод работы с мобами
                    mob_sees = all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]]
                    mob_status = all_obj[i][j].gen[all_obj[i][j].counter]

                    if mob_status == MOB_LOOK:
                        all_obj[i][j].sees = all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]]
                    else:
                        all_obj[i][j].sees = None

                    if mob_status == MOB_TRANSFORM:
                        if type(mob_sees) == Poison:
                            all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] = Food(mob_sees.rect.x, mob_sees.rect.y)

                    elif mob_status == MOB_EAT:
                        if type(mob_sees) == Food:
                            all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] = None

                    elif mob_status == MOB_TURN_LEFT:
                        all_obj[i][j].direction(-1)

                    elif mob_status == MOB_TURN_RIGHT:
                        all_obj[i][j].direction(1)

                    elif mob_status == MOB_GO_FORWARD:
                        if all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] is None:
                            all_obj[i][j].rect = pygame.rect.Rect(all_obj[i][j].look[0]*SIZE_CELL, all_obj[i][j].look[1]*SIZE_CELL, SIZE_OBJ, SIZE_OBJ)
                            all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] = all_obj[i][j]
                            all_obj[i][j] = None

                    if all_obj[i][j] is not None:
                        all_obj[i][j].next_counter()


                    # if type(all_obj[i][j].sees) is Food:
                    #     # all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] # точно food.
                    #     # all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]] = all_obj[i][j].sees
                    #     pass
                if all_obj[i][j] is not None:
                    all_obj[i][j].update()

    clock.tick(30)
    pygame.display.flip()

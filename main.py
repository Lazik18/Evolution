import random
import sys
import os
import pygame
import time
import copy

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
        s += list(map(int, line.replace('\t', ' ').split(' ')))
    all_gen.append(s)
    file.close()

last_gens = copy.deepcopy(all_gen)
all_gen *= SIZE_POPULATION
random.shuffle(all_gen)

MOB_TURN_LEFT = 0
MOB_TURN_RIGHT = 1
MOB_LOOK = 2
MOB_TRANSFORM = 3
MOB_EAT = 4
MOB_GO_FORWARD = 5

FOOD_ENERGY_BOOST = 10
MOB_ENERGY = 20

COMMAND_AMOUNT = 24


# 0 поворот налево на 45 +
# 1 поворот направо на 45 +
# 2 посмотреть (1 - пусто; 2 - еда; 3 - моб; 4 - стена; 5 - яд)+
# 3 преобразовать яд в еду +
# 4 съесть
# 5 перейти вперед

# 6-63 переход на такое кол-во клеток по таблице



def map_move(the_obj):
    map_remove(the_obj)
    the_obj.coordinates = the_obj.get_look()
    all_obj[the_obj.look[0]][the_obj.look[1]] = the_obj
    the_obj.look = the_obj.get_look()


def map_remove(the_obj):
    all_obj[the_obj.coordinates[0]][the_obj.coordinates[1]] = None


def map_transform(the_obj):
    all_obj[the_obj.coordinates[0]][the_obj.coordinates[1]] = Food(the_obj.coordinates[0], the_obj.coordinates[1])


class Mob:
    def __init__(self, x, y, gen, id, colour=(42, 141, 156), energy: int = 20, life: int = 0):
        self.coordinates = [x, y]
        self.id = id
        self.orientation = random.randint(0, 7)
        self.gen = gen
        self.counter = 0
        self.look = self.get_look()
        self.sees = None
        self.direction(0)
        self.energy = energy
        self.colour = colour
        self.life = life

    def __str__(self):
        return "> id: %s\n> look: %s\tsees: %s\n> energy: %s\n> command: %s\ngen: %s\ngenotype: %s\n life: %s\n coor: %s" % (
            self.id, self.look, self.sees, self.energy, self.gen[self.counter], self.gen, sum(self.gen), self.life,
            self.coordinates)

    def next_counter(self):
        temp_count = self.counter

        if self.gen[self.counter] < 6:
            if self.gen[self.counter] != MOB_LOOK:
                temp_count += 1

            else:
                can_see = [Food, Mob, Wall, Poison]
                for o in range(0, len(can_see)):
                    if type(self.sees) is can_see[o]:
                        temp_count += (o + 2)
                        break
                else:
                    temp_count += 1

        else:
            temp_count += self.gen[self.counter]

        self.counter = temp_count % len(self.gen)

    def update(self):
        status = self.gen[self.counter]
        if status == MOB_GO_FORWARD:
            # Проверяем, если впереди клетка пустая
            if self.sees is None:
                self.move()

        elif status == MOB_LOOK:
            pass
            # возможно баг

        elif status == MOB_EAT:
            self.eat()

        elif status == MOB_TRANSFORM:
            self.transform_poison()

        elif status == MOB_TURN_RIGHT:
            self.direction(1)

        elif status == MOB_TURN_LEFT:
            self.direction(-1)

        self.next_counter()
        self.look = self.get_look()
        self.energy -= 1

        if self.energy <= 0:
            map_remove(self)

    def can_be_eaten(self, by_obj):
        return False

    def eat(self):
        if self.sees is not None:
            if self.sees.can_be_eaten(self):
                if type(self.sees) is Food:
                    self.energy += FOOD_ENERGY_BOOST
                    # исправить
                    map_remove(self.sees)
                elif type(self.sees) is Poison:
                    map_remove(self)

    def move(self):
        map_move(self)

    def transform_poison(self):
        if type(self.sees) is Poison:
            map_transform(self.sees)

    def get_look(self):
        x, y = self.coordinates[0], self.coordinates[1]

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
        self.coordinates = [x, y]
        self.id = 2
        self.colour = (31, 52, 56)

    def can_be_eaten(self, by_obj):
        return False


class Food:
    def __init__(self, x, y):
        self.coordinates = [x, y]
        self.id = 3
        self.colour = (230, 103, 97)

    def can_be_eaten(self, by_obj):
        return True


class Poison:
    def __init__(self, x, y):
        self.coordinates = [x, y]
        self.id = 4
        self.colour = (118, 255, 122)

    def can_be_eaten(self, by_obj):
        return True


screen = pygame.display.set_mode((700, 625))


def draw_map():
    obj_map = []
    for i in range(0, map_img.get_width()):
        s = []
        for j in range(0, map_img.get_height()):
            _obj = None
            if map_img.get_at([i, j]) == pygame.color.Color(0, 0, 0):
                _obj = Wall(i, j)
            elif map_img.get_at([j, i]) == pygame.color.Color(255, 0, 0):
                r = random.randint(1, 10)
                if r == 1:
                    _obj = Poison(i, j)
                else:
                    _obj = Food(i, j)
            elif map_img.get_at([i, j]) == pygame.color.Color(0, 0, 255):
                _obj = Mob(i, j, all_gen[0], i * j + i + j,
                           (sum(all_gen[0]) % 140, sum(all_gen[0]) % 210, sum(all_gen[0]) % 55), MOB_ENERGY)
                all_gen.pop(0)
            s.append(_obj)
        obj_map.append(s)

    return obj_map


clock = pygame.time.Clock()
current_ticks = 10
evo_life = 0

all_obj = draw_map()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            try:
                obj = all_obj[event.pos[0] // SIZE_CELL][event.pos[1] // SIZE_CELL]

                if event.button == 1:
                    print('click (x: %s y: %s)' % (event.pos[0] // SIZE_CELL, event.pos[1] // SIZE_CELL))
                    print(obj)

            except IndexError:
                pass

        elif event.type == pygame.MOUSEWHEEL:
            current_ticks += (event.y * 10)
            if current_ticks < 1:
                current_ticks = 1

    screen.fill(pygame.color.Color(80, 80, 80))

    evo_life += 1

    mob_survived = []

    for i in range(0, map_img.get_width()):
        for j in range(0, map_img.get_height()):
            if all_obj[i][j] is not None:
                if type(all_obj[i][j]) is Mob:
                    mob_survived.append(all_obj[i][j])

                    all_obj[i][j].sees = all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]]
                    if all_obj[i][j].life <= evo_life:
                        all_obj[i][j].life += 1
                        all_obj[i][j].update()

    for i in range(0, map_img.get_width()):
        for j in range(0, map_img.get_height()):
            if all_obj[i][j] is not None:
                pygame.draw.rect(screen, all_obj[i][j].colour, pygame.Rect(all_obj[i][j].coordinates[0] * SIZE_CELL + 1,
                                                                           all_obj[i][j].coordinates[1] * SIZE_CELL + 1,
                                                                           SIZE_OBJ, SIZE_OBJ))

    if len(mob_survived) <= 5:
        print(evo_life)
        evo_life = 0
        if len(mob_survived) > 0:
            for i in range(5):
                all_gen.append(mob_survived[i % len(mob_survived)].gen)

            last_gens = copy.deepcopy(all_gen)

        else:
            all_gen = copy.deepcopy(last_gens)

        all_gen += copy.deepcopy(all_gen) * 4

        for i in range(5):
            r1 = random.randint(0, COMMAND_AMOUNT)
            r2 = random.randint(1, COMMAND_AMOUNT+1)
            all_gen[i][r1] = r2-1

        random.shuffle(all_gen)
        all_obj = draw_map()

    pygame.display.flip()
    clock.tick(current_ticks)
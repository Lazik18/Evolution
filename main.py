import random
import sys
import os
import pygame
import copy
import csv

pygame.init()  # инициализация библиотеки
random.seed()

game_folder = os.path.dirname(__file__)  # Определение пути с игрой
img_folder = os.path.join(game_folder, 'img')  # Определение пути к пнг файлам

map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))  # путь к карте

SIZE_CELL = 12  # Размер клетки (для отрисовки)
SIZE_OBJ = 10  # Размер объекта (для отрисовки)
SIZE_POPULATION = 10  # Размер популяции на один ген

all_gen = []  # здесь мы из файлов gen1-5 считываем гены в список, чтоб потом раздать их
for i in range(1, 6):
    file = open('gen/gen' + str(i) + '.txt', 'r')
    s = []
    for line in file:
        s += list(map(int, line.replace('\t', ' ').split(' ')))
    all_gen.append(s)
    file.close()

last_gens = copy.deepcopy(all_gen)  # список с выживщими мобами
all_gen *= SIZE_POPULATION  # умножаем, чтоб сделать 50 генов
random.shuffle(all_gen)  # мешаем их, чтоб потом раздать в случайном порядке

# тут мы для удобства сделали команды константами
MOB_TURN_LEFT, MOB_TURN_RIGHT, MOB_LOOK, MOB_TRANSFORM, MOB_EAT, MOB_GO = 0, 1, 2, 3, 4, 5

# столько дается энергии за съеденную еду
FOOD_ENERGY_BOOST, MOB_ENERGY = 10, 100

# кол-во команд всего (изначально их было 64)

COMMAND_AMOUNT, MOB_FREE_COMMAND = 35, 13


# 0 поворот налево на 45 +
# 1 поворот направо на 45 +
# 2 посмотреть (1 - пусто; 2 - еда; 3 - моб; 4 - стена; 5 - яд)+
# 3 преобразовать яд в еду +
# 4 съесть
# 5 - 12 переход по направлению *!ПОЗИЦИЯ ЗРЕНИЯ НЕ МЕНЯЕТСЯ

# 13-63 переход на такое кол-во клеток по таблице


def map_move(the_obj, where):  # тут происходит отрисовка и передвежение мобов на карте
    if all_obj[where[0]][where[1]] is None:
        map_remove(the_obj)
        the_obj.coordinates = where
        all_obj[where[0]][where[1]] = the_obj
        the_obj.look = the_obj.get_look()


def map_remove(the_obj):  # удаляем объекты с карты
    all_obj[the_obj.coordinates[0]][the_obj.coordinates[1]] = None


def map_transform(the_obj):  # изменение яда на еду (вызывают мобы)
    all_obj[the_obj.coordinates[0]][the_obj.coordinates[1]] = Food(the_obj.coordinates[0], the_obj.coordinates[1])


class Mob:
    def __init__(self, x, y, gen, id, colour=(42, 141, 156), energy: int = 20, life: int = 0):
        self.coordinates = [x, y]
        self.id = id
        self.orientation = random.randint(0, 7)  # изначально задается случайное направление куда он смотрит
        self.gen = gen  # генотип моба
        self.counter = 0  # счетчик, указывающий на текущую команду
        self.look = self.get_look()  # объект на который он смотрит
        self.sees = None
        self.direction(0)
        self.energy = energy
        self.colour = colour
        self.life = life  # кол-во прожитых раундов

    def __str__(self):  # позволяет вывести инфу о мобе, если тык в него на карте
        return "> id: %s\n> look: %s\tsees: %s\n> energy: %s\n> command: %s\ngen: %s\ngenotype: %s\n life: %s\n coor: %s" % (
            self.id, self.look, self.sees, self.energy, self.gen[self.counter], self.gen, sum(self.gen), self.life,
            self.coordinates)

    def next_counter(self, rec=0):  # тут происходит управление счетчиком
        temp_count = self.counter

        if self.gen[self.counter] < MOB_FREE_COMMAND or rec >= 10:  # если команда, онзачает какое-то действие
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
            self.counter = temp_count % len(self.gen)
            self.energy -= 1

        else:  # команды 13-31
            temp_count += self.gen[self.counter]
            self.counter = temp_count % len(self.gen)
            self.update(rec + 1)

    def update(self, rec=0):  # метод, который вызывается у всех классов, для изменения их состояния
        status = self.gen[self.counter]

        if MOB_GO + 7 > status >= MOB_GO:
            self.move(status - MOB_GO)

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

        self.next_counter(rec)
        self.look = self.get_look()

        if self.energy <= 0:
            map_remove(self)

    def can_be_eaten(self, by_obj):
        return False
        # if self.energy < by_obj.energy:
        #     return by_obj.energy - self.energy
        # else:
        #     return 0

    def eat(self):  # КУСЬ (если можем)
        if self.sees is not None:
            if self.sees.can_be_eaten(self):

                if type(self.sees) is Food:
                    self.energy += FOOD_ENERGY_BOOST
                    map_remove(self.sees)
                elif type(self.sees) is Poison:
                    self.energy += FOOD_ENERGY_BOOST
                    map_remove(self)

    def move(self, where):  # передвижение, а так же если мы наступаем в еду или яд, мы ее кусаем
        self.eat()
        map_move(self, self.get_look(orientation=where))

    def transform_poison(self):  # вызов функии превращения яда в еду
        if type(self.sees) is Poison:
            map_transform(self.sees)

    # эта функция позволяет нам определить куда смотрит клетка, когда крутится
    def get_look(self, coordinates: list = None, orientation=None):

        if orientation is None:
            orientation = self.orientation

        if coordinates is None:
            x, y = self.coordinates[0], self.coordinates[1]
        else:
            x, y = coordinates[0], coordinates[1]

        if orientation == 0:
            return [x, y + 1]
        elif orientation == 1:
            return [x + 1, y + 1]
        elif orientation == 2:
            return [x + 1, y]
        elif orientation == 3:
            return [x + 1, y - 1]
        elif orientation == 4:
            return [x, y - 1]
        elif orientation == 5:
            return [x - 1, y - 1]
        elif orientation == 6:
            return [x - 1, y]
        elif orientation == 7:
            return [x - 1, y + 1]

    def direction(self, arg: int):
        self.orientation = (self.orientation + arg) % 8


class Wall:
    def __init__(self, x, y):
        self.coordinates = [x, y]
        self.id = 2
        self.colour = (31, 52, 56)

    def can_be_eaten(self, by_obj):
        return 0


class Food:
    def __init__(self, x, y):
        self.coordinates = [x, y]
        self.id = 3
        self.colour = (230, 103, 97)

    def can_be_eaten(self, by_obj):  # функиция позволяющяя узнать, можно ли кусь этот объект
        return FOOD_ENERGY_BOOST


class Poison:
    def __init__(self, x, y):
        self.coordinates = [x, y]
        self.id = 4
        self.colour = (118, 255, 122)

    def can_be_eaten(self, by_obj):
        return -100


screen = pygame.display.set_mode((1500, 750))  # наше окно с симуляцией


def draw_map():  # функция отрисовки карты из карты.пнг (лежит в папке img)
    obj_map = []
    for i in range(0, map_img.get_width()):
        s = []
        for j in range(0, map_img.get_height()):
            _obj = None
            if map_img.get_at([i, j]) == pygame.color.Color(0, 0, 0):  # определяя цвет на рисунке, мы раставляем мобов,
                _obj = Wall(i, j)  # стены, яд и еду
            elif map_img.get_at([i, j]) == pygame.color.Color(255, 0, 0):
                r = random.randint(1, 2)
                if r == 1:
                    _obj = Poison(i, j)
                else:
                    _obj = Food(i, j)
            elif map_img.get_at([i, j]) == pygame.color.Color(0, 0, 255):
                _obj = Mob(i, j, all_gen[0], i * j + i + j,
                           (sum(all_gen[0]) % 140, sum(all_gen[0]) % 55, sum(all_gen[0]) % 255), MOB_ENERGY)
                all_gen.pop(0)  # удаляем из пула генов, ген, который использовали
            s.append(_obj)
        obj_map.append(s)

    return obj_map


clock = pygame.time.Clock()
current_ticks = 10  # условно, скорость отрисовки
evo_life = 0  # кол-во раундов в одной симуляции
evo_years = 1  # кол-во симуляций

all_obj = draw_map()

while evo_life < 100000:
    for event in pygame.event.get():  # закрытие окна
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:  # клик по мобу, чтоб вызвать сведения о нем
            try:
                obj = all_obj[event.pos[0] // SIZE_CELL][event.pos[1] // SIZE_CELL]

                if event.button == 1:
                    print('click (x: %s y: %s)' % (event.pos[0] // SIZE_CELL, event.pos[1] // SIZE_CELL))
                    print(obj)

            except IndexError:
                pass

        elif event.type == pygame.MOUSEWHEEL:  # круть колесико, чтоб изменить скорость
            current_ticks += (event.y * 10)
            if current_ticks < 1:
                current_ticks = 1

    f = open('data.csv', 'a', encoding='UTF8', newline='')  # собираем инфу для графиков
    writer = csv.writer(f)

    screen.fill(pygame.color.Color(80, 80, 80))

    evo_life += 1

    mob_survived = []

    for i in range(0, map_img.get_width()):  # поклеточная отрисовка и логика
        for j in range(0, map_img.get_height()):
            if all_obj[i][j] is not None:
                if type(all_obj[i][j]) is Mob:
                    mob_survived.append(all_obj[i][j])

                    all_obj[i][j].sees = all_obj[all_obj[i][j].look[0]][all_obj[i][j].look[1]]
                    if all_obj[i][j].life <= evo_life:
                        all_obj[i][j].life += 1
                        all_obj[i][j].update()
            else:
                if random.randint(1, 2000) == 1:
                    if random.randint(1, 10) == 1:
                        all_obj[i][j] = Poison(i, j)
                    else:
                        all_obj[i][j] = Food(i, j)

    for i in range(0, map_img.get_width()):
        for j in range(0, map_img.get_height()):
            if all_obj[i][j] is not None:
                pygame.draw.rect(screen, all_obj[i][j].colour, pygame.Rect(all_obj[i][j].coordinates[0] * SIZE_CELL + 1,
                                                                           all_obj[i][j].coordinates[1] * SIZE_CELL + 1,
                                                                           SIZE_OBJ, SIZE_OBJ))

    if len(mob_survived) <= 5:  # работа с выжившими генами
        all_gen = []
        evo_years += 1

        mob_s_text = " | "
        if len(mob_survived) > 0:
            for i in range(5):
                all_gen.append(mob_survived[i % len(mob_survived)].gen)
                mob_s_text += "%s (%s)   " % (
                    mob_survived[i % len(mob_survived)].energy, sum((mob_survived[i % len(mob_survived)].gen)))

            last_gens = copy.deepcopy(all_gen)

        else:
            all_gen = copy.deepcopy(last_gens)

        for i in range(5):
            for j in range(SIZE_POPULATION - 1):
                all_gen.append(copy.deepcopy(all_gen[i]))

        for i in range(5):  # тут происходит мутация трех случ. команд, у каждого пяти мобов с разными генами
            for j in range(3):
                r1 = random.randint(0, COMMAND_AMOUNT)
                r2 = random.randint(1, COMMAND_AMOUNT + 1)
                # print('all_gen', all_gen[i], len(all_gen), len(all_gen[i]))
                all_gen[i][r1] = r2 - 1

        random.shuffle(all_gen)  # опять мешаем гены, чтоб потом раздать
        # print(evo_years, mob_s_text, evo_life)
        writer.writerow([evo_life])
        f.flush()
        evo_life = 0

        all_obj = draw_map()

    f.close()
    pygame.display.flip()
    clock.tick(current_ticks)

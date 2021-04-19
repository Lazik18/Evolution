import pygame
import os

# настройка папки ассетов
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
sound_folder = os.path.join(game_folder, 'sound')
player_img = pygame.image.load(os.path.join(img_folder, 'cat.png'))
map_img = pygame.image.load(os.path.join(img_folder, 'map.png'))

WIDTH = 360
HEIGHT = 480
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Map:
    def __init__(self):
        self.x = map_img.get_width()
        self.y = map_img.get_height()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self):
        self.rect.x -= 3
        if self.rect.right < 0:
            self.rect.left = WIDTH
            meow.play()


# Создаем игру и окно
field = Map()
pygame.init()
pygame.mixer.init()
meow = pygame.mixer.Sound(os.path.join(sound_folder, 'meow.mp3'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evo")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)


# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(BLUE)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()

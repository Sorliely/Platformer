import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path #проверяет путь файла
"""можно прочитать описание класса Platform там все четко описано что и как делать с объектами"""
pygame.init()
clock = pygame.time.Clock()
fps = 60
#создание окна
win_width = 1000
win_heigth = 1000

win = pygame.display.set_mode((win_heigth, win_width))
pygame.display.set_caption('platform')

#размер текста в игре
font_score = pygame.font.SysFont('Bauhause 93', 30)
font = pygame.font.SysFont('Bauhaus 93', 70)
#цвет


#определить игровые параметры
title_size = 50   #размер сетки
game_over = 0
main_menu = True
level = 7
max_levels = 8
score = 0
#цвет
white = (255, 255, 255)
blue = (0, 0, 255)
#задний фон игры сама картинка/ изображения
sun_img = pygame.image.load('sun.png')
bg_img = pygame.image.load('sky.png')
restart_img = pygame.image.load('restart_btn.png')
start_img = pygame.image.load('start_btn.png')
exit_img = pygame.image.load('exit_btn.png')


def draw_text(text, font, text_color, x, y):
    """рисует текст в игре например счет монет или конец игры"""
    img = font.render(text, True , text_color)
    win.blit(img,(x, y))
#функция для сброса уровня
def reset_level(level):
    player.reset(100, win_heigth - 130)
    #удоляет вск группы
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    #загрузить даные мира и создать его (снова)
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


class Button():
    """класс с кнопками рестарт"""
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False #определяет нажал ли я на кнопку


    def draw(self):
        action = False
        key = pygame.key.get_pressed()
        """рисует кнопку"""
        #даёт текущую позицию курсора мыши
        pos = pygame.mouse.get_pos()
        #проверяет наведение мыши и нажатие на кнопку
        """если курсор мыши приближается к значку рестарт функция 
           collidepoint определитт приближение зарание """
        if self.rect.collidepoint(pos):
            # 0 в списке это ЛКМ 2 в списке это ПКМ
            # self.clicked == False означает что я до этого не нажимал кнопку
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True #только что нажал кнопку
        #так же воскрешает через пробел на прыжок не влияет
        if key[pygame.K_SPACE] and self.clicked == False:
            action = True
            self.clicked = True


            #Возвращает значение False кнопки т.е не нажата
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        #рисует кнопку
        win.blit(self.image, self.rect)
        return action


class Player():
    """механика"""
    def __init__(self, x, y):
        self.reset(x,y)
    def update(self, game_over):
        """игровой цикл"""
        dx = 0
        dy = 0
        #должен пройти N интераций для обновления индекса
        walk_cooldown = 5
        #порог  столкновкния определяет не находится ли игрок слишком высоко над платформой
        #если растояние меньше 20 пиксел. значит игорок под платформой
        col_thresh = 20
        if game_over == 0:
            #получить нажатие клавиш
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:#последнее исключает спам пробела
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index]
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #обрабатывание анимации
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            #гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            #проверяет столкновение
            # говорит что игрок всё ещё в воздухе
            self.in_air = True
            for tile in world.tile_list:
                """если я использую всё в мире в виде квадратов то во время приближения игрока 
                   т.е его формы функция colliderect создаёт ещё один квадрат который предсказывает 
                   где будет игрок в следующем ходу"""
                # проверка на столкновение в направлении X (лево, право)
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #проверка на столкновение в направлении Y (высота)
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверить если игрок ниже земли т.е прыгает
                    """берет низ клетку и вычетает верх квадрата игрока
                       во второй фонкции наооборот, также нельзя выполнить 
                       другое действие тоесть другое вычесление пока проверяется первое"""
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # проверить если игрок над земли т.е падает
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False  #исключает спам пробела

            #проверяет на столкновение с врагами
            #используемые функции из библиотеки
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            # проверяет на столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            # проверяет на столкновение с выходом
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #проверяет колизию с платформами
            for platform in platform_group:
                #колизия для х координат
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # колизия для у координат
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверить есть ли платформа выше
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #проверить есть ли платформа ниже
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        #-1 помощает игрока на 1 пиусель выше платформы и  не сковывает движения
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #движения игрока вместе с платформой
                    """если платформа не равна 0 то мы можем просто перемещать игрока вместе с ней"""
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            #обновить координаты игрока
            self.rect.x += dx
            self.rect.y += dy
            if self.rect.bottom > win_heigth:
                self.rect.bottom = win_heigth
                dy = 0
        #рисует персонажа на экране
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (win_width // 2) - 150, win_heigth // 2)
            if self.rect.y > 200:
                self.rect.y -= 5
        #рисует игрока на экране
        win.blit(self.image, self.rect)

        return game_over

    def reset(self,x,y):
        """изначально было функцией __init__ до дабовления возраждения
           фактически если в игре задумано возраждение можно сразу создать
           эту функцию и все новые переменые добовлять уже здесь"""
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)  # добавит изображения в список
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('ghost.png')
        """{num} берет и добавляет все картинки с названем guy
        меняя их номер. В переди обязательно ставиться 'f'  """
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

class World():
    """внешний вид мира"""
    def __init__(self,data):
        self.tile_list = []
        """рисует блок грязи в каждой клетке с еденицей """
        dirt_img = pygame.image.load('dirt.png')
        grass_img = pygame.image.load('grass.png')
        #цикл для подсчёта столбцов
        row_count = 0
        for row in data: #проверяет количество столбцов
            col_count = 0 #количество столбцов
            for tile in row:
                if  tile == 1:
                    img = pygame.transform.scale(dirt_img,(title_size, title_size))  #маштобирует картинку земли
                    img_rect = img.get_rect()   #берёт изображение и создаёт прямоугольник
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (title_size, title_size))  # маштобирует картинку земли
                    img_rect = img.get_rect()  # берёт изображение и создаёт прямоугольник
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    """координата X зависит от количества столбца col_count который в данный момент находиться
                     в этом умножении на размер плитки, а затем строка которая находиться 
                     в подсчёте строк (row_count)умножается так же на размер плитки
                     если враги порят в воздухе необходимо конце метода blob добавить 
                     несколько пикселей чтобы враги опустились на поверхность"""
                    blob = Emyne(col_count * title_size, row_count * title_size + 16  )
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * title_size, row_count * title_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * title_size, row_count * title_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * title_size, row_count * title_size + 25)
                    lava_group.add(lava)
                if tile == 7:
                    #необходимо делить на 2 чтобы монеты были по центру
                    coin = Coin(col_count * title_size+ (title_size // 2), row_count * title_size + (title_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * title_size, row_count * title_size - 25)
                    exit_group.add(exit)

                col_count += 1  #счётчитк вызовов
            row_count += 1  #счётчитк вызовов
    def draw(self):
        """метод рисования. постоянно перебирвет клетки класса для его изменения """
        for tile in self.tile_list:
            win.blit(tile[0], tile[1])


class Emyne(pygame.sprite.Sprite):
    """класс врага использует наследоввание классов,
       наследуемый класс встроен в бтблиотеку pygame,
       не пишим врагов в мировом классе потому что там
       используются только статичные объекты"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_count = 0
    def update(self):
        self.rect.x += self.move_direction
        self.move_count += 1
        if abs(self.move_count) > 50:
            self.move_direction *= -1
            self.move_count *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        """Все классы объектов впринципе одинаковые и пишуться по одному алгоритму
        сначала мы делаем класс наследуемым через класс который встроен в pygame
        затем создаем конструктор и инициолизируем класс, следом загружаем изображение
        потом даем изображению определеный размер и переводим это изображение в квадрат
        все что идет после self.rect.y(что является координатами) это механика данного объекта
        потом добовляется група объекта в основном игоровом классе, рисуется группа и
        добовляется экземпляр объекта в мировой класс"""
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('platform.png')
        self.image = pygame.transform.scale(img, (title_size, title_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #отвечает заперемещение платформ
        self.move_direction = 1
        self.move_count = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        # отвечает заперемещение платформ по х коорденате
        self.rect.x += self.move_direction * self.move_x
        # отвечает заперемещение платформ по у коорденате
        self.rect.y += self.move_direction * self.move_y
        self.move_count -= 1
        if abs(self.move_count) > 50:
            self.move_direction *= -1
            self.move_count *= -1
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(img, (title_size, title_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    """класс с механикой монет"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('coin.png')
        #так как манетка маленькая нужно делить в х и у направлениях
        self.image = pygame.transform.scale(img, (title_size // 2, title_size // 2))
        self.rect = self.image.get_rect()
        #рисует манеты с центра а не с угла
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('exit.png')
        # int убирает проблему с плавоющей точкой
        self.image = pygame.transform.scale(img, (title_size, int(title_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, win_heigth - 130)
"""100 по х, а по у высота экрана - 130
он класс просто поместит игрока поверх блоков"""
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
#создать фиктивную монету для отбражения счета
score_coin = Coin(title_size // 2, title_size // 2)
coin_group.add(score_coin)

#загрузить даные мира и создать его
"""переменая pickle_in при открывает файл level с уровнями,
   которые лежат в одной директории с проэктом, потом при 
   помощи функции {level} подставляет в переменую level которая
   была созданавыше новое значение уровня тем самыс уровни идут
   последовательно их номеру"""
if path.exists(f'level{level}_data'):
    """фактическм говрит если существует этот файл то загружай его"""
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)
#зоздание кнопок
#обязательно делить на 2 чтобы избежать чисел с плавоющей точкой
restart_button = Button(win_width // 2 - 50, win_heigth // 2 + 50, restart_img)
start_button = Button(win_width // 2 - 350, win_heigth // 2, start_img)
exit_button = Button(win_width // 2 + 150, win_heigth // 2, exit_img)
#цикл для проверки игры
run = True
while run:
    """указывать функции для рисования нужно в той последовательности
       в какой нужно т.е сначало фон потом игрок и другое"""
    #бесконечное повторение этой картинки в цикле
    clock.tick(fps) #ограничивает частоту кадров

    win.blit(bg_img, (0, 0))
    win.blit(sun_img, (100, 100))

    #кнопки начала и выйти в отдельном меню
    if main_menu == True:
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False
    else:

        # прорисовка мира, вызов функций
        # рисует
        world.draw()  #рисует все блоки

        if game_over == 0:
             blob_group.update()
             platform_group.update()
            #обновляет счет
            #проверяет были ли собраны монеты
        if pygame.sprite.spritecollide(player, coin_group, True):
            score += 1
        #отображает счет монет
        draw_text('X ' + str(score), font_score, white, title_size - 10, 10)
        blob_group.draw(win) # рисует врагов
        platform_group.draw(win) #рисует платформы
        lava_group.draw(win) # рисует лаву
        coin_group.draw(win) # рисует манеты
        exit_group.draw(win) # рисует выход

        game_over = player.update(game_over)

        #если игрок умер то мы рисуем эту кнопку
        if game_over == -1:
            #кнопка рестарт
            if restart_button.draw():
                #удаляет даные мира и зоздает новый
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        #если игрок прошел уровень
        if game_over == 1:
           #перезагрузить игру и перейти на следующий уровень
            level += 1
            if level <= max_levels:
                #сбросить уровень
                world_data = []
                #говорит что мир равкн уровню сброса
                world = reset_level(level)
                game_over = 0
            else:
                #обновляет игру
                if restart_button.draw():
                    level = 1
                    #обновляет уровень
                    world_data = []
                    world = reset_level(level)
                    game_over = 0


    #выполняет закрытие игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #обновляет окно со всеми визуальными обновлениями
    pygame.display.update()

pygame.quit()
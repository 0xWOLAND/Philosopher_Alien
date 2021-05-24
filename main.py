import pygame
from pygame.locals import *
import pickle
pygame.init()
clock = pygame.time.Clock()
fps = 60

WIDTH = 1000
HEIGHT = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Philosopher Alien")

# font -->
font_score = pygame.font.SysFont('Bauhaus 93', 30)


# load images
bg_img = pygame.image.load('img/sky.jpg')
menu_bg_img = pygame.image.load('img/menu_bg.jpg')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
ghost_img = pygame.image.load(
    'img/Extra animations and enemies/Enemy sprites/ghost.png')
liquid_lava_top_img = pygame.image.load('img/chains.png')
restart_img = pygame.image.load('img/restart_btn.png')
item_img = pygame.image.load('img/lightbulb.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
npc_img = pygame.image.load('img/guy1.png')
book_img = pygame.image.load('img/book.png')
done_img = pygame.image.load('img/done_img.png')
characters = []
pics = []

for i in range(1, 7):
    characters.append(pygame.image.load(f'img/characters/character{i}.png'))

# Boss Images
run = True
tile_size = 50
game_over = 0
main_menu = True
showing_info = -1
level = 1
max_levels = 7
score = 50

# Colors -->
white = (255, 255, 255)
paper = (241, 241, 212)
black = (0,   0,   0)
gold = (255, 215,   0)
purple = (75, 0, 130)


def get_information():
    info = []
    with open('info.txt', 'r') as file:
        line = file.readline()
        while line != '':
            t = []
            for word in line.split('|'):
                t.append(word.replace('\n', ''))

            info.append(t)
            line = file.readline()

    return info


def print_text(text, x, y, width, height, img=None):
    font = font_score
    colour = black
    rect = pygame.draw.rect(screen, paper, pygame.Rect(x, y, width, height))
    x = rect.centerx
    y = rect.centery
    allowed_width = 600
    words = text.split()

    # now, construct lines out of these words
    lines = []
    while len(words) > 0:
        # get as many words as will fit within allowed_width
        line_words = []
        while len(words) > 0:
            line_words.append(words.pop(0))
            fw, fh = font.size(' '.join(line_words + words[:1]))
            if fw > allowed_width:
                break

        # add a line consisting of those words
        line = ' '.join(line_words)
        lines.append(line)

    # now we've split our text into lines that fit into the width, actually
    # render them

    # we'll render each line below the last, so we need to keep track of
    # the culmative height of the lines we've rendered so far
    y_offset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2
        ty = y + y_offset

        font_surface = font.render(line, True, colour)
        screen.blit(font_surface, (tx, ty))

        y_offset += fh


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(100, HEIGHT - 130)
    ghost_group.empty()
    lava_group.empty()
    exit_group.empty()
    npc_group.empty()
    item_group.empty()
    book_group.empty()
    boss_bullet.empty()
    hero_bullet.empty()
    item_group.add(score_item)
    world_data = []
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world, level


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.attack = []
        self.index = 0
        self.counter = 0
        for i in range(18):
            k = str(i + 1)
            img_path = f'img/Skeleton/Attack/Skeleton Attack-{k}.png'
            img_left = pygame.image.load(img_path)
            img_left = pygame.transform.scale(img_left, (80, 80))
            img_left = pygame.transform.flip(img_left, True, False)
            self.attack.append(img_left)

        self.image = self.attack[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        attack_cooldown = 8
        self.counter += 1
        if self.counter == attack_cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.centery +
                            10, tile_size // 4, purple, -1)
            boss_bullet.add(bullet)
            self.counter = 0
        if self.counter % 2 == 0:
            self.index = (self.index + 1) % len(self.attack)
            self.image = self.attack[self.index]
            screen.blit(self.image, self.rect)


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over, showing_info, score):
        if game_over == -1:
            return -1, -1, score
        key = pygame.key.get_pressed()
        dx = 0
        dy = 0
        walk_cooldown = 5
        shoot_cooldown = 5
        if game_over == 0:
            if key[pygame.K_UP] and not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]
            if key[pygame.K_SPACE]:
                self.shoot_counter += 1
                if self.shoot_counter == shoot_cooldown and score > 0:
                    bullet = Bullet(self.rect.centerx + 35 * self.direction,
                                    self.rect.centery, tile_size // 4, gold, self.direction)
                    hero_bullet.add(bullet)
                    self.shoot_counter = 0
                    score -= 1
                elif self.shoot_counter == shoot_cooldown:
                    self.shoot_counter = 0
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if(self.index >= len(self.images_right)):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            self.vel_y += 0.5
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = self.rect.bottom - tile[1].top
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, ghost_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
            if pygame.sprite.spritecollide(self, npc_group, False) and not self.didMeetPerson:
                self.didMeetPerson = True
                showing_info = 0

            if pygame.sprite.spritecollide(self, book_group, False) and not self.didReadBook:
                self.didReadBook = True
                showing_info = 1

            self.rect.x += dx
            self.rect.y += dy
        else:
            self.image = self.dead_image
            self.image = pygame.transform.scale(self.image, (40, 40))
            x = self.rect.x
            y = self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y + 5
        screen.blit(self.image, self.rect)
        return game_over, showing_info, score

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for i in range(12):
            k = str(i)
            if i < 10:
                k = '0' + k
            img_path = f'img/Base pack/Player/p1_walk/PNG/p1_walk{k}.png'
            img_right = pygame.image.load(img_path)
            img_right = pygame.transform.scale(img_right, (40, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_left.append(img_left)
            self.images_right.append(img_right)

        self.dead_image = pygame.image.load(
            'img/Extra animations and enemies/Alien sprites/alienBeige_duck.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True
        self.didReadBook = False
        self.didMeetPerson = False
        self.shoot_counter = 0


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, img, text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (65, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - (tile_size // 2)
        self.text = text


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ghost_img
        self.image = pygame.transform.scale(self.image, (40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

    def __del__(self):
        self.kill()
        pass


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            liquid_lava_top_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Book(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(
            img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class World():
    def __init__(self, data):
        row_count = 0

        self.tile_list = []
        for row in data:
            col_count = 0
            for tile in row:
                if tile > 0:
                    if tile == 1:
                        img = pygame.transform.scale(
                            dirt_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 2:
                        img = pygame.transform.scale(
                            grass_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 3:
                        ghost = Enemy(col_count * tile_size,
                                      row_count * tile_size)
                        ghost_group.add(ghost)
                    elif tile == 4:
                        npc = NPC(col_count * tile_size, row_count *
                                  tile_size, characters[level - 1], "Hello World!")
                        npc_group.add(npc)
                    elif tile == 5:
                        book = Book(col_count * tile_size,
                                    row_count * tile_size, book_img)
                        book_group.add(book)
                    elif tile == 6:
                        lava = Lava(col_count * tile_size,
                                    row_count * tile_size + (tile_size // 2))
                        lava_group.add(lava)
                    elif tile == 7:
                        item = Item(col_count * tile_size + (tile_size // 2),
                                    row_count * tile_size + (tile_size // 2), item_img)
                        item_group.add(item)
                    elif tile == 8:
                        exit = Exit(col_count * tile_size,
                                    row_count * tile_size - (tile_size // 2))
                        exit_group.add(exit)
                    elif tile == 9:
                        boss = Boss(col_count * tile_size - 30,
                                    row_count * (tile_size) - 30)
                        boss_group.add(boss)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, direction):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.direction = direction
        self.vel = 8 * direction
        self.isHero = color == gold
        if self.isHero:
            self.health = 100
        else:
            self.health = 100
        self.rect = pygame.Rect((x, y), (2 * radius, 2 * radius))
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, game_state):
        if not self.isHero and pygame.sprite.spritecollide(self, hero_bullet, True):
            self.health -= 100
        if self.isHero and pygame.sprite.spritecollide(self, boss_bullet, True):
            self.health -= 100

        if self.isHero:
            if pygame.sprite.spritecollide(self, ghost_group, True):
                self.kill()
            if pygame.sprite.spritecollide(self, boss_group, True):
                game_state = 2
                self.kill()
        elif not self.isHero and player.rect.colliderect(self.rect.x, self.rect.y, self.radius * 2, self.radius * 2):
            game_state = -1
        if 0 <= self.x and self.x <= WIDTH and self.health > 0:
            pygame.draw.circle(screen, self.color,
                               (self.x + self.vel, self.y), self.radius)
            self.x += self.vel
            self.rect.x = self.x
        else:
            self.kill()

        return game_state


ghost_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
npc_group = pygame.sprite.Group()
book_group = pygame.sprite.Group()
hero_bullet = pygame.sprite.Group()
boss_bullet = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
score_item = Item(tile_size // 2, tile_size // 2, item_img)
item_group.add(score_item)
info = get_information()
player = Player(100, HEIGHT - 110)
world_data = []
pickle_in = open(f'level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)
restart_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, restart_img)
start_button = Button(WIDTH // 2 - 350, HEIGHT // 2, start_img)
exit_button = Button(WIDTH // 2 + 150, HEIGHT // 2, exit_img)
close_button = Button(805, 300, pygame.transform.scale(
    done_img, (tile_size, tile_size)))
info_button = Button(450, 875, pygame.transform.scale(
    done_img, (tile_size, tile_size)))
game_over_screen = Button(0, 0, pygame.transform.scale(
    pygame.image.load('img/game_over.jpg'), (WIDTH, HEIGHT)))

game_over = 0

while run:
    clock.tick(fps)

    if main_menu:
        screen.blit(pygame.transform.scale(
            menu_bg_img, (WIDTH, HEIGHT)), (0, 0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    elif showing_info != -1:
        print_text(info[level - 1][showing_info], 100, 250, 800, 550)
        if close_button.draw():
            showing_info = -1
    else:
        screen.blit(bg_img, (0, 0))
        world.draw()
        if game_over == 0:
            ghost_group.update()
            if pygame.sprite.spritecollide(player, item_group, True):
                score += 1
            draw_text(f'X {score} {"Epiphany" if score == 1  else "Epiphanies"} ',
                      font_score, white, tile_size - 10, 10)
        ghost_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        item_group.draw(screen)
        npc_group.draw(screen)
        book_group.draw(screen)
        boss_group.draw(screen)
        for bullet in boss_bullet:
            game_over = bullet.draw(screen, game_over)
        for bullet in hero_bullet:
            game_over = bullet.draw(screen, game_over)
        game_over, showing_info, score = player.update(
            game_over, showing_info, score)
        for boss in boss_group:
            boss.update()
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                if level == 7:
                    level = 1
                    boss_group.empty()
                    bg_img = pygame.image.load('img/sky.jpg')
                world, level = reset_level(level)
                game_over = 0
        if game_over == 1:
            level += 1
            if level == 3 or level == 4:
                bg_img = pygame.image.load('img/sky2.jpg')
            elif level == 5 or level == 6:
                bg_img = pygame.image.load('img/sky3.jpg')
            elif level == 7:
                bg_img = pygame.image.load('img/sky4.png')
            if level <= max_levels:
                world_data = []
                world, level = reset_level(level)
                game_over = 0
        if game_over == 2:
            screen.fill(white)
            bg_img = pygame.image.load('img/final_screen.png')
            bg_img = pygame.transform.scale(
                bg_img, (WIDTH, bg_img.get_height()))
            screen.blit(bg_img, (0, 0))
            print_text("Where do you stand?", 20, 700, 960, 250)
            if info_button.draw():
                game_over = 3
        elif game_over == 3:
            if game_over_screen.draw():
                game_over = 4
        elif game_over == 4:
            game_over = 0
            level = 1
            world, level = reset_level(level)
            bg_img = pygame.image.load('img/sky.jpg')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()

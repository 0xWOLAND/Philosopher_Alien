import pygame
from pygame.locals import *
import pickle
pygame.init()
clock = pygame.time.Clock()
fps = 60

WIDTH = 1000
HEIGHT  = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Philosopher Kid")

# font -->
font_score = pygame.font.SysFont('Bauhaus 93', 30)


# load images
bg_img = pygame.image.load('img/sky.jpg')
menu_bg_img = pygame.image.load('img/menu_bg.jpg')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
ghost_img = pygame.image.load('img/Extra animations and enemies/Enemy sprites/ghost.png')
liquid_lava_top_img = pygame.image.load('img/chains.png')
restart_img = pygame.image.load('img/restart_btn.png')
item_img = pygame.image.load('img/lightbulb.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
npc_img = pygame.image.load('img/guy1.png')

run = True
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 5
score = 0

# Colors -->
white = (255, 255, 255)

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
    item_group.add(score_item)
    world_data = []
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


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

class Player():
    def __init__(self, x, y):
        self.reset(x,y)
    def update(self, game_over):

        key = pygame.key.get_pressed()
        dx = 0
        dy = 0
        walk_cooldown = 5
        if game_over == 0:
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
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


                # if pygame.sprite.spritecollide(self, ghost_group, False):
                #     game_over = -1
                # if pygame.sprite.spritecollide(self, lava_group, False):
                #     game_over = -1
                if pygame.sprite.spritecollide(self, exit_group, False):
                    game_over = 1
                
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
        return game_over
    
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for i in range(12):
            k = str(i);
            if i < 10:
                k = '0' + k
            img_path = f'img/Base pack/Player/p1_walk/PNG/p1_walk{k}.png'
            img_right = pygame.image.load(img_path)
            img_right = pygame.transform.scale(img_right, (40, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_left.append(img_left)
            self.images_right.append(img_right)
            
        self.dead_image = pygame.image.load('img/Extra animations and enemies/Alien sprites/alienBeige_duck.png')
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
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, img, text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (40, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
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
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(liquid_lava_top_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)  

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
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
                        img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 2:
                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 3:
                        ghost = Enemy(col_count * tile_size, row_count * tile_size)
                        ghost_group.add(ghost)
                    elif tile == 4:
                        npc = NPC(col_count * tile_size, row_count * tile_size, npc_img, "Hello World!")
                        npc_group.add(npc)
                    elif tile == 6:
                        lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                        lava_group.add(lava)
                    elif tile == 7:
                        item = Item(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2), item_img)
                        item_group.add(item)
                    elif tile == 8:
                        exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                        exit_group.add(exit)
                col_count += 1
            row_count += 1
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

ghost_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
npc_group = pygame.sprite.Group()

score_item = Item(tile_size // 2, tile_size // 2, item_img)
item_group.add(score_item)

player = Player(100, HEIGHT - 110)
world_data = []
pickle_in = open(f'level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)
restart_button = Button(WIDTH // 2 - 50, HEIGHT // 2 + 100, restart_img)
start_button = Button(WIDTH // 2 - 350, HEIGHT // 2, start_img)
exit_button = Button(WIDTH // 2 + 150, HEIGHT // 2, exit_img)




while run:
    clock.tick(fps)
    if main_menu:
        screen.blit(pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT)), (0,0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        screen.blit(bg_img, (-450,0))
        world.draw()
        if game_over == 0:
            ghost_group.update()
            if pygame.sprite.spritecollide(player, item_group, True):
                score += 1
            draw_text(f'X {score} {"Epiphany" if score == 1  else "Epiphanies"} ', font_score, white, tile_size - 10, 10)
        ghost_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        item_group.draw(screen)
        npc_group.draw(screen)
        game_over = player.update(game_over)
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
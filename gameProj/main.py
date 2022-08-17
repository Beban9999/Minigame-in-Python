import pygame
from pygame.locals import *
import pickle
from os import path

pygame.init()

screenWidth = 800
screenHeight = 800
score = 0
gameover = 0
main_menu = True
level = 8

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Igrica")

fontScore = pygame.font.SysFont("Bauhaus 93", 30)
fontGameOver = pygame.font.SysFont("Bauhaus 93", 70)

fontColor = (255, 255, 255)
fontColorOver = (0, 0, 255)

bgImg1 = pygame.image.load("bg1.jpg")
bgImg1 = pygame.transform.scale(bgImg1, (800, 800))
restart_img = pygame.image.load("rr.png")
back_manu = pygame.image.load("backtomain.png")
start_img = pygame.image.load("start.png")
start_img = pygame.transform.scale(start_img, (150, 150))
exit_img = pygame.image.load("exit.png")
exit_img = pygame.transform.scale(exit_img, (150, 150))


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def resetLevel(level):
    player.reset(100, screenHeight - 130)
    enemGroup.empty()
    lavaGroup.empty()
    platformGroup.empty()
    coinGroup.empty()
    exitGroup.empty()

    if path.exists(f"level{level}_data"):
        pickleIn = open(f"level{level}_data", "rb")
        worldList = pickle.load(pickleIn)
    world = World(worldList)

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
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        if self.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, gameover):
        dx = 0
        dy = 0
        walkCd = 2
        colTresh = 20

        if gameover == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.inAir == False:
                self.jumped = True
                self.vel_y = -15
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direct = "l"
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direct = "r"
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index] if self.direct == "r" else self.images_left[self.index]

            # animacija
            if self.counter > walkCd:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = self.images_right[self.index] if self.direct == "r" else self.images_left[self.index]

            # "gravitacija"
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # kolizija
            self.inAir = True
            for tile in world.tile_list:
                # za x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width - 10, self.height):
                    dx = 0
                # za y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width - 10, self.height):
                    # igrac ispod
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.inAir = False
            # kolizija sa neprijateljima
            if pygame.sprite.spritecollide(self, enemGroup, False):
                gameover = -1
            if pygame.sprite.spritecollide(self, lavaGroup, False):
                gameover = -1
            if pygame.sprite.spritecollide(self, exitGroup, False):
                gameover = 1

            # kolizija sa platformama

            for platform in platformGroup:
                # po x-u
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width - 10, self.height):
                    dx = 0
                # po y-u
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width - 10, self.height):
                    #ispod
                    if abs((self.rect.top + dy) - platform.rect.bottom) < colTresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top - 2
                    #iznad
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < colTresh:
                        self.rect.bottom = platform.rect.top
                        self.inAir = False
                        dy = 0
                    #pomeraj na platformi
                    if platform.movX != 0:
                        self.rect.x += platform.direction







            # update pozicija igraca
            self.rect.x += dx
            self.rect.y += dy

        elif gameover == -1:
            self.image = self.dead_image
            draw_text("GAME OVER!", fontGameOver, fontColorOver, (screenWidth // 2) - 180, screenHeight // 2 - 100)
            if self.rect.y > 0:
                self.rect.y -= 7

        screen.blit(self.image, self.rect)
        return gameover

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 12):
            img_right = pygame.image.load(f"char/p3_walk{num}.png")
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("char/deadT.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (40, 80))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direct = 'r'
        self.jumped = False
        self.inAir = True


class World():
    def __init__(self, data):
        self.tile_list = []
        tileWid = 40
        tileHei = 40

        dirt_img = pygame.image.load("dirt.png")
        grass_img = pygame.image.load("grass.png")
        rowInd = 0
        for row in data:
            colInd = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tileWid, tileHei))
                    img_rect = img.get_rect()
                    img_rect.x = colInd * tileWid
                    img_rect.y = rowInd * tileHei
                    self.tile_list.append((img, img_rect))
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tileWid, tileHei))
                    img_rect = img.get_rect()
                    img_rect.x = colInd * tileWid
                    img_rect.y = rowInd * tileHei
                    self.tile_list.append((img, img_rect))
                if tile == 3:
                    enem = Enemy(colInd * tileHei, rowInd * tileWid)
                    enemGroup.add(enem)
                if tile == 4:
                    platform = Platform(colInd * tileHei, rowInd * tileWid, 1, 0)
                    platformGroup.add(platform)
                if tile == 5:
                    platform = Platform(colInd * tileHei, rowInd * tileWid, 0, 1)
                    platformGroup.add(platform)
                if tile == 6:
                    lava = Lava(colInd * tileHei, rowInd * tileWid + (tileHei // 2))
                    lavaGroup.add(lava)
                if tile == 7:
                    coin = Coin(colInd * tileHei + (tileHei // 2), rowInd * tileWid + (tileHei // 2))
                    coinGroup.add(coin)
                if tile == 8:
                    exit = Exit(colInd * tileHei, rowInd * tileWid)
                    exitGroup.add(exit)
                colInd += 1
            rowInd += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("enemy1.png")
        self.image = pygame.transform.scale(self.image, (30, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.movCount = 0

    def update(self):
        self.rect.x += self.direction
        self.movCount += 1
        if abs(self.movCount) > 50:
            self.direction *= -1
            self.movCount *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, movX, movY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("platform.png")
        self.image = pygame.transform.scale(self.image, (40, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movCount = 0
        self.direction = 1
        self.movX = movX
        self.movY = movY

    def update(self):
        self.rect.x += self.direction * self.movX
        self.rect.y += self.direction * self.movY
        self.movCount += 1
        if abs(self.movCount) > 40:
            self.direction *= -1
            self.movCount *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("lava.png")
        self.image = pygame.transform.scale(self.image, (40, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("coin.png")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("exit1.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


if path.exists(f"level{level}_data"):
    pickleIn = open(f"level{level}_data", "rb")
    worldList = pickle.load(pickleIn)

player = Player(100, screenHeight - 130)

enemGroup = pygame.sprite.Group()
platformGroup = pygame.sprite.Group()
lavaGroup = pygame.sprite.Group()
coinGroup = pygame.sprite.Group()
exitGroup = pygame.sprite.Group()


world = World(worldList)

restartBtn = Button(screenWidth // 2 - 20, screenHeight // 2 - 200, restart_img)
backtomanu = Button(screenWidth // 2 - 20, screenHeight // 2, back_manu)
start_button = Button(screenWidth // 2 - 90, screenWidth // 2 - 200, start_img)
exit_button = Button(screenWidth // 2 - 75, screenWidth // 2 + 100, exit_img)

scoreCoin = Coin(15, 20)
coinGroup.add(scoreCoin)

run = True

while run:
    #godMode
    #player.inAir = False
    screen.blit(bgImg1, (0, 0))

    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = 0

    else:
        world.draw()
        if gameover == 0:
            enemGroup.update()
            platformGroup.update()
            # skor
            if pygame.sprite.spritecollide(player, coinGroup, True):
                score += 1
            draw_text("X " + str(score), fontScore, fontColor, 27, 5)
        enemGroup.draw(screen)
        platformGroup.draw(screen)
        lavaGroup.draw(screen)
        coinGroup.draw(screen)
        exitGroup.draw(screen)

        gameover = player.update(gameover)

        if gameover == -1:
            score = 0
            if restartBtn.draw():
                player.reset(100, screenHeight - 130)
                gameover = 0
            if backtomanu.draw():
                main_menu = True
                player.reset(100, screenHeight - 130)
                gameover = 0
        if gameover == 1:
            score = 0
            level += 1
            if path.exists(f"level{level}_data"):
                #restartuj
                worldList = []
                world = resetLevel(level)
                gameover = 0
            else:
                #ispis kraja
                draw_text("GOOD JOB!", fontGameOver, fontColorOver, (screenWidth // 2) - 170, screenHeight // 2 - 100)
                if restartBtn.draw():
                    level = 1
                    worldList = []
                    world = resetLevel(level)
                    gameover = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # pygame.display.update()
    pygame.display.flip()
    pygame.time.Clock().tick(60)
pygame.quit()

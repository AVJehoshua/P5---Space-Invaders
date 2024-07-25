import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750 
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(" AV Space Invaders")

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Main player -> yellow
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lazers
RED_LAZER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LAZER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LAZER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LAZER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


# Background

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH,HEIGHT))



class Laser:
  def __init__(self, x, y, img):
    self.x = x
    self.y = y
    self.img = img
    self.mask = pygame.mask.from_surface(self.img)

  def draw(self, window):
    window.blit(self.img,  (self.x, self.y))

  def move(self, vel):
    self.y += vel

  def off_screen(self, height):
    return not(self.y <= height and self.y >= 0)

  def collision(self, obj):
    return collide(self, obj)   


class Ship:
  COOLDOWN = 30
  def __init__(self, x, y, health=100):
    self.x = x
    self.y = y
    self.health = health
    self.ship_img = None
    self.laser_img = None
    self.lasers = []
    self.cool_down_counter = 0


  def draw(self, window):
    window.blit(self.ship_img, (self.x, self.y))
    for laser in self.lasers:
      laser.draw(window)

  def move_lasers(self, vel, obj):
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel)
      if laser.off_screen(HEIGHT):
        self.lasers.remove(laser)
      elif laser.collision(obj):
        obj.health -= 10
        self.lasers.remove(laser)

  def cooldown(self):
    if self.cool_down_counter >= self.COOLDOWN:
      self.cool_down_counter = 0
    elif self.cool_down_counter > 0:
      self.cool_down_counter += 1

  def shoot(self):
    if self.cool_down_counter == 0:
      laser = Laser(self.x, self.y, self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter = 1

  def get_width(self):
    return self.ship_img.get_width()
  
  def get_height(self):
    return self.ship_img.get_height()
  


class Player(Ship):
  def __init__(self, x, y, health=100):
    #super refers to parent class (ship) lets use the attributes in ship and assign to player ship
    super().__init__(x, y, health)
    self.ship_img = YELLOW_SPACE_SHIP
    self.laser_img = YELLOW_LAZER
    self.mask = pygame.mask.from_surface(self.ship_img)
    self.max_health = health
    
  def move_lasers(self, vel, objs):
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel)
      if laser.off_screen(HEIGHT):
        self.lasers.remove(laser)
      else:
        for obj in objs:
          if laser.collision(obj):  
            objs.remove(obj)
            self.lasers.remove(laser)

class Enemy(Ship):

  COLOUR_MAP = {
    "red" : (RED_SPACE_SHIP, RED_LAZER),
    "green" : (GREEN_SPACE_SHIP, GREEN_LAZER),
    "blue" : (BLUE_SPACE_SHIP, BLUE_LAZER)
  }

  def __init__(self, x, y, colour, health=100): 
    super().__init__(x, y, health)
    self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
    self.mask = pygame.mask.from_surface(self.ship_img)

  def move(self, vel):
    self.y += vel



def collide(obj1, obj2):
  offset_x = obj2.x - obj1.x  # causing error message -> No attribute x
  offset_y = obj2.y - obj1.y
  return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main(): 
  run = True
  # Frames per second set to 60
  FPS = 60 
  clock = pygame.time.Clock()
  level = 0
  lives = 6
  main_font = pygame.font.SysFont("comicsans", 60)
  lost_font = pygame.font.SysFont("comicsans", 90)
  player_vel = 4
  laser_vel = 5 

  enemies = []
  enemy_vel = 1
  wave_length = 5

  lost = False
  lost_count = 0

  player = Player(300, 650)

  def redraw_window():
    # calling .blit method takes a pygame image (surface) and draws to window at defined location
    # pygame co-ordinates start at top left of the graph (0,0) indicates, (X, Y), indicates top left corner of square
    WIN.blit(BG, (0,0))
    # draw text
    # (0, 0, 255) represents RGB code for blue
    level_label = main_font.render(f"Level:{level}", 1, (0, 0, 255))
    lives_label = main_font.render(f"Lives:{lives}", 1, (0, 0, 255))
    #
    WIN.blit(lives_label, (10, 10))
    WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

    for enemy in enemies:
      enemy.draw(WIN)

    player.draw(WIN)

    if lost == True:
      absurd_label = main_font.render("Life is absurd...", 1, (0, 0, 255))
      lost_label = main_font.render("Game Over", 1, (0, 0, 255))
      WIN.blit(absurd_label, (WIDTH/2 - absurd_label.get_width()/2, 250))
      WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

    pygame.display.update()
    


  while run:
    # runs the game at the same speed, regardless of device
    clock.tick(FPS)
    redraw_window()

    if lives <= 0 or player.health == 0:
      lost = True
      lost_count += 1

    if lost:
      if lost_count > FPS * 3:
        run = False
      else:
        continue

      
    if len(enemies) == 0:
      level += 1
      wave_length += 5
      enemy_vel += 0.5

      for i in range(wave_length):
        enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
        enemies.append(enemy)

    # whilst an event is occuring, get the event
    # events are user-clickable actions (directions, quit, etc)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and player.x - player_vel > 0:
      player.x -= player_vel
    if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
      player.x += player_vel
    if keys[pygame.K_UP] and player.y - player_vel > 0:
      player.y -= player_vel
    if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT:
      player.y += player_vel
    if keys[pygame.K_SPACE]:
      player.shoot()


    for enemy in enemies[:]:
      enemy.move(enemy_vel)
      enemy.move_lasers(laser_vel, player)
      if enemy.y + enemy.get_height() > HEIGHT:
        lives -= 1
        enemies.remove(enemy)

    player.move_lasers(-laser_vel, enemies)  

main()





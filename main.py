import random
import time

import pygame
from pygame import Vector2
from pygame.transform import rotozoom

# —--------------------------------------
# Player's stats
multi_shot_level = 1
turning_rate = 1
score = 0
last_score = 0
bananas = 0
health = 3
invulnerable_ticks = 0


# —--------------------------------------
# Functions

def wrap_position(position, screen):
    x, y = position  # where are we
    w, h = screen.get_size()  # how big is the screen
    return Vector2(x % w, y % h)  # x mod width (division) // y mod height (division)
    # mod is dividing and gives you the leftover amount, so now update it elsewhere


def shop(open):
    global multi_shot_level
    global turning_rate
    global bananas
    if open:
        black = pygame.image.load('assets/black.png')
        black = pygame.transform.scale(black, (8000, 600))
        screen.blit(black, (0, 920))
        shop_item_1 = font.render(f'(1) Multi Hit Lvl:{multi_shot_level} Costs {multi_shot_level * 10} bananas', True,
                                  (255, 255, 255))
        if turning_rate == 1: shop_item_2 = font.render(f'(2) Faster turning rate Costs {7} bananas', True,
                                                        (255, 255, 255))
        screen.blit(shop_item_1, (10, 950))
        if turning_rate == 1: screen.blit(shop_item_2, (470, 950))
        if pygame.key.get_pressed()[pygame.K_1]:
            if bananas >= multi_shot_level * 10:
                bananas -= multi_shot_level * 10
                multi_shot_level += 1
        if pygame.key.get_pressed()[pygame.K_2]:
            if bananas >= 7 and turning_rate == 1:
                bananas -= 7
                turning_rate += 1.5


# —--------------------------------------
# Classes


class Ship:
    def __init__(self, position):
        self.position = Vector2(position)
        self.image = pygame.image.load('assets/ship.png')
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.forward = Vector2(0, -1.25)
        self.forward = self.forward.rotate(120)
        self.bullets = []
        self.can_shoot = 0
        self.drift = (0, 0)

    def update(self):
        is_key_pressed = pygame.key.get_pressed()
        if is_key_pressed[pygame.K_w]:
            self.position += self.forward
            self.drift = (self.drift + self.forward) / 1.5
        if is_key_pressed[pygame.K_s]:
            self.position -= self.forward
            self.drift = (self.drift - self.forward) / 1.5
        if is_key_pressed[pygame.K_a]:
            self.forward = self.forward.rotate(-1)
        if is_key_pressed[pygame.K_d]:
            self.forward = self.forward.rotate(1 * turning_rate)
        if is_key_pressed[pygame.K_SPACE] and self.can_shoot == 0:
            for i in range(multi_shot_level):
                self.bullets.append(Bullet(Vector2(self.position), self.forward * 10))
            self.can_shoot = 500
        self.position += self.drift
        if self.can_shoot > 0:
            self.can_shoot -= clock.get_time()
        else:
            self.can_shoot = 0

    def draw(self, screen):
        self.position = wrap_position(self.position, screen)
        angle = self.forward.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(self.image, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size // 2
        screen.blit(rotated_surface, blit_position)


class Bullet:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.time_spawned = time.time()

    def update(self):
        self.position += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), [self.position.x, self.position.y, 5, 5])

    def get_pos(self):
        return self.position

    def random_vel(self):
        self.velocity = Vector2(random.randint(-2, 2), random.randint(-2, 2) * 5)


# Classes for the types of Asteroids

class Asteroid:
    def __init__(self, position):
        self.position = Vector2(position)
        self.position2 = Vector2(self.position[0] + 128, self.position[1] + 128)
        self.velocity = Vector2(random.randint(-3, 3), random.randint(-3, 3)) / 2
        self.image = pygame.image.load('assets/lunar.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.id = random.randint(0, 10000)  # if the id's collide, that's "intended"
        self.type = "default"

    def update(self):
        self.position += self.velocity
        if self.position.x < out_of_bounds[0] or \
                self.position.x > out_of_bounds[2]:
            self.velocity.x *= -1
        if self.position.y < out_of_bounds[1] or \
                self.position.y > out_of_bounds[3]:
            self.velocity.y *= -1
        self.position2 = Vector2(self.position[0] + 128, self.position[1] + 128)

    def draw(self, screen):
        screen.blit(self.image, self.position)

    def destroy(self):
        for a in asteroids:
            if a.id == self.id:
                asteroids.remove(a)

    def collide(self):
        global health
        global invulnerable_ticks
        health -= 1
        invulnerable_ticks = 75
        self.destroy()


class ExplosiveAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/explosion.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.boom = pygame.image.load('assets/boom.png')
        self.boom = pygame.transform.scale(self.boom, (128, 128))
        self.explosion_size = Vector2(128, 128)
        self.type = "explosive"

    def destroy(self):
        global score
        global bananas
        for a in asteroids:
            if a.position.distance_to(self.position) < 200 and a.position2.distance_to(
                    self.position) < 200 and self.id != a.id:
                bananas += 2
                score += 1
                asteroids.remove(a)
                a.destroy()
            if self.id == a.id:
                asteroids.remove(a)

    def explode(self):
        screen.blit(self.boom, self.position)


class ReflectiveAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/reflect.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "reflect"

    def destroy(self):
        global bananas
        bananas += 1
        for b in ship.bullets:
            if b.get_pos().distance_to(self.position) < 128 and b.get_pos().distance_to(self.position2) < 128:
                b.random_vel()
        super().destroy()


class banana(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/banana.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "banana"

    def collide(self):
        global bananas
        bananas += 10
        super().destroy()


# —--------------------------------------
# Initialization


pygame.init()  # Pygame initialization
pygame.display.set_caption("Asteroids and Bananas")
background = pygame.image.load('assets/space_aw1.png')
screen = pygame.display.set_mode((1880, 1000))
clock = pygame.time.Clock()

game_over = False  # Variables
shop_open = False
ship = Ship((100, 100))
asteroids = []
out_of_bounds = [-150, -150, screen.get_width() + 150, screen.get_height() + 150]
old_keys_pressed = pygame.key.get_pressed()
font = pygame.font.SysFont('comicsans', 30, True)

for i in range(35):  # Initialize the asteroids
    rand = random.randint(0, 3)
    if rand == 0:
        asteroids.append(
            ReflectiveAsteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 1:
        asteroids.append(Asteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 2:
        asteroids.append(
            ExplosiveAsteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 3:
        asteroids.append(banana((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
    # asteroids.append(ExplosiveAsteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))

# —--------------------------------------
# Main game loop


while not game_over:
    clock.tick(75)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
    screen.blit(background, (0, 0))

    ship.update()
    ship.draw(screen)

    if score != last_score:
        last_score = score
        print(f"score: {score}")

    for b in ship.bullets:
        b.update()
        b.draw(screen)
        if b.get_pos().y < out_of_bounds[1] \
                or b.get_pos().y > out_of_bounds[3] \
                or b.get_pos().x < out_of_bounds[0] \
                or b.get_pos().x > out_of_bounds[2]:
            ship.bullets.remove(b)
            break
        for a in asteroids:
            if b.get_pos().distance_to(a.position) < 128 and b.get_pos().distance_to(a.position2) < 128:
                score += 1
                bananas += 1
                a.destroy()
                if a.type != "reflect":
                    ship.bullets.remove(b)
                break
        if (time.time() - b.time_spawned) > 3:
            ship.bullets.remove(b)

    for a in asteroids:
        a.update()
        a.draw(screen)
        if ship.position.distance_to(a.position) < 128 and ship.position.distance_to(a.position2) < 128 and invulnerable_ticks == 0:
            a.collide()

    if invulnerable_ticks > 0:
        invulnerable_ticks -= 1
    if health == 0:
        game_over = True

    score_text = font.render('Score: ' + str(score), True, (255, 255, 255))
    banana_text = font.render('Bananas: ' + str(bananas), True, (255, 255, 255))
    health_text = font.render('Health: ' + str(health), True, (255, 255, 255))
    black = pygame.image.load('assets/black.png')
    black = pygame.transform.scale(black, (400, 50))
    screen.blit(black, (0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(banana_text, (140, 10))
    screen.blit(health_text, (290, 10))

    # Here we are checking if the player has pressed a key that wasn't pressed before last cycle
    # This lets us toggle the shop once instead of it being toggled every cycle
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_e] and not old_keys_pressed[pygame.K_e]:
        shop_open = not shop_open
    old_keys_pressed = pygame.key.get_pressed()

    shop(shop_open)
    pygame.display.update()
pygame.quit()

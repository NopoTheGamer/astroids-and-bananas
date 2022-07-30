import pygame
import random
import time
from pygame import Vector2
from pygame.transform import rotozoom


# —--------------------------------------
# NEW
# creating a wrap for the ship
# new global method

def wrap_position(position, screen):
    x, y = position  # where are we
    w, h = screen.get_size()  # how big is the screen
    return Vector2(x % w, y % h)  # x mod width (division) // y mod height (division)
    # mod is dividing and gives you the leftover amount, so now update it elsewhere


# —--------------------------------------


class Ship:
    def __init__(self, position):
        self.position = Vector2(position)
        self.image = pygame.image.load('assets/ship.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.forward = Vector2(0, -2)
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
            self.forward = self.forward.rotate(1)
        if is_key_pressed[pygame.K_SPACE] and self.can_shoot == 0:
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

    def update(self):
        self.position += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), [self.position.x, self.position.y, 5, 5])

    def get_pos(self):
        return self.position


class Asteroid:
    def __init__(self, position):
        self.position = Vector2(position)
        self.position2 = Vector2(self.position[0] + 128, self.position[1] + 128)
        self.velocity = Vector2(random.randint(-3, 3), random.randint(-3, 3)) / 2
        self.image = pygame.image.load('assets/lunar.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.id = random.randint(0, 10000)

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


class ExplosiveAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/explosion.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.boom = pygame.image.load('assets/boom.png')
        self.boom = pygame.transform.scale(self.boom, (128, 128))
        self.explosion_size = Vector2(128, 128)

    def destroy(self):
        global score
        for a in asteroids:
            if a.position.distance_to(self.position) < 200 and a.position2.distance_to(
                    self.position) < 200 and self.id != a.id:
                score += 1
                asteroids.remove(a)
                a.destroy()
            if self.id == a.id:
                asteroids.remove(a)

    def explode(self):
        screen.blit(self.boom, self.position)


pygame.init()
score = 0
last_score = 0
screen = pygame.display.set_mode((1880, 1000))
pygame.display.set_caption("'Roids")
background = pygame.image.load('assets/space_aw1.png')
game_over = False
ship = Ship((100, 700))
asteroids = []
out_of_bounds = [-150, -150, screen.get_width() + 150, screen.get_height() + 150]
for i in range(35):
    if random.randint(0, 1) == 0:
        asteroids.append(
            ExplosiveAsteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
    else:
        asteroids.append(Asteroid((random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))))
clock = pygame.time.Clock()
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
        print(score)

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
                a.destroy()
                ship.bullets.remove(b)
                break

    for a in asteroids:
        a.update()
        a.draw(screen)

    pygame.display.update()
pygame.quit()

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
bananas = 0
health = 3
invulnerable_ticks = 75  # So you don't die in the first second
double_time = 0
double_time_secs = 30
# This is double the time its meant to run for
# This is due to the shop only restocking it after 2x the run time
more_spawns = 30  # This is set to 30 at the start so when the game starts it will spawn 30 asteroids
more_spawns_counter = 0
save_highscores = True
ass_shots = False


# —--------------------------------------
# Functions


def wrap_position(position, screen):  # This function is word for word ripped from the Google Classroom
    x, y = position  # where are we
    w, h = screen.get_size()  # how big is the screen
    return Vector2(x % w, y % h)  # x mod width (division) // y mod height (division)
    # mod is dividing and gives you the leftover amount, so now update it elsewhere
    # From my understanding it will return something like a percentage of how far along you are on the screen
    # So when you go past the edge of the screen it overflows and your "1% of the next screen"
    # But because we don't have a next screen we just go back to the start of the screen


def shop(open):
    # I have decided to go with long global statements as I think its just nicer
    global multi_shot_level, turning_rate, bananas, double_time, more_spawns_counter, more_spawns, fps, shop_open, ass_shots
    if open:
        fps = 55  # This slows down the game a tad, so you have more time to think in the shop
        black = pygame.image.load('assets/black.png')
        black = pygame.transform.scale(black, (8000, 600))
        screen.blit(black, (0, 900))
        # The shop is pretty simple, just some text and if you input a button it will change the value of the variable
        shop_item_1 = font.render(
            f'(1) Multi Hit Lvl:{multi_shot_level} Costs {multi_shot_level * 10} bananas', True, (255, 255, 255))
        if turning_rate == 1:
            shop_item_2 = font.render(
                f'(2) Faster Turning Rate Costs {7} bananas', True, (255, 255, 255))
        shop_item_3 = font.render(
            f'(3) Double Bananas for 15s Costs {20} bananas', True, (255, 255, 255))
        shop_item_4 = font.render(
            f'(4) Spawn Next Wave Costs {25 + more_spawns_counter * 5} bananas', True, (255, 255, 255))
        shop_item_5 = font.render(
            f'(5) You can now shoot from your backside Costs {50} bananas', True, (255, 255, 255))

        screen.blit(shop_item_1, (screen.get_width() - 1870, screen.get_height() - 80))
        if turning_rate == 1:
            screen.blit(shop_item_2, (screen.get_width() - 1870, screen.get_height() - 50))
        if double_time == 0:
            screen.blit(shop_item_3, (screen.get_width() - 1420, screen.get_height() - 80))
        screen.blit(shop_item_4, (screen.get_width() - 1380, screen.get_height() - 50))
        if not ass_shots:
            screen.blit(shop_item_5, (screen.get_width() - 870, screen.get_height() - 80))
        # We do the old_ket_pressed thing here so that the player doesn't buy an upgrade more than once per click
        if pygame.key.get_pressed()[pygame.K_1] and not old_keys_pressed[pygame.K_1]:
            if bananas >= multi_shot_level * 10:
                bananas -= multi_shot_level * 10
                multi_shot_level += 1
        if pygame.key.get_pressed()[pygame.K_2] and not old_keys_pressed[pygame.K_2]:
            if bananas >= 7 and turning_rate == 1:
                bananas -= 7
                turning_rate += 1.5
        if pygame.key.get_pressed()[pygame.K_3] and not old_keys_pressed[pygame.K_3]:
            if bananas >= 20 and double_time == 0:
                bananas -= 20
                fps = 75  # I close the shop here otherwise you don't get the correct amount of time from this upgrade
                double_time = double_time_secs * fps
                shop_open = False
        if pygame.key.get_pressed()[pygame.K_4] and not old_keys_pressed[pygame.K_4]:
            if bananas >= 25 + more_spawns_counter * 5:
                bananas -= 25 + more_spawns_counter * 5
                more_spawns_counter += 1
                more_spawns = 30 + more_spawns_counter * 5
        if pygame.key.get_pressed()[pygame.K_5] and not old_keys_pressed[pygame.K_5]:
            if bananas >= 50 and not ass_shots:
                bananas -= 50
                ass_shots = True
    else:
        fps = 75
        open_shop_text = font.render(f'(E) To open shop', True, (255, 255, 255))
        screen.blit(open_shop_text, (10, 950))


def spawn_asteroids():
    rand = random.randint(0, 4)
    if rand == 0:
        asteroids.append(
            ReflectiveAsteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 1:
        asteroids.append(Asteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 2:
        asteroids.append(
            ExplosiveAsteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 3:
        asteroids.append(Banana((random.randint(100, screen.get_width()), random.randint(0, screen.get_height()))))
    elif rand == 4:  # I thought there were too many portal asteroids, so I made them only 50% due to the fact it spawns 2 portals
        if random.randint(0, 1) == 0:
            asteroids.append(
                PortalAsteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height()))))


def show_highscores(save):
    highscores = []  # Variables needed for high score saving
    highscores_str = []
    last_index = -1

    # Will crash if you don't have this file
    # But the repo comes with it so you should have it
    with open('highscore.txt', 'r') as f:  # Reads the high score file
        for x in f:  # This replace is to remove the newline character. so that it is an int instead of a string
            highscores.append(x.replace('\n', ''))

    for i in highscores:  # Loops over the high score array
        if last_index != -1:  # If the score is higher than one in the array this loop will be called
            highscores.insert(last_index, score)  # Inserts your score into the array
            break  # Breaks the loop
        elif score >= int(i):  # If the score is higher than one of the current high scores
            last_index = highscores.index(i)  # Sets last index so the above if statement can run

    if save:  # So we don't save it 75 times a second (only slightly wasteful)
        with open('highscore.txt', 'w') as f:  # Saves the file with the new high scores
            for x in highscores:
                f.write(str(x) + '\n')

    for i in range(len(highscores)-1):
        highscores_str.append(font.render(f'#{i+1}: {highscores[i]}', True, (255, 255, 255)))  # Puts the high scores in an array
        screen.blit(highscores_str[i], (screen.get_width() / 2 - 220, screen.get_height() / 2 - 360 + i * 50))  # Accesses this array and puts it on the screen
    if last_index != -1:  # Checks if you made the leaderboard
        score_text = font.render(f"Your score was {score}, you placed #{last_index + 1} on the leaderboard", False, (255, 255, 255))
    else:
        # Pretty sure you only don't get the leaderboard if you get less than the bottom score
        score_text = font.render(f"Your score was {score}, you didnt make it on to the leaderboard", False, (255, 255, 255))
    death_text = font.render("You died", False, (255, 255, 255))
    restart_text = font.render('Press SPACE to restart', False, (255, 255, 255))
    screen.blit(score_text, (screen.get_width() / 2 - 420, screen.get_height() / 2 - 400))
    screen.blit(death_text, (screen.get_width() / 2 - 220, screen.get_height() / 2 - 450))
    screen.blit(restart_text, (screen.get_width() / 2 - 220, screen.get_height() / 2 + 350))


def starting_screen():
    welcome_text = font.render("Welcome to Asteroids and Bananas", False, (255, 255, 255))
    menu_text = font.render('Press SPACE to start', False, (255, 255, 255))
    menu_text2 = font.render('Use WASD to move', False, (255, 255, 255))
    menu_text3 = font.render('Use SPACE to shoot', False, (255, 255, 255))
    menu_text4 = font.render('Use E To open the shop', False, (255, 255, 255))
    menu_text5 = font.render('Click the numbers in the shop to buy said item', False, (255, 255, 255))
    menu_text6 = font.render('The game also runs slower while the shop is open', False, (255, 255, 255))
    menu_text7 = font.render('Asteroid types:', False, (255, 255, 255))
    default_asteroid = font.render('Default asteroid: Does nothing cool', False, (255, 255, 255))
    reflective_asteroid = font.render('Reflective asteroid: Bounces bullets in a random direction', False,
                                      (255, 255, 255))
    explosive_asteroid = font.render('Explosive asteroid: Destroys nearby asteroids when shot', False, (255, 255, 255))
    portal_asteroid = font.render('Portal asteroid: Has a chance to teleport you to the other portal', False,
                                  (255, 255, 255))
    banana_asteroid = font.render('Banana: Gives you 5 bananas on collision', False, (255, 255, 255))
    screen.blit(menu_text, (screen.get_width() / 2 - 220, screen.get_height() / 2 + 350))
    screen.blit(menu_text2, (screen.get_width() / 2 - 700, screen.get_height() / 2 - 400))
    screen.blit(menu_text3, (screen.get_width() / 2 - 700, screen.get_height() / 2 - 350))
    screen.blit(menu_text4, (screen.get_width() / 2 - 700, screen.get_height() / 2 - 300))
    screen.blit(menu_text5, (screen.get_width() / 2 - 700, screen.get_height() / 2 - 250))
    screen.blit(menu_text6, (screen.get_width() / 2 - 700, screen.get_height() / 2 - 200))
    screen.blit(menu_text7, (screen.get_width() / 2 - 0, screen.get_height() / 2 - 400))
    screen.blit(default_asteroid, (screen.get_width() / 2 + 130, screen.get_height() / 2 - 370))
    screen.blit(reflective_asteroid, (screen.get_width() / 2 + 130, screen.get_height() / 2 - 220))
    screen.blit(explosive_asteroid, (screen.get_width() / 2 + 130, screen.get_height() / 2 - 90))
    screen.blit(portal_asteroid, (screen.get_width() / 2 + 130, screen.get_height() / 2 + 20))
    screen.blit(banana_asteroid, (screen.get_width() / 2 + 130, screen.get_height() / 2 + 160))
    screen.blit(welcome_text, (screen.get_width() / 2 - 220, screen.get_height() / 2 - 450))
    for a in asteroids:  # I use real asteroids on the starting screen
        a.draw(screen)
    pygame.display.update()


def death_screen():
    global save_highscores
    show_highscores(save_highscores)
    save_highscores = False  # This is used so the file isn't written too 75 times a second
    pygame.display.update()


def reset_game():
    global multi_shot_level, turning_rate, score, bananas, health, invulnerable_ticks, double_time, double_time_secs, more_spawns, more_spawns_counter, save_highscores, game_over, shop_open, dont_shoot, fps, spawn_timer, ship, asteroids, death_time, ass_shots
    multi_shot_level = 1
    turning_rate = 1
    score = 0
    bananas = 0
    health = 3
    invulnerable_ticks = 75
    double_time = 0
    double_time_secs = 30
    more_spawns = 30
    more_spawns_counter = 0
    save_highscores = True
    game_over = False
    shop_open = False
    dont_shoot = False
    fps = 75
    spawn_timer = 3 * fps
    ship = Ship((100, 100))
    asteroids = []
    death_time = 50
    ass_shots = False


# —--------------------------------------
# Classes


class Ship:
    # Alot of this ship code is the same as the classroom one
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
            self.forward = self.forward.rotate(-1 * turning_rate)
        if is_key_pressed[pygame.K_d]:
            self.forward = self.forward.rotate(1 * turning_rate)
        if is_key_pressed[pygame.K_SPACE] and self.can_shoot == 0:
            for i in range(multi_shot_level):
                self.bullets.append(Bullet(Vector2(self.position), self.forward * 10))
                if ass_shots:
                    self.bullets.append(Bullet(Vector2(self.position), -self.forward * 10))
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
        self.id = random.randint(0, 10000)  # If the id's collide, that's "intended"
        self.type = "default"  # The type is used for reflective and portal asteroids

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
        global health, invulnerable_ticks
        health -= 1
        invulnerable_ticks = fps
        self.destroy()


# For the different types of Asteroids I extended the Asteroid class
# This is so I can still iterate over them
# and use the same methods for all of them
class ExplosiveAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/explosion.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.explosion_size = Vector2(128, 128)
        self.type = "explosive"

    def destroy(self):
        global score, bananas
        for a in asteroids:
            # The collision check is scuffed but like it works well enough ¯\_(ツ)_/¯
            if a.position.distance_to(self.position) < 200 and a.position2.distance_to(
                    self.position) < 200 and self.id != a.id:
                if double_time > (double_time_secs / 2) * fps:
                    bananas += 2
                bananas += 2
                score += 1
                asteroids.remove(a)
                a.destroy()
            if self.id == a.id:
                asteroids.remove(a)


class ReflectiveAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/reflect.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "reflect"

    def destroy(self):
        global bananas
        if double_time > (double_time_secs / 2) * fps:
            bananas += 1
        bananas += 1
        for b in ship.bullets:
            if b.get_pos().distance_to(self.position) < 128 and b.get_pos().distance_to(self.position2) < 128:
                b.random_vel()
        super().destroy()


class Banana(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load('assets/banana.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "banana"

    def collide(self):
        global bananas, score
        if double_time > (double_time_secs / 2) * fps:
            bananas += 5
        bananas += 5
        score += 1
        super().destroy()


class PortalAsteroid(Asteroid):
    def __init__(self, position):
        super().__init__(position)
        self.type = "portal"
        self.spawn()

    def spawn(self):
        global asteroids
        # These have id+1 so they don't have the same id as this dummy asteroid
        asteroids.append(
            RedPortalAsteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height())),
                              self.id + 1))
        asteroids.append(
            BluePortalAsteroid((random.randint(100, screen.get_width()), random.randint(0, screen.get_height())),
                               self.id + 1))
        self.destroy()

    def collide(self):
        pass


class RedPortalAsteroid(PortalAsteroid):
    def __init__(self, position, id):
        super().__init__(position)
        self.image = pygame.image.load('assets/red_portal.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "red_portal"
        self.id = id

    def collide(self):
        for a in asteroids:
            if a.id == self.id and a.type == "blue_portal":
                ship.position = a.position
                a.destroy()
        self.destroy()

    def spawn(self):  # Prevent infinite loop
        pass


class BluePortalAsteroid(PortalAsteroid):
    def __init__(self, position, id):
        super().__init__(position)
        self.image = pygame.image.load('assets/blue_portal.png')
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.type = "blue_portal"
        self.id = id

    def collide(self):
        for a in asteroids:
            if a.id == self.id and a.type == "red_portal":
                ship.position = a.position
                a.destroy()
        self.destroy()

    def spawn(self):
        pass


# —--------------------------------------
# Initialization


pygame.init()  # Pygame initialization
pygame.display.set_caption("Asteroids and Bananas")
background = pygame.image.load('assets/space_aw1.png')  # This is my desktop background lol
screen = pygame.display.set_mode((1880, 1000))  # If you have a screen smaller than 1920x1080 then the game just won't work
clock = pygame.time.Clock()

game_over = False  # Variables
shop_open = False
starting_menu = True
dont_shoot = False
fps = 75
spawn_timer = 3 * fps
ship = Ship((100, 100))
asteroids = []
out_of_bounds = [-150, -150, screen.get_width() + 150, screen.get_height() + 150]
old_keys_pressed = pygame.key.get_pressed()
# BTD6 bloon pop sound
pop_sound = pygame.mixer.Sound("assets/pop_.mp3")
# Stolen from https://www.youtube.com/watch?v=PZu3rLDtsdI
pygame.mixer.music.load('assets/scifi_background.mp3')
pygame.mixer.music.set_volume(0.5)
black = pygame.image.load('assets/black.png')
pygame.mixer.music.play(-1)
# So when I was first working on this the font name I had was invalid
# And now im am too lazy too fix sizing issues so you will have to deal with the default font
font = pygame.font.SysFont('something that doesnt exist (I would hope)', 30, True)
death_time = 50  # So you have just under a second before you can click space again to respawn after you die

# These asteroids are the ones shown on the starting screen
asteroids.append(Asteroid((screen.get_width() / 2 - 0, screen.get_height() / 2 - 380)))
asteroids.append(ReflectiveAsteroid((screen.get_width() / 2 - 0, screen.get_height() / 2 - 230)))
asteroids.append(ExplosiveAsteroid((screen.get_width() / 2 - 0, screen.get_height() / 2 - 100)))
asteroids.append(RedPortalAsteroid((screen.get_width() / 2 - 0, screen.get_height() / 2 + 20), 0))
asteroids.append(BluePortalAsteroid((screen.get_width() / 2 - 135, screen.get_height() / 2 + 20), 0))
asteroids.append(Banana((screen.get_width() / 2 - 0, screen.get_height() / 2 + 150)))
# —--------------------------------------
# Main game loop

while not game_over:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
    screen.fill((0, 0, 0))
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        starting_menu = False
    if starting_menu:
        starting_screen()
        continue  # Continue is a keyword that tells python to skip the rest of the code in this loop
    death_time -= 1  # This will go down by 1 per loop but if the game isn't over it also resets to 50 every loop
    if health <= 0:
        death_screen()
        if pygame.key.get_pressed()[pygame.K_SPACE] and death_time <= 0:
            reset_game()
        continue
    screen.blit(background, (0, 0))
    death_time = 50

    ship.update()
    ship.draw(screen)

    for b in ship.bullets:
        b.update()
        b.draw(screen)
        if b.get_pos().y < out_of_bounds[1] \
                or b.get_pos().y > out_of_bounds[3] \
                or b.get_pos().x < out_of_bounds[0] \
                or b.get_pos().x > out_of_bounds[2]:
            ship.bullets.remove(b)  # I added oob checks to the bullets
            break
        for a in asteroids:
            if b.get_pos().distance_to(a.position) < 128 and b.get_pos().distance_to(a.position2) < 128:
                score += 1
                pygame.mixer.Sound.play(pop_sound)
                if double_time > (double_time_secs / 2) * fps:
                    bananas += 1
                bananas += 1
                a.destroy()
                if a.type != "reflect":  # Reflective asteroids send them in a random direction instead
                    ship.bullets.remove(b)
                    break
        if (time.time() - b.time_spawned) > 3:  # If the bullet is alive for too long it despawns
            ship.bullets.remove(b)  # Because it can get 0,0 vel and I didn't want them to just be stuck

    asteroid_count = 0  # Used for stats at the top, as well as spawning more when you are low on asteroids
    for a in asteroids:
        if a.type == "portal":
            a.destroy()
        if a.type != "red_portal":
            asteroid_count += 1
        a.update()
        a.draw(screen)
        if ship.position.distance_to(a.position) < 128 and ship.position.distance_to(
                a.position2) < 128 and invulnerable_ticks == 0:
            a.collide()

    # These all tick down every frame
    # So every second it will go down by the number of frames
    if invulnerable_ticks > 0:
        invulnerable_ticks -= 1
    if double_time > 0:
        double_time -= 1
    if more_spawns > 0:
        spawn_asteroids()
        more_spawns -= 1
        invulnerable_ticks = fps  # Gives a second of invulnerability after spawning

    if spawn_timer > 0:  # Spawns a new asteroid every 3 seconds
        spawn_timer -= 1
    else:
        spawn_asteroids()
        spawn_timer = 3 * fps

    if asteroid_count < 5:  # Where's the fun if you have nothing to blow up?
        for i in range(15):
            spawn_asteroids()

    score_text = font.render('Score: ' + str(score), True, (255, 255, 255))
    banana_text = font.render('Bananas: ' + str(bananas), True, (255, 255, 255))
    health_text = font.render('Health: ' + str(health), True, (255, 255, 255))
    asteroid_count_text = font.render('Asteroids: ' + str(asteroid_count), True, (255, 255, 255))
    black = pygame.transform.scale(black, (600, 50))
    screen.blit(black, (screen.get_width() - screen.get_width(), screen.get_height() - screen.get_height()))
    screen.blit(score_text, (screen.get_width() - screen.get_width() + 10, screen.get_height() - screen.get_height() + 10))
    screen.blit(banana_text, (screen.get_width() - screen.get_width() + 140, screen.get_height() - screen.get_height() + 10))
    screen.blit(health_text, (screen.get_width() - screen.get_width() + 300, screen.get_height() - screen.get_height() + 10))
    screen.blit(asteroid_count_text, (screen.get_width() - screen.get_width() + 430, screen.get_height() - screen.get_height() + 10))

    # Here we are checking if the player has pressed a key that wasn't pressed before last cycle
    # This lets us toggle the shop once instead of it being toggled every cycle
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_e] and not old_keys_pressed[pygame.K_e]:
        shop_open = not shop_open
    shop(shop_open)
    old_keys_pressed = pygame.key.get_pressed()

    pygame.display.update()
# —--------------------------------------
# After game code
show_highscores(True)
pygame.quit()

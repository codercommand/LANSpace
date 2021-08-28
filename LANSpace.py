# Pygame Imports
from pygame.locals import *
import pygame

# Networking Imports
import network

# Entity struct imports
import entity

# Other imports
import random, math, sys, time, GMath

display_size = display_width, display_height = 1080, 700


# Setting up player object


player = entity.Player(0, entity.Type.Actor, 0, random.randrange(0, display_width), random.randrange(0, display_height), random.randint(1, 4))
player_alive = True
player.find_id() # find_id must be called to give the player an available ID
print(player.id)
player.rotation = 90
velocity = 10

firerate = 0.05
last_fired = time.time()
projs_speed = 15 # If projectile speed is too low, the player will kill themself.
proj_cur_count = 0
proj_max_count = 5
reload_time = 0.5
last_reload = time.time()


# Creating game window
pygame.init()
pygame.display.set_caption('LANSpace')
pygame.display.set_icon(pygame.image.load('assets/spaceship/2.png'))

display_surface = pygame.display.set_mode(display_size)
fpsclock = pygame.time.Clock()
FPS = 60


# Custom cursor
pygame.mouse.set_visible(False)
cursor = pygame.image.load('assets/cursor.png')
cursor_size = 29 # 42 is the original image size. I use size 29 because it's a better size and doesn't have weird scaling noise.
cursor = pygame.transform.scale(cursor, (cursor_size, cursor_size))


def render_offset(position: tuple, size: tuple) -> tuple:
    # render_offset returns the offset position the object should be rendered at.
    # Formula: (x-(size/2), y-(size/2)) = (x_offset, y_offset)
    x, y = 0, 1
    return (position[x]-(size[x]/2), position[y]-(size[y]/2))


def collision(obj1, obj2: object) -> bool:
    obj1_x, obj1_y = render_offset((obj1.x, obj1.y), (obj1.size, obj1.size))
    obj2_x, obj2_y = render_offset((obj2.x, obj2.y), (obj2.size, obj2.size))
    if (obj2_x > obj1_x and obj2_x < (obj1_x+obj1.size)) and (obj2_y > obj1_y and obj2_y < (obj1_y+obj1.size)):
        return True
    else:
        return False


def died_message():
    RED = 255, 0, 0,
    text = "You're DEAD!"
    font = pygame.font.Font('assets/freesansbold.ttf', 115)
    textSurface = font.render(text, True, RED)
    TextRect = textSurface.get_rect()
    TextRect.center = ((display_width/2),(display_height/2))
    display_surface.blit(textSurface, TextRect)

def respawn_message():
    WHITE = 255, 255, 255,
    text = "Press R to respawn..."
    font = pygame.font.Font('assets/freesansbold.ttf', 30)
    textSurface = font.render(text, True, WHITE)
    TextRect = textSurface.get_rect()
    TextRect.center = ((display_width/2), (display_height/2)+80)
    display_surface.blit(textSurface, TextRect)

    
# Main game loop. network_manager never stops.
for entities in entity.network_reader(player.id):

    display_surface.fill((0, 0, 0)) # Fills the window black

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    # Respawn player
    keys = keys = pygame.key.get_pressed()
    if keys[pygame.K_r]: player_alive = True


    # Player logic below! ----------------------------------------------------------------------------------------------------------------
    if player_alive:
        # The direction the player is to move in.
        dir_x, dir_y = 0, 0

        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            dir_y -= 1
        if keys[pygame.K_s]:
            dir_y += 1
        if keys[pygame.K_a]:
            dir_x -= 1
        if keys[pygame.K_d]:
            dir_x += 1

        if dir_x != 0 or dir_y != 0:
            dir_x, dir_y = GMath.normalize(dir_x, dir_y)
            player.x += dir_x * velocity
            player.y += dir_y * velocity

        # Checks player position is not illegal, if it is then the player is moved back inside the window.
        border_offset = (player.size/2)
        if player.x < 0+border_offset:
            player.x = 0+border_offset
        if player.x > display_width-border_offset:
            player.x = display_width-border_offset
        if player.y < 0+border_offset:
            player.y = 0+border_offset
        if player.y > display_height-border_offset:
            player.y = display_height-border_offset

        # Player rotation based on mouse position
        mx, my = pygame.mouse.get_pos()
        rel_x = mx - player.x
        rel_y = my - player.y
        
        # 180 is the offset angle to make the rotation between 0-360, otherwise it would be between -180 - 180
        angle = math.degrees(-math.atan2(rel_y, rel_x))+180
        # Offset to make player face cursor 270, can't use -90 because it could make a negative number.
        player.rotation = int(angle)+270


    # End of player logic! --------------------------------------------------------------------------------------------------------------

    # Render Logic Logic ----------------------------------------------------------------------------------------------------------------
    
    # Render enemy players & projectiels
    for enemy in entities:
        if enemy.type == entity.Type.Actor:
            display_surface.blit(enemy.get_spaceship(), render_offset((enemy.x, enemy.y), (enemy.size, enemy.size)))

        if enemy.type == entity.Type.Projectile:
            dir_x = math.cos(math.radians(-enemy.rotation+90))
            dir_y = math.sin(math.radians(-enemy.rotation+90))
            enemy.x -= (dir_x * projs_speed)
            enemy.y -= (dir_y * projs_speed)
            display_surface.blit(enemy.get_projectile(), render_offset((enemy.x, enemy.y), (enemy.size, enemy.size)))

            # Findout if player has been hit
            if collision(player, enemy):
                player_alive = False

    if player_alive:
        # Broadcast player position.
        network.BROADCAST(player.to_bytes())
        # Using a delayed broadcast only inceases the player limit by about 3-5, it's not worth it.

        # Render Player at postion x, y
        display_surface.blit(player.get_spaceship(), render_offset((player.x, player.y), (player.size, player.size)))
    else:
        died_message()
        respawn_message()

    # Projectile Logic ------------------------------------------------------------------------------------------------------------------

    if pygame.mouse.get_pressed()[0] and (time.time()-last_reload) > reload_time and (time.time()-last_fired) > firerate and player_alive:
        last_fired = time.time()
        proj_cur_count += 1

        # Creates projectile
        front_of_ship_x = player.x + (math.cos(math.radians(-player.rotation+90)) * 40)
        front_of_ship_y = player.y + (math.sin(math.radians(-player.rotation+90)) * 40)
        proj = entity.Projectile(player.rotation, front_of_ship_x, front_of_ship_y)
        network.BROADCAST(proj.to_bytes())

        if proj_cur_count == proj_max_count:
            last_reload = time.time()
            proj_cur_count = 0

    # Projectile Logic ------------------------------------------------------------------------------------------------------------------


    # Render custom mouse
    mx, my = pygame.mouse.get_pos()
    display_surface.blit(cursor, render_offset((mx, my), (cursor_size, cursor_size)))


    # Updates the display
    pygame.display.update()
    fpsclock.tick(FPS)
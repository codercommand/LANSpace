# entity.py is a module used by LANSpace.py
# Its purpose is to provide an easy to use abstraction layer for
# managing player objects on the network and their states.
#
#
#
# Public Interface:
#   Type            Used to identify the entity type.
#   Player          The class used to create the main player that the user controls.
#   Avatar          The class used to create representations of network clones of players.
#   network_reader  Generator used to provide the game state of the network for each game loop.

import pygame, time, network

#from pygame.constants import GL_MULTISAMPLEBUFFERS


# Available entity types --------------------------------------------------------------------
from collections import namedtuple

entitytype = namedtuple("entitytype", "Projectile Actor")
Type = entitytype(Projectile=0, Actor=1)
# Available entity types --------------------------------------------------------------------

# Entity Container --------------------------------------------------------------------------
Entity = namedtuple("Entity", "type object")
# Entity Container --------------------------------------------------------------------------


class Projectile:
    def __init__(self, rotation: int, x: int, y: int) -> None:
        self.type = Type.Projectile
        self.rotation = rotation
        self.x = x
        self.y = y

        self.size = 21
        self.duration = time.time()
        self.projectile_cache = pygame.image.load('assets/projectile.png')


    def to_bytes(self) -> bytes:
        data = []

        data.append(self.type)
        for x in self.rotation.to_bytes(length=2, byteorder="big", signed=False):
            data.append(x)
        for x in int(self.x).to_bytes(length=4, byteorder="big", signed=False):
            data.append(x)
        for x in int(self.y).to_bytes(length=4, byteorder="big", signed=False):
            data.append(x)

        return bytes(data)


    def from_bytes(self, data: bytes) -> None:
        self.type =     data[0]
        self.rotation = int.from_bytes(data[1:3], byteorder="big", signed=False)
        self.x =        int.from_bytes(data[3:7], byteorder="big", signed=False)
        self.y =        int.from_bytes(data[7:11], byteorder="big", signed=False)


    def get_projectile(self):
        # get_spaceship gets a surface object of the spaceship at it's current position and rotation.

        
        # Sets the properties of the rendered version.
        projectile = self.projectile_cache.copy() # Created a copy of the original cache to prevent noise damage on rerenders
        projectile = pygame.transform.scale(projectile, (self.size, self.size))
        
        # To make the ship rotate on its center, I used a reference:
        # https://www.pygame.org/wiki/RotateCenter?parent=CookBook
        projectile_rect = projectile.get_rect().copy()
        rot_projectile = pygame.transform.rotate(projectile, self.rotation)#+270) # 270 is the amount the ship must be rotated by to point toward the mouse.
        projectile_rect.center = rot_projectile.get_rect().center
        rot_projectile = rot_projectile.subsurface(projectile_rect)

        return rot_projectile



# Base type used to make the two seperate player types: Avatar & Player.
class Actor:
    def __init__(self, id: int, _type: Type, rotation: int, x: int, y: int, shiptype: int) -> None:
        self.type =     _type
        self.id =       id
        self.rotation = rotation # I only want to store 0-360 in rotation, nothing other.
        self.x =        x
        self.y =        y
        self.shiptype = shiptype # Ship type must be between and including 1-4

        self.spaceship_cache = None
        self.size = 42

    def to_bytes(self) -> bytes:
        data = []

        data.append(self.type)
        data.append(self.id)
        for x in self.rotation.to_bytes(length=2, byteorder="big", signed=False):
            data.append(x)
        for x in int(self.x).to_bytes(length=4, byteorder="big", signed=False):
            data.append(x)
        for x in int(self.y).to_bytes(length=4, byteorder="big", signed=False):
            data.append(x)
        data.append(self.shiptype)

        return bytes(data)


    def from_bytes(self, data: bytes) -> None:
        self.type =     data[0]
        self.id =       data[1]
        self.rotation = int.from_bytes(data[2:4], byteorder="big", signed=False)
        self.x =        int.from_bytes(data[4:8], byteorder="big", signed=False)
        self.y =        int.from_bytes(data[8:12], byteorder="big", signed=False)
        self.shiptype = data[12]


    def get_spaceship(self):
        # get_spaceship gets a surface object of the spaceship at it's current position and rotation.

        # Initializes the img cache, if not already done.
        if not self.spaceship_cache:
            self.spaceship_cache = pygame.image.load('assets/spaceship/{}.png'.format(self.shiptype))
        
        # Sets the properties of the rendered version.
        spaceship = self.spaceship_cache.copy() # Created a copy of the original cache to prevent noise damage on rerenders
        spaceship = pygame.transform.scale(spaceship, (self.size, self.size))
        
        # To make the ship rotate on its center, I used a reference:
        # https://www.pygame.org/wiki/RotateCenter?parent=CookBook
        spaceship_rect = spaceship.get_rect().copy()
        rot_spaceship = pygame.transform.rotate(spaceship, self.rotation)#+270) # 270 is the amount the ship must be rotated by to point toward the mouse.
        spaceship_rect.center = rot_spaceship.get_rect().center
        rot_spaceship = rot_spaceship.subsurface(spaceship_rect)

        return rot_spaceship


# An abstract layer ontop of Actor that provides additional functions.
class Player(Actor):
    def find_id(self) -> None:
        # find_id finds a free ID between 0-255 on the network

        # end_time is the time 1.5 seconds in the future
        end_time = time.time() + 1.5

        playersIDs = [] # List of used player IDs

        # Collects all the currently used IDs on the network.
        while time.time() < end_time:
            random_player = Avatar(0,0,0,0,0,0)
            data = network.CATCH() # Catch a player on the network
            if data: # If data is not empty, then use it to create an Actor object
                random_player.from_bytes(data)
                playersIDs.append(random_player.id)

        # Turning the list to a set removes the duplicate IDs
        playersIDs = set(playersIDs)

        # Searchs for an unused ID, and returns the first unused ID.
        newID = 0
        for ID in playersIDs:
            if newID == ID:
                newID += 1

        self.id = newID
        return


# An abstract layer ontop of Actor that provides additional functions.
class Avatar(Actor):
    last_update = 0


# A generator used for reading the game network before each game loop.
def network_reader(main_player_id: int) -> list:
    
    game_state = []

    while True:
        for _ in range(255): # Can handle up to 20 players on a network.
            
            # Gets an entity from the network
            data = network.CATCH()
            if data:
                entity = object()
                if data[0] == Type.Actor:
                    entity = Avatar(0,0,0,0,0,0)
                elif data[0] == Type.Projectile:
                    entity = Projectile(0,0,0)
                else:
                    print(data)
                
                entity.from_bytes(data)

                # Updates enemy player on the game_state
                if entity.type == Type.Actor and entity.id != main_player_id:
                    for ent in game_state:
                        if ent.type == Type.Actor:
                            if entity.id == ent.id:
                                # Don't need to update type or id since the never change.
                                ent.rotation = entity.rotation
                                ent.x = entity.x
                                ent.y = entity.y
                                ent.last_update = time.time()
                                # ent = entity - Don't do this... it causes a weird jumping glitch because of how
                                # python processes the action.
                                break

                    else:
                        entity.last_update = time.time()
                        game_state.append(entity)

                if entity.type == Type.Projectile:
                    entity.rotation += 180
                    game_state.append(entity)


        # Removes enemies that have stopped playing for more than 1 second.
        for x in range(len(game_state)-1, -1, -1):

            # Remoevs enemy players that have quit playing.
            if game_state[x].type == Type.Actor:
                if (time.time() - game_state[x].last_update) > 0.03:
                    game_state.pop(x)
                    continue

            # Removes projectiles that have been in the world for over 2 seconds. Updates the position of others
            if game_state[x].type == Type.Projectile:
                if (time.time()-game_state[x].duration) > 2.0:
                    game_state.pop(x)
                    continue

        yield game_state
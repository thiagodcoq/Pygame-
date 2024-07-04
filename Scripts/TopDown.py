import pygame
import sys
from pygame.locals import QUIT

# Constants
WIDTH, HEIGHT = 800, 600

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Camera Example")

# World dimensions
WORLD_WIDTH, WORLD_HEIGHT = 1100, 1300

# Camera setup
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
offset_x, offset_y = 0, 0

# Load assets (assuming these files are in the same directory)
tileset = pygame.image.load("t.png")
tileProp = pygame.image.load("props.png")
colliders = []

colliders = []

clock = pygame.time.Clock()

pygame.init()
some_other_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 20, 50, 50)

class Player:
    def __init__(self, x, y, sizeX, sizeY, events):
        self.x = x
        self.y = y
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.curr_frame = 0
        self.curr_frame_time = 0

        self.currAnim = 0

        self.spriteSheet = pygame.image.load("Walk.png")
        self.PlayerAnimations = []

        self.events = events

        self.speed = 1

    def handle(self, dt):

        keys = pygame.key.get_pressed()

        # Animations
        self.PlayerAnimations = [
            pygame.Rect(self.curr_frame * 32, 0, 32, 32),        # DOWN
            pygame.Rect(self.curr_frame * 32, 32, 32, 32),      # UP
            pygame.Rect(self.curr_frame * 32, 64, 32, 32),  # LEFT
            pygame.Rect(self.curr_frame * 32, 96, 32, 32)   # RIGHT
        ]

        # Create a temporary position for testing collisions
        temp_x = self.x
        temp_y = self.y

        print(temp_x, temp_y)

        if keys[pygame.K_RIGHT] and self.x < WORLD_WIDTH - 100 + 32:
            self.x = self.x + self.speed * dt
            self.currAnim = 2
        elif keys[pygame.K_LEFT] and self.x > 0:
            self.x = self.x - self.speed * dt
            self.currAnim = 3
        elif keys[pygame.K_UP] and self.y > 0:
            self.y = self.y - self.speed * dt
            self.currAnim = 1
        elif keys[pygame.K_DOWN] and self.y < WORLD_HEIGHT - 100 + 32:
            self.y = self.y + self.speed * dt
            self.currAnim = 0

        # Animation handling
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            if self.curr_frame_time >= 100:
                self.curr_frame = (self.curr_frame + 1) % 4
                self.curr_frame_time = 0
            self.curr_frame_time += dt
        else:
            self.curr_frame = 3

        global collider_jogador
        collider_jogador = pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY)

        if any(collider_jogador.colliderect(floor) for floor in colliders):
            self.x = temp_x
            self.y = temp_y

    def show(self, screen):
        # Scaling the player image
        current_frame = self.spriteSheet.subsurface(self.PlayerAnimations[self.currAnim])
        scaled_frame = pygame.transform.scale(current_frame, (self.PlayerAnimations[self.currAnim].width * 2, self.PlayerAnimations[self.currAnim].height * 2))

        pygame.draw.rect(screen, (0, 255, 0), collider_jogador)

        # Draw Player
        screen.blit(scaled_frame, (self.x - offset_x, self.y - offset_y))


def read(file_path):
    with open(file_path, 'r') as file:
        pattern = [line.strip().split() for line in file]
    return pattern

def draw_tiles(screen):

    g = tileset.subsurface(pygame.Rect(0, 0, 32, 32))
    f = tileset.subsurface(pygame.Rect(32 * 7, 0, 32, 32))
    r = tileset.subsurface(pygame.Rect(32, 32 * 5, 32, 32))

    box = tileProp.subsurface(pygame.Rect(32 * 3, 32, 32, 32))

    tile_images = {
        'G': pygame.transform.scale(g, (g.get_width() * 2, g.get_height() * 2)),
        'F': pygame.transform.scale(f, (f.get_width() * 2, f.get_height() * 2)),
        'R': pygame.transform.scale(r, (r.get_width() * 2, r.get_height() * 2)),
        'B': pygame.transform.scale(box, (box.get_width() * 2, box.get_height() * 2)),
    }

    colliders.clear()
    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile in tile_images:
                screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))
    
    for y, row in enumerate(prop_map):
        for x, tile in enumerate(row):
            if tile in tile_images:
                if tile == 'B':
                    screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))
                    colliders.append(pygame.Rect(x * 64 - offset_x, y * 64 - offset_y, 64, 64))

def cameraUpdate(player):
    global camera
    camera.center = (player.x, player.y)
    camera.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

def load(events):
    global PlayerX, tile_map, prop_map

    PlayerX = Player(100, 100, 32, 32, events)  # Initialize player with proper size and position

    tile_map = read('map.txt')
    prop_map = read('propMap.txt')

def update(dt):
    PlayerX.handle(dt)
    
    cameraUpdate(PlayerX)

    draw(screen)


def draw(screen):
    global offset_x, offset_y
    offset_x = camera.left
    offset_y = camera.top

    screen.fill((152, 209, 250))

    draw_tiles(screen)
    PlayerX.show(screen)

    pygame.display.flip()


load(pygame.event.get())
while True:
    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    clock.tick(60)
    dt = clock.get_time()
    
    update(dt)
    pygame.display.update()

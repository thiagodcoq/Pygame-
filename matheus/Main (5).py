import pygame, sys, Classes
from pygame.locals import QUIT

# Constants
WIDTH, HEIGHT = 1000, 700
WORLD_WIDTH, WORLD_HEIGHT = 1100, 1300

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game")

# Camera setup
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
offset_x, offset_y = 0, 0

# Load assets (assuming these files are in the same directory)
tileset = pygame.image.load("Tiles/Dungeon_Tileset.png")
tileProp = pygame.image.load("Tiles/props.png")
colliders = []

heart_image = pygame.image.load("Sprites/heart.png")
# Redimensionar a imagem do coração
heart_image = pygame.transform.scale(heart_image, (40, 40))

clock = pygame.time.Clock()

pygame.init()
fonteScore = pygame.font.Font(None, 48)  # Inicializa a fonte
fonteObjective = pygame.font.Font(None, 40)  # Inicializa a fonte
some_other_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 20, 50, 50)

def read(file_path):
    with open(file_path, 'r') as file:
        pattern = [line.strip().split() for line in file]
    return pattern

def draw_tiles(screen):
    g = tileset.subsurface(pygame.Rect(32, 0, 32, 32)) #Top
    f = tileset.subsurface(pygame.Rect(0, 32, 32, 32)) #Left
    r = tileset.subsurface(pygame.Rect(32 * 2, 32, 32, 32)) # Right
    b = tileset.subsurface(pygame.Rect(32, 32 * 2, 32, 16)) # Corner Bottom Right
    
    c1 = tileset.subsurface(pygame.Rect(0, 0, 32, 32)) # Corner Top Left
    c2 = tileset.subsurface(pygame.Rect(32 * 2, 0, 32, 32)) # Corner Top Right

    c3 = tileset.subsurface(pygame.Rect(0, 32 * 2, 32, 16)) # Corner Bottom Left
    c4 = tileset.subsurface(pygame.Rect(32 * 2, 32 * 2, 32, 16)) # Corner Bottom Right

    floor = tileset.subsurface(pygame.Rect(32, 32, 32, 32)) # Floor

    tile_images = {
        'G': pygame.transform.scale(g, (g.get_width() * 2, g.get_height() * 2)),
        'F': pygame.transform.scale(f, (f.get_width() * 2, f.get_height() * 2)),
        'R': pygame.transform.scale(r, (r.get_width() * 2, r.get_height() * 2)),
        'B': pygame.transform.scale(b, (r.get_width() * 2, r.get_height())),
        
        'Q': pygame.transform.scale(c1, (r.get_width() * 2, r.get_height() * 2)),
        'W': pygame.transform.scale(c2, (r.get_width() * 2, r.get_height() * 2)),
        'E': pygame.transform.scale(c3, (r.get_width() * 2, r.get_height())),
        'S': pygame.transform.scale(c4, (r.get_width() * 2, r.get_height())),

        'V': pygame.transform.scale(floor, (r.get_width() * 2, r.get_height() * 2)),
    }

    colliders.clear()
    for y, row in enumerate(tile_floor):
        for x, tile in enumerate(row):
            if tile in tile_images:
                screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))

    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile in tile_images:
                    colliders.append(pygame.Rect(x * 64 - offset_x, y * 64 - offset_y, 32, 32))
                    screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))
    
    
def cameraUpdate(player):
    global camera
    camera.center = (player.x, player.y)
    camera.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
    
def draw_score(screen, score):
    global fonteScore
    
    score_text = fonteScore.render("Kills: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))  # Desenha o texto na posição (10, 10)

def draw_objective(screen):
    global fonteObjective
    
    score_text = fonteObjective.render("Kill 10 enemies to win", True, (142, 195, 245))
    screen.blit(score_text, (250, 10))
    
def draw_heart(screen, qtdHearts):
    yHeart = 650
    
    for i in range(qtdHearts):
        screen.blit(heart_image, (yHeart, 10))
        yHeart += 50
        
def load():
    global PlayerX, tile_map, prop_map, Gun, bullets, tile_floor

    PlayerX = Classes.Player(65, 65, 32, 32, WORLD_WIDTH, WORLD_HEIGHT, colliders)  # Initialize player with proper size and position
    
    Gun = Classes.Gun(PlayerX)

    pygame.mixer.music.load("sound/music.wav")
    pygame.mixer.music.play(-1)
   
    bullets = pygame.sprite.Group()

    tile_map = read('map.txt')
    tile_floor = read('floorMapping.txt')
    prop_map = read('propMap.txt')

def update(dt):
    PlayerX.handle(dt, offset_x, offset_y)

    Gun.handle(dt, offset_x, offset_y, bullets)
    bullets.update(dt)
    
    cameraUpdate(PlayerX)
    draw(screen)

def draw(screen):
    global offset_x, offset_y
    offset_x = camera.left
    offset_y = camera.top

    screen.fill((152, 209, 250))

    draw_tiles(screen)
    PlayerX.show(screen, offset_x, offset_y)
    bullets.draw(screen)
    Gun.show(screen, offset_x, offset_y)

    draw_score(screen, PlayerX.score)
    draw_heart(screen, PlayerX.life)
    draw_objective(screen)

    pygame.display.flip()

load()
while True:    
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if pygame.key.get_pressed()[pygame.K_r]:
            load()

    #print(bullets)

    clock.tick(60)
    dt = clock.get_time()
    update(dt)
    pygame.display.update()
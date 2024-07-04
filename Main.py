import pygame, sys, Classes, random
from pygame.locals import QUIT

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
WORLD_WIDTH, WORLD_HEIGHT = 2100, 1300

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeons and Pygame")

# Camera setup
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
offset_x, offset_y = 0, 0

# Load assets (assuming these files are in the same directory)
tileset = pygame.image.load("Tiles/Dungeon_Tileset.png")
tileProp = pygame.image.load("Tiles/props.png")
colliders = []

# UI
heart_image = pygame.image.load("Sprites/heart.png")
# Redimensionar a imagem do coração
heart_image = pygame.transform.scale(heart_image, (40, 40))


fonteObjective = pygame.font.Font("Bodoni 72 OS.ttc", 28)
fonteScore = pygame.font.Font("Bodoni 72 OS.ttc", 40)
fonteGameOver = pygame.font.Font("Bodoni 72 OS.ttc", 80)

clock = pygame.time.Clock()

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

        'v': pygame.transform.scale(floor, (r.get_width() * 2, r.get_height() * 2)),
    }

    colliders.clear()
    for y, row in enumerate(tile_map):
        for x, tile in enumerate(row):
            if tile in tile_images:
                if tile == 'v':
                    screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))
                else:
                    colliders.append(pygame.Rect(x * 64 - offset_x, y * 64 - offset_y, 32, 32))
                    screen.blit(tile_images[tile], (x * 64 - offset_x, y * 64 - offset_y))
    
def cameraUpdate(player):
    global camera
    camera.center = (player.x, player.y)
    camera.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

def draw_score(screen):
    global fonteScore
    
    score_text = fonteScore.render("Wave: " + str(waveCount), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))  # Desenha o texto na posição (10, 10)

def draw_objective(screen):
    global fonteObjective
    
    score_text = fonteObjective.render("%s enemies remaining in this wave" %str(len(Enemies)), True, (142, 195, 245))
    screen.blit(score_text, (250, 10))
    
def draw_heart(screen, qtdHearts):
    yHeart = 650
    
    for i in range(qtdHearts):
        screen.blit(heart_image, (yHeart, 10))
        yHeart += 50

def waves():
    global waveCount
    if len(Enemies) <= 0:
        waveCount += 1
        spawn()

def spawn():
    num = waveCount * 2

    min_distance_from_player = 300
    max_attempts = 1000
    for _ in range(num):
        for enemy_type in [Classes.Enemy(random.randint(32, WIDTH-32), random.randint(32, HEIGHT-32), 32, 32, WORLD_WIDTH, WORLD_HEIGHT, colliders, PlayerX, bullets, 3, esqueleto, 0.1), 
                           Classes.Enemy(random.randint(32, WIDTH-32), random.randint(32, HEIGHT-32), 32, 32, WORLD_WIDTH, WORLD_HEIGHT, colliders, PlayerX, bullets, 2, morcego, 0.15)]:
            
            attempts = 0
            while attempts < max_attempts:
                x = random.randint(32, WIDTH - 32)
                y = random.randint(32, HEIGHT - 32)
                
                if ((x - PlayerX.collider_jogador.x) and (y - PlayerX.collider_jogador.y)) >= min_distance_from_player:
                    enemy_rect = pygame.Rect(x, y, 32, 32)
                    if not any(enemy_rect.colliderect(e.rect) for e in Enemies):
                        enemy_type.rect.topleft = (x, y)
                        Enemies.append(enemy_type)
                        break
                attempts += 1

            if attempts >= max_attempts:
                print("Warning: Could not find a valid spawn location for an enemy.")

def load():
    global PlayerX, tile_map, prop_map, Gun, bullets, tile_floor, Enemies, waveCount, game_over
    waveCount = 1

    Enemies = []
    
    PlayerX = Classes.Player(WIDTH/2, HEIGHT/2, 32, 32, WORLD_WIDTH, WORLD_HEIGHT, colliders, Enemies, 3)  # Initialize player with proper size and position
    
    global esqueleto, morcego
    esqueleto = [pygame.image.load("Sprites/S1.png"), pygame.image.load("Sprites/S2.png"), pygame.image.load("Sprites/S3.png"), pygame.image.load("Sprites/S4.png")]
    morcego = [pygame.image.load("Sprites/M1.png"), pygame.image.load("Sprites/M2.png"), pygame.image.load("Sprites/M3.png"), pygame.image.load("Sprites/M4.png")]

    Gun = Classes.Gun(PlayerX)
    bullets = pygame.sprite.Group()
    tile_map = read('map.txt')
    
    spawn()
        
    pygame.mixer.music.load("music.wav")
    pygame.mixer.music.play(-1)
    game_over = False

def check_game_over():
    global game_over
    if PlayerX.life <= 0:
        game_over = True

def show_game_over(screen):
    global fonteGameOver
    game_over_text = fonteGameOver.render("YOU DIED", True, (255, 0, 0))
    wave_text = fonteGameOver.render("Wave: " + str(waveCount), True, (255, 255, 255))
    restart_text = fonteScore.render("Press R to restart", True, (255, 255, 255))
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2 - 40))
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 - wave_text.get_height() // 2 + 40))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 - restart_text.get_height() // 2 + 120))
    
    pygame.display.flip()

def update(dt):
    if game_over:
        return

    PlayerX.handle(dt, offset_x, offset_y)

    Gun.handle(dt, offset_x, offset_y, bullets)
    bullets.update(dt, colliders, Enemies)
    
    if len(Enemies) > 0:
        for enemy in Enemies:
        
            colliders.append(enemy.rect)
            enemy.handle(dt, offset_x, offset_y)
        
            if(enemy.life <= 0):
                Enemies.remove(enemy)
    else:
        waves()

    cameraUpdate(PlayerX)
    draw(screen)
    check_game_over()

def draw(screen):
    global offset_x, offset_y
    offset_x = camera.left
    offset_y = camera.top

    screen.fill(("#25131A"))

    draw_tiles(screen)

    PlayerX.show(screen, offset_x, offset_y)
    bullets.draw(screen)
    Gun.show(screen, offset_x, offset_y)

    for enemy in Enemies:
        enemy.show(screen, offset_x, offset_y)


    draw_score(screen)
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

    clock.tick(60)
    dt = clock.get_time()
    update(dt)
    
    if game_over:
        show_game_over(screen)
    else:
        pygame.display.update()

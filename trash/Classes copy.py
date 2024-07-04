import pygame
import math

class Player:
    def __init__(self, x, y, sizeX, sizeY, world_width, world_height, colliders):
        self.x = x
        self.y = y
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.curr_frame = 0
        self.curr_frame_time = 0

        self.currAnim = 0

        self.spriteSheet = pygame.image.load("Sprites/Walk.png")
        self.PlayerAnimations = []

        self.speed = 0.3

        self.world_width = world_width
        self.world_height = world_height
        self.colliders = colliders

    def handle(self, dt, offset_x, offset_y):
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

        if keys[pygame.K_d] and self.x < self.world_width - 100 + 32:
            self.x = self.x + self.speed * dt
            self.currAnim = 2
        if keys[pygame.K_a] and self.x > 0:
            self.x = self.x - self.speed * dt
            self.currAnim = 3
        if keys[pygame.K_w] and self.y > 0:
            self.y = self.y - self.speed * dt
            self.currAnim = 1
        if keys[pygame.K_s] and self.y < self.world_height - 100 + 32:
            self.y = self.y + self.speed * dt
            self.currAnim = 0

        # Animation handling
        if keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_s]:
            if self.curr_frame_time >= 100:
                self.curr_frame = (self.curr_frame + 1) % 4
                self.curr_frame_time = 0
            self.curr_frame_time += dt
        else:
            self.curr_frame = 3

        collider_jogador = pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY)

        if any(collider_jogador.colliderect(floor) for floor in self.colliders):
            self.x = temp_x
            self.y = temp_y

    def show(self, screen, offset_x, offset_y):
        # Scaling the player image
        current_frame = self.spriteSheet.subsurface(self.PlayerAnimations[self.currAnim])
        scaled_frame = pygame.transform.scale(current_frame, (self.PlayerAnimations[self.currAnim].width * 2, self.PlayerAnimations[self.currAnim].height * 2))

        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY))

        # Draw Player
        screen.blit(scaled_frame, (self.x - offset_x, self.y - offset_y))

class Gun:
    def __init__(self, Player):
        self.x = Player.x
        self.y = Player.y
        self.sizeX = 32
        self.sizeY = 32

        self.anchor = Player

        self.curr_frame = 0
        self.curr_frame_time = 0

        self.currAnim = 0

        self.spriteSheet = pygame.image.load("Sprites/Gun.png")
        self.Animations = []

        self.shooting = False
        self.cooldown = 0
        self.angle = 0

    def Rotation(self, offset_x, offset_y):
        # Rotate the gun on its own axis
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x + offset_x - self.x, mouse_y + offset_y - self.y
        
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        
    def Shoot(self, bullets, offset_x, offset_y):
        # Convert angle to a direction vector
        direction = pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
        bullet = Bullet((self.x - offset_x + 10, self.y - offset_y), direction)
        bullets.add(bullet)

    def handle(self, dt, offset_x, offset_y, bullets):
        keys = pygame.key.get_pressed()

        # Positioning
        self.x = self.anchor.x + self.anchor.sizeX
        self.y = self.anchor.y + self.anchor.sizeY + 5

        # Rotation
        self.Rotation(offset_x, offset_y)

        # Animations
        self.Animations = [
            pygame.Rect(self.curr_frame * 48 + 48, 64, 48, 24),  # Idle
            pygame.Rect(self.curr_frame * 48, 0, 48, 24),   # Shoot
        ]

        # Shooting (modified to trigger only on click)
        if self.cooldown <= 0:
            if pygame.mouse.get_pressed()[0] and not self.shooting:
                self.shooting = True
                self.currAnim = 1
                self.curr_frame = 0
                self.cooldown = 0
                self.Shoot(bullets, offset_x, offset_y)
        else:
            self.cooldown -= dt  # Remove the multiplication by 1000 to handle time correctly

        # Animation handling
        if self.shooting:
            if self.curr_frame_time >= 50:
                self.curr_frame += 1
                self.curr_frame_time = 0

            if self.curr_frame >= 7:
                self.shooting = False

            self.curr_frame_time += dt
        else:
            self.curr_frame = 0
            self.curr_frame_time = 0
            self.currAnim = 0

    def show(self, screen, offset_x, offset_y):
        # Get the current frame from the sprite sheet
        current_frame = self.spriteSheet.subsurface(self.Animations[self.currAnim])
        scaled_frame = pygame.transform.scale(current_frame, (int(self.Animations[self.currAnim].width * 1.3), int(self.Animations[self.currAnim].height * 1.3)))

        if self.angle > 90 or self.angle < -90:
            scaled_frame = pygame.transform.flip(scaled_frame, False, True)

        self.rotated_image = pygame.transform.rotate(scaled_frame, self.angle)
        self.rotated_rect = self.rotated_image.get_rect(center=(self.x - offset_x, self.y - offset_y))

        # Draw the gun
        screen.blit(self.rotated_image, self.rotated_rect.topleft)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, size=10, color=(255, 0, 0)):
        super().__init__()  # Initialize the parent Sprite class
        self.image = pygame.Surface((size, size))  # Create a square surface for the bullet
        self.image.fill(color)  # Fill the square with the specified color
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction  # Direction as a Vector2
        self.speed = 600  # Adjusted speed for visibility
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        # Move the bullet based on direction and speed
        self.rect.center += self.direction * self.speed * dt / 1000  # Corrected for dt
        # Check if the bullet's lifetime has exceeded and remove it
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()  # Remove the sprite from all groups



class Enemy:
    def __init__(self, x, y, sizeX, sizeY, world_width, world_height, colliders):
        self.x = x
        self.y = y
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.curr_frame = 0
        self.curr_frame_time = 0

        self.currAnim = 0

        self.spriteSheet = pygame.image.load("Sprites/Walk.png")
        self.PlayerAnimations = []

        self.speed = 0.3

        self.world_width = world_width
        self.world_height = world_height
        self.colliders = colliders

    def handle(self, dt, offset_x, offset_y):
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

        if keys[pygame.K_d] and self.x < self.world_width - 100 + 32:
            self.x = self.x + self.speed * dt
            self.currAnim = 2
        if keys[pygame.K_a] and self.x > 0:
            self.x = self.x - self.speed * dt
            self.currAnim = 3
        if keys[pygame.K_w] and self.y > 0:
            self.y = self.y - self.speed * dt
            self.currAnim = 1
        if keys[pygame.K_s] and self.y < self.world_height - 100 + 32:
            self.y = self.y + self.speed * dt
            self.currAnim = 0

        # Animation handling
        if keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_s]:
            if self.curr_frame_time >= 100:
                self.curr_frame = (self.curr_frame + 1) % 4
                self.curr_frame_time = 0
            self.curr_frame_time += dt
        else:
            self.curr_frame = 3

        collider_jogador = pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY)

        if any(collider_jogador.colliderect(floor) for floor in self.colliders):
            self.x = temp_x
            self.y = temp_y

    def show(self, screen, offset_x, offset_y):
        # Scaling the player image
        current_frame = self.spriteSheet.subsurface(self.PlayerAnimations[self.currAnim])
        scaled_frame = pygame.transform.scale(current_frame, (self.PlayerAnimations[self.currAnim].width * 2, self.PlayerAnimations[self.currAnim].height * 2))

        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY))

        # Draw Player
        screen.blit(scaled_frame, (self.x - offset_x, self.y - offset_y))

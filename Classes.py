import pygame
import math

class Player:
    def __init__(self, x, y, sizeX, sizeY, world_width, world_height, colliders, Enemies, life):
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
        self.Enemies = Enemies

        self.life = life
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 3000  # 3 seconds
        
        self.collider_jogador = pygame.Rect(self.x, self.y, self.sizeX, self.sizeY)
    
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
        if keys[pygame.K_a] and self.x > 32:
            self.x = self.x - self.speed * dt
            self.currAnim = 3
        if keys[pygame.K_w] and self.y > 0:
            self.y = self.y - self.speed * dt
            self.currAnim = 1
        if keys[pygame.K_s] and self.y < self.world_height - 120 + 32:
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

        self.collider_jogador = pygame.Rect(self.x + self.sizeX/2 - offset_x, self.y + self.sizeY/2 - offset_y, self.sizeX, self.sizeY)

        if any(self.collider_jogador.colliderect(obj) for obj in self.colliders):
            self.x = temp_x
            self.y = temp_y
        
        for enemy in self.Enemies:
            if self.collider_jogador.colliderect(enemy.rect) and not self.invincible:
                self.Hit()

        # Check if invincibility should end
        if self.invincible and pygame.time.get_ticks() - self.invincible_start_time >= self.invincible_duration:
            self.invincible = False

    def Hit(self):
        # Take 1 life point
        self.life -= 1

        # Start invincibility
        self.invincible = True
        self.invincible_start_time = pygame.time.get_ticks()

    def show(self, screen, offset_x, offset_y):
        # Scaling the player image
        current_frame = self.spriteSheet.subsurface(self.PlayerAnimations[self.currAnim])
        scaled_frame = pygame.transform.scale(current_frame, (self.PlayerAnimations[self.currAnim].width * 2, self.PlayerAnimations[self.currAnim].height * 2))

        # Blink effect for invincibility
        if self.invincible:
            if (pygame.time.get_ticks() // 200) % 2 == 0:  # Blink every 200 ms
                screen.blit(scaled_frame, (self.x - offset_x, self.y - offset_y))
        else:
            screen.blit(scaled_frame, (self.x - offset_x, self.y - offset_y))

        #pygame.draw.rect(screen, (0, 255, 0), self.collider_jogador)

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
        #screen.blit(self.rotated_image, self.rotated_rect.topleft)

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

    def update(self, dt, *target_groups):
        # Move the bullet based on direction and speed
        self.rect.center += self.direction * self.speed * dt / 1000  # Corrected for dt
        
        for rect in target_groups:
            for i in rect:
                if self.rect.colliderect(i):
                    if type(i) == Enemy: 
                        i.get_hit()

                    self.kill()  # Remove the bullet if it collides with any rect
                    break
        
        # Check if the bullet's lifetime has exceeded and remove it
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()  # Remove the sprite from all groups

class Enemy:
    def __init__(self, x, y, sizeX, sizeY, world_width, world_height, colliders, Player, bullets, life, sprite, speed):
        self.x = x
        self.y = y

        self.sizeX = sizeX
        self.sizeY = sizeY

        self.curr_frame = 0

        self.PlayerAnimations = []

        for img in sprite:
            scaled_img = pygame.transform.scale(img, (self.sizeX * 2, self.sizeY * 2))
            self.PlayerAnimations.append(scaled_img)

        self.speed = speed
        self.anchor = Player

        self.world_width = world_width
        self.world_height = world_height

        self.colliders = colliders

        self.stopping_distance = 32  # Distance at which the enemy stops to avoid overlapping

        self.rect = pygame.Rect(self.x, self.y, 48, 48)  # Adjusted hitbox size to 48x48
        self.direction = pygame.Vector2()

        self.bullets = bullets
        self.life = life

        self.hit = False
        self.hit_time = 0
        self.hit_duration = 100

        self.animation_time = 150
        self.animation_speed = 150

    def handle(self, dt, offset_x, offset_y):
        rel_x, rel_y = 0, 0

        # Calculate the vector to the player
        if (self.x < self.world_width - 100 + 32) and (self.x > 0):
            rel_x = self.anchor.x - 4 - self.x

        if (self.y < self.world_height - 120 + 32) and (self.y > 0):
            rel_y = self.anchor.y - 4 - self.y

        # Calculate the distance to the player
        distance = math.sqrt(rel_x**2 + rel_y**2)

        # Check if the enemy is within the stopping distance
        if distance > self.stopping_distance:
            # Calculate the direction vector
            self.direction = pygame.Vector2(rel_x / distance, rel_y / distance)

            # Update the position of the enemy
            self.x += self.direction.x * self.speed * dt
            self.y += self.direction.y * self.speed * dt

        # Animation handling
        self.animation_time += dt
        if self.animation_time > self.animation_speed:
            self.curr_frame = (self.curr_frame + 1) % len(self.PlayerAnimations)
            self.animation_time = 0

        self.rect = pygame.Rect(self.x - offset_x, self.y - offset_y, 48, 48)  # Adjusted hitbox size to 48x48

        # Handle hit effect timing
        if self.hit:
            self.hit_time += dt
            if self.hit_time > self.hit_duration:
                self.hit = False
                self.hit_time = 0

    def show(self, screen, offset_x, offset_y):
        current_frame = self.PlayerAnimations[self.curr_frame]
        if self.hit:
            red_overlay = pygame.Surface((self.sizeX * 1.5, self.sizeY * 1.5), pygame.SRCALPHA)  # Use SRCALPHA for transparency
            red_overlay.fill((255, 0, 0, 128))  # Fill with red color and 50% transparency

            screen.blit(current_frame, (self.x - offset_x, self.y - offset_y))
            screen.blit(red_overlay, (self.x - offset_x, self.y - offset_y))
        else:
            screen.blit(current_frame, (self.x - offset_x, self.y - offset_y))

    def get_hit(self):
        self.hit = True
        self.hit_time = 0
        self.life -= 1
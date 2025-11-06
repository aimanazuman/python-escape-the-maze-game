import pygame
from constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, TILE_SIZE

class Player:

    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.is_moving = False
        self.move_direction = None

        try:
            self.image = pygame.image.load("assets/images/player.png")
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.use_image = True
        except:
            self.image = None
            self.use_image = False

    def handle_input(self, keys):
        """Detect movement key presses"""
        if not self.is_moving:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.move_direction = "left"
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.move_direction = "right"
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.move_direction = "up"
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.move_direction = "down"

    def update(self, walls):
        was_moving = self.is_moving
        """Move one tile per key press"""
        if not self.is_moving and self.move_direction:
            dx, dy = 0, 0
            if self.move_direction == "left":
                dx = -1
            elif self.move_direction == "right":
                dx = 1
            elif self.move_direction == "up":
                dy = -1
            elif self.move_direction == "down":
                dy = 1

            new_x = self.grid_x + dx
            new_y = self.grid_y + dy

            # Build a rect for the next tile
            test_rect = pygame.Rect(
                new_x * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
                new_y * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
                self.size, self.size
            )

            # Check collision with walls
            collision = any(test_rect.colliderect(wall) for wall in walls)

            if not collision:
                self.target_x = new_x * TILE_SIZE + TILE_SIZE // 2
                self.target_y = new_y * TILE_SIZE + TILE_SIZE // 2
                self.grid_x = new_x
                self.grid_y = new_y
                self.is_moving = True

                # audio.sounds["move"].play(loops=-1)

            self.move_direction = None

        elif self.is_moving:
            self._move_towards_target()
            if self._reached_target():
                self.is_moving = False

    def _move_towards_target(self):
        """Smooth movement toward next tile"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if abs(dx) > self.speed:
            self.x += self.speed if dx > 0 else -self.speed
        else:
            self.x = self.target_x

        if abs(dy) > self.speed:
            self.y += self.speed if dy > 0 else -self.speed
        else:
            self.y = self.target_y

    def _reached_target(self):
        return self.x == self.target_x and self.y == self.target_y

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def get_position(self):
        return (self.x, self.y)

    def draw(self, screen):
        if self.use_image and self.image:
            screen.blit(self.image, (self.x - self.size // 2, self.y - self.size // 2))
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
            eye_offset = self.size // 6
            eye_size = self.size // 10
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)

    def reset(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        self.move_direction = None

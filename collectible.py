"""
Collectible Class - Items player can collect for puzzles
"""

import pygame
import math
from constants import COLLECTIBLE_SIZE, COLLECTIBLE_COLOR, TILE_SIZE


class Collectible:
    """Collectible items that must be gathered to escape"""

    def __init__(self, x, y):
        """
        Initialize collectible

        Args:
            x: Grid x position
            y: Grid y position
        """
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.size = COLLECTIBLE_SIZE
        self.color = COLLECTIBLE_COLOR
        self.collected = False
        self.animation_offset = 0
        self.animation_speed = 0.1

        # Try to load collectible image
        try:
            self.image = pygame.image.load("assets/images/collectible.png")
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.use_image = True
        except:
            self.image = None
            self.use_image = False

    def update(self):
        """Update collectible animation"""
        if not self.collected:
            self.animation_offset += self.animation_speed
            if self.animation_offset > 2 * math.pi:
                self.animation_offset = 0

    def check_collision(self, player_rect):
        """
        Check if player collected this item

        Args:
            player_rect: Player collision rectangle

        Returns:
            bool: True if collected
        """
        if not self.collected:
            collectible_rect = self.get_rect()
            if player_rect.colliderect(collectible_rect):
                self.collected = True
                return True
        return False

    def get_rect(self):
        """Get collectible collision rectangle"""
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )

    def draw(self, screen):
        """Draw collectible with floating animation"""
        if not self.collected:
            # Calculate floating offset
            float_offset = math.sin(self.animation_offset) * 5
            draw_y = int(self.y + float_offset)

            if self.use_image and self.image:
                screen.blit(
                    self.image,
                    (self.x - self.size // 2, draw_y - self.size // 2)
                )
            else:
                # Draw as star shape
                points = []
                for i in range(10):
                    angle = math.pi * 2 * i / 10 - math.pi / 2
                    if i % 2 == 0:
                        radius = self.size // 2
                    else:
                        radius = self.size // 4
                    px = self.x + math.cos(angle) * radius
                    py = draw_y + math.sin(angle) * radius
                    points.append((px, py))

                pygame.draw.polygon(screen, self.color, points)
                pygame.draw.polygon(screen, (255, 255, 255), points, 2)

    def reset(self):
        """Reset collectible state"""
        self.collected = False
        self.animation_offset = 0
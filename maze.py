"""
Maze Class - Enhanced visuals with gradients and shadows
"""

import pygame
from constants import TILE_SIZE, BLACK, DARK_GRAY, CYAN, DARK_BLUE, LIGHT_BLUE, WHITE
from player import Player
from enemy import Enemy
from collectible import Collectible


class Maze:
    """Maze with enhanced visual effects"""

    def __init__(self, maze_layout):
        self.layout = maze_layout
        self.walls = []
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.exit_rect = None
        self.exit_unlocked = False
        self._parse_layout()

    def _parse_layout(self):
        self.walls = []
        self.enemies = []
        self.collectibles = []

        for row_idx, row in enumerate(self.layout):
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if cell == 1:
                    wall_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.walls.append(wall_rect)
                elif cell == 2:
                    self.player = Player(col_idx, row_idx)
                elif cell == 3:
                    self.exit_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                elif cell == 4:
                    enemy = Enemy(col_idx, row_idx)
                    self.enemies.append(enemy)
                elif cell == 5:
                    collectible = Collectible(col_idx, row_idx)
                    self.collectibles.append(collectible)

    def update(self):
        if self.player:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.walls)

            player_pos = self.player.get_position()
            for enemy in self.enemies:
                enemy.update(player_pos, self.walls)

            player_rect = self.player.get_rect()
            for collectible in self.collectibles:
                collectible.update()
                collectible.check_collision(player_rect)

            self.exit_unlocked = all(c.collected for c in self.collectibles)

    def check_player_enemy_collision(self):
        if self.player:
            player_rect = self.player.get_rect()
            for enemy in self.enemies:
                if player_rect.colliderect(enemy.get_rect()):
                    return True
        return False

    def check_player_exit_collision(self):
        if self.player and self.exit_rect and self.exit_unlocked:
            player_rect = self.player.get_rect()
            if player_rect.colliderect(self.exit_rect):
                return True
        return False

    def get_collected_count(self):
        return sum(1 for c in self.collectibles if c.collected)

    def get_total_collectibles(self):
        return len(self.collectibles)

    def draw(self, screen):
        # Draw background gradient
        for y in range(0, screen.get_height(), 2):
            ratio = y / screen.get_height()
            color = (
                int(DARK_BLUE[0] * (1 - ratio)),
                int(DARK_BLUE[1] * (1 - ratio)),
                int(DARK_BLUE[2] * (1 - ratio) + 20 * ratio)
            )
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))

        # Draw walls with depth
        for wall in self.walls:
            # Shadow
            shadow_rect = wall.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, BLACK, shadow_rect)

            # Main wall with gradient
            pygame.draw.rect(screen, (80, 80, 100), wall)
            pygame.draw.rect(screen, (120, 120, 140), wall, 2)

            # Highlight
            highlight = pygame.Rect(wall.x + 2, wall.y + 2, wall.w - 4, wall.h - 4)
            pygame.draw.rect(screen, (100, 100, 120), highlight, 1)

        # Draw exit with glow
        if self.exit_rect:
            if self.exit_unlocked:
                # Glow effect
                for i in range(3):
                    glow_rect = self.exit_rect.inflate(i * 6, i * 6)
                    glow_surf = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
                    alpha = 60 - i * 15
                    pygame.draw.rect(glow_surf, (0, 255, 0, alpha), glow_surf.get_rect(), border_radius=5)
                    screen.blit(glow_surf, glow_rect)

                color = (0, 220, 0)
            else:
                color = (100, 100, 100)

            pygame.draw.rect(screen, color, self.exit_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, self.exit_rect, 3, border_radius=5)

            font = pygame.font.Font(None, 20)
            text = font.render("EXIT", True, WHITE)
            text_rect = text.get_rect(center=self.exit_rect.center)
            screen.blit(text, text_rect)

        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw player
        if self.player:
            self.player.draw(screen)

    def reset(self):
        self._parse_layout()
        self.exit_unlocked = False
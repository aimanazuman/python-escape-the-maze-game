"""
UI Module - Enhanced visual design
"""

import pygame
from constants import *

class Button:
    """Modern animated button"""

    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.clicked = False
        self.scale = 1.0

    def update(self, mouse_pos, mouse_pressed):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # Smooth scale animation
        if self.is_hovered:
            self.scale = min(1.05, self.scale + 0.02)
        else:
            self.scale = max(1.0, self.scale - 0.02)

        if self.is_hovered and mouse_pressed and not self.clicked:
            self.clicked = True
            return True

        if not mouse_pressed:
            self.clicked = False

        return False

    def draw(self, screen):
        # Create scaled rect
        scaled_w = int(self.rect.w * self.scale)
        scaled_h = int(self.rect.h * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_w // 2,
            self.rect.centery - scaled_h // 2,
            scaled_w, scaled_h
        )

        # Shadow
        shadow = scaled_rect.copy()
        shadow.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow, border_radius=12)

        # Button
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, scaled_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, scaled_rect, 3, border_radius=12)

        font = pygame.font.Font(FONT_NAME, int(FONT_SIZE_MEDIUM * self.scale))
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)

class UI:
    """Enhanced UI manager"""

    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self._create_buttons()

    def _create_buttons(self):
        button_y = 280
        button_spacing = 90

        self.menu_start_btn = Button(
            SCREEN_WIDTH // 2 - 120, button_y, 240, 50, "START", (30, 144, 255), CYAN
        )
        self.menu_instructions_btn = Button(
            SCREEN_WIDTH // 2 - 120, button_y + button_spacing, 240, 50, "INSTRUCTIONS", BLUE, LIGHT_BLUE
        )
        self.menu_exit_btn = Button(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 180, 240, 50, "EXIT", RED, ORANGE
        )

        self.instructions_back_btn = Button(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 50, "BACK", BLUE, CYAN
        )

        pause_y = 280
        self.pause_resume_btn = Button(
            SCREEN_WIDTH // 2 - 120, pause_y, 240, 50, "RESUME", GREEN, CYAN
        )
        self.pause_restart_btn = Button(
            SCREEN_WIDTH // 2 - 120, pause_y + 90, 240, 50, "RESTART", BLUE, LIGHT_BLUE
        )
        self.pause_menu_btn = Button(
            SCREEN_WIDTH // 2 - 120, pause_y + 180, 240, 50, "MAIN MENU", RED, ORANGE
        )

        win_y = 420
        self.win_next_btn = Button(
            SCREEN_WIDTH // 2 - 120, win_y, 240, 50, "NEXT LEVEL", GREEN, CYAN
        )
        self.win_menu_btn = Button(
            SCREEN_WIDTH // 2 - 120, win_y + 90, 240, 50, "MAIN MENU", BLUE, LIGHT_BLUE
        )

        lose_y = 380
        self.lose_retry_btn = Button(
            SCREEN_WIDTH // 2 - 120, lose_y, 240, 50, "RETRY", GREEN, CYAN
        )
        self.lose_menu_btn = Button(
            SCREEN_WIDTH // 2 - 120, lose_y + 90, 240, 50, "MAIN MENU", BLUE, LIGHT_BLUE
        )

    def update_menu(self, mouse_pos, mouse_pressed):
        if self.menu_start_btn.update(mouse_pos, mouse_pressed):
            return "start"
        if self.menu_instructions_btn.update(mouse_pos, mouse_pressed):
            return "instructions"
        if self.menu_exit_btn.update(mouse_pos, mouse_pressed):
            return "exit"
        return None

    def update_instructions(self, mouse_pos, mouse_pressed):
        if self.instructions_back_btn.update(mouse_pos, mouse_pressed):
            return "back"
        return None

    def update_pause(self, mouse_pos, mouse_pressed):
        if self.pause_resume_btn.update(mouse_pos, mouse_pressed):
            return "resume"
        if self.pause_restart_btn.update(mouse_pos, mouse_pressed):
            return "restart"
        if self.pause_menu_btn.update(mouse_pos, mouse_pressed):
            return "menu"
        return None

    def update_win(self, mouse_pos, mouse_pressed):
        if self.win_next_btn.update(mouse_pos, mouse_pressed):
            return "next"
        if self.win_menu_btn.update(mouse_pos, mouse_pressed):
            return "menu"
        return None

    def update_lose(self, mouse_pos, mouse_pressed):
        if self.lose_retry_btn.update(mouse_pos, mouse_pressed):
            return "retry"
        if self.lose_menu_btn.update(mouse_pos, mouse_pressed):
            return "menu"
        return None

    def draw_menu(self):
        # Gradient background
        for y in range(0, SCREEN_HEIGHT, 2):
            ratio = y / SCREEN_HEIGHT
            color = (int(10 + 30 * ratio), int(10 + 40 * ratio), int(30 + 60 * ratio))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        for i in range(3):
            blur_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((0, 0, 0, 40))
            self.screen.blit(blur_surf, (0, 0))

        # Title with glow
        title_text = "ESCAPE THE MAZE!"
        for offset in range(5, 0, -1):
            glow_surf = self.font_large.render(title_text, True, (0, 255, 255, 50))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, 120 + offset))
            self.screen.blit(glow_surf, glow_rect)

        title = self.font_large.render(title_text, True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        subtitle = self.font_small.render("Collect all stars and escape!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(subtitle, subtitle_rect)

        self.menu_start_btn.draw(self.screen)
        self.menu_instructions_btn.draw(self.screen)
        self.menu_exit_btn.draw(self.screen)

    def draw_instructions(self):
        self.screen.fill((15, 20, 40))

        title = self.font_large.render("INSTRUCTIONS", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        instructions = [
            "HOW TO PLAY:",
            "",
            "• Use ARROW KEYS or WASD to move",
            "• Collect all YELLOW STARS to unlock exit",
            "• Avoid RED ENEMIES - they chase you!",
            "• Reach the GREEN EXIT before time runs out",
            "• Press ESC to pause | Press R to restart",
            "",
            "ENEMIES:",
            "• Patrol when you're far away",
            "• Chase when you get close",
            "• Different colors show their state",
        ]

        y = 140
        for line in instructions:
            if line.startswith("•"):
                text = self.font_small.render(line, True, WHITE)
            elif line == "":
                y += 15
                continue
            else:
                text = self.font_medium.render(line, True, YELLOW)

            text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            self.screen.blit(text, text_rect)
            y += 45

        self.instructions_back_btn.draw(self.screen)

    def draw_hud(self, time_left, collected, total, level_name, score):
        # Modern HUD panel
        panel = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 20, 40, 220), panel.get_rect(), border_radius=0)
        pygame.draw.line(panel, CYAN, (0, 60), (SCREEN_WIDTH, 60), 2)
        self.screen.blit(panel, (0, 0))

        # Level
        level_text = self.font_small.render(level_name, True, CYAN)
        level_rect = level_text.get_rect(left=15, centery=15)
        self.screen.blit(level_text, level_rect)

        # Timer with warning
        timer_color = (255, 50, 50) if time_left < 15 else WHITE
        timer_text = self.font_small.render(f"{int(time_left)}s", True, timer_color)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 15))
        self.screen.blit(timer_text, timer_rect)

        # Collectibles
        star_text = self.font_small.render(f"Stars {collected}/{total}", True, YELLOW)
        star_rect = star_text.get_rect(right=SCREEN_WIDTH - 15, centery=15)
        self.screen.blit(star_text, star_rect)

    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Blur effect - draw game dimmed multiple times
        for i in range(3):
            blur_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((0, 0, 0, 40))
            self.screen.blit(blur_surf, (0, 0))

        pause_text = self.font_large.render("PAUSED", True, CYAN)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(pause_text, pause_rect)

        self.pause_resume_btn.draw(self.screen)
        self.pause_restart_btn.draw(self.screen)
        self.pause_menu_btn.draw(self.screen)

    def draw_win_screen(self, level_name, time_taken, score):
        for y in range(0, SCREEN_HEIGHT, 2):
            ratio = y / SCREEN_HEIGHT
            color = (int(10 + 20 * ratio), int(40 + 40 * ratio), int(10 + 30 * ratio))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        victory_text = self.font_large.render("LEVEL COMPLETE!", True, GREEN)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(victory_text, victory_rect)

        stats = [
            f"Level: {level_name}",
            f"Time: {time_taken:.1f}s",
            f"Score: {score}",
        ]

        y = 240
        for stat in stats:
            text = self.font_medium.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 60

        self.win_next_btn.draw(self.screen)
        self.win_menu_btn.draw(self.screen)

    def draw_lose_screen(self, reason):
        for y in range(0, SCREEN_HEIGHT, 2):
            ratio = y / SCREEN_HEIGHT
            color = (int(40 + 20 * ratio), int(10 + 10 * ratio), int(10 + 10 * ratio))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        gameover_text = self.font_large.render("GAME OVER!", True, RED)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(gameover_text, gameover_rect)

        reason_text = self.font_medium.render(reason, True, WHITE)
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        self.screen.blit(reason_text, reason_rect)

        self.lose_retry_btn.draw(self.screen)
        self.lose_menu_btn.draw(self.screen)
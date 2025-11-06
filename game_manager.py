"""
Game Manager - Manages game states, levels, and game flow
"""

import pygame
from constants import *
from maze import Maze
from ui import UI
from audio_manager import AudioManager

class GameManager:
    """Main game manager controlling game flow and states"""

    def __init__(self, screen):
        self.screen = screen
        self.state = STATE_MENU
        self.ui = UI(screen)
        self.audio = AudioManager()

        # 🎵 Load background music ONCE
        pygame.mixer.music.load("assets/sounds/background.mp3")
        pygame.mixer.music.set_volume(0.30)  # lowered volume
        pygame.mixer.music.play(-1)  # loop forever
        self.music_paused = False

        self.current_level = 0
        self.maze = None
        self.timer = 0
        self.max_time = 0
        self.score = 0
        self.last_collected = 0
        self.mouse_pressed = False

    # Music helpers
    def _pause_music(self):
        if not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

    def _resume_music(self):
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False

    def load_level(self, level_index):
        if 0 <= level_index < len(LEVELS):
            level_data = LEVELS[level_index]
            self.maze = Maze(level_data["maze"])
            self.max_time = level_data["time"]
            self.timer = self.max_time
            self.current_level = level_index
            self.last_collected = 0

    def start_game(self):
        self.current_level = 0
        self.score = 0
        self.load_level(self.current_level)
        self.state = STATE_PLAYING
        self._resume_music()

    def restart_level(self):
        self.load_level(self.current_level)
        self.state = STATE_PLAYING
        self._resume_music()

    def next_level(self):
        if self.current_level < len(LEVELS) - 1:
            self.current_level += 1
            self.load_level(self.current_level)
            self.state = STATE_PLAYING
            self._resume_music()
        else:
            self.state = STATE_MENU

    def handle_event(self, event):
        if self.state == STATE_PLAYING:
            self._handle_playing_event(event)

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
            elif event.key == pygame.K_r:
                self.restart_level()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_pressed = mouse_buttons[0]

        if self.state == STATE_MENU:
            self._resume_music()
            self._update_menu(mouse_pos)

        elif self.state == STATE_INSTRUCTIONS:
            self._pause_music()
            self._update_instructions(mouse_pos)

        elif self.state == STATE_PLAYING:
            self._resume_music()
            pygame.mixer.music.set_volume(0.30)
            self._update_playing()

        elif self.state == STATE_PAUSED:
            self._pause_music()
            self._update_pause(mouse_pos)

        elif self.state == STATE_WIN:
            pygame.mixer.music.set_volume(0.10)
            self._update_win(mouse_pos)

        elif self.state == STATE_LOSE:
            self._pause_music()
            self._update_lose(mouse_pos)

    def _update_menu(self, mouse_pos):
        action = self.ui.update_menu(mouse_pos, self.mouse_pressed)
        if action == "start":
            self.start_game()
        elif action == "instructions":
            self.state = STATE_INSTRUCTIONS
        elif action == "exit":
            pygame.quit()
            import sys
            sys.exit()

    def _update_instructions(self, mouse_pos):
        action = self.ui.update_instructions(mouse_pos, self.mouse_pressed)
        if action == "back":
            self.state = STATE_MENU
            self._resume_music()  # ✅ continue music again

    def _update_pause(self, mouse_pos):
        action = self.ui.update_pause(mouse_pos, self.mouse_pressed)
        if action == "resume":
            self.state = STATE_PLAYING
        elif action == "restart":
            self.restart_level()
        elif action == "menu":
            self.state = STATE_MENU

    def _update_win(self, mouse_pos):
        action = self.ui.update_win(mouse_pos, self.mouse_pressed)
        if action == "next":
            self.next_level()
        elif action == "menu":
            self.state = STATE_MENU

    def _update_lose(self, mouse_pos):
        action = self.ui.update_lose(mouse_pos, self.mouse_pressed)
        if action == "retry":
            self.restart_level()
        elif action == "menu":
            self.state = STATE_MENU
            self._resume_music()

    def _update_playing(self):
        if not self.maze:
            return

        self.maze.update()

        collected = self.maze.get_collected_count()
        if collected > self.last_collected:
            self.audio.play_sound("collect")
            self.score += 100
            self.last_collected = collected

        self.timer -= 1 / FPS
        if self.timer <= 0:
            self.audio.play_sound("lose")
            self.state = STATE_LOSE
            self.lose_reason = "Time's up!"
            return

        if self.maze.check_player_enemy_collision():
            self.audio.play_sound("lose")
            self.state = STATE_LOSE
            self.lose_reason = "Caught by enemy!"
            return

        if self.maze.check_player_exit_collision():
            self.audio.play_sound("win")
            time_bonus = int(self.timer * 10)
            self.score += time_bonus + 500
            self.time_taken = self.max_time - self.timer
            self.state = STATE_WIN
            return

    def draw(self):
        if self.state == STATE_MENU:
            self.ui.draw_menu()

        elif self.state == STATE_INSTRUCTIONS:
            self.ui.draw_instructions()

        elif self.state == STATE_PLAYING:
            self.screen.fill(BLACK)
            if self.maze:
                self.maze.draw(self.screen)
                level_data = LEVELS[self.current_level]
                self.ui.draw_hud(
                    self.timer,
                    self.maze.get_collected_count(),
                    self.maze.get_total_collectibles(),
                    level_data["name"],
                    self.score
                )

        elif self.state == STATE_PAUSED:
            if self.maze:
                self.maze.draw(self.screen)
            self.ui.draw_pause_menu()

        elif self.state == STATE_WIN:
            level_data = LEVELS[self.current_level]
            self.ui.draw_win_screen(
                level_data["name"],
                self.time_taken,
                self.score
            )

        elif self.state == STATE_LOSE:
            self.ui.draw_lose_screen(self.lose_reason)

"""
Escape the Maze! - Main Game Entry Point
SWC3643 Python Programming Project
"""

import pygame
import sys
from game_manager import GameManager
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE


def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Create clock for FPS control
    clock = pygame.time.Clock()

    # Create game manager instance
    game_manager = GameManager(screen)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_manager.handle_event(event)

        # Update game state
        game_manager.update()

        # Draw everything
        game_manager.draw()

        # Update display
        pygame.display.flip()

        # Maintain frame rate
        clock.tick(FPS)

    # Quit game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
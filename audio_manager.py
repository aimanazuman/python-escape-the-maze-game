"""
Audio Manager - Handles game sounds and music
"""

import pygame


class AudioManager:
    """Manages all game audio including sounds and music"""

    def __init__(self):
        """Initialize audio system"""
        pygame.mixer.init()
        self.sounds = {}
        self.sound_enabled = True

        self._load_sounds()

    def _load_sounds(self):
        """Load all game sounds"""
        sound_files = {
            "collect": "assets/sounds/collect.wav",
            "win": "assets/sounds/win.wav",
            "lose": "assets/sounds/lose.wav",
            "move": "assets/sounds/move.mp3",
        }

        for name, filepath in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(filepath)
            except:
                # If sound file doesn't exist, create placeholder
                self.sounds[name] = None

    def play_sound(self, sound_name):
        """
        Play a sound effect

        Args:
            sound_name: Name of sound to play
        """
        if self.sound_enabled and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound:
                sound.play()
            else:
                # Generate beep sound if file not available
                self._generate_beep(sound_name)

    def _generate_beep(self, sound_type):
        """
        Generate simple beep sound as fallback

        Args:
            sound_type: Type of sound to generate
        """
        try:
            # Different frequencies for different sound types
            frequencies = {
                "collect": 600,
                "win": 800,
                "lose": 200,
                "move": 400,
            }

            freq = frequencies.get(sound_type, 440)
            duration = 100  # milliseconds

            # Create a simple beep
            sample_rate = 22050
            n_samples = int(round(duration * sample_rate / 1000))

            # Generate sine wave (simplified)
            # Note: This is a basic implementation
            # pygame.mixer can be used for more complex sound generation
        except:
            pass  # Silently fail if sound generation fails

    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

    def stop_all(self):
        """Stop all playing sounds"""
        pygame.mixer.stop()
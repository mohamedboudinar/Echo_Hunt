import math
import pygame
import numpy as np


class AudioManager:
    SAMPLE_RATE = 22050
    CHANNELS = 2

    def __init__(self):
        self.music_enabled = True
        self.sfx_enabled = True
        self.music_volume = 0.18
        self.sfx_volume = 0.60
        self.mixer_ready = False
        self.music_sound = None
        self.sounds = {}
        self.music_channel = None
        self._init_mixer()
        self._load_audio()

    def _init_mixer(self):
        try:
            pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=self.CHANNELS, buffer=512)
            self.mixer_ready = True
        except Exception:
            self.mixer_ready = False

    def _make_wave(self, waveform, duration, volume=0.25, attack=0.01, decay=0.25, stereo=True):
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        if waveform == "sine":
            wave = np.sin(2 * math.pi * 220 * t)
        elif waveform == "pulse":
            wave = np.sign(np.sin(2 * math.pi * 440 * t)) * 0.8
        elif waveform == "noise":
            wave = np.random.uniform(-1.0, 1.0, size=samples)
        else:
            wave = np.sin(2 * math.pi * 220 * t)
        envelope = np.ones_like(wave)
        if attack > 0:
            envelope[: int(samples * min(0.5, attack / duration))] = np.linspace(0, 1, int(samples * min(0.5, attack / duration)))
        if decay > 0:
            tail = int(samples * min(0.9, decay / duration))
            if tail > 0:
                envelope[-tail:] = np.linspace(1, 0, tail)
        wave = wave * envelope * volume
        if stereo:
            stereo_wave = np.column_stack((wave, wave * 0.98))
        else:
            stereo_wave = wave
        array = np.asarray(stereo_wave * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(array)

    def _load_audio(self):
        if not self.mixer_ready:
            return
        # Try to load custom background music, fall back to synthesized
        self.music_sound = self._load_or_create_music()
        self.sounds["dash"] = self._make_wave("pulse", 0.18, volume=0.24, attack=0.001, decay=0.10)
        self.sounds["hit"] = self._make_wave("noise", 0.18, volume=0.18, attack=0.0, decay=0.20)
        self.sounds["menu"] = self._make_wave("sine", 0.16, volume=0.20, attack=0.002, decay=0.10)
        # Load game over and level up sounds
        self._load_event_sounds()
        self.music_channel = pygame.mixer.Channel(0)
        self.music_channel.set_volume(self.music_volume)
        self.play_music()

    def _create_music_loop(self):
        duration = 12.0
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        bass = 0.12 * np.sin(2 * math.pi * 110 * t)
        pad = (
            0.08 * np.sin(2 * math.pi * 165 * t)
            + 0.06 * np.sin(2 * math.pi * 220 * t)
            + 0.05 * np.sin(2 * math.pi * 262 * t)
        )
        pulse = 0.06 * np.sin(2 * math.pi * 88 * t) * (0.45 + 0.55 * np.sin(2 * math.pi * 0.22 * t))
        arp_notes = [220, 247, 262, 294, 330, 349, 392, 440]
        arp = np.zeros_like(t)
        for i, freq in enumerate(arp_notes):
            phase = 2 * math.pi * freq * t
            gate = np.clip(np.sin(2 * math.pi * 0.5 * t - i * 0.78) * 2.2, 0.0, 1.0)
            arp += 0.016 * np.sin(phase) * gate
        melody = 0.07 * np.sin(2 * math.pi * 440 * t + 0.8 * np.sin(2 * math.pi * 0.33 * t))
        hi_hat = 0.03 * np.sin(2 * math.pi * 6800 * t) * np.square(np.mod(t, 0.25) < 0.06)
        wave = bass + pad + pulse + arp + melody + hi_hat
        envelope = 0.97 * np.clip(1.0 - (t / duration) * 0.05, 0.0, 1.0)
        wave = wave * envelope
        stereo_wave = np.column_stack((wave, wave * 0.95))
        array = np.asarray(stereo_wave * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(array)

    def _load_or_create_music(self):
        """Load custom background music if available, otherwise create synthesized music."""
        import os
        music_path = os.path.join("assets", "music", "bg_music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                return True  # Indicates file-based music is loaded
            except Exception as e:
                print(f"Error loading background music: {e}")
                return self._create_music_loop()
        return self._create_music_loop()

    def _load_event_sounds(self):
        """Load game over and level up sound effects."""
        import os
        gameover_path = os.path.join("assets", "sounds", "gameover.wav")
        lvlup_path = os.path.join("assets", "sounds", "lvl_up.mp3")
        
        if os.path.exists(gameover_path):
            try:
                self.sounds["gameover"] = pygame.mixer.Sound(gameover_path)
            except Exception as e:
                print(f"Error loading game over sound: {e}")
        
        if os.path.exists(lvlup_path):
            try:
                self.sounds["level_up"] = pygame.mixer.Sound(lvlup_path)
            except Exception as e:
                print(f"Error loading level up sound: {e}")

    def play_music(self):
        if not self.mixer_ready or not self.music_enabled:
            return
        if self.music_sound is True:
            # File-based music
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
        elif self.music_sound is not None:
            # Synthesized music
            if self.music_channel:
                self.music_channel.stop()
                self.music_channel.play(self.music_sound, loops=-1)

    def stop_music(self):
        if not self.mixer_ready:
            return
        if self.music_sound is True:
            # File-based music
            pygame.mixer.music.stop()
        elif self.music_channel:
            # Synthesized music
            self.music_channel.stop()

    def set_music_enabled(self, enabled):
        self.music_enabled = enabled
        if enabled:
            self.play_music()
        else:
            self.stop_music()

    def set_sfx_enabled(self, enabled):
        self.sfx_enabled = enabled

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_sound is True:
            # File-based music
            pygame.mixer.music.set_volume(self.music_volume)
        elif self.music_channel:
            # Synthesized music
            self.music_channel.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def play_sfx(self, key):
        if not self.mixer_ready or not self.sfx_enabled:
            return
        sound = self.sounds.get(key)
        if sound:
            sound.set_volume(self.sfx_volume)
            sound.play()

    def play_game_over(self):
        """Play the game over sound effect."""
        if not self.mixer_ready or not self.sfx_enabled:
            return
        sound = self.sounds.get("gameover")
        if sound:
            sound.set_volume(self.sfx_volume)
            sound.play()

    def play_level_up(self):
        """Play the level up sound effect."""
        if not self.mixer_ready or not self.sfx_enabled:
            return
        sound = self.sounds.get("level_up")
        if sound:
            sound.set_volume(self.sfx_volume)
            sound.play()

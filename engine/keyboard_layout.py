import locale
import sys

import pygame


class KeyboardLayout:
    def __init__(self, language_code=None):
        self.language_code = (language_code or self.detect_language()).lower()
        self.name, self.bindings, self.move_label = self._resolve_layout(self.language_code)
        self.movement_labels = self._movement_labels(self.bindings)

    def refresh(self):
        language_code = self.detect_language().lower()
        if language_code == self.language_code:
            return
        self.language_code = language_code
        self.name, self.bindings, self.move_label = self._resolve_layout(self.language_code)
        self.movement_labels = self._movement_labels(self.bindings)

    @staticmethod
    def detect_language():
        if sys.platform == "win32":
            language_code = KeyboardLayout._detect_windows_input_language()
            if language_code:
                return language_code

        lang, _ = locale.getlocale()
        if not lang:
            return "en"
        return lang.split("_", 1)[0]

    @staticmethod
    def _detect_windows_input_language():
        try:
            import ctypes
        except ImportError:
            return None

        try:
            user32 = ctypes.windll.user32
            foreground_window = user32.GetForegroundWindow()
            thread_id = user32.GetWindowThreadProcessId(foreground_window, None)
            keyboard_layout = user32.GetKeyboardLayout(thread_id)
        except (AttributeError, OSError):
            return None

        language_id = keyboard_layout & 0xFFFF
        return KeyboardLayout._language_from_windows_langid(language_id)

    @staticmethod
    def _language_from_windows_langid(language_id):
        primary_language_id = language_id & 0x03FF
        windows_languages = {
            0x07: "de",
            0x09: "en",
            0x0C: "fr",
        }
        return windows_languages.get(primary_language_id)

    @staticmethod
    def _resolve_layout(language_code):
        if language_code == "fr":
            return (
                "AZERTY",
                {
                    "up": pygame.K_z,
                    "left": pygame.K_q,
                    "down": pygame.K_s,
                    "right": pygame.K_d,
                },
                "ZQSD",
            )
        if language_code == "de":
            return (
                "QWERTZ",
                {
                    "up": pygame.K_w,
                    "left": pygame.K_a,
                    "down": pygame.K_s,
                    "right": pygame.K_d,
                },
                "WASD",
            )
        return (
            "QWERTY",
            {
                "up": pygame.K_w,
                "left": pygame.K_a,
                "down": pygame.K_s,
                "right": pygame.K_d,
            },
            "WASD",
        )

    @staticmethod
    def _movement_labels(bindings):
        key_names = {
            pygame.K_w: "W",
            pygame.K_a: "A",
            pygame.K_s: "S",
            pygame.K_d: "D",
            pygame.K_z: "Z",
            pygame.K_q: "Q",
            pygame.K_UP: "Up Arrow",
            pygame.K_LEFT: "Left Arrow",
            pygame.K_DOWN: "Down Arrow",
            pygame.K_RIGHT: "Right Arrow",
        }
        return {
            direction: key_names.get(key, pygame.key.name(key).upper())
            for direction, key in bindings.items()
        }

import locale

import pygame


class KeyboardLayout:
    def __init__(self, language_code=None):
        self.language_code = (language_code or self.detect_language()).lower()
        self.name, self.bindings, self.move_label = self._resolve_layout(self.language_code)

    @staticmethod
    def detect_language():
        lang, _ = locale.getlocale()
        if not lang:
            return "en"
        return lang.split("_", 1)[0]

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

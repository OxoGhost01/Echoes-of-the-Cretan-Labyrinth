import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class MessageManager:
    def __init__(self, font_size=16):
        self.font = pygame.font.SysFont("Arial", font_size)
        self.messages = []
        self.display_time = 5000  # ms
        self.last_time = 0

    def show_message(self, message, duration=None):
        self.messages.append({
            "text": message,
            "duration": duration if duration else self.display_time,
            "start_time": pygame.time.get_ticks()
        })

    def draw(self, surface):
        now = pygame.time.get_ticks()
        for msg in self.messages[:]:
            elapsed = now - msg["start_time"]
            if elapsed > msg["duration"]:
                self.messages.remove(msg)
                continue

            # Wrap text to fit screen width
            max_width = SCREEN_WIDTH - 20
            words = msg["text"].split()
            lines = []
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if self.font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            # Draw each line
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, (0, 0, 0))
                surface.blit(text_surface, (10, SCREEN_HEIGHT - 20*(len(lines)-i)))

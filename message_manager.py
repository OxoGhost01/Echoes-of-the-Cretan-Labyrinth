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
            text_surface = self.font.render(msg["text"], True, (255, 255, 255))
            surface.blit(text_surface, (10, SCREEN_HEIGHT - 30))

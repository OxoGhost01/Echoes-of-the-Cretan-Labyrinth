import pygame
from settings import PLAYER_SIZE, PLAYER_COLOR, PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=start_pos)
        # Pixel-perfect collision mask
        self.mask = pygame.mask.Mask((PLAYER_SIZE, PLAYER_SIZE), fill=True)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy

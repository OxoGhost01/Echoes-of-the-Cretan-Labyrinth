import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from map_manager import MapManager
from player import Player

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aventure Archéologique")
clock = pygame.time.Clock()

# Initialize
player = Player(start_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
map_manager = MapManager("assets/map.png")
all_sprites = pygame.sprite.Group(player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle input
    old_pos = player.rect.topleft
    player.handle_input()

    # Collision with walls
    if map_manager.check_collision(player.rect, player.mask):
        player.rect.topleft = old_pos

    # Room transitions
    if player.rect.x < 0:
        map_manager.move_room("left")
        player.rect.x = SCREEN_WIDTH - player.rect.width
    elif player.rect.x >= SCREEN_WIDTH:
        map_manager.move_room("right")
        player.rect.x = 0
    if player.rect.y < 0:
        map_manager.move_room("up")
        player.rect.y = SCREEN_HEIGHT - player.rect.height
    elif player.rect.y >= SCREEN_HEIGHT:
        map_manager.move_room("down")
        player.rect.y = 0

    # Draw
    screen.blit(map_manager.get_room_surface(), (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

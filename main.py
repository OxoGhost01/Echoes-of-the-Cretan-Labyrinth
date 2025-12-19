import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from map_manager import MapManager
from player import Player
from teleport_manager import TeleportManager
from message_manager import MessageManager


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aventure Archéologique")
clock = pygame.time.Clock()

# Initialize map manager first to know map dimensions
map_manager = MapManager("assets/map.png")

map_manager.current_room = (3, 6)

# Initialize player at center of screen
player = Player(start_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

all_sprites = pygame.sprite.Group(player)
teleport_manager = TeleportManager()

message_manager = MessageManager()
message_manager.show_message("Bienvenue ! Trouvez les 3 clés pour libérer le Mynothor.", 5000)


running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle input
    old_pos = player.rect.topleft
    player.handle_input()
    
    # Collision with walls
    if map_manager.check_collision(
        player.rect,
        player.mask,
        teleport_manager):
        player.rect.topleft = old_pos
        # Check if player is back at spawn room with all keys
        spawn_room = (3, 6)
        if map_manager.current_room == spawn_room:
            if all(map_manager.keys.values()):
                message_manager.show_message(
                    "Bravo ! Vous avez libéré le Mynothor !", 5000
                )

    map_manager.check_keys_at_player(player.rect, message_manager)

    teleport_result = teleport_manager.check_teleport(
        player.rect,
        map_manager.current_room
    )

    if teleport_result:
        new_room, new_pos = teleport_result
        map_manager.current_room = new_room
        player.rect.topleft = new_pos
    
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
    message_manager.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
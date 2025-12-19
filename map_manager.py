import pygame
from PIL import Image
from settings import ROOM_WIDTH, ROOM_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT

class MapManager:
    def __init__(self, map_path):
        self.map_image = Image.open(map_path).convert("RGB")
        self.map_width, self.map_height = self.map_image.size

        self.cols = self.map_width // ROOM_WIDTH
        self.rows = self.map_height // ROOM_HEIGHT
        self.current_room = (0, 0)

        # Precompute wall masks for each room
        self.rooms_masks = []
        for row in range(self.rows):
            row_masks = []
            for col in range(self.cols):
                room_box = (
                    col * ROOM_WIDTH,
                    row * ROOM_HEIGHT,
                    (col + 1) * ROOM_WIDTH,
                    (row + 1) * ROOM_HEIGHT
                )
                room_image = self.map_image.crop(room_box)
                mask = self.create_wall_mask(room_image)
                row_masks.append(mask)
            self.rooms_masks.append(row_masks)

    def create_wall_mask(self, room_image):
        """Create a pygame.Mask where walls = 1 (non-grey pixels)"""
        room_surface = pygame.Surface(room_image.size)
        pixels = room_image.load()
        for y in range(room_image.height):
            for x in range(room_image.width):
                r, g, b = pixels[x, y]
                # Grey pixels are walkable
                if 165 <= r <= 175 and 165 <= g <= 175 and 165 <= b <= 175:
                    room_surface.set_at((x, y), (128, 128, 128))
                else:
                    room_surface.set_at((x, y), (0, 0, 0))
        # Create mask: walls (black) = 1, grey = 0
        mask = pygame.mask.from_threshold(room_surface, (0, 0, 0), (1,1,1,255))
        return mask

    def check_collision(self, player_rect, player_mask):
        """Check pixel-perfect collision between player and current room walls"""
        col, row = self.current_room
        room_mask = self.rooms_masks[row][col]
        offset = (player_rect.left, player_rect.top)
        return room_mask.overlap(player_mask, offset) is not None

    def get_room_surface(self):
        col, row = self.current_room
        room_box = (
            col * ROOM_WIDTH,
            row * ROOM_HEIGHT,
            (col + 1) * ROOM_WIDTH,
            (row + 1) * ROOM_HEIGHT
        )
        room_image = self.map_image.crop(room_box)
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame_image = pygame.image.fromstring(
            room_image.tobytes(), room_image.size, room_image.mode
        )
        surface.blit(pygame_image, (0,0))
        return surface

    def move_room(self, direction):
        x, y = self.current_room
        if direction == "left" and x > 0:
            x -= 1
        elif direction == "right" and x < self.cols - 1:
            x += 1
        elif direction == "up" and y > 0:
            y -= 1
        elif direction == "down" and y < self.rows - 1:
            y += 1
        self.current_room = (x, y)

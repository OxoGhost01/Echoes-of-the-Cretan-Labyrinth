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

        # Spawn position
        self.spawn_room = (3, 6)
        self.spawn_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        
        # Keys inventory (color: has_key)
        self.keys = {
            'black': False,
            'white': False,
            'yellow': False
        }

        self.key_colors = {
            'black': (51, 26, 163),    # #331aa3
            'yellow': (210, 210, 64),  # #d2d240
            'white': (236, 236, 236)   # #ececec
        }
        
        # Precompute wall masks and special room info for each room
        self.rooms_masks = []
        self.rooms_special = []  # Store special room type
        
        for row in range(self.rows):
            row_masks = []
            row_special = []
            for col in range(self.cols):
                room_box = (
                    col * ROOM_WIDTH,
                    row * ROOM_HEIGHT,
                    (col + 1) * ROOM_WIDTH,
                    (row + 1) * ROOM_HEIGHT
                )
                room_image = self.map_image.crop(room_box)
                
                # Detect special room type
                special_type = self.detect_special_room(room_image)
                row_special.append(special_type)
                
                # Create appropriate mask
                if special_type:
                    mask = self.create_special_room_mask(room_image, special_type)
                else:
                    mask = self.create_wall_mask(room_image)
                
                row_masks.append(mask)
            
            self.rooms_masks.append(row_masks)
            self.rooms_special.append(row_special)
    
    def detect_special_room(self, room_image):
        """Detect if room is a special key room by checking dominant non-grey color (for the "castle" rooms)"""
        pixels = room_image.load()
        color_counts = {'black': 0, 'white': 0, 'yellow': 0}
        
        # Sample center area to determine room type
        center_x = room_image.width // 2
        center_y = room_image.height // 2
        sample_size = 20
        
        for y in range(max(0, center_y - sample_size), min(room_image.height, center_y + sample_size)):
            for x in range(max(0, center_x - sample_size), min(room_image.width, center_x + sample_size)):
                r, g, b = pixels[x, y]
                
                # Skip grey pixels
                if 165 <= r <= 175 and 165 <= g <= 175 and 165 <= b <= 175:
                    continue
                
                # Detect black (very dark)
                if r < 30 and g < 30 and b < 30:
                    color_counts['black'] += 1
                # Detect white (very bright)
                elif 205 <= r <= 225 and 205 <= g <= 225 and 205 <= b <= 225:
                    color_counts['white'] += 1
                # Detect yellow
                elif r > 200 and g > 200 and b < 100:
                    color_counts['yellow'] += 1
        
        # Return the dominant special color if any
        max_color = max(color_counts, key=color_counts.get)
        if color_counts[max_color] > 50:  # Threshold to confirm special room
            return max_color
        return None
    
    def create_special_room_mask(self, room_image, room_type):
        """Create mask for special rooms - blocks center if key not found"""
        room_surface = pygame.Surface(room_image.size)
        pixels = room_image.load()
        
        # Define the center passage area (vertical corridor in middle)
        center_left = room_image.width // 2 - 30
        center_right = room_image.width // 2 + 30
        
        for y in range(room_image.height):
            for x in range(room_image.width):
                r, g, b = pixels[x, y]
                
                # Grey pixels are always walkable
                if 165 <= r <= 175 and 165 <= g <= 175 and 165 <= b <= 175:
                    room_surface.set_at((x, y), (128, 128, 128))
                # Check if pixel is in center passage
                elif center_left <= x <= center_right:
                    # Center passage - color it differently to handle dynamically
                    room_surface.set_at((x, y), (64, 64, 64))  # Dark grey for locked passage
                else:
                    # Side walls - always solid
                    room_surface.set_at((x, y), (0, 0, 0))

        mask = pygame.mask.from_threshold(room_surface, (0, 0, 0), (1,1,1,255))
        return mask
    
    def create_wall_mask(self, room_image):
        """
        Normal rooms:
        - Grey floor (#aaaaaa) = walkable
        - Black background = walkable
        - Any other color = wall
        """
        room_surface = pygame.Surface(room_image.size)
        pixels = room_image.load()

        for y in range(room_image.height):
            for x in range(room_image.width):
                r, g, b = pixels[x, y]

                is_grey = (
                    165 <= r <= 175 and
                    165 <= g <= 175 and
                    165 <= b <= 175
                )

                is_black = (r < 30 and g < 30 and b < 30)
                is_white = (r > 230 and g > 230 and b > 230)
                is_yellow = (r > 200 and g > 200 and b < 120)

                if is_grey or is_black or is_white or is_yellow:
                    # Walkable (floor, void, letters -> if cheat enabled)
                    room_surface.set_at((x, y), (128, 128, 128))
                else:
                    # Wall
                    room_surface.set_at((x, y), (0, 0, 0))

        return pygame.mask.from_threshold(
            room_surface, (0, 0, 0), (1, 1, 1, 255)
        )

    
    def check_collision(self, player_rect, player_mask, teleport_manager):
        """Check pixel-perfect collision between player and current room walls"""
        col, row = self.current_room
        special_type = self.rooms_special[row][col]
        
        # If special room and player doesn't have key, check center collision
        if special_type and not self.keys[special_type]:
            # Create temporary mask with center blocked
            room_box = (
                col * ROOM_WIDTH,
                row * ROOM_HEIGHT,
                (col + 1) * ROOM_WIDTH,
                (row + 1) * ROOM_HEIGHT
            )
            room_image = self.map_image.crop(room_box)
            room_surface = pygame.Surface(room_image.size)
            pixels = room_image.load()
            
            center_left = room_image.width // 2 - 30
            center_right = room_image.width // 2 + 30
            
            for y in range(room_image.height):
                for x in range(room_image.width):
                    r, g, b = pixels[x, y]
                    
                    # Grey pixels are walkable
                    if 165 <= r <= 175 and 165 <= g <= 175 and 165 <= b <= 175:
                        room_surface.set_at((x, y), (128, 128, 128))
                    # Block center passage without key
                    elif center_left <= x <= center_right:
                        room_surface.set_at((x, y), (0, 0, 0))
                    else:
                        room_surface.set_at((x, y), (0, 0, 0))
            
            mask = pygame.mask.from_threshold(room_surface, (0, 0, 0), (1,1,1,255))
            offset = (player_rect.left, player_rect.top)
            return mask.overlap(player_mask, offset) is not None
        
        room_mask = self.rooms_masks[row][col].copy()

        # Make letters walkable
        for letter_rect in teleport_manager.get_letter_rects_for_room(self.current_room):
            room_mask.erase(
                pygame.mask.Mask(letter_rect.size, fill=True),
                letter_rect.topleft
            )

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
    
    def add_key(self, color):
        """Add a key to the inventory"""
        if color in self.keys:
            self.keys[color] = True
    
    def has_key(self, color):
        """Check if player has a specific key"""
        return self.keys.get(color, False)
    
    def is_special_room(self):
        """Check if current room is a special key room"""
        col, row = self.current_room
        return self.rooms_special[row][col]
    
    def check_keys_at_player(self, player_rect, message_manager):
        key_messages = {
            'black': "Le passage nord mène à un ancien sanctuaire oublié.",
            'yellow': "Les murs dorés de cette salle cachent de nombreux secrets.",
            'white': "Cette chambre était utilisée par les anciens scribes pour protéger leurs trésors."
        }
        


        """Collect keys when player touches a pixel of key color"""
        col, row = self.current_room
        room_box = (
            col * ROOM_WIDTH,
            row * ROOM_HEIGHT,
            (col + 1) * ROOM_WIDTH,
            (row + 1) * ROOM_HEIGHT
        )
        room_image = self.map_image.crop(room_box)
        pixels = room_image.load()

        # Check each pixel under player rect
        for y in range(player_rect.height):
            for x in range(player_rect.width):
                px = player_rect.x % ROOM_WIDTH + x
                py = player_rect.y % ROOM_HEIGHT + y
                if px >= room_image.width or py >= room_image.height:
                    continue
                r, g, b = pixels[px, py]

                for key_name, color in self.key_colors.items():
                    if self.keys[key_name]:
                        continue  # already collected
                    if (r, g, b) == color:
                        self.keys[key_name] = True
                        message_manager.show_message(key_messages[key_name], 5000)
                        break
    
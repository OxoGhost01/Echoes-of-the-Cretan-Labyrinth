import pygame
from settings import ROOM_WIDTH, ROOM_HEIGHT


class TeleportManager:
    def __init__(self):
        self.zones = [
            {(0,0), (0,1), (1,0), (1,1)},
            {(1,4), (1,5), (2,5), (0,6), (1,6)},
            {(2,7), (2,8), (3,7), (3,8)},
            {(4,8), (4,9)},
        ]

        self.letter_size = (16, 16)

        #  All letters coords, hand written ; you can see them by using the cheat map
        self.letters = {
            (0, 0): [("A1", 5, 154), ("B1", 5, 89), ("C1", 5, 25), ("F1", 74, 4), ("E1", 233, 4)],
            (0, 1): [("D1", 5, 283), ("E2", 233, 368), ("F2", 74, 368)],
            (1, 0): [("D2", 622, 89)],
            (1, 1): [("A2", 622, 347), ("B2", 622, 283), ("C2", 622, 219)],

            (1, 4): [("J1", 324, 797), ("L1", 624, 797), ("K1", 324, 926), ("M1", 624, 926)],
            (1, 5): [("A1", 324, 1118), ("B1", 324, 1055), ("C1", 324, 990)],
            (2, 5): [("A2", 940, 1118), ("B2", 940, 1055), ("C2", 940, 990),
                    ("D1", 882, 968), ("E1", 850, 968), ("F1", 818, 968),
                    ("G1", 768, 968), ("H1", 736, 968), ("I1", 709, 968)],
            (0, 6): [("L2", 3, 1183), ("M2", 3, 1312),
                    ("D2", 242, 1334), ("E2", 211, 1334), ("F2", 179, 1334),
                    ("G2", 130, 1334), ("H2", 96, 1334), ("I2", 69, 1334)],
            (1, 6): [("J2", 624, 1185), ("K2", 624, 1310)],

            (2, 7): [("C1", 645, 1440), ("D1", 645, 1377)],
            (3, 7): [("C2", 1260, 1440), ("D2", 1260, 1377)],
            (2, 8): [("A1", 645, 1634), ("B1", 645, 1698)],
            (3, 8): [("A2", 1260, 1634), ("B2", 1260, 1698)],

            (4, 8): [("A1", 1284, 1570), ("B1", 1284, 1634), ("C1", 1284, 1700),
                    ("D2", 1583, 1570), ("E2", 1583, 1634), ("F2", 1583, 1700)],
            (4, 9): [("A2", 1583, 1763), ("B2", 1583, 1827), ("C2", 1583, 1891),
                    ("D1", 1284, 1763), ("E1", 1284, 1827), ("F1", 1284, 1891)]
        }

        self.cooldown_ms = 1000
        self.last_teleport_time = 0

    def get_zone_for_room(self, room):
        for zone in self.zones:
            if room in zone:
                return zone
        return None

    def check_teleport(self, player_rect, current_room):
        """Check if player is on a letter and teleport if so"""
        now = pygame.time.get_ticks()

        if now - self.last_teleport_time < self.cooldown_ms:
            return None

        if current_room not in self.letters:
            return None

        zone = self.get_zone_for_room(current_room)
        if not zone:
            return None

        room_col, room_row = current_room

        for label, gx, gy in self.letters[current_room]:
            lx = gx - room_col * ROOM_WIDTH
            ly = gy - room_row * ROOM_HEIGHT

            letter_rect = pygame.Rect(
                lx, ly,
                self.letter_size[0],
                self.letter_size[1]
            )

            if player_rect.colliderect(letter_rect):
                self.last_teleport_time = now
                return self._teleport_from(
                    source_room=current_room,
                    zone=zone,
                    source_label=label
                )

        return None


    def _teleport_from(self, source_room, zone, source_label):
        """ Teleport from source_label to target_label in zone """
        base = source_label[0]          # "A"
        target_suffix = "2" if source_label.endswith("1") else "1"
        target_label = base + target_suffix

        for room in zone:
            if room == source_room:
                continue  # skip current room to avoid self-teleport
            if room not in self.letters:
                continue

            for label, gx, gy in self.letters[room]:
                if label == target_label:
                    room_col, room_row = room
                    # Convert GLOBAL → ROOM-local
                    lx = gx - room_col * ROOM_WIDTH
                    ly = gy - room_row * ROOM_HEIGHT
                    # Small offset to avoid top-left overlap
                    return room, (lx + 2, ly + 2)

        # fallback: if not found, do not teleport
        return None

    
    def get_letter_rects_for_room(self, room):
        """  Returns a list of letter rects for a given room """
        rects = []
        if room not in self.letters:
            return rects

        room_col, room_row = room

        for _, gx, gy in self.letters[room]:
            lx = gx - room_col * ROOM_WIDTH
            ly = gy - room_row * ROOM_HEIGHT
            rects.append(pygame.Rect(lx, ly, *self.letter_size))

        return rects


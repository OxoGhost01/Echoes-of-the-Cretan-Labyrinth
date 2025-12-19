import random
import pygame

class TeleportManager:
    def __init__(self):
        self.zones = [
            {(0,0), (0,1), (1,0), (1,1)},
            {(1,4), (1,5), (2,5), (0,6), (1,6)},
            {(2,7), (2,8), (3,7), (3,8)},
            {(4,8), (4,9)},
        ]

        # Room -> list of letter positions (room-local coords)
        self.letter_size = (14,14)  # (width, height)
        self.letters = {
            (0, 0): [("A1", 5, 154), ("B1", 5, 89), ("C1", 5, 25), ("F1", 74, 4), ("E1", 233, 4)],
            (0, 1): [("D1", 5, 283), ("E2", 233, 368), ("F2", 74, 368)],
            (1, 0): [("D2", 622, 89)],
            (1, 1): [("A2",  622, 347), ("B2", 622, 283), ("C2", 622, 219)],

            (1, 4): [("J1", 324, 797), ("L1", 624, 797), ("K1", 324, 926), ("M1", 624, 926)],
            (1, 5): [("A1", 324, 1118), ("B1", 324, 1055), ("C1", 324, 990)],
            (2, 5): [("A2", 940, 1118), ("B2", 940, 1055), ("C2", 940, 990), ("D1", 882, 968), ("E1", 850, 968), ("F1", 818, 968), ("G1", 768, 968), ("H1", 736, 968), ("I1", 709, 968)],
            (0, 6): [("L2", 3, 1183), ("M2", 3, 1312), ("D2", 242, 1334), ("E2", 211, 1334), ("F2", 179, 1334), ("G2", 130, 1334), ("H2", 96, 1334), ("I2", 69, 1334)],
            (1, 6): [("J2", 624, 1185), ("K2", 624, 1310), ],

            (2, 7): [("C1", 645, 1440), ("D1", 645, 1377)],
            (3, 7): [("C2", 1260, 1440), ("D2", 1260, 1377)],
            (2, 8): [("A1", 645, 1634), ("B1", 645, 1698), ],
            (3, 8): [("A2", 1260, 1634), ("B2", 1260, 1698)],

            (4, 8): [("A1", 1284, 1570), ("B1", 1284, 1634), ("C1", 1284, 1700), ("D2", 1583, 1570), ("E2", 1583, 1634), ("F2", 1583, 1700)],
            (4, 9): [("A2", 1583, 1763), ("B2", 1583, 1827), ("C2", 1583, 1891), ("D1", 1284, 1763), ("E1", 1284, 1827), ("F1", 1284, 1891)]
        }

        self.trigger_radius = 12
        self.teleport_offset = 40

    def get_zone_for_room(self, room):
        for zone in self.zones:
            if room in zone:
                return zone
        return None

    def check_teleport(self, player_rect, current_room):
        """
        Returns (new_room, new_player_position) or None
        """
        if current_room not in self.letters:
            return None

        zone = self.get_zone_for_room(current_room)
        if not zone:
            return None

        # Check collision with any letter in the room
        for lx, ly in self.letters[current_room]:
            letter_rect = pygame.Rect(
                lx - self.trigger_radius,
                ly - self.trigger_radius,
                self.trigger_radius * 2,
                self.trigger_radius * 2
            )

            if player_rect.colliderect(letter_rect):
                return self._teleport_from(current_room, zone)

        return None

    def _teleport_from(self, source_room, zone):
        # Collect all possible destinations except source
        candidates = []

        for room in zone:
            if room == source_room:
                continue
            if room in self.letters:
                for pos in self.letters[room]:
                    candidates.append((room, pos))

        if not candidates:
            return None

        dest_room, (lx, ly) = random.choice(candidates)

        # Offset spawn position to avoid instant retrigger
        spawn_x = lx + self.teleport_offset
        spawn_y = ly

        return dest_room, (spawn_x, spawn_y)

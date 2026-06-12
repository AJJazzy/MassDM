"""
STICK REALM: SHADOW OPEN WORLD - Dungeon System
Handles dungeon generation, rooms, and boss encounters
"""

import pygame
import random
import math
from config import *


class DungeonRoom:
    """
    A single room in a dungeon.
    Can be normal, trap, puzzle, treasure, or boss room.
    """
    
    def __init__(self, room_type, width, height, dungeon):
        """
        Initialize a dungeon room.
        room_type: Type of room ('normal', 'trap', 'puzzle', 'treasure', 'boss')
        width, height: Room dimensions in tiles
        dungeon: Reference to the dungeon this room belongs to
        """
        self.type = room_type
        self.width = width
        self.height = height
        self.dungeon = dungeon
        
        # Position within dungeon
        self.x = 0
        self.y = 0
        
        # Connections to other rooms
        self.connections = {
            'north': None,
            'south': None,
            'east': None,
            'west': None
        }
        
        # Room contents
        self.enemies = []
        self.items = []
        self.traps = []
        self.doors = []
        
        # Room state
        self.visited = False
        self.completed = False
        self.locked = False
        
        # Generate room content based on type
        self._generate_content()
    
    def _generate_content(self):
        """Generate room content based on type."""
        if self.type == 'normal':
            self._generate_normal_room()
        elif self.type == 'trap':
            self._generate_trap_room()
        elif self.type == 'puzzle':
            self._generate_puzzle_room()
        elif self.type == 'treasure':
            self._generate_treasure_room()
        elif self.type == 'boss':
            self._generate_boss_room()
    
    def _generate_normal_room(self):
        """Generate a normal room with enemies and loot."""
        # Number of enemies based on dungeon depth
        depth = self.dungeon.depth if self.dungeon else 1
        num_enemies = random.randint(3, 6)
        
        for _ in range(num_enemies):
            enemy_type = random.choice(['grunt', 'archer', 'tank'])
            self.enemies.append({
                'type': enemy_type,
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2)
            })
        
        # Some loot
        if random.random() < 0.5:
            self.items.append({
                'type': 'coin',
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2),
                'amount': random.randint(10, 50)
            })
        
        if random.random() < 0.3:
            self.items.append({
                'type': random.choice(['health_potion', 'weapon_upgrade', 'armour_upgrade']),
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2)
            })
    
    def _generate_trap_room(self):
        """Generate a trap room with environmental hazards."""
        # Add traps
        num_traps = random.randint(2, 5)
        for _ in range(num_traps):
            trap_type = random.choice(['spike', 'arrow', 'falling_rock'])
            self.traps.append({
                'type': trap_type,
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2),
                'triggered': False
            })
        
        # Some enemies
        num_enemies = random.randint(1, 3)
        for _ in range(num_enemies):
            self.enemies.append({
                'type': random.choice(['grunt', 'archer']),
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2)
            })
    
    def _generate_puzzle_room(self):
        """Generate a puzzle room."""
        # Simple puzzle: step on plates to open door
        self.puzzle_type = random.choice(['pressure_plates', 'switches'])
        
        if self.puzzle_type == 'pressure_plates':
            # Add pressure plates
            num_plates = random.randint(2, 4)
            for i in range(num_plates):
                self.traps.append({
                    'type': 'pressure_plate',
                    'x': random.randint(1, self.width - 2),
                    'y': random.randint(1, self.height - 2),
                    'activated': False,
                    'index': i
                })
        
        # Lock the exit door
        self.locked = True
    
    def _generate_treasure_room(self):
        """Generate a treasure room with high-value loot."""
        # Rich loot
        self.items.append({
            'type': 'coin',
            'x': self.width // 2,
            'y': self.height // 2,
            'amount': random.randint(100, 300)
        })
        
        if random.random() < 0.7:
            self.items.append({
                'type': random.choice(['weapon_upgrade', 'armour_upgrade']),
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2)
            })
        
        # Guarded by enemies
        num_enemies = random.randint(2, 4)
        for _ in range(num_enemies):
            self.enemies.append({
                'type': random.choice(['tank', 'assassin', 'mage']),
                'x': random.randint(1, self.width - 2),
                'y': random.randint(1, self.height - 2)
            })
    
    def _generate_boss_room(self):
        """Generate a boss room."""
        # Boss enemy
        boss_type = self.dungeon.boss_type if self.dungeon else 'boss'
        self.enemies.append({
            'type': boss_type,
            'x': self.width // 2,
            'y': self.height // 2
        })
        
        # Lock the room
        self.locked = True
    
    def connect(self, direction, other_room):
        """Connect this room to another room in the specified direction."""
        if direction in self.connections:
            self.connections[direction] = other_room
            
            # Add door
            if direction == 'north':
                door_x = self.width // 2
                door_y = 0
            elif direction == 'south':
                door_x = self.width // 2
                door_y = self.height - 1
            elif direction == 'east':
                door_x = self.width - 1
                door_y = self.height // 2
            elif direction == 'west':
                door_x = 0
                door_y = self.height // 2
            
            self.doors.append({
                'x': door_x,
                'y': door_y,
                'direction': direction,
                'locked': self.locked
            })
    
    def render(self, surface, camera, tile_size=TILE_SIZE):
        """
        Render the room.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        tile_size: Size of each tile in pixels
        """
        # Calculate screen position
        cam_x, cam_y = camera.get_offset()
        screen_x = int(self.x * tile_size - cam_x)
        screen_y = int(self.y * tile_size - cam_y)
        
        # Don't render if off-screen
        if (screen_x + self.width * tile_size < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height * tile_size < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # Draw room background
        room_color = GRAY_30
        pygame.draw.rect(surface, room_color,
                        (screen_x, screen_y, self.width * tile_size, self.height * tile_size), 0)
        
        # Draw room outline
        pygame.draw.rect(surface, GRAY_50,
                        (screen_x, screen_y, self.width * tile_size, self.height * tile_size), 2)
        
        # Draw doors
        for door in self.doors:
            door_x = screen_x + door['x'] * tile_size
            door_y = screen_y + door['y'] * tile_size
            
            if door['direction'] in ['north', 'south']:
                # Horizontal door
                door_width = tile_size // 2
                door_height = tile_size // 4
                pygame.draw.rect(surface, GRAY_70,
                                (door_x - door_width // 2, door_y, door_width, door_height), 0)
            else:
                # Vertical door
                door_width = tile_size // 4
                door_height = tile_size // 2
                pygame.draw.rect(surface, GRAY_70,
                                (door_x, door_y - door_height // 2, door_width, door_height), 0)
        
        # Draw traps
        for trap in self.traps:
            self._draw_trap(surface, trap, screen_x, screen_y, tile_size)
        
        # Draw items
        for item in self.items:
            self._draw_item(surface, item, screen_x, screen_y, tile_size)
    
    def _draw_trap(self, surface, trap, screen_x, screen_y, tile_size):
        """Draw a trap."""
        trap_x = screen_x + trap['x'] * tile_size
        trap_y = screen_y + trap['y'] * tile_size
        
        if trap['type'] == 'spike':
            # Draw spikes
            pygame.draw.polygon(surface, GRAY_70, [
                (trap_x, trap_y + tile_size),
                (trap_x + tile_size // 2, trap_y),
                (trap_x + tile_size, trap_y + tile_size)
            ], 0)
        elif trap['type'] == 'arrow':
            # Draw arrow trap
            pygame.draw.line(surface, GRAY_70, 
                            (trap_x, trap_y + tile_size // 2),
                            (trap_x + tile_size, trap_y + tile_size // 2), 2)
            pygame.draw.polygon(surface, GRAY_70, [
                (trap_x + tile_size, trap_y + tile_size // 2),
                (trap_x + tile_size - 5, trap_y + tile_size // 2 - 3),
                (trap_x + tile_size - 5, trap_y + tile_size // 2 + 3)
            ], 0)
        elif trap['type'] == 'falling_rock':
            # Draw rock
            pygame.draw.circle(surface, GRAY_50, 
                              (trap_x + tile_size // 2, trap_y + tile_size // 2), 
                              tile_size // 3, 0)
        elif trap['type'] == 'pressure_plate':
            # Draw pressure plate
            if trap.get('activated', False):
                color = GREEN
            else:
                color = GRAY_60
            pygame.draw.rect(surface, color,
                            (trap_x + tile_size // 4, trap_y + tile_size // 4,
                             tile_size // 2, tile_size // 2), 0)
    
    def _draw_item(self, surface, item, screen_x, screen_y, tile_size):
        """Draw an item in the room."""
        item_x = screen_x + item['x'] * tile_size
        item_y = screen_y + item['y'] * tile_size
        
        if item['type'] == 'coin':
            # Draw coin
            pygame.draw.circle(surface, YELLOW,
                              (item_x + tile_size // 2, item_y + tile_size // 2),
                              tile_size // 4, 0)
            if item.get('amount', 1) > 1:
                font = pygame.font.SysFont('Arial', 12)
                text = font.render(str(item['amount']), True, BLACK)
                surface.blit(text, (item_x + tile_size // 2 - text.get_width() // 2,
                                    item_y + tile_size // 2 - text.get_height() // 2))
        elif item['type'] == 'health_potion':
            # Draw health potion
            pygame.draw.rect(surface, RED,
                            (item_x + tile_size // 4, item_y + tile_size // 4,
                             tile_size // 2, tile_size // 2), 0, border_radius=3)
        elif item['type'] == 'weapon_upgrade':
            # Draw weapon upgrade
            pygame.draw.rect(surface, GRAY_70,
                            (item_x + tile_size // 4, item_y + tile_size // 4,
                             tile_size // 2, tile_size // 2), 0, border_radius=2)
        elif item['type'] == 'armour_upgrade':
            # Draw armour upgrade
            pygame.draw.rect(surface, GRAY_60,
                            (item_x + tile_size // 4, item_y + tile_size // 4,
                             tile_size // 2, tile_size // 2), 0, border_radius=2)


class Dungeon:
    """
    A dungeon with multiple connected rooms.
    """
    
    def __init__(self, dungeon_type, depth, game):
        """
        Initialize a dungeon.
        dungeon_type: Type of dungeon ('cave_dungeon', 'ruins_dungeon', etc.)
        depth: Number of rooms in the dungeon
        game: Reference to the main game instance
        """
        self.type = dungeon_type
        self.config = DUNGEONS.get(dungeon_type, DUNGEONS['cave_dungeon'])
        self.depth = depth
        self.game = game
        
        # Boss type
        self.boss_type = self.config.get('boss', 'boss')
        
        # Rooms
        self.rooms = []
        self.room_grid = []  # 2D grid of rooms for layout
        
        # Dungeon entrance
        self.entrance_x = 0
        self.entrance_y = 0
        
        # Dungeon exit
        self.exit_x = 0
        self.exit_y = 0
        
        # Generate dungeon layout
        self._generate_layout()
        
        # Dungeon state
        self.completed = False
        self.boss_defeated = False
    
    def _generate_layout(self):
        """Generate the dungeon layout with connected rooms."""
        # Create a path of rooms
        self.rooms = []
        
        # Room dimensions
        room_width = 10
        room_height = 8
        
        # Create rooms in a path
        for i in range(self.depth):
            # Determine room type
            if i == self.depth - 1:
                room_type = 'boss'
            elif i == self.depth - 2:
                room_type = 'treasure'
            elif i % 3 == 0:
                room_type = random.choice(['trap', 'puzzle'])
            else:
                room_type = 'normal'
            
            room = DungeonRoom(room_type, room_width, room_height, self)
            room.x = i * room_width * 2  # Spaced out
            room.y = 0
            self.rooms.append(room)
            
            # Connect to previous room
            if i > 0:
                prev_room = self.rooms[i - 1]
                prev_room.connect('east', room)
                room.connect('west', prev_room)
        
        # Set entrance at first room
        if self.rooms:
            self.entrance_x = self.rooms[0].x * TILE_SIZE + self.rooms[0].width * TILE_SIZE // 2
            self.entrance_y = self.rooms[0].y * TILE_SIZE + self.rooms[0].height * TILE_SIZE // 2
        
        # Set exit at last room
        if self.rooms:
            self.exit_x = self.rooms[-1].x * TILE_SIZE + self.rooms[-1].width * TILE_SIZE // 2
            self.exit_y = self.rooms[-1].y * TILE_SIZE + self.rooms[-1].height * TILE_SIZE // 2
    
    def update(self, dt):
        """
        Update dungeon state.
        dt: Time since last frame in seconds
        """
        # Check if boss is defeated
        if not self.boss_defeated and self._is_boss_defeated():
            self.boss_defeated = True
            self.completed = True
            
            # Unlock exit
            if self.rooms:
                self.rooms[-1].locked = False
    
    def _is_boss_defeated(self):
        """Check if the boss has been defeated."""
        # In a full implementation, this would check the boss entity
        return False
    
    def render(self, surface, camera):
        """
        Render the dungeon.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        # Render all rooms
        for room in self.rooms:
            room.render(surface, camera)
    
    def get_room_at(self, world_x, world_y):
        """Get the room at the specified world coordinates."""
        for room in self.rooms:
            room_x = room.x * TILE_SIZE
            room_y = room.y * TILE_SIZE
            if (world_x >= room_x and world_x < room_x + room.width * TILE_SIZE and
                world_y >= room_y and world_y < room_y + room.height * TILE_SIZE):
                return room
        return None
    
    def get_entrance_position(self):
        """Get the entrance position."""
        return (self.entrance_x, self.entrance_y)
    
    def get_exit_position(self):
        """Get the exit position."""
        return (self.exit_x, self.exit_y)
    
    def is_completed(self):
        """Check if the dungeon is completed."""
        return self.completed
    
    def check_ground_collision(self, entity):
        """Check if entity is on the ground (for dungeon brawler physics)."""
        # In dungeon brawler mode, ground is at floor_y
        # For now, use a simple floor at the bottom of the dungeon
        # This will be enhanced with proper platform detection
        entity_bottom = entity.y + entity.height
        return entity_bottom >= self.floor_y
    
    def create_attack_effect(self, x, y, direction, combo_count):
        """Create a visual effect for an attack."""
        # This would create particles or visual effects
        # For now, just a placeholder
        pass
    
    @property
    def floor_y(self):
        """Get the floor Y position for dungeon brawler mode."""
        # Return a reasonable floor position
        # In a full implementation, this would be based on the dungeon layout
        return SCREEN_HEIGHT - 100
    
    @property
    def boss_x(self):
        """Get the boss X position."""
        if self.rooms:
            boss_room = self.rooms[-1]  # Last room is boss room
            return boss_room.x * TILE_SIZE + boss_room.width * TILE_SIZE // 2
        return self.entrance_x + 200
    
    @property
    def boss_y(self):
        """Get the boss Y position."""
        if self.rooms:
            boss_room = self.rooms[-1]
            return boss_room.y * TILE_SIZE + boss_room.height * TILE_SIZE // 2
        return self.entrance_y
    
    @property
    def walls(self):
        """Get dungeon walls for collision."""
        walls = []
        for room in self.rooms:
            # Add room boundaries as walls
            room_x = room.x * TILE_SIZE
            room_y = room.y * TILE_SIZE
            walls.append({
                'x': room_x,
                'y': room_y,
                'width': room.width * TILE_SIZE,
                'height': room.height * TILE_SIZE
            })
        return walls
    
    @property
    def enemies(self):
        """Get dungeon enemies for brawler mode."""
        enemies = []
        for room in self.rooms:
            for enemy_data in room.enemies:
                enemies.append({
                    'x': room.x * TILE_SIZE + enemy_data['x'] * TILE_SIZE,
                    'y': room.y * TILE_SIZE + enemy_data['y'] * TILE_SIZE,
                    'type': enemy_data['type']
                })
        return enemies


# Dungeon type mapping
DUNGEON_CLASS_MAP = {
    'cave_dungeon': Dungeon,
    'ruins_dungeon': Dungeon,
    'castle_dungeon': Dungeon,
    'shadow_temple': Dungeon
}


def create_dungeon(dungeon_type, depth, game):
    """Factory function to create a dungeon of the specified type."""
    dungeon_class = DUNGEON_CLASS_MAP.get(dungeon_type, Dungeon)
    return dungeon_class(dungeon_type, depth, game)

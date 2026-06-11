"""
STICK REALM: SHADOW OPEN WORLD - Chunk System
Handles chunk-based world loading and unloading
"""

import pygame
import random
from config import *


class Chunk:
    """
    A chunk of the world - 16x16 tiles that can be loaded/unloaded dynamically.
    Each chunk contains terrain, trees, rocks, and other features.
    """
    
    def __init__(self, chunk_x, chunk_y, biome_type=None):
        """
        Initialize a chunk at grid position (chunk_x, chunk_y).
        chunk_x, chunk_y: Chunk coordinates in the chunk grid
        biome_type: Biome type for this chunk (optional)
        """
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        
        # Calculate world position
        self.x = chunk_x * CHUNK_SIZE * TILE_SIZE
        self.y = chunk_y * CHUNK_SIZE * TILE_SIZE
        self.width = CHUNK_SIZE * TILE_SIZE
        self.height = CHUNK_SIZE * TILE_SIZE
        
        # Biome
        if biome_type:
            self.biome_type = biome_type
        else:
            # Default to forest
            self.biome_type = 'forest'
        
        # Terrain data
        self.tiles = []  # 2D array of tile types
        self.features = []  # List of features (trees, rocks, etc.)
        
        # Generate chunk content
        self._generate_terrain()
        self._generate_features()
        
        # Rendering
        self.surface = None
        self.dirty = True  # Needs to be re-rendered
        
        # Entities in this chunk
        self.entities = []
    
    def _generate_terrain(self):
        """Generate terrain tiles for this chunk."""
        self.tiles = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        
        # Get biome config
        biome_config = BIOMES.get(self.biome_type, BIOMES['forest'])
        base_color = biome_config['color']
        
        # Generate base terrain with some noise
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                # Base tile type
                tile_type = 'grass'
                
                # Add some variation based on biome
                if self.biome_type == 'forest':
                    # Forest has grass with some dirt paths
                    if random.random() < 0.1:
                        tile_type = 'dirt'
                elif self.biome_type == 'village':
                    # Village has more dirt/stone
                    if random.random() < 0.3:
                        tile_type = 'dirt'
                    elif random.random() < 0.1:
                        tile_type = 'stone'
                elif self.biome_type == 'cave':
                    # Cave has stone floor
                    tile_type = 'stone'
                elif self.biome_type == 'castle':
                    # Castle has stone
                    tile_type = 'stone'
                elif self.biome_type == 'shadow_realm':
                    # Shadow realm has dark terrain
                    tile_type = 'shadow'
                elif self.biome_type == 'dungeon':
                    # Dungeon has stone
                    tile_type = 'stone'
                elif self.biome_type == 'desert':
                    # Desert has sand
                    tile_type = 'sand'
                elif self.biome_type == 'ice_wastes':
                    # Ice wastes has ice
                    tile_type = 'ice'
                
                # Add some random variation
                if random.random() < 0.05:
                    # Slightly different shade
                    tile_type = f"{tile_type}_dark" if random.random() < 0.5 else f"{tile_type}_light"
                
                self.tiles[x][y] = {
                    'type': tile_type,
                    'color': self._get_tile_color(tile_type, base_color)
                }
    
    def _get_tile_color(self, tile_type, base_color):
        """Get the color for a specific tile type."""
        # Base color with some variation
        r, g, b = base_color
        
        # Add noise
        noise = random.randint(-20, 20)
        r = clamp(r + noise, 0, 255)
        g = clamp(g + noise, 0, 255)
        b = clamp(b + noise, 0, 255)
        
        return (r, g, b)
    
    def _generate_features(self):
        """Generate trees, rocks, and other features for this chunk."""
        self.features = []
        
        # Get biome config
        biome_config = BIOMES.get(self.biome_type, BIOMES['forest'])
        
        # Trees (for forest biome)
        if self.biome_type == 'forest':
            tree_density = biome_config.get('tree_density', 0.3)
            num_trees = random.randint(0, int(CHUNK_SIZE * CHUNK_SIZE * tree_density))
            for _ in range(num_trees):
                tree_x = random.randint(0, CHUNK_SIZE - 1)
                tree_y = random.randint(0, CHUNK_SIZE - 1)
                self.features.append({
                    'type': 'tree',
                    'x': tree_x,
                    'y': tree_y,
                    'size': random.randint(20, 40)
                })
        
        # Buildings (for village biome)
        if self.biome_type == 'village':
            building_density = biome_config.get('building_density', 0.4)
            num_buildings = random.randint(0, int(CHUNK_SIZE * CHUNK_SIZE * building_density / 100))
            for _ in range(num_buildings):
                building_x = random.randint(0, CHUNK_SIZE - 1)
                building_y = random.randint(0, CHUNK_SIZE - 1)
                self.features.append({
                    'type': 'building',
                    'x': building_x,
                    'y': building_y,
                    'width': random.randint(40, 80),
                    'height': random.randint(40, 80)
                })
        
        # Rocks (for cave biome)
        if self.biome_type == 'cave':
            rock_density = biome_config.get('rock_density', 0.5)
            num_rocks = random.randint(0, int(CHUNK_SIZE * CHUNK_SIZE * rock_density))
            for _ in range(num_rocks):
                rock_x = random.randint(0, CHUNK_SIZE - 1)
                rock_y = random.randint(0, CHUNK_SIZE - 1)
                self.features.append({
                    'type': 'rock',
                    'x': rock_x,
                    'y': rock_y,
                    'size': random.randint(15, 30)
                })
        
        # Cacti (for desert biome)
        if self.biome_type == 'desert':
            cacti_density = biome_config.get('cacti_density', 0.05)
            num_cacti = random.randint(0, int(CHUNK_SIZE * CHUNK_SIZE * cacti_density))
            for _ in range(num_cacti):
                cactus_x = random.randint(0, CHUNK_SIZE - 1)
                cactus_y = random.randint(0, CHUNK_SIZE - 1)
                self.features.append({
                    'type': 'cactus',
                    'x': cactus_x,
                    'y': cactus_y,
                    'size': random.randint(10, 20)
                })
    
    def render(self, surface, camera):
        """
        Render the chunk.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        # Get camera offset
        cam_x, cam_y = camera.get_offset()
        
        # Calculate screen position
        screen_x = int(self.x - cam_x)
        screen_y = int(self.y - cam_y)
        
        # Don't render if completely off-screen
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # Get biome color
        biome_config = BIOMES.get(self.biome_type, BIOMES['forest'])
        biome_color = biome_config['color']
        
        # Draw tiles
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                tile = self.tiles[x][y]
                if tile:
                    # Calculate screen position for this tile
                    tile_screen_x = screen_x + x * TILE_SIZE
                    tile_screen_y = screen_y + y * TILE_SIZE
                    
                    # Only draw if visible
                    if (tile_screen_x + TILE_SIZE >= 0 and tile_screen_x <= SCREEN_WIDTH and
                        tile_screen_y + TILE_SIZE >= 0 and tile_screen_y <= SCREEN_HEIGHT):
                        
                        # Draw tile
                        pygame.draw.rect(surface, tile['color'],
                                        (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE), 0)
                        
                        # Draw tile outline (subtle)
                        outline_color = self._darken_color(tile['color'], 30)
                        pygame.draw.rect(surface, outline_color,
                                       (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE), 1)
        
        # Draw features
        for feature in self.features:
            self._draw_feature(surface, feature, screen_x, screen_y, biome_color)
    
    def _draw_feature(self, surface, feature, screen_x, screen_y, biome_color):
        """Draw a feature (tree, rock, building, etc.)."""
        feature_type = feature['type']
        fx = feature['x'] * TILE_SIZE
        fy = feature['y'] * TILE_SIZE
        
        # Calculate screen position
        feature_screen_x = screen_x + fx
        feature_screen_y = screen_y + fy
        
        # Don't draw if off-screen
        if (feature_screen_x + 100 < 0 or feature_screen_x > SCREEN_WIDTH or
            feature_screen_y + 100 < 0 or feature_screen_y > SCREEN_HEIGHT):
            return
        
        if feature_type == 'tree':
            self._draw_tree(surface, feature_screen_x, feature_screen_y, feature['size'])
        elif feature_type == 'building':
            self._draw_building(surface, feature_screen_x, feature_screen_y, 
                                feature['width'], feature['height'])
        elif feature_type == 'rock':
            self._draw_rock(surface, feature_screen_x, feature_screen_y, feature['size'])
        elif feature_type == 'cactus':
            self._draw_cactus(surface, feature_screen_x, feature_screen_y, feature['size'])
    
    def _draw_tree(self, surface, x, y, size):
        """Draw a tree."""
        # Trunk
        trunk_height = size
        trunk_width = size // 4
        pygame.draw.rect(surface, GRAY_40, (x + trunk_width, y - trunk_height, trunk_width * 2, trunk_height), 0)
        
        # Canopy (circle)
        canopy_radius = size // 2
        pygame.draw.circle(surface, GRAY_50, (x + size // 2, y - trunk_height - canopy_radius // 2), canopy_radius, 0)
        
        # Canopy outline
        pygame.draw.circle(surface, GRAY_30, (x + size // 2, y - trunk_height - canopy_radius // 2), canopy_radius, 1)
    
    def _draw_building(self, surface, x, y, width, height):
        """Draw a building."""
        # Walls
        pygame.draw.rect(surface, GRAY_50, (x, y - height, width, height), 0)
        
        # Roof
        roof_height = height // 4
        pygame.draw.polygon(surface, GRAY_40, [
            (x, y - height),
            (x + width // 2, y - height - roof_height),
            (x + width, y - height)
        ], 0)
        
        # Door
        door_width = width // 5
        door_height = height // 3
        pygame.draw.rect(surface, GRAY_30, (x + width // 2 - door_width // 2, y - door_height, door_width, door_height), 0)
        
        # Windows
        window_size = width // 6
        pygame.draw.rect(surface, GRAY_70, (x + width // 4, y - height // 2, window_size, window_size), 0)
        pygame.draw.rect(surface, GRAY_70, (x + width - width // 4 - window_size, y - height // 2, window_size, window_size), 0)
    
    def _draw_rock(self, surface, x, y, size):
        """Draw a rock."""
        # Simple irregular shape
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            radius = size // 2 + random.randint(-5, 5)
            px = x + size // 2 + int(math.cos(angle) * radius)
            py = y - size // 2 + int(math.sin(angle) * radius)
            points.append((px, py))
        
        pygame.draw.polygon(surface, GRAY_40, points, 0)
        pygame.draw.polygon(surface, GRAY_30, points, 1)
    
    def _draw_cactus(self, surface, x, y, size):
        """Draw a cactus."""
        # Main body
        pygame.draw.rect(surface, GRAY_60, (x, y - size, size // 2, size), 0)
        
        # Arms
        arm_width = size // 4
        arm_height = size // 3
        pygame.draw.rect(surface, GRAY_60, (x - arm_width, y - size + size // 4, arm_width * 2, arm_height), 0)
        pygame.draw.rect(surface, GRAY_60, (x - arm_width // 2, y - size + size // 2, arm_width * 2, arm_height), 0)
        
        # Outline
        pygame.draw.rect(surface, GRAY_40, (x, y - size, size // 2, size), 1)
    
    def _darken_color(self, color, amount):
        """Darken a color by the specified amount."""
        r, g, b = color
        r = clamp(r - amount, 0, 255)
        g = clamp(g - amount, 0, 255)
        b = clamp(b - amount, 0, 255)
        return (r, g, b)
    
    def get_biome_type(self):
        """Get the biome type for this chunk."""
        return self.biome_type
    
    def set_biome_type(self, biome_type):
        """Set the biome type for this chunk and regenerate."""
        self.biome_type = biome_type
        self._generate_terrain()
        self._generate_features()
        self.dirty = True
    
    def get_center(self):
        """Get the center position of the chunk in world coordinates."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def contains_point(self, world_x, world_y):
        """Check if a world point is within this chunk."""
        return (world_x >= self.x and world_x < self.x + self.width and
                world_y >= self.y and world_y < self.y + self.height)
    
    def get_tile_at(self, world_x, world_y):
        """Get the tile at the specified world coordinates."""
        # Convert to chunk-local coordinates
        local_x = int((world_x - self.x) / TILE_SIZE)
        local_y = int((world_y - self.y) / TILE_SIZE)
        
        # Check bounds
        if local_x < 0 or local_x >= CHUNK_SIZE or local_y < 0 or local_y >= CHUNK_SIZE:
            return None
        
        return self.tiles[local_x][local_y]
    
    def is_loaded(self):
        """Check if this chunk is currently loaded."""
        # In a full implementation, this would check against the game's loaded chunks
        return True

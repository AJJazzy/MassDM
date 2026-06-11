"""
STICK REALM: SHADOW OPEN WORLD - World System
Main world class that manages chunks, entities, and world state
"""

import pygame
import random
import math
from config import *
from .chunk import Chunk
from .biome import Biome, generate_biome_map, get_biome_at
from .camera import Camera
from .dungeon import Dungeon, create_dungeon
from game.entities.enemy import create_enemy
from game.entities.items import create_item
from game.entities.projectile import create_projectile


class World:
    """
    The main game world - manages chunks, entities, biomes, and world state.
    Supports infinite world generation with chunk-based loading.
    """
    
    def __init__(self, game):
        """
        Initialize the world.
        game: Reference to the main game instance
        """
        self.game = game
        
        # World dimensions
        self.width = WORLD_WIDTH_PIXELS
        self.height = WORLD_HEIGHT_PIXELS
        
        # Chunks
        self.chunks = {}  # Dictionary: (chunk_x, chunk_y) -> Chunk
        self.loaded_chunks = set()  # Set of loaded chunk coordinates
        
        # Biome map
        self.biome_map = None
        self.biome_seed = random.randint(0, 1000000)
        
        # Entities
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.players = []  # For multiplayer
        
        # Dungeons
        self.dungeons = []
        self.active_dungeon = None
        self.dungeon_entrances = []
        self.boss_positions = []
        
        # Spawning
        self.spawn_timer = 0
        self.spawn_interval = 0.5  # seconds between spawn checks
        
        # Time
        self.time = 0  # World time in seconds
        self.day_length = 600  # 10 minutes per day
        
        # Weather
        self.weather = 'clear'
        self.weather_timer = 0
        self.weather_duration = 300  # 5 minutes per weather
        
        # Player reference (set when player is added)
        self.player = None
    
    def add_entity(self, entity):
        """Add an entity to the world."""
        if hasattr(entity, 'type'):
            if entity.type == 'player':
                self.player = entity
                self.players.append(entity)
            elif entity.type in ['grunt', 'archer', 'tank', 'assassin', 'mage', 'boss']:
                self.enemies.append(entity)
            elif entity.type in ['coin', 'health_potion', 'weapon_upgrade', 'armour_upgrade']:
                self.items.append(entity)
            elif entity.type in ['arrow', 'fireball', 'shockwave']:
                self.projectiles.append(entity)
        
        # Initialize biome map
        self._init_biome_map()
        
        # Camera (will be set by main game)
        self.camera = None
        
        # World state
        self.paused = False
        self.game_over = False
        self.victory = False
    
    def _init_biome_map(self):
        """Initialize the biome map for the world."""
        # Calculate number of biome cells
        biome_width = int(WORLD_WIDTH_TILES / (CHUNK_SIZE * 4))  # 4 chunks per biome cell
        biome_height = int(WORLD_HEIGHT_TILES / (CHUNK_SIZE * 4))
        
        self.biome_map = generate_biome_map(biome_width, biome_height, self.biome_seed)
    
    def update(self, dt):
        """
        Update the world state.
        dt: Time since last frame in seconds
        """
        if self.paused:
            return
        
        # Update time
        self.time += dt
        
        # Update weather
        self._update_weather(dt)
        
        # Update camera
        self.camera.update(dt)
        
        # Load/unload chunks based on player position
        self._update_chunks()
        
        # Update entities
        self._update_entities(dt)
        
        # Check for spawning
        self._check_spawning(dt)
        
        # Update dungeons
        self._update_dungeons(dt)
        
        # Clean up dead entities
        self._cleanup_entities()
    
    def _update_weather(self, dt):
        """Update weather state."""
        self.weather_timer += dt
        
        if self.weather_timer >= self.weather_duration:
            self.weather_timer = 0
            self.weather_duration = random.randint(300, 600)  # 5-10 minutes
            
            # Change weather
            weather_types = ['clear', 'rain', 'fog', 'wind']
            self.weather = random.choice(weather_types)
    
    def _update_chunks(self):
        """Load and unload chunks based on player position."""
        if not hasattr(self.game, 'player'):
            return
        
        player = self.game.player
        player_chunk_x = int(player.x / (CHUNK_SIZE * TILE_SIZE))
        player_chunk_y = int(player.y / (CHUNK_SIZE * TILE_SIZE))
        
        # Load chunks in a radius around the player
        for dx in range(-CHUNK_LOAD_DISTANCE, CHUNK_LOAD_DISTANCE + 1):
            for dy in range(-CHUNK_LOAD_DISTANCE, CHUNK_LOAD_DISTANCE + 1):
                chunk_x = player_chunk_x + dx
                chunk_y = player_chunk_y + dy
                
                # Check if chunk should be loaded
                if self._should_load_chunk(chunk_x, chunk_y):
                    self._load_chunk(chunk_x, chunk_y)
        
        # Unload chunks that are too far away
        chunks_to_unload = []
        for (chunk_x, chunk_y) in self.loaded_chunks:
            if not self._should_load_chunk(chunk_x, chunk_y):
                chunks_to_unload.append((chunk_x, chunk_y))
        
        for chunk_coords in chunks_to_unload:
            self._unload_chunk(*chunk_coords)
    
    def _should_load_chunk(self, chunk_x, chunk_y):
        """Check if a chunk should be loaded."""
        if not hasattr(self.game, 'player'):
            return False
        
        player = self.game.player
        player_chunk_x = int(player.x / (CHUNK_SIZE * TILE_SIZE))
        player_chunk_y = int(player.y / (CHUNK_SIZE * TILE_SIZE))
        
        dx = abs(chunk_x - player_chunk_x)
        dy = abs(chunk_y - player_chunk_y)
        
        return dx <= CHUNK_LOAD_DISTANCE and dy <= CHUNK_LOAD_DISTANCE
    
    def _load_chunk(self, chunk_x, chunk_y):
        """Load a chunk."""
        if (chunk_x, chunk_y) in self.chunks:
            return
        
        # Determine biome for this chunk
        biome_type = get_biome_at(
            chunk_x * CHUNK_SIZE * TILE_SIZE,
            chunk_y * CHUNK_SIZE * TILE_SIZE,
            self.biome_map,
            chunks_per_biome=4
        )
        
        # Create chunk
        chunk = Chunk(chunk_x, chunk_y, biome_type)
        self.chunks[(chunk_x, chunk_y)] = chunk
        self.loaded_chunks.add((chunk_x, chunk_y))
    
    def _unload_chunk(self, chunk_x, chunk_y):
        """Unload a chunk."""
        if (chunk_x, chunk_y) not in self.chunks:
            return
        
        # Remove chunk
        del self.chunks[(chunk_x, chunk_y)]
        self.loaded_chunks.discard((chunk_x, chunk_y))
    
    def _update_entities(self, dt):
        """Update all entities in the world."""
        # Update enemies
        for enemy in self.enemies[:]:
            if self.player:
                if not enemy.update(dt, self.player):
                    # Enemy returned False - remove it
                    self.enemies.remove(enemy)
        
        # Update items
        for item in self.items[:]:
            item.update(dt)
            # Items remove themselves when collected
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            if not projectile.update(dt):
                self.projectiles.remove(projectile)
    
    def _check_spawning(self, dt):
        """Check if new enemies should be spawned."""
        if not hasattr(self.game, 'player'):
            return
        
        self.spawn_timer += dt
        if self.spawn_timer < self.spawn_interval:
            return
        
        self.spawn_timer = 0
        
        # Check if we need more enemies
        if len(self.enemies) >= MAX_ENEMIES_ON_SCREEN:
            return
        
        # Get player position
        player = self.player
        player_x, player_y = player.get_center()
        
        # Get visible area
        visible_rect = self.camera.get_visible_rect()
        
        # Spawn enemies in visible area
        for _ in range(random.randint(0, 2)):  # Spawn 0-2 enemies per check
            if len(self.enemies) >= MAX_ENEMIES_ON_SCREEN:
                break
            
            # Random position in visible area
            spawn_x = random.randint(int(visible_rect.x), int(visible_rect.x + visible_rect.width))
            spawn_y = random.randint(int(visible_rect.y), int(visible_rect.y + visible_rect.height))
            
            # Check distance from player
            distance = distance(spawn_x, spawn_y, player_x, player_y)
            if distance < SPAWN_DISTANCE:
                continue
            
            # Get biome at spawn position
            biome_type = get_biome_at(spawn_x, spawn_y, self.biome_map, chunks_per_biome=4)
            biome = Biome(biome_type)
            
            # Get random enemy type for this biome
            enemy_type = biome.get_random_enemy_type()
            
            # Create enemy
            enemy = create_enemy(spawn_x, spawn_y, enemy_type, self.game)
            self.enemies.append(enemy)
    
    def _update_dungeons(self, dt):
        """Update active dungeon."""
        if self.active_dungeon:
            self.active_dungeon.update(dt)
    
    def _cleanup_entities(self):
        """Clean up dead entities."""
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.health > 0]
        
        # Remove collected items
        self.items = [i for i in self.items if not i.collected or i.x >= 0]
    
    def render(self, surface):
        """
        Render the world.
        surface: Pygame surface to draw on
        """
        # Render chunks
        for chunk in self.chunks.values():
            chunk.render(surface, self.camera)
        
        # Render dungeon if active
        if self.active_dungeon:
            self.active_dungeon.render(surface, self.camera)
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(surface, self.camera)
        
        # Render items
        for item in self.items:
            item.render(surface, self.camera)
        
        # Render enemies
        for enemy in self.enemies:
            enemy.render(surface, self.camera)
        
        # Render player (handled separately by game)
    
    def add_enemy(self, enemy_type, x, y):
        """Add an enemy to the world."""
        enemy = create_enemy(x, y, enemy_type, self.game)
        self.enemies.append(enemy)
        return enemy
    
    def add_item(self, item_type, x, y, amount=1):
        """Add an item to the world."""
        item = create_item(item_type, x, y, self.game, amount)
        self.items.append(item)
        return item
    
    def add_projectile(self, projectile_type, x, y, vx, vy, owner):
        """Add a projectile to the world."""
        projectile = create_projectile(projectile_type, x, y, vx, vy, owner, self.game)
        self.projectiles.append(projectile)
        return projectile
    
    def create_dungeon(self, dungeon_type, x, y):
        """Create a dungeon at the specified position."""
        dungeon_config = DUNGEONS.get(dungeon_type, DUNGEONS['cave_dungeon'])
        dungeon = create_dungeon(dungeon_type, dungeon_config['depth'], self.game)
        
        # Position dungeon entrance
        dungeon.entrance_x = x
        dungeon.entrance_y = y
        
        self.dungeons.append(dungeon)
        return dungeon
    
    def enter_dungeon(self, dungeon_index):
        """Enter a dungeon."""
        if dungeon_index < len(self.dungeons):
            self.active_dungeon = self.dungeons[dungeon_index]
            
            # Teleport player to dungeon entrance
            if hasattr(self.game, 'player'):
                entrance_x, entrance_y = self.active_dungeon.get_entrance_position()
                self.game.player.x = entrance_x - self.game.player.width // 2
                self.game.player.y = entrance_y - self.game.player.height // 2
            
            return True
        return False
    
    def exit_dungeon(self):
        """Exit the current dungeon."""
        if self.active_dungeon:
            # Teleport player to dungeon exit (which is in the overworld)
            if hasattr(self.game, 'player'):
                exit_x, exit_y = self.active_dungeon.get_exit_position()
                self.game.player.x = exit_x - self.game.player.width // 2
                self.game.player.y = exit_y - self.game.player.height // 2
            
            self.active_dungeon = None
            return True
        return False
    
    def get_biome_at(self, world_x, world_y):
        """Get the biome at the specified world coordinates."""
        return get_biome_at(world_x, world_y, self.biome_map, chunks_per_biome=4)
    
    def get_chunk_at(self, world_x, world_y):
        """Get the chunk at the specified world coordinates."""
        chunk_x = int(world_x / (CHUNK_SIZE * TILE_SIZE))
        chunk_y = int(world_y / (CHUNK_SIZE * TILE_SIZE))
        return self.chunks.get((chunk_x, chunk_y))
    
    def get_tile_at(self, world_x, world_y):
        """Get the tile at the specified world coordinates."""
        chunk = self.get_chunk_at(world_x, world_y)
        if chunk:
            return chunk.get_tile_at(world_x, world_y)
        return None
    
    def is_position_valid(self, world_x, world_y):
        """Check if a position is valid (not blocked by terrain)."""
        # In a full implementation, this would check collision with terrain
        # For now, just check if it's within world bounds
        return (0 <= world_x < self.width and 0 <= world_y < self.height)
    
    def game_over(self):
        """Trigger game over."""
        self.game_over = True
        if hasattr(self.game, 'game_over'):
            self.game.game_over()
    
    def victory(self):
        """Trigger victory."""
        self.victory = True
        if hasattr(self.game, 'victory'):
            self.game.victory()
    
    def reset(self):
        """Reset the world state."""
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.dungeons = []
        self.active_dungeon = None
        self.time = 0
        self.weather = 'clear'
        self.weather_timer = 0
        self.game_over = False
        self.victory = False
        
        # Keep chunks but reset entities
        for chunk in self.chunks.values():
            chunk.entities = []

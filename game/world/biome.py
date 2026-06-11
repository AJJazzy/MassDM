"""
STICK REALM: SHADOW OPEN WORLD - Biome System
Handles biome generation, transitions, and properties
"""

import pygame
import random
import math
import noise
from config import *


class Biome:
    """
    Represents a biome type with its properties and generation rules.
    """
    
    def __init__(self, biome_type):
        """
        Initialize a biome.
        biome_type: Type of biome ('forest', 'village', etc.)
        """
        self.type = biome_type
        self.config = BIOMES.get(biome_type, BIOMES['forest'])
        
        # Properties
        self.color = self.config.get('color', GRAY_40)
        self.difficulty = self.config.get('difficulty', 1.0)
        self.ambience = self.config.get('ambience', 'forest')
        
        # Enemy types that spawn in this biome
        self.enemy_types = self.config.get('enemies', ['grunt'])
        
        # Feature densities
        self.tree_density = self.config.get('tree_density', 0)
        self.rock_density = self.config.get('rock_density', 0)
        self.building_density = self.config.get('building_density', 0)
        self.cacti_density = self.config.get('cacti_density', 0)
        self.ice_patch_density = self.config.get('ice_patch_density', 0)
        self.trap_density = self.config.get('trap_density', 0)
        
        # Spawn weights for enemies
        self.enemy_weights = {}
        for enemy_type in self.enemy_types:
            self.enemy_weights[enemy_type] = 1.0
    
    def get_spawnable_enemies(self):
        """Get list of enemies that can spawn in this biome."""
        return self.enemy_types
    
    def get_random_enemy_type(self):
        """Get a random enemy type weighted by spawn probability."""
        total_weight = sum(self.enemy_weights.values())
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for enemy_type, weight in self.enemy_weights.items():
            cumulative += weight
            if r <= cumulative:
                return enemy_type
        
        return self.enemy_types[0] if self.enemy_types else 'grunt'
    
    def get_enemy_spawn_rate(self):
        """Get the base enemy spawn rate for this biome."""
        return 0.01 * self.difficulty  # Higher difficulty = more spawns
    
    def get_feature_density(self, feature_type):
        """Get the density of a specific feature in this biome."""
        if feature_type == 'tree':
            return self.tree_density
        elif feature_type == 'rock':
            return self.rock_density
        elif feature_type == 'building':
            return self.building_density
        elif feature_type == 'cactus':
            return self.cacti_density
        elif feature_type == 'ice_patch':
            return self.ice_patch_density
        elif feature_type == 'trap':
            return self.trap_density
        return 0


def generate_biome_map(width_chunks, height_chunks, seed=None):
    """
    Generate a biome map for the world.
    width_chunks, height_chunks: Size of the world in chunks
    seed: Random seed for reproducible generation
    Returns: 2D array of biome types
    """
    if seed is None:
        seed = random.randint(0, 1000000)
    
    # Create noise generator
    # Using simple Perlin noise for biome transitions
    scale = 0.1
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    
    biome_map = [[None for _ in range(width_chunks)] for _ in range(height_chunks)]
    
    # Generate noise values
    noise_values = [[0 for _ in range(width_chunks)] for _ in range(height_chunks)]
    
    for x in range(width_chunks):
        for y in range(height_chunks):
            # Generate noise value
            nx = x / width_chunks - 0.5
            ny = y / height_chunks - 0.5
            
            # Simple noise using hash function (simplified Perlin)
            noise_val = hash((x * 997 + seed, y * 991 + seed)) / float(2**32)
            noise_val = (noise_val - 0.5) * 2  # Range: -1 to 1
            
            # Add octaves
            value = noise_val
            amplitude = 1
            frequency = 1
            for _ in range(octaves - 1):
                frequency *= lacunarity
                amplitude *= persistence
                nx2 = x / width_chunks * frequency - 0.5
                ny2 = y / height_chunks * frequency - 0.5
                noise_val2 = hash((int(x * frequency) * 997 + seed, int(y * frequency) * 991 + seed)) / float(2**32)
                noise_val2 = (noise_val2 - 0.5) * 2
                value += noise_val2 * amplitude
            
            noise_values[x][y] = value
    
    # Assign biomes based on noise values
    biome_types = list(BIOMES.keys())
    
    for x in range(width_chunks):
        for y in range(height_chunks):
            value = noise_values[x][y]
            
            # Map noise value to biome
            # Forest is most common (center of range)
            if value < -0.6:
                biome_type = 'shadow_realm'
            elif value < -0.4:
                biome_type = 'cave'
            elif value < -0.2:
                biome_type = 'dungeon'
            elif value < 0:
                biome_type = 'castle'
            elif value < 0.2:
                biome_type = 'forest'
            elif value < 0.4:
                biome_type = 'village'
            elif value < 0.6:
                biome_type = 'desert'
            else:
                biome_type = 'ice_wastes'
            
            biome_map[x][y] = biome_type
    
    # Smooth biome transitions
    biome_map = _smooth_biome_map(biome_map, width_chunks, height_chunks)
    
    return biome_map


def _smooth_biome_map(biome_map, width, height):
    """
    Smooth biome transitions to reduce single-tile biomes.
    """
    smoothed = [[None for _ in range(width)] for _ in range(height)]
    
    for x in range(width):
        for y in range(height):
            # Get neighboring biomes
            neighbors = []
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append(biome_map[nx][ny])
            
            # Use the most common biome in the neighborhood
            if neighbors:
                biome_counts = {}
                for biome in neighbors:
                    biome_counts[biome] = biome_counts.get(biome, 0) + 1
                smoothed[x][y] = max(biome_counts.items(), key=lambda x: x[1])[0]
            else:
                smoothed[x][y] = biome_map[x][y]
    
    return smoothed


def get_biome_at(world_x, world_y, biome_map, chunks_per_biome=1):
    """
    Get the biome at specific world coordinates.
    world_x, world_y: World coordinates in pixels
    biome_map: 2D array of biome types
    chunks_per_biome: How many chunks per biome cell
    Returns: Biome type string
    """
    # Convert world coordinates to biome map coordinates
    chunk_x = int(world_x / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome))
    chunk_y = int(world_y / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome))
    
    # Clamp to map bounds
    chunk_x = clamp(chunk_x, 0, len(biome_map) - 1)
    chunk_y = clamp(chunk_y, 0, len(biome_map[0]) - 1)
    
    return biome_map[chunk_x][chunk_y]


def get_biome_transition(world_x, world_y, biome_map, chunks_per_biome=1):
    """
    Get biome transition information at specific coordinates.
    Returns: (primary_biome, secondary_biome, transition_factor)
    transition_factor: 0 = fully in primary, 1 = fully in secondary
    """
    # Get the biome at this position
    chunk_x = int(world_x / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome))
    chunk_y = int(world_y / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome))
    
    # Clamp to map bounds
    chunk_x = clamp(chunk_x, 0, len(biome_map) - 1)
    chunk_y = clamp(chunk_y, 0, len(biome_map[0]) - 1)
    
    primary_biome = biome_map[chunk_x][chunk_y]
    
    # Check neighboring biomes for transitions
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = chunk_x + dx, chunk_y + dy
        if 0 <= nx < len(biome_map) and 0 <= ny < len(biome_map[0]):
            neighbor_biome = biome_map[nx][ny]
            if neighbor_biome != primary_biome:
                # Calculate transition factor based on position within chunk
                chunk_local_x = (world_x % (CHUNK_SIZE * TILE_SIZE * chunks_per_biome)) / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome)
                chunk_local_y = (world_y % (CHUNK_SIZE * TILE_SIZE * chunks_per_biome)) / (CHUNK_SIZE * TILE_SIZE * chunks_per_biome)
                
                if dx == -1:
                    factor = chunk_local_x
                elif dx == 1:
                    factor = 1 - chunk_local_x
                elif dy == -1:
                    factor = chunk_local_y
                elif dy == 1:
                    factor = 1 - chunk_local_y
                
                return (primary_biome, neighbor_biome, factor)
    
    return (primary_biome, None, 0)


# Simple hash function for noise generation
def hash(p):
    """Simple hash function for pseudo-random number generation."""
    x, y = p
    h = (x * 123456791 + y * 987654321) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    h = (h * 0x85ebca6b) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) & 0xFFFFFFFF
    h = (h * 0xc2b2ae35) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return h

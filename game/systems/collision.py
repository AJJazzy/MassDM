"""
STICK REALM: SHADOW OPEN WORLD - Collision System
Handles collision detection with spatial partitioning and broad phase checks
"""

import pygame
import math
from config import *


class CollisionSystem:
    """
    Handles collision detection between entities and terrain.
    Uses spatial partitioning for efficient collision checks.
    """
    
    def __init__(self, world):
        """
        Initialize the collision system.
        world: Reference to the world instance
        """
        self.world = world
        
        # Spatial grid for broad phase collision
        self.grid_cell_size = 64  # Size of each grid cell in pixels
        self.grid = {}  # Dictionary: (cell_x, cell_y) -> list of entities
        
        # Collision settings
        self.broad_phase = PHYSICS_BROAD_PHASE
        self.spatial_partitioning = PHYSICS_SPATIAL_PARTITIONING
        self.distance_checks = PHYSICS_DISTANCE_CHECKS
        self.sleeping = PHYSICS_SLEEPING
        
        # Statistics
        self.collision_checks = 0
        self.collisions_detected = 0
    
    def update(self, dt):
        """
        Update collision system.
        dt: Time since last frame in seconds
        """
        # Clear grid
        self.grid = {}
        
        # Rebuild spatial grid
        if self.spatial_partitioning:
            self._rebuild_grid()
    
    def _rebuild_grid(self):
        """Rebuild the spatial grid with all collidable entities."""
        # Add all enemies
        for enemy in self.world.enemies:
            self._add_to_grid(enemy)
        
        # Add all items
        for item in self.world.items:
            self._add_to_grid(item)
        
        # Add all projectiles
        for projectile in self.world.projectiles:
            self._add_to_grid(projectile)
        
        # Add player
        self._add_to_grid(self.world.player)
    
    def _add_to_grid(self, entity):
        """Add an entity to the spatial grid."""
        if not hasattr(entity, 'get_hitbox'):
            return
        
        hitbox = entity.get_hitbox()
        
        # Calculate grid cells this entity occupies
        min_cell_x = int(hitbox.x / self.grid_cell_size)
        min_cell_y = int(hitbox.y / self.grid_cell_size)
        max_cell_x = int((hitbox.x + hitbox.width) / self.grid_cell_size)
        max_cell_y = int((hitbox.y + hitbox.height) / self.grid_cell_size)
        
        # Add to all occupied cells
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_key = (cell_x, cell_y)
                if cell_key not in self.grid:
                    self.grid[cell_key] = []
                if entity not in self.grid[cell_key]:
                    self.grid[cell_key].append(entity)
    
    def check_collision(self, entity, other_entity=None):
        """
        Check if an entity collides with any other entity.
        entity: Entity to check
        other_entity: Specific entity to check against (optional)
        Returns: List of colliding entities
        """
        if not hasattr(entity, 'get_hitbox'):
            return []
        
        collisions = []
        entity_hitbox = entity.get_hitbox()
        
        if other_entity is not None:
            # Check against specific entity
            if hasattr(other_entity, 'get_hitbox'):
                if entity_hitbox.colliderect(other_entity.get_hitbox()):
                    collisions.append(other_entity)
            return collisions
        
        # Broad phase: Check spatial grid
        if self.broad_phase and self.spatial_partitioning:
            collisions = self._broad_phase_collision(entity, entity_hitbox)
        else:
            # Brute force check against all entities
            collisions = self._brute_force_collision(entity, entity_hitbox)
        
        return collisions
    
    def _broad_phase_collision(self, entity, entity_hitbox):
        """Perform broad phase collision detection using spatial grid."""
        collisions = []
        
        # Calculate grid cells this entity occupies
        min_cell_x = int(entity_hitbox.x / self.grid_cell_size)
        min_cell_y = int(entity_hitbox.y / self.grid_cell_size)
        max_cell_x = int((entity_hitbox.x + entity_hitbox.width) / self.grid_cell_size)
        max_cell_y = int((entity_hitbox.y + entity_hitbox.height) / self.grid_cell_size)
        
        # Check all entities in occupied cells and neighboring cells
        for cell_x in range(min_cell_x - 1, max_cell_x + 2):
            for cell_y in range(min_cell_y - 1, max_cell_y + 2):
                cell_key = (cell_x, cell_y)
                if cell_key in self.grid:
                    for other_entity in self.grid[cell_key]:
                        # Skip self
                        if other_entity is entity:
                            continue
                        
                        # Narrow phase: Check actual collision
                        if hasattr(other_entity, 'get_hitbox'):
                            other_hitbox = other_entity.get_hitbox()
                            if entity_hitbox.colliderect(other_hitbox):
                                collisions.append(other_entity)
        
        return collisions
    
    def _brute_force_collision(self, entity, entity_hitbox):
        """Perform brute force collision detection."""
        collisions = []
        
        # Check against all enemies
        # Check against enemies
        for other_entity in self.world.enemies:
            if other_entity is entity:
                continue
            if hasattr(other_entity, 'get_hitbox'):
                if entity_hitbox.colliderect(other_entity.get_hitbox()):
                    collisions.append(other_entity)
        
        # Check against items
        for other_entity in self.world.items:
            if other_entity is entity:
                continue
            if hasattr(other_entity, 'get_hitbox'):
                if entity_hitbox.colliderect(other_entity.get_hitbox()):
                    collisions.append(other_entity)
        
        # Check against projectiles
        for other_entity in self.world.projectiles:
            if other_entity is entity:
                continue
            if hasattr(other_entity, 'get_hitbox'):
                if entity_hitbox.colliderect(other_entity.get_hitbox()):
                    collisions.append(other_entity)
        
        # Check against player
        if self.world.player is not entity:
            if hasattr(self.world.player, 'get_hitbox'):
                if entity_hitbox.colliderect(self.world.player.get_hitbox()):
                    collisions.append(self.world.player)
        
        return collisions
    
    def check_terrain_collision(self, entity, dx=0, dy=0):
        """
        Check if an entity collides with terrain.
        entity: Entity to check
        dx, dy: Movement offset to check
        Returns: True if collision, False otherwise
        """
        if not hasattr(entity, 'get_hitbox'):
            return False
        
        hitbox = entity.get_hitbox()
        
        # Calculate new position
        new_x = hitbox.x + dx
        new_y = hitbox.y + dy
        new_hitbox = pygame.Rect(new_x, new_y, hitbox.width, hitbox.height)
        
        # Check against world terrain
        # Get chunks that this hitbox overlaps
        min_chunk_x = int(new_x / (CHUNK_SIZE * TILE_SIZE))
        min_chunk_y = int(new_y / (CHUNK_SIZE * TILE_SIZE))
        max_chunk_x = int((new_x + hitbox.width) / (CHUNK_SIZE * TILE_SIZE))
        max_chunk_y = int((new_y + hitbox.height) / (CHUNK_SIZE * TILE_SIZE))
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.world.get_chunk_at(
                    chunk_x * CHUNK_SIZE * TILE_SIZE,
                    chunk_y * CHUNK_SIZE * TILE_SIZE
                )
                if chunk:
                    # Check collision with chunk features
                    if self._check_chunk_collision(chunk, new_hitbox):
                        return True
        
        # Check world bounds
        if new_x < 0 or new_x + hitbox.width > WORLD_WIDTH_PIXELS:
            return True
        if new_y < 0 or new_y + hitbox.height > WORLD_HEIGHT_PIXELS:
            return True
        
        return False
    
    def _check_chunk_collision(self, chunk, hitbox):
        """Check collision with features in a chunk."""
        # Check against trees, rocks, buildings, etc.
        for feature in chunk.features:
            feature_type = feature['type']
            
            if feature_type == 'tree':
                # Tree collision (trunk)
                tree_x = feature['x'] * TILE_SIZE
                tree_y = feature['y'] * TILE_SIZE
                tree_size = feature['size']
                
                # Trunk hitbox
                trunk_width = tree_size // 4
                trunk_height = tree_size
                trunk_x = tree_x + (TILE_SIZE - trunk_width) // 2
                trunk_y = tree_y - trunk_height
                trunk_hitbox = pygame.Rect(trunk_x, trunk_y, trunk_width, trunk_height)
                
                if hitbox.colliderect(trunk_hitbox):
                    return True
            
            elif feature_type == 'rock':
                # Rock collision
                rock_x = feature['x'] * TILE_SIZE
                rock_y = feature['y'] * TILE_SIZE
                rock_size = feature['size']
                
                rock_hitbox = pygame.Rect(
                    rock_x - rock_size // 2, 
                    rock_y - rock_size // 2,
                    rock_size, rock_size
                )
                
                if hitbox.colliderect(rock_hitbox):
                    return True
            
            elif feature_type == 'building':
                # Building collision
                building_x = feature['x'] * TILE_SIZE
                building_y = feature['y'] * TILE_SIZE
                building_width = feature['width']
                building_height = feature['height']
                
                building_hitbox = pygame.Rect(
                    building_x, 
                    building_y - building_height,
                    building_width, building_height
                )
                
                if hitbox.colliderect(building_hitbox):
                    return True
        
        return False
    
    def resolve_collision(self, entity, dx, dy):
        """
        Resolve collision for an entity trying to move.
        entity: Entity to move
        dx, dy: Desired movement
        Returns: (actual_dx, actual_dy) after collision resolution
        """
        if not hasattr(entity, 'get_hitbox'):
            return (dx, dy)
        
        hitbox = entity.get_hitbox()
        
        # Try moving in x direction
        new_x = hitbox.x + dx
        new_hitbox_x = pygame.Rect(new_x, hitbox.y, hitbox.width, hitbox.height)
        
        if not self.check_terrain_collision(entity, dx, 0):
            actual_dx = dx
        else:
            # Try smaller steps
            actual_dx = 0
            step = dx / 4
            for _ in range(4):
                if not self.check_terrain_collision(entity, actual_dx + step, 0):
                    actual_dx += step
                else:
                    break
        
        # Try moving in y direction
        new_y = hitbox.y + dy
        new_hitbox_y = pygame.Rect(hitbox.x + actual_dx, new_y, hitbox.width, hitbox.height)
        
        if not self.check_terrain_collision(entity, 0, dy):
            actual_dy = dy
        else:
            # Try smaller steps
            actual_dy = 0
            step = dy / 4
            for _ in range(4):
                if not self.check_terrain_collision(entity, 0, actual_dy + step):
                    actual_dy += step
                else:
                    break
        
        # Check entity collisions
        entity_hitbox = pygame.Rect(
            hitbox.x + actual_dx, 
            hitbox.y + actual_dy,
            hitbox.width, hitbox.height
        )
        
        # Check against other entities
        collisions = self.check_collision(entity)
        for other_entity in collisions:
            # Push out of collision
            if hasattr(other_entity, 'get_hitbox'):
                other_hitbox = other_entity.get_hitbox()
                
                # Calculate overlap
                overlap_x = min(entity_hitbox.right, other_hitbox.right) - max(entity_hitbox.left, other_hitbox.left)
                overlap_y = min(entity_hitbox.bottom, other_hitbox.bottom) - max(entity_hitbox.top, other_hitbox.top)
                
                if overlap_x < overlap_y:
                    # Push horizontally
                    if entity_hitbox.centerx < other_hitbox.centerx:
                        actual_dx = max(0, actual_dx - overlap_x)
                    else:
                        actual_dx = min(0, actual_dx + overlap_x)
                else:
                    # Push vertically
                    if entity_hitbox.centery < other_hitbox.centery:
                        actual_dy = max(0, actual_dy - overlap_y)
                    else:
                        actual_dy = min(0, actual_dy + overlap_y)
        
        return (actual_dx, actual_dy)
    
    def get_collision_normal(self, entity, other_entity):
        """
        Get the collision normal between two entities.
        entity: First entity
        other_entity: Second entity
        Returns: (nx, ny) normal vector
        """
        if not hasattr(entity, 'get_hitbox') or not hasattr(other_entity, 'get_hitbox'):
            return (0, 0)
        
        hitbox1 = entity.get_hitbox()
        hitbox2 = other_entity.get_hitbox()
        
        # Calculate overlap
        overlap_x = min(hitbox1.right, hitbox2.right) - max(hitbox1.left, hitbox2.left)
        overlap_y = min(hitbox1.bottom, hitbox2.bottom) - max(hitbox1.top, hitbox2.top)
        
        if overlap_x < overlap_y:
            # Horizontal collision
            if hitbox1.centerx < hitbox2.centerx:
                return (-1, 0)
            else:
                return (1, 0)
        else:
            # Vertical collision
            if hitbox1.centery < hitbox2.centery:
                return (0, -1)
            else:
                return (0, 1)
    
    def get_stats(self):
        """Get collision system statistics."""
        return {
            'collision_checks': self.collision_checks,
            'collisions_detected': self.collisions_detected,
            'grid_cells': len(self.grid)
        }
    
    def reset_stats(self):
        """Reset collision statistics."""
        self.collision_checks = 0
        self.collisions_detected = 0

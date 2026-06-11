"""
STICK REALM: SHADOW OPEN WORLD
Minimap System

Minimalist black and white minimap showing world layout.
All elements rendered as simple geometric shapes.
"""

import pygame
import math
from config import *


class Minimap:
    """Minimalist minimap showing player position, chunks, and points of interest."""
    
    def __init__(self, world, x, y, width, height):
        self.world = world
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey(BLACK)
        self.zoom = MINIMAP_ZOOM
        self.rotation = 0  # 0 = north up, can be rotated
        
    def update(self, player, dt):
        """Update minimap (currently just follows player)."""
        pass
        
    def render(self, screen):
        """Render the minimap."""
        # Clear surface
        self.surface.fill(BLACK)
        
        # Calculate scale
        scale = self.rect.width / (WORLD_CHUNK_SIZE * CHUNK_SIZE * self.zoom)
        
        # Draw chunks
        for chunk_pos in self.world.loaded_chunks:
            chunk_x, chunk_y = chunk_pos
            
            # Calculate screen position
            screen_x = self.rect.width // 2 + (chunk_x * CHUNK_SIZE - self.world.camera.x) * scale
            screen_y = self.rect.height // 2 + (chunk_y * CHUNK_SIZE - self.world.camera.y) * scale
            
            # Draw chunk border
            chunk_size_px = CHUNK_SIZE * scale
            if chunk_size_px > 2:  # Only draw if visible
                pygame.draw.rect(
                    self.surface, 
                    GRAY_30, 
                    (screen_x - chunk_size_px // 2, 
                     screen_y - chunk_size_px // 2, 
                     chunk_size_px, chunk_size_px), 
                    1
                )
        
        # Draw biome colors (simplified)
        for chunk_pos, chunk in self.world.loaded_chunks.items():
            chunk_x, chunk_y = chunk_pos
            biome = chunk.biome
            
            # Get biome color (black and white)
            biome_color = BIOME_COLORS.get(biome, GRAY_20)
            
            # Calculate screen position
            screen_x = self.rect.width // 2 + (chunk_x * CHUNK_SIZE - self.world.camera.x) * scale
            screen_y = self.rect.height // 2 + (chunk_y * CHUNK_SIZE - self.world.camera.y) * scale
            
            # Draw biome fill
            chunk_size_px = CHUNK_SIZE * scale
            if chunk_size_px > 2:
                pygame.draw.rect(
                    self.surface, 
                    biome_color, 
                    (screen_x - chunk_size_px // 2, 
                     screen_y - chunk_size_px // 2, 
                     chunk_size_px, chunk_size_px)
                )
        
        # Draw player position (stick figure)
        player_x = self.rect.width // 2 + (self.world.player.x - self.world.camera.x) * scale
        player_y = self.rect.height // 2 + (self.world.player.y - self.world.camera.y) * scale
        
        # Draw player as a small stick figure
        head_radius = max(2, int(4 * scale))
        pygame.draw.circle(self.surface, WHITE, (int(player_x), int(player_y)), head_radius, 1)
        
        # Body
        body_length = head_radius * 3
        pygame.draw.line(
            self.surface, WHITE,
            (int(player_x), int(player_y) + head_radius),
            (int(player_x), int(player_y) + head_radius + body_length), 1
        )
        
        # Direction indicator (facing direction)
        if hasattr(self.world.player, 'facing'):
            angle = self.world.player.facing
            dir_length = head_radius * 2
            end_x = player_x + dir_length * math.cos(angle)
            end_y = player_y + dir_length * math.sin(angle)
            pygame.draw.line(
                self.surface, YELLOW,
                (int(player_x), int(player_y)),
                (int(end_x), int(end_y)), 1
            )
        
        # Draw enemies as small dots
        for enemy in self.world.enemies:
            enemy_x = self.rect.width // 2 + (enemy.x - self.world.camera.x) * scale
            enemy_y = self.rect.height // 2 + (enemy.y - self.world.camera.y) * scale
            
            # Different colors for different enemy types
            color = ENEMY_COLORS.get(type(enemy).__name__, RED)
            pygame.draw.circle(self.surface, color, (int(enemy_x), int(enemy_y)), 2)
        
        # Draw dungeon entrances
        for dungeon_pos in self.world.dungeon_entrances:
            dungeon_x = self.rect.width // 2 + (dungeon_pos[0] - self.world.camera.x) * scale
            dungeon_y = self.rect.height // 2 + (dungeon_pos[1] - self.world.camera.y) * scale
            
            # Draw dungeon as a square
            size = max(3, int(6 * scale))
            pygame.draw.rect(
                self.surface, BLUE,
                (int(dungeon_x) - size // 2, int(dungeon_y) - size // 2, size, size), 1
            )
        
        # Draw boss markers
        for boss_pos in self.world.boss_positions:
            boss_x = self.rect.width // 2 + (boss_pos[0] - self.world.camera.x) * scale
            boss_y = self.rect.height // 2 + (boss_pos[1] - self.world.camera.y) * scale
            
            # Draw boss as a star
            size = max(4, int(8 * scale))
            pygame.draw.circle(self.surface, RED, (int(boss_x), int(boss_y)), size, 1)
            pygame.draw.circle(self.surface, RED, (int(boss_x), int(boss_y)), size // 2, 1)
        
        # Draw minimap border
        pygame.draw.rect(self.surface, WHITE, (0, 0, self.rect.width, self.rect.height), 1)
        
        # Draw compass directions
        font = pygame.font.SysFont(None, int(12 * scale))
        directions = ['N', 'E', 'S', 'W']
        for i, dir_text in enumerate(directions):
            text = font.render(dir_text, True, WHITE)
            angle = i * 90
            rad = math.radians(angle)
            text_x = self.rect.width // 2 + (self.rect.width // 2 - 10) * math.cos(rad)
            text_y = self.rect.height // 2 + (self.rect.height // 2 - 10) * math.sin(rad)
            text_rect = text.get_rect(center=(int(text_x), int(text_y)))
            self.surface.blit(text, text_rect)
        
        # Blit to screen
        screen.blit(self.surface, (self.rect.x, self.rect.y))
        
    def get_screen_position(self, world_x, world_y):
        """Convert world coordinates to minimap screen coordinates."""
        scale = self.rect.width / (WORLD_CHUNK_SIZE * CHUNK_SIZE * self.zoom)
        screen_x = self.rect.x + self.rect.width // 2 + (world_x - self.world.camera.x) * scale
        screen_y = self.rect.y + self.rect.height // 2 + (world_y - self.world.camera.y) * scale
        return (int(screen_x), int(screen_y))

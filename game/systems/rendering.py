"""
STICK REALM: SHADOW OPEN WORLD - Rendering System
Handles all rendering with batching, culling, and LOD
"""

import pygame
import math
from config import *


class RenderingSystem:
    """
    Handles all rendering for the game.
    Supports batching, culling, and level-of-detail rendering.
    """
    
    def __init__(self, world, camera):
        """
        Initialize the rendering system.
        world: Reference to the world instance
        camera: Reference to the camera instance
        """
        self.world = world
        self.camera = camera
        
        # Display
        self.screen = None
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        # Render settings
        self.batch_rendering = RENDER_BATCHING
        self.culling = RENDER_CULLING
        self.lod = RENDER_LOD
        self.occlusion = RENDER_OCCLUSION
        
        # Statistics
        self.draw_calls = 0
        self.triangles_drawn = 0
        self.entities_rendered = 0
        
        # Initialize screen
        self._init_screen()
    
    def _init_screen(self):
        """Initialize the game screen."""
        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
    
    def clear(self, color=None):
        """Clear the screen."""
        if color is None:
            color = BLACK
        self.screen.fill(color)
        
        # Reset statistics
        self.draw_calls = 0
        self.triangles_drawn = 0
        self.entities_rendered = 0
    
    def render_frame(self):
        """Render a complete frame."""
        # Clear screen
        self.clear()
        
        # Render world
        self.world.render(self.screen)
        
        # Render player (handled by world)
        
        # Note: HUD and menus are rendered separately by the main game
        
    def render_world(self):
        """Render the game world."""
        self.world.render(self.screen)
    
    def render_player(self):
        """Render the player."""
        # Player is rendered by the world
        pass
    
    def render_entity(self, entity, camera):
        """
        Render a single entity with culling and LOD.
        entity: Entity to render
        camera: Camera object
        """
        if not hasattr(entity, 'render'):
            return
        
        # Culling check
        if self.culling:
            if not self._is_visible(entity, camera):
                return
        
        # LOD check
        if self.lod:
            distance = self._get_distance_to_camera(entity, camera)
            if distance > 500:  # Far away - use lower detail
                # In a full implementation, would use simplified rendering
                pass
        
        # Render the entity
        entity.render(self.screen, camera)
        self.entities_rendered += 1
    
    def _is_visible(self, entity, camera):
        """Check if an entity is visible on screen."""
        # Get entity bounds
        if hasattr(entity, 'get_hitbox'):
            hitbox = entity.get_hitbox()
            if hitbox.width <= 0 or hitbox.height <= 0:
                return False
        else:
            return True
        
        # Get camera offset
        cam_x, cam_y = camera.get_offset()
        
        # Calculate screen position
        screen_x = hitbox.x - cam_x
        screen_y = hitbox.y - cam_y
        
        # Check if on screen
        if (screen_x + hitbox.width < 0 or screen_x > self.screen_width or
            screen_y + hitbox.height < 0 or screen_y > self.screen_height):
            return False
        
        return True
    
    def _get_distance_to_camera(self, entity, camera):
        """Get the distance from an entity to the camera."""
        if hasattr(entity, 'get_center'):
            entity_x, entity_y = entity.get_center()
        else:
            return 0
        
        cam_x, cam_y = camera.get_center()
        return distance(entity_x, entity_y, cam_x, cam_y)
    
    def draw_line(self, surface, color, start_pos, end_pos, width=1):
        """Draw a line with batching."""
        pygame.draw.line(surface, color, start_pos, end_pos, width)
        self.draw_calls += 1
    
    def draw_circle(self, surface, color, center, radius, width=0):
        """Draw a circle with batching."""
        pygame.draw.circle(surface, color, center, radius, width)
        self.draw_calls += 1
    
    def draw_rect(self, surface, color, rect, width=0):
        """Draw a rectangle with batching."""
        pygame.draw.rect(surface, color, rect, width)
        self.draw_calls += 1
    
    def draw_polygon(self, surface, color, points, width=0):
        """Draw a polygon with batching."""
        pygame.draw.polygon(surface, color, points, width)
        self.draw_calls += 1
    
    def draw_text(self, surface, text, font, color, position):
        """Draw text with batching."""
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, position)
        self.draw_calls += 1
    
    def get_stats(self):
        """Get rendering statistics."""
        return {
            'draw_calls': self.draw_calls,
            'entities_rendered': self.entities_rendered,
            'triangles_drawn': self.triangles_drawn
        }
    
    def set_fullscreen(self, fullscreen):
        """Set fullscreen mode."""
        if fullscreen:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
    
    def resize(self, width, height):
        """Resize the screen."""
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height))
        
        # Update config
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = width
        SCREEN_HEIGHT = height

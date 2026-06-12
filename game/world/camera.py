"""
STICK REALM: SHADOW OPEN WORLD - Camera System
Smooth following camera with shake effects and zoom
"""

import pygame
import math
import random
from config import *


class Camera:
    """
    Camera system that follows the player with smooth interpolation.
    Supports zoom, shake effects, and clamping to world bounds.
    """
    
    def __init__(self, target, screen_width, screen_height):
        """
        Initialize the camera.
        target: Entity to follow (usually the player)
        screen_width: Width of the screen
        screen_height: Height of the screen
        """
        # Position
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        
        # Screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Target to follow
        self.target = target
        
        # Smoothing
        self.lerp_factor = CAMERA_LERP_FACTOR
        
        # Zoom
        self.zoom = CAMERA_ZOOM_DEFAULT
        self.target_zoom = CAMERA_ZOOM_DEFAULT
        self.zoom_speed = CAMERA_ZOOM_SPEED
        
        # Shake
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Clamping
        self.clamp_to_world = True
        self.world_width = WORLD_WIDTH_PIXELS
        self.world_height = WORLD_HEIGHT_PIXELS
        
        # Viewport
        self.viewport_width = SCREEN_WIDTH
        self.viewport_height = SCREEN_HEIGHT
    
    def update(self, dt):
        """
        Update camera position, zoom, and shake effects.
        dt: Time since last frame in seconds
        """
        # Update zoom
        if self.zoom != self.target_zoom:
            if abs(self.zoom - self.target_zoom) < self.zoom_speed * dt * 60:
                self.zoom = self.target_zoom
            else:
                self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed * dt * 60
        
        # Update shake
        self._update_shake(dt)
        
        # Update target position from followed entity
        if self.target:
            self.target_x = self.target.x + self.target.width // 2
            self.target_y = self.target.y + self.target.height // 2
        
        # Smoothly interpolate position toward target
        self.x = lerp(self.x, self.target_x, self.lerp_factor * 60 * dt)
        self.y = lerp(self.y, self.target_y, self.lerp_factor * 60 * dt)
        
        # Clamp to world bounds
        if self.clamp_to_world:
            self._clamp_to_world()
    
    def _update_shake(self, dt):
        """Update shake effect."""
        if self.shake_timer > 0:
            self.shake_timer -= dt
            
            # Generate random offset
            if self.shake_intensity > 0:
                self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
                self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            else:
                self.shake_offset_x = 0
                self.shake_offset_y = 0
        else:
            self.shake_intensity = 0
            self.shake_duration = 0
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def _clamp_to_world(self):
        """Clamp camera position to world bounds."""
        # Calculate visible area
        visible_width = self.viewport_width / self.zoom
        visible_height = self.viewport_height / self.zoom
        
        # Clamp x
        if visible_width >= self.world_width:
            self.x = self.world_width // 2 - visible_width // 2
        else:
            self.x = clamp(self.x, 0, self.world_width - visible_width)
        
        # Clamp y
        if visible_height >= self.world_height:
            self.y = self.world_height // 2 - visible_height // 2
        else:
            self.y = clamp(self.y, 0, self.world_height - visible_height)
    
    def shake(self, intensity, duration):
        """
        Start a camera shake effect.
        intensity: Maximum shake offset in pixels
        duration: Duration of shake in seconds
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration
    
    def set_zoom(self, zoom):
        """Set target zoom level."""
        self.target_zoom = clamp(zoom, CAMERA_ZOOM_MIN, CAMERA_ZOOM_MAX)
    
    def zoom_in(self):
        """Zoom in."""
        self.target_zoom = clamp(self.zoom - CAMERA_ZOOM_SPEED * 2, CAMERA_ZOOM_MIN, CAMERA_ZOOM_MAX)
    
    def zoom_out(self):
        """Zoom out."""
        self.target_zoom = clamp(self.zoom + CAMERA_ZOOM_SPEED * 2, CAMERA_ZOOM_MIN, CAMERA_ZOOM_MAX)
    
    def reset_zoom(self):
        """Reset zoom to default."""
        self.target_zoom = CAMERA_ZOOM_DEFAULT
    
    def get_offset(self):
        """
        Get the camera offset for rendering.
        Returns: (offset_x, offset_y) to subtract from world coordinates
        """
        # Apply zoom
        offset_x = self.x - self.viewport_width / (2 * self.zoom)
        offset_y = self.y - self.viewport_height / (2 * self.zoom)
        
        # Apply shake
        offset_x += self.shake_offset_x
        offset_y += self.shake_offset_y
        
        return (offset_x, offset_y)
    
    def get_scale(self):
        """Get the current zoom scale."""
        return self.zoom
    
    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.
        world_x, world_y: World coordinates
        Returns: (screen_x, screen_y)
        """
        offset_x, offset_y = self.get_offset()
        screen_x = (world_x - offset_x) * self.zoom
        screen_y = (world_y - offset_y) * self.zoom
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.
        screen_x, screen_y: Screen coordinates
        Returns: (world_x, world_y)
        """
        offset_x, offset_y = self.get_offset()
        world_x = screen_x / self.zoom + offset_x
        world_y = screen_y / self.zoom + offset_y
        return (world_x, world_y)
    
    def get_visible_rect(self):
        """
        Get the rectangle of the world that is currently visible.
        Returns: pygame.Rect
        """
        offset_x, offset_y = self.get_offset()
        visible_width = self.viewport_width / self.zoom
        visible_height = self.viewport_height / self.zoom
        return pygame.Rect(offset_x, offset_y, visible_width, visible_height)
    
    def set_position(self, x, y):
        """Set camera position directly."""
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
    
    def set_target(self, x, y):
        """Set camera target position (for smooth following)."""
        self.target_x = x
        self.target_y = y
    
    def lock_to_player(self, player):
        """Lock camera to follow a player."""
        self.target = player
        if player:
            self.target_x = player.x + player.width // 2
            self.target_y = player.y + player.height // 2
    
    def get_center(self):
        """Get the center of the camera in world coordinates."""
        return (self.x, self.y)

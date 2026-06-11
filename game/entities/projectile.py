"""
STICK REALM: SHADOW OPEN WORLD - Projectile Entities
Arrows, fireballs, shockwaves, and other projectiles
"""

import pygame
import math
from config import *


class Projectile:
    """
    Base projectile class - moves through the world and deals damage on hit.
    All projectiles are rendered as simple geometric shapes.
    """
    
    def __init__(self, projectile_type, x, y, vx, vy, owner, game):
        """
        Initialize a projectile at position (x, y) with velocity (vx, vy).
        projectile_type: Type of projectile ('arrow', 'fireball', 'shockwave')
        x, y: Starting position
        vx, vy: Velocity components
        owner: Entity that fired this projectile
        game: Reference to the main game instance
        """
        self.type = projectile_type
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.game = game
        
        # Dimensions
        self.width = 10
        self.height = 10
        
        # Lifetime
        self.lifetime = 3.0  # Default lifetime in seconds
        self.age = 0
        
        # Damage
        self.damage = 10
        self.damage_type = 'normal'
        
        # Physics
        self.gravity = 0
        self.knockback = 50
        
        # Piercing
        self.piercing = False
        self.hit_entities = []
        
        # Visual
        self.color = WHITE
        self.rotation = 0
        self.scale = 1.0
        
        # Set properties based on projectile type
        self._init_properties()
    
    def _init_properties(self):
        """Initialize properties based on projectile type."""
        if self.type == 'arrow':
            self.width = ARROW_LENGTH
            self.height = ARROW_WIDTH
            self.lifetime = ARROW_LIFETIME
            self.color = ARROW_COLOR
            self.damage = 10
            self.gravity = 0.2
            self.knockback = 30
            self.piercing = False
        elif self.type == 'fireball':
            self.width = FIREBALL_DIAMETER
            self.height = FIREBALL_DIAMETER
            self.lifetime = FIREBALL_LIFETIME
            self.color = GRAY_70
            self.damage = FIREBALL_BASE_DAMAGE
            self.damage_type = 'burn'
            self.gravity = 0.1
            self.knockback = 40
            self.piercing = False
        elif self.type == 'shockwave':
            self.width = 0
            self.height = 0
            self.lifetime = SHOCKWAVE_MAX_RADIUS / SHOCKWAVE_SPEED
            self.color = SHOCKWAVE_COLOR
            self.damage = 40
            self.gravity = 0
            self.knockback = 50
            self.piercing = True
        else:
            # Default projectile
            self.width = 10
            self.height = 10
            self.lifetime = 3.0
            self.color = GRAY_70
            self.damage = 10
    
    def update(self, dt):
        """
        Update projectile position and check for collisions.
        dt: Time since last frame in seconds
        Returns: True if projectile should continue to exist, False if it should be removed
        """
        # Update age
        self.age += dt
        if self.age >= self.lifetime:
            self._on_expiry()
            return False
        
        # Apply gravity
        self.vy += self.gravity * dt * 60
        
        # Apply velocity
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Update rotation (for arrows)
        if self.type == 'arrow':
            self.rotation = math.degrees(math.atan2(self.vy, self.vx))
        
        # Update scale (for shockwave)
        if self.type == 'shockwave':
            self.scale = min(1.0, self.age * SHOCKWAVE_SPEED / SHOCKWAVE_MAX_RADIUS)
            self.width = int(SHOCKWAVE_MAX_RADIUS * self.scale * 2)
            self.height = int(SHOCKWAVE_MAX_RADIUS * self.scale * 2)
        
        # Check for collisions
        if self._check_collisions(dt):
            return False
        
        # Clamp position to world bounds
        self.x = clamp(self.x, 0, WORLD_WIDTH_PIXELS)
        self.y = clamp(self.y, 0, WORLD_HEIGHT_PIXELS)
        
        # Remove if out of bounds
        if (self.x < 0 or self.x > WORLD_WIDTH_PIXELS or
            self.y < 0 or self.y > WORLD_HEIGHT_PIXELS):
            return False
        
        return True
    
    def _check_collisions(self, dt):
        """Check for collisions with entities and terrain. Returns True if hit something."""
        # Check collision with player
        if hasattr(self.game, 'player'):
            player = self.game.player
            if self._check_entity_collision(player):
                return True
        
        # Check collision with enemies (if not owned by an enemy)
        if hasattr(self.game, 'world') and hasattr(self.game.world, 'enemies'):
            for enemy in self.game.world.enemies[:]:
                # Don't collide with owner
                if enemy == self.owner:
                    continue
                if self._check_entity_collision(enemy):
                    if not self.piercing:
                        return True
        
        # Check collision with terrain (simplified - would use tilemap in full implementation)
        if self.y >= WORLD_HEIGHT_PIXELS - self.height:
            if self.type == 'arrow':
                # Arrow sticks to ground
                self.vx = 0
                self.vy = 0
                self.lifetime = 5.0  # Stay for a while
                return False
            else:
                # Other projectiles explode on ground contact
                self._on_hit(None, self.x, self.y)
                return True
        
        return False
    
    def _check_entity_collision(self, entity):
        """Check collision with a specific entity."""
        # Get hitboxes
        my_hitbox = self.get_hitbox()
        their_hitbox = entity.get_hitbox()
        
        # Check intersection
        if my_hitbox.colliderect(their_hitbox):
            # Don't hit the same entity twice (unless piercing)
            if entity in self.hit_entities and not self.piercing:
                return False
            
            # Register hit
            self.hit_entities.append(entity)
            
            # Calculate direction of hit
            my_center = (self.x + self.width // 2, self.y + self.height // 2)
            their_center = entity.get_center()
            dx = my_center[0] - their_center[0]
            direction = 1 if dx > 0 else -1
            
            # Apply damage
            if hasattr(entity, 'take_damage'):
                entity.take_damage(self.damage, direction, self.knockback, self.damage_type)
            
            # Handle hit
            self._on_hit(entity, their_center[0], their_center[1])
            
            return True
        
        return False
    
    def _on_hit(self, entity, hit_x, hit_y):
        """Handle hit event."""
        if self.type == 'fireball':
            # Create explosion
            if hasattr(self.game, 'combat_system'):
                self.game.combat_system.create_explosion(
                    hit_x, hit_y, FIREBALL_EXPLOSION_RADIUS, FIREBALL_EXPLOSION_DAMAGE, self.owner
                )
        elif self.type == 'shockwave':
            # Shockwave already handles its own damage
            pass
        
        # Create hit particles
        if hasattr(self.game, 'particle_system'):
            if self.damage_type == 'burn':
                self.game.particle_system.create_spark_particles(hit_x, hit_y)
            else:
                self.game.particle_system.create_damage_particles(hit_x, hit_y)
    
    def _on_expiry(self):
        """Handle projectile expiry."""
        if self.type == 'shockwave':
            # Shockwave fades out
            pass
        elif hasattr(self.game, 'particle_system'):
            # Create small particles on expiry
            self.game.particle_system.create_dust_particles(self.x, self.y)
    
    def render(self, surface, camera):
        """
        Render the projectile.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        # Get camera offset
        cam_x, cam_y = camera.get_offset()
        
        # Calculate screen position
        screen_x = int(self.x - cam_x)
        screen_y = int(self.y - cam_y)
        
        # Don't render if off-screen
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # Draw based on projectile type
        if self.type == 'arrow':
            self._draw_arrow(surface, screen_x, screen_y)
        elif self.type == 'fireball':
            self._draw_fireball(surface, screen_x, screen_y)
        elif self.type == 'shockwave':
            self._draw_shockwave(surface, screen_x, screen_y)
        else:
            self._draw_default(surface, screen_x, screen_y)
    
    def _draw_arrow(self, surface, screen_x, screen_y):
        """Draw an arrow."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Arrow shaft (line)
        pygame.draw.line(surface, self.color, 
                        (screen_x, center_y), 
                        (screen_x + self.width, center_y), 
                        self.height)
        
        # Arrow head (triangle)
        head_points = [
            (screen_x + self.width, center_y),
            (screen_x + self.width - 5, center_y - 3),
            (screen_x + self.width - 5, center_y + 3)
        ]
        pygame.draw.polygon(surface, self.color, head_points, 0)
        
        # Rotate if needed
        if self.rotation != 0:
            # Create a surface for the arrow
            arrow_surface = pygame.Surface((self.width + 5, self.height * 2), pygame.SRCALPHA)
            arrow_center = (self.width // 2 + 2, self.height)
            
            # Draw arrow on surface
            pygame.draw.line(arrow_surface, self.color, (0, self.height), (self.width, self.height), self.height)
            head_points_surface = [
                (self.width, self.height),
                (self.width - 5, self.height - 3),
                (self.width - 5, self.height + 3)
            ]
            pygame.draw.polygon(arrow_surface, self.color, head_points_surface, 0)
            
            # Rotate surface
            rotated_surface = pygame.transform.rotate(arrow_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=arrow_center)
            
            # Blit rotated surface
            surface.blit(rotated_surface, (screen_x - rotated_rect.x, screen_y - rotated_rect.y + self.height // 2))
    
    def _draw_fireball(self, surface, screen_x, screen_y):
        """Draw a fireball."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Fireball (circle)
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.width // 2, 0)
        
        # Fireball outline
        pygame.draw.circle(surface, (200, 100, 0), (center_x, center_y), self.width // 2, 1)
        
        # Trail effect (simple)
        trail_length = min(20, self.width // 2)
        for i in range(1, trail_length):
            alpha = int(255 * (1 - i / trail_length))
            trail_color = (255, 150, 0, alpha)
            trail_radius = self.width // 2 - i // 2
            if trail_radius > 0:
                # Draw trail circle
                trail_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color, (self.width // 2 + 2, self.height // 2 + 2), trail_radius, 0)
                surface.blit(trail_surface, (screen_x - 2 + int(i * self.vx / abs(self.vx) if self.vx != 0 else 0), 
                                            screen_y - 2 + int(i * self.vy / abs(self.vy) if self.vy != 0 else 0)))
    
    def _draw_shockwave(self, surface, screen_x, screen_y):
        """Draw a shockwave."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Shockwave is a circle with fade-out
        radius = int(self.width // 2)
        alpha = int(255 * (1 - self.scale))
        
        # Create shockwave surface
        shockwave_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        
        # Draw shockwave circle
        color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(shockwave_surface, color_with_alpha, (radius + 2, radius + 2), radius, 2)
        
        # Blit to main surface
        surface.blit(shockwave_surface, (screen_x - radius - 2, screen_y - radius - 2))
    
    def _draw_default(self, surface, screen_x, screen_y):
        """Draw a default projectile (circle)."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.width // 2, 0)
        pygame.draw.circle(surface, WHITE, (center_x, center_y), self.width // 2, 1)
    
    def get_hitbox(self):
        """Get the projectile's hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self):
        """Get the center position of the projectile."""
        return (self.x + self.width // 2, self.y + self.height // 2)


class Arrow(Projectile):
    """Arrow projectile."""
    
    def __init__(self, x, y, vx, vy, owner, game):
        super().__init__('arrow', x, y, vx, vy, owner, game)
        self.damage = 10


class Fireball(Projectile):
    """Fireball projectile."""
    
    def __init__(self, x, y, vx, vy, owner, game):
        super().__init__('fireball', x, y, vx, vy, owner, game)
        self.damage = FIREBALL_BASE_DAMAGE
        self.damage_type = 'burn'
    
    def _on_hit(self, entity, hit_x, hit_y):
        """Create explosion on hit."""
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.create_explosion(
                hit_x, hit_y, FIREBALL_EXPLOSION_RADIUS, FIREBALL_EXPLOSION_DAMAGE, self.owner
            )
        
        # Create spark particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_spark_particles(hit_x, hit_y)


class Shockwave(Projectile):
    """Shockwave projectile (expanding circle)."""
    
    def __init__(self, x, y, radius, damage, owner, game):
        # Shockwave starts at center and expands
        super().__init__('shockwave', x - radius, y - radius, 0, 0, owner, game)
        self.max_radius = radius
        self.damage = damage
        self.current_radius = 0
        self.lifetime = radius / SHOCKWAVE_SPEED
    
    def update(self, dt):
        """Update shockwave - expand over time."""
        self.age += dt
        
        # Calculate current radius
        self.current_radius = min(self.max_radius, SHOCKWAVE_SPEED * self.age)
        self.width = int(self.current_radius * 2)
        self.height = int(self.current_radius * 2)
        
        # Check for collisions with entities
        self._check_collisions(dt)
        
        if self.age >= self.lifetime:
            return False
        
        return True
    
    def _check_collisions(self, dt):
        """Check for collisions with entities in radius."""
        center_x, center_y = self.get_center()
        
        # Check collision with player
        if hasattr(self.game, 'player'):
            player = self.game.player
            player_center = player.get_center()
            distance = distance(center_x, center_y, player_center[0], player_center[1])
            
            if distance <= self.current_radius:
                # Calculate direction
                dx = center_x - player_center[0]
                direction = 1 if dx > 0 else -1
                
                # Apply damage
                player.take_damage(self.damage, direction, self.knockback, self.damage_type)
        
        # Check collision with enemies
        if hasattr(self.game, 'world') and hasattr(self.game.world, 'enemies'):
            for enemy in self.game.world.enemies[:]:
                # Don't hit owner
                if enemy == self.owner:
                    continue
                
                enemy_center = enemy.get_center()
                distance = distance(center_x, center_y, enemy_center[0], enemy_center[1])
                
                if distance <= self.current_radius:
                    # Calculate direction
                    dx = center_x - enemy_center[0]
                    direction = 1 if dx > 0 else -1
                    
                    # Apply damage
                    enemy.take_damage(self.damage, direction, self.knockback, self.damage_type)
    
    def _on_hit(self, entity, hit_x, hit_y):
        """Shockwave doesn't need special hit handling."""
        pass


# Projectile type mapping for spawning
PROJECTILE_CLASS_MAP = {
    'arrow': Arrow,
    'fireball': Fireball,
    'shockwave': Shockwave
}


def create_projectile(projectile_type, x, y, vx, vy, owner, game):
    """Factory function to create a projectile of the specified type."""
    if projectile_type == 'shockwave':
        # Shockwave needs radius parameter
        return Shockwave(x, y, vx, vy, owner, game)
    
    projectile_class = PROJECTILE_CLASS_MAP.get(projectile_type, Projectile)
    return projectile_class(x, y, vx, vy, owner, game)

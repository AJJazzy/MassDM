"""
STICK REALM: SHADOW OPEN WORLD - Particle System
Handles particle effects for combat, movement, and special events
"""

import pygame
import random
import math
from config import *


class Particle:
    """
    A single particle with position, velocity, lifetime, and appearance.
    """
    
    def __init__(self, x, y, particle_type, game):
        """
        Initialize a particle.
        x, y: Starting position
        particle_type: Type of particle
        game: Reference to the main game instance
        """
        self.x = x
        self.y = y
        self.type = particle_type
        self.game = game
        
        # Lifetime
        self.lifetime = 1.0  # Default lifetime in seconds
        self.age = 0
        
        # Physics
        self.vx = 0
        self.vy = 0
        self.gravity = 0
        self.friction = 0
        
        # Appearance
        self.size = 5
        self.color = WHITE
        self.alpha = 255
        self.rotation = 0
        self.rotation_speed = 0
        
        # Set properties based on particle type
        self._init_properties()
    
    def _init_properties(self):
        """Initialize properties based on particle type."""
        if self.type == 'dust':
            self.lifetime = random.uniform(0.3, 0.8)
            self.vx = random.uniform(-50, 50)
            self.vy = random.uniform(-50, -100)
            self.gravity = 0.5
            self.friction = 0.9
            self.size = random.randint(2, 4)
            self.color = GRAY_50
            self.alpha = random.randint(100, 200)
        elif self.type == 'blood':
            self.lifetime = random.uniform(0.5, 1.0)
            self.vx = random.uniform(-100, 100)
            self.vy = random.uniform(-100, -50)
            self.gravity = 0.8
            self.friction = 0.95
            self.size = random.randint(3, 6)
            self.color = RED
            self.alpha = 255
        elif self.type == 'spark':
            self.lifetime = random.uniform(0.2, 0.5)
            self.vx = random.uniform(-200, 200)
            self.vy = random.uniform(-200, 200)
            self.gravity = 0
            self.friction = 0.9
            self.size = random.randint(2, 5)
            self.color = YELLOW
            self.alpha = 255
        elif self.type == 'heal':
            self.lifetime = random.uniform(0.5, 1.0)
            self.vx = random.uniform(-20, 20)
            self.vy = random.uniform(-50, -20)
            self.gravity = 0.2
            self.friction = 0.95
            self.size = random.randint(3, 5)
            self.color = GREEN
            self.alpha = 200
        elif self.type == 'level_up':
            self.lifetime = random.uniform(0.5, 1.0)
            self.vx = random.uniform(-100, 100)
            self.vy = random.uniform(-100, 100)
            self.gravity = 0
            self.friction = 0.9
            self.size = random.randint(4, 8)
            self.color = YELLOW
            self.alpha = 255
        elif self.type == 'damage':
            self.lifetime = random.uniform(0.3, 0.6)
            self.vx = random.uniform(-50, 50)
            self.vy = random.uniform(-50, 50)
            self.gravity = 0
            self.friction = 0.95
            self.size = random.randint(3, 6)
            self.color = RED
            self.alpha = 200
        elif self.type == 'block':
            self.lifetime = random.uniform(0.2, 0.4)
            self.vx = random.uniform(-50, 50)
            self.vy = random.uniform(-50, 50)
            self.gravity = 0
            self.friction = 0.9
            self.size = random.randint(2, 4)
            self.color = BLUE
            self.alpha = 200
        elif self.type == 'crit':
            self.lifetime = random.uniform(0.3, 0.6)
            self.vx = random.uniform(-100, 100)
            self.vy = random.uniform(-100, 100)
            self.gravity = 0
            self.friction = 0.9
            self.size = random.randint(4, 8)
            self.color = YELLOW
            self.alpha = 255
        elif self.type == 'warning':
            self.lifetime = random.uniform(0.5, 1.0)
            self.vx = 0
            self.vy = random.uniform(-20, 20)
            self.gravity = 0
            self.friction = 1.0
            self.size = random.randint(5, 10)
            self.color = RED
            self.alpha = int(128 + 127 * math.sin(self.age * math.pi * 2))
        elif self.type == 'death':
            self.lifetime = random.uniform(0.5, 1.0)
            self.vx = random.uniform(-100, 100)
            self.vy = random.uniform(-100, 100)
            self.gravity = 0.2
            self.friction = 0.95
            self.size = random.randint(5, 10)
            self.color = RED
            self.alpha = 255
    
    def update(self, dt):
        """
        Update particle state.
        dt: Time since last frame in seconds
        Returns: True if particle should continue to exist, False if it should be removed
        """
        # Update age
        self.age += dt
        if self.age >= self.lifetime:
            return False
        
        # Apply gravity
        self.vy += self.gravity * dt * 60
        
        # Apply friction
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Apply velocity
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Update rotation
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360
        
        # Update alpha (fade out)
        if self.age > self.lifetime * 0.7:
            self.alpha = int(255 * (1 - (self.age - self.lifetime * 0.7) / (self.lifetime * 0.3)))
        
        return True
    
    def render(self, surface, camera):
        """
        Render the particle.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        # Get camera offset
        cam_x, cam_y = camera.get_offset()
        
        # Calculate screen position
        screen_x = int(self.x - cam_x)
        screen_y = int(self.y - cam_y)
        
        # Don't render if off-screen
        if (screen_x + self.size < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.size < 0 or screen_y > SCREEN_HEIGHT):
            return
        
        # Draw based on particle type
        if self.type in ['dust', 'blood', 'spark', 'heal', 'damage', 'block', 'crit', 'death']:
            # Draw as a circle
            if self.alpha < 255:
                # Create surface with alpha
                particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                color_with_alpha = (self.color[0], self.color[1], self.color[2], self.alpha)
                pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size, 0)
                surface.blit(particle_surface, (screen_x - self.size, screen_y - self.size))
            else:
                pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size, 0)
        elif self.type == 'level_up':
            # Draw as a star
            self._draw_star(surface, screen_x, screen_y)
        elif self.type == 'warning':
            # Draw as a pulsing circle
            if self.alpha < 255:
                particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                color_with_alpha = (self.color[0], self.color[1], self.color[2], self.alpha)
                pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size, 0)
                surface.blit(particle_surface, (screen_x - self.size, screen_y - self.size))
            else:
                pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size, 0)
    
    def _draw_star(self, surface, x, y):
        """Draw a star-shaped particle."""
        points = []
        for i in range(5):
            angle = i * math.pi * 2 / 5 - math.pi / 2
            outer_radius = self.size
            inner_radius = self.size * 0.4
            
            # Outer point
            px = x + int(math.cos(angle) * outer_radius)
            py = y + int(math.sin(angle) * outer_radius)
            points.append((px, py))
            
            # Inner point
            angle += math.pi / 5
            px = x + int(math.cos(angle) * inner_radius)
            py = y + int(math.sin(angle) * inner_radius)
            points.append((px, py))
        
        # Draw star
        if self.alpha < 255:
            star_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            color_with_alpha = (self.color[0], self.color[1], self.color[2], self.alpha)
            # Convert points to star surface coordinates
            star_points = [(p[0] - x + self.size * 2, p[1] - y + self.size * 2) for p in points]
            pygame.draw.polygon(star_surface, color_with_alpha, star_points, 0)
            surface.blit(star_surface, (x - self.size * 2, y - self.size * 2))
        else:
            pygame.draw.polygon(surface, self.color, points, 0)


class ParticleSystem:
    """
    Manages all particles in the game.
    Handles creation, updating, and rendering of particles.
    """
    
    def __init__(self, game):
        """
        Initialize the particle system.
        game: Reference to the main game instance
        """
        self.game = game
        self.particles = []
        self.max_particles = MAX_PARTICLES
        
        # Statistics
        self.particles_created = 0
        self.particles_removed = 0
    
    def update(self, dt):
        """
        Update all particles.
        dt: Time since last frame in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self, surface, camera):
        """
        Render all particles.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        for particle in self.particles:
            particle.render(surface, camera)
    
    def create_particle(self, particle_type, x, y):
        """
        Create a single particle.
        particle_type: Type of particle
        x, y: Starting position
        Returns: The created particle
        """
        if len(self.particles) >= self.max_particles:
            # Remove oldest particle
            self.particles.pop(0)
        
        particle = Particle(x, y, particle_type, self.game)
        self.particles.append(particle)
        self.particles_created += 1
        return particle
    
    def create_particles(self, particle_type, x, y, count=10):
        """
        Create multiple particles.
        particle_type: Type of particle
        x, y: Starting position
        count: Number of particles to create
        """
        for _ in range(count):
            self.create_particle(particle_type, x, y)
    
    def create_dust_particles(self, x, y, count=5):
        """Create dust particles (for movement)."""
        self.create_particles('dust', x, y, count)
    
    def create_blood_particles(self, x, y, direction, count=8):
        """Create blood particles (for damage)."""
        for _ in range(count):
            particle = self.create_particle('blood', x, y)
            # Add some direction to blood
            particle.vx += direction * random.uniform(20, 50)
    
    def create_spark_particles(self, x, y, count=10):
        """Create spark particles (for critical hits)."""
        self.create_particles('spark', x, y, count)
    
    def create_heal_particles(self, x, y, count=5):
        """Create heal particles."""
        self.create_particles('heal', x, y, count)
    
    def create_level_up_particles(self, x, y, count=20):
        """Create level up particles."""
        self.create_particles('level_up', x, y, count)
    
    def create_damage_particles(self, x, y, count=5):
        """Create damage particles."""
        self.create_particles('damage', x, y, count)
    
    def create_block_particles(self, x, y, count=5):
        """Create block particles."""
        self.create_particles('block', x, y, count)
    
    def create_crit_particles(self, x, y, count=10):
        """Create critical hit particles."""
        self.create_particles('crit', x, y, count)
    
    def create_warning_particles(self, x, y, count=3):
        """Create warning particles."""
        self.create_particles('warning', x, y, count)
    
    def create_death_particles(self, x, y, count=15):
        """Create death particles."""
        self.create_particles('death', x, y, count)
    
    def create_explosion_particles(self, x, y, radius, count=30):
        """Create explosion particles."""
        for _ in range(count):
            particle = self.create_particle('spark', x, y)
            # Random direction
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            particle.vx = math.cos(angle) * speed
            particle.vy = math.sin(angle) * speed
            particle.lifetime = random.uniform(0.3, 0.8)
            particle.color = (255, 150, 0)  # Orange
    
    def clear(self):
        """Clear all particles."""
        self.particles = []
    
    def get_stats(self):
        """Get particle system statistics."""
        return {
            'particles_active': len(self.particles),
            'particles_created': self.particles_created,
            'particles_removed': self.particles_removed
        }
    
    def reset_stats(self):
        """Reset particle statistics."""
        self.particles_created = 0
        self.particles_removed = 0

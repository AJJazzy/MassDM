"""
STICK REALM: SHADOW OPEN WORLD - Item Entities
All item types that can be collected by the player
"""

import pygame
import math
from config import *


class Item:
    """
    Base item class - can be collected by the player.
    All items are rendered as simple geometric shapes.
    """
    
    def __init__(self, item_type, x, y, game, amount=1):
        """
        Initialize an item at position (x, y).
        item_type: Type of item ('coin', 'health_potion', etc.)
        x, y: Position
        game: Reference to the main game instance
        amount: Quantity (for coins)
        """
        self.type = item_type
        self.x = x
        self.y = y
        self.game = game
        self.amount = amount
        
        # Dimensions
        self.width = 20
        self.height = 20
        
        # Physics
        self.vx = 0
        self.vy = 0
        self.gravity = 0.4
        self.velocity_y = -5  # Bounce up initially
        self.bounce_factor = 0.7
        
        # Animation
        self.animation_timer = 0
        self.rotation = 0
        self.rotation_speed = 2  # degrees per frame
        
        # Collection
        self.collected = False
        self.collect_timer = 0
        self.collect_speed = 10
        
        # Color and appearance
        self.color = WHITE
        self.glow_timer = 0
        self.glow_alpha = 0
        
        # Set properties based on item type
        self._init_properties()
    
    def _init_properties(self):
        """Initialize properties based on item type."""
        if self.type == 'coin':
            self.width = COIN_DIAMETER
            self.height = COIN_DIAMETER
            self.color = COIN_COLOR
            self.value = COIN_VALUE * self.amount
        elif self.type == 'health_potion':
            self.width = HEALTH_POTION_SIZE
            self.height = HEALTH_POTION_SIZE
            self.color = RED
        elif self.type == 'weapon_upgrade':
            self.width = WEAPON_UPGRADE_SIZE
            self.height = WEAPON_UPGRADE_SIZE
            self.color = GRAY_70
        elif self.type == 'armour_upgrade':
            self.width = ARMOUR_UPGRADE_SIZE
            self.height = ARMOUR_UPGRADE_SIZE
            self.color = GRAY_60
        else:
            # Default item
            self.width = 20
            self.height = 20
            self.color = GRAY_70
    
    def update(self, dt):
        """
        Update item state.
        dt: Time since last frame in seconds
        """
        if self.collected:
            # Move toward player
            self._move_to_player(dt)
            return
        
        # Apply gravity
        self.velocity_y += self.gravity * dt * 60
        
        # Apply velocity
        self.x += self.vx * dt * 60
        self.y += self.velocity_y * dt * 60
        
        # Bounce off ground
        if self.y >= WORLD_HEIGHT_PIXELS - self.height:
            self.y = WORLD_HEIGHT_PIXELS - self.height
            self.velocity_y = -abs(self.velocity_y) * self.bounce_factor
            self.vx *= 0.8  # Reduce horizontal velocity on bounce
        
        # Update animation
        self.animation_timer += dt * 10
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360
        
        # Glow effect
        self.glow_timer += dt * 2
        self.glow_alpha = int(128 + 127 * math.sin(self.glow_timer))
        
        # Check for auto-collection
        if hasattr(self.game, 'player'):
            player_center = self.game.player.get_center()
            distance = distance(
                self.x + self.width // 2, self.y + self.height // 2,
                player_center[0], player_center[1]
            )
            if distance <= COIN_AUTO_COLLECT_RANGE:
                self.collect()
    
    def _move_to_player(self, dt):
        """Move item toward player after collection."""
        if not hasattr(self.game, 'player'):
            return
        
        player_center = self.game.player.get_center()
        dx = player_center[0] - (self.x + self.width // 2)
        dy = player_center[1] - (self.y + self.height // 2)
        
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 20:
            # Reached player - actually collect
            self._finalize_collection()
            return
        
        # Move toward player
        speed = self.collect_speed * (1 + 5 * (1 - dist / 200))  # Faster when closer
        self.x += (dx / dist) * speed * dt * 60
        self.y += (dy / dist) * speed * dt * 60
    
    def collect(self):
        """Start collection animation."""
        if self.collected:
            return
        
        self.collected = True
        self.collect_timer = 0
        
        # Play sound
        if hasattr(self.game, 'audio_system'):
            self.game.audio_system.play_sound('collect')
    
    def _finalize_collection(self):
        """Finalize collection and apply effects."""
        if self.type == 'coin':
            if hasattr(self.game, 'player'):
                self.game.player.collect_coins(self.amount)
        elif self.type == 'health_potion':
            if hasattr(self.game, 'player'):
                self.game.player.use_health_potion()
        elif self.type == 'weapon_upgrade':
            if hasattr(self.game, 'player'):
                self.game.player.collect_weapon_upgrade()
        elif self.type == 'armour_upgrade':
            if hasattr(self.game, 'player'):
                self.game.player.collect_armour_upgrade()
        
        # Mark for removal
        self.collected = True
        self.x = -1000  # Move off-screen
    
    def render(self, surface, camera):
        """
        Render the item.
        surface: Pygame surface to draw on
        camera: Camera object for position offset
        """
        # Get camera offset
        cam_x, cam_y = camera.get_offset()
        
        # Calculate screen position
        screen_x = int(self.x - cam_x)
        screen_y = int(self.y - cam_y)
        
        # Don't render if off-screen (unless being collected)
        if (screen_x + self.width < 0 or screen_x > SCREEN_WIDTH or
            screen_y + self.height < 0 or screen_y > SCREEN_HEIGHT):
            if not self.collected:
                return
        
        # Draw based on item type
        if self.type == 'coin':
            self._draw_coin(surface, screen_x, screen_y)
        elif self.type == 'health_potion':
            self._draw_health_potion(surface, screen_x, screen_y)
        elif self.type == 'weapon_upgrade':
            self._draw_weapon_upgrade(surface, screen_x, screen_y)
        elif self.type == 'armour_upgrade':
            self._draw_armour_upgrade(surface, screen_x, screen_y)
        else:
            self._draw_default(surface, screen_x, screen_y)
    
    def _draw_coin(self, surface, screen_x, screen_y):
        """Draw a coin."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Draw coin (circle)
        pygame.draw.circle(surface, self.color, (center_x, center_y), self.width // 2, 0)
        
        # Draw coin edge
        pygame.draw.circle(surface, YELLOW, (center_x, center_y), self.width // 2, 1)
        
        # Draw coin shine (rotating)
        shine_x = center_x + (self.width // 4) * math.cos(math.radians(self.rotation))
        shine_y = center_y + (self.width // 4) * math.sin(math.radians(self.rotation))
        pygame.draw.line(surface, WHITE, (center_x, center_y), (shine_x, shine_y), 1)
        
        # Draw amount if > 1
        if self.amount > 1:
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(str(self.amount), True, BLACK)
            surface.blit(text, (screen_x + self.width - text.get_width(), screen_y))
    
    def _draw_health_potion(self, surface, screen_x, screen_y):
        """Draw a health potion."""
        # Bottle
        pygame.draw.rect(surface, RED, (screen_x, screen_y, self.width, self.height), 0, border_radius=3)
        
        # Bottle outline
        pygame.draw.rect(surface, WHITE, (screen_x, screen_y, self.width, self.height), 1, border_radius=3)
        
        # Liquid inside
        liquid_height = int(self.height * 0.7)
        pygame.draw.rect(surface, (200, 0, 0), 
                        (screen_x + 2, screen_y + 2, self.width - 4, liquid_height), 
                        0, border_radius=2)
        
        # Glow effect
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 0, 0, self.glow_alpha), 
                           (0, 0, self.width + 4, self.height + 4), 
                           0, border_radius=5)
            surface.blit(glow_surface, (screen_x - 2, screen_y - 2))
    
    def _draw_weapon_upgrade(self, surface, screen_x, screen_y):
        """Draw a weapon upgrade (sword icon)."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Sword hilt
        pygame.draw.rect(surface, GRAY_50, 
                        (center_x - 4, center_y + 5, 8, 15), 0)
        
        # Sword blade
        pygame.draw.rect(surface, GRAY_70, 
                        (center_x - 2, center_y - 15, 4, 30), 0)
        
        # Sword guard
        pygame.draw.circle(surface, GRAY_40, (center_x, center_y + 5), 4, 0)
        
        # Glow effect (yellow)
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
            glow_color = (255, 255, 0, self.glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (self.width // 2 + 2, self.height // 2 + 2), 
                              max(self.width, self.height) // 2 + 2, 0)
            surface.blit(glow_surface, (screen_x - 2, screen_y - 2))
    
    def _draw_armour_upgrade(self, surface, screen_x, screen_y):
        """Draw an armour upgrade (shield icon)."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Shield
        pygame.draw.circle(surface, GRAY_60, (center_x, center_y), self.width // 2, 0)
        
        # Shield outline
        pygame.draw.circle(surface, GRAY_40, (center_x, center_y), self.width // 2, 1)
        
        # Shield boss
        boss_size = self.width // 4
        pygame.draw.circle(surface, GRAY_80, (center_x, center_y), boss_size, 0)
        
        # Glow effect (blue)
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
            glow_color = (0, 0, 255, self.glow_alpha)
            pygame.draw.circle(glow_surface, glow_color, (self.width // 2 + 2, self.height // 2 + 2), 
                              max(self.width, self.height) // 2 + 2, 0)
            surface.blit(glow_surface, (screen_x - 2, screen_y - 2))
    
    def _draw_default(self, surface, screen_x, screen_y):
        """Draw a default item (diamond shape)."""
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Draw diamond
        points = [
            (center_x, center_y - self.height // 2),
            (center_x + self.width // 2, center_y),
            (center_x, center_y + self.height // 2),
            (center_x - self.width // 2, center_y)
        ]
        pygame.draw.polygon(surface, self.color, points, 0)
        pygame.draw.polygon(surface, WHITE, points, 1)
    
    def get_hitbox(self):
        """Get the item's hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self):
        """Get the center position of the item."""
        return (self.x + self.width // 2, self.y + self.height // 2)


class Coin(Item):
    """Coin item."""
    
    def __init__(self, x, y, game, amount=1):
        super().__init__('coin', x, y, game, amount)


class HealthPotion(Item):
    """Health potion item."""
    
    def __init__(self, x, y, game):
        super().__init__('health_potion', x, y, game)


class WeaponUpgrade(Item):
    """Weapon upgrade item."""
    
    def __init__(self, x, y, game):
        super().__init__('weapon_upgrade', x, y, game)


class ArmourUpgrade(Item):
    """Armour upgrade item."""
    
    def __init__(self, x, y, game):
        super().__init__('armour_upgrade', x, y, game)


# Item type mapping for spawning
ITEM_CLASS_MAP = {
    'coin': Coin,
    'health_potion': HealthPotion,
    'weapon_upgrade': WeaponUpgrade,
    'armour_upgrade': ArmourUpgrade
}


def create_item(item_type, x, y, game, amount=1):
    """Factory function to create an item of the specified type."""
    item_class = ITEM_CLASS_MAP.get(item_type, Item)
    return item_class(x, y, game, amount)

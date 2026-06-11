"""
STICK REALM: SHADOW OPEN WORLD - HUD System
Handles health bar, XP bar, notifications, and other on-screen displays
"""

import pygame
import time
import math
from config import *


class Notification:
    """A single notification that appears on screen."""
    
    def __init__(self, text, duration=NOTIFICATION_DURATION, color=WHITE, font_size=NOTIFICATION_FONT_SIZE):
        """
        Initialize a notification.
        text: Notification text
        duration: Display duration in seconds
        color: Text color
        font_size: Font size
        """
        self.text = text
        self.duration = duration
        self.color = color
        self.font_size = font_size
        
        # State
        self.age = 0
        self.alpha = 0
        self.y_offset = 0
        
        # Font
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text_surface = self.font.render(text, True, color)
        self.text_width = self.text_surface.get_width()
        self.text_height = self.text_surface.get_height()
        
        # Animation
        self.fade_in_duration = 0.3
        self.fade_out_duration = 0.3
        self.slide_duration = 0.3
        self.target_y = 0
    
    def update(self, dt):
        """
        Update notification state.
        dt: Time since last frame in seconds
        Returns: True if notification should continue to exist, False if it should be removed
        """
        self.age += dt
        
        if self.age >= self.duration + self.fade_out_duration:
            return False
        
        # Fade in
        if self.age < self.fade_in_duration:
            self.alpha = int(255 * (self.age / self.fade_in_duration))
            self.y_offset = -50 * (1 - self.age / self.fade_in_duration)
        # Fade out
        elif self.age > self.duration:
            self.alpha = int(255 * (1 - (self.age - self.duration) / self.fade_out_duration))
        else:
            self.alpha = 255
            self.y_offset = 0
        
        return True
    
    def render(self, surface, x, y):
        """
        Render the notification.
        surface: Pygame surface to draw on
        x, y: Position to render at
        """
        if self.alpha <= 0:
            return
        
        # Create surface with alpha
        notification_surface = pygame.Surface((self.text_width + 20, self.text_height + 10), pygame.SRCALPHA)
        
        # Draw background
        bg_color = (0, 0, 0, 180)
        pygame.draw.rect(notification_surface, bg_color, (0, 0, self.text_width + 20, self.text_height + 10), 0, border_radius=5)
        
        # Draw border
        border_color = (255, 255, 255, self.alpha)
        pygame.draw.rect(notification_surface, border_color, (0, 0, self.text_width + 20, self.text_height + 10), 1, border_radius=5)
        
        # Draw text
        text_color = (self.color[0], self.color[1], self.color[2], self.alpha)
        text_surface = self.font.render(self.text, True, text_color)
        notification_surface.blit(text_surface, (10, 5))
        
        # Blit to screen
        surface.blit(notification_surface, (x, y + self.y_offset))


class ChatMessage:
    """A single chat message."""
    
    def __init__(self, text, color=WHITE, font_size=20):
        """
        Initialize a chat message.
        text: Message text
        color: Text color
        font_size: Font size
        """
        self.text = text
        self.color = color
        self.font_size = font_size
        self.age = 0
        self.lifetime = 10.0  # 10 seconds
        
        # Font
        self.font = pygame.font.SysFont('Arial', font_size)
        self.text_surface = self.font.render(text, True, color)
        self.text_width = self.text_surface.get_width()
        self.text_height = self.text_surface.get_height()
    
    def update(self, dt):
        """
        Update chat message state.
        dt: Time since last frame in seconds
        Returns: True if message should continue to exist, False if it should be removed
        """
        self.age += dt
        return self.age < self.lifetime
    
    def render(self, surface, x, y):
        """
        Render the chat message.
        surface: Pygame surface to draw on
        x, y: Position to render at
        """
        surface.blit(self.text_surface, (x, y))


class HUD:
    """
    Heads-Up Display - shows player stats, notifications, and other game info.
    """
    
    def __init__(self, game):
        """
        Initialize the HUD.
        game: Reference to the main game instance
        """
        self.game = game
        
        # Fonts
        self.font_small = pygame.font.SysFont('Arial', 16)
        self.font_medium = pygame.font.SysFont('Arial', 20)
        self.font_large = pygame.font.SysFont('Arial', 28)
        self.font_title = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Notifications
        self.notifications = []
        self.notification_spacing = 40
        
        # Chat messages
        self.chat_messages = []
        self.chat_max_messages = 10
        self.chat_open = False
        self.chat_input = ""
        
        # Debug info
        self.show_debug = False
        self.debug_font = pygame.font.SysFont('Arial', 12)
    
    def update(self, dt):
        """
        Update HUD state.
        dt: Time since last frame in seconds
        """
        # Update notifications
        self.notifications = [n for n in self.notifications if n.update(dt)]
        
        # Update chat messages
        self.chat_messages = [m for m in self.chat_messages if m.update(dt)]
    
    def render(self, surface):
        """
        Render the HUD.
        surface: Pygame surface to draw on
        """
        if not hasattr(self.game, 'player'):
            return
        
        player = self.game.player
        
        # Draw health bar
        self._draw_health_bar(surface, player)
        
        # Draw XP bar
        self._draw_xp_bar(surface, player)
        
        # Draw level
        self._draw_level(surface, player)
        
        # Draw coin counter
        self._draw_coins(surface, player)
        
        # Draw score counter
        self._draw_score(surface, player)
        
        # Draw kills counter
        self._draw_kills(surface, player)
        
        # Draw notifications
        self._draw_notifications(surface)
        
        # Draw chat
        self._draw_chat(surface)
        
        # Draw debug info
        if self.show_debug:
            self._draw_debug_info(surface)
    
    def _draw_health_bar(self, surface, player):
        """Draw the health bar."""
        x, y = HEALTH_BAR_POSITION
        width, height = HEALTH_BAR_SIZE
        
        # Calculate health percentage
        health_percent = player.health / player.max_health
        
        # Determine color based on health
        if health_percent > 0.66:
            color = HEALTH_BAR_COLORS['high']
        elif health_percent > 0.33:
            color = HEALTH_BAR_COLORS['medium']
        else:
            color = HEALTH_BAR_COLORS['low']
        
        # Draw background
        pygame.draw.rect(surface, HEALTH_BAR_BACKGROUND, (x, y, width, height), 0)
        
        # Draw border
        pygame.draw.rect(surface, HEALTH_BAR_BORDER, (x, y, width, height), 1)
        
        # Draw health fill
        fill_width = int(width * health_percent)
        pygame.draw.rect(surface, color, (x, y, fill_width, height), 0)
        
        # Draw health text
        health_text = f"{int(player.health)}/{int(player.max_health)}"
        text_surface = self.font_small.render(health_text, True, WHITE)
        surface.blit(text_surface, (x + width + 10, y))
    
    def _draw_xp_bar(self, surface, player):
        """Draw the XP bar."""
        x, y = XP_BAR_POSITION
        width, height = XP_BAR_SIZE
        
        # Calculate XP percentage
        xp_percent = player.xp / player.xp_to_level if player.xp_to_level > 0 else 0
        
        # Draw background
        pygame.draw.rect(surface, XP_BAR_BACKGROUND, (x, y, width, height), 0)
        
        # Draw border
        pygame.draw.rect(surface, WHITE, (x, y, width, height), 1)
        
        # Draw XP fill
        fill_width = int(width * xp_percent)
        pygame.draw.rect(surface, XP_BAR_COLOR, (x, y, fill_width, height), 0)
        
        # Draw XP text
        xp_text = f"{int(player.xp)}/{int(player.xp_to_level)}"
        text_surface = self.font_small.render(xp_text, True, WHITE)
        surface.blit(text_surface, (x, y + height + 5))
    
    def _draw_level(self, surface, player):
        """Draw the level display."""
        x, y = LEVEL_DISPLAY_POSITION
        
        level_text = f"Level: {player.level}"
        text_surface = self.font_medium.render(level_text, True, LEVEL_DISPLAY_COLOR)
        surface.blit(text_surface, (x - text_surface.get_width(), y))
    
    def _draw_coins(self, surface, player):
        """Draw the coin counter."""
        x, y = COIN_COUNTER_POSITION
        
        coin_text = f"Coins: {player.coins}"
        text_surface = self.font_medium.render(coin_text, True, COIN_COUNTER_COLOR)
        surface.blit(text_surface, (x, y))
    
    def _draw_score(self, surface, player):
        """Draw the score counter."""
        x, y = SCORE_COUNTER_POSITION
        
        score_text = f"Score: {player.score}"
        text_surface = self.font_medium.render(score_text, True, SCORE_COUNTER_COLOR)
        surface.blit(text_surface, (x, y))
    
    def _draw_kills(self, surface, player):
        """Draw the kills counter."""
        x, y = KILLS_COUNTER_POSITION
        
        kills_text = f"Kills: {player.kills}"
        text_surface = self.font_medium.render(kills_text, True, KILLS_COUNTER_COLOR)
        surface.blit(text_surface, (x - text_surface.get_width(), y))
    
    def _draw_notifications(self, surface):
        """Draw all notifications."""
        start_x = SCREEN_WIDTH // 2
        start_y = 100
        
        for i, notification in enumerate(self.notifications):
            # Calculate position (stacked vertically)
            y = start_y + i * self.notification_spacing
            notification.render(surface, start_x - notification.text_width // 2, y)
    
    def _draw_chat(self, surface):
        """Draw chat messages."""
        if not self.chat_messages:
            return
        
        # Draw chat background
        chat_height = min(200, len(self.chat_messages) * 25 + 20)
        pygame.draw.rect(surface, (0, 0, 0, 180), (20, SCREEN_HEIGHT - chat_height - 20, 400, chat_height), 0, border_radius=5)
        
        # Draw chat messages
        start_y = SCREEN_HEIGHT - chat_height - 15
        for i, message in enumerate(self.chat_messages):
            y = start_y + i * 25
            message.render(surface, 30, y)
        
        # Draw chat input if open
        if self.chat_open:
            # Draw input background
            pygame.draw.rect(surface, (50, 50, 50, 200), (20, SCREEN_HEIGHT - 50, 400, 30), 0, border_radius=5)
            
            # Draw input text
            input_text = self.chat_input + "|"
            text_surface = self.font_medium.render(input_text, True, WHITE)
            surface.blit(text_surface, (30, SCREEN_HEIGHT - 45))
    
    def _draw_debug_info(self, surface):
        """Draw debug information."""
        debug_info = []
        
        # FPS
        if hasattr(self.game, 'clock'):
            fps = self.game.clock.get_fps()
            debug_info.append(f"FPS: {fps:.1f}")
        
        # Entity count
        if hasattr(self.game, 'world'):
            debug_info.append(f"Enemies: {len(self.game.world.enemies)}")
            debug_info.append(f"Items: {len(self.game.world.items)}")
            debug_info.append(f"Projectiles: {len(self.game.world.projectiles)}")
            debug_info.append(f"Chunks: {len(self.game.world.chunks)}")
        
        # Player position
        if hasattr(self.game, 'player'):
            player = self.game.player
            debug_info.append(f"Pos: ({player.x:.1f}, {player.y:.1f})")
            debug_info.append(f"Health: {player.health}/{player.max_health}")
            debug_info.append(f"Level: {player.level}")
        
        # Biome
        if hasattr(self.game, 'world'):
            player = self.game.player
            if player:
                biome = self.game.world.get_biome_at(player.x, player.y)
                debug_info.append(f"Biome: {biome}")
        
        # Draw debug text
        for i, line in enumerate(debug_info):
            text_surface = self.debug_font.render(line, True, GREEN)
            surface.blit(text_surface, (10, 10 + i * 15))
    
    def add_notification(self, text, duration=None, color=None):
        """
        Add a notification to the HUD.
        text: Notification text
        duration: Display duration (default: NOTIFICATION_DURATION)
        color: Text color (default: WHITE)
        """
        if duration is None:
            duration = NOTIFICATION_DURATION
        if color is None:
            color = WHITE
        
        notification = Notification(text, duration, color)
        self.notifications.append(notification)
    
    def add_chat_message(self, text, color=None):
        """
        Add a chat message to the HUD.
        text: Message text
        color: Text color (default: WHITE)
        """
        if color is None:
            color = WHITE
        
        message = ChatMessage(text, color)
        self.chat_messages.append(message)
        
        # Limit number of messages
        if len(self.chat_messages) > self.chat_max_messages:
            self.chat_messages.pop(0)
    
    def toggle_chat(self):
        """Toggle chat open/closed."""
        self.chat_open = not self.chat_open
        if self.chat_open:
            self.chat_input = ""
    
    def add_chat_input(self, char):
        """Add a character to chat input."""
        if self.chat_open:
            self.chat_input += char
    
    def remove_chat_input(self):
        """Remove last character from chat input."""
        if self.chat_open and self.chat_input:
            self.chat_input = self.chat_input[:-1]
    
    def send_chat(self):
        """Send chat message."""
        if self.chat_open and self.chat_input:
            # Add to chat messages
            self.add_chat_message(f"You: {self.chat_input}")
            
            # Send to network
            if hasattr(self.game, 'networking'):
                self.game.networking.send_chat(self.chat_input)
            
            # Clear input
            self.chat_input = ""
            self.chat_open = False
    
    def toggle_debug(self):
        """Toggle debug info display."""
        self.show_debug = not self.show_debug

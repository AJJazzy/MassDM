"""
STICK REALM: SHADOW OPEN WORLD
Menu System

All menus are rendered as stick figures and minimalist elements.
Black and white color palette with accent colors.
"""

import pygame
import sys
from config import *


class Button:
    """Stick figure style button with minimalist rendering."""
    
    def __init__(self, x, y, width, height, text, action=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font_size = font_size
        self.hovered = False
        self.clicked = False
        self.cooldown = 0
        
    def update(self, mouse_pos, mouse_pressed, dt):
        """Update button state."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if self.cooldown > 0:
            self.cooldown -= dt
        
        if self.hovered and mouse_pressed[0] and self.cooldown <= 0:
            self.clicked = True
            self.cooldown = BUTTON_CLICK_COOLDOWN
            if self.action:
                self.action()
        else:
            self.clicked = False
            
    def render(self, screen):
        """Render stick figure style button."""
        # Button background (minimalist stick figure frame)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Stick figure icon in button center
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        # Draw a small stick figure
        head_radius = min(self.rect.width, self.rect.height) // 8
        pygame.draw.circle(screen, WHITE, (center_x, center_y - 10), head_radius, 1)
        
        # Body (vertical line)
        body_length = head_radius * 3
        pygame.draw.line(screen, WHITE, 
                        (center_x, center_y - 10 + head_radius), 
                        (center_x, center_y - 10 + head_radius + body_length), 1)
        
        # Arms
        arm_length = head_radius * 2
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y - 10 + head_radius + body_length // 3),
                        (center_x - arm_length, center_y - 10 + head_radius + body_length // 3), 1)
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y - 10 + head_radius + body_length // 3),
                        (center_x + arm_length, center_y - 10 + head_radius + body_length // 3), 1)
        
        # Legs
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y - 10 + head_radius + body_length),
                        (center_x - arm_length // 2, center_y - 10 + head_radius + body_length + arm_length), 1)
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y - 10 + head_radius + body_length),
                        (center_x + arm_length // 2, center_y - 10 + head_radius + body_length + arm_length), 1)
        
        # Text
        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(center_x, center_y + body_length + arm_length + 20))
        screen.blit(text_surface, text_rect)
        
        # Hover effect
        if self.hovered:
            pygame.draw.rect(screen, GRAY_50, self.rect, 1)
        
        # Click effect
        if self.clicked:
            pygame.draw.rect(screen, YELLOW, self.rect, 1)


class Slider:
    """Stick figure style slider for volume/brightness settings."""
    
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.knob_radius = height // 2
        
    def update(self, mouse_pos, mouse_pressed, dt):
        """Update slider state."""
        knob_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        knob_rect = pygame.Rect(knob_x - self.knob_radius, self.rect.y - self.knob_radius, 
                               self.knob_radius * 2, self.knob_radius * 2)
        
        if mouse_pressed[0]:
            if knob_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.dragging:
                # Update value based on mouse position
                self.value = self.min_val + (mouse_pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
                self.value = max(self.min_val, min(self.max_val, self.value))
        else:
            self.dragging = False
            
    def render(self, screen):
        """Render stick figure style slider."""
        # Track (horizontal line)
        pygame.draw.line(screen, WHITE, 
                        (self.rect.x, self.rect.centery), 
                        (self.rect.x + self.rect.width, self.rect.centery), 2)
        
        # Knob (stick figure head)
        knob_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, WHITE, (int(knob_x), self.rect.centery), self.knob_radius, 1)
        
        # Stick figure body on knob
        pygame.draw.line(screen, WHITE,
                        (int(knob_x), self.rect.centery - self.knob_radius),
                        (int(knob_x), self.rect.centery + self.knob_radius), 1)
        
        # Label
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(self.label, True, WHITE)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 30))
        
        # Value text
        value_text = f"{int(self.value * 100)}"
        text_surface = font.render(value_text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + self.rect.width + 10, self.rect.centery - 10))


class Menu:
    """Base menu class."""
    
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.sliders = []
        self.active = True
        self.alpha = 0
        self.target_alpha = 255
        
    def update(self, dt):
        """Update menu."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        # Fade in/out
        if self.alpha < self.target_alpha:
            self.alpha = min(self.alpha + MENU_FADE_SPEED * dt, self.target_alpha)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.alpha - MENU_FADE_SPEED * dt, self.target_alpha)
        
        # Update buttons and sliders
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed, dt)
        for slider in self.sliders:
            slider.update(mouse_pos, mouse_pressed, dt)
            
    def render(self, screen):
        """Render menu."""
        # Semi-transparent background
        if self.alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(int(self.alpha * 0.8))
            screen.blit(overlay, (0, 0))
        
        # Render buttons and sliders
        for button in self.buttons:
            button.render(screen)
        for slider in self.sliders:
            slider.render(screen)
            
    def add_button(self, x, y, width, height, text, action=None):
        """Add a button to the menu."""
        button = Button(x, y, width, height, text, action)
        self.buttons.append(button)
        return button
        
    def add_slider(self, x, y, width, height, min_val, max_val, initial_val, label=""):
        """Add a slider to the menu."""
        slider = Slider(x, y, width, height, min_val, max_val, initial_val, label)
        self.sliders.append(slider)
        return slider
    
    def clear(self):
        """Clear all buttons and sliders."""
        self.buttons = []
        self.sliders = []


class MainMenu(Menu):
    """Main menu with title screen and options."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_alpha = 0
        self.title_target_alpha = 255
        self.stick_figure_angle = 0
        
        # Add buttons
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50,
            200, 50, "PLAY", 
            lambda: self.game.start_game()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "MULTIPLAYER", 
            lambda: self.game.start_multiplayer()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90,
            200, 50, "OPTIONS", 
            lambda: self.game.show_options()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160,
            200, 50, "QUIT", 
            lambda: self.game.quit()
        )
        
    def update(self, dt):
        """Update main menu."""
        super().update(dt)
        
        # Update title fade
        if self.title_alpha < self.title_target_alpha:
            self.title_alpha = min(self.title_alpha + MENU_FADE_SPEED * dt, self.title_target_alpha)
        
        # Animate stick figure
        self.stick_figure_angle += dt * 0.5
        
    def render(self, screen):
        """Render main menu."""
        # Render animated stick figure in center
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 3
        
        # Draw stick figure with animation
        head_radius = 30
        pygame.draw.circle(screen, WHITE, (center_x, center_y), head_radius, 2)
        
        # Animated arms
        arm_length = 60
        arm_angle = self.stick_figure_angle
        end_x1 = center_x + arm_length * pygame.math.Vector2(1, 0).rotate(arm_angle).x
        end_y1 = center_y + head_radius + 20 + arm_length * pygame.math.Vector2(1, 0).rotate(arm_angle).y
        end_x2 = center_x + arm_length * pygame.math.Vector2(1, 0).rotate(-arm_angle).x
        end_y2 = center_y + head_radius + 20 + arm_length * pygame.math.Vector2(1, 0).rotate(-arm_angle).y
        
        pygame.draw.line(screen, WHITE, (center_x, center_y + head_radius), (end_x1, end_y1), 2)
        pygame.draw.line(screen, WHITE, (center_x, center_y + head_radius), (end_x2, end_y2), 2)
        
        # Body
        body_length = 80
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y + head_radius),
                        (center_x, center_y + head_radius + body_length), 2)
        
        # Legs
        leg_length = 50
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y + head_radius + body_length),
                        (center_x - 20, center_y + head_radius + body_length + leg_length), 2)
        pygame.draw.line(screen, WHITE,
                        (center_x, center_y + head_radius + body_length),
                        (center_x + 20, center_y + head_radius + body_length + leg_length), 2)
        
        # Title text
        title_font = pygame.font.SysFont(None, 64)
        title_text = title_font.render("STICK REALM", True, WHITE)
        title_rect = title_text.get_rect(center=(center_x, center_y + head_radius + body_length + leg_length + 40))
        title_text.set_alpha(int(self.title_alpha))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 32)
        subtitle_text = subtitle_font.render("SHADOW OPEN WORLD", True, GRAY_50)
        subtitle_rect = subtitle_text.get_rect(center=(center_x, center_y + head_radius + body_length + leg_length + 80))
        subtitle_text.set_alpha(int(self.title_alpha))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Render buttons
        super().render(screen)


class PauseMenu(Menu):
    """Pause menu."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Add buttons
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50,
            200, 50, "RESUME", 
            lambda: self.game.resume()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "OPTIONS", 
            lambda: self.game.show_options()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90,
            200, 50, "SAVE", 
            lambda: self.game.save_game()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 160,
            200, 50, "MAIN MENU", 
            lambda: self.game.return_to_main_menu()
        )


class GameOverMenu(Menu):
    """Game over menu."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Add buttons
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50,
            200, 50, "RETRY", 
            lambda: self.game.restart()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120,
            200, 50, "MAIN MENU", 
            lambda: self.game.return_to_main_menu()
        )
        
    def render(self, screen):
        """Render game over menu."""
        # Game over text
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, RED)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(text, rect)
        
        # Score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.game.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        super().render(screen)


class VictoryMenu(Menu):
    """Victory menu (after defeating final boss)."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Add buttons
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50,
            200, 50, "PLAY AGAIN", 
            lambda: self.game.restart()
        )
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120,
            200, 50, "MAIN MENU", 
            lambda: self.game.return_to_main_menu()
        )
        
    def render(self, screen):
        """Render victory menu."""
        # Victory text
        font = pygame.font.SysFont(None, 72)
        text = font.render("VICTORY", True, GREEN)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(text, rect)
        
        # Stats
        font = pygame.font.SysFont(None, 36)
        stats = [
            f"Time: {self.game.play_time:.2f}s",
            f"Kills: {self.game.kills}",
            f"Level: {self.game.player.level}",
            f"Score: {self.game.score}"
        ]
        
        for i, stat in enumerate(stats):
            text = font.render(stat, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40 + i * 40))
            screen.blit(text, rect)
        
        super().render(screen)


class OptionsMenu(Menu):
    """Options menu for settings."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Add sliders
        self.music_slider = self.add_slider(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100,
            300, 20, 0, 1, game.music_volume, "Music Volume"
        )
        self.sfx_slider = self.add_slider(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30,
            300, 20, 0, 1, game.sfx_volume, "SFX Volume"
        )
        self.brightness_slider = self.add_slider(
            SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40,
            300, 20, 0, 1, game.brightness, "Brightness"
        )
        
        # Add buttons
        self.add_button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120,
            200, 50, "BACK", 
            lambda: self.game.return_to_previous_menu()
        )
        
    def update(self, dt):
        """Update options menu."""
        super().update(dt)
        
        # Update game settings from sliders
        self.game.music_volume = self.music_slider.value
        self.game.sfx_volume = self.sfx_slider.value
        self.game.brightness = self.brightness_slider.value

"""
STICK REALM: SHADOW OPEN WORLD
Main Game File

Entry point for the game.
Initializes all systems and runs the main game loop.
"""

import pygame
import sys
import os
import time
import random
from config import *
from game.entities.player import Player
from game.entities.enemy import create_enemy
from game.entities.items import create_item
from game.entities.projectile import create_projectile
from game.world.world import World
from game.world.camera import Camera
from game.systems.rendering import RenderingSystem
from game.systems.collision import CollisionSystem
from game.systems.combat import CombatSystem
from game.systems.particles import ParticleSystem
from game.systems.networking import NetworkingSystem
from game.ui.hud import HUD
from game.ui.menu import MainMenu, PauseMenu, GameOverMenu, VictoryMenu, OptionsMenu
from game.ui.minimap import Minimap


class Game:
    """Main game class that manages all game states and systems."""
    
    def __init__(self):
        """Initialize the game."""
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("STICK REALM: SHADOW OPEN WORLD")
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = "menu"  # menu, playing, paused, game_over, victory
        self.running = True
        self.play_time = 0
        self.score = 0
        self.kills = 0
        self.coins = 0
        
        # Settings
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        self.brightness = DEFAULT_BRIGHTNESS
        
        # Initialize systems
        self.world = None
        self.player = None
        self.camera = None
        self.rendering_system = None
        self.collision_system = None
        self.combat_system = None
        self.particle_system = None
        self.networking_system = None
        self.hud = None
        self.minimap = None
        
        # Initialize menus
        self.main_menu = None
        self.pause_menu = None
        self.game_over_menu = None
        self.victory_menu = None
        self.options_menu = None
        self.current_menu = None
        self.previous_menu = None
        
        # Multiplayer
        self.is_multiplayer = False
        self.is_host = False
        self.connected_peers = []
        
        # Initialize game
        self._initialize_game()
        
    def _initialize_game(self):
        """Initialize game systems."""
        # Create world
        self.world = World(self)
        
        # Create player
        self.player = Player(
            WORLD_CENTER_X, WORLD_CENTER_Y,
            self
        )
        self.world.add_entity(self.player)
        
        # Create camera
        self.camera = Camera(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.world.camera = self.camera
        
        # Create systems
        self.rendering_system = RenderingSystem(self.world, self.camera)
        self.collision_system = CollisionSystem(self.world)
        self.combat_system = CombatSystem(self.world, self.player)
        self.particle_system = ParticleSystem(self)
        self.networking_system = NetworkingSystem(self)
        
        # Create HUD
        self.hud = HUD(self)
        
        # Create minimap
        self.minimap = Minimap(
            self.world, 
            MINIMAP_X, MINIMAP_Y, 
            MINIMAP_WIDTH, MINIMAP_HEIGHT
        )
        
        # Create menus
        self.main_menu = MainMenu(self)
        self.pause_menu = PauseMenu(self)
        self.game_over_menu = GameOverMenu(self)
        self.victory_menu = VictoryMenu(self)
        self.options_menu = OptionsMenu(self)
        
        # Set initial menu
        self.current_menu = self.main_menu
        self.state = "menu"
        
        # Seed random
        random.seed(time.time())
        
    def start_game(self):
        """Start a new game."""
        self._initialize_game()
        self.state = "playing"
        self.current_menu = None
        self.play_time = 0
        self.score = 0
        self.kills = 0
        self.coins = 0
        
        # Spawn initial entities
        self._spawn_initial_entities()
        
    def start_multiplayer(self):
        """Start a multiplayer game."""
        self.is_multiplayer = True
        self.start_game()
        self.networking_system.start()
        
    def _spawn_initial_entities(self):
        """Spawn initial entities around the player."""
        # Spawn some enemies
        for i in range(INITIAL_ENEMIES):
            x = self.player.x + random.uniform(-200, 200)
            y = self.player.y + random.uniform(-200, 200)
            enemy_type = random.choice(["grunt", "archer", "tank"])
            enemy = create_enemy(x, y, enemy_type)
            self.world.add_entity(enemy)
        
        # Spawn some items
        for i in range(INITIAL_ITEMS):
            x = self.player.x + random.uniform(-150, 150)
            y = self.player.y + random.uniform(-150, 150)
            item_type = random.choice(["coin", "health_potion"])
            item = create_item(x, y, item_type)
            self.world.add_entity(item)
            
    def pause(self):
        """Pause the game."""
        if self.state == "playing":
            self.state = "paused"
            self.current_menu = self.pause_menu
            self.current_menu.alpha = 0
            self.current_menu.target_alpha = 255
            
    def resume(self):
        """Resume the game."""
        if self.state == "paused":
            self.state = "playing"
            self.current_menu = None
            
    def show_options(self):
        """Show options menu."""
        self.previous_menu = self.current_menu
        self.current_menu = self.options_menu
        self.current_menu.alpha = 0
        self.current_menu.target_alpha = 255
        
    def return_to_previous_menu(self):
        """Return to the previous menu."""
        if self.previous_menu:
            self.current_menu = self.previous_menu
            self.previous_menu = None
            self.current_menu.alpha = 0
            self.current_menu.target_alpha = 255
        else:
            self.current_menu = None
            self.state = "playing"
            
    def return_to_main_menu(self):
        """Return to the main menu."""
        self.state = "menu"
        self.current_menu = self.main_menu
        self.current_menu.alpha = 0
        self.current_menu.target_alpha = 255
        self.previous_menu = None
        
    def game_over(self):
        """Game over."""
        self.state = "game_over"
        self.current_menu = self.game_over_menu
        self.current_menu.alpha = 0
        self.current_menu.target_alpha = 255
        
    def victory(self):
        """Victory."""
        self.state = "victory"
        self.current_menu = self.victory_menu
        self.current_menu.alpha = 0
        self.current_menu.target_alpha = 255
        
    def restart(self):
        """Restart the game."""
        self.start_game()
        
    def quit(self):
        """Quit the game."""
        self.running = False
        
    def save_game(self):
        """Save the game."""
        # Save game state
        save_data = {
            'player_x': self.player.x,
            'player_y': self.player.y,
            'player_health': self.player.health,
            'player_level': self.player.level,
            'player_xp': self.player.xp,
            'score': self.score,
            'kills': self.kills,
            'coins': self.coins,
            'play_time': self.play_time,
        }
        
        # Save to file
        import json
        with open('savegame.json', 'w') as f:
            json.dump(save_data, f)
        
        # Show notification
        self.hud.add_notification("Game Saved", GREEN)
        
    def load_game(self):
        """Load the game."""
        try:
            import json
            with open('savegame.json', 'r') as f:
                save_data = json.load(f)
            
            # Restore game state
            self.player.x = save_data.get('player_x', WORLD_CENTER_X)
            self.player.y = save_data.get('player_y', WORLD_CENTER_Y)
            self.player.health = save_data.get('player_health', PLAYER_MAX_HEALTH)
            self.player.level = save_data.get('player_level', 1)
            self.player.xp = save_data.get('player_xp', 0)
            self.score = save_data.get('score', 0)
            self.kills = save_data.get('kills', 0)
            self.coins = save_data.get('coins', 0)
            self.play_time = save_data.get('play_time', 0)
            
            # Show notification
            self.hud.add_notification("Game Loaded", GREEN)
            
        except FileNotFoundError:
            self.hud.add_notification("No save file found", RED)
        except Exception as e:
            self.hud.add_notification(f"Error loading: {e}", RED)
            
    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)
                
    def _handle_keydown(self, event):
        """Handle key down events."""
        if event.key == pygame.K_ESCAPE:
            if self.state == "playing":
                self.pause()
            elif self.state == "paused":
                self.resume()
            elif self.state == "menu":
                self.running = False
                
        elif event.key == pygame.K_p:
            self.pause()
            
        elif event.key == pygame.K_F1:
            # Toggle debug info
            self.hud.show_debug = not self.hud.show_debug
            
        elif event.key == pygame.K_F2:
            # Save game
            self.save_game()
            
        elif event.key == pygame.K_F3:
            # Load game
            self.load_game()
            
        # Player movement
        if self.state == "playing":
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.player.moving_up = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.player.moving_down = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.player.moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.player.moving_right = True
            if event.key == pygame.K_SPACE:
                self.player.jump()
            if event.key == pygame.K_LSHIFT:
                self.player.running = True
            if event.key == pygame.K_LCTRL:
                self.player.dashing = True
                
            # Combat
            if event.key == pygame.K_j:
                self.player.light_attack()
            if event.key == pygame.K_k:
                self.player.heavy_attack()
            if event.key == pygame.K_l:
                self.player.block()
            if event.key == pygame.K_i:
                self.player.use_ability(0)
            if event.key == pygame.K_o:
                self.player.use_ability(1)
            if event.key == pygame.K_u:
                self.player.use_ability(2)
                
    def _handle_keyup(self, event):
        """Handle key up events."""
        if self.state == "playing":
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.player.moving_up = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.player.moving_down = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.player.moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.player.moving_right = False
            if event.key == pygame.K_LSHIFT:
                self.player.running = False
            if event.key == pygame.K_LCTRL:
                self.player.dashing = False
                
    def _handle_mouse_down(self, event):
        """Handle mouse down events."""
        if event.button == 1:  # Left click
            if self.state == "playing":
                # Player attack
                self.player.light_attack()
                
    def _handle_mouse_up(self, event):
        """Handle mouse up events."""
        pass
        
    def update(self, dt):
        """Update game state."""
        if self.state == "playing":
            self._update_playing(dt)
        elif self.state == "paused":
            self._update_paused(dt)
        elif self.state == "menu":
            self._update_menu(dt)
        elif self.state == "game_over":
            self._update_game_over(dt)
        elif self.state == "victory":
            self._update_victory(dt)
            
        # Update play time
        if self.state == "playing":
            self.play_time += dt
            
    def _update_playing(self, dt):
        """Update game when playing."""
        # Update player
        self.player.update(dt)
        
        # Update world
        self.world.update(dt)
        
        # Update camera
        self.camera.update(dt)
        
        # Update systems
        self.collision_system.update(dt)
        self.combat_system.update(dt)
        self.particle_system.update(dt)
        self.networking_system.update(dt)
        
        # Update HUD
        self.hud.update(dt)
        
        # Update minimap
        self.minimap.update(self.player, dt)
        
        # Check for game over
        if self.player.health <= 0:
            self.game_over()
            
        # Check for victory (defeated final boss)
        if hasattr(self.world, 'final_boss_defeated') and self.world.final_boss_defeated:
            self.victory()
            
    def _update_paused(self, dt):
        """Update game when paused."""
        if self.current_menu:
            self.current_menu.update(dt)
            
    def _update_menu(self, dt):
        """Update game when in menu."""
        if self.current_menu:
            self.current_menu.update(dt)
            
    def _update_game_over(self, dt):
        """Update game over state."""
        if self.current_menu:
            self.current_menu.update(dt)
            
    def _update_victory(self, dt):
        """Update victory state."""
        if self.current_menu:
            self.current_menu.update(dt)
            
    def render(self):
        """Render the game."""
        if self.state == "playing":
            self._render_playing()
        elif self.state == "paused":
            self._render_paused()
        elif self.state == "menu":
            self._render_menu()
        elif self.state == "game_over":
            self._render_game_over()
        elif self.state == "victory":
            self._render_victory()
            
        # Flip display
        pygame.display.flip()
        
    def _render_playing(self):
        """Render game when playing."""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Render world
        self.rendering_system.render(self.screen)
        
        # Render particles
        self.particle_system.render(self.screen)
        
        # Render HUD
        self.hud.render(self.screen)
        
        # Render minimap
        self.minimap.render(self.screen)
        
    def _render_paused(self):
        """Render game when paused."""
        # Render playing state
        self._render_playing()
        
        # Render pause menu
        if self.current_menu:
            self.current_menu.render(self.screen)
            
    def _render_menu(self):
        """Render main menu."""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Render menu
        if self.current_menu:
            self.current_menu.render(self.screen)
            
    def _render_game_over(self):
        """Render game over screen."""
        # Render playing state (dimmed)
        self._render_playing()
        
        # Render overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Render menu
        if self.current_menu:
            self.current_menu.render(self.screen)
            
    def _render_victory(self):
        """Render victory screen."""
        # Render playing state (dimmed)
        self._render_playing()
        
        # Render overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Render menu
        if self.current_menu:
            self.current_menu.render(self.screen)
            
    def run(self):
        """Main game loop."""
        last_time = time.time()
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Cap delta time
            dt = min(dt, MAX_DT)
            
            # Handle events
            self.handle_events()
            
            # Update game
            self.update(dt)
            
            # Render game
            self.render()
            
            # Cap frame rate
            self.clock.tick(TARGET_FPS)
            
        # Cleanup
        self._cleanup()
        
    def _cleanup(self):
        """Clean up resources."""
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

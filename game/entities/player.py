"""
STICK REALM: SHADOW OPEN WORLD - Player Entity
Handles player movement, combat, abilities, and rendering as a stick figure
"""

import pygame
import math
import time
from config import *


class Player:
    """
    The player character - a stick figure with movement, combat, and abilities.
    All rendering is done with simple lines and circles (stick figure style).
    """
    
    def __init__(self, x, y, game):
        """
        Initialize the player at position (x, y).
        game: Reference to the main game instance
        """
        # Position and dimensions
        self.x = x
        self.y = y
        self.width = PLAYER_HITBOX_WIDTH
        self.height = PLAYER_HITBOX_HEIGHT
        self.size = PLAYER_SIZE
        
        # Movement state
        self.vx = 0
        self.vy = 0
        self.speed = PLAYER_SPEED
        self.run_speed = PLAYER_RUN_SPEED
        self.facing_right = True
        self.is_running = False
        self.is_grounded = True
        self.jump_power = 12
        self.gravity = 0.8
        self.velocity_y = 0
        
        # Combat state
        self.health = PLAYER_BASE_HEALTH
        self.max_health = PLAYER_BASE_HEALTH
        self.damage_light = PLAYER_BASE_DAMAGE_LIGHT
        self.damage_heavy = PLAYER_BASE_DAMAGE_HEAVY
        self.defense = PLAYER_DEFENSE
        
        # Level and progression
        self.level = 1
        self.xp = 0
        self.xp_to_level = BASE_XP_TO_LEVEL
        self.xp_multiplier = 1.0
        self.coins = 0
        self.score = 0
        self.kills = 0
        
        # Weapon and armour upgrades
        self.weapon_upgrades = 0
        self.armour_upgrades = 0
        
        # Combat cooldowns
        self.light_attack_cooldown = 0
        self.heavy_attack_charge = 0
        self.heavy_attack_cooldown = 0
        self.blocking = False
        self.perfect_block_window = 0
        
        # Movement cooldowns
        self.dash_cooldown = 0
        self.roll_cooldown = 0
        self.dashing = False
        self.rolling = False
        self.dash_timer = 0
        self.roll_timer = 0
        self.invincible_timer = 0
        
        # Abilities
        self.abilities = {
            'dash': True,
            'roll': True,
            'double_jump': False,
            'whirlwind': False,
            'fire_attack': False,
            'ice_attack': False,
            'shadow_dash': False
        }
        self.ability_cooldowns = {
            'whirlwind': 0,
            'fire_attack': 0,
            'ice_attack': 0,
            'shadow_dash': 0
        }
        
        # Animation state
        self.animation_state = 'idle'
        self.animation_timer = 0
        self.animation_frame = 0
        
        # Status effects
        self.status_effects = {}
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        
        # Hit detection
        self.hit_timer = 0
        self.hit_direction = 0
        
        # Reference to game
        self.game = game
        
        # Color (can be customized)
        self.color = WHITE
        
        # Stick figure body parts for animation
        self.head_radius = self.size // 5
        self.body_length = self.size // 2
        self.arm_length = self.size // 3
        self.leg_length = self.size // 2.5
        
    def update(self, dt, keys, mouse_buttons, mouse_pos):
        """
        Update player state based on time delta and input.
        dt: Time since last frame in seconds
        keys: Dictionary of pressed keys
        mouse_buttons: Mouse button states
        mouse_pos: Mouse position tuple (x, y)
        """
        # Update cooldowns and timers
        self._update_timers(dt)
        
        # Handle input
        self._handle_input(dt, keys, mouse_buttons, mouse_pos)
        
        # Apply gravity
        if not self.is_grounded:
            self.velocity_y += self.gravity * dt * 60
        
        # Update position
        self._update_position(dt)
        
        # Update animation state
        self._update_animation()
        
        # Check for level up
        self._check_level_up()
        
        # Apply status effects
        self._apply_status_effects(dt)
        
        # Clamp position to world bounds
        self.x = clamp(self.x, 0, WORLD_WIDTH_PIXELS - self.width)
        self.y = clamp(self.y, 0, WORLD_HEIGHT_PIXELS - self.height)
        
        # Update camera to follow player
        if hasattr(self.game, 'camera'):
            self.game.camera.target_x = self.x + self.width // 2
            self.game.camera.target_y = self.y + self.height // 2
    
    def _update_timers(self, dt):
        """Update all cooldown and effect timers."""
        # Combat cooldowns
        self.light_attack_cooldown = max(0, self.light_attack_cooldown - dt)
        self.heavy_attack_cooldown = max(0, self.heavy_attack_cooldown - dt)
        
        # Movement cooldowns
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        self.roll_cooldown = max(0, self.roll_cooldown - dt)
        
        # Dash/roll timers
        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False
        
        if self.rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.rolling = False
        
        # Invincibility timer
        self.invincible_timer = max(0, self.invincible_timer - dt)
        
        # Perfect block window
        self.perfect_block_window = max(0, self.perfect_block_window - dt)
        
        # Combo timer
        self.combo_timer = max(0, self.combo_timer - dt)
        if self.combo_timer <= 0:
            self.combo_count = 0
        
        # Hit timer
        self.hit_timer = max(0, self.hit_timer - dt)
        
        # Ability cooldowns
        for ability in self.ability_cooldowns:
            self.ability_cooldowns[ability] = max(0, self.ability_cooldowns[ability] - dt)
        
        # Status effects
        for effect in list(self.status_effects.keys()):
            self.status_effects[effect]['timer'] -= dt
            if self.status_effects[effect]['timer'] <= 0:
                del self.status_effects[effect]
    
    def _handle_input(self, dt, keys, mouse_buttons, mouse_pos):
        """Handle keyboard and mouse input."""
        # Reset horizontal velocity
        self.vx = 0
        
        # Movement input
        if keys.get(KEY_BINDINGS['move_left'], False):
            self.vx -= self.run_speed if self.is_running else self.speed
            self.facing_right = False
        if keys.get(KEY_BINDINGS['move_right'], False):
            self.vx += self.run_speed if self.is_running else self.speed
            self.facing_right = True
        
        self.is_running = keys.get(KEY_BINDINGS['run'], False)
        
        # Jump
        if keys.get(KEY_BINDINGS['move_up'], False) and self.is_grounded:
            self.velocity_y = -self.jump_power
            self.is_grounded = False
            # Double jump ability
            if self.abilities['double_jump'] and not keys.get(KEY_BINDINGS['move_up'], False):
                self._double_jump()
        
        # Light attack (keyboard)
        if (keys.get(KEY_BINDINGS['light_attack'], False) and 
            self.light_attack_cooldown <= 0 and not self.dashing and not self.rolling):
            self._light_attack()
        
        # Light attack (mouse)
        if (mouse_buttons.get(MOUSE_BINDINGS['light_attack'], False) and 
            self.light_attack_cooldown <= 0 and not self.dashing and not self.rolling):
            self._light_attack()
        
        # Heavy attack charge (keyboard)
        if keys.get(KEY_BINDINGS['heavy_attack_charge'], False):
            if self.heavy_attack_charge < HEAVY_ATTACK_CHARGE_TIME:
                self.heavy_attack_charge += dt
        elif self.heavy_attack_charge > 0 and self.heavy_attack_cooldown <= 0:
            self._heavy_attack()
            self.heavy_attack_charge = 0
        
        # Heavy attack charge (mouse)
        if mouse_buttons.get(MOUSE_BINDINGS['heavy_attack_charge'], False):
            if self.heavy_attack_charge < HEAVY_ATTACK_CHARGE_TIME:
                self.heavy_attack_charge += dt
        elif self.heavy_attack_charge > 0 and self.heavy_attack_cooldown <= 0:
            self._heavy_attack()
            self.heavy_attack_charge = 0
        
        # Block
        self.blocking = keys.get(KEY_BINDINGS['block'], False)
        if self.blocking:
            self.perfect_block_window = PERFECT_BLOCK_WINDOW
        
        # Dash
        if (keys.get(KEY_BINDINGS['dash'], False) and 
            self.dash_cooldown <= 0 and not self.dashing and not self.rolling):
            self._dash()
        
        # Roll
        if (keys.get(KEY_BINDINGS['roll'], False) and 
            self.roll_cooldown <= 0 and not self.dashing and not self.rolling):
            self._roll()
        
        # Abilities
        if self.abilities['whirlwind'] and keys.get(KEY_BINDINGS['whirlwind'], False):
            if self.ability_cooldowns['whirlwind'] <= 0:
                self._whirlwind_attack()
        
        if self.abilities['fire_attack'] and keys.get(KEY_BINDINGS['fire_attack'], False):
            if self.ability_cooldowns['fire_attack'] <= 0:
                self._fire_attack()
        
        if self.abilities['ice_attack'] and keys.get(KEY_BINDINGS['ice_attack'], False):
            if self.ability_cooldowns['ice_attack'] <= 0:
                self._ice_attack()
        
        if self.abilities['shadow_dash'] and keys.get(KEY_BINDINGS['shadow_dash'], False):
            if self.ability_cooldowns['shadow_dash'] <= 0:
                self._shadow_dash()
    
    def _update_position(self, dt):
        """Update player position based on velocity."""
        # Apply horizontal velocity
        if not self.dashing and not self.rolling:
            self.x += self.vx * dt * 60
        elif self.dashing:
            dash_direction = 1 if self.facing_right else -1
            self.x += dash_direction * DASH_DISTANCE * (DASH_DURATION - self.dash_timer) / DASH_DURATION * 60 * dt
        elif self.rolling:
            roll_direction = 1 if self.facing_right else -1
            self.x += roll_direction * ROLL_DISTANCE * (ROLL_DURATION - self.roll_timer) / ROLL_DURATION * 60 * dt
        
        # Apply vertical velocity
        self.y += self.velocity_y * dt * 60
        
        # Check if grounded (simplified - would use collision in full implementation)
        if self.y >= WORLD_HEIGHT_PIXELS - self.height:
            self.y = WORLD_HEIGHT_PIXELS - self.height
            self.velocity_y = 0
            self.is_grounded = True
    
    def _update_animation(self):
        """Update animation state based on current actions."""
        if self.dashing:
            self.animation_state = 'dash'
        elif self.rolling:
            self.animation_state = 'roll'
        elif self.light_attack_cooldown > LIGHT_ATTACK_COOLDOWN - 0.1:
            self.animation_state = 'attack'
        elif self.heavy_attack_charge > 0:
            self.animation_state = 'heavy_charge'
        elif self.blocking:
            self.animation_state = 'block'
        elif not self.is_grounded:
            self.animation_state = 'jump'
        elif self.vx != 0:
            self.animation_state = 'run' if self.is_running else 'walk'
        else:
            self.animation_state = 'idle'
        
        # Update animation timer
        self.animation_timer += 0.1
        if self.animation_timer >= 1:
            self.animation_timer = 0
    
    def _check_level_up(self):
        """Check if player has enough XP to level up."""
        if self.xp >= self.xp_to_level:
            self.level_up()
    
    def level_up(self):
        """Level up the player and apply bonuses."""
        self.level += 1
        self.xp -= self.xp_to_level
        self.xp_to_level = int(BASE_XP_TO_LEVEL * (1.5 ** (self.level - 1)))
        
        # Apply level up bonuses
        self.max_health += HEALTH_PER_LEVEL
        self.health = self.max_health
        self.damage_light += DAMAGE_PER_LEVEL
        self.damage_heavy += DAMAGE_PER_LEVEL
        self.speed += SPEED_PER_LEVEL
        self.run_speed = self.speed * 1.5
        self.xp_multiplier += XP_MULTIPLIER_PER_LEVEL
        
        # Unlock abilities at milestone levels
        if self.level >= ABILITY_UNLOCK_LEVELS['double_jump']:
            self.abilities['double_jump'] = True
        if self.level >= ABILITY_UNLOCK_LEVELS['whirlwind']:
            self.abilities['whirlwind'] = True
        if self.level >= ABILITY_UNLOCK_LEVELS['fire_attack']:
            self.abilities['fire_attack'] = True
        if self.level >= ABILITY_UNLOCK_LEVELS['ice_attack']:
            self.abilities['ice_attack'] = True
        if self.level >= ABILITY_UNLOCK_LEVELS['shadow_dash']:
            self.abilities['shadow_dash'] = True
        
        # Trigger level up effects
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_level_up_particles(self.x + self.width // 2, self.y + self.height // 2)
        
        # Notification
        if hasattr(self.game, 'hud'):
            self.game.hud.add_notification(f"Level {self.level}!")
    
    def _apply_status_effects(self, dt):
        """Apply active status effects."""
        for effect, data in self.status_effects.items():
            if effect == 'poison':
                self.take_damage(data['damage'] * dt * 60)
            elif effect == 'burn':
                self.take_damage(data['damage'] * dt * 60)
            elif effect == 'slow':
                self.speed = max(10, self.speed * (1 - data['amount']))
                self.run_speed = self.speed * 1.5
            elif effect == 'freeze':
                self.vx = 0
                self.velocity_y = 0
    
    # ==================== COMBAT METHODS ====================
    
    def _light_attack(self):
        """Perform a light attack."""
        self.light_attack_cooldown = LIGHT_ATTACK_COOLDOWN
        self.combo_count += 1
        self.combo_timer = 2.0  # 2 second combo window
        
        # Calculate damage with combo bonus
        damage = self.damage_light + self.weapon_upgrades * WEAPON_UPGRADE_LIGHT_DAMAGE_BONUS
        combo_bonus = self.combo_count * 0.10  # 10% per combo hit
        damage = int(damage * (1 + combo_bonus))
        
        # Create attack hitbox
        attack_range = 60
        attack_x = self.x + (self.width if self.facing_right else 0)
        attack_y = self.y + self.height // 4
        attack_width = attack_range
        attack_height = self.height // 2
        
        # Check for hits (would be handled by combat system in full implementation)
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.player_light_attack(
                self, attack_x, attack_y, attack_width, attack_height, damage
            )
        
        # Camera shake
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_LIGHT, 0.1)
    
    def _heavy_attack(self):
        """Perform a heavy attack based on charge time."""
        charge_ratio = min(1.0, self.heavy_attack_charge / HEAVY_ATTACK_CHARGE_TIME)
        damage = int((self.damage_heavy + self.weapon_upgrades * WEAPON_UPGRADE_HEAVY_DAMAGE_BONUS) * (0.5 + charge_ratio))
        
        self.heavy_attack_cooldown = HEAVY_ATTACK_COOLDOWN
        self.combo_count += 1
        self.combo_timer = 2.0
        
        # Create attack hitbox
        attack_range = 80
        attack_x = self.x + (self.width if self.facing_right else -attack_range)
        attack_y = self.y + self.height // 4
        attack_width = attack_range
        attack_height = self.height // 2
        
        # Check for hits
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.player_heavy_attack(
                self, attack_x, attack_y, attack_width, attack_height, damage
            )
        
        # Camera shake
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_HEAVY * charge_ratio, 0.2 * charge_ratio)
    
    def _whirlwind_attack(self):
        """Perform a whirlwind attack (hits all enemies around)."""
        self.ability_cooldowns['whirlwind'] = 5.0
        damage = 15 + self.weapon_upgrades * 2
        radius = 100
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.player_whirlwind_attack(
                self, self.x + self.width // 2, self.y + self.height // 2, radius, damage
            )
    
    def _fire_attack(self):
        """Perform a fire attack (creates fire projectile)."""
        self.ability_cooldowns['fire_attack'] = 3.0
        
        if hasattr(self.game, 'combat_system'):
            direction = 1 if self.facing_right else -1
            start_x = self.x + (self.width if self.facing_right else 0)
            start_y = self.y + self.height // 2
            self.game.combat_system.create_fireball(
                start_x, start_y, direction, self
            )
    
    def _ice_attack(self):
        """Perform an ice attack (slows enemies)."""
        self.ability_cooldowns['ice_attack'] = 4.0
        
        if hasattr(self.game, 'combat_system'):
            direction = 1 if self.facing_right else -1
            start_x = self.x + (self.width if self.facing_right else 0)
            start_y = self.y + self.height // 2
            self.game.combat_system.create_ice_projectile(
                start_x, start_y, direction, self
            )
    
    def _shadow_dash(self):
        """Perform a shadow dash (teleport through enemies)."""
        self.ability_cooldowns['shadow_dash'] = 8.0
        
        if hasattr(self.game, 'combat_system'):
            direction = 1 if self.facing_right else -1
            start_x = self.x + (self.width if self.facing_right else 0)
            start_y = self.y + self.height // 2
            self.game.combat_system.player_shadow_dash(
                self, start_x, start_y, direction, DASH_DISTANCE * 1.5
            )
    
    def _dash(self):
        """Perform a dash movement."""
        self.dash_cooldown = DASH_COOLDOWN
        self.dashing = True
        self.dash_timer = DASH_DURATION
        self.invincible_timer = DASH_INVINCIBILITY
        
        # Camera shake
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_LIGHT, 0.1)
    
    def _roll(self):
        """Perform a roll movement."""
        self.roll_cooldown = ROLL_COOLDOWN
        self.rolling = True
        self.roll_timer = ROLL_DURATION
        self.invincible_timer = 0.3
    
    def _double_jump(self):
        """Perform a double jump."""
        if not self.is_grounded and self.velocity_y >= 0:
            self.velocity_y = -self.jump_power * 0.9
            # Reset double jump until grounded
            temp_ability = self.abilities['double_jump']
            self.abilities['double_jump'] = False
            # Schedule re-enabling after landing
            # (In full implementation, would use a timer)
    
    # ==================== DAMAGE & HEALTH ====================
    
    def take_damage(self, amount, direction=0, knockback=100, damage_type='normal'):
        """
        Take damage from an attack.
        amount: Damage amount
        direction: Direction of attack (1 for right, -1 for left)
        knockback: Knockback force
        damage_type: Type of damage (normal, poison, burn, etc.)
        """
        if self.invincible_timer > 0:
            return
        
        # Apply defense if blocking
        if self.blocking:
            amount *= (1 - BLOCK_DAMAGE_REDUCTION)
            
            # Check for perfect block
            if self.perfect_block_window > 0:
                # Counter attack
                self._light_attack()
                return
        
        # Apply armour reduction
        amount *= (1 - self.armour_upgrades * ARMOUR_UPGRADE_DAMAGE_REDUCTION_BONUS)
        
        # Clamp minimum damage
        amount = max(1, int(amount))
        
        # Apply damage
        self.health -= amount
        self.hit_timer = 0.5
        self.hit_direction = direction
        self.invincible_timer = 0.5
        self.combo_count = 0  # Reset combo on hit
        
        # Knockback
        if knockback > 0:
            self.vx = direction * knockback * 0.5
            if direction != 0:
                self.velocity_y = -5
        
        # Status effects from damage type
        if damage_type == 'poison':
            self.add_status_effect('poison', {'damage': 5, 'timer': 5.0})
        elif damage_type == 'burn':
            self.add_status_effect('burn', {'damage': 8, 'timer': 3.0})
        elif damage_type == 'freeze':
            self.add_status_effect('freeze', {'timer': 2.0})
        elif damage_type == 'slow':
            self.add_status_effect('slow', {'amount': 0.5, 'timer': 3.0})
        
        # Check for death
        if self.health <= 0:
            self.die()
        
        # Camera shake
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_LIGHT, 0.1)
        
        # Blood particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_blood_particles(
                self.x + self.width // 2, self.y + self.height // 2, direction
            )
    
    def heal(self, amount):
        """Heal the player by the specified amount."""
        self.health = min(self.max_health, self.health + amount)
        
        # Heal particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_heal_particles(
                self.x + self.width // 2, self.y
            )
    
    def add_status_effect(self, effect_type, data):
        """Add a status effect to the player."""
        # Don't overwrite stronger effects
        if effect_type in self.status_effects:
            if data.get('damage', 0) > self.status_effects[effect_type].get('damage', 0):
                self.status_effects[effect_type] = data
        else:
            self.status_effects[effect_type] = data
    
    def die(self):
        """Handle player death."""
        self.health = 0
        self.animation_state = 'death'
        
        # Trigger game over
        if hasattr(self.game, 'game_over'):
            self.game.game_over()
        
        # Death particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_death_particles(
                self.x + self.width // 2, self.y + self.height // 2
            )
        
        # Camera effect
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_HEAVY, 1.0)
    
    def respawn(self, x, y):
        """Respawn the player at the specified position."""
        self.x = x
        self.y = y
        self.health = self.max_health
        self.animation_state = 'idle'
        self.velocity_y = 0
        self.vx = 0
        self.invincible_timer = 1.0  # Brief invincibility after respawn
    
    # ==================== ITEM COLLECTION ====================
    
    def collect_coins(self, amount):
        """Add coins to player's total."""
        self.coins += amount
        self.score += amount * 10
    
    def collect_xp(self, amount):
        """Add XP to player's total."""
        self.xp += int(amount * self.xp_multiplier)
        self.score += int(amount * 2)
    
    def collect_weapon_upgrade(self):
        """Collect a weapon upgrade."""
        self.weapon_upgrades += 1
        self.score += 100
    
    def collect_armour_upgrade(self):
        """Collect an armour upgrade."""
        self.armour_upgrades += 1
        self.max_health += ARMOUR_UPGRADE_HEALTH_BONUS
        self.health = self.max_health
        self.score += 100
    
    def use_health_potion(self):
        """Use a health potion."""
        self.heal(HEALTH_POTION_HEAL_AMOUNT)
        return True  # Return True if potion was used
    
    # ==================== RENDERING ====================
    
    def render(self, surface, camera):
        """
        Render the player as a stick figure.
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
        
        # Center position for stick figure
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 4  # Stick figure is taller than hitbox
        
        # Determine color based on state
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            color = WHITE  # Flash white when invincible
        elif self.hit_timer > 0:
            color = RED  # Flash red when hit
        else:
            color = self.color
        
        # Draw stick figure based on animation state
        self._draw_stick_figure(surface, center_x, center_y, color)
        
        # Draw weapon if attacking
        if self.animation_state == 'attack' or self.animation_state == 'heavy_charge':
            self._draw_weapon(surface, center_x, center_y, color)
    
    def _draw_stick_figure(self, surface, center_x, center_y, color):
        """Draw the stick figure body."""
        # Body parts
        head_radius = self.head_radius
        body_length = self.body_length
        arm_length = self.arm_length
        leg_length = self.leg_length
        
        # Head (circle)
        pygame.draw.circle(surface, color, (center_x, center_y - body_length // 2), head_radius, 2)
        
        # Draw eyes (simple)
        eye_offset = head_radius // 3
        eye_y = center_y - body_length // 2
        if self.facing_right:
            left_eye_x = center_x - eye_offset
            right_eye_x = center_x + eye_offset
        else:
            left_eye_x = center_x + eye_offset
            right_eye_x = center_x - eye_offset
        
        # Eyes are small circles
        pygame.draw.circle(surface, color, (left_eye_x, eye_y - eye_offset // 2), head_radius // 4, 1)
        pygame.draw.circle(surface, color, (right_eye_x, eye_y - eye_offset // 2), head_radius // 4, 1)
        
        # Mouth (line that changes based on state)
        mouth_y = center_y - body_length // 2 + head_radius // 2
        if self.animation_state == 'attack':
            # Open mouth when attacking
            if self.facing_right:
                pygame.draw.line(surface, color, (center_x, mouth_y), 
                                (center_x + head_radius // 2, mouth_y + head_radius // 2), 1)
            else:
                pygame.draw.line(surface, color, (center_x, mouth_y), 
                                (center_x - head_radius // 2, mouth_y + head_radius // 2), 1)
        else:
            # Neutral mouth
            pygame.draw.line(surface, color, 
                            (center_x - head_radius // 3, mouth_y), 
                            (center_x + head_radius // 3, mouth_y), 1)
        
        # Body (vertical line)
        body_top = center_y - body_length // 2 + head_radius
        body_bottom = center_y + body_length // 2
        pygame.draw.line(surface, color, (center_x, body_top), (center_x, body_bottom), 2)
        
        # Arms (change position based on animation)
        shoulder_y = center_y - body_length // 4
        
        if self.animation_state == 'idle':
            # Arms down at sides
            left_arm_end = (center_x - arm_length, shoulder_y + arm_length // 2)
            right_arm_end = (center_x + arm_length, shoulder_y + arm_length // 2)
        elif self.animation_state == 'walk' or self.animation_state == 'run':
            # Arms swinging
            swing_offset = arm_length // 2 * math.sin(self.animation_timer * math.pi * 2)
            left_arm_end = (center_x - arm_length, shoulder_y + swing_offset)
            right_arm_end = (center_x + arm_length, shoulder_y - swing_offset)
        elif self.animation_state == 'attack':
            # One arm extended forward, one pulled back
            if self.facing_right:
                left_arm_end = (center_x - arm_length, shoulder_y)
                right_arm_end = (center_x + arm_length * 1.5, shoulder_y)
            else:
                left_arm_end = (center_x - arm_length * 1.5, shoulder_y)
                right_arm_end = (center_x + arm_length, shoulder_y)
        elif self.animation_state == 'heavy_charge':
            # Both arms pulled back
            charge_ratio = self.heavy_attack_charge / HEAVY_ATTACK_CHARGE_TIME
            arm_offset = arm_length * charge_ratio
            if self.facing_right:
                left_arm_end = (center_x - arm_offset, shoulder_y)
                right_arm_end = (center_x + arm_offset, shoulder_y)
            else:
                left_arm_end = (center_x - arm_offset, shoulder_y)
                right_arm_end = (center_x + arm_offset, shoulder_y)
        elif self.animation_state == 'block':
            # Arms crossed in front
            left_arm_end = (center_x + arm_length // 2, shoulder_y + arm_length // 2)
            right_arm_end = (center_x - arm_length // 2, shoulder_y - arm_length // 2)
        elif self.animation_state == 'dash':
            # Arms back
            left_arm_end = (center_x - arm_length * 1.5, shoulder_y)
            right_arm_end = (center_x + arm_length * 1.5, shoulder_y)
        elif self.animation_state == 'roll':
            # Curled up
            left_arm_end = (center_x - arm_length // 2, shoulder_y + arm_length)
            right_arm_end = (center_x + arm_length // 2, shoulder_y + arm_length)
        elif self.animation_state == 'jump':
            # Arms up
            left_arm_end = (center_x - arm_length // 2, shoulder_y - arm_length)
            right_arm_end = (center_x + arm_length // 2, shoulder_y - arm_length)
        else:
            # Default idle
            left_arm_end = (center_x - arm_length, shoulder_y + arm_length // 2)
            right_arm_end = (center_x + arm_length, shoulder_y + arm_length // 2)
        
        # Draw arms
        pygame.draw.line(surface, color, (center_x, shoulder_y), left_arm_end, 2)
        pygame.draw.line(surface, color, (center_x, shoulder_y), right_arm_end, 2)
        
        # Legs (change position based on animation)
        hip_y = center_y + body_length // 4
        
        if self.animation_state == 'walk' or self.animation_state == 'run':
            # Legs alternating
            swing_offset = leg_length // 3 * math.sin(self.animation_timer * math.pi * 2 + math.pi)
            left_leg_end = (center_x - leg_length // 2, hip_y + leg_length + swing_offset)
            right_leg_end = (center_x + leg_length // 2, hip_y + leg_length - swing_offset)
        elif self.animation_state == 'jump':
            # Legs together
            left_leg_end = (center_x - leg_length // 3, hip_y + leg_length)
            right_leg_end = (center_x + leg_length // 3, hip_y + leg_length)
        elif self.animation_state == 'dash':
            # One leg forward, one back
            if self.facing_right:
                left_leg_end = (center_x - leg_length // 2, hip_y + leg_length)
                right_leg_end = (center_x + leg_length, hip_y)
            else:
                left_leg_end = (center_x - leg_length, hip_y)
                right_leg_end = (center_x + leg_length // 2, hip_y + leg_length)
        else:
            # Default standing
            left_leg_end = (center_x - leg_length // 2, hip_y + leg_length)
            right_leg_end = (center_x + leg_length // 2, hip_y + leg_length)
        
        # Draw legs
        pygame.draw.line(surface, color, (center_x, hip_y), left_leg_end, 2)
        pygame.draw.line(surface, color, (center_x, hip_y), right_leg_end, 2)
    
    def _draw_weapon(self, surface, center_x, center_y, color):
        """Draw the player's weapon."""
        # Simple sword as a rectangle/line
        if self.animation_state == 'attack':
            # Extended sword
            sword_length = 40
            if self.facing_right:
                sword_start = (center_x + self.arm_length * 1.2, center_y - self.body_length // 4)
                sword_end = (center_x + self.arm_length * 1.2 + sword_length, center_y - self.body_length // 4)
            else:
                sword_start = (center_x - self.arm_length * 1.2, center_y - self.body_length // 4)
                sword_end = (center_x - self.arm_length * 1.2 - sword_length, center_y - self.body_length // 4)
            
            pygame.draw.line(surface, color, sword_start, sword_end, 3)
            
            # Sword tip
            pygame.draw.circle(surface, color, sword_end, 3, 0)
    
    def get_hitbox(self):
        """Get the player's hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self):
        """Get the center position of the player."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def is_invincible(self):
        """Check if player is currently invincible."""
        return self.invincible_timer > 0
    
    def get_stats(self):
        """Get player stats as a dictionary."""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'level': self.level,
            'xp': self.xp,
            'xp_to_level': self.xp_to_level,
            'coins': self.coins,
            'score': self.score,
            'kills': self.kills,
            'damage_light': self.damage_light,
            'damage_heavy': self.damage_heavy,
            'speed': self.speed,
            'weapon_upgrades': self.weapon_upgrades,
            'armour_upgrades': self.armour_upgrades
        }

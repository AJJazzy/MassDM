"""
STICK REALM: SHADOW OPEN WORLD - Enemy Entities
All enemy types as stick figures with AI behavior
"""

import pygame
import math
import random
from config import *


class Enemy:
    """
    Base enemy class - a stick figure with AI behavior.
    All enemies are rendered as simple stick figures.
    """
    
    def __init__(self, x, y, enemy_type, game):
        """
        Initialize an enemy at position (x, y).
        enemy_type: Type of enemy ('grunt', 'archer', 'tank', etc.)
        game: Reference to the main game instance
        """
        # Get enemy type configuration
        self.type = enemy_type
        self.config = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES['grunt'])
        
        # Position and dimensions
        self.x = x
        self.y = y
        self.base_size = ENEMY_BASE_SIZE
        self.size = int(self.base_size * self.config['size'])
        self.width = int(self.size * 0.7)
        self.height = self.size
        
        # Movement
        self.vx = 0
        self.vy = 0
        self.speed = ENEMY_BASE_SPEED * self.config['speed']
        self.facing_right = True
        self.is_grounded = True
        self.gravity = 0.8
        self.velocity_y = 0
        self.jump_power = 8
        
        # Combat
        self.health = int(ENEMY_BASE_HEALTH * self.config['health'])
        self.max_health = self.health
        self.damage = int(ENEMY_BASE_DAMAGE * self.config['damage'])
        self.aggro_range = self.config['aggro_range']
        self.attack_range = self.config.get('attack_range', ENEMY_ATTACK_RANGE_MELEE)
        self.attack_cooldown = self.config['attack_cooldown']
        self.attack_timer = 0
        
        # AI state
        self.state = 'patrol'  # patrol, chase, attack, flee, special
        self.patrol_points = []
        self.patrol_index = 0
        self.target_x = x
        self.target_y = y
        self.chase_target = None  # Player to chase
        
        # Special properties
        self.knockback_resistance = self.config.get('knockback_resistance', 0)
        self.critical_chance = self.config.get('critical_chance', 0)
        self.critical_multiplier = self.config.get('critical_multiplier', 1.0)
        
        # Despawning
        self.spawn_distance = SPAWN_DISTANCE
        self.despawn_distance = ENEMY_DESPAWN_DISTANCE
        self.despawn_timer = 0
        
        # Animation
        self.animation_state = 'idle'
        self.animation_timer = 0
        
        # Status effects
        self.status_effects = {}
        
        # Hit detection
        self.hit_timer = 0
        self.hit_direction = 0
        
        # Reference to game
        self.game = game
        
        # Color
        self.color = self.config['color']
        
        # Stick figure body parts
        self.head_radius = self.size // 6
        self.body_length = self.size // 2.5
        self.arm_length = self.size // 3.5
        self.leg_length = self.size // 3
        
        # Initialize patrol points
        self._init_patrol()
    
    def update(self, dt, player):
        """
        Update enemy state based on time delta and player position.
        dt: Time since last frame in seconds
        player: Reference to the player
        """
        # Update timers
        self._update_timers(dt)
        
        # Check distance to player
        player_center = player.get_center()
        distance_to_player = distance(
            self.x + self.width // 2, self.y + self.height // 2,
            player_center[0], player_center[1]
        )
        
        # Check if should despawn
        if distance_to_player > self.despawn_distance:
            self.despawn_timer += dt
            if self.despawn_timer > 2.0:  # 2 second grace period
                return False  # Signal to remove this enemy
        else:
            self.despawn_timer = 0
        
        # Update AI state based on distance
        self._update_ai_state(dt, player, distance_to_player)
        
        # Apply gravity
        if not self.is_grounded:
            self.velocity_y += self.gravity * dt * 60
        
        # Update position
        self._update_position(dt)
        
        # Update animation
        self._update_animation()
        
        # Apply status effects
        self._apply_status_effects(dt)
        
        # Clamp position to world bounds
        self.x = clamp(self.x, 0, WORLD_WIDTH_PIXELS - self.width)
        self.y = clamp(self.y, 0, WORLD_HEIGHT_PIXELS - self.height)
        
        return True  # Keep this enemy
    
    def _update_timers(self, dt):
        """Update all timers."""
        self.attack_timer = max(0, self.attack_timer - dt)
        self.hit_timer = max(0, self.hit_timer - dt)
        
        # Status effects
        for effect in list(self.status_effects.keys()):
            self.status_effects[effect]['timer'] -= dt
            if self.status_effects[effect]['timer'] <= 0:
                del self.status_effects[effect]
    
    def _update_ai_state(self, dt, player, distance_to_player):
        """Update AI state based on player distance and behavior."""
        player_center = player.get_center()
        
        # Check if player is in aggro range
        if distance_to_player <= self.aggro_range:
            self.chase_target = player
            
            # Flee if health is low (below 30%)
            if self.health / self.max_health < 0.3 and random.random() < 0.1:
                self.state = 'flee'
            else:
                # Chase or attack
                if distance_to_player <= self.attack_range:
                    self.state = 'attack'
                else:
                    self.state = 'chase'
        else:
            # Patrol if no target
            if self.chase_target is None:
                self.state = 'patrol'
            else:
                # Continue chasing for a bit even if player leaves aggro range
                if distance_to_player > self.aggro_range * 1.5:
                    self.chase_target = None
                    self.state = 'patrol'
        
        # Execute state behavior
        if self.state == 'patrol':
            self._patrol(dt)
        elif self.state == 'chase':
            self._chase(dt, player_center)
        elif self.state == 'attack':
            self._attack(dt, player)
        elif self.state == 'flee':
            self._flee(dt, player_center)
        elif self.state == 'special':
            self._special(dt, player)
    
    def _patrol(self, dt):
        """Patrol behavior - move between patrol points."""
        if not self.patrol_points:
            # Just stand still if no patrol points
            self.vx = 0
            return
        
        # Move toward current patrol point
        target = self.patrol_points[self.patrol_index]
        dx = target[0] - (self.x + self.width // 2)
        dy = target[1] - (self.y + self.height // 2)
        
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 10:  # Reached patrol point
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
            return
        
        # Move toward target
        self.vx = (dx / dist) * self.speed * 0.5  # Patrol at half speed
        
        # Face direction of movement
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
    
    def _chase(self, dt, player_center):
        """Chase behavior - move toward player."""
        dx = player_center[0] - (self.x + self.width // 2)
        dy = player_center[1] - (self.y + self.height // 2)
        
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 10:
            self.vx = 0
            return
        
        # Move toward player
        self.vx = (dx / dist) * self.speed
        
        # Face direction of movement
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        
        # Jump if player is above and we're on ground
        if dy < -50 and self.is_grounded and random.random() < 0.05:
            self.velocity_y = -self.jump_power
            self.is_grounded = False
    
    def _attack(self, dt, player):
        """Attack behavior - attack the player."""
        player_center = player.get_center()
        dx = player_center[0] - (self.x + self.width // 2)
        
        # Face player
        if dx > 0:
            self.facing_right = True
        else:
            self.facing_right = False
        
        # Check if can attack
        if self.attack_timer <= 0:
            self._perform_attack(player)
            self.attack_timer = self.attack_cooldown
    
    def _flee(self, dt, player_center):
        """Flee behavior - run away from player."""
        dx = (self.x + self.width // 2) - player_center[0]
        dy = (self.y + self.height // 2) - player_center[1]
        
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 10:
            self.vx = 0
            return
        
        # Move away from player
        self.vx = (dx / dist) * self.speed * 1.5  # Flee at 1.5x speed
        
        # Face direction of movement
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
    
    def _special(self, dt, player):
        """Special behavior - override in subclasses for special attacks."""
        pass
    
    def _perform_attack(self, player):
        """Perform an attack on the player."""
        # Default melee attack
        if hasattr(self.game, 'combat_system'):
            # Create attack hitbox
            attack_x = self.x + (self.width if self.facing_right else 0)
            attack_y = self.y + self.height // 4
            attack_width = self.attack_range
            attack_height = self.height // 2
            
            # Check for critical hit
            is_critical = random.random() < self.critical_chance
            damage = self.damage
            if is_critical:
                damage = int(damage * self.critical_multiplier)
            
            self.game.combat_system.enemy_attack(
                self, attack_x, attack_y, attack_width, attack_height, damage
            )
    
    def _update_position(self, dt):
        """Update position based on velocity."""
        # Apply horizontal velocity
        self.x += self.vx * dt * 60
        
        # Apply vertical velocity
        self.y += self.velocity_y * dt * 60
        
        # Check if grounded
        if self.y >= WORLD_HEIGHT_PIXELS - self.height:
            self.y = WORLD_HEIGHT_PIXELS - self.height
            self.velocity_y = 0
            self.is_grounded = True
    
    def _update_animation(self):
        """Update animation state based on current actions."""
        if self.hit_timer > 0:
            self.animation_state = 'hit'
        elif self.attack_timer > self.attack_cooldown - 0.1:
            self.animation_state = 'attack'
        elif self.vx != 0:
            self.animation_state = 'walk'
        else:
            self.animation_state = 'idle'
        
        # Update animation timer
        self.animation_timer += 0.1
        if self.animation_timer >= 1:
            self.animation_timer = 0
    
    def _apply_status_effects(self, dt):
        """Apply active status effects."""
        for effect, data in self.status_effects.items():
            if effect == 'poison':
                self.take_damage(data['damage'] * dt * 60)
            elif effect == 'burn':
                self.take_damage(data['damage'] * dt * 60)
            elif effect == 'slow':
                self.speed = max(10, self.speed * (1 - data['amount']))
            elif effect == 'freeze':
                self.vx = 0
                self.velocity_y = 0
    
    def _init_patrol(self):
        """Initialize patrol points around spawn location."""
        # Create a small patrol area around spawn point
        self.patrol_points = [
            (self.x, self.y),
            (self.x + 100, self.y),
            (self.x + 100, self.y + 50),
            (self.x, self.y + 50)
        ]
        self.patrol_index = 0
    
    # ==================== COMBAT ====================
    
    def take_damage(self, amount, direction=0, knockback=100, damage_type='normal'):
        """
        Take damage from an attack.
        amount: Damage amount
        direction: Direction of attack (1 for right, -1 for left)
        knockback: Knockback force
        damage_type: Type of damage
        """
        # Apply knockback resistance
        knockback *= (1 - self.knockback_resistance)
        
        # Clamp minimum damage
        amount = max(1, int(amount))
        
        # Apply damage
        self.health -= amount
        self.hit_timer = 0.3
        self.hit_direction = direction
        
        # Knockback
        if knockback > 0:
            self.vx = direction * knockback * 0.3
            if direction != 0:
                self.velocity_y = -3
        
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
        
        # Blood particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_blood_particles(
                self.x + self.width // 2, self.y + self.height // 2, direction
            )
    
    def add_status_effect(self, effect_type, data):
        """Add a status effect to the enemy."""
        if effect_type in self.status_effects:
            if data.get('damage', 0) > self.status_effects[effect_type].get('damage', 0):
                self.status_effects[effect_type] = data
        else:
            self.status_effects[effect_type] = data
    
    def die(self):
        """Handle enemy death - drop items and trigger effects."""
        self.animation_state = 'death'
        
        # Drop items
        self._drop_items()
        
        # Give XP to player
        if hasattr(self.game, 'player'):
            self.game.player.collect_xp(XP_REWARDS.get(self.type, 20))
            self.game.player.kills += 1
        
        # Death particles
        if hasattr(self.game, 'particle_system'):
            self.game.particle_system.create_death_particles(
                self.x + self.width // 2, self.y + self.height // 2
            )
        
        # Camera shake
        if hasattr(self.game, 'camera'):
            self.game.camera.shake(CAMERA_SHAKE_INTENSITY_LIGHT, 0.1)
    
    def _drop_items(self):
        """Drop items based on enemy type."""
        config = self.config
        
        # Always drop coins
        coins = config.get('drop_coins', 20)
        if hasattr(self.game, 'world'):
            self.game.world.add_item(
                'coin', self.x + self.width // 2, self.y + self.height // 2, coins
            )
        
        # Drop health potion
        if random.random() < config.get('health_potion_chance', 0):
            if hasattr(self.game, 'world'):
                self.game.world.add_item(
                    'health_potion', self.x + self.width // 2, self.y + self.height // 2
                )
        
        # Drop weapon upgrade
        if random.random() < config.get('weapon_upgrade_chance', 0):
            if hasattr(self.game, 'world'):
                self.game.world.add_item(
                    'weapon_upgrade', self.x + self.width // 2, self.y + self.height // 2
                )
        
        # Drop armour upgrade
        if random.random() < config.get('armour_upgrade_chance', 0):
            if hasattr(self.game, 'world'):
                self.game.world.add_item(
                    'armour_upgrade', self.x + self.width // 2, self.y + self.height // 2
                )
    
    # ==================== RENDERING ====================
    
    def render(self, surface, camera):
        """
        Render the enemy as a stick figure.
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
        center_y = screen_y + self.height // 4
        
        # Determine color based on state
        if self.hit_timer > 0:
            color = RED  # Flash red when hit
        else:
            color = self.color
        
        # Draw stick figure
        self._draw_stick_figure(surface, center_x, center_y, color)
        
        # Draw weapon if applicable
        if self.type == 'archer':
            self._draw_bow(surface, center_x, center_y, color)
        elif self.type in ['tank', 'knight']:
            self._draw_sword(surface, center_x, center_y, color)
        elif self.type == 'mage':
            self._draw_staff(surface, center_x, center_y, color)
    
    def _draw_stick_figure(self, surface, center_x, center_y, color):
        """Draw the stick figure body."""
        head_radius = self.head_radius
        body_length = self.body_length
        arm_length = self.arm_length
        leg_length = self.leg_length
        
        # Head (circle)
        pygame.draw.circle(surface, color, (center_x, center_y - body_length // 2), head_radius, 2)
        
        # Eyes (different for different enemy types)
        eye_offset = head_radius // 3
        eye_y = center_y - body_length // 2
        
        if self.type == 'assassin':
            # Assassin has sharp eyes
            if self.facing_right:
                left_eye_x = center_x - eye_offset
                right_eye_x = center_x + eye_offset
            else:
                left_eye_x = center_x + eye_offset
                right_eye_x = center_x - eye_offset
            
            pygame.draw.line(surface, color, (left_eye_x, eye_y), 
                           (left_eye_x - 3 if self.facing_right else left_eye_x + 3, eye_y - 3), 1)
            pygame.draw.line(surface, color, (right_eye_x, eye_y), 
                           (right_eye_x - 3 if self.facing_right else right_eye_x + 3, eye_y - 3), 1)
        else:
            # Normal eyes
            if self.facing_right:
                left_eye_x = center_x - eye_offset
                right_eye_x = center_x + eye_offset
            else:
                left_eye_x = center_x + eye_offset
                right_eye_x = center_x - eye_offset
            
            pygame.draw.circle(surface, color, (left_eye_x, eye_y), head_radius // 4, 1)
            pygame.draw.circle(surface, color, (right_eye_x, eye_y), head_radius // 4, 1)
        
        # Mouth (different based on state)
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
        
        # Arms
        shoulder_y = center_y - body_length // 4
        
        if self.animation_state == 'attack':
            # Attack animation
            if self.facing_right:
                left_arm_end = (center_x - arm_length, shoulder_y)
                right_arm_end = (center_x + arm_length * 1.5, shoulder_y)
            else:
                left_arm_end = (center_x - arm_length * 1.5, shoulder_y)
                right_arm_end = (center_x + arm_length, shoulder_y)
        elif self.animation_state == 'hit':
            # Hit animation
            left_arm_end = (center_x - arm_length * 0.5, shoulder_y + arm_length)
            right_arm_end = (center_x + arm_length * 0.5, shoulder_y + arm_length)
        else:
            # Default
            left_arm_end = (center_x - arm_length, shoulder_y + arm_length // 2)
            right_arm_end = (center_x + arm_length, shoulder_y + arm_length // 2)
        
        pygame.draw.line(surface, color, (center_x, shoulder_y), left_arm_end, 2)
        pygame.draw.line(surface, color, (center_x, shoulder_y), right_arm_end, 2)
        
        # Legs
        hip_y = center_y + body_length // 4
        
        if self.animation_state == 'walk':
            # Walking animation
            swing_offset = leg_length // 3 * math.sin(self.animation_timer * math.pi * 2)
            left_leg_end = (center_x - leg_length // 2, hip_y + leg_length + swing_offset)
            right_leg_end = (center_x + leg_length // 2, hip_y + leg_length - swing_offset)
        else:
            # Default standing
            left_leg_end = (center_x - leg_length // 2, hip_y + leg_length)
            right_leg_end = (center_x + leg_length // 2, hip_y + leg_length)
        
        pygame.draw.line(surface, color, (center_x, hip_y), left_leg_end, 2)
        pygame.draw.line(surface, color, (center_x, hip_y), right_leg_end, 2)
    
    def _draw_bow(self, surface, center_x, center_y, color):
        """Draw a bow for archer enemies."""
        if self.animation_state == 'attack':
            # Bow drawn
            if self.facing_right:
                bow_start = (center_x + self.arm_length * 1.2, center_y - self.body_length // 4)
                bow_end = (center_x + self.arm_length * 1.8, center_y - self.body_length // 4)
                bow_string = (center_x + self.arm_length * 1.5, center_y - self.body_length // 4 - 10)
            else:
                bow_start = (center_x - self.arm_length * 1.2, center_y - self.body_length // 4)
                bow_end = (center_x - self.arm_length * 1.8, center_y - self.body_length // 4)
                bow_string = (center_x - self.arm_length * 1.5, center_y - self.body_length // 4 - 10)
            
            pygame.draw.line(surface, color, bow_start, bow_end, 2)
            pygame.draw.line(surface, color, bow_start, bow_string, 1)
            pygame.draw.line(surface, color, bow_end, bow_string, 1)
    
    def _draw_sword(self, surface, center_x, center_y, color):
        """Draw a sword for tank/knight enemies."""
        if self.animation_state == 'attack':
            sword_length = 30
            if self.facing_right:
                sword_start = (center_x + self.arm_length * 1.2, center_y - self.body_length // 4)
                sword_end = (center_x + self.arm_length * 1.2 + sword_length, center_y - self.body_length // 4)
            else:
                sword_start = (center_x - self.arm_length * 1.2, center_y - self.body_length // 4)
                sword_end = (center_x - self.arm_length * 1.2 - sword_length, center_y - self.body_length // 4)
            
            pygame.draw.line(surface, color, sword_start, sword_end, 3)
            pygame.draw.circle(surface, color, sword_end, 3, 0)
    
    def _draw_staff(self, surface, center_x, center_y, color):
        """Draw a staff for mage enemies."""
        staff_length = 40
        if self.facing_right:
            staff_start = (center_x + self.arm_length * 1.2, center_y - self.body_length // 4)
            staff_end = (center_x + self.arm_length * 1.2 + staff_length, center_y - self.body_length // 4)
        else:
            staff_start = (center_x - self.arm_length * 1.2, center_y - self.body_length // 4)
            staff_end = (center_x - self.arm_length * 1.2 - staff_length, center_y - self.body_length // 4)
        
        pygame.draw.line(surface, color, staff_start, staff_end, 2)
        
        # Staff orb
        if self.animation_state == 'attack':
            orb_radius = 5
            if self.facing_right:
                orb_x = staff_end[0] + orb_radius
            else:
                orb_x = staff_end[0] - orb_radius
            pygame.draw.circle(surface, BLUE, (orb_x, staff_end[1]), orb_radius, 0)
    
    def get_hitbox(self):
        """Get the enemy's hitbox rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self):
        """Get the center position of the enemy."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_stats(self):
        """Get enemy stats as a dictionary."""
        return {
            'type': self.type,
            'health': self.health,
            'max_health': self.max_health,
            'damage': self.damage,
            'speed': self.speed,
            'state': self.state
        }


# ==================== SPECIFIC ENEMY CLASSES ====================

class Grunt(Enemy):
    """Basic melee enemy."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'grunt', game)


class Archer(Enemy):
    """Ranged enemy that shoots arrows."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'archer', game)
        self.arrow_cooldown = 0
        self.arrow_speed = ARROW_SPEED
        self.arrow_damage = 10
    
    def _perform_attack(self, player):
        """Shoot an arrow at the player."""
        if self.arrow_cooldown > 0:
            return
        
        self.arrow_cooldown = self.attack_cooldown
        
        # Calculate direction to player
        player_center = player.get_center()
        dx = player_center[0] - (self.x + self.width // 2)
        dy = player_center[1] - (self.y + self.height // 2)
        
        # Normalize direction
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return
        
        vx = (dx / dist) * self.arrow_speed
        vy = (dy / dist) * self.arrow_speed
        
        # Create arrow
        if hasattr(self.game, 'world'):
            self.game.world.add_projectile(
                'arrow', self.x + self.width // 2, self.y + self.height // 2, vx, vy, self
            )
    
    def update(self, dt, player):
        """Update with arrow cooldown."""
        self.arrow_cooldown = max(0, self.arrow_cooldown - dt)
        return super().update(dt, player)


class Tank(Enemy):
    """Heavy melee enemy with high health and damage."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'tank', game)


class Assassin(Enemy):
    """Fast melee enemy that tries to flank the player."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'assassin', game)
    
    def _chase(self, dt, player_center):
        """Chase with flanking behavior."""
        # Try to get behind the player
        player_x = player_center[0]
        my_x = self.x + self.width // 2
        
        # If player is to our right, try to go left, and vice versa
        if player_x > my_x:
            target_x = player_x - 100  # Try to get to player's left
        else:
            target_x = player_x + 100  # Try to get to player's right
        
        target_y = player_center[1]
        
        dx = target_x - my_x
        dy = target_y - (self.y + self.height // 2)
        
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 10:
            self.vx = 0
            return
        
        self.vx = (dx / dist) * self.speed
        
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False


class Mage(Enemy):
    """Ranged spellcaster that casts fireballs."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'mage', game)
        self.fireball_cooldown = 0
        self.fireball_damage = self.config.get('fireball_damage', 25)
        self.explosion_radius = self.config.get('explosion_radius', 50)
        self.explosion_damage = self.config.get('explosion_damage', 15)
    
    def _perform_attack(self, player):
        """Cast a fireball at the player."""
        if self.fireball_cooldown > 0:
            return
        
        self.fireball_cooldown = self.attack_cooldown
        
        # Calculate direction to player
        player_center = player.get_center()
        dx = player_center[0] - (self.x + self.width // 2)
        dy = player_center[1] - (self.y + self.height // 2)
        
        # Normalize direction
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return
        
        vx = (dx / dist) * FIREBALL_SPEED
        vy = (dy / dist) * FIREBALL_SPEED
        
        # Create fireball
        if hasattr(self.game, 'world'):
            self.game.world.add_projectile(
                'fireball', self.x + self.width // 2, self.y + self.height // 2, vx, vy, self
            )
    
    def update(self, dt, player):
        """Update with fireball cooldown."""
        self.fireball_cooldown = max(0, self.fireball_cooldown - dt)
        return super().update(dt, player)


class Boss(Enemy):
    """Final boss enemy with multiple phases."""
    
    def __init__(self, x, y, game):
        super().__init__(x, y, 'boss', game)
        self.phase = 1  # 1, 2, or 3
        self.shockwave_cooldown = 0
        self.shockwave_timer = 0
        self.shockwave_radius = self.config.get('shockwave_radius', 300)
        self.shockwave_damage = self.config.get('shockwave_damage', 40)
    
    def _update_ai_state(self, dt, player, distance_to_player):
        """Update AI with boss-specific behavior."""
        # Update phase based on health
        health_percent = self.health / self.max_health
        if health_percent <= 0.2 and self.phase != 3:
            self.phase = 3
        elif health_percent <= 0.5 and self.phase != 2:
            self.phase = 2
        
        # Use shockwave periodically
        self.shockwave_cooldown = max(0, self.shockwave_cooldown - dt)
        self.shockwave_timer += dt
        
        if self.shockwave_cooldown <= 0 and self.shockwave_timer >= 5.0:
            self._shockwave_attack()
            self.shockwave_cooldown = self.config.get('shockwave_cooldown', 5.0)
            self.shockwave_timer = 0
        
        # Call parent update
        super()._update_ai_state(dt, player, distance_to_player)
    
    def _shockwave_attack(self):
        """Perform a shockwave attack."""
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.create_shockwave(
                self.x + self.width // 2, self.y + self.height // 2,
                self.shockwave_radius, self.shockwave_damage, self
            )
    
    def _perform_attack(self, player):
        """Boss melee attack."""
        # Enhanced damage based on phase
        phase_multiplier = {1: 1.0, 2: 1.5, 3: 2.0}
        damage = int(self.damage * phase_multiplier.get(self.phase, 1.0))
        
        if hasattr(self.game, 'combat_system'):
            attack_x = self.x + (self.width if self.facing_right else 0)
            attack_y = self.y + self.height // 4
            attack_width = self.attack_range * phase_multiplier.get(self.phase, 1.0)
            attack_height = self.height // 2
            
            self.game.combat_system.enemy_attack(
                self, attack_x, attack_y, attack_width, attack_height, damage
            )
    
    def die(self):
        """Boss death - special effects."""
        super().die()
        
        # Create massive explosion
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.create_shockwave(
                self.x + self.width // 2, self.y + self.height // 2,
                500, 100, self
            )
        
        # Trigger victory
        if hasattr(self.game, 'victory'):
            self.game.victory()


# Enemy type mapping for spawning
ENEMY_CLASS_MAP = {
    'grunt': Grunt,
    'archer': Archer,
    'tank': Tank,
    'assassin': Assassin,
    'mage': Mage,
    'boss': Boss,
    'knight': Tank,  # Knight is essentially a tank
    'shadow_grunt': Grunt,
    'reaper': Assassin,  # Reaper is like a stronger assassin
    'spider': Grunt,  # Placeholder
    'wolf': Grunt,  # Placeholder
    'scorpion': Grunt,
    'bandit': Archer,
    'sand_worm': Tank,
    'yeti': Tank,
    'ice_mage': Mage,
    'frost_troll': Tank,
    'skeleton': Grunt,
    'zombie': Grunt,
    'golem': Tank,
    'cave_troll': Boss,
    'ancient_golem': Boss,
    'dark_knight': Boss,
    'shadow_dragon': Boss
}


def create_enemy(x, y, enemy_type, game):
    """Factory function to create an enemy of the specified type."""
    enemy_class = ENEMY_CLASS_MAP.get(enemy_type, Enemy)
    return enemy_class(x, y, game)

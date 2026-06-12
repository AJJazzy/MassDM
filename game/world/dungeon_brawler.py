"""
STICK REALM: SHADOW OPEN WORLD - Dungeon Brawler Mode

When entering dungeons, the game transforms into a side-view 2D brawler
with chaotic physics similar to Stick Fight: The Game.

Features:
- Side-view 2D perspective (instead of top-down)
- Chaotic physics with ragdoll effects
- Enhanced combat with melee weapons and environmental interactions
- Traps and hazards unique to dungeons
- Boss battles with special mechanics
"""

import pygame
import random
import math
from config import *
from .dungeon import Dungeon


class DungeonPhysics:
    """
    Chaotic physics system for dungeon brawler mode.
    Handles ragdoll physics, collisions, and environmental interactions.
    """
    
    def __init__(self):
        self.gravity = DUNGEON_GRAVITY
        self.air_resistance = DUNGEON_AIR_RESISTANCE
        self.friction = DUNGEON_FRICTION
        self.bounce_factor = DUNGEON_BOUNCE_FACTOR
        self.max_velocity = DUNGEON_MAX_VELOCITY
        
    def apply_gravity(self, entity, dt):
        """Apply gravity to an entity."""
        entity.vy += self.gravity * dt * 60
        
    def apply_friction(self, entity, dt):
        """Apply friction to an entity when on ground."""
        if entity.is_grounded:
            entity.vx *= (1 - self.friction * dt * 60)
            if abs(entity.vx) < 0.1:
                entity.vx = 0
                
    def apply_air_resistance(self, entity, dt):
        """Apply air resistance to an entity."""
        if not entity.is_grounded:
            entity.vx *= (1 - self.air_resistance * dt * 60)
            
    def clamp_velocity(self, entity):
        """Clamp entity velocity to maximum."""
        if abs(entity.vx) > self.max_velocity:
            entity.vx = self.max_velocity * (1 if entity.vx > 0 else -1)
        if abs(entity.vy) > self.max_velocity:
            entity.vy = self.max_velocity * (1 if entity.vy > 0 else -1)


class DungeonEntity:
    """
    Base class for dungeon entities with ragdoll physics.
    """
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.is_grounded = False
        self.health = 100
        self.max_health = 100
        self.facing_right = True
        self.stun_timer = 0
        self.knockback_multiplier = 1.0
        
        # Physics body parts for ragdoll
        self.body_parts = []
        self.joints = []
        
    def update(self, dt, physics, dungeon):
        """Update entity with dungeon physics."""
        if self.stun_timer > 0:
            self.stun_timer -= dt
            return
            
        # Apply physics
        physics.apply_gravity(self, dt)
        physics.apply_air_resistance(self, dt)
        physics.clamp_velocity(self)
        
        # Update position
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Check ground collision
        self.is_grounded = dungeon.check_ground_collision(self)
        
        if self.is_grounded:
            physics.apply_friction(self, dt)
            self.vy = 0
            
    def apply_force(self, fx, fy):
        """Apply force to entity."""
        self.vx += fx
        self.vy += fy
        
    def apply_knockback(self, force, direction):
        """Apply knockback force."""
        self.vx += direction * force * self.knockback_multiplier
        self.stun_timer = 0.1
        
    def take_damage(self, damage, direction):
        """Take damage and apply knockback."""
        self.health -= damage
        self.apply_knockback(damage * 0.5, direction)
        return self.health <= 0


class DungeonPlayer(DungeonEntity):
    """
    Player character in dungeon brawler mode.
    """
    
    def __init__(self, x, y):
        super().__init__(x, y, DUNGEON_PLAYER_WIDTH, DUNGEON_PLAYER_HEIGHT)
        self.health = DUNGEON_PLAYER_HEALTH
        self.max_health = DUNGEON_PLAYER_HEALTH
        self.jump_power = DUNGEON_JUMP_POWER
        self.speed = DUNGEON_PLAYER_SPEED
        self.attack_cooldown = 0
        self.attack_damage = DUNGEON_PLAYER_DAMAGE
        self.attack_range = DUNGEON_PLAYER_ATTACK_RANGE
        
        # Combat state
        self.is_attacking = False
        self.attack_timer = 0
        self.combo_count = 0
        
        # Movement state
        self.is_jumping = False
        self.jump_buffer = 0
        self.coyote_time = 0
        
    def update(self, dt, physics, dungeon, input_state):
        """Update player with input."""
        super().update(dt, physics, dungeon)
        
        # Handle input
        if input_state['move_left']:
            self.vx = -self.speed
            self.facing_right = False
        elif input_state['move_right']:
            self.vx = self.speed
            self.facing_right = True
        else:
            # Apply friction when not moving
            if self.is_grounded:
                self.vx *= 0.8
                
        # Jump
        if input_state['jump'] and self.jump_buffer > 0:
            self.vy = -self.jump_power
            self.is_jumping = True
            self.is_grounded = False
            self.jump_buffer = 0
            
        # Update jump buffer
        if self.is_grounded:
            self.jump_buffer = DUNGEON_JUMP_BUFFER
        else:
            self.jump_buffer = max(0, self.jump_buffer - dt * 60)
            
        # Coyote time
        if self.is_grounded:
            self.coyote_time = DUNGEON_COYOTE_TIME
        else:
            self.coyote_time = max(0, self.coyote_time - dt * 60)
            
        # Attack
        if input_state['attack'] and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = DUNGEON_ATTACK_DURATION
            self.attack_cooldown = DUNGEON_ATTACK_COOLDOWN
            self.combo_count += 1
            
            # Perform attack
            self._perform_attack(dungeon)
            
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt * 60
            if self.attack_timer <= 0:
                self.is_attacking = False
                
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt * 60
            
        # Reset combo if no attack for a while
        if self.combo_count > 0 and not self.is_attacking:
            self.combo_timer = max(0, self.combo_timer - dt * 60)
            if self.combo_timer <= 0:
                self.combo_count = 0
        else:
            self.combo_timer = DUNGEON_COMBO_WINDOW
            
    def _perform_attack(self, dungeon):
        """Perform melee attack."""
        direction = 1 if self.facing_right else -1
        attack_x = self.x + (self.width if self.facing_right else 0)
        attack_y = self.y + self.height // 2
        
        # Create attack hitbox
        hitbox = pygame.Rect(
            attack_x - 5,
            attack_y - self.height // 2,
            self.attack_range + 10,
            self.height
        )
        
        # Check for hits
        for enemy in dungeon.enemies:
            if hitbox.colliderect(enemy.get_hitbox()):
                damage = self.attack_damage * (1 + self.combo_count * 0.2)
                enemy.take_damage(damage, direction)
                
        # Create attack effect
        dungeon.create_attack_effect(attack_x, attack_y, direction, self.combo_count)
        
    def get_hitbox(self):
        """Get player hitbox."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def render(self, screen, camera):
        """Render player as stick figure."""
        # Get screen position
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Draw body (vertical line)
        body_height = self.height - 10
        pygame.draw.line(
            screen, WHITE,
            (int(screen_x + self.width // 2), int(screen_y + 5)),
            (int(screen_x + self.width // 2), int(screen_y + 5 + body_height)),
            3
        )
        
        # Draw head
        head_radius = 8
        pygame.draw.circle(
            screen, WHITE,
            (int(screen_x + self.width // 2), int(screen_y + 5)),
            head_radius, 2
        )
        
        # Draw arms
        arm_length = 15
        arm_y = screen_y + 15
        if self.is_attacking:
            # Swing arm for attack
            swing_offset = 20 * (1 if self.facing_right else -1)
            pygame.draw.line(
                screen, WHITE,
                (int(screen_x + self.width // 2), int(arm_y)),
                (int(screen_x + self.width // 2 + arm_length + swing_offset), int(arm_y - 10)),
                2
            )
        else:
            pygame.draw.line(
                screen, WHITE,
                (int(screen_x + self.width // 2), int(arm_y)),
                (int(screen_x + self.width // 2 + (arm_length if self.facing_right else -arm_length)), int(arm_y)),
                2
            )
            
        # Draw legs
        leg_length = 10
        pygame.draw.line(
            screen, WHITE,
            (int(screen_x + self.width // 2), int(screen_y + 5 + body_height)),
            (int(screen_x + self.width // 2 - 5), int(screen_y + 5 + body_height + leg_length)),
            2
        )
        pygame.draw.line(
            screen, WHITE,
            (int(screen_x + self.width // 2), int(screen_y + 5 + body_height)),
            (int(screen_x + self.width // 2 + 5), int(screen_y + 5 + body_height + leg_length)),
            2
        )
        
        # Draw weapon if attacking
        if self.is_attacking:
            weapon_length = 25
            weapon_end_x = screen_x + self.width // 2 + (weapon_length if self.facing_right else -weapon_length)
            weapon_end_y = screen_y + 15 - 5
            pygame.draw.line(
                screen, YELLOW,
                (int(screen_x + self.width // 2), int(screen_y + 15)),
                (int(weapon_end_x), int(weapon_end_y)),
                3
            )


class DungeonEnemy(DungeonEntity):
    """
    Enemy in dungeon brawler mode with ragdoll physics.
    """
    
    def __init__(self, x, y, enemy_type):
        width = DUNGEON_ENEMY_WIDTH
        height = DUNGEON_ENEMY_HEIGHT
        super().__init__(x, y, width, height)
        
        self.type = enemy_type
        self.config = DUNGEON_ENEMY_TYPES.get(enemy_type, DUNGEON_ENEMY_TYPES['grunt'])
        self.health = self.config['health']
        self.max_health = self.config['health']
        self.damage = self.config['damage']
        self.speed = self.config['speed']
        self.attack_range = self.config['attack_range']
        self.attack_cooldown = 0
        self.attack_timer = 0
        
        # AI state
        self.state = 'idle'  # idle, chase, attack, hurt, dead
        self.target = None
        self.detection_range = 200
        self.attack_cooldown_max = 1.0
        
    def update(self, dt, physics, dungeon, player):
        """Update enemy AI and physics."""
        if self.health <= 0:
            self.state = 'dead'
            return
            
        super().update(dt, physics, dungeon)
        
        # Update target
        self.target = player
        
        # State machine
        if self.state == 'idle':
            self._update_idle(dt)
        elif self.state == 'chase':
            self._update_chase(dt, player)
        elif self.state == 'attack':
            self._update_attack(dt, player)
        elif self.state == 'hurt':
            self._update_hurt(dt)
            
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt * 60
            
    def _update_idle(self, dt):
        """Idle state - look for player."""
        if self.target and abs(self.x - self.target.x) < self.detection_range:
            self.state = 'chase'
            
    def _update_chase(self, dt, player):
        """Chase state - move towards player."""
        direction = 1 if player.x > self.x else -1
        self.facing_right = direction > 0
        
        # Move towards player
        self.vx = direction * self.speed
        
        # Check if in attack range
        distance = abs(self.x - player.x)
        if distance < self.attack_range and self.attack_cooldown <= 0:
            self.state = 'attack'
            self.attack_timer = 0.5
            
    def _update_attack(self, dt, player):
        """Attack state - perform attack."""
        self.vx = 0  # Stop moving while attacking
        
        self.attack_timer -= dt * 60
        if self.attack_timer <= 0:
            # Perform attack
            self._perform_attack(player)
            self.attack_cooldown = self.attack_cooldown_max
            self.state = 'chase'
            
    def _update_hurt(self, dt):
        """Hurt state - temporary stun."""
        self.stun_timer -= dt * 60
        if self.stun_timer <= 0:
            self.state = 'chase'
            
    def _perform_attack(self, player):
        """Perform attack on player."""
        direction = 1 if self.facing_right else -1
        attack_x = self.x + (self.width if self.facing_right else 0)
        
        # Create attack hitbox
        hitbox = pygame.Rect(
            attack_x - 5,
            self.y + 5,
            self.attack_range + 10,
            self.height - 10
        )
        
        # Check for hit on player
        if hitbox.colliderect(player.get_hitbox()):
            player.take_damage(self.damage, direction)
            
    def take_damage(self, damage, direction):
        """Take damage and react."""
        super().take_damage(damage, direction)
        self.state = 'hurt'
        self.stun_timer = 0.3
        
    def get_hitbox(self):
        """Get enemy hitbox."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def render(self, screen, camera):
        """Render enemy as stick figure."""
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Different colors for different enemy types
        color = DUNGEON_ENEMY_COLORS.get(self.type, RED)
        
        # Draw body
        body_height = self.height - 8
        pygame.draw.line(
            screen, color,
            (int(screen_x + self.width // 2), int(screen_y + 4)),
            (int(screen_x + self.width // 2), int(screen_y + 4 + body_height)),
            2
        )
        
        # Draw head
        head_radius = 6
        pygame.draw.circle(
            screen, color,
            (int(screen_x + self.width // 2), int(screen_y + 4)),
            head_radius, 1
        )
        
        # Draw arms
        arm_length = 12
        arm_y = screen_y + 12
        pygame.draw.line(
            screen, color,
            (int(screen_x + self.width // 2), int(arm_y)),
            (int(screen_x + self.width // 2 + (arm_length if self.facing_right else -arm_length)), int(arm_y)),
            1
        )
        
        # Draw legs
        pygame.draw.line(
            screen, color,
            (int(screen_x + self.width // 2), int(screen_y + 4 + body_height)),
            (int(screen_x + self.width // 2 - 4), int(screen_y + 4 + body_height + 8)),
            1
        )
        pygame.draw.line(
            screen, color,
            (int(screen_x + self.width // 2), int(screen_y + 4 + body_height)),
            (int(screen_x + self.width // 2 + 4), int(screen_y + 4 + body_height + 8)),
            1
        )


class DungeonCamera:
    """
    Camera for dungeon brawler mode - side-view following.
    """
    
    def __init__(self, target, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.target = target
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.lerp_factor = 0.1
        self.shake_intensity = 0
        self.shake_timer = 0
        
    def update(self, dt):
        """Update camera position."""
        # Target position (centered on player)
        target_x = self.target.x - self.screen_width // 2 + self.target.width // 2
        target_y = self.target.y - self.screen_height // 2 + self.target.height // 2
        
        # Smooth follow
        self.x += (target_x - self.x) * self.lerp_factor * 60 * dt
        self.y += (target_y - self.y) * self.lerp_factor * 60 * dt
        
        # Apply shake
        if self.shake_timer > 0:
            self.x += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.y += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= dt * 60
        else:
            self.shake_intensity = 0
            
    def shake(self, intensity, duration):
        """Apply camera shake."""
        self.shake_intensity = intensity
        self.shake_timer = duration * 60


class DungeonBrawlerMode:
    """
    Main dungeon brawler mode controller.
    Transforms the open-world gameplay into a side-view 2D brawler.
    """
    
    def __init__(self, game, dungeon):
        self.game = game
        self.dungeon = dungeon
        self.active = False
        
        # Create dungeon-specific entities
        self.player = DungeonPlayer(dungeon.entrance_x, dungeon.entrance_y)
        self.camera = DungeonCamera(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.physics = DungeonPhysics()
        
        # Create dungeon enemies
        self.enemies = []
        for enemy_data in dungeon.enemies:
            enemy = DungeonEnemy(
                enemy_data['x'], enemy_data['y'],
                enemy_data['type']
            )
            self.enemies.append(enemy)
            
        # Dungeon state
        self.completed = False
        self.boss_defeated = False
        self.score = 0
        self.time = 0
        
    def enter(self):
        """Enter dungeon brawler mode."""
        self.active = True
        self.time = 0
        print("Entering dungeon brawler mode!")
        
    def exit(self):
        """Exit dungeon brawler mode."""
        self.active = False
        print("Exiting dungeon brawler mode!")
        
    def update(self, dt, input_state):
        """Update dungeon brawler mode."""
        if not self.active:
            return
            
        self.time += dt
        
        # Update player
        self.player.update(dt, self.physics, self.dungeon, input_state)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.physics, self.dungeon, self.player)
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += 100
                
        # Update camera
        self.camera.update(dt)
        
        # Check for completion
        if not self.enemies and not self.boss_defeated:
            self.boss_defeated = True
            self._spawn_boss()
            
        if self.boss_defeated and not self.enemies:
            self.completed = True
            
    def _spawn_boss(self):
        """Spawn the dungeon boss."""
        boss = DungeonEnemy(
            self.dungeon.boss_x, self.dungeon.boss_y,
            'boss'
        )
        boss.health *= 5
        boss.damage *= 2
        boss.speed *= 0.7
        self.enemies.append(boss)
        print("Boss spawned!")
        
    def render(self, screen):
        """Render dungeon brawler mode."""
        # Clear screen
        screen.fill(BLACK)
        
        # Render dungeon background
        self._render_background(screen)
        
        # Render dungeon tiles
        self._render_tiles(screen)
        
        # Render enemies
        for enemy in self.enemies:
            enemy.render(screen, self.camera)
            
        # Render player
        self.player.render(screen, self.camera)
        
        # Render HUD
        self._render_hud(screen)
        
    def _render_background(self, screen):
        """Render dungeon background."""
        # Draw gradient background
        for y in range(0, SCREEN_HEIGHT, 20):
            alpha = min(50, y // 4)
            color = (alpha, alpha, alpha)
            pygame.draw.line(
                screen, color,
                (0, y), (SCREEN_WIDTH, y), 1
            )
            
    def _render_tiles(self, screen):
        """Render dungeon floor and walls."""
        # Calculate visible area
        start_x = int(self.camera.x)
        end_x = int(self.camera.x + SCREEN_WIDTH)
        start_y = int(self.camera.y)
        end_y = int(self.camera.y + SCREEN_HEIGHT)
        
        # Draw floor
        floor_y = self.dungeon.floor_y
        pygame.draw.line(
            screen, GRAY_40,
            (0, floor_y - self.camera.y),
            (SCREEN_WIDTH, floor_y - self.camera.y),
            2
        )
        
        # Draw walls if any
        for wall in self.dungeon.walls:
            wall_x = wall['x'] - self.camera.x
            wall_y = wall['y'] - self.camera.y
            pygame.draw.rect(
                screen, GRAY_30,
                (wall_x, wall_y, wall['width'], wall['height']),
                1
            )
            
    def _render_hud(self, screen):
        """Render dungeon HUD."""
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        # Background
        pygame.draw.rect(
            screen, GRAY_20,
            (health_x, health_y, health_width, health_height),
            0
        )
        
        # Health fill
        health_percent = self.player.health / self.player.max_health
        fill_width = int(health_width * health_percent)
        fill_color = GREEN if health_percent > 0.5 else YELLOW if health_percent > 0.25 else RED
        pygame.draw.rect(
            screen, fill_color,
            (health_x, health_y, fill_width, health_height),
            0
        )
        
        # Border
        pygame.draw.rect(
            screen, WHITE,
            (health_x, health_y, health_width, health_height),
            1
        )
        
        # Score
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        # Time
        time_text = font.render(f"Time: {int(self.time)}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 50))
        
        # Combo
        if self.player.combo_count > 0:
            combo_text = font.render(f"Combo: x{self.player.combo_count}", True, YELLOW)
            screen.blit(combo_text, (SCREEN_WIDTH // 2 - 50, 20))




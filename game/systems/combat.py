"""
STICK REALM: SHADOW OPEN WORLD - Combat System
Handles damage calculation, hit detection, and combat mechanics
"""

import pygame
import random
import math
from config import *


class CombatSystem:
    """
    Handles all combat mechanics including damage calculation, hit detection,
    combo system, status effects, and special attacks.
    """
    
    def __init__(self, game):
        """
        Initialize the combat system.
        game: Reference to the main game instance
        """
        self.game = game
        
        # Combat settings
        self.critical_hit_chance = 0.20
        self.critical_hit_multiplier = 2.0
        self.knockback_force = 100
        
        # Combo system
        self.combo_multiplier = 1.0
        
        # Hit detection
        self.hit_registry = {}  # Track hits to prevent double-counting
        
        # Statistics
        self.damage_dealt = 0
        self.damage_taken = 0
        self.kills = 0
        self.critical_hits = 0
    
    def update(self, dt):
        """
        Update combat system.
        dt: Time since last frame in seconds
        """
        # Clear hit registry periodically
        self.hit_registry = {}
    
    def player_light_attack(self, player, attack_x, attack_y, attack_width, attack_height, damage):
        """
        Handle player light attack.
        player: Player entity
        attack_x, attack_y: Attack hitbox position
        attack_width, attack_height: Attack hitbox dimensions
        damage: Base damage
        """
        # Create attack hitbox
        attack_hitbox = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
        
        # Check for hits
        if hasattr(self.game, 'world'):
            for enemy in self.game.world.enemies[:]:
                self._check_attack_hit(player, enemy, attack_hitbox, damage, 'light')
    
    def player_heavy_attack(self, player, attack_x, attack_y, attack_width, attack_height, damage):
        """
        Handle player heavy attack.
        player: Player entity
        attack_x, attack_y: Attack hitbox position
        attack_width, attack_height: Attack hitbox dimensions
        damage: Base damage
        """
        # Create attack hitbox
        attack_hitbox = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
        
        # Check for hits
        if hasattr(self.game, 'world'):
            for enemy in self.game.world.enemies[:]:
                self._check_attack_hit(player, enemy, attack_hitbox, damage, 'heavy')
    
    def player_whirlwind_attack(self, player, center_x, center_y, radius, damage):
        """
        Handle player whirlwind attack (hits all enemies in radius).
        player: Player entity
        center_x, center_y: Center of attack
        radius: Attack radius
        damage: Base damage
        """
        if hasattr(self.game, 'world'):
            for enemy in self.game.world.enemies[:]:
                enemy_center = enemy.get_center()
                distance = distance(center_x, center_y, enemy_center[0], enemy_center[1])
                
                if distance <= radius:
                    # Calculate direction
                    dx = enemy_center[0] - center_x
                    dy = enemy_center[1] - center_y
                    direction = 1 if dx > 0 else -1
                    
                    # Apply damage
                    self._apply_damage_to_enemy(enemy, damage, direction, player, 'whirlwind')
    
    def player_shadow_dash(self, player, start_x, start_y, direction, dash_distance):
        """
        Handle player shadow dash (teleport through enemies, dealing damage).
        player: Player entity
        start_x, start_y: Starting position
        direction: Direction of dash (1 for right, -1 for left)
        dash_distance: Distance to teleport
        """
        if not hasattr(self.game, 'world'):
            return
        
        # Calculate end position
        end_x = start_x + direction * dash_distance
        
        # Check for enemies along the path
        for enemy in self.game.world.enemies[:]:
            enemy_center = enemy.get_center()
            
            # Check if enemy is between start and end
            if direction > 0:
                if (start_x <= enemy_center[0] <= end_x and
                    abs(enemy_center[1] - start_y) < 50):
                    # Apply damage
                    self._apply_damage_to_enemy(enemy, 30, -direction, player, 'shadow_dash')
            else:
                if (end_x <= enemy_center[0] <= start_x and
                    abs(enemy_center[1] - start_y) < 50):
                    # Apply damage
                    self._apply_damage_to_enemy(enemy, 30, -direction, player, 'shadow_dash')
        
        # Teleport player
        player.x = end_x - player.width // 2
        player.y = start_y - player.height // 2
    
    def enemy_attack(self, enemy, attack_x, attack_y, attack_width, attack_height, damage):
        """
        Handle enemy attack.
        enemy: Enemy entity
        attack_x, attack_y: Attack hitbox position
        attack_width, attack_height: Attack hitbox dimensions
        damage: Base damage
        """
        # Create attack hitbox
        attack_hitbox = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
        
        # Check for hit on player
        if hasattr(self.game, 'player'):
            player = self.game.player
            if hasattr(player, 'get_hitbox'):
                player_hitbox = player.get_hitbox()
                if attack_hitbox.colliderect(player_hitbox):
                    # Calculate direction
                    enemy_center = enemy.get_center()
                    player_center = player.get_center()
                    dx = player_center[0] - enemy_center[0]
                    direction = 1 if dx > 0 else -1
                    
                    # Apply damage to player
                    self._apply_damage_to_player(player, damage, direction, enemy)
    
    def create_fireball(self, x, y, direction, owner):
        """
        Create a fireball projectile.
        x, y: Starting position
        direction: Direction (1 for right, -1 for left)
        owner: Entity that fired the fireball
        """
        if hasattr(self.game, 'world'):
            vx = direction * FIREBALL_SPEED
            vy = 0
            self.game.world.add_projectile('fireball', x, y, vx, vy, owner)
    
    def create_ice_projectile(self, x, y, direction, owner):
        """
        Create an ice projectile.
        x, y: Starting position
        direction: Direction (1 for right, -1 for left)
        owner: Entity that fired the projectile
        """
        if hasattr(self.game, 'world'):
            vx = direction * FIREBALL_SPEED * 0.8
            vy = 0
            # Create a custom ice projectile (would need to add to projectile types)
            self.game.world.add_projectile('fireball', x, y, vx, vy, owner)
            # Note: In full implementation, would have a separate ice projectile type
    
    def create_shockwave(self, x, y, radius, damage, owner):
        """
        Create a shockwave.
        x, y: Center position
        radius: Shockwave radius
        damage: Damage to deal
        owner: Entity that created the shockwave
        """
        if hasattr(self.game, 'world'):
            # Shockwave is handled specially - it's not a regular projectile
            # For now, we'll create a shockwave projectile
            self.game.world.add_projectile('shockwave', x - radius, y - radius, 0, 0, owner)
            # The shockwave projectile will handle its own expansion and damage
    
    def create_explosion(self, x, y, radius, damage, owner):
        """
        Create an explosion at the specified position.
        x, y: Center position
        radius: Explosion radius
        damage: Damage to deal
        owner: Entity that caused the explosion
        """
        if hasattr(self.game, 'world'):
            # Apply damage to all entities in radius
            for enemy in self.game.world.enemies[:]:
                enemy_center = enemy.get_center()
                distance = distance(x, y, enemy_center[0], enemy_center[1])
                
                if distance <= radius:
                    # Calculate damage based on distance (falloff)
                    damage_ratio = 1.0 - (distance / radius)
                    actual_damage = int(damage * damage_ratio)
                    
                    # Calculate direction
                    dx = enemy_center[0] - x
                    direction = 1 if dx > 0 else -1
                    
                    # Apply damage
                    enemy.take_damage(actual_damage, direction, 50, 'burn')
            
            # Apply damage to player if in radius
            if hasattr(self.game, 'player'):
                player = self.game.player
                player_center = player.get_center()
                distance = distance(x, y, player_center[0], player_center[1])
                
                if distance <= radius:
                    damage_ratio = 1.0 - (distance / radius)
                    actual_damage = int(damage * damage_ratio)
                    
                    dx = player_center[0] - x
                    direction = 1 if dx > 0 else -1
                    
                    player.take_damage(actual_damage, direction, 50, 'burn')
            
            # Create explosion particles
            if hasattr(self.game, 'particle_system'):
                self.game.particle_system.create_explosion_particles(x, y, radius)
    
    def _check_attack_hit(self, attacker, target, attack_hitbox, base_damage, attack_type):
        """
        Check if an attack hits a target.
        attacker: Entity performing the attack
        target: Entity being attacked
        attack_hitbox: Attack hitbox rectangle
        base_damage: Base damage of the attack
        attack_type: Type of attack ('light', 'heavy', etc.)
        """
        if not hasattr(target, 'get_hitbox'):
            return
        
        target_hitbox = target.get_hitbox()
        
        # Check collision
        if not attack_hitbox.colliderect(target_hitbox):
            return
        
        # Check if already hit this frame (prevent double-counting)
        hit_key = (id(attacker), id(target))
        if hit_key in self.hit_registry:
            return
        self.hit_registry[hit_key] = True
        
        # Calculate direction
        attacker_center = attacker.get_center()
        target_center = target.get_center()
        dx = target_center[0] - attacker_center[0]
        direction = 1 if dx > 0 else -1
        
        # Calculate damage
        damage = self._calculate_damage(attacker, target, base_damage, attack_type)
        
        # Apply damage
        if hasattr(target, 'take_damage'):
            target.take_damage(damage, direction, self.knockback_force, self._get_damage_type(attack_type))
        
        # Track statistics
        self.damage_dealt += damage
        
        # Check for kill
        if hasattr(target, 'health') and target.health <= 0:
            self.kills += 1
            if hasattr(attacker, 'kills'):
                attacker.kills += 1
    
    def _apply_damage_to_enemy(self, enemy, damage, direction, attacker, attack_type):
        """
        Apply damage to an enemy.
        enemy: Enemy to damage
        damage: Amount of damage
        direction: Direction of attack
        attacker: Entity that attacked
        attack_type: Type of attack
        """
        # Calculate final damage
        final_damage = self._calculate_damage(attacker, enemy, damage, attack_type)
        
        # Apply damage
        enemy.take_damage(final_damage, direction, self.knockback_force, self._get_damage_type(attack_type))
        
        # Track statistics
        self.damage_dealt += final_damage
        
        # Check for kill
        if enemy.health <= 0:
            self.kills += 1
            if hasattr(attacker, 'kills'):
                attacker.kills += 1
    
    def _apply_damage_to_player(self, player, damage, direction, attacker):
        """
        Apply damage to the player.
        player: Player to damage
        damage: Amount of damage
        direction: Direction of attack
        attacker: Entity that attacked
        """
        # Apply damage
        player.take_damage(damage, direction, self.knockback_force)
        
        # Track statistics
        self.damage_taken += damage
    
    def _calculate_damage(self, attacker, target, base_damage, attack_type):
        """
        Calculate final damage after all modifiers.
        attacker: Entity dealing damage
        target: Entity receiving damage
        base_damage: Base damage amount
        attack_type: Type of attack
        Returns: Final damage amount
        """
        damage = base_damage
        
        # Critical hit check
        critical_chance = self.critical_hit_chance
        if hasattr(attacker, 'critical_chance'):
            critical_chance += attacker.critical_chance
        
        is_critical = random.random() < critical_chance
        if is_critical:
            damage = int(damage * self.critical_hit_multiplier)
            self.critical_hits += 1
        
        # Combo multiplier
        if hasattr(attacker, 'combo_count') and attacker.combo_count > 0:
            combo_bonus = attacker.combo_count * 0.10
            damage = int(damage * (1 + combo_bonus))
        
        # Attack type modifiers
        if attack_type == 'heavy':
            # Heavy attacks do more damage
            damage = int(damage * 1.2)
        elif attack_type == 'whirlwind':
            # Whirlwind does less damage per hit
            damage = int(damage * 0.8)
        elif attack_type == 'shadow_dash':
            # Shadow dash does fixed damage
            damage = 30
        
        # Target defense
        if hasattr(target, 'defense'):
            damage = int(damage * (1 - target.defense))
        
        # Clamp minimum damage
        damage = max(1, damage)
        
        return damage
    
    def _get_damage_type(self, attack_type):
        """Get the damage type for an attack."""
        if attack_type == 'fire_attack':
            return 'burn'
        elif attack_type == 'ice_attack':
            return 'slow'
        elif attack_type == 'shadow_dash':
            return 'normal'
        else:
            return 'normal'
    
    def check_perfect_block(self, player, attacker):
        """
        Check if the player performed a perfect block.
        player: Player entity
        attacker: Attacking entity
        Returns: True if perfect block
        """
        if not hasattr(player, 'perfect_block_window'):
            return False
        
        return player.perfect_block_window > 0
    
    def get_combo_multiplier(self, combo_count):
        """
        Get the damage multiplier for a combo count.
        combo_count: Current combo count
        Returns: Damage multiplier
        """
        return 1.0 + combo_count * 0.10
    
    def reset_combo(self, entity):
        """
        Reset the combo for an entity.
        entity: Entity to reset combo for
        """
        if hasattr(entity, 'combo_count'):
            entity.combo_count = 0
        if hasattr(entity, 'combo_timer'):
            entity.combo_timer = 0
    
    def get_stats(self):
        """Get combat system statistics."""
        return {
            'damage_dealt': self.damage_dealt,
            'damage_taken': self.damage_taken,
            'kills': self.kills,
            'critical_hits': self.critical_hits
        }
    
    def reset_stats(self):
        """Reset combat statistics."""
        self.damage_dealt = 0
        self.damage_taken = 0
        self.kills = 0
        self.critical_hits = 0

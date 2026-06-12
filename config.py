"""
STICK REALM: SHADOW OPEN WORLD - Configuration File
All game constants and settings defined here
"""

import pygame
import math

# ==================== CORE SETTINGS ====================

# Game version
VERSION = "1.0.0"
GAME_TITLE = "STICK REALM: SHADOW OPEN WORLD"

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TARGET_FPS = 60
MAX_DT = 0.1  # Maximum delta time (seconds)

# World settings
WORLD_CENTER_X = 0
WORLD_CENTER_Y = 0
WORLD_CHUNK_SIZE = 16  # Chunks in each direction from center

# Initial spawn settings
INITIAL_ENEMIES = 5
INITIAL_ITEMS = 3

# ==================== COLOR PALETTE ====================
# STRICTLY BLACK AND WHITE with minimal accents

# Primary colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Grayscale palette (10 shades in 10% increments)
GRAY_05 = (12, 12, 12)      # Nearly black
GRAY_10 = (25, 25, 25)      # Almost black
GRAY_15 = (38, 38, 38)      # Very dark gray
GRAY_20 = (51, 51, 51)
GRAY_30 = (76, 76, 76)
GRAY_40 = (102, 102, 102)    # Forest biome
GRAY_50 = (128, 128, 128)    # Village biome
GRAY_55 = (140, 140, 140)    # Desert biome (slightly lighter)
GRAY_60 = (153, 153, 153)    # Tank color
GRAY_65 = (165, 165, 165)    # Mage color
GRAY_70 = (178, 178, 178)    # Archer color
GRAY_75 = (195, 195, 195)    # Ice Wastes biome
GRAY_80 = (204, 204, 204)    # Assassin color
GRAY_90 = (230, 230, 230)    # Very light gray

# Accent colors (ONLY for critical UI elements)
YELLOW = (255, 255, 0)      # Coins, notifications
RED = (255, 0, 0)            # Health bars (low), damage numbers
GREEN = (0, 255, 0)          # Health bars (high), healing
BLUE = (0, 0, 255)           # XP, water, special abilities

# Biome colors for minimap
BIOME_COLORS = {
    'forest': GRAY_40,
    'village': GRAY_50,
    'desert': GRAY_55,
    'ice_wastes': GRAY_75,
    'mountain': GRAY_30,
    'volcano': GRAY_20,
    'shadow_realm': GRAY_10,
    'shadow_temple': GRAY_15,
}

# Enemy colors for minimap
ENEMY_COLORS = {
    'Grunt': RED,
    'Archer': GREEN,
    'Tank': BLUE,
    'Assassin': YELLOW,
    'Mage': GRAY_65,
    'Boss': RED,
    'ShadowGrunt': GRAY_50,
    'Reaper': GRAY_10,
}

# Semi-transparent versions
YELLOW_TRANSLUCENT = (255, 255, 0, 200)
RED_TRANSLUCENT = (255, 0, 0, 200)

# ==================== WORLD SETTINGS ====================

# Tile settings
TILE_SIZE = 64
CHUNK_SIZE = 16  # 16x16 tiles per chunk
WORLD_WIDTH_TILES = 1000
WORLD_HEIGHT_TILES = 1000
WORLD_WIDTH_PIXELS = WORLD_WIDTH_TILES * TILE_SIZE
WORLD_HEIGHT_PIXELS = WORLD_HEIGHT_TILES * TILE_SIZE

# Chunk loading
CHUNK_LOAD_DISTANCE = 2  # Load chunks within this radius
CHUNK_UNLOAD_DISTANCE = 3  # Unload chunks beyond this radius

# ==================== PLAYER SETTINGS ====================

# Base stats
PLAYER_SIZE = 40  # Height in pixels
PLAYER_SPEED = 150  # pixels/second
PLAYER_RUN_SPEED = 225  # pixels/second (1.5x)
PLAYER_BASE_HEALTH = 100
PLAYER_BASE_DAMAGE_LIGHT = 25
PLAYER_BASE_DAMAGE_HEAVY = 40
PLAYER_DEFENSE = 0.30  # 30% damage reduction when blocking

# Hitbox
PLAYER_HITBOX_WIDTH = 24
PLAYER_HITBOX_HEIGHT = 60

# Combat
LIGHT_ATTACK_COOLDOWN = 0.3  # seconds
HEAVY_ATTACK_CHARGE_TIME = 0.5  # max charge time
HEAVY_ATTACK_COOLDOWN = 0.5
BLOCK_DAMAGE_REDUCTION = 0.70  # 70% reduction
PERFECT_BLOCK_WINDOW = 0.1  # seconds for perfect block timing
PERFECT_BLOCK_COUNTER_MULTIPLIER = 1.5

# Movement
DASH_DISTANCE = 150
DASH_DURATION = 0.2
DASH_COOLDOWN = 0.5
DASH_INVINCIBILITY = 0.3

ROLL_DISTANCE = 100
ROLL_DURATION = 0.2
ROLL_COOLDOWN = 0.3

# ==================== ENEMY SETTINGS ====================

# Base enemy stats
ENEMY_BASE_SIZE = 35
ENEMY_BASE_SPEED = 80
ENEMY_BASE_HEALTH = 60
ENEMY_BASE_DAMAGE = 15
ENEMY_AGGRO_RANGE = 200
ENEMY_ATTACK_RANGE_MELEE = 40
ENEMY_DESPAWN_DISTANCE = 800

# Enemy spawn settings
MAX_ENEMIES_ON_SCREEN = 100
SPAWN_DISTANCE = 300

# Enemy type multipliers
ENEMY_TYPES = {
    'grunt': {
        'size': 0.9, 'speed': 0.9, 'health': 0.8, 'damage': 0.8,
        'aggro_range': 200, 'attack_range': 40, 'attack_cooldown': 1.2,
        'color': GRAY_60, 'drop_coins': 20, 'health_potion_chance': 0.10,
        'weapon_upgrade_chance': 0.05, 'armour_upgrade_chance': 0.00
    },
    'archer': {
        'size': 0.8, 'speed': 0.8, 'health': 0.6, 'damage': 1.0,
        'aggro_range': 250, 'attack_range': 300, 'attack_cooldown': 1.5,
        'color': GRAY_70, 'drop_coins': 25, 'health_potion_chance': 0.00,
        'weapon_upgrade_chance': 0.15, 'armour_upgrade_chance': 0.00
    },
    'tank': {
        'size': 1.3, 'speed': 0.5, 'health': 2.0, 'damage': 1.8,
        'aggro_range': 300, 'attack_range': 50, 'attack_cooldown': 1.8,
        'color': GRAY_50, 'drop_coins': 35, 'health_potion_chance': 0.00,
        'weapon_upgrade_chance': 0.00, 'armour_upgrade_chance': 0.20,
        'knockback_resistance': 0.5
    },
    'assassin': {
        'size': 0.7, 'speed': 1.8, 'health': 0.5, 'damage': 2.5,
        'aggro_range': 240, 'attack_range': 35, 'attack_cooldown': 0.5,
        'color': GRAY_80, 'drop_coins': 30, 'health_potion_chance': 0.00,
        'weapon_upgrade_chance': 0.25, 'armour_upgrade_chance': 0.00,
        'critical_chance': 0.20, 'critical_multiplier': 2.0
    },
    'mage': {
        'size': 0.9, 'speed': 0.75, 'health': 0.66, 'damage': 1.0,
        'aggro_range': 250, 'attack_range': 400, 'attack_cooldown': 2.0,
        'color': GRAY_65, 'drop_coins': 30, 'health_potion_chance': 0.10,
        'weapon_upgrade_chance': 0.10, 'armour_upgrade_chance': 0.10,
        'fireball_damage': 25, 'explosion_radius': 50, 'explosion_damage': 15
    },
    'boss': {
        'size': 2.0, 'speed': 0.7, 'health': 10.0, 'damage': 3.0,
        'aggro_range': 500, 'attack_range': 80, 'attack_cooldown': 1.0,
        'color': RED, 'drop_coins': 500, 'health_potion_chance': 0.00,
        'weapon_upgrade_chance': 1.0, 'armour_upgrade_chance': 1.0,
        'shockwave_radius': 300, 'shockwave_damage': 40, 'shockwave_cooldown': 5.0
    }
}

# ==================== PROJECTILE SETTINGS ====================

# Arrow
ARROW_LENGTH = 8
ARROW_WIDTH = 2
ARROW_SPEED = 300
ARROW_LIFETIME = 3.0
ARROW_COLOR = GRAY_80

# Fireball
FIREBALL_DIAMETER = 15
FIREBALL_SPEED = 250
FIREBALL_LIFETIME = 2.5
FIREBALL_BASE_DAMAGE = 25
FIREBALL_EXPLOSION_RADIUS = 50
FIREBALL_EXPLOSION_DAMAGE = 15

# Shockwave
SHOCKWAVE_MAX_RADIUS = 300
SHOCKWAVE_SPEED = 400
SHOCKWAVE_COLOR = (255, 200, 0, 200)  # Yellow with transparency

# ==================== ITEM SETTINGS ====================

# Coin
COIN_DIAMETER = 20
COIN_COLOR = YELLOW
COIN_VALUE = 10
COIN_SPAWN_RATE = 0.01
COIN_AUTO_COLLECT_RANGE = 50

# Health Potion
HEALTH_POTION_SIZE = 25
HEALTH_POTION_HEAL_AMOUNT = 30
HEALTH_POTION_SPAWN_RATE = 0.002
HEALTH_POTION_DROP_CHANCE = 0.10

# Weapon Upgrade
WEAPON_UPGRADE_SIZE = 30
WEAPON_UPGRADE_LIGHT_DAMAGE_BONUS = 5
WEAPON_UPGRADE_HEAVY_DAMAGE_BONUS = 10
WEAPON_UPGRADE_SPAWN_RATE = 0.001
WEAPON_UPGRADE_DROP_CHANCE_BASE = 0.05

# Armour Upgrade
ARMOUR_UPGRADE_SIZE = 30
ARMOUR_UPGRADE_HEALTH_BONUS = 10
ARMOUR_UPGRADE_DAMAGE_REDUCTION_BONUS = 0.05  # 5%
ARMOUR_UPGRADE_SPAWN_RATE = 0.0005
ARMOUR_UPGRADE_DROP_CHANCE_BASE = 0.05

# ==================== PROGRESSION SYSTEM ====================

# XP rewards
XP_REWARDS = {
    'grunt': 20,
    'archer': 30,
    'tank': 40,
    'assassin': 50,
    'mage': 50,
    'boss': 500
}

# XP to level formula: base * (1.5 ^ (level-1))
BASE_XP_TO_LEVEL = 1000
MAX_LEVEL = 50

# Level up bonuses
HEALTH_PER_LEVEL = 10
DAMAGE_PER_LEVEL = 2
SPEED_PER_LEVEL = 1
XP_MULTIPLIER_PER_LEVEL = 0.10  # 10% bonus XP gain per level

# Ability unlock levels
ABILITY_UNLOCK_LEVELS = {
    'dash': 1,
    'roll': 1,
    'double_jump': 5,
    'whirlwind': 10,
    'fire_attack': 15,
    'ice_attack': 20,
    'shadow_dash': 25
}

# ==================== BIOME SETTINGS ====================

BIOMES = {
    'forest': {
        'color': GRAY_40,
        'tree_density': 0.30,
        'enemies': ['grunt', 'archer', 'wolf'],
        'difficulty': 1.0,
        'ambience': 'forest'
    },
    'village': {
        'color': GRAY_50,
        'building_density': 0.40,
        'enemies': ['grunt', 'archer'],
        'difficulty': 0.8,
        'ambience': 'village'
    },
    'cave': {
        'color': GRAY_20,
        'rock_density': 0.50,
        'enemies': ['grunt', 'tank', 'spider'],
        'difficulty': 1.5,
        'ambience': 'cave'
    },
    'castle': {
        'color': GRAY_50,
        'accent_color': GRAY_30,
        'trap_density': 0.30,
        'enemies': ['knight', 'archer', 'tank', 'mage'],
        'difficulty': 2.0,
        'ambience': 'castle'
    },
    'shadow_realm': {
        'color': GRAY_10,
        'fog_density': 0.70,
        'enemies': ['shadow_grunt', 'assassin', 'mage', 'reaper'],
        'difficulty': 2.5,
        'ambience': 'shadow'
    },
    'dungeon': {
        'color': GRAY_15,
        'trap_density': 0.50,
        'enemies': ['skeleton', 'zombie', 'golem'],
        'difficulty': 3.0,
        'ambience': 'dungeon'
    },
    'desert': {
        'color': GRAY_55,
        'cacti_density': 0.05,
        'enemies': ['scorpion', 'bandit', 'sand_worm'],
        'difficulty': 1.8,
        'ambience': 'desert'
    },
    'ice_wastes': {
        'color': GRAY_75,
        'ice_patch_density': 0.20,
        'enemies': ['yeti', 'ice_mage', 'frost_troll'],
        'difficulty': 2.2,
        'ambience': 'ice'
    }
}

# Biome transition settings
BIOME_BLEND_RADIUS = 32  # tiles

# ==================== DUNGEON SETTINGS ====================

DUNGEONS = {
    'cave_dungeon': {
        'depth': 3,
        'boss': 'cave_troll',
        'theme': 'dark_rocky',
        'traps': ['spike', 'falling_rock']
    },
    'ruins_dungeon': {
        'depth': 4,
        'boss': 'ancient_golem',
        'theme': 'crumbling_stone',
        'traps': ['pressure_plate', 'arrow_trap']
    },
    'castle_dungeon': {
        'depth': 5,
        'boss': 'dark_knight',
        'theme': 'gothic',
        'traps': ['guillotine', 'swinging_blade']
    },
    'shadow_temple': {
        'depth': 6,
        'boss': 'shadow_dragon',
        'theme': 'dark_ethereal',
        'traps': ['shadow_trap', 'teleporter']
    }
}

# Room types
ROOM_TYPES = ['normal', 'trap', 'puzzle', 'treasure', 'boss']


# ==================== DUNGEON BRAWLER SETTINGS ====================

# Physics
DUNGEON_GRAVITY = 1.2
DUNGEON_AIR_RESISTANCE = 0.02
DUNGEON_FRICTION = 0.15
DUNGEON_BOUNCE_FACTOR = 0.3
DUNGEON_MAX_VELOCITY = 20

# Player
DUNGEON_PLAYER_WIDTH = 30
DUNGEON_PLAYER_HEIGHT = 60
DUNGEON_PLAYER_HEALTH = 100
DUNGEON_PLAYER_SPEED = 5
DUNGEON_PLAYER_DAMAGE = 15
DUNGEON_PLAYER_ATTACK_RANGE = 40

# Movement
DUNGEON_JUMP_POWER = 12
DUNGEON_JUMP_BUFFER = 0.1  # seconds
DUNGEON_COYOTE_TIME = 0.1  # seconds

# Combat
DUNGEON_ATTACK_DURATION = 0.2  # seconds
DUNGEON_ATTACK_COOLDOWN = 0.3  # seconds
DUNGEON_COMBO_WINDOW = 1.0  # seconds

# Enemy
DUNGEON_ENEMY_WIDTH = 25
DUNGEON_ENEMY_HEIGHT = 50

DUNGEON_ENEMY_TYPES = {
    'grunt': {'health': 50, 'damage': 10, 'speed': 2, 'attack_range': 30},
    'archer': {'health': 30, 'damage': 15, 'speed': 3, 'attack_range': 60},
    'tank': {'health': 100, 'damage': 20, 'speed': 1, 'attack_range': 25},
    'assassin': {'health': 40, 'damage': 25, 'speed': 4, 'attack_range': 20},
    'mage': {'health': 35, 'damage': 12, 'speed': 2, 'attack_range': 50},
    'boss': {'health': 200, 'damage': 30, 'speed': 2, 'attack_range': 40},
}

DUNGEON_ENEMY_COLORS = {
    'grunt': GRAY_60,
    'archer': GREEN,
    'tank': BLUE,
    'assassin': YELLOW,
    'mage': GRAY_65,
    'boss': RED,
}

# ==================== CAMERA SETTINGS ====================

# Camera properties
CAMERA_LERP_FACTOR = 0.1
CAMERA_ZOOM_DEFAULT = 1.0
CAMERA_ZOOM_MIN = 0.1
CAMERA_ZOOM_MAX = 3.0
CAMERA_ZOOM_SPEED = 0.1

# Camera shake
CAMERA_SHAKE_INTENSITY_LIGHT = 5
CAMERA_SHAKE_INTENSITY_HEAVY = 20
CAMERA_SHAKE_DURATION_MIN = 0.1
CAMERA_SHAKE_DURATION_MAX = 1.0

# ==================== PARTICLE SYSTEM ====================

MAX_PARTICLES = 500
PARTICLE_TYPES = [
    'dust', 'blood', 'spark', 'heal', 'level_up',
    'damage', 'block', 'crit', 'warning', 'death'
]

# ==================== HUD SETTINGS ====================

# Health bar
HEALTH_BAR_POSITION = (20, 20)
HEALTH_BAR_SIZE = (200, 20)
HEALTH_BAR_COLORS = {
    'high': GREEN,
    'medium': YELLOW,
    'low': RED
}
HEALTH_BAR_BACKGROUND = GRAY_20
HEALTH_BAR_BORDER = WHITE

# XP bar
XP_BAR_POSITION = (20, 50)
XP_BAR_SIZE = (150, 15)
XP_BAR_COLOR = BLUE
XP_BAR_BACKGROUND = GRAY_20

# Level display
LEVEL_DISPLAY_POSITION = (SCREEN_WIDTH - 100, 20)
LEVEL_DISPLAY_COLOR = YELLOW

# Coin counter
COIN_COUNTER_POSITION = (20, SCREEN_HEIGHT - 30)
COIN_COUNTER_COLOR = YELLOW

# Menu settings
MENU_FADE_SPEED = 1000  # alpha per second
BUTTON_CLICK_COOLDOWN = 0.3  # seconds

# Minimap settings
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
MINIMAP_X = SCREEN_WIDTH - MINIMAP_WIDTH - 10
MINIMAP_Y = 10
MINIMAP_ZOOM = 0.5  # 0.5 = show half the world

# Score counter
SCORE_COUNTER_POSITION = (20, SCREEN_HEIGHT - 60)
SCORE_COUNTER_COLOR = WHITE

# Kills counter
KILLS_COUNTER_POSITION = (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30)
KILLS_COUNTER_COLOR = RED

# Notifications
NOTIFICATION_POSITION = (SCREEN_WIDTH // 2, 100)
NOTIFICATION_DURATION = 3.0
NOTIFICATION_FONT_SIZE = 24

# ==================== MULTIPLAYER SETTINGS ====================

# Network
DEFAULT_PORT = 25565
MAX_PLAYERS = 8
RECOMMENDED_PLAYERS = 4
UPDATE_RATE = 30  # updates per second

# Connection code
CONNECTION_CODE_LENGTH = 8
CONNECTION_CODE_FORMAT = "XXXX-XXXX"
CONNECTION_CODE_EXPIRATION = 24 * 60 * 60  # 24 hours in seconds

# Shadow Realms
SHADOW_DELAY = 1.0  # seconds
SHADOW_LIFETIME_AFTER_DEATH = 30.0  # seconds
REALM_PHASE_DURATION = 5 * 60  # 5 minutes in seconds

# Multiplayer abilities cooldowns
REALM_SWAP_COOLDOWN = 30.0
SHADOW_CLONE_COOLDOWN = 45.0
DIMENSIONAL_STRIKE_COOLDOWN = 60.0
PHASE_WALK_COOLDOWN = 90.0

# Bandwidth
BANDWIDTH_PER_PLAYER = 50  # KB/s
MIN_UPLOAD_SPEED = 512  # KB/s for 8 players

# ==================== DIFFICULTY SETTINGS ====================

DIFFICULTY_LEVELS = {
    'easy': {
        'enemy_health': 0.7,
        'enemy_damage': 0.7,
        'player_health': 1.5,
        'xp_gain': 1.2,
        'coin_drops': 1.5
    },
    'normal': {
        'enemy_health': 1.0,
        'enemy_damage': 1.0,
        'player_health': 1.0,
        'xp_gain': 1.0,
        'coin_drops': 1.0
    },
    'hard': {
        'enemy_health': 1.5,
        'enemy_damage': 1.5,
        'player_health': 0.8,
        'xp_gain': 0.8,
        'coin_drops': 0.8
    },
    'insane': {
        'enemy_health': 2.0,
        'enemy_damage': 2.0,
        'player_health': 0.5,
        'xp_gain': 0.5,
        'coin_drops': 0.5
    }
}

# Difficulty modifiers
ENRAGING_ENABLED = True
ENRAGING_TIME = 30.0  # seconds
ENRAGING_BONUS = 0.10  # 10% damage/health increase

SWARM_ENABLED = False
SWARM_MULTIPLIER = 0.50  # 50% more enemies

IRONMAN_ENABLED = False
NO_HUD_ENABLED = False
BLACKOUT_ENABLED = False

# ==================== SAVE SYSTEM ====================

NUM_SAVE_SLOTS = 5
AUTOSAVE_INTERVAL = 30.0  # seconds
QUICK_SAVE_KEY = pygame.K_F5
QUICK_LOAD_KEY = pygame.K_F9

SAVE_FILE_FORMAT = "savegame_{}.dat"
BACKUP_EXTENSION = ".bak"

# ==================== AUDIO SETTINGS ====================

# Volume levels (0.0 to 1.0)
MASTER_VOLUME = 0.8
MUSIC_VOLUME = 0.7
SFX_VOLUME = 0.8
UI_VOLUME = 0.8

# Default settings
DEFAULT_MUSIC_VOLUME = MUSIC_VOLUME
DEFAULT_SFX_VOLUME = SFX_VOLUME
DEFAULT_BRIGHTNESS = 1.0

# ==================== CONTROLS ====================

# Default key bindings
KEY_BINDINGS = {
    # Movement
    'move_up': pygame.K_w,
    'move_down': pygame.K_s,
    'move_left': pygame.K_a,
    'move_right': pygame.K_d,
    'run': pygame.K_LSHIFT,
    
    # Combat
    'light_attack': pygame.K_SPACE,
    'heavy_attack_charge': pygame.K_e,
    'block': pygame.K_q,
    'dash': pygame.K_LCTRL,
    'roll': pygame.K_LALT,
    
    # Abilities
    'whirlwind': pygame.K_r,
    'fire_attack': pygame.K_f,
    'ice_attack': pygame.K_g,
    'double_jump': pygame.K_t,
    'shadow_dash': pygame.K_y,
    
    # UI
    'pause': pygame.K_ESCAPE,
    'inventory': [pygame.K_TAB, pygame.K_i],
    'map': pygame.K_m,
    'quick_save': pygame.K_F5,
    'quick_load': pygame.K_F9,
    'menu': pygame.K_F10,
    'select': pygame.K_RETURN,
    
    # Camera
    'zoom_in': pygame.K_EQUALS,
    'zoom_out': pygame.K_MINUS,
    
    # Multiplayer
    'player_list': pygame.K_p,
    'chat': pygame.K_t,
    'toggle_chat': pygame.K_y
}

# Mouse bindings
MOUSE_BINDINGS = {
    'light_attack': 1,  # Left mouse button
    'heavy_attack_charge': 3  # Right mouse button
}

# ==================== ACHIEVEMENT SYSTEM ====================

# Achievement definitions
ACHIEVEMENTS = {
    # Combat
    'first_blood': {'name': 'First Blood', 'description': 'Kill your first enemy', 'category': 'combat'},
    'combat_master': {'name': 'Combat Master', 'description': 'Kill 1000 enemies', 'category': 'combat'},
    'combo_king': {'name': 'Combo King', 'description': 'Achieve a 10-hit combo', 'category': 'combat'},
    'critical_strike': {'name': 'Critical Strike', 'description': 'Land 10 critical hits in a row', 'category': 'combat'},
    'unyielding': {'name': 'Unyielding', 'description': 'Block 50 attacks without taking damage', 'category': 'combat'},
    'finisher': {'name': 'Finisher', 'description': 'Kill 10 enemies with heavy attacks', 'category': 'combat'},
    'executioner': {'name': 'Executioner', 'description': 'Kill 50 enemies with the killing blow', 'category': 'combat'},
    
    # Exploration
    'adventurer': {'name': 'Adventurer', 'description': 'Explore 10% of the world', 'category': 'exploration'},
    'world_traveler': {'name': 'World Traveler', 'description': 'Explore 50% of the world', 'category': 'exploration'},
    'completionist': {'name': 'Completionist', 'description': 'Explore 100% of the world', 'category': 'exploration'},
    'biome_hopper': {'name': 'Biome Hopper', 'description': 'Visit all 8 biomes', 'category': 'exploration'},
    'dungeon_delver': {'name': 'Dungeon Delver', 'description': 'Enter 10 dungeons', 'category': 'exploration'},
    'cartographer': {'name': 'Cartographer', 'description': 'Discover all dungeon entrances', 'category': 'exploration'},
    
    # Progression
    'apprentice': {'name': 'Apprentice', 'description': 'Reach level 5', 'category': 'progression'},
    'journeyman': {'name': 'Journeyman', 'description': 'Reach level 10', 'category': 'progression'},
    'master': {'name': 'Master', 'description': 'Reach level 20', 'category': 'progression'},
    'legend': {'name': 'Legend', 'description': 'Reach level 50', 'category': 'progression'},
    'wealthy': {'name': 'Wealthy', 'description': 'Collect 10,000 coins', 'category': 'progression'},
    'rich': {'name': 'Rich', 'description': 'Collect 100,000 coins', 'category': 'progression'},
    'immortal': {'name': 'Immortal', 'description': 'Reach max health without dying', 'category': 'progression'},
    
    # Enemies
    'grunt_work': {'name': 'Grunt Work', 'description': 'Kill 100 grunts', 'category': 'enemies'},
    'archer_enemy': {'name': 'Archer Enemy', 'description': 'Kill 50 archers', 'category': 'enemies'},
    'tank_buster': {'name': 'Tank Buster', 'description': 'Kill 20 tanks', 'category': 'enemies'},
    'assassins_creed': {'name': "Assassin's Creed", 'description': 'Kill 15 assassins', 'category': 'enemies'},
    'mage_slayer': {'name': 'Mage Slayer', 'description': 'Kill 10 mages', 'category': 'enemies'},
    'boss_hunter': {'name': 'Boss Hunter', 'description': 'Defeat 5 bosses', 'category': 'enemies'},
    'dragon_slayer': {'name': 'Dragon Slayer', 'description': 'Defeat the Shadow Dragon', 'category': 'enemies'},
    
    # Items
    'coin_collector': {'name': 'Coin Collector', 'description': 'Collect 1000 coins', 'category': 'items'},
    'potion_master': {'name': 'Potion Master', 'description': 'Use 50 health potions', 'category': 'items'},
    'upgrade_addict': {'name': 'Upgrade Addict', 'description': 'Collect 20 weapon upgrades', 'category': 'items'},
    'tanky': {'name': 'Tanky', 'description': 'Collect 10 armour upgrades', 'category': 'items'},
    'hoarder': {'name': 'Hoarder', 'description': 'Have 100 items in inventory', 'category': 'items'},
    
    # Multiplayer
    'host': {'name': 'Host', 'description': 'Host your first multiplayer world', 'category': 'multiplayer'},
    'joiner': {'name': 'Joiner', 'description': 'Join your first multiplayer world', 'category': 'multiplayer'},
    'social': {'name': 'Social', 'description': 'Play with 3 friends', 'category': 'multiplayer'},
    'party': {'name': 'Party', 'description': 'Play with 7 friends', 'category': 'multiplayer'},
    'shadow_master': {'name': 'Shadow Master', 'description': 'Kill 10 enemies with shadow abilities', 'category': 'multiplayer'},
    'realm_hopper': {'name': 'Realm Hopper', 'description': 'Use Realm Swap 10 times', 'category': 'multiplayer'},
    'team_player': {'name': 'Team Player', 'description': 'Deal 50% of boss damage in co-op', 'category': 'multiplayer'},
    
    # Challenges
    'no_damage': {'name': 'No Damage', 'description': 'Complete a dungeon without taking damage', 'category': 'challenges'},
    'speedrun': {'name': 'Speedrun', 'description': 'Defeat a boss in under 1 minute', 'category': 'challenges'},
    'pacifist': {'name': 'Pacifist', 'description': 'Reach level 10 without killing enemies', 'category': 'challenges'},
    'minimalist': {'name': 'Minimalist', 'description': 'Defeat 100 enemies using only light attacks', 'category': 'challenges'},
    'tank': {'name': 'Tank', 'description': 'Survive 10 hits in a row without dying', 'category': 'challenges'},
    'ironman': {'name': 'Ironman', 'description': 'Reach level 20 without dying', 'category': 'challenges'},
    
    # Secrets
    'easter_egg': {'name': 'Easter Egg', 'description': 'Find the hidden developer room', 'category': 'secrets'},
    'glitch_hunter': {'name': 'Glitch Hunter', 'description': 'Find and exploit a glitch (intentional)', 'category': 'secrets'},
    'true_ending': {'name': 'True Ending', 'description': 'Complete the secret final quest', 'category': 'secrets'},
    'all_seeing_eye': {'name': "All-Seeing Eye", 'description': 'Find the hidden observation point', 'category': 'secrets'}
}

# Achievement rewards
ACHIEVEMENT_REWARDS = {
    'xp_bonus': 0.10,  # 10% XP bonus
    'coin_bonus': 50,  # 50 coins
    'title': True,     # Unlocks a title
    'emote': True,    # Unlocks an emote
    'cosmetic': True  # Unlocks a cosmetic
}

# ==================== DEBUG SETTINGS ====================

DEBUG_ENABLED = False
DEBUG_CONSOLE_OPEN = False

# Debug commands
DEBUG_COMMANDS = [
    '/god', '/give', '/spawn', '/teleport', '/biome',
    '/fps', '/hitboxes', '/aggro', '/grid', '/kill',
    '/levelup', '/xp', '/health', '/coins', '/difficulty'
]

# ==================== PERFORMANCE SETTINGS ====================

# Rendering
RENDER_CULLING = True
RENDER_BATCHING = True
RENDER_LOD = True
RENDER_OCCLUSION = True
RENDER_STATIC_BATCHING = True

# Physics
PHYSICS_SPATIAL_PARTITIONING = True
PHYSICS_SLEEPING = True
PHYSICS_DISTANCE_CHECKS = True
PHYSICS_BROAD_PHASE = True

# Memory
MEMORY_OBJECT_POOLING = True
MEMORY_TEXTURE_ATLAS = True
MEMORY_GARBAGE_COLLECTION = True
MEMORY_STREAMING = True

# Network
NETWORK_DELTA_COMPRESSION = True
NETWORK_DISTANCE_CULLING = True
NETWORK_RATE_LIMITING = True
NETWORK_PREDICTION = True

# ==================== FILE PATHS ====================

# Asset paths
FONT_PATH = "assets/fonts/"
SOUND_PATH = "assets/sounds/"

# Default font
DEFAULT_FONT = None  # Will be loaded at runtime
DEFAULT_FONT_SIZE = 24

# ==================== UTILITY FUNCTIONS ====================

def get_gray_shade(percent):
    """Get a grayscale color based on percentage (0-100)"""
    value = int(255 * (percent / 100))
    return (value, value, value)

def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t

def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def clamp(value, min_val, max_val):
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))

def normalize_angle(angle):
    """Normalize angle to 0-360 degrees"""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def degrees_to_radians(degrees):
    """Convert degrees to radians"""
    return degrees * math.pi / 180

def radians_to_degrees(radians):
    """Convert radians to degrees"""
    return radians * 180 / math.pi

# Initialize Pygame font (will be called after Pygame init)
def init_fonts():
    global DEFAULT_FONT
    try:
        DEFAULT_FONT = pygame.font.Font(None, DEFAULT_FONT_SIZE)
    except:
        DEFAULT_FONT = pygame.font.SysFont('Arial', DEFAULT_FONT_SIZE)

# ==================== END OF CONFIG ====================

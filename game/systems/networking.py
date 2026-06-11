"""
STICK REALM: SHADOW OPEN WORLD - Networking System
Handles peer-to-peer multiplayer networking with Shadow Realms twist
"""

import socket
import threading
import queue
import json
import hashlib
import random
import string
import time
from config import *


class NetworkingSystem:
    """
    Handles peer-to-peer networking for multiplayer.
    Implements the StickNet Protocol with connection codes and Shadow Realms mechanics.
    """
    
    def __init__(self, game):
        """
        Initialize the networking system.
        game: Reference to the main game instance
        """
        self.game = game
        
        # Network state
        self.is_host = False
        self.is_client = False
        self.connected = False
        self.connection_code = None
        self.players = {}  # player_id -> player_info
        self.local_player_id = None
        
        # Socket
        self.socket = None
        self.port = DEFAULT_PORT
        
        # Threading
        self.running = False
        self.receive_thread = None
        self.send_queue = queue.Queue()
        self.message_queue = queue.Queue()
        
        # Shadow Realms
        self.shadow_realms_enabled = False
        self.realm_phase = 'normal'  # normal, convergence, divergence, eclipse
        self.realm_phase_timer = 0
        self.realm_phase_duration = REALM_PHASE_DURATION
        
        # Connection code generation
        self.code_expiration = CONNECTION_CODE_EXPIRATION
        
        # Statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
    
    def start_host(self, port=DEFAULT_PORT):
        """Start hosting a multiplayer world."""
        self.port = port
        self.is_host = True
        self.is_client = False
        self.connected = True
        
        # Generate connection code
        self.connection_code = self._generate_connection_code()
        
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind(('0.0.0.0', port))
        except Exception as e:
            print(f"Failed to bind to port {port}: {e}")
            self.connected = False
            return False
        
        # Start receive thread
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        
        # Add local player
        self.local_player_id = self._generate_player_id()
        self.players[self.local_player_id] = {
            'name': 'Host',
            'address': ('localhost', port),
            'connected': True,
            'ping': 0,
            'last_update': time.time()
        }
        
        # Enable Shadow Realms
        self.shadow_realms_enabled = True
        
        return True
    
    def connect_to_host(self, connection_code, host_address=None):
        """Connect to a hosted world."""
        self.is_host = False
        self.is_client = True
        self.connection_code = connection_code
        
        # Parse connection code to get host info
        if host_address is None:
            # In a real implementation, would use STUN/ICE to resolve the code
            # For now, we'll assume localhost
            host_address = ('localhost', DEFAULT_PORT)
        
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Generate local player ID
        self.local_player_id = self._generate_player_id()
        
        # Send handshake
        handshake = self._create_handshake_message(connection_code)
        self._send_message(handshake, host_address)
        
        # Start receive thread
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        
        # Wait for handshake response
        start_time = time.time()
        while time.time() - start_time < 5.0:  # 5 second timeout
            if not self.message_queue.empty():
                message = self.message_queue.get()
                if message['type'] == 'handshake_response':
                    self.connected = True
                    self.players[self.local_player_id] = {
                        'name': 'Player',
                        'address': None,
                        'connected': True,
                        'ping': 0,
                        'last_update': time.time()
                    }
                    return True
            time.sleep(0.1)
        
        self.connected = False
        return False
    
    def stop(self):
        """Stop networking."""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        if self.socket:
            self.socket.close()
        self.socket = None
        self.connected = False
        self.is_host = False
        self.is_client = False
        self.players = {}
    
    def _generate_connection_code(self):
        """Generate a unique connection code."""
        # Format: XXXX-XXXX
        chars = string.ascii_uppercase + string.digits
        part1 = ''.join(random.choices(chars, k=4))
        part2 = ''.join(random.choices(chars, k=4))
        return f"{part1}-{part2}"
    
    def _generate_player_id(self):
        """Generate a unique player ID."""
        return hashlib.sha256(str(time.time() + random.random()).encode()).hexdigest()[:16]
    
    def _create_handshake_message(self, connection_code):
        """Create a handshake message."""
        return {
            'type': 'handshake',
            'code': connection_code,
            'player_id': self.local_player_id,
            'player_name': 'Player',
            'version': VERSION,
            'timestamp': time.time()
        }
    
    def _create_world_snapshot(self):
        """Create a world state snapshot for new players."""
        snapshot = {
            'type': 'world_snapshot',
            'timestamp': time.time(),
            'players': {},
            'entities': []
        }
        
        # Add player info
        for player_id, player_info in self.players.items():
            snapshot['players'][player_id] = {
                'name': player_info['name'],
                'x': 0,  # Would get from actual player position
                'y': 0,
                'health': 100,
                'level': 1
            }
        
        # Add entity info (simplified)
        if hasattr(self.game, 'world'):
            for enemy in self.game.world.enemies:
                snapshot['entities'].append({
                    'type': 'enemy',
                    'enemy_type': enemy.type,
                    'x': enemy.x,
                    'y': enemy.y,
                    'health': enemy.health
                })
            
            for item in self.game.world.items:
                snapshot['entities'].append({
                    'type': 'item',
                    'item_type': item.type,
                    'x': item.x,
                    'y': item.y
                })
        
        return snapshot
    
    def _send_message(self, message, address):
        """Send a message to a specific address."""
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.sendto(data, address)
            self.packets_sent += 1
            self.bytes_sent += len(data)
        except Exception as e:
            print(f"Failed to send message: {e}")
    
    def _broadcast_message(self, message, exclude=None):
        """Broadcast a message to all connected players."""
        for player_id, player_info in self.players.items():
            if player_id == self.local_player_id:
                continue
            if exclude and player_id in exclude:
                continue
            if player_info['address']:
                self._send_message(message, player_info['address'])
    
    def _receive_loop(self):
        """Receive loop for incoming messages."""
        while self.running:
            try:
                data, address = self.socket.recvfrom(4096)
                self.bytes_received += len(data)
                self.packets_received += 1
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self._handle_message(message, address)
                except json.JSONDecodeError:
                    pass
            except socket.error:
                pass
            except Exception as e:
                print(f"Error in receive loop: {e}")
            
            # Process send queue
            while not self.send_queue.empty():
                message, address = self.send_queue.get()
                self._send_message(message, address)
            
            time.sleep(0.01)
    
    def _handle_message(self, message, address):
        """Handle an incoming message."""
        message_type = message.get('type')
        
        if message_type == 'handshake':
            self._handle_handshake(message, address)
        elif message_type == 'handshake_response':
            self._handle_handshake_response(message, address)
        elif message_type == 'world_snapshot':
            self._handle_world_snapshot(message, address)
        elif message_type == 'input':
            self._handle_input(message, address)
        elif message_type == 'state_update':
            self._handle_state_update(message, address)
        elif message_type == 'chat':
            self._handle_chat(message, address)
        elif message_type == 'event':
            self._handle_event(message, address)
        elif message_type == 'ping':
            self._handle_ping(message, address)
        elif message_type == 'disconnect':
            self._handle_disconnect(message, address)
        
        # Add to message queue for game thread
        self.message_queue.put(message)
    
    def _handle_handshake(self, message, address):
        """Handle a handshake message."""
        if not self.is_host:
            return
        
        # Validate connection code
        if message.get('code') != self.connection_code:
            return
        
        # Check version
        if message.get('version') != VERSION:
            # Send version mismatch response
            self._send_message({
                'type': 'handshake_response',
                'success': False,
                'reason': 'version_mismatch'
            }, address)
            return
        
        # Add player
        player_id = message.get('player_id')
        player_name = message.get('player_name', 'Player')
        
        self.players[player_id] = {
            'name': player_name,
            'address': address,
            'connected': True,
            'ping': 0,
            'last_update': time.time()
        }
        
        # Send handshake response
        self._send_message({
            'type': 'handshake_response',
            'success': True,
            'player_id': player_id,
            'world_state': self._create_world_snapshot()
        }, address)
        
        # Send current world state
        self._send_message(self._create_world_snapshot(), address)
    
    def _handle_handshake_response(self, message, address):
        """Handle a handshake response."""
        if message.get('success'):
            self.connected = True
            self.local_player_id = message.get('player_id')
        else:
            self.connected = False
    
    def _handle_world_snapshot(self, message, address):
        """Handle a world snapshot."""
        # Apply world state
        if hasattr(self.game, 'world'):
            # Clear existing entities
            self.game.world.enemies = []
            self.game.world.items = []
            
            # Add entities from snapshot
            for entity in message.get('entities', []):
                if entity['type'] == 'enemy':
                    self.game.world.add_enemy(
                        entity['enemy_type'],
                        entity['x'], entity['y']
                    )
                elif entity['type'] == 'item':
                    self.game.world.add_item(
                        entity['item_type'],
                        entity['x'], entity['y']
                    )
    
    def _handle_input(self, message, address):
        """Handle input from a player."""
        player_id = message.get('player_id')
        if player_id not in self.players:
            return
        
        # Update player's last update time
        self.players[player_id]['last_update'] = time.time()
        
        # In a full implementation, would apply the input to the player's shadow
        # For Shadow Realms, would update the player's shadow entity
        pass
    
    def _handle_state_update(self, message, address):
        """Handle a state update."""
        # Apply state updates to entities
        for update in message.get('updates', []):
            entity_id = update.get('entity_id')
            # In a full implementation, would find and update the entity
            pass
    
    def _handle_chat(self, message, address):
        """Handle a chat message."""
        player_id = message.get('player_id')
        text = message.get('text', '')
        
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            # Display chat message in game
            if hasattr(self.game, 'hud'):
                self.game.hud.add_chat_message(f"{player_name}: {text}")
    
    def _handle_event(self, message, address):
        """Handle an event message."""
        event_type = message.get('event_type')
        
        if event_type == 'player_death':
            player_id = message.get('player_id')
            # Create shadow entity for dead player
            pass
        elif event_type == 'boss_defeat':
            # Handle boss defeat in all realms
            pass
    
    def _handle_ping(self, message, address):
        """Handle a ping message."""
        # Send pong response
        self._send_message({
            'type': 'pong',
            'timestamp': message.get('timestamp')
        }, address)
    
    def _handle_disconnect(self, message, address):
        """Handle a disconnect message."""
        player_id = message.get('player_id')
        if player_id in self.players:
            self.players[player_id]['connected'] = False
    
    def send_input(self, input_data):
        """Send player input to the host."""
        if not self.connected or self.is_host:
            return
        
        message = {
            'type': 'input',
            'player_id': self.local_player_id,
            'input': input_data,
            'timestamp': time.time()
        }
        
        # Send to host (in a real implementation, would know host address)
        if hasattr(self.game, 'world') and self.game.world.players:
            for player_id, player_info in self.game.world.players.items():
                if player_id != self.local_player_id and player_info['address']:
                    self._send_message(message, player_info['address'])
    
    def send_chat(self, text):
        """Send a chat message."""
        if not self.connected:
            return
        
        message = {
            'type': 'chat',
            'player_id': self.local_player_id,
            'text': text,
            'timestamp': time.time()
        }
        
        if self.is_host:
            self._broadcast_message(message)
        else:
            # Send to host
            if hasattr(self.game, 'world') and self.game.world.players:
                for player_id, player_info in self.game.world.players.items():
                    if player_id != self.local_player_id and player_info['address']:
                        self._send_message(message, player_info['address'])
    
    def send_event(self, event_type, data=None):
        """Send an event message."""
        if not self.connected:
            return
        
        message = {
            'type': 'event',
            'event_type': event_type,
            'player_id': self.local_player_id,
            'data': data or {},
            'timestamp': time.time()
        }
        
        if self.is_host:
            self._broadcast_message(message)
        else:
            # Send to host
            if hasattr(self.game, 'world') and self.game.world.players:
                for player_id, player_info in self.game.world.players.items():
                    if player_id != self.local_player_id and player_info['address']:
                        self._send_message(message, player_info['address'])
    
    def update_shadow_realms(self, dt):
        """
        Update Shadow Realms state.
        dt: Time since last frame in seconds
        """
        if not self.shadow_realms_enabled:
            return
        
        self.realm_phase_timer += dt
        
        # Check for phase transition
        if self.realm_phase_timer >= self.realm_phase_duration:
            self.realm_phase_timer = 0
            
            # Cycle through phases
            if self.realm_phase == 'normal':
                self.realm_phase = 'convergence'
            elif self.realm_phase == 'convergence':
                self.realm_phase = 'divergence'
            elif self.realm_phase == 'divergence':
                self.realm_phase = 'eclipse'
            elif self.realm_phase == 'eclipse':
                self.realm_phase = 'normal'
            
            # Broadcast phase change
            self.send_event('realm_phase_change', {'phase': self.realm_phase})
    
    def get_shadow_position(self, player, delay=SHADOW_DELAY):
        """
        Get the shadow position for a player.
        player: Player entity
        delay: Shadow delay in seconds
        Returns: (x, y) shadow position
        """
        # In a full implementation, would track player's position history
        # For now, just return a position behind the player
        if player.vx > 0:
            return (player.x - 50, player.y)
        elif player.vx < 0:
            return (player.x + 50, player.y)
        else:
            return (player.x, player.y)
    
    def get_stats(self):
        """Get networking statistics."""
        return {
            'is_host': self.is_host,
            'is_client': self.is_client,
            'connected': self.connected,
            'players': len(self.players),
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'shadow_realms_enabled': self.shadow_realms_enabled,
            'realm_phase': self.realm_phase
        }
    
    def reset_stats(self):
        """Reset networking statistics."""
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0

"""
User authentication and management system
Handles user registration, login, and user data storage
"""

import json
import os
import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime


USERS_DIR = 'data/users'


def _get_users_path() -> str:
    """Returns the path to the users JSON file"""
    os.makedirs(USERS_DIR, exist_ok=True)
    return os.path.join(USERS_DIR, 'users.json')


def _load_users() -> Dict:
    """Load all users from storage"""
    users_path = _get_users_path()
    if not os.path.exists(users_path):
        return {}
    try:
        with open(users_path, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}


def _save_users(users: Dict) -> None:
    """Save users to storage"""
    users_path = _get_users_path()
    try:
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"Error saving users: {e}")


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def _verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash"""
    try:
        salt, stored_hash = password_hash.split(':')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    except ValueError:
        return False


def register_user(username: str, password: str) -> tuple[bool, Optional[str]]:
    """
    Register a new user
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    if not username or not password:
        return False, "Username and password are required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    users = _load_users()
    
    # Check if username already exists
    if username.lower() in {u.lower() for u in users.keys()}:
        return False, "Username already exists"
    
    # Create new user
    user_id = secrets.token_urlsafe(16)
    users[username] = {
        'user_id': user_id,
        'username': username,
        'password_hash': _hash_password(password),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    _save_users(users)
    return True, None


def authenticate_user(username: str, password: str) -> tuple[bool, Optional[Dict]]:
    """
    Authenticate a user
    
    Returns:
        (success: bool, user_data: Optional[Dict])
    """
    if not username or not password:
        return False, None
    
    users = _load_users()
    
    # Find user (case-insensitive)
    user_key = None
    for key in users.keys():
        if key.lower() == username.lower():
            user_key = key
            break
    
    if not user_key:
        return False, None
    
    user = users[user_key]
    
    # Verify password
    if not _verify_password(password, user['password_hash']):
        return False, None
    
    # Return user data (without password hash)
    return True, {
        'user_id': user['user_id'],
        'username': user['username']
    }


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user data by user_id"""
    users = _load_users()
    for user_data in users.values():
        if user_data.get('user_id') == user_id:
            return {
                'user_id': user_data['user_id'],
                'username': user_data['username']
            }
    return None


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user data by username"""
    users = _load_users()
    user_key = None
    for key in users.keys():
        if key.lower() == username.lower():
            user_key = key
            break
    
    if not user_key:
        return None
    
    user = users[user_key]
    return {
        'user_id': user['user_id'],
        'username': user['username']
    }


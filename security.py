"""
Password validation utilities for production security.
"""
import re
from typing import Tuple

# Reserved usernames that cannot be registered
RESERVED_USERNAMES = {
    # System accounts
    'admin', 'administrator', 'root', 'system', 'sysadmin', 'superuser',
    'moderator', 'mod', 'support', 'help', 'helpdesk',
    
    # App-specific
    'odoyewu', 'nearlove', 'official', 'staff', 'team', 'bot',
    
    # Common reserved
    'api', 'www', 'mail', 'email', 'webmaster', 'postmaster',
    'hostmaster', 'info', 'contact', 'sales', 'marketing',
    
    # Prevent impersonation
    'null', 'undefined', 'none', 'anonymous', 'guest', 'user',
    'test', 'demo', 'example', 'sample',
    
    # Security
    'security', 'abuse', 'noreply', 'no-reply', 'mailer-daemon',
    
    # Social
    'everyone', 'all', 'here', 'channel', 'group',
    
    # Profanity/inappropriate (add more as needed)
    'fuck', 'shit', 'ass', 'bitch', 'damn', 'porn', 'sex',
}

def is_username_reserved(username: str) -> bool:
    """Check if username is reserved"""
    return username.lower() in RESERVED_USERNAMES

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username/handle meets requirements.
    
    Requirements:
    - 3-30 characters
    - Alphanumeric, underscores, hyphens only
    - Must start with letter or number
    - Not reserved
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must be no more than 30 characters long"
    
    # Check format (alphanumeric, underscores, hyphens)
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter or number and contain only letters, numbers, underscores, and hyphens"
    
    # Check reserved
    if is_username_reserved(username):
        return False, "This username is reserved and cannot be used"
    
    # Check for consecutive special characters
    if re.search(r'[_-]{2,}', username):
        return False, "Username cannot contain consecutive underscores or hyphens"
    
    # Cannot end with underscore or hyphen
    if username.endswith('_') or username.endswith('-'):
        return False, "Username cannot end with an underscore or hyphen"
    
    return True, ""

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    # Check for common weak passwords
    weak_passwords = [
        "password", "12345678", "qwerty", "abc123", "password123",
        "admin123", "letmein", "welcome", "monkey", "dragon"
    ]
    if password.lower() in weak_passwords:
        return False, "This password is too common. Please choose a stronger password"
    
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    return True, ""

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Limit length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text.strip()

"""
TEST CASE 4: Admin Dashboard
Vulnerabilities: Authentication Bypass, Weak Crypto, Information Disclosure
"""

import hashlib
import base64
from datetime import datetime

# VULNERABILITY 1: Multiple hardcoded secrets
MASTER_PASSWORD = "P@ssw0rd2024!"
ENCRYPTION_KEY = "1234567890123456"  # Weak 16-char key
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"

class AdminDashboard:
    def __init__(self):
        self.logged_in_users = {}
    
    def admin_login(self, username, password):
        """Admin authentication"""
        # VULNERABILITY 2: Weak password check (hardcoded comparison)
        if username == "admin" and password == MASTER_PASSWORD:
            return True
        
        # VULNERABILITY 3: SQL Injection in admin check
        import sqlite3
        conn = sqlite3.connect('admin.db')
        query = f"SELECT * FROM admins WHERE username='{username}' AND password='{password}'"
        result = conn.execute(query).fetchone()
        return result is not None
    
    def hash_password(self, password):
        """Hash user passwords"""
        # VULNERABILITY 4: Weak hashing algorithm (MD5)
        return hashlib.md5(password.encode()).hexdigest()
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        # VULNERABILITY 5: Weak encryption (base64 is not encryption!)
        return base64.b64encode(data.encode()).decode()
    
    def log_admin_action(self, action, user_id):
        """Log administrative actions"""
        import sqlite3
        conn = sqlite3.connect('logs.db')
        
        # VULNERABILITY 6: SQL Injection in logging
        timestamp = datetime.now().isoformat()
        query = f"INSERT INTO admin_logs (action, user_id, timestamp) VALUES ('{action}', {user_id}, '{timestamp}')"
        conn.execute(query)
        conn.commit()
    
    def get_user_data(self, user_id):
        """Retrieve user data"""
        import sqlite3
        conn = sqlite3.connect('users.db')
        
        # VULNERABILITY 7: SQL Injection + Information Disclosure
        query = f"SELECT * FROM users WHERE id = {user_id}"
        user = conn.execute(query).fetchone()
        
        # VULNERABILITY 8: Information Disclosure - returning sensitive fields
        return {
            'id': user[0],
            'username': user[1],
            'password_hash': user[2],  # Exposing password hash!
            'ssn': user[3],            # Exposing SSN!
            'credit_card': user[4]     # Exposing credit card!
        }
    
    def delete_user_account(self, user_id):
        """Delete user account"""
        import sqlite3
        conn = sqlite3.connect('users.db')
        
        # VULNERABILITY 9: SQL Injection in delete
        query = "DELETE FROM users WHERE id = " + str(user_id)
        conn.execute(query)
        conn.commit()

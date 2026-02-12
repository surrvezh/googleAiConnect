"""
SECURE VERSION - How the vulnerable_app.py SHOULD look

This demonstrates what the Security Guardian agent suggests as fixes.
"""

import sqlite3
from flask import Flask, request, render_template, escape
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)

# FIX 1: Use environment variables for secrets
DB_PASSWORD = os.getenv('DB_PASSWORD')
API_KEY = os.getenv('API_KEY')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')


def get_db_connection():
    """Connect to database"""
    # FIX 2: Use environment variable for connection string
    db_path = os.getenv('DB_PATH', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # FIX 3: Use parameterized queries to prevent SQL injection
    conn = get_db_connection()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    user = conn.execute(query, (username, password)).fetchone()
    
    if user:
        return {"status": "success", "user": dict(user)}
    else:
        return {"status": "failed"}


@app.route('/search', methods=['GET'])
def search():
    """Search users endpoint"""
    search_term = request.args.get('q', '')
    
    # FIX 4: Use parameterized query with LIKE
    conn = get_db_connection()
    query = "SELECT * FROM users WHERE name LIKE ?"
    results = conn.execute(query, (f'%{search_term}%',)).fetchall()
    
    return {"results": [dict(row) for row in results]}


@app.route('/profile/<int:user_id>')
def profile(user_id):
    """User profile endpoint"""
    conn = get_db_connection()
    
    # FIX 5: Use parameterized query and type hints
    query = "SELECT * FROM users WHERE id = ?"
    user = conn.execute(query, (user_id,)).fetchone()
    
    if not user:
        return {"error": "User not found"}, 404
    
    # FIX 6: Use template rendering with auto-escaping
    return render_template('profile.html', user=dict(user))


@app.route('/download')
def download_file():
    """File download endpoint"""
    filename = request.args.get('file', '')
    
    # FIX 7: Prevent path traversal
    # Validate filename and use secure path joining
    import re
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        return {"error": "Invalid filename"}, 400
    
    # Use secure path joining
    base_dir = "/var/data/"
    file_path = os.path.abspath(os.path.join(base_dir, filename))
    
    # Ensure the resolved path is still within base_dir
    if not file_path.startswith(os.path.abspath(base_dir)):
        return {"error": "Access denied"}, 403
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"error": "File not found"}, 404


@app.route('/execute')
def execute_command():
    """Execute system command (admin only)"""
    # FIX 8: Remove or properly restrict command execution
    return {"error": "Command execution disabled for security"}, 403
    
    # If absolutely needed, use allowlist of safe commands:
    # ALLOWED_COMMANDS = {'status': 'systemctl status', 'uptime': 'uptime'}
    # cmd_key = request.args.get('cmd')
    # if cmd_key in ALLOWED_COMMANDS:
    #     result = os.system(ALLOWED_COMMANDS[cmd_key])
    #     return {"result": result}


# FIX 9: Disable debug mode in production
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)

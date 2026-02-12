"""
Sample vulnerable Flask app for testing Security Guardian.

This file contains multiple security vulnerabilities:
1. SQL Injection
2. Hardcoded credentials
3. Insecure file operations
4. Weak password handling

Perfect for demonstrating the agent's capabilities!
"""

import sqlite3
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Database Credentials
DB_PASSWORD = "super_secret_password_123"
API_KEY = "sk-abc123def456ghi789"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


def get_db_connection():
    """Connect to database"""
    # VULNERABILITY 2: Hardcoded connection string
    conn = sqlite3.connect('database.db')
    return conn


@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # VULNERABILITY 3: SQL Injection via string concatenation
    conn = get_db_connection()
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    user = conn.execute(query).fetchone()
    
    if user:
        return {"status": "success", "user": user}
    else:
        return {"status": "failed"}


@app.route('/search', methods=['GET'])
def search():
    """Search users endpoint"""
    search_term = request.args.get('q')
    
    # VULNERABILITY 4: SQL Injection via f-string
    conn = get_db_connection()
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    results = conn.execute(query).fetchall()
    
    return {"results": results}


@app.route('/profile/<user_id>')
def profile(user_id):
    """User profile endpoint"""
    conn = get_db_connection()
    
    # VULNERABILITY 5: SQL Injection via format()
    query = "SELECT * FROM users WHERE id = {}".format(user_id)
    user = conn.execute(query).fetchone()
    
    # VULNERABILITY 6: XSS via direct rendering
    html = f"<h1>Profile: {user[1]}</h1>"
    return render_template_string(html)


@app.route('/download')
def download_file():
    """File download endpoint"""
    filename = request.args.get('file')
    
    # VULNERABILITY 7: Path Traversal
    file_path = "/var/data/" + filename
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    return {"content": content}


@app.route('/execute')
def execute_command():
    """Execute system command (admin only)"""
    cmd = request.args.get('cmd')
    
    # VULNERABILITY 8: Command Injection
    result = os.system(cmd)
    
    return {"result": result}


# VULNERABILITY 9: Debug mode in production
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

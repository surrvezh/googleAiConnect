"""
TEST CASE 3: API Server
Vulnerabilities: Authentication Issues, Command Injection, Insecure Deserialization
"""

import os
import pickle
import subprocess
import json

# VULNERABILITY 1: Hardcoded API credentials
ADMIN_PASSWORD = "admin123"
JWT_SECRET = "supersecretkey123"
DATABASE_URL = "postgresql://admin:password123@db.example.com:5432/prod"

class APIServer:
    def __init__(self):
        self.admin_token = "Bearer admin_token_12345"
    
    def execute_system_command(self, command):
        """Execute system commands for admin tasks"""
        # VULNERABILITY 2: Command Injection - user input directly in shell
        result = os.system(command)
        return result
    
    def run_diagnostic(self, server_name):
        """Run network diagnostics"""
        # VULNERABILITY 3: Command Injection via subprocess
        cmd = f"ping -c 4 {server_name}"
        output = subprocess.run(cmd, shell=True, capture_output=True)
        return output.stdout
    
    def deserialize_user_data(self, data):
        """Load user preferences from serialized data"""
        # VULNERABILITY 4: Insecure Deserialization (pickle)
        user_prefs = pickle.loads(data)
        return user_prefs
    
    def evaluate_expression(self, expr):
        """Evaluate mathematical expressions"""
        # VULNERABILITY 5: Code Injection via eval()
        result = eval(expr)
        return result
    
    def execute_user_script(self, script_code):
        """Execute user-provided scripts"""
        # VULNERABILITY 6: Code Injection via exec()
        exec(script_code)
        return "Script executed"
    
    def backup_database(self, backup_path):
        """Backup database to specified path"""
        # VULNERABILITY 7: Command Injection in backup
        command = f"mysqldump -u admin -p{ADMIN_PASSWORD} mydb > {backup_path}"
        os.system(command)

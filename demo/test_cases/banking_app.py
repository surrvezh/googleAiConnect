"""
TEST CASE 1: Banking Application
Vulnerabilities: SQL Injection, Hardcoded Credentials, Weak Authentication
"""

import sqlite3
import hashlib

# VULNERABILITY 1: Hardcoded database credentials
DB_HOST = "production-db.bank.com"
DB_PASSWORD = "P@ssw0rd123!"
DB_USER = "admin"
API_SECRET_KEY = "sk_live_51KZqYq2eZvKYlo2CTEST123456789"

class BankingSystem:
    def __init__(self):
        self.conn = sqlite3.connect('banking.db')
    
    def transfer_money(self, from_account, to_account, amount):
        """Transfer money between accounts"""
        # VULNERABILITY 2: SQL Injection via string concatenation
        query = "UPDATE accounts SET balance = balance - " + str(amount) + \
                " WHERE account_number = '" + from_account + "'"
        self.conn.execute(query)
        
        query2 = "UPDATE accounts SET balance = balance + " + str(amount) + \
                 " WHERE account_number = '" + to_account + "'"
        self.conn.execute(query2)
        
        # VULNERABILITY 3: SQL Injection in transaction log
        log_query = f"INSERT INTO transactions (from_acc, to_acc, amount) VALUES ('{from_account}', '{to_account}', {amount})"
        self.conn.execute(log_query)
        
        self.conn.commit()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        # VULNERABILITY 4: SQL Injection in authentication
        query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
        result = self.conn.execute(query).fetchone()
        
        # VULNERABILITY 5: Weak password hashing (MD5)
        hashed = hashlib.md5(password.encode()).hexdigest()
        
        return result is not None
    
    def get_account_balance(self, account_id):
        """Get account balance"""
        # VULNERABILITY 6: SQL Injection via format()
        query = "SELECT balance FROM accounts WHERE id = {}".format(account_id)
        return self.conn.execute(query).fetchone()
    
    def search_transactions(self, search_term):
        """Search transactions by description"""
        # VULNERABILITY 7: SQL Injection in search
        query = f"SELECT * FROM transactions WHERE description LIKE '%{search_term}%' OR amount > {search_term}"
        return self.conn.execute(query).fetchall()

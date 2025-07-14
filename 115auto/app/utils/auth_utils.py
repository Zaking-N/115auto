import os
import hashlib
from functools import wraps
from flask import session, redirect, url_for

class AuthManager:
    def __init__(self):
        # 在实际应用中，应该使用数据库存储用户信息
        self.users = {
            'admin': {
                'password': self._hash_password('admin123'),
                'role': 'admin'
            }
        }
    
    def _hash_password(self, password):
        """密码哈希处理"""
        salt = os.getenv('SECRET_KEY', 'default-secret-key')
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def authenticate(self, username, password):
        """用户认证"""
        user = self.users.get(username)
        if user and user['password'] == self._hash_password(password):
            return True
        return False
    
    def login_required(self, f):
        """登录装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def admin_required(self, f):
        """管理员装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != 'admin':
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
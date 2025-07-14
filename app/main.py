import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from utils.file_utils import FileOrganizer
from utils.auth_utils import AuthManager
import json
from pathlib import Path

# 初始化应用
app = Flask(__name__)

# 加载配置
config_path = os.getenv('CONFIG_PATH', 'config/app/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

app.secret_key = os.getenv('SECRET_KEY', config['app']['secret_key'])
app.config['UPLOAD_FOLDER'] = '/data/media'

# 初始化工具
file_organizer = FileOrganizer(config_path)
auth_manager = AuthManager()

# 设置日志
log_path = config['app']['logging']['path']
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    level=config['app']['logging']['level'],
    format=config['app']['logging']['format'],
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if auth_manager.authenticate(username, password):
            session['user_id'] = username
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/scan', methods=['POST'])
def scan_files():
    try:
        # 这里应该是实际的115网盘扫描逻辑
        files = file_organizer.scan_115_files(session.get('cookie'))
        return jsonify({'status': 'success', 'files': files})
    except Exception as e:
        logger.error(f"Scan error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/organize', methods=['POST'])
def organize_files():
    try:
        data = request.get_json()
        result = file_organizer.organize_files(
            data.get('files', []),
            data.get('rules', {})
        )
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        logger.error(f"Organize error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files')
def get_files():
    try:
        # 模拟返回文件数据
        files = [
            {"name": "Movie.2020.mp4", "size": 1024**3, "type": "movie"},
            {"name": "TV.Show.S01E01.mkv", "size": 1024**2*800, "type": "tv"}
        ]
        return jsonify({
            'status': 'success',
            'total_files': len(files),
            'movie_count': len([f for f in files if f['type'] == 'movie']),
            'tv_count': len([f for f in files if f['type'] == 'tv']),
            'files': files
        })
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['app']['port'])
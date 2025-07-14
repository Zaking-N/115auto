import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

class FileOrganizer:
    def __init__(self, config_path='config/app/config.json'):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def scan_115_files(self, cookie, cid="0"):
        """扫描115网盘文件"""
        if not cookie:
            raise ValueError("Cookie is required")
            
        self.session.headers.update({
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            url = f"{self.config['115_api']['base_url']}{self.config['115_api']['endpoints']['files']}"
            params = {
                'aid': 1,
                'cid': cid,
                'o': 'user_ptime',
                'asc': 0,
                'offset': 0,
                'limit': 1000,
                'show_dir': 1,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params, timeout=self.config['115_api']['timeout'])
            response.raise_for_status()
            
            data = response.json()
            if data.get('state'):
                return self._process_files(data.get('data', []))
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to scan 115 files: {str(e)}")
            raise
    
    def _process_files(self, files):
        """处理文件列表"""
        result = []
        for item in files:
            if item.get('fid'):
                file_info = {
                    'id': item['fid'],
                    'name': item.get('n', ''),
                    'size': item.get('s', 0),
                    'type': self._determine_file_type(item),
                    'path': item.get('p', ''),
                    'modified': item.get('t', '')
                }
                result.append(file_info)
        return result
    
    def _determine_file_type(self, file_item):
        """确定文件类型"""
        name = file_item.get('n', '').lower()
        
        # 如果是文件夹
        if file_item.get('f', 0) == 1:
            return 'folder'
            
        # 视频文件
        video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
        if any(name.endswith(ext) for ext in video_exts):
            if re.search(r'[sS]\d{1,2}[eE]\d{1,2}', name):
                return 'tv'
            return 'movie'
            
        return 'other'
    
    def organize_files(self, files, rules):
        """整理文件"""
        organized = {'movie': 0, 'tv': 0, 'other': 0}
        
        for file in files:
            try:
                target_folder = self._determine_target_folder(file['name'], rules)
                # 这里应该是实际的115网盘移动文件操作
                # move_result = self._move_file(file['id'], target_folder)
                organized[target_folder.split('/')[0].lower()] += 1
            except Exception as e:
                self.logger.error(f"Failed to organize file {file['name']}: {str(e)}")
                continue
                
        return organized
    
    def _determine_target_folder(self, filename, rules):
        """确定目标文件夹"""
        # 尝试匹配电视剧
        tv_match = re.search(r'(.+?)[sS](\d{1,2})[eE](\d{1,2})', filename)
        if tv_match:
            show_name = tv_match.group(1).replace('.', ' ').strip()
            season_num = int(tv_match.group(2))
            return f"TV Shows/{show_name}/Season {season_num}"
        
        # 尝试匹配电影
        year_match = re.search(r'(.+?)(19|20)\d{2}', filename)
        if year_match:
            movie_name = year_match.group(1).replace('.', ' ').strip()
            year = year_match.group(2)
            return f"Movies/{movie_name} ({year})"
            
        return "Other"
    
    def _move_file(self, file_id, target_folder):
        """移动文件到目标文件夹"""
        # 这里实现实际的115网盘API调用
        pass
document.addEventListener('DOMContentLoaded', function() {
    // 初始化文件列表
    loadFiles();
    
    // 绑定按钮事件
    document.getElementById('scan-btn').addEventListener('click', scanFiles);
    document.getElementById('organize-btn').addEventListener('click', organizeFiles);
    document.getElementById('logout-btn').addEventListener('click', logout);
});

function loadFiles() {
    fetch('/api/files')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateFileStats(data);
                renderFileList(data.files);
            } else {
                showError(data.message);
            }
        })
        .catch(error => {
            showError('Failed to load files');
            console.error('Error:', error);
        });
}

function scanFiles() {
    const button = document.getElementById('scan-btn');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    
    fetch('/api/scan', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showSuccess('Files scanned successfully');
            loadFiles();
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        showError('Failed to scan files');
        console.error('Error:', error);
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-sync-alt"></i> Scan Files';
    });
}

function organizeFiles() {
    const button = document.getElementById('organize-btn');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Organizing...';
    
    fetch('/api/organize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            rules: getOrganizationRules()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showSuccess('Files organized successfully');
            loadFiles();
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        showError('Failed to organize files');
        console.error('Error:', error);
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-folder"></i> Organize Files';
    });
}

function updateFileStats(data) {
    document.getElementById('total-files').textContent = data.total_files;
    document.getElementById('movie-count').textContent = data.movie_count;
    document.getElementById('tv-count').textContent = data.tv_count;
}

function renderFileList(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        fileItem.innerHTML = `
            <div class="file-icon">
                <i class="fas ${file.type === 'movie' ? 'fa-film' : 'fa-tv'}"></i>
            </div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${formatFileSize(file.size)}</div>
            <div class="file-actions">
                <button class="btn btn-small" onclick="previewFile('${file.name}')">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        `;
        
        fileList.appendChild(fileItem);
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getOrganizationRules() {
    // 这里可以从UI获取分类规则
    return {
        movie: {
            pattern: /(.*?)\.(19|20)\d{2}\./i,
            folder: 'movies'
        },
        tv: {
            pattern: /(.*?)\.s\d{2}e\d{2}\./i,
            folder: 'tv_shows'
        }
    };
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.textContent = message;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger';
    alert.textContent = message;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}

function logout() {
    fetch('/logout', {
        method: 'POST'
    }).then(() => {
        window.location.href = '/login';
    });
}
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorElement = document.getElementById('error-message');
            
            // 简单验证
            if (!username || !password) {
                errorElement.textContent = 'Please enter both username and password';
                return;
            }
            
            // 这里应该是实际的登录请求
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.text();
                }
            })
            .then(text => {
                try {
                    const data = JSON.parse(text);
                    errorElement.textContent = data.error || 'Login failed';
                } catch {
                    errorElement.textContent = 'Login failed';
                }
            })
            .catch(error => {
                errorElement.textContent = 'Network error';
                console.error('Error:', error);
            });
        });
    }
});
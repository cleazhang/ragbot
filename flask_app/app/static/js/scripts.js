// 全局变量
let currentFiles = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面
    if (document.getElementById('loginForm')) {
        initAuthPage();
    } else if (document.getElementById('chatContainer')) {
        initChatPage();
    }
});

// 初始化认证页面
function initAuthPage() {
    // 标签切换
    const tabBtns = document.querySelectorAll('.tab-btn');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (tab === 'login') {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
        });
    });
    
    // 登录表单
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const errorDiv = document.getElementById('loginError');
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    window.location.href = '/';
                } else {
                    errorDiv.textContent = data.message || 'Login failed';
                    errorDiv.classList.add('show');
                }
            } catch (error) {
                errorDiv.textContent = 'Network error';
                errorDiv.classList.add('show');
            }
        });
    }
    
    // 注册表单
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('registerUsername')?.value || 
                           document.getElementById('username')?.value;
            const password = document.getElementById('registerPassword')?.value || 
                           document.getElementById('password')?.value;
            const errorDiv = document.getElementById('registerError');
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });
                
                const data = await response.json();
                
                if (response.ok || response.status === 201) {
                    alert('Registration successful. Please log in.');
                    if (tabBtns.length > 0) {
                        tabBtns[0].click();
                    } else {
                        window.location.href = '/login';
                    }
                } else {
                    errorDiv.textContent = data.message || 'Registration failed';
                    errorDiv.classList.add('show');
                }
            } catch (error) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.classList.add('show');
            }
        });
    }
}

// 初始化聊天页面
function initChatPage() {
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const clearFilesBtn = document.getElementById('clearFilesBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    
    // 输入框自动调整高度
    questionInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        sendBtn.disabled = !this.value.trim();
    });
    
    // Enter发送，Shift+Enter换行
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) {
                sendMessage();
            }
        }
    });
    
    // 发送按钮
    sendBtn.addEventListener('click', sendMessage);
    
    // 上传文件
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    
    // 清空文件
    clearFilesBtn.addEventListener('click', clearFiles);
    
    // 退出登录
    logoutBtn.addEventListener('click', async function() {
        try {
            await fetch('/logout');
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
        }
    });
    
    // 新建对话
    newChatBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the current conversation history?')) {
            clearHistory();
        }
    });
    
    // 加载用户名
    loadUserInfo();
}

// 发送消息
async function sendMessage() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) return;
    
    // 添加用户消息到界面
    addMessage('user', question);
    
    // 清空输入框
    questionInput.value = '';
    questionInput.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;
    
    // 显示加载提示
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('query', question);
        
        const response = await fetch('/ask', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 添加AI回复
            addMessage('assistant', data.answer, data.retrieved_result);
        } else {
            addMessage('assistant', 'An error occurred:' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        addMessage('assistant', 'Network error. Please check your connection and try again.');
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// 添加消息到聊天界面
function addMessage(role, content, retrievedDocs = null) {
    const chatContainer = document.getElementById('chatContainer');
    
    // 移除欢迎消息
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);
    
    // 添加时间戳
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    messageDiv.appendChild(timeDiv);
    
    // 添加检索到的文档
    if (retrievedDocs && retrievedDocs.length > 0) {
        const docsDiv = document.createElement('div');
        docsDiv.className = 'retrieved-docs';
        docsDiv.innerHTML = '<div class="retrieved-docs-title">📄 Reference Documentation: </div>';
        
        retrievedDocs.slice(0, 3).forEach((doc, index) => {
            const docItem = document.createElement('div');
            docItem.className = 'retrieved-doc-item';
            docItem.textContent = doc.substring(0, 200) + (doc.length > 200 ? '...' : '');
            docsDiv.appendChild(docItem);
        });
        
        messageDiv.appendChild(docsDiv);
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 处理文件上传
async function handleFileUpload(e) {
    const files = e.target.files;
    if (files.length === 0) return;
    
    showLoading();
    
    try {
        const formData = new FormData();
        for (let file of files) {
            formData.append('file', file);
        }
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            // 更新文件列表
            const uploadedFiles = Array.from(files).map(f => f.name);
            currentFiles = currentFiles.concat(uploadedFiles);
            updateFileList();
            alert('Files uploaded successfully! Total files uploaded: ' + uploadedFiles.length);
        } else {
            const data = await response.json().catch(() => ({message: 'Server error'}));
            alert('Upload failed:' + (data.message || 'Unknown error (status code: ' + response.status + ')'));
        }
    } catch (error) {
        alert('Upload failed: Network error - ' + error.message);
        console.error('Upload error:', error);
    } finally {
        hideLoading();
        e.target.value = ''; // 清空文件选择
    }
}

// 更新文件列表显示
function updateFileList() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    
    if (currentFiles.length === 0) {
        fileList.innerHTML = '<div class="file-item">No files available</div>';
        return;
    }
    
    currentFiles.forEach(fileName => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.textContent = fileName;
        fileList.appendChild(fileItem);
    });
}

// 清空文件
async function clearFiles() {
    if (!confirm('Are you sure you want to clear all uploaded documents?')) return;
    
    showLoading();
    
    try {
        const response = await fetch('/clear_uploads', {
            method: 'POST'
        });
        
        if (response.ok) {
            currentFiles = [];
            updateFileList();
            alert('All documents have been cleared.');
        } else {
            alert('Failed to clear.');
        }
    } catch (error) {
        alert('Network error');
        console.error('Clear files error:', error);
    } finally {
        hideLoading();
    }
}

// 清除历史记录
async function clearHistory() {
    try {
        const response = await fetch('/clear_history', {
            method: 'POST'
        });
        
        if (response.ok) {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = `
                <div class="welcome-message">
                    <h1>Welcome to the RAG Intelligent Q&A System</h1>
                    <p>After you upload documents, I can answer your questions based on their content.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Clear history error:', error);
    }
}

// 加载用户信息
async function loadUserInfo() {
    // 这里可以从session获取，暂时显示默认值
    const usernameEl = document.getElementById('username');
    if (usernameEl) {
        // 可以添加一个API来获取当前用户信息
        usernameEl.textContent = 'User';
    }
}

// 显示/隐藏加载提示
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

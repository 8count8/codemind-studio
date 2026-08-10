// JavaScript Document

document.addEventListener('DOMContentLoaded', () => {
    // 主题切换功能
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const body = document.body;

    // 初始化主题
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });

    function setTheme(theme) {
        body.setAttribute('data-theme', theme);
        themeIcon.textContent = theme === 'dark' ? '🌙' : '🌞';
    }

    // 用户状态管理
     let currentUser = null; // 新增用户对象变量
    let isLoggedIn = false;
    const userMenu = document.getElementById('user-menu');
    const loginBtn = document.getElementById('login-btn');
    const userAvatarContainer = document.getElementById('user-avatar-container');
    const userAvatar = document.getElementById('user-avatar');
    const userDropdown = document.getElementById('user-dropdown');


    function checkLoginStatus() {
        // 实际应从后端获取登录状态
        fetch('/auth/status')
      .then(res => {
            if (!res.ok) {
                throw new Error(`网络请求失败，状态码: ${res.status}`);
            }
            return res.json();
        })
      .then(data => {
            isLoggedIn = data.isAuthenticated;
            updateUserUI(data.user);
        })
      .catch(error => {
            console.error('检查登录状态时出错:', error);
            // 可以添加更多调试信息，例如请求地址
            console.log('请求地址:', '/auth/status');
        });
    }

    function updateUserUI(user = null) {
        const userMenu = document.getElementById('user-menu');
    console.log('用户菜单元素:', userMenu);  // 输出用户菜单元素，确认是否选择正确
    if (isLoggedIn && user) {
        userMenu.innerHTML = `
            <div class="user-info" id="user-info">
                <img src="/static/img/user_icon.png"
                     class="user-avatar"
                     alt="用户头像"
                     id="user-avatar">
                <div class="user-details">
                    <span class="username">${user.username}</span>
                </div>
            </div>
        `;
    } else {
        userMenu.innerHTML = '<button class="btn btn-login" id="login-btn">登录</button>';
    }
     // 重新绑定事件
        bindEvents();
}
// 绑定事件
    function bindEvents() {
        // 登录按钮事件
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => {
                window.location.href = '/login';
            });
        }
        // 用户头像点击事件
        const userAvatar = document.getElementById('user-avatar');
        if (userAvatar) {
            userAvatar.addEventListener('click', (e) => {
                e.stopPropagation(); 
                userDropdown.classList.toggle('active');
            });
        }
    }

    // 收藏题目功能
    const favoritesList = document.getElementById('favorites-list');

    function loadFavorites() {
        const favoritesList = document.getElementById('favorites-list');
        if (!favoritesList) {
            console.error('收藏列表容器未找到');
            return;
        }

        fetch('/api/user/favorites')
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.status !== 200) {
                    throw new Error(data.message || '获取收藏失败');
                }
                renderFavorites(data.data || []);
            })
            .catch(error => {
                console.error('获取收藏失败:', error);
                favoritesList.innerHTML = `
                    <div class="error">
                        加载收藏失败: ${error.message}
                        <button onclick="loadFavorites()">重试</button>
                    </div>`;
            });
    }

    function renderFavorites(favorites) {
        const favoritesList = document.getElementById('favorites-list');
        if (!favoritesList) {
            console.error('收藏列表容器未找到');
            return;
        }

        if (favorites.length === 0) {
            favoritesList.innerHTML = '<div class="empty">暂无收藏题目</div>';
            return;
        }

        favoritesList.innerHTML = favorites.map(fav => `
            <div class="favorite-item" data-id="${fav.id}">
                <h4>${fav.title}</h4>
                <p>难度：{fav.difficulty}</p>
            </div>
        `).join('');

// 添加点击事件
        document.querySelectorAll('.favorite-item').forEach(item => {
            item.addEventListener('click', () => {
                window.location.href = `/problems/${item.dataset.id}`;
            });
        });
    }

    // 初始化
    checkLoginStatus();
    loadFavorites();

    // 用户菜单交互
    document.body.addEventListener('click', (e) => {
        if (e.target.closest('#user-avatar')) {
            userDropdown.classList.toggle('active');
        } else {
            userDropdown.classList.remove('active');
        }
    });

    // 登录功能
     loginBtn?.addEventListener('click', () => {
        // 检查是否已登录
        if (!isLoggedIn) {
            // 跳转到登录页面
            window.location.href = 'login';
        }
    });

    // 退出登录
    document.getElementById('logout-btn').addEventListener('click', () => {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        if (!csrfToken) {
            console.error('CSRF令牌未找到！');
            return;
        }
    
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok || response.status === 304) {
                throw new Error('退出失败');
            }
            return response.json();
        })
        .then(() => {
            isLoggedIn = false;
            updateUserUI();
            userDropdown.classList.remove('active');
            window.location.href = '/login'; // 重定向到登录页
        })
        .catch(error => {
            console.error('退出登录失败:', error);
            alert('退出登录失败，请重试');
        });
    });

    // 功能模块跳转逻辑
    document.querySelectorAll('.module-card').forEach(card => {
        card.addEventListener('click', () => {
            const module = card.getAttribute('data-module');
            switch (module) {
                case 'practice':
                    window.location.href = 'quizbank';
                    break;
                case 'ai-question':
                    window.location.href = 'ai-question';
                    break;
                case 'ai-review':
                    window.location.href = 'code-review';
                    break;
                case 'ability-matrix':
                    window.location.href = 'ability-matrix';
                    break;
                default:
                    console.warn(`未知模块: ${module}`);
            }
        });
    });
    })


    document.addEventListener('click', (e) => {
        const isClickInside = e.target.closest('#user-avatar') || 
                         e.target.closest('.user-dropdown');
        if (!isClickInside) {
            userDropdown.classList.remove('active');
        }
    });



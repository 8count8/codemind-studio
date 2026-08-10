
document.addEventListener('DOMContentLoaded', function() {
    // 主题切换功能
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    const body = document.body;

    if (!themeToggle || !themeIcon || !themeText) {
        console.error("关键元素缺失");
        return;
    }
    // 检查本地存储中的主题偏好
   function initTheme() {
        try {
            const savedTheme = localStorage.getItem('theme');
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const theme = savedTheme || (systemDark ? 'dark' : 'light');
            setTheme(theme);
        } catch (e) {
            console.error("本地存储访问失败:", e);
            setTheme('light');
        }
    }

    function setTheme(theme) {
        console.log('正在应用主题:', theme);
        body.setAttribute('data-theme', theme);
        themeIcon.textContent = theme === 'dark' ? '🌙' : '🌞';
        themeText.textContent = theme === 'dark' ? '暗色' : '亮色';

       try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.error("本地存储写入失败:", e);
        }
    }


     // 主题切换按钮事件
    themeToggle.addEventListener('click', () => {
        const currentTheme = body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });



// 开始按钮事件
    const startBtn = document.getElementById('start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            // 验证路径有效性
            const targetUrl = new URL('dashboard', window.location.href);

            fetch(targetUrl)
                .then(response => {
                    if (response.ok) {
                        window.location.href = targetUrl.href;
                    } else {
                        alert("错误：目标页面不存在 (404)");
                    }
                })
                .catch(error => {
                    console.error("跳转错误:", error);
                    alert("无法访问目标页面");
                });
        });

    }

    // 初始化主题
    initTheme();
});
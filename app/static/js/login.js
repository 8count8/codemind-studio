


document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!username || !password) {
                alert('用户名和密码不能为空！');
                return;
            }

            // 获取 CSRF token
            const csrfTokenInput = loginForm.querySelector('[name="csrf_token"]');
            if (!csrfTokenInput) {
                console.error('CSRF token input not found');
                alert('内部错误: 未找到 CSRF token 输入字段');
                return;
            }
            const csrfToken = csrfTokenInput.value;

            // 显示加载状态
            const submitButton = loginForm.querySelector('input[type="submit"]');
            submitButton.disabled = true;
            submitButton.value = '正在登录...';

            // 提交表单数据（使用AJAX请求）
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        username: username,
                        password: password,
                        csrf_token: csrfToken
                    })
                });

                console.log('服务器响应:', response);

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    console.log('服务器返回的JSON数据:', data);
                    if (data.status === 200) {
                        window.location.href = data.redirect;
                    } else {
                        submitButton.disabled = false;
                        submitButton.value = '登录';
                        alert(data.message);
                    }
                } else if (contentType && contentType.includes('text/html')) {
                    const htmlText = await response.text();
                    console.error('服务器返回的HTML内容:', htmlText);
                    submitButton.disabled = false;
                    submitButton.value = '登录';
                    alert('登录过程中发生错误，请稍后再试');
                } else {
                    throw new Error('Unexpected content type: ' + contentType);
                }
            } catch (error) {
                submitButton.disabled = false;
                submitButton.value = '登录';
                console.error('在请求过程中出现了问题:', error);

                if (error instanceof Response) {
                    try {
                        const errorMessage = await error.text();
                        console.error('服务器错误消息:', errorMessage);
                        alert(errorMessage);
                    } catch (e) {
                        console.error('无法读取服务器错误消息:', e);
                        alert('网络请求出错，请稍后再试');
                    }
                } else {
                    console.error('其他错误:', error);
                    alert('网络请求出错，请稍后再试');
                }
            }
        });
    }
});

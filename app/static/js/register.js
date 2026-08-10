
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('register-form');  // 获取注册表单元素

    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();  // 阻止表单默认的提交行为

            const newUsername = document.getElementById('new-username').value.trim();  // 获取新用户名输入并去除前后空格
            const newPassword = document.getElementById('new-password').value.trim();  // 获取新密码输入并去除前后空格
            const confirmPassword = document.getElementById('confirm-password').value.trim();  // 获取确认密码输入并去除前后空格
            const userEmail = document.getElementById('new-email').value.trim();  // 获取邮箱输入并去除前后空格
            const verificationCode = document.getElementById('verification-code').value.trim();  // 获取验证码输入并去除前后空格

            if (!newUsername || !newPassword || !confirmPassword || !userEmail || !verificationCode) {
                alert('所有字段都是必填项！');  // 弹出提示框提醒用户填写所有字段
                return;  // 返回，停止后续执行
            }

            if (newPassword !== confirmPassword) {
                alert('密码和确认密码不匹配！');  // 弹出提示框提醒用户密码不匹配
                return;  // 返回，停止后续执行
            }
            //修改了
			 // 验证邮箱格式
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(userEmail)) {
                alert('请输入有效的邮箱地址！');  // 弹出提示框提醒用户输入有效的邮箱地址
                return;  // 返回，停止后续执行
            }

            // 显示加载状态
            const submitButton = registerForm.querySelector('input[type="submit"]');  // 获取提交按钮元素
            submitButton.disabled = true; // 禁用提交按钮防止重复提交
            submitButton.value = '正在注册...';  // 更改提交按钮的文本为“正在注册...”

            // 获取 CSRF token
            const csrfTokenInput = registerForm.querySelector('[name="csrf_token"]');
            if (!csrfTokenInput) {
                console.error('CSRF token input not found');
                alert('内部错误: 未找到 CSRF token 输入字段');
                return;
            }
            const csrfToken = csrfTokenInput.value;

            // 提交表单数据（使用AJAX请求）
            console.log('提交注册信息...');
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'new-username': newUsername,
                        'new-password': newPassword,
                        'new-email': userEmail,
                        'verification-code': verificationCode,
                        'csrf_token': csrfToken
                    })
                });

                console.log('服务器响应:', response);

                if (response.ok) {
                    const data = await response.json();
                    console.log('服务器返回的JSON数据:', data);
                    if (data.status === 200) {
                        window.location.href = data.redirect;
                    } else {
                        submitButton.disabled = false;
                        submitButton.value = '注册';
                        alert(data.message);
                    }
                } else {
                    throw response;
                }
            } catch (error) {
                console.error('在请求过程中出现了问题:', error);

                // 如果网络请求出现问题，恢复按钮状态并提示用户
                submitButton.disabled = false;
                submitButton.value = '注册';

                // 尝试读取错误消息
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

        // 获取验证码按钮点击事件
        const getVerificationCodeBtn = document.getElementById('get-verification-code-btn');
        getVerificationCodeBtn.addEventListener('click', async function () {
            const userEmail = document.getElementById('new-email').value.trim();
            if (!userEmail) {
                alert('请输入邮箱地址！');
                return;
            }

            // 显示加载状态
            getVerificationCodeBtn.disabled = true;
            getVerificationCodeBtn.value = '正在发送...';

            // 获取 CSRF token
            const csrfTokenInput = registerForm.querySelector('[name="csrf_token"]');
            if (!csrfTokenInput) {
                console.error('CSRF token input not found');
                alert('内部错误: 未找到 CSRF token 输入字段');
                return;
            }
            const csrfToken = csrfTokenInput.value;

            // 发送获取验证码请求（使用AJAX请求）
            console.log('请求获取验证码...');
            try {
                const response = await fetch('/get_verification_code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'email': userEmail,
                        'csrf_token': csrfToken
                    })
                });

                console.log('服务器响应:', response);

                if (response.ok) {
                    const data = await response.json();
                    console.log('服务器返回的JSON数据:', data);
                    if (data.status === 200) {
                        alert('验证码已发送，请查收邮箱。');
                    } else {
                        alert(data.message);
                    }
                } else {
                    throw response;
                }
            } catch (error) {
                console.error('在请求过程中出现了问题:', error);

                // 如果网络请求出现问题，恢复按钮状态并提示用户
                getVerificationCodeBtn.disabled = false;
                getVerificationCodeBtn.value = '获取验证码';

                // 尝试读取错误消息
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
            } finally {
                getVerificationCodeBtn.disabled = false;
                getVerificationCodeBtn.value = '获取验证码';
            }
        });
    }
});

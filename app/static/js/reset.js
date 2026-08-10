document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reset-password-form');
    const getVerificationCodeBtn = document.getElementById('get-verification-code-btn');

    getVerificationCodeBtn.addEventListener('click', async () => {
        const emailInput = document.getElementById('email');
        const email = emailInput.value.trim();

        if (!validateEmail(email)) {
            alert('请输入有效的邮箱地址');
            return;
        }

        try {
            const response = await fetch('/get_forgot_password_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRF-Token': document.querySelector('input[name="csrf_token"]').value
                },
                body: `email=${encodeURIComponent(email)}`
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);
            } else {
                const errorData = await response.json();
                alert(errorData.message || '获取验证码失败，请稍后再试');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('发生错误，请稍后再试');
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // 阻止表单默认提交行为

        const emailInput = document.getElementById('email');
        const newPasswordInput = document.getElementById('new-password');
        const verificationCodeInput = document.getElementById('verification-code');

        const email = emailInput.value.trim();
        const newPassword = newPasswordInput.value.trim();
        const verificationCode = verificationCodeInput.value.trim();

        if (!validateEmail(email)) {
            alert('请输入有效的邮箱地址');
            return;
        }

        if (newPassword === '') {
            alert('请输入新密码');
            return;
        }

        if (verificationCode === '') {
            alert('请输入验证码');
            return;
        }

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRF-Token': document.querySelector('input[name="csrf_token"]').value
                },
                body: `email=${encodeURIComponent(email)}&new_password=${encodeURIComponent(newPassword)}&verification_code=${encodeURIComponent(verificationCode)}`
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message || '密码重置成功，请使用新密码登录');
                window.location.href = '/login';
            } else {
                const errorData = await response.json();
                alert(errorData.message || '重置失败，请稍后再试');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('发生错误，请稍后再试');
        }
    });
});

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}



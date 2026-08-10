document.addEventListener('DOMContentLoaded', function() {
    // 添加元素存在性检查
    const exitProfileBtn = document.getElementById('exitProfileBtn');
    if (exitProfileBtn) {
        exitProfileBtn.addEventListener('click', function() {
            window.location.href = '/dashboard';
        });
    }
    const historyBtn = document.getElementById('history-btn');
    const favoritesBtn = document.getElementById('favorites-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userAvatar = document.querySelector('.user-avatar');
    const userNickname = document.querySelector('.profile-info h2');
    const userEmail = document.querySelector('.profile-info p');
    const avatarInput = document.getElementById('avatar-input');

    // 从 localStorage 中获取用户设置的头像、昵称和邮箱
    const savedAvatar = localStorage.getItem('userAvatar');
    const savedNickname = localStorage.getItem('userNickname');
    const savedEmail = localStorage.getItem('userEmail');

    // 如果有保存的头像、昵称和邮箱，则显示
    if (savedAvatar) {
        userAvatar.src = savedAvatar;
    }
    if (savedNickname) {
        userNickname.textContent = savedNickname;
    }
    if (savedEmail) {
        userEmail.textContent = `邮箱: ${savedEmail}`;
    }

    historyBtn.addEventListener('click', function () {
        // 弹出历史记录页面的逻辑
        window.location.href = '/history'; // 替换为实际的历史记录页面路径
    });

    // 能力矩阵按钮点击事件
    const abilityMatrixBtn = document.getElementById('ability-matrix-btn');
    if (abilityMatrixBtn) {
        abilityMatrixBtn.addEventListener('click', function () {
            window.location.href = '/ability-matrix';
        });
    }

    favoritesBtn.addEventListener('click', function () {
        // 弹出收藏记录页面的逻辑
        window.location.href = '/favorites'; // 替换为实际的收藏记录页面路径
    });

    logoutBtn.addEventListener('click', function () {
        // 退出登录的逻辑
        window.location.href = '/logout';
    });

    // 点击头像修改头像
    userAvatar.addEventListener('click', function () {
        avatarInput.click();
    });

	 // 退出页面按钮点击事件
    exitProfileBtn.addEventListener('click', function () {
        // 导航到dashboard页面
        window.location.href = "/dashboard";
    });

    // 处理文件选择事件
    avatarInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const currentAvatar = userAvatar.src;
                userAvatar.src = e.target.result;
                const isConfirmed = confirm('是否保存新的头像？');
                if (isConfirmed) {
                    localStorage.setItem('userAvatar', e.target.result);
                } else {
                    userAvatar.src = currentAvatar;
                }
            };
            reader.readAsDataURL(file);
        }
    });

    // 点击昵称修改昵称
    userNickname.addEventListener('click', function () {
        const currentNickname = userNickname.textContent;
        const newNickname = prompt('请输入新的昵称');
        if (newNickname) {
            const isConfirmed = confirm('是否保存新的昵称？');
            if (isConfirmed) {
                userNickname.textContent = newNickname;
                localStorage.setItem('userNickname', newNickname);
            } else {
                userNickname.textContent = currentNickname;
            }
        }
    });

    // 点击邮箱修改邮箱
    userEmail.addEventListener('click', function () {
        const currentEmail = userEmail.textContent.replace('邮箱: ', '');
        const newEmail = prompt('请输入新的邮箱地址', currentEmail);
        if (newEmail) {
            const isConfirmed = confirm('是否保存新的邮箱地址？');
            if (isConfirmed) {
                userEmail.textContent = `邮箱: ${newEmail}`;
                localStorage.setItem('userEmail', newEmail);
            } else {
                userEmail.textContent = `邮箱: ${currentEmail}`;
            }
        }
    });
});
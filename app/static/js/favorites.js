document.addEventListener('DOMContentLoaded', async function () {
    const favoritesList = document.getElementById('favorites-list');

    try {
        const response = await fetch('/api/user/favorites');
        if (!response.ok) throw new Error(`网络请求失败，状态码: ${response.status}`);
        
        const data = await response.json();
        
        // 修改数据验证逻辑
        if (!data || typeof data !== 'object') {
            throw new Error('无效的响应格式');
        }
        
        // 确保data.data是数组
        if (!Array.isArray(data.data)) {
            throw new Error('收藏数据格式不正确，应为数组');
        }

        renderFavorites(data.data);

        function renderFavorites(favorites) {
            if (favorites.length === 0) {
                favoritesList.innerHTML = '<div class="empty">暂无收藏题目</div>';
            } else {
                favoritesList.innerHTML = favorites.map(fav => `
                    <div class="favorite-item" data-id="${fav.id || fav.title}">
                        <h4>${fav.title}</h4>
                        ${fav.difficulty ? `<p>难度: ${fav.difficulty}</p>` : ''}
                    </div>
                `).join('');

                document.querySelectorAll('.favorite-item').forEach(item => {
                    item.addEventListener('click', () => {
                        window.location.href = `/problems/${item.dataset.id}`;
                    });
                });
            }
        }
    } catch (error) {
        console.error('获取收藏失败:', error);
        favoritesList.innerHTML = `
            <div class="error">
                加载收藏失败: ${error.message}
                <button onclick="location.reload()">刷新重试</button>
            </div>`;
    }
});

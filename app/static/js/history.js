document.addEventListener('DOMContentLoaded', function () {
    const historyList = document.getElementById('history-list');

    // 从本地存储中获取历史记录列表
    const histories = JSON.parse(localStorage.getItem('histories')) || [];

    // 按照时间排序，最新的在前面
    histories.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    if (histories.length === 0) {
        historyList.innerHTML = '<div class="empty">暂无历史记录</div>';
    } else {
        historyList.innerHTML = histories.map(history => `
            <div class="history-item" data-id="${history.id}">
                <h4>${history.title}</h4>
                <p>时间: ${new Date(history.timestamp).toLocaleString()}</p>
            </div>
        `).join('');

        // 添加点击事件
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                window.location.href = `/problems/${item.dataset.id}`;
            });
        });
    }
});
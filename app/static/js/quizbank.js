// JavaScript Document

// 使用 fetch 获取题目数据
async function fetchQuestions() {
    try {
        const response = await fetch('/api/questions');
        if (!response.ok) {
            throw new Error('获取题目数据失败');
        }
        const result = await response.json();
        if (result.status !== 200) {
            throw new Error(result.message);
        }
        return result.data; // 直接返回data数组
    } catch (error) {
        console.error('获取题目数据时出错:', error);
        return []; // 返回空数组作为兜底
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    // 从后端 API 获取题目数据
    const questions = await fetchQuestions();

    // 筛选状态
    let filters = {
        difficulties: new Set(),
        tags: new Set(),
        searchQuery: ''
    };

    // DOM元素
    const difficultyFilter = document.getElementById('difficulty-filter');
    const tagFilter = document.getElementById('tag-filter');
    const searchInput = document.getElementById('search-input');
    const questionList = document.getElementById('question-list');

    // 初始化筛选器
    function initFilters() {
        // 生成难度选项
        const difficulties = ['简单', '中等', '困难'];
        renderFilterOptions(difficultyFilter, difficulties, 'difficulty');

        // 生成标签选项
        const tags = [...new Set(questions.flatMap(q => JSON.parse(q.tags)))];
        renderFilterOptions(tagFilter, tags, 'tag');
    }

    // 新增：渲染筛选选项的函数
    function renderFilterOptions(container, options, type) {
        container.innerHTML = options.map(option => `
            <div class="filter-option" data-type="${type}" data-value="${option}">
                ${option}
            </div>
        `).join('');
    }

    // 题目渲染
    function renderQuestions() {
        console.log('当前难度筛选条件:', [...filters.difficulties]);
        console.log('所有题目难度:', questions.map(q => q.difficulty));
        
        const filtered = questions.filter(q => {
            // 确保难度筛选正确匹配
            const matchesDifficulty = filters.difficulties.size === 0 ||
                filters.difficulties.has(q.difficulty);

            // 将tags字符串转换为数组
            const tagsArray = JSON.parse(q.tags);
            const matchesTags = filters.tags.size === 0 ||
                tagsArray.some(tag => filters.tags.has(tag));

            const matchesSearch = q.title.includes(filters.searchQuery) ||
                tagsArray.some(tag => tag.includes(filters.searchQuery));

            return matchesDifficulty && matchesTags && matchesSearch;
        });

        questionList.innerHTML = filtered.map(q => {
            // 将tags字符串转换为数组
            const tagsArray = JSON.parse(q.tags);
            return `
            <div class="question-card" data-id="${q.id}">
                <div class="question-header">
                    <div class="question-title">${q.title}</div>
                    <button class="favorite-btn" data-id="${q.id}">
                        ${q.favorite ? '★' : '☆'}
                    </button>
                </div>
                <div class="question-meta">
                    <span>难度：${q.difficulty}</span>
                    <span>创建时间：${new Date(q.created_at).toLocaleDateString()}</span>
                </div>
                <div class="question-tags">
                    ${tagsArray.map(tag => `
                        <span class="tag">${tag}</span>
                    `).join('')}
                </div>
            </div>
            `;
        }).join('');
    }

    // 事件监听
    function setupEventListeners() {
        // 筛选选项点击（统一处理难度和标签）
        document.querySelectorAll('.filter-option').forEach(option => {
            option.addEventListener('click', function() {
                const type = this.dataset.type;
                const value = this.dataset.value;
                
                // 确保访问正确的filter set
                const filterSet = type === 'difficulty' ? filters.difficulties : 
                                type === 'tag' ? filters.tags : null;
                
                if (filterSet) {
                    // 切换active类
                    this.classList.toggle('active');
                    filterSet.has(value) ? filterSet.delete(value) : filterSet.add(value);
                    renderQuestions();
                }
            });
        });

        // 搜索功能
        searchInput.addEventListener('input', () => {
            filters.searchQuery = searchInput.value.trim();
            renderQuestions();
        });

        // 收藏功能
        questionList.addEventListener('click', e => {
            if (e.target.classList.contains('favorite-btn')) {
                e.stopPropagation();
                const questionId = parseInt(e.target.dataset.id);
                const question = questions.find(q => q.id === questionId);
                
                // 发送收藏/取消收藏请求
                fetch('/api/user/favorites', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        questionId: questionId,
                        action: question.favorite ? 'remove' : 'add'
                    })
                }).then(response => {
                    if (response.ok) {
                        question.favorite = !question.favorite;
                        e.target.textContent = question.favorite ? '★' : '☆';
                    }
                });
            }
        });

        // 点击题目卡片跳转到答题页面
        questionList.addEventListener('click', e => {
            const questionCard = e.target.closest('.question-card');
            if (questionCard && !e.target.classList.contains('favorite-btn')) {
                const questionId = questionCard.dataset.id;
                window.location.href = `/answerpad?questionId=${questionId}`;
            }
        });
    }

    // 初始化
    initFilters();
    renderQuestions();
    setupEventListeners();
});

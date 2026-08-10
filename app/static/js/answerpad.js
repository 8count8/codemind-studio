const editor = ace.edit("editor")
const languageSelect = document.getElementById('language-select');
const saveStatus = document.getElementById('save-status');
const favoriteBtn = document.getElementById('favorite-btn');
let autoSaveTimer;
let aiReviewPolling;

// 强化 marked 库检查
const marked = (() => {
    if (typeof window.marked === 'object' && typeof window.marked.parse === 'function') {
        return window.marked;
    }
    if (typeof window.marked === 'function') {
        return { parse: window.marked };
    }
    console.error('marked 库未加载！');
    return null;
})();

// 初始化代码编辑器
document.addEventListener('DOMContentLoaded', initEditor);

function getModeByLanguage(language) {
    const modeMap = {
        'python': 'ace/mode/python',
        'javascript': 'ace/mode/javascript',
        'java': 'ace/mode/java',
        'c++': 'ace/mode/c_cpp'
    };
    return modeMap[language] || 'ace/mode/python';
}

function initEditor() {
    // 增强错误处理
    if (!marked) {
        console.error('marked 库加载失败，请检查HTML引入: <script src="/static/js/Marked/marked.umd.js"></script>');
        document.querySelectorAll('.markdown-body').forEach(el => {
            el.style.color = 'red';
            el.textContent = 'Markdown渲染库加载失败，请刷新页面或联系管理员';
        });
        return;
    }

    // 配置 marked 选项（兼容新旧版本）
    if (typeof marked.use === 'function') {
        marked.use({
            breaks: true,
            gfm: true,
            tables: true,
            sanitize: false // 允许原始HTML
        });
    } else if (marked.defaults) {
        marked.setOptions({
            breaks: true,
            gfm: true,
            tables: true
        });
    }

    // 处理Markdown内容
    document.querySelectorAll('.markdown-body').forEach(element => {
        let content = element.innerHTML
           .replace(/&lt;/g, '<')
           .replace(/&gt;/g, '>')
           .replace(/&quot;/g, '"')
           .replace(/&amp;/g, '&')
           .split('\n')
           .map(line => line.trimStart())
           .join('\n');

        try {
            element.innerHTML = marked.parse(content);
        } catch (e) {
            console.error('Markdown解析错误:', e);
            element.innerHTML = `<pre>${content}</pre>`;
        }
    });

    // 初始化编辑器配置
    editor.setTheme("ace/theme/monokai");
    const savedData = JSON.parse(localStorage.getItem('currentQuestion')) || {};
    const initialLanguage = savedData.language || 'python';

    editor.session.setMode(getModeByLanguage(initialLanguage));
    editor.setOptions({
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        fontSize: "14px",
        fontFamily: "'JetBrains Mono', 'Consolas', 'Courier New', monospace",
        showLineNumbers: true,
        showGutter: true,
        highlightActiveLine: true,
        showPrintMargin: false,
        cursorStyle: "smooth",
        scrollPastEnd: 0.5,
        highlightSelectedWord: true,
        animatedScroll: true
    });

    editor.setValue(savedData.code || "// 开始编写你的代码.....", -1);
    languageSelect.value = initialLanguage;

    // 首先从URL参数获取questionId
    const urlParams = new URLSearchParams(window.location.search);
    const questionIdFromUrl = urlParams.get('questionId');

    // 如果URL中存在questionId，可以使用它加载题目数据
    if (questionIdFromUrl) {
        console.log(`从URL参数获取到题目ID: ${questionIdFromUrl}`);
        // 这里可以添加代码，通过API请求加载对应ID的题目
        // 例如: loadQuestionById(questionIdFromUrl);
    }

    // 继续加载题目数据
    const questionDataElement = document.getElementById('question-data');
    if (!questionDataElement) {
        console.error('question-data元素未找到');
        return;
    }

    let questionData;
    try {
        questionData = JSON.parse(questionDataElement.textContent);
        const questionTitleElement = document.getElementById('question-title');
        const questionDetailsElement = document.getElementById('question-details');
        if (questionTitleElement) {
            questionTitleElement.textContent = questionData.title;
        }
        if (questionDetailsElement) {
            questionDetailsElement.innerHTML = `
                <div class="question-meta">
                    <span>难度：${questionData.difficulty}</span>
                    <span>标签：${questionData.tags}</span>
                    <span>创建时间：${new Date(questionData.created_at).toLocaleDateString()}</span>
                </div>
                <div class="question-content markdown-body">
                    ${marked.parse(questionData.content)}
                </div>
            `;
        }
    } catch (e) {
        console.error('题目数据解析失败:', e);
        const questionDetailsElement = document.getElementById('question-details');
        if (questionDetailsElement) {
            questionDetailsElement.innerHTML = '题目加载失败，请检查数据格式';
        }
    }
}

// 语言切换事件监听
languageSelect.addEventListener('change', function() {
    const language = this.value;
    const mode = getModeByLanguage(language);
    editor.session.setMode(mode);

    // 更新本地存储
    const savedData = JSON.parse(localStorage.getItem('currentQuestion')) || {};
    savedData.language = language;
    localStorage.setItem('currentQuestion', JSON.stringify(savedData));
});

// 自动保存逻辑
function setupAutoSave() {
    autoSaveTimer = setInterval(() => {
        const code = editor.getValue();
        const language = languageSelect.value;
        localStorage.setItem('currentQuestion', JSON.stringify({ code, language }));
        saveStatus.textContent = `已保存 ${new Date().toLocaleTimeString()}`;
    }, 30000);
}

// 代码高亮逻辑
function setupSyntaxHighlighting() {
    // 简化的语法高亮实现
    const keywords = {
        python: ['def', 'class', 'if', 'else', 'for', 'while'],
        javascript: ['function', 'const', 'let', 'if', 'else'],
        java: ['public', 'class', 'void', 'static']
    };

    const code = editor.getValue();
    const lang = languageSelect.value;
    const highlightedCode = code.replace(/(\b\w+\b)/g, word => {
        if (keywords[lang].includes(word)) {
            return `<span class="keyword">${word}</span>`;
        }
        return word;
    });
    // 假设有办法更新编辑器的内容显示高亮
    // 实际可能需要使用 ACE 编辑器的 API 来实现
    console.log(highlightedCode);
}

// 获取 CSRF token
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta? meta.getAttribute('content') : null;
}

// 提交评估
document.getElementById('submit-btn').addEventListener('click', async () => {
    const code = editor.getValue();
    const language = languageSelect.value;
    const csrftoken = getCSRFToken();

    // 从URL获取题目ID
    let questionId = null;
    // 首先从URL中获取questionId参数
    const urlParams = new URLSearchParams(window.location.search);
    questionId = urlParams.get('questionId');

    // 如果URL中没有，尝试从questionData元素获取
    if (!questionId) {
        const questionDataElement = document.getElementById('question-data');
        if (questionDataElement) {
            try {
                const questionData = JSON.parse(questionDataElement.textContent);
                questionId = questionData.id;
            } catch (e) {
                console.error('获取题目ID失败:', e);
            }
        }
    }

    console.log(`提交代码 - 题目ID: ${questionId}, 语言: ${language}`);

    try {
        const response = await fetch('/api/process_algorithm_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                code,
                language,
                question_id: questionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        showEvaluationResult(result);
        startAIReviewPolling(result.task_id);
    } catch (error) {
        console.error('提交代码时出错:', error);
    }
});

// 显示评估结果
function showEvaluationResult(result) {
    const runResultContainer = document.getElementById('run-result');
    const aiReviewResult = document.getElementById('ai-review-result');

    // 显示运行结果
    if (runResultContainer) {
        const testCases = result.run_result.results;
        const totalCases = result.run_result.total_cases;
        const passedCases = result.run_result.passed_cases;
        const failedCases = result.run_result.failed_cases;
        const totalExecutionTime = testCases.reduce((acc, testCase) => acc + testCase.run_time, 0);

        const overallStatus = result.run_result.success? '成功' : '失败';

        // 详细信息状态样式类
        let overallStatusClass = 'status-processing';
        if (overallStatus === '成功') overallStatusClass = 'status-success';
        if (overallStatus === '失败') overallStatusClass = 'status-failed';
        if (overallStatus === '错误') overallStatusClass = 'status-error';

        let overallHtml = `<div class="result-container overall-result" onclick="toggleTestCases(this)">
            <div class="result-header">
                <div class="result-status ${overallStatusClass}">
                    <span>${overallStatus}<i class="status-icon"></i></span>
                </div>
                <div class="result-metrics">
                    <span class="metric-item metric-style">总测试用例数: ${totalCases}</span>
                    <span class="metric-item metric-style">通过测试用例数: ${passedCases}</span>
                    <span class="metric-item metric-style">失败测试用例数: ${failedCases}</span>
                    <span class="metric-item metric-style">总执行时间: ${totalExecutionTime.toFixed(6)}</span>
                </div>
            </div>
            <div class="result-output">
                <h4 class="detail-info-style">
                    详细信息<i class="fa-solid fa-chevron-down expand-icon"></i>
                </h4>
            </div>
            <div class="test-cases-wrapper" style="display: none;">`;

        let resultsHtml = '';

        testCases.forEach((testCase, index) => {
            const status = testCase.success? '成功' : '失败';
            // 处理输出中的换行符
            let output = testCase.actual_output || testCase.error || '暂无输出';
            output = output.replace(/\n/g, '<br>').trim();
            const executionTime = testCase.run_time.toFixed(6) || '未知';

            // 单个测试用例状态样式类
            let statusClass = 'status-processing';
            if (status === '成功') statusClass = 'status-success';
            if (status === '失败') statusClass = 'status-failed';
            if (status === '错误') statusClass = 'status-error';

            resultsHtml += `<div class="result-container">
                <div class="result-header">
                    <div class="result-status ${statusClass}">
                        <i class="status-icon"></i>
                        <span>${status}</span>
                    </div>
                    <div class="result-metrics">
                        <span class="metric-item">执行时间: ${executionTime}</span>
                    </div>
                </div>
                <div class="result-output">
                    <h4>输出:</h4>
                    <div class="output-content">${output}</div>
                </div>
            </div>`;
        });

        overallHtml += resultsHtml + `</div></div>`;

        runResultContainer.innerHTML = overallHtml;
    } else {
        runResultContainer.innerHTML = `<div class="result-container">
            <div class="result-header">
                <div class="result-status status-error">
                    <i class="status-icon"></i>
                    <span>无运行结果</span>
                </div>
            </div>
            <div class="result-output">
                <p>无法获取运行结果数据</p>
            </div>
        </div>`;
    }

    // 初始化AI批改结果
    aiReviewResult.innerHTML = `<div class="ai-processing">
        <span>AI批改处理中</span>
        <div class="ai-loading-dots"></div>
    </div>`;
}

// 点击详细信息区域时切换测试用例的显示状态
function toggleTestCases(element) {
    const testCasesWrapper = element.querySelector('.test-cases-wrapper');
    const expandIcon = element.querySelector('.expand-icon');
    if (testCasesWrapper.style.display === 'none') {
        testCasesWrapper.style.display = 'block';
        expandIcon.classList.remove('fa-chevron-down');
        expandIcon.classList.add('fa-chevron-up');
    } else {
        testCasesWrapper.style.display = 'none';
        expandIcon.classList.remove('fa-chevron-up');
        expandIcon.classList.add('fa-chevron-down');
    }
}

// 启动AI批改轮询
function startAIReviewPolling(taskId) {
    // 清除可能存在的之前的轮询
    if (aiReviewPolling) {
        clearInterval(aiReviewPolling);
    }

    // 设置轮询计数和最大尝试次数
    let pollingCount = 0;
    const maxPollingAttempts = 30; // 最多尝试30次，约1分钟

    // 初始化显示处理中状态
    const aiReviewResult = document.getElementById('ai-review-result');
    aiReviewResult.innerHTML = `<div class="ai-processing"><span>AI批改处理中</span><div class="ai-loading-dots"></div></div>`;

    aiReviewPolling = setInterval(async () => {
        try {
            pollingCount++;
            console.log(`AI批改轮询中... (${pollingCount}/${maxPollingAttempts})`);

            const response = await fetch(`/api/ai_review_status/${taskId}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log("获取到AI批改结果:", result);

            // 检查请求是否返回了数据
            if (!result) {
                throw new Error("未获取到任何结果数据");
            }

            // 处理完成状态
            if (result.status === 'complete') {
                clearInterval(aiReviewPolling);
                console.log("AI批改完成，显示结果");

                // 显示分数
                const score = result.score || 0;

                // 处理反馈中可能的换行
                let feedback = result.feedback || "无评价反馈";
                feedback = feedback.replace(/\n/g, ' ').trim();

                // 处理改进建议列表，移除换行和过滤空字符串
                let improvements = result.improvements || [];
                improvements = improvements
                    .map(item => item.replace(/\n/g, ' ').trim())
                    .filter(item => item.length > 0);

                // 如果没有改进建议，显示默认消息
                let improvementsHtml = '<div class="ai-feedback-content">无具体改进建议</div>';

                // 如果有改进建议，格式化它们
                if (improvements.length > 0) {
                    improvementsHtml = improvements
                        .map(imp => `<div class="ai-improvement-item">${imp}</div>`)
                        .join('');
                }

                // 渲染基本AI批改结果
                aiReviewResult.innerHTML = `
                    <div class="ai-review-container">
                        <div class="ai-review-header">
                            <h3 class="ai-review-title">AI代码评估</h3>
                            <div class="ai-score"><span class="ai-score-value">${score}</span><span>分</span></div>
                        </div>
                        <div class="ai-feedback-section">
                            <h4 class="ai-feedback-title">评价反馈</h4>
                            <div class="ai-feedback-content">${feedback}</div>
                        </div>
                        <div class="ai-feedback-section">
                            <h4 class="ai-feedback-title">改进建议</h4>
                            ${improvementsHtml}
                        </div>
                    </div>`;

                // 添加代码对比部分
                if (result.original_code && result.reviewed_code) {
                    renderCodeComparison(
                        result.original_code,
                        result.reviewed_code,
                        result.language || 'python',
                        aiReviewResult
                    );
                }
            }
            // 处理错误状态
            else if (result.status === 'error') {
                clearInterval(aiReviewPolling);
                console.error("AI批改失败:", result.message);

                let errorMessage = result.message || '未知错误';

                // 提取更友好的错误信息
                if (errorMessage.includes('JSON解析失败') || errorMessage.includes('JSON格式错误')) {
                    errorMessage = "AI批改处理失败：响应格式错误，请稍后重试";
                } else if (errorMessage.includes('代码审查异常')) {
                    errorMessage = "AI批改过程中出现问题，请稍后重试";
                }

                errorMessage = errorMessage.replace(/\n/g, ' ').trim();
                aiReviewResult.innerHTML = `<div class="ai-review-container"><div class="ai-error"><h4>AI批改失败</h4><p>错误信息: ${errorMessage}</p><p><button id="retry-review" class="btn-retry">重试批改</button></p></div></div>`;

                // 添加重试按钮事件处理
                document.getElementById('retry-review')?.addEventListener('click', () => {
                    const submitBtn = document.getElementById('submit-btn');
                    if (submitBtn) {
                        submitBtn.click(); // 触发重新提交
                    }
                });
            }
            // 处理处理中状态
            else if (result.status === 'processing') {
                aiReviewResult.innerHTML = `<div class="ai-processing"><span>AI批改处理中 (${pollingCount}/${maxPollingAttempts})</span><div class="ai-loading-dots"></div></div>`;

                // 如果超过最大尝试次数，停止轮询
                if (pollingCount >= maxPollingAttempts) {
                    clearInterval(aiReviewPolling);
                    aiReviewResult.innerHTML = `<div class="ai-review-container"><div class="ai-warning"><h4>AI批改超时</h4><p>请稍后刷新页面查看结果</p><p><button id="retry-review" class="btn-retry">重试批改</button></p></div></div>`;

                    // 添加重试按钮事件处理
                    document.getElementById('retry-review')?.addEventListener('click', () => {
                        const submitBtn = document.getElementById('submit-btn');
                        if (submitBtn) {
                            submitBtn.click(); // 触发重新提交
                        }
                    });
                }
            }
            // 处理其他未知状态
            else {
                console.warn("未知的AI批改状态:", result.status);
                aiReviewResult.innerHTML = `<div class="ai-processing"><span>AI批改状态: ${result.status}</span><div class="ai-loading-dots"></div></div>`;
            }
        } catch (error) {
            console.error('获取AI批改结果失败:', error);

            // 显示错误消息但不停止轮询，除非达到最大尝试次数
            if (pollingCount >= maxPollingAttempts) {
                clearInterval(aiReviewPolling);
                const errorMsg = error.message.replace(/\n/g, ' ').trim();
                aiReviewResult.innerHTML = `<div class="ai-review-container"><div class="ai-error"><h4>获取结果时出错</h4><p>${errorMsg}</p><p>已达到最大尝试次数</p><p><button id="retry-review" class="btn-retry">重试批改</button></p></div></div>`;

                // 添加重试按钮事件处理
                document.getElementById('retry-review')?.addEventListener('click', () => {
                    const submitBtn = document.getElementById('submit-btn');
                    if (submitBtn) {
                        submitBtn.click(); // 触发重新提交
                    }
                });
            } else {
                aiReviewResult.innerHTML = `<div class="ai-processing"><span>重试获取结果 (${pollingCount}/${maxPollingAttempts})</span><div class="ai-loading-dots"></div></div>`;
            }
        }
    }, 2000);
}

// 渲染代码对比和高亮
function renderCodeComparison(originalCode, reviewedCode, language, container) {
    // 创建代码对比容器
    const codeComparisonHtml = `
        <div class="code-comparison-container">
            <div class="code-comparison-header">
                <div class="code-tab active" id="tab-original">原始代码</div>
                <div class="code-tab" id="tab-reviewed">带批注代码</div>
            </div>
            <div class="code-editors-container">
                <div class="code-editor-wrapper" id="original-code-editor">
                    <div class="code-editor-label">您提交的代码</div>
                    <pre><code class="${language}">${escapeHtml(originalCode)}</code></pre>
                </div>
                <div class="code-editor-wrapper" id="reviewed-code-editor" style="display: none;">
                    <div class="code-editor-label">带批注的代码</div>
                    <pre><code class="${language}">${escapeHtml(reviewedCode)}</code></pre>
                </div>
            </div>
        </div>
    `;

    // 添加到容器
    container.insertAdjacentHTML('beforeend', codeComparisonHtml);

    // 添加标签切换事件
    const tabOriginal = document.getElementById('tab-original');
    const tabReviewed = document.getElementById('tab-reviewed');
    if (tabOriginal) {
        tabOriginal.addEventListener('click', function () {
            this.classList.add('active');
            if (tabReviewed) {
                tabReviewed.classList.remove('active');
            }
            const originalEditor = document.getElementById('original-code-editor');
            const reviewedEditor = document.getElementById('reviewed-code-editor');
            if (originalEditor) {
                originalEditor.style.display = 'block';
            }
            if (reviewedEditor) {
                reviewedEditor.style.display = 'none';
            }
        });
    }
    if (tabReviewed) {
        tabReviewed.addEventListener('click', function () {
            this.classList.add('active');
            if (tabOriginal) {
                tabOriginal.classList.remove('active');
            }
            const originalEditor = document.getElementById('original-code-editor');
            const reviewedEditor = document.getElementById('reviewed-code-editor');
            if (originalEditor) {
                originalEditor.style.display = 'none';
            }
            if (reviewedEditor) {
                reviewedEditor.style.display = 'block';
            }
        });
    }
}

// 转义 HTML 字符，防止 XSS 攻击
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// 高亮注释行和添加警告标记
function highlightWarnings(editor) {
    const session = editor.getSession();
    const doc = session.getDocument();
    const lines = doc.getAllLines();

    // 查找包含注释和警告的行
    lines.forEach((line, index) => {
        // 检查行是否包含警告或错误关键词
        if (line.includes('// 错误') ||
            line.includes('# 错误') ||
            line.includes('// 警告') ||
            line.includes('# 警告') ||
            line.includes('// 问题') ||
            line.includes('# 问题') ||
            line.includes('// ⚠️') ||
            line.includes('# ⚠️') ||
            line.match(/\/\/\s+.*(错误|警告|问题)/) ||
            line.match(/#\s+.*(错误|警告|问题)/)
        ) {
            // 添加行高亮样式
            session.addGutterDecoration(index, "warning");

            // 创建警告提示框
            const content = line.replace(/^(\/\/|#)\s+/, '').trim();

            // 为这一行添加鼠标悬停事件
            editor.on("mousemove", function(e) {
                const position = e.getDocumentPosition();
                if (position.row === index) {
                    showTooltip(content, e.clientX, e.clientY);
                } else {
                    hideTooltip();
                }
            });
        }
    });
}

// 显示提示框
function showTooltip(content, x, y) {
    let tooltip = document.getElementById('code-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'code-tooltip';
        tooltip.className = 'tooltip-warning';
        document.body.appendChild(tooltip);
    }

    tooltip.innerHTML = content;
    tooltip.style.left = `${x + 10}px`;
    tooltip.style.top = `${y - 40}px`;
    tooltip.style.opacity = 1;
}

// 隐藏提示框
function hideTooltip() {
    const tooltip = document.getElementById('code-tooltip');
    if (tooltip) {
        tooltip.style.opacity = 0;
    }
}

// 错题诊断引擎
const weaknessData = {
    weaknesses: [
        { category: '算法', topic: '动态规划', frequency: 5 },
        { category: '数据结构', topic: '二叉树', frequency: 3 }
    ],
    recommendations: [
        { id: 101, title: '背包问题', difficulty: '中等' },
        { id: 205, title: '二叉树遍历', difficulty: '简单' },
        { id: 308, title: '图论基础', difficulty: '困难' }
    ]
};

function renderDiagnosis() {
    const weaknessListElement = document.getElementById('weakness-list');
    const recommendedQuestionsElement = document.getElementById('recommended-questions');

    if (weaknessListElement) {
        weaknessListElement.innerHTML = weaknessData.weaknesses
           .map(w => `
                <div class="weakness-item">
                    <h4>${w.category} - ${w.topic}</h4>
                    <progress value="${w.frequency}" max="10"></progress>
                </div>
            `).join('');
    }

    if (recommendedQuestionsElement) {
        recommendedQuestionsElement.innerHTML = weaknessData.recommendations
           .map(q => `
                <div class="question" data-id="${q.id}">
                    <span class="difficulty ${q.difficulty}">${q.difficulty}</span>
                    ${q.title}
                </div>
            `).join('');
    }
}

// PDF导出
document.getElementById('export-pdf').addEventListener('click', () => {
    // 此处应集成PDF生成库
    alert('PDF导出功能需集成jsPDF库');
});

// 收藏功能
function handleFavorite(id, title) {
    const favorites = JSON.parse(localStorage.getItem('favorites')) || [];
    if (!favorites.find(fav => fav.id === id)) {
        favorites.push({ id, title });
        localStorage.setItem('favorites', JSON.stringify(favorites));
        alert(`题目 "${title}" 已收藏！`);
    } else {
        alert(`题目 "${title}" 已经在收藏列表中。`);
    }
}

// 绑定收藏按钮事件
favoriteBtn.addEventListener('click', () => {
    const currentQuestion = JSON.parse(localStorage.getItem('currentQuestion')) || {};
    const title = "当前题目"; // 假设题目标题为"当前题目"
    handleFavorite("current", title); // 收藏当前题目
});

document.getElementById('recommended-questions').addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-favorite')) {
        const questionId = e.target.getAttribute('data-id');
        const questionTitle = e.target.parentElement.textContent.trim();
        handleFavorite(questionId, questionTitle);
    }
});

// 初始化
initEditor();
setupAutoSave();
renderDiagnosis();

// 事件监听
languageSelect.addEventListener('change', setupSyntaxHighlighting);
editor.on('input', () => {
    clearInterval(autoSaveTimer);
    setupAutoSave();
});
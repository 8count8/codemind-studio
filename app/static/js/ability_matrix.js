/**
 * 能力矩阵页面 JavaScript
 *
 * 功能：
 * 1. 加载和展示能力矩阵数据（雷达图 + 维度条）
 * 2. 代码提交评估
 * 3. 提交历史展示
 * 4. 薄弱维度分析与学习推荐
 * 5. 主题切换
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================
    // 全局变量
    // =========================================
    let radarChart = null;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    // 维度颜色配置
    const DIMENSION_COLORS = {
        syntax_score:    { bg: 'rgba(66, 133, 244, 0.25)',  border: '#4285f4' },
        algorithm_score: { bg: 'rgba(52, 168, 83, 0.25)',   border: '#34a853' },
        project_score:   { bg: 'rgba(251, 188, 4, 0.25)',   border: '#fbbc04' },
        debug_score:     { bg: 'rgba(234, 67, 53, 0.25)',   border: '#ea4335' },
        security_score:  { bg: 'rgba(142, 68, 173, 0.25)',  border: '#8e44ad' }
    };

    const DIMENSION_LABELS = {
        syntax_score:    '语法基础',
        algorithm_score: '算法思维',
        project_score:   '项目实践',
        debug_score:     '调试能力',
        security_score:  '安全意识'
    };

    const SOURCE_LABELS = {
        code_submit: '代码提交',
        ai_review:   'AI审查',
        quiz_answer: '答题记录'
    };

    // =========================================
    // 初始化
    // =========================================
    initTheme();
    initBackButton();
    loadAbilityMatrix();
    loadSubmissionHistory();
    loadRecommendations();
    bindSubmitEvent();

    // =========================================
    // 主题切换
    // =========================================
    function initTheme() {
        const toggle = document.getElementById('theme-toggle');
        const icon   = document.getElementById('theme-icon');
        const text   = document.getElementById('theme-text');

        const saved = localStorage.getItem('theme') || 'light';
        applyTheme(saved);

        toggle?.addEventListener('click', () => {
            const current = document.body.getAttribute('data-theme') || 'light';
            const next = current === 'light' ? 'dark' : 'light';
            applyTheme(next);
            localStorage.setItem('theme', next);
            // 重新渲染雷达图以适配主题
            if (radarChart) updateRadarChart(radarChart._scores || {});
        });

        function applyTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            if (icon) icon.textContent = theme === 'dark' ? '🌙' : '🌞';
            if (text) text.textContent = theme === 'dark' ? '暗色' : '亮色';
        }
    }

    // =========================================
    // 返回按钮
    // =========================================
    function initBackButton() {
        document.getElementById('back-btn')?.addEventListener('click', () => {
            window.location.href = '/dashboard';
        });
    }

    // =========================================
    // 加载能力矩阵数据
    // =========================================
    function loadAbilityMatrix() {
        fetch('/api/ability-matrix')
            .then(res => res.json())
            .then(data => {
                if (data.status === 200 && data.data) {
                    const matrix = data.data.matrix || {};
                    const dims   = matrix.dimensions || {};
                    renderStats(matrix);
                    updateRadarChart(dims);
                    renderDimensions(dims);
                    renderWeakDimensions(data.data.weak_dimensions || []);
                } else {
                    showToast(data.message || '加载数据失败', 'error');
                }
            })
            .catch(err => {
                console.error('加载能力矩阵失败:', err);
                showToast('网络错误，请稍后重试', 'error');
            });
    }

    // =========================================
    // 渲染顶部统计
    // =========================================
    function renderStats(matrix) {
        setText('stat-level', matrix.level || '初学者');
        setText('stat-submissions', matrix.total_submissions || 0);
        setText('stat-average', matrix.average_score || 0);
        setText('stat-updated', matrix.updated_at ? matrix.updated_at.substring(0, 10) : '-');
    }

    // =========================================
    // 雷达图
    // =========================================
    function updateRadarChart(dims) {
        const labels = [];
        const scores = [];

        for (const key of Object.keys(DIMENSION_LABELS)) {
            const d = dims[key];
            labels.push(DIMENSION_LABELS[key]);
            scores.push(d ? d.score : 0);
        }

        const isDark = document.body.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)';
        const tickColor = isDark ? '#bbb' : '#555';

        const chartData = {
            labels: labels,
            datasets: [{
                label: '能力得分',
                data: scores,
                backgroundColor: 'rgba(66, 133, 244, 0.2)',
                borderColor: '#4285f4',
                borderWidth: 2,
                pointBackgroundColor: '#4285f4',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#4285f4',
                pointRadius: 5
            }]
        };

        const config = {
            type: 'radar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        min: 0,
                        ticks: {
                            stepSize: 20,
                            color: tickColor,
                            backdropColor: 'transparent'
                        },
                        grid: { color: gridColor },
                        angleLines: { color: gridColor },
                        pointLabels: {
                            font: { size: 13, weight: '600' },
                            color: tickColor
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.label}: ${ctx.parsed.r} 分`
                        }
                    }
                }
            }
        };

        if (radarChart) {
            radarChart.data = chartData;
            radarChart.options.scales.r.ticks.color = tickColor;
            radarChart.options.scales.r.grid.color  = gridColor;
            radarChart.options.scales.r.angleLines.color = gridColor;
            radarChart.options.scales.r.pointLabels.color = tickColor;
            radarChart.update();
        } else {
            const canvas = document.getElementById('radarChart');
            if (canvas) {
                radarChart = new Chart(canvas.getContext('2d'), config);
            }
        }
        // 保存 scores 供主题切换时重新渲染
        if (radarChart) radarChart._scores = dims;
    }

    // =========================================
    // 维度得分条
    // =========================================
    function renderDimensions(dims) {
        const container = document.getElementById('dimensions-list');
        if (!container) return;

        container.innerHTML = '';
        for (const key of Object.keys(DIMENSION_LABELS)) {
            const d     = dims[key] || {};
            const score = d.score || 0;
            const cls   = score >= 70 ? 'score-high' : score >= 40 ? 'score-medium' : 'score-low';

            const row = document.createElement('div');
            row.className = 'dimension-item';

            const label = document.createElement('span');
            label.className = 'dimension-label';
            label.textContent = DIMENSION_LABELS[key];

            const barWrap = document.createElement('div');
            barWrap.className = 'dimension-bar-wrapper';
            const bar = document.createElement('div');
            bar.className = 'dimension-bar ' + cls;
            bar.style.width = score + '%';
            barWrap.appendChild(bar);

            const scoreEl = document.createElement('span');
            scoreEl.className = 'dimension-score ' + cls;
            scoreEl.textContent = score;

            row.append(label, barWrap, scoreEl);
            container.appendChild(row);
        }
    }

    // =========================================
    // 薄弱维度
    // =========================================
    function renderWeakDimensions(weakList) {
        const container = document.getElementById('weak-list');
        if (!container) return;

        container.innerHTML = '';

        if (!weakList || weakList.length === 0) {
            const p = document.createElement('p');
            p.className = 'empty-hint';
            p.textContent = '暂无薄弱维度，继续保持！';
            container.appendChild(p);
            return;
        }

        weakList.forEach(w => {
            const item = document.createElement('div');
            item.className = 'weak-item';

            const icon = document.createElement('span');
            icon.className = 'weak-icon';
            icon.textContent = '⚠️';

            const info = document.createElement('div');
            info.className = 'weak-info';

            const name = document.createElement('div');
            name.className = 'weak-name';
            name.textContent = w.label + ' ';
            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'weak-score';
            scoreSpan.textContent = (w.score || 0) + ' 分';
            name.appendChild(scoreSpan);

            const suggestion = document.createElement('div');
            suggestion.className = 'weak-suggestion';
            suggestion.textContent = w.suggestion || '';

            info.append(name, suggestion);
            item.append(icon, info);
            container.appendChild(item);
        });
    }

    // =========================================
    // 学习推荐
    // =========================================
    function loadRecommendations() {
        fetch('/api/ability-matrix/recommendations')
            .then(res => res.json())
            .then(data => {
                if (data.status === 200) {
                    renderRecommendations(data.data?.recommendations || []);
                }
            })
            .catch(err => console.error('加载推荐失败:', err));
    }

    function renderRecommendations(recs) {
        const container = document.getElementById('recommend-list');
        if (!container) return;

        container.innerHTML = '';

        if (!recs || recs.length === 0) {
            const p = document.createElement('p');
            p.className = 'empty-hint';
            p.textContent = '完成更多评估后将为您生成个性化推荐';
            container.appendChild(p);
            return;
        }

        recs.forEach(rec => {
            const group = document.createElement('div');
            group.className = 'recommend-group';

            const h3 = document.createElement('h3');
            h3.textContent = `${rec.label}（${rec.current_score || 0}分）`;

            const desc = document.createElement('p');
            desc.style.cssText = 'font-size:0.82rem;opacity:0.75;margin-bottom:0.5rem';
            desc.textContent = rec.suggestion || '';

            const tasksWrap = document.createElement('div');
            tasksWrap.className = 'recommend-tasks';

            (rec.recommended_tasks || []).forEach(t => {
                const taskItem = document.createElement('div');
                taskItem.className = 'task-item';

                const title = document.createElement('span');
                title.className = 'task-title';
                title.textContent = t.title;

                const badge = document.createElement('span');
                badge.className = 'task-badge';
                badge.textContent = t.difficulty;

                taskItem.append(title, badge);
                tasksWrap.appendChild(taskItem);
            });

            group.append(h3, desc, tasksWrap);
            container.appendChild(group);
        });
    }

    // =========================================
    // 提交历史
    // =========================================
    function loadSubmissionHistory() {
        fetch('/api/ability-matrix/history?limit=20')
            .then(res => res.json())
            .then(data => {
                if (data.status === 200) {
                    renderHistory(data.data?.submissions || []);
                }
            })
            .catch(err => console.error('加载历史记录失败:', err));
    }

    function renderHistory(submissions) {
        const tbody = document.getElementById('history-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (!submissions || submissions.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 7;
            td.className = 'empty-cell';
            td.textContent = '暂无历史记录';
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        submissions.forEach(s => {
            const tr = document.createElement('tr');
            const cells = [
                s.created_at || '-',
                SOURCE_LABELS[s.source_type] || s.source_type || '-',
                s.syntax_score || 0,
                s.algorithm_score || 0,
                s.project_score || 0,
                s.debug_score || 0,
                s.security_score || 0
            ];
            cells.forEach(val => {
                const td = document.createElement('td');
                td.textContent = val;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }

    // =========================================
    // 提交代码评估
    // =========================================
    function bindSubmitEvent() {
        const btn = document.getElementById('submit-btn');
        btn?.addEventListener('click', handleSubmit);
    }

    function handleSubmit() {
        const codeInput = document.getElementById('code-input');
        const code = codeInput?.value?.trim();

        if (!code) {
            showToast('请先输入代码', 'warning');
            return;
        }

        if (code.length < 10) {
            showToast('代码内容过短，请粘贴完整代码', 'warning');
            return;
        }

        showLoading(true);

        fetch('/api/ability-matrix/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ code: code })
        })
        .then(res => res.json())
        .then(data => {
            showLoading(false);
            if (data.status === 200) {
                showToast('评估完成！能力矩阵已更新', 'success');
                codeInput.value = '';
                // 重新加载所有数据
                loadAbilityMatrix();
                loadSubmissionHistory();
                loadRecommendations();
            } else {
                showToast(data.message || '评估失败', 'error');
            }
        })
        .catch(err => {
            showLoading(false);
            console.error('提交评估失败:', err);
            showToast('网络错误，请稍后重试', 'error');
        });
    }

    // =========================================
    // 工具函数
    // =========================================
    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    /** HTML 转义，防止 XSS */
    function esc(str) {
        if (str == null) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
        return String(str).replace(/[&<>"']/g, c => map[c]);
    }

    function showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.toggle('active', show);
        }
    }

    function showToast(msg, type = '') {
        const toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = msg;
        toast.className = 'toast show ' + type;
        setTimeout(() => {
            toast.className = 'toast';
        }, 3000);
    }
});

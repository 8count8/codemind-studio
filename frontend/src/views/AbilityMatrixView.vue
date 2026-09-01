<template>
  <!-- 导航栏 -->
  <nav class="navbar">
    <a class="logo" @click.prevent="$router.push('/dashboard')" href="#">
      <img src="/img/logo.jpg" alt="Logo" id="logo-img">
      <span>CodeMind Studio</span>
    </a>
    <div class="nav-buttons">
      <button class="btn btn-secondary" @click="$router.push('/dashboard')">返回首页</button>
      <ThemeToggle />
    </div>
  </nav>

  <div class="ability-container">
    <div class="page-header">
      <h1>能力矩阵</h1>
      <p class="page-subtitle">基于您的代码提交记录，全方位评估编程能力</p>
      <button class="btn btn-secondary export-btn" @click="exportReport" :disabled="exporting">
        {{ exporting ? '正在生成报告...' : '导出能力诊断 PDF' }}
      </button>
    </div>

    <!-- 顶部统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <span class="stat-value">{{ matrix.level || '初学者' }}</span>
          <span class="stat-label">当前等级</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <span class="stat-value">{{ matrix.total_submissions || 0 }}</span>
          <span class="stat-label">提交次数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
          <span class="stat-value">{{ averageScore }}</span>
          <span class="stat-label">平均得分</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <span class="stat-value">{{ percentile ? '超过' + percentile.overall_percentile + '%' : '-' }}</span>
          <span class="stat-label">群体分位</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-info">
          <span class="stat-value">{{ matrix.updated_at || '-' }}</span>
          <span class="stat-label">最近评估</span>
        </div>
      </div>
    </div>

    <!-- 成就勋章展示区 -->
    <div class="card achievements-card" v-if="achievements.length > 0">
      <h2 class="card-title">成就勋章（已解锁 {{ unlockedCount }}/{{ achievements.length }}）</h2>
      <div class="achievements-row">
        <div v-for="a in achievements" :key="a.id" class="achievement-badge" :class="{ unlocked: a.unlocked, locked: !a.unlocked }">
          <div class="badge-icon">{{ a.unlocked ? '🏅' : '🔒' }}</div>
          <div class="badge-name">{{ a.name }}</div>
          <div class="badge-desc">{{ a.description }}</div>
        </div>
      </div>
    </div>

    <!-- 主体两列布局 -->
    <div class="main-content">
      <div class="left-panel">
        <div class="card radar-card">
          <h2 class="card-title">能力雷达图</h2>
          <div class="radar-wrapper">
            <canvas ref="radarCanvas"></canvas>
          </div>
        </div>
        <div class="card dimensions-card">
          <h2 class="card-title">维度得分</h2>
          <div class="dimensions-list">
            <div v-for="dim in dimensions" :key="dim.key" class="dimension-item">
              <div class="dim-header">
                <span class="dim-label">{{ dim.label }}</span>
                <span class="dim-score">{{ matrix[dim.key] || 0 }}</span>
              </div>
              <div class="dim-bar"><div class="dim-bar-fill" :style="{ width: (matrix[dim.key] || 0) + '%' }"></div></div>
              <!-- 子维度细化展示 -->
              <div v-if="subscores[dim.key]" class="sub-dimensions">
                <span v-for="sub in subscores[dim.key].sub_dimensions" :key="sub.name" class="sub-dim-tag">
                  {{ sub.name }}: {{ sub.score }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="card weak-card">
          <h2 class="card-title">薄弱维度分析</h2>
          <div class="weak-list">
            <p v-if="weakDimensions.length === 0" class="empty-hint">暂无评估数据</p>
            <div v-for="w in weakDimensions" :key="w.key" class="weak-item">
              <span>{{ w.label }}: {{ matrix[w.key] || 0 }}分</span>
            </div>
          </div>
        </div>
        <div class="card recommend-card">
          <h2 class="card-title">智能推荐</h2>
          <!-- 推荐标签页切换 -->
          <div class="rec-tabs">
            <button :class="['rec-tab', { active: activeRecTab === 'rule' }]" @click="activeRecTab = 'rule'">规则推荐</button>
            <button :class="['rec-tab', { active: activeRecTab === 'content' }]" @click="activeRecTab = 'content'">内容推荐</button>
            <button :class="['rec-tab', { active: activeRecTab === 'collab' }]" @click="activeRecTab = 'collab'">协同推荐</button>
            <button :class="['rec-tab', { active: activeRecTab === 'error' }]" @click="activeRecTab = 'error'">错题强化</button>
            <button :class="['rec-tab', { active: activeRecTab === 'mastery' }]" @click="activeRecTab = 'mastery'">最近发展区</button>
          </div>
          <!-- 规则推荐 -->
          <div v-if="activeRecTab === 'rule'" class="recommend-list">
            <p v-if="recommendations.length === 0" class="empty-hint">完成评估后将为您生成推荐</p>
            <div v-for="(r, i) in recommendations" :key="i" class="recommend-item">
              <strong>{{ r.label }}</strong>（{{ r.current_score }}分）
              <p class="recommend-suggestion">{{ r.suggestion }}</p>
              <ul class="recommend-tasks">
                <li v-for="task in r.recommended_tasks" :key="task.title">{{ task.title }} · {{ task.difficulty }}</li>
              </ul>
            </div>
          </div>
          <!-- 内容推荐 -->
          <div v-if="activeRecTab === 'content'" class="recommend-list">
            <p v-if="contentRecs.length === 0" class="empty-hint">暂无内容推荐，需先答对题目</p>
            <div v-for="(r, i) in contentRecs" :key="'c'+i" class="recommend-item">
              <strong>{{ r.title }}</strong> · {{ r.difficulty }}
              <p class="recommend-suggestion">{{ r.reason }}</p>
            </div>
          </div>
          <!-- 协同过滤推荐 -->
          <div v-if="activeRecTab === 'collab'" class="recommend-list">
            <p v-if="collabRecs.length === 0" class="empty-hint">需用户量≥100 时启用协同过滤</p>
            <div v-for="(r, i) in collabRecs" :key="'co'+i" class="recommend-item">
              <strong>{{ r.title }}</strong> · {{ r.difficulty }}
              <p class="recommend-suggestion">{{ r.reason }}</p>
            </div>
          </div>
          <!-- 错题加权推荐 -->
          <div v-if="activeRecTab === 'error'" class="recommend-list">
            <p v-if="errorWeightedRecs.length === 0" class="empty-hint">暂无错题记录或错题无标签</p>
            <div v-for="(r, i) in errorWeightedRecs" :key="'e'+i" class="recommend-item">
              <strong>{{ r.title }}</strong> · {{ r.difficulty }}
              <p class="recommend-suggestion">{{ r.reason }}</p>
            </div>
          </div>
          <!-- 最近发展区推荐 -->
          <div v-if="activeRecTab === 'mastery'" class="recommend-list">
            <p v-if="masteryRecs.length === 0" class="empty-hint">暂无最近发展区推荐</p>
            <div v-for="(r, i) in masteryRecs" :key="'m'+i" class="recommend-item">
              <strong>{{ r.title }}</strong> · {{ r.difficulty }}
              <p class="recommend-suggestion">{{ r.reason }}</p>
            </div>
          </div>
        </div>
        <div class="card path-card">
          <h2 class="card-title">四周学习路径</h2>
          <p v-if="learningPath.length === 0" class="empty-hint">完成评估后生成周计划</p>
          <ol v-else class="learning-path">
            <li v-for="item in learningPath" :key="item.week">
              <strong>第 {{ item.week }} 周 · {{ item.focus }}</strong>
              <p>{{ item.goal }}</p>
              <span v-if="item.milestone" class="milestone-hint">📍 {{ item.milestone }}</span>
              <span v-for="task in item.tasks" :key="task.title" class="path-task">{{ task.title }}</span>
            </li>
          </ol>
        </div>
        <!-- 知识追踪（掌握概率） -->
        <div class="card mastery-card">
          <h2 class="card-title">知识追踪（掌握概率）</h2>
          <p v-if="mastery.length === 0" class="empty-hint">完成答题后将追踪各知识点掌握概率</p>
          <div v-else class="mastery-list">
            <div v-for="(m, i) in mastery.slice(0, 8)" :key="i" class="mastery-item">
              <div class="mastery-header">
                <span class="mastery-tag">{{ m.tag }}</span>
                <span class="mastery-prob" :class="{ zpd: m.in_zpd }">{{ (m.mastery_probability * 100).toFixed(0) }}%</span>
              </div>
              <div class="mastery-bar">
                <div class="mastery-bar-fill" :style="{ width: (m.mastery_probability * 100) + '%' }"></div>
              </div>
              <span class="mastery-label">{{ m.zpd_label }}</span>
            </div>
          </div>
        </div>
        <!-- 复习计划（Anki SM-2 间隔重复） -->
        <div class="card review-card">
          <h2 class="card-title">复习计划（间隔重复）<span v-if="dueReviewCount > 0" class="due-badge">{{ dueReviewCount }} 题到期</span></h2>
          <p v-if="reviewSchedule.length === 0" class="empty-hint">完成答题后将生成复习计划</p>
          <div v-else class="review-list">
            <div v-for="(r, i) in reviewSchedule" :key="i" class="review-item" :class="{ due: r.is_due }">
              <div class="review-header">
                <strong>{{ r.title || '题目 #' + r.question_id }}</strong>
                <span v-if="r.is_due" class="due-tag">需复习</span>
                <span v-else class="future-tag">{{ r.next_review_days }} 天后</span>
              </div>
              <span class="review-meta">难度: {{ r.difficulty }} | 下次复习: {{ r.next_review_date }}</span>
            </div>
          </div>
        </div>
        <!-- 错题诊断 -->
        <div class="card error-diagnosis-card">
          <h2 class="card-title">错题诊断</h2>
          <div v-if="errorPatterns.weak_tags && errorPatterns.weak_tags.length > 0" class="error-patterns">
            <h3 class="subsection-title">薄弱知识点</h3>
            <div class="weak-tags">
              <span v-for="(wt, i) in errorPatterns.weak_tags.slice(0, 5)" :key="i" class="weak-tag">
                {{ wt.tag }} ({{ wt.error_count }}错)
              </span>
            </div>
          </div>
          <div v-if="errorRecs.length > 0" class="error-recs">
            <h3 class="subsection-title">推荐强化练习</h3>
            <div v-for="(r, i) in errorRecs" :key="'er'+i" class="recommend-item">
              <strong>{{ r.title }}</strong> · {{ r.difficulty }}
              <p class="recommend-suggestion">{{ r.reason }}</p>
            </div>
          </div>
          <p v-if="(!errorPatterns.weak_tags || errorPatterns.weak_tags.length === 0) && errorRecs.length === 0" class="empty-hint">暂无错题诊断数据</p>
        </div>
        <div class="card submit-card">
          <h2 class="card-title">快速评估</h2>
          <p class="submit-hint">粘贴您的代码，系统将自动评估各项能力</p>
          <textarea v-model="codeInput" class="code-textarea" placeholder="在此粘贴您的代码..."></textarea>
          <button class="btn btn-primary submit-btn" @click="submitEvaluation" :disabled="submitting">
            {{ submitting ? '评估中...' : '提交评估' }}
          </button>
        </div>
      </div>
    </div>

    <div class="card trend-card">
      <h2 class="card-title">最近 30 天能力趋势</h2>
      <p v-if="!hasTrendData" class="empty-hint">完成更多评估后将显示趋势折线。</p>
      <div v-else class="trend-wrapper"><canvas ref="trendCanvas"></canvas></div>
    </div>

    <!-- 提交历史 -->
    <div class="card history-card">
      <h2 class="card-title">评估历史</h2>
      <div class="history-table-wrapper">
        <table class="history-table">
          <thead>
            <tr><th>时间</th><th>来源</th><th>语法基础</th><th>算法思维</th><th>项目实践</th><th>调试能力</th><th>安全意识</th></tr>
          </thead>
          <tbody>
            <tr v-if="history.length === 0"><td colspan="7" class="empty-cell">暂无历史记录</td></tr>
            <tr v-for="(h, i) in history" :key="i">
              <td>{{ h.created_at }}</td><td>{{ h.source }}</td>
              <td>{{ h.syntax_score }}</td><td>{{ h.algorithm_score }}</td>
              <td>{{ h.project_score }}</td><td>{{ h.debug_score }}</td><td>{{ h.security_score }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 加载遮罩 -->
  <LoadingOverlay :visible="submitting" text="正在评估中..." />
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import ThemeToggle from '../components/ThemeToggle.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'
import http from '../utils/http'
import { ABILITY_DIMENSIONS } from '../utils/constants'

Chart.register(...registerables)

const radarCanvas = ref(null)
const trendCanvas = ref(null)
let chartInstance = null
let trendChartInstance = null

const matrix = ref({})
const history = ref([])
const recommendations = ref([])
const learningPath = ref([])
const codeInput = ref('')
const submitting = ref(false)
const exporting = ref(false)
const trends = ref({})
const dimensions = ABILITY_DIMENSIONS

// P1/P2 新增响应式数据
const percentile = ref(null)          // 群体分位对比
const subscores = ref({})             // 子维度细化
const achievements = ref([])          // 成就勋章
const contentRecs = ref([])           // 内容推荐(标签相似度)
const collabRecs = ref([])            // 协同过滤推荐
const errorWeightedRecs = ref([])     // 错题加权推荐
const mastery = ref([])               // 知识追踪(掌握概率)
const masteryRecs = ref([])           // 最近发展区推荐
const reviewSchedule = ref([])        // 复习计划(Anki SM-2)
const errorPatterns = ref({})         // 错题诊断模式
const errorRecs = ref([])             // 错题诊断推荐
const activeRecTab = ref('rule')      // 推荐标签页: rule/content/collab/error/mastery

const averageScore = computed(() => {
  const keys = dimensions.map(d => d.key)
  const vals = keys.map(k => matrix.value[k] || 0)
  const sum = vals.reduce((a, b) => a + b, 0)
  return vals.length ? Math.round(sum / vals.length) : 0
})

const weakDimensions = computed(() => {
  return dimensions
    .map(d => ({ ...d, score: matrix.value[d.key] || 0 }))
    .filter(d => d.score > 0)
    .sort((a, b) => a.score - b.score)
    .slice(0, 3)
})

const hasTrendData = computed(() => Object.values(trends.value).some(item => (item.data || []).length > 1))

// 成就统计
const unlockedCount = computed(() => achievements.value.filter(a => a.unlocked).length)
const lockedCount = computed(() => achievements.value.filter(a => !a.unlocked).length)

// 到期复习题数
const dueReviewCount = computed(() => reviewSchedule.value.filter(r => r.is_due).length)

function renderChart() {
  if (!radarCanvas.value) return
  if (chartInstance) chartInstance.destroy()
  const scores = dimensions.map(d => matrix.value[d.key] || 0)
  const labels = dimensions.map(d => d.label)
  chartInstance = new Chart(radarCanvas.value, {
    type: 'radar',
    data: {
      labels,
      datasets: [{ label: '能力得分', data: scores, backgroundColor: 'rgba(66,133,244,0.2)', borderColor: '#4285f4', pointBackgroundColor: '#4285f4' }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } }
    }
  })
}

function renderTrendChart() {
  if (!trendCanvas.value || !hasTrendData.value) return
  if (trendChartInstance) trendChartInstance.destroy()
  const colors = ['#2563eb', '#7c3aed', '#059669', '#ea580c', '#dc2626']
  const entries = Object.values(trends.value)
  const maxPoints = Math.max(...entries.map(item => (item.data || []).length), 1)
  trendChartInstance = new Chart(trendCanvas.value, {
    type: 'line',
    data: {
      labels: Array.from({ length: maxPoints }, (_, i) => `第 ${i + 1} 次`),
      datasets: entries.map((item, index) => ({
        label: item.label,
        data: (item.data || []).map(point => point.score),
        borderColor: colors[index],
        backgroundColor: colors[index],
        tension: 0.3,
      })),
    },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } },
  })
}

async function loadMatrix() {
  try {
    const res = await http.get('/api/ability-matrix')
    if (res.data.status === 200) {
      const data = res.data.data || {}
      // 把 matrix 内部字段平铺到顶层，同时保留 weak_dimensions / average_score
      const m = data.matrix || {}
      matrix.value = {
        ...m,
        weak_dimensions: data.weak_dimensions || [],
        average_score: data.average_score || 0,
      }
      await nextTick()
      renderChart()
    }
  } catch (e) { console.error('加载能力矩阵失败:', e) }
}

async function loadHistory() {
  try {
    const res = await http.get('/api/ability-matrix/history')
    if (res.data.status === 200) {
      const data = res.data.data || {}
      history.value = data.history || []
    }
  } catch (e) { console.error('加载历史失败:', e) }
}

async function loadRecommendations() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations')
    if (res.data.status === 200) {
      const data = res.data.data || {}
      recommendations.value = data.recommendations || []
      learningPath.value = data.learning_path || []
    }
  } catch (e) { console.error('加载推荐失败:', e) }
}

async function loadTrends() {
  try {
    const res = await http.get('/api/ability-matrix/trend?days=30')
    trends.value = res.data?.data?.trends || {}
    await nextTick()
    renderTrendChart()
  } catch (e) { console.error('加载能力趋势失败:', e) }
}

// ============================================================
// P1/P2 新增 API 调用函数
// ============================================================

// 群体分位对比（§6.3）
async function loadPercentile() {
  try {
    const res = await http.get('/api/ability-matrix/percentile')
    if (res.data.status === 200) percentile.value = res.data.data
  } catch (e) { console.error('加载分位对比失败:', e) }
}

// 子维度细化（§1.2.1）
async function loadSubscores() {
  try {
    const res = await http.get('/api/ability-matrix/subscores')
    if (res.data.status === 200) subscores.value = res.data.data?.subscores || {}
  } catch (e) { console.error('加载子维度失败:', e) }
}

// 成就勋章（§十一）
async function loadAchievements() {
  try {
    const res = await http.get('/api/ability-matrix/achievements')
    if (res.data.status === 200) achievements.value = res.data.data?.achievements || []
  } catch (e) { console.error('加载成就失败:', e) }
}

// 内容推荐 - 标签相似度（§10.3.1）
async function loadContentRecs() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations/content?limit=5')
    if (res.data.status === 200) contentRecs.value = res.data.data?.recommendations || []
  } catch (e) { console.error('加载内容推荐失败:', e) }
}

// 协同过滤推荐（§10.4.1）
async function loadCollabRecs() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations/collaborative?limit=5')
    if (res.data.status === 200) collabRecs.value = res.data.data?.recommendations || []
  } catch (e) { console.error('加载协同推荐失败:', e) }
}

// 错题加权推荐（§10.3.2）
async function loadErrorWeightedRecs() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations/error-weighted?limit=5')
    if (res.data.status === 200) errorWeightedRecs.value = res.data.data?.recommendations || []
  } catch (e) { console.error('加载错题推荐失败:', e) }
}

// 知识追踪 - 掌握概率（§10.4.2）
async function loadMastery() {
  try {
    const res = await http.get('/api/ability-matrix/mastery')
    if (res.data.status === 200) mastery.value = res.data.data?.mastery || []
  } catch (e) { console.error('加载知识追踪失败:', e) }
}

// 最近发展区推荐（§10.4.2）
async function loadMasteryRecs() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations/mastery?limit=5')
    if (res.data.status === 200) masteryRecs.value = res.data.data?.recommendations || []
  } catch (e) { console.error('加载最近发展区推荐失败:', e) }
}

// 复习计划 - Anki SM-2（§10.4.3）
async function loadReviewSchedule() {
  try {
    const res = await http.get('/api/ability-matrix/review-schedule?limit=10')
    if (res.data.status === 200) reviewSchedule.value = res.data.data?.review_schedule || []
  } catch (e) { console.error('加载复习计划失败:', e) }
}

// 错题诊断 - 错误模式（P0 错题诊断引擎）
async function loadErrorPatterns() {
  try {
    const res = await http.get('/api/error-diagnosis/patterns?limit=50')
    if (res.data.status === 200) errorPatterns.value = res.data.data || {}
  } catch (e) { console.error('加载错题诊断失败:', e) }
}

// 错题诊断 - 相似题推荐（P0 错题诊断引擎）
async function loadErrorRecs() {
  try {
    const res = await http.get('/api/error-diagnosis/recommendations?limit=5')
    if (res.data.status === 200) errorRecs.value = res.data.data?.recommendations || []
  } catch (e) { console.error('加载错题推荐失败:', e) }
}

async function submitEvaluation() {
  if (!codeInput.value.trim()) { alert('请输入代码'); return }
  submitting.value = true
  try {
    const res = await http.post('/api/ability-matrix/submit', { code: codeInput.value, language: 'python' })
    await loadMatrix()
    await loadHistory()
    await loadRecommendations()
    // 评估后刷新 P1/P2 数据
    await Promise.all([
      loadPercentile(),
      loadSubscores(),
      loadAchievements(),
      loadMastery(),
      loadReviewSchedule(),
    ])
    codeInput.value = ''
    // 检查是否有新成就解锁
    const newAch = res.data?.data?.newly_unlocked || []
    if (newAch.length > 0) {
      const names = newAch.map(a => a.name).join('、')
      alert(`评估完成！恭喜解锁新成就：${names}`)
    } else {
      alert('评估完成')
    }
  } catch (e) { alert('评估失败: ' + (e.response?.data?.message || e.message)) }
  finally { submitting.value = false }
}

async function exportReport() {
  exporting.value = true
  try {
    const res = await http.get('/api/ability-matrix/export?format=pdf', { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'codemind-ability-report.pdf'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('报告导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  // 并行加载所有数据
  await Promise.all([
    loadMatrix(),
    loadHistory(),
    loadRecommendations(),
    loadTrends(),
  ])
  // 并行加载 P1/P2 增强数据
  await Promise.all([
    loadPercentile(),
    loadSubscores(),
    loadAchievements(),
    loadContentRecs(),
    loadCollabRecs(),
    loadErrorWeightedRecs(),
    loadMastery(),
    loadMasteryRecs(),
    loadReviewSchedule(),
    loadErrorPatterns(),
    loadErrorRecs(),
  ])
})
</script>

<style>
@import '../assets/css/ability_matrix.css';
</style>

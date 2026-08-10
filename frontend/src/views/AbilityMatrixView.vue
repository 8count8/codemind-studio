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
        <div class="stat-icon">📅</div>
        <div class="stat-info">
          <span class="stat-value">{{ matrix.updated_at || '-' }}</span>
          <span class="stat-label">最近评估</span>
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
          <h2 class="card-title">学习推荐</h2>
          <div class="recommend-list">
            <p v-if="recommendations.length === 0" class="empty-hint">完成评估后将为您生成推荐</p>
            <div v-for="(r, i) in recommendations" :key="i" class="recommend-item">{{ r }}</div>
          </div>
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
let chartInstance = null

const matrix = ref({})
const history = ref([])
const recommendations = ref([])
const codeInput = ref('')
const submitting = ref(false)
const dimensions = ABILITY_DIMENSIONS

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

async function loadMatrix() {
  try {
    const res = await http.get('/api/ability-matrix')
    if (res.data.status === 200) {
      matrix.value = res.data.data || {}
      await nextTick()
      renderChart()
    }
  } catch (e) { console.error('加载能力矩阵失败:', e) }
}

async function loadHistory() {
  try {
    const res = await http.get('/api/ability-matrix/history')
    if (res.data.status === 200) history.value = res.data.data || []
  } catch (e) { console.error('加载历史失败:', e) }
}

async function loadRecommendations() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations')
    if (res.data.status === 200) recommendations.value = res.data.data || []
  } catch (e) { console.error('加载推荐失败:', e) }
}

async function submitEvaluation() {
  if (!codeInput.value.trim()) { alert('请输入代码'); return }
  submitting.value = true
  try {
    await http.post('/api/ability-matrix/submit', { code: codeInput.value, language: 'python' })
    await loadMatrix()
    await loadHistory()
    await loadRecommendations()
    codeInput.value = ''
    alert('评估完成')
  } catch (e) { alert('评估失败: ' + (e.response?.data?.message || e.message)) }
  finally { submitting.value = false }
}

onMounted(async () => {
  await loadMatrix()
  await loadHistory()
  await loadRecommendations()
})
</script>

<style>
@import '../assets/css/ability_matrix.css';
</style>

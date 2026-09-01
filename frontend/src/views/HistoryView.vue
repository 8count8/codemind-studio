<template>
  <nav class="navbar">
    <a class="logo" href="#" @click.prevent="router.push('/dashboard')">
      <img src="/img/logo.jpg" alt="Logo"><span>CodeMind Studio</span>
    </a>
    <div class="nav-buttons"><ThemeToggle /></div>
  </nav>

  <main class="history-page">
    <div class="page-heading">
      <div><p class="eyebrow">学习轨迹</p><h1>代码提交历史</h1><p>筛选提交、查看完整判题结果，并对比任意两个代码快照。</p></div>
      <button class="primary-btn" :disabled="selectedIds.length !== 2" @click="compareSelected">对比所选版本（{{ selectedIds.length }}/2）</button>
    </div>

    <form class="filters" @submit.prevent="applyFilters">
      <input v-model="filters.keyword" placeholder="搜索题目标题">
      <select v-model="filters.result"><option value="">全部结果</option><option value="passed">通过</option><option value="failed">未通过</option></select>
      <select v-model="filters.difficulty"><option value="">全部难度</option><option>简单</option><option>中等</option><option>困难</option></select>
      <input v-model="filters.date_from" type="date" aria-label="开始日期">
      <input v-model="filters.date_to" type="date" aria-label="结束日期">
      <button class="primary-btn">筛选</button>
      <button type="button" class="ghost-btn" @click="resetFilters">重置</button>
    </form>

    <div class="history-card">
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="items.length === 0" class="empty">暂无提交记录，完成一次题目提交后会显示在这里。</div>
      <div v-for="item in items" :key="item.id" class="submission-row">
        <label class="compare-check"><input type="checkbox" :checked="selectedIds.includes(item.id)" @change="toggleSelected(item.id)"><span>对比</span></label>
        <div class="submission-main" @click="openDetail(item.id)">
          <div class="submission-title"><strong>{{ item.title }}</strong><span class="status" :class="item.is_correct ? 'passed' : 'failed'">{{ item.is_correct ? '通过' : '未通过' }}</span></div>
          <div class="meta"><span>{{ item.difficulty || '未知难度' }}</span><span>{{ item.language || 'python' }}</span><span>得分 {{ Math.round(item.score || 0) }}</span><span>{{ item.run_time_ms || 0 }} ms</span><span>{{ formatTime(item.created_at) }}</span></div>
        </div>
        <button class="ghost-btn" @click="openDetail(item.id)">查看代码</button>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button class="ghost-btn" :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页 · 共 {{ total }} 条</span>
      <button class="ghost-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">下一页</button>
    </div>
  </main>

  <div v-if="detail" class="modal-backdrop" @click.self="detail = null">
    <section class="modal-card">
      <button class="close-btn" @click="detail = null">×</button>
      <h2>{{ detail.title }}</h2>
      <p class="meta">{{ detail.language }} · {{ formatTime(detail.created_at) }} · 得分 {{ Math.round(detail.score || 0) }}</p>
      <h3>代码快照</h3><pre><code>{{ detail.code }}</code></pre>
      <h3>执行结果</h3><pre><code>{{ formatExecution(detail.execution_result) }}</code></pre>
    </section>
  </div>

  <div v-if="comparison" class="modal-backdrop" @click.self="comparison = null">
    <section class="modal-card compare-modal">
      <button class="close-btn" @click="comparison = null">×</button>
      <h2>代码版本对比</h2>
      <div class="compare-grid">
        <article v-for="side in ['left', 'right']" :key="side">
          <h3>{{ comparison[side].title }} · #{{ comparison[side].id }}</h3>
          <p class="meta">{{ formatTime(comparison[side].created_at) }} · {{ comparison[side].score }} 分</p>
          <pre><code>{{ comparison[side].code }}</code></pre>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const router = useRouter()
const items = ref([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const perPage = 20
const detail = ref(null)
const comparison = ref(null)
const selectedIds = ref([])
const filters = ref({ keyword: '', result: '', difficulty: '', date_from: '', date_to: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

function formatTime(value) { return value ? new Date(value).toLocaleString('zh-CN') : '-' }
function formatExecution(value) { return typeof value === 'string' ? value : JSON.stringify(value || {}, null, 2) }

async function loadHistory() {
  loading.value = true
  try {
    const res = await http.get('/api/history/submissions', { params: { ...filters.value, page: page.value, per_page: perPage } })
    const data = res.data?.data || {}
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('加载提交历史失败:', e)
    items.value = []
  } finally { loading.value = false }
}

function applyFilters() { page.value = 1; selectedIds.value = []; loadHistory() }
function resetFilters() { filters.value = { keyword: '', result: '', difficulty: '', date_from: '', date_to: '' }; applyFilters() }
function changePage(next) { page.value = next; selectedIds.value = []; loadHistory() }
function toggleSelected(id) {
  if (selectedIds.value.includes(id)) selectedIds.value = selectedIds.value.filter(value => value !== id)
  else if (selectedIds.value.length < 2) selectedIds.value = [...selectedIds.value, id]
  else alert('一次只能选择两个版本进行对比')
}
async function openDetail(id) {
  const res = await http.get(`/api/history/submissions/${id}`)
  detail.value = res.data?.data || null
}
async function compareSelected() {
  const [left, right] = selectedIds.value
  const res = await http.get('/api/history/compare', { params: { left, right } })
  comparison.value = res.data?.data || null
}

onMounted(loadHistory)
</script>

<style scoped>
.navbar { display:flex; justify-content:space-between; align-items:center; padding:12px 30px; background:var(--card-bg,#fff); box-shadow:0 2px 12px rgba(0,0,0,.08); }
.logo { display:flex; align-items:center; gap:10px; color:var(--primary-color,#2563eb); text-decoration:none; font-weight:700; }.logo img{width:36px;height:36px;border-radius:50%}
.history-page { max-width:1120px; margin:34px auto; padding:0 20px; color:var(--text-color,#1f2937); }
.page-heading { display:flex; align-items:end; justify-content:space-between; gap:20px; margin-bottom:22px; }.page-heading h1{margin:.15rem 0}.eyebrow{color:var(--primary-color,#2563eb);font-size:.78rem;font-weight:800;letter-spacing:.08em}
.filters { display:grid; grid-template-columns:2fr repeat(4,1fr) auto auto; gap:10px; margin-bottom:18px; }.filters input,.filters select{min-width:0;padding:10px;border:1px solid #cbd5e1;border-radius:8px;background:var(--card-bg,#fff);color:inherit}
.primary-btn,.ghost-btn{border:0;border-radius:8px;padding:9px 14px;cursor:pointer}.primary-btn{background:var(--primary-color,#2563eb);color:#fff}.ghost-btn{background:#e2e8f0;color:#334155}.primary-btn:disabled,.ghost-btn:disabled{opacity:.45;cursor:not-allowed}
.history-card{background:var(--card-bg,#fff);border-radius:14px;box-shadow:0 5px 24px rgba(0,0,0,.08);overflow:hidden}.submission-row{display:grid;grid-template-columns:64px 1fr auto;gap:14px;align-items:center;padding:16px;border-bottom:1px solid #e2e8f0}.submission-row:last-child{border:0}.submission-main{cursor:pointer}.submission-title{display:flex;align-items:center;gap:10px}.status{font-size:.75rem;padding:2px 8px;border-radius:999px}.status.passed{color:#047857;background:#d1fae5}.status.failed{color:#b91c1c;background:#fee2e2}.meta{display:flex;gap:12px;flex-wrap:wrap;color:#64748b;font-size:.85rem;margin-top:6px}.compare-check{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:.72rem}.empty{text-align:center;padding:48px;color:#64748b}.pagination{display:flex;justify-content:center;align-items:center;gap:14px;margin-top:18px}
.modal-backdrop{position:fixed;inset:0;background:rgba(15,23,42,.72);display:grid;place-items:center;padding:24px;z-index:2000}.modal-card{position:relative;width:min(900px,96vw);max-height:90vh;overflow:auto;background:var(--card-bg,#fff);color:var(--text-color,#1f2937);border-radius:14px;padding:24px}.close-btn{position:absolute;right:14px;top:10px;border:0;background:transparent;font-size:28px;cursor:pointer;color:inherit}.modal-card pre{background:#0f172a;color:#e2e8f0;padding:15px;border-radius:9px;overflow:auto;white-space:pre-wrap}.compare-modal{width:min(1240px,96vw)}.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.compare-grid pre{min-height:420px;white-space:pre;}
@media(max-width:900px){.filters{grid-template-columns:1fr 1fr}.page-heading{align-items:flex-start;flex-direction:column}.compare-grid{grid-template-columns:1fr}.submission-row{grid-template-columns:52px 1fr}.submission-row>button{grid-column:2}.meta{gap:7px}}
</style>

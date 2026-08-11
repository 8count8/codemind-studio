<template>
  <!-- 导航栏 -->
  <nav class="navbar">
    <a class="logo">
      <img src="/img/logo.jpg" alt="Logo" id="logo-img">
      <span>CodeMind Studio</span>
    </a>
    <div class="nav-buttons">
      <ThemeToggle />
    </div>
  </nav>

  <div class="profile-container">
    <div class="profile-info">
      <h2>历史记录</h2>
    </div>
    <div class="history-list" id="history-list">
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="historyItems.length === 0" class="empty">暂无历史记录</div>
      <div
        v-for="(item, idx) in historyItems"
        :key="idx"
        class="history-item"
      >
        <div class="history-item-header">
          <span class="history-type-badge" :class="'badge-' + item.record_type">
            {{ typeLabel(item.record_type) }}
          </span>
          <h4>{{ item.name || '未命名' }}</h4>
        </div>
        <p class="history-meta">
          {{ item.file_type || '' }}
          <span v-if="item.timestamp"> · {{ formatTime(item.timestamp) }}</span>
        </p>
      </div>
    </div>
    <div class="profile-actions">
      <router-link to="/dashboard">返回</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const router = useRouter()
const historyItems = ref([])
const loading = ref(true)

function typeLabel(type) {
  const map = {
    'function': '功能使用',
    'upload': '代码上传',
    'api_response': '审查结果'
  }
  return map[type] || type
}

function formatTime(ts) {
  if (!ts) return ''
  try {
    return new Date(ts).toLocaleString('zh-CN')
  } catch {
    return String(ts)
  }
}

onMounted(async () => {
  try {
    const res = await http.get('/api/user/history')
    if (res.data.status === 200) {
      historyItems.value = res.data.data || []
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
    historyItems.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 30px;
  background: var(--bg-secondary, #1a1a2e);
  border-bottom: 1px solid var(--border-color, #333);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-primary, #eee);
  font-size: 1.3rem;
  font-weight: bold;
}
#logo-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}
.profile-container {
  max-width: 800px;
  margin: 30px auto;
  padding: 0 20px;
}
.profile-info h2 {
  color: var(--text-primary, #eee);
  margin-bottom: 20px;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.empty {
  text-align: center;
  color: var(--text-secondary, #888);
  padding: 40px 0;
}
.history-item {
  background: var(--bg-card, #16213e);
  border: 1px solid var(--border-color, #333);
  border-radius: 8px;
  padding: 16px 20px;
  transition: border-color 0.2s;
}
.history-item:hover {
  border-color: var(--accent, #e94560);
}
.history-item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.history-item-header h4 {
  margin: 0;
  color: var(--text-primary, #eee);
  font-size: 1rem;
}
.history-type-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.badge-function {
  background: #3b82f620;
  color: #60a5fa;
}
.badge-upload {
  background: #e9456020;
  color: #f87171;
}
.badge-api_response {
  background: #10b98120;
  color: #34d399;
}
.history-meta {
  margin: 0;
  color: var(--text-secondary, #888);
  font-size: 0.85rem;
}
.profile-actions {
  margin-top: 24px;
  text-align: center;
}
.profile-actions a {
  display: inline-block;
  padding: 10px 30px;
  background: var(--accent, #e94560);
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  transition: opacity 0.2s;
}
.profile-actions a:hover {
  opacity: 0.85;
}
</style>

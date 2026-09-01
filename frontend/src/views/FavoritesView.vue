<template>
  <nav class="navbar">
    <a class="logo" href="#" @click.prevent="router.push('/dashboard')"><img src="/img/logo.jpg" alt="Logo"><span>CodeMind Studio</span></a>
    <ThemeToggle />
  </nav>
  <main class="favorites-page">
    <header class="page-heading">
      <div><p class="eyebrow">我的收藏</p><h1>收藏题单</h1><p>建立主题题单、添加标签，并把收藏题目拖入清晰的学习计划。</p></div>
      <button class="primary-btn" @click="createTopic">+ 新建题单</button>
    </header>

    <section class="topic-strip">
      <button :class="{active: activeTopic === 'all'}" @click="activeTopic = 'all'">全部 <small>{{ favorites.length }}</small></button>
      <button :class="{active: activeTopic === null}" @click="activeTopic = null">未分类 <small>{{ unclassifiedCount }}</small></button>
      <div v-for="topic in topics" :key="topic.id" class="topic-pill" :class="{active: activeTopic === topic.id}">
        <button @click="activeTopic = topic.id">{{ topic.name }} <small>{{ topic.item_count }}</small></button>
        <button title="编辑题单" @click="editTopic(topic)">✎</button>
        <button title="删除题单" @click="deleteTopic(topic)">×</button>
      </div>
    </section>

    <section class="favorites-grid">
      <p v-if="filteredFavorites.length === 0" class="empty">当前题单暂无收藏题目。</p>
      <article v-for="fav in filteredFavorites" :key="fav.id" class="favorite-card">
        <div class="card-top"><span class="difficulty">{{ fav.difficulty || '未标难度' }}</span><button class="remove-btn" @click="removeFavorite(fav)">移除</button></div>
        <h2 @click="goQuestion(fav.id)">{{ fav.title }}</h2>
        <div class="tags"><span v-for="tag in parseTags(fav.tags)" :key="tag">{{ tag }}</span></div>
        <label>所属题单
          <select :value="fav.topic_id || ''" @change="assignTopic(fav, $event.target.value)">
            <option value="">未分类</option>
            <option v-for="topic in topics" :key="topic.id" :value="topic.id">{{ topic.name }}</option>
          </select>
        </label>
        <button class="practice-btn" @click="goQuestion(fav.id)">继续练习 →</button>
      </article>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const router = useRouter()
const favorites = ref([])
const topics = ref([])
const activeTopic = ref('all')
const unclassifiedCount = computed(() => favorites.value.filter(item => !item.topic_id).length)
const filteredFavorites = computed(() => {
  if (activeTopic.value === 'all') return favorites.value
  if (activeTopic.value === null) return favorites.value.filter(item => !item.topic_id)
  return favorites.value.filter(item => Number(item.topic_id) === Number(activeTopic.value))
})

function parseTags(value) {
  if (Array.isArray(value)) return value
  try { const parsed = JSON.parse(value); return Array.isArray(parsed) ? parsed : String(value || '').split(',').filter(Boolean) }
  catch { return String(value || '').split(',').map(v => v.trim()).filter(Boolean) }
}
function goQuestion(id) { router.push(`/answerpad?questionId=${id}`) }
async function loadData() {
  const [favRes, topicRes] = await Promise.all([http.get('/api/user/favorites'), http.get('/api/favorites/topics')])
  favorites.value = favRes.data?.data || []
  topics.value = topicRes.data?.data || []
}
async function createTopic() {
  const name = prompt('题单名称')
  if (!name) return
  const description = prompt('题单说明（可选）') || ''
  const tags = prompt('题单标签（逗号分隔，可选）') || ''
  try { await http.post('/api/favorites/topics', { name, description, tags }); await loadData() }
  catch (e) { alert(e.response?.data?.message || '创建题单失败') }
}
async function editTopic(topic) {
  const name = prompt('题单名称', topic.name)
  if (!name) return
  const description = prompt('题单说明', topic.description || '') ?? topic.description
  const tags = prompt('题单标签（逗号分隔）', topic.tags || '') ?? topic.tags
  try { await http.put(`/api/favorites/topics/${topic.id}`, { name, description, tags }); await loadData() }
  catch (e) { alert(e.response?.data?.message || '更新题单失败') }
}
async function deleteTopic(topic) {
  if (!confirm(`删除题单“${topic.name}”？题目会保留在未分类中。`)) return
  await http.delete(`/api/favorites/topics/${topic.id}`)
  if (activeTopic.value === topic.id) activeTopic.value = 'all'
  await loadData()
}
async function assignTopic(fav, value) {
  await http.post('/api/favorites/assign', { question_id: fav.id, topic_id: value || null })
  await loadData()
}
async function removeFavorite(fav) {
  if (!confirm(`从收藏中移除“${fav.title}”？`)) return
  await http.post('/api/user/favorites', { questionId: fav.id, action: 'remove' })
  await loadData()
}
onMounted(() => loadData().catch(e => console.error('加载收藏失败:', e)))
</script>

<style scoped>
.navbar{display:flex;justify-content:space-between;align-items:center;padding:12px 30px;background:var(--card-bg,#fff);box-shadow:0 2px 12px rgba(0,0,0,.08)}.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--primary-color,#2563eb);font-weight:700}.logo img{width:36px;height:36px;border-radius:50%}
.favorites-page{max-width:1120px;margin:34px auto;padding:0 20px;color:var(--text-color,#1f2937)}.page-heading{display:flex;align-items:end;justify-content:space-between;gap:20px}.page-heading h1{margin:.15rem 0}.eyebrow{color:var(--primary-color,#2563eb);font-size:.78rem;font-weight:800;letter-spacing:.08em}.primary-btn,.practice-btn{border:0;border-radius:9px;padding:10px 15px;background:var(--primary-color,#2563eb);color:white;cursor:pointer}
.topic-strip{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:24px 0}.topic-strip>button,.topic-pill{border:1px solid #cbd5e1;background:var(--card-bg,#fff);border-radius:999px;color:inherit}.topic-strip>button,.topic-pill button{padding:8px 12px;border:0;background:transparent;color:inherit;cursor:pointer}.topic-pill{display:flex;overflow:hidden}.topic-pill button+button{padding-left:5px;padding-right:7px}.topic-strip .active{border-color:var(--primary-color,#2563eb);color:var(--primary-color,#2563eb);box-shadow:0 0 0 2px color-mix(in srgb,var(--primary-color,#2563eb) 14%,transparent)}small{opacity:.65}
.favorites-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.favorite-card{background:var(--card-bg,#fff);border:1px solid #e2e8f0;border-radius:14px;padding:18px;box-shadow:0 5px 20px rgba(0,0,0,.06)}.card-top{display:flex;justify-content:space-between}.difficulty{font-size:.75rem;padding:3px 8px;border-radius:999px;background:#dbeafe;color:#1d4ed8}.remove-btn{border:0;background:transparent;color:#dc2626;cursor:pointer}.favorite-card h2{font-size:1.08rem;cursor:pointer;margin:14px 0}.tags{display:flex;gap:6px;flex-wrap:wrap;min-height:24px}.tags span{font-size:.72rem;background:#f1f5f9;color:#475569;padding:3px 7px;border-radius:5px}.favorite-card label{display:grid;gap:5px;font-size:.8rem;color:#64748b;margin:15px 0}.favorite-card select{padding:8px;border:1px solid #cbd5e1;border-radius:7px;background:var(--card-bg,#fff);color:var(--text-color,#1f2937)}.practice-btn{width:100%}.empty{grid-column:1/-1;text-align:center;padding:50px;color:#64748b}
@media(max-width:900px){.favorites-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){.favorites-grid{grid-template-columns:1fr}.page-heading{align-items:flex-start;flex-direction:column}}
</style>

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

  <div class="container">
    <!-- 筛选面板 -->
    <aside class="filter-panel">
      <div class="filter-section">
        <h3>难度等级</h3>
        <div class="difficulty-filter" id="difficulty-filter">
          <div
            v-for="d in difficulties"
            :key="d"
            class="filter-option"
            :class="{ active: selectedDifficulties.has(d) }"
            @click="toggleDifficulty(d)"
          >{{ d }}</div>
        </div>
      </div>

      <div class="filter-section">
        <h3>知识点标签</h3>
        <div class="tag-filter" id="tag-filter">
          <div
            v-for="tag in allTags"
            :key="tag"
            class="filter-option"
            :class="{ active: selectedTags.has(tag) }"
            @click="toggleTag(tag)"
          >{{ tag }}</div>
        </div>
      </div>
    </aside>

    <!-- 主要内容区 -->
    <main class="main-content">
      <div class="search-box">
        <input type="text" id="search-input" v-model="searchQuery" placeholder="输入关键词搜索题目...">
        <button id="search-btn">搜索</button>
      </div>

      <div class="question-list" id="question-list">
        <div
          v-for="q in filteredQuestions"
          :key="q.id"
          class="question-card"
          :data-id="q.id"
          @click="goAnswer(q.id)"
        >
          <div class="question-header">
            <div class="question-title">{{ q.title }}</div>
            <button class="favorite-btn" @click.stop="toggleFavorite(q)">
              {{ q.favorite ? '★' : '☆' }}
            </button>
          </div>
          <div class="question-meta">
            <span>难度：{{ q.difficulty }}</span>
            <span>创建时间：{{ formatDate(q.created_at) }}</span>
          </div>
          <div class="question-tags">
            <span class="tag" v-for="tag in parseTags(q.tags)" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const router = useRouter()

const questions = ref([])
const selectedDifficulties = ref(new Set())
const selectedTags = ref(new Set())
const searchQuery = ref('')
const difficulties = ['简单', '中等', '困难']

const allTags = computed(() => {
  const tagSet = new Set()
  questions.value.forEach(q => {
    parseTags(q.tags).forEach(t => tagSet.add(t))
  })
  return [...tagSet]
})

const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    const matchesDiff = selectedDifficulties.value.size === 0 || selectedDifficulties.value.has(q.difficulty)
    const tags = parseTags(q.tags)
    const matchesTag = selectedTags.value.size === 0 || tags.some(t => selectedTags.value.has(t))
    const query = searchQuery.value.trim()
    const matchesSearch = !query || q.title.includes(query) || tags.some(t => t.includes(query))
    return matchesDiff && matchesTag && matchesSearch
  })
})

function parseTags(tagsStr) {
  try {
    return JSON.parse(tagsStr)
  } catch {
    return []
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString()
}

function toggleDifficulty(d) {
  const s = new Set(selectedDifficulties.value)
  s.has(d) ? s.delete(d) : s.add(d)
  selectedDifficulties.value = s
}

function toggleTag(tag) {
  const s = new Set(selectedTags.value)
  s.has(tag) ? s.delete(tag) : s.add(tag)
  selectedTags.value = s
}

function goAnswer(questionId) {
  router.push(`/answerpad?questionId=${questionId}`)
}

async function toggleFavorite(q) {
  try {
    await http.post('/api/user/favorites', {
      questionId: q.id,
      action: q.favorite ? 'remove' : 'add'
    })
    q.favorite = !q.favorite
  } catch (e) {
    console.error('收藏操作失败:', e)
  }
}

onMounted(async () => {
  try {
    const res = await http.get('/api/questions')
    if (res.data.status === 200) {
      questions.value = res.data.data || []
    }
  } catch (e) {
    console.error('获取题目失败:', e)
  }
})
</script>

<style>
@import '../assets/css/quizbank.css';
</style>

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
      <div v-if="historyItems.length === 0" class="empty">暂无历史记录</div>
      <div
        v-for="(item, idx) in historyItems"
        :key="idx"
        class="history-item"
        @click="goQuestion(item.questionId)"
      >
        <h4>{{ item.title || '未命名题目' }}</h4>
        <p>{{ item.language }} - {{ item.date }}</p>
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

const router = useRouter()
const historyItems = ref([])

function goQuestion(questionId) {
  if (questionId) {
    router.push(`/answerpad?questionId=${questionId}`)
  }
}

onMounted(() => {
  // 从 localStorage 加载历史记录
  try {
    const data = JSON.parse(localStorage.getItem('answerHistory')) || []
    historyItems.value = data
  } catch {
    historyItems.value = []
  }
})
</script>

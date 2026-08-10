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
      <h2>收藏记录</h2>
    </div>
    <div class="favorites-list" id="favorites-list">
      <div v-if="favorites.length === 0" class="empty">暂无收藏题目</div>
      <div
        v-for="fav in favorites"
        :key="fav.id"
        class="favorite-item"
        @click="goQuestion(fav.id)"
      >
        <h4>{{ fav.title }}</h4>
        <p>难度：{{ fav.difficulty }}</p>
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
const favorites = ref([])

function goQuestion(id) {
  router.push(`/answerpad?questionId=${id}`)
}

onMounted(async () => {
  try {
    const res = await http.get('/api/user/favorites')
    if (res.data.status === 200) {
      favorites.value = res.data.data || []
    }
  } catch (e) {
    console.error('获取收藏失败:', e)
  }
})
</script>

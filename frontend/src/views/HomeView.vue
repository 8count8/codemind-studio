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

  <!-- 主大屏区域 -->
  <section class="hero">
    <h1>掌握编程，从今天开始</h1>
    <p>AI驱动的个性化学习平台，帮助你高效掌握编程技能，实时反馈，智能推荐学习路径</p>
    <button class="btn btn-primary" id="start-btn" @click="goStart">立即开始</button>
  </section>

  <!-- 网站介绍区域 -->
  <section class="features">
    <h2 class="section-title">我们的特色</h2>
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">💡</div>
        <h3>智能评估</h3>
        <p>基于AI的用户能力评估系统，精准分析你的编程水平，推荐最适合的学习路径。</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>个性化出题</h3>
        <p>智能出题引擎根据你的学习进度和能力，动态调整题目难度和类型。</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>实时反馈</h3>
        <p>代码练习+AI实时反馈，立即发现并改正错误，加速学习过程。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()

function goStart() {
  router.push('/dashboard')
}
</script>

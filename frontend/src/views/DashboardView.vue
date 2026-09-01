<template>
  <!-- 导航栏 -->
  <Navbar />

  <!-- 主内容区 -->
  <main class="container">
    <section class="dashboard-hero">
      <div>
        <p class="eyebrow">学习工作台</p>
        <h1>今天也向前一步</h1>
        <p>查看学习进度，继续练习，或进入 AI 辅助模块。</p>
      </div>
      <button v-if="summary.recent_practice" class="continue-btn" @click="continuePractice">
        继续：{{ summary.recent_practice.title || `题目 #${summary.recent_practice.question_id}` }}
      </button>
      <button v-else class="continue-btn" @click="router.push('/quizbank')">开始第一次练习</button>
    </section>

    <section class="overview-grid" aria-label="学习数据概览">
      <div v-for="card in statCards" :key="card.label" class="overview-card">
        <span>{{ card.icon }}</span><strong>{{ card.value }}</strong><small>{{ card.label }}</small>
      </div>
    </section>

    <section class="ability-preview">
      <div class="section-heading">
        <div><p class="eyebrow">五维能力</p><h2>能力矩阵缩略图</h2></div>
        <button class="text-btn" @click="router.push('/ability-matrix')">查看完整矩阵 →</button>
      </div>
      <div class="ability-bars">
        <div v-for="dim in dimensions" :key="dim.key" class="ability-row">
          <span>{{ dim.label }}</span>
          <div><i :style="{ width: `${summary.ability?.[dim.key] || 0}%` }"></i></div>
          <strong>{{ Math.round(summary.ability?.[dim.key] || 0) }}</strong>
        </div>
      </div>
    </section>

    <!-- 功能模块 -->
    <section class="modules">
      <div class="module-card" data-module="practice" @click="goModule('practice')">
        <h3>代码练习</h3>
        <p>通过实战提升编程能力</p>
      </div>
      <div class="module-card" data-module="ai-question" @click="goModule('ai-question')">
        <h3>AI编程题</h3>
        <p>AI生成编程题</p>
      </div>
      <div class="module-card" data-module="ai-review" @click="goModule('ai-review')">
        <h3>AI代码审查</h3>
        <p>获取智能代码分析建议</p>
      </div>
      <div class="module-card" data-module="ability-matrix" @click="goModule('ability-matrix')">
        <h3>能力矩阵</h3>
        <p>全方位评估编程能力</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import http from '../utils/http'
import { ABILITY_DIMENSIONS } from '../utils/constants'

const router = useRouter()
const summary = ref({ stats: {}, ability: {}, streak_days: 0, recent_practice: null })
const dimensions = ABILITY_DIMENSIONS
const statCards = computed(() => [
  { icon: '✓', label: '已练题目', value: summary.value.stats?.answers || 0 },
  { icon: '⌨', label: '代码提交', value: summary.value.stats?.submissions || 0 },
  { icon: '★', label: '收藏题目', value: summary.value.stats?.favorites || 0 },
  { icon: '🔥', label: '连续学习天数', value: summary.value.streak_days || 0 },
])

function continuePractice() {
  const id = summary.value.recent_practice?.question_id
  router.push(id ? `/answerpad?questionId=${id}` : '/quizbank')
}

function goModule(module) {
  switch (module) {
    case 'practice':
      router.push('/quizbank')
      break
    case 'ai-question':
      router.push('/ai-question')
      break
    case 'ai-review':
      router.push('/code-review')
      break
    case 'ability-matrix':
      router.push('/ability-matrix')
      break
    default:
      console.warn(`未知模块: ${module}`)
  }
}

onMounted(async () => {
  try {
    const res = await http.get('/api/dashboard/summary')
    if (res.data?.status === 200) summary.value = res.data.data || summary.value
  } catch (e) {
    console.error('加载学习概览失败:', e)
  }
})
</script>

<style>
@import '../assets/css/dashboard.css';
</style>

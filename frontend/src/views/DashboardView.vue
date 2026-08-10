<template>
  <!-- 导航栏 -->
  <Navbar />

  <!-- 主内容区 -->
  <main class="container">
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
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const router = useRouter()

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
</script>

<style>
@import '../assets/css/dashboard.css';
</style>

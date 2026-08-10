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

  <div id="login-form-popup" class="popup show">
    <form id="login-form" class="auth-form" @submit.prevent="handleLogin">
      <h2>登录</h2>
      <label for="username">用户名：</label>
      <input type="text" id="username" v-model="username" required autocomplete="username">
      <label for="password">密码：</label>
      <input type="password" id="password" v-model="password" required autocomplete="current-password">
      <input type="submit" value="登录" :disabled="userStore.loading">
      <button type="button" @click="$router.push('/')">关闭</button>
      <p>还没有账号？<router-link to="/register">立即注册</router-link></p>
      <p><router-link to="/reset" id="forgot-password-link">忘记密码？</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')

async function handleLogin() {
  const result = await userStore.login(username.value, password.value)
  if (result.success) {
    router.push(result.redirect || '/dashboard')
  } else {
    alert(result.message)
  }
}
</script>

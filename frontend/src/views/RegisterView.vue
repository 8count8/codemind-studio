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

  <div id="register-form-popup" class="popup show">
    <form id="register-form" class="auth-form" @submit.prevent="handleRegister">
      <h2>注册</h2>
      <label for="new-username">用户名：</label>
      <input type="text" id="new-username" v-model="username" required autocomplete="username">
      <label for="new-password">密码：</label>
      <input type="password" id="new-password" v-model="password" required autocomplete="new-password">
      <label for="confirm-password">确认密码：</label>
      <input type="password" id="confirm-password" v-model="confirmPassword" required autocomplete="new-password">
      <label for="new-email">邮箱：</label>
      <input type="email" id="new-email" v-model="email" required autocomplete="new-email">
      <label for="verification-code">验证码：</label>
      <div class="verification-code-container">
        <input type="text" id="verification-code" v-model="verificationCode" required autocomplete="off">
        <button type="button" id="get-verification-code-btn" @click="handleSendCode" :disabled="codeCooldown > 0">
          {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
        </button>
      </div>
      <input type="submit" value="注册" :disabled="userStore.loading">
      <button type="button" @click="$router.push('/')">关闭</button>
      <p>已有账号？<router-link to="/login">立即登录</router-link></p>
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
const confirmPassword = ref('')
const email = ref('')
const verificationCode = ref('')
const codeCooldown = ref(0)
let cooldownTimer = null

async function handleSendCode() {
  if (!email.value) {
    alert('请输入邮箱地址')
    return
  }
  const result = await userStore.sendVerificationCode(email.value)
  if (result.status === 'success') {
    alert('验证码已发送')
    startCooldown(60)
  } else {
    alert(result.message || '发送验证码失败')
  }
}

function startCooldown(seconds) {
  codeCooldown.value = seconds
  cooldownTimer = setInterval(() => {
    codeCooldown.value--
    if (codeCooldown.value <= 0) {
      clearInterval(cooldownTimer)
    }
  }, 1000)
}

async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }
  const result = await userStore.register(
    username.value,
    password.value,
    email.value,
    verificationCode.value
  )
  if (result.success) {
    alert('注册成功，请登录')
    router.push('/login')
  } else {
    alert(result.message)
  }
}
</script>

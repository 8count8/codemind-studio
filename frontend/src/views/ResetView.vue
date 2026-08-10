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

  <div id="reset-password-form-container" class="popup show">
    <form id="reset-password-form" class="auth-form" @submit.prevent="handleReset">
      <h2>找回密码</h2>
      <label for="email">邮箱：</label>
      <input type="email" id="email" v-model="email" required autocomplete="email">
      <label for="new-password">新密码：</label>
      <input type="password" id="new-password" v-model="newPassword" required autocomplete="new-password">
      <label for="verification-code">验证码：</label>
      <div class="verification-code-container">
        <input type="text" id="verification-code" v-model="verificationCode" required autocomplete="off">
        <button type="button" id="get-verification-code-btn" @click="handleSendCode" :disabled="codeCooldown > 0">
          {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
        </button>
      </div>
      <input type="submit" value="重置密码" :disabled="userStore.loading">
      <button type="button" @click="$router.push('/login')">返回登录</button>
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

const email = ref('')
const newPassword = ref('')
const verificationCode = ref('')
const codeCooldown = ref(0)
let cooldownTimer = null

async function handleSendCode() {
  if (!email.value) {
    alert('请输入邮箱地址')
    return
  }
  const result = await userStore.sendForgotPasswordCode(email.value)
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

async function handleReset() {
  const result = await userStore.resetPassword(
    email.value,
    newPassword.value,
    verificationCode.value
  )
  if (result.success) {
    alert('密码重置成功，请登录')
    router.push('/login')
  } else {
    alert(result.message)
  }
}
</script>

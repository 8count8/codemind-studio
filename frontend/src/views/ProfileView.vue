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
      <img :src="avatar" alt="用户头像" class="user-avatar" @click="changeAvatar">
      <input type="file" ref="avatarInput" class="hidden-input" accept="image/*" @change="onAvatarChange">
      <h2 @click="editNickname">{{ nickname }}</h2>
      <p @click="editEmail">邮箱: {{ email }}</p>
    </div>
    <div class="profile-actions">
      <button class="btn btn-primary" @click="$router.push('/ability-matrix')">能力矩阵</button>
      <button class="btn btn-primary" @click="$router.push('/history')">历史记录</button>
      <button class="btn btn-primary" @click="$router.push('/favorites')">收藏记录</button>
      <button class="btn btn-primary" @click="handleLogout">退出登录</button>
      <button class="btn btn-primary" @click="$router.push('/dashboard')">退出页面</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()
const userStore = useUserStore()
const avatarInput = ref(null)

const avatar = ref('/img/user_icon.png')
const nickname = ref('用户')
const email = ref('')

onMounted(() => {
  const savedAvatar = localStorage.getItem('userAvatar')
  const savedNickname = localStorage.getItem('userNickname')
  const savedEmail = localStorage.getItem('userEmail')
  if (savedAvatar) avatar.value = savedAvatar
  if (savedNickname) nickname.value = savedNickname
  if (savedEmail) email.value = savedEmail
  else if (userStore.user) {
    nickname.value = userStore.user.username || '用户'
    email.value = userStore.user.email || ''
  }
})

function changeAvatar() { avatarInput.value?.click() }

function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    const prev = avatar.value
    avatar.value = ev.target.result
    if (confirm('是否保存新的头像？')) {
      localStorage.setItem('userAvatar', ev.target.result)
    } else {
      avatar.value = prev
    }
  }
  reader.readAsDataURL(file)
}

function editNickname() {
  const newNick = prompt('请输入新的昵称')
  if (newNick) {
    if (confirm('是否保存新的昵称？')) {
      nickname.value = newNick
      localStorage.setItem('userNickname', newNick)
    }
  }
}

function editEmail() {
  const newEmail = prompt('请输入新的邮箱地址', email.value)
  if (newEmail) {
    if (confirm('是否保存新的邮箱地址？')) {
      email.value = newEmail
      localStorage.setItem('userEmail', newEmail)
    }
  }
}

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

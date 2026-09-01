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
      <p class="profile-time">注册于 {{ formatTime(createdAt) }} · 最近登录 {{ formatTime(lastLogin) }}</p>
    </div>
    <div class="profile-stats">
      <div><strong>{{ stats.answers }}</strong><span>答题记录</span></div>
      <div><strong>{{ stats.submissions }}</strong><span>代码提交</span></div>
      <div><strong>{{ stats.favorites }}</strong><span>收藏题目</span></div>
      <div><strong>{{ stats.evaluations }}</strong><span>能力评估</span></div>
    </div>
    <button class="ability-preview" @click="$router.push('/ability-matrix')">
      <span v-for="dim in dimensions" :key="dim.key">
        <small>{{ dim.label }}</small><i><b :style="{ width: `${ability[dim.key] || 0}%` }"></b></i><strong>{{ Math.round(ability[dim.key] || 0) }}</strong>
      </span>
      <em>查看完整能力矩阵 →</em>
    </button>
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
import http from '../utils/http'
import { ABILITY_DIMENSIONS } from '../utils/constants'

const router = useRouter()
const userStore = useUserStore()
const avatarInput = ref(null)

const avatar = ref('/img/user_icon.png')
const nickname = ref('用户')
const email = ref('')
const createdAt = ref(null)
const lastLogin = ref(null)
const stats = ref({ answers: 0, submissions: 0, favorites: 0, evaluations: 0 })
const ability = ref({})
const dimensions = ABILITY_DIMENSIONS

onMounted(async () => {
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
  try {
    const res = await http.get('/api/profile')
    const data = res.data?.data
    if (data) {
      nickname.value = data.username
      email.value = data.email
      createdAt.value = data.created_at
      lastLogin.value = data.last_login
      stats.value = { ...stats.value, ...(data.stats || {}) }
      userStore.user = { ...(userStore.user || {}), id: data.id, username: data.username, email: data.email }
    }
  } catch (e) {
    console.error('加载个人资料失败:', e)
  }
  try {
    const res = await http.get('/api/ability-matrix')
    ability.value = res.data?.data?.matrix || {}
  } catch (e) { console.error('加载能力缩略图失败:', e) }
})

function formatTime(value) {
  if (!value) return '暂无'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function saveProfile(nextNickname, nextEmail) {
  const res = await http.put('/api/profile', { username: nextNickname, email: nextEmail })
  const data = res.data?.data
  nickname.value = data?.username || nextNickname
  email.value = data?.email || nextEmail
  localStorage.removeItem('userNickname')
  localStorage.removeItem('userEmail')
}

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

async function editNickname() {
  const newNick = prompt('请输入新的昵称')
  if (newNick) {
    if (confirm('是否保存新的昵称？')) {
      try { await saveProfile(newNick, email.value) }
      catch (e) { alert(e.response?.data?.message || '保存失败') }
    }
  }
}

async function editEmail() {
  const newEmail = prompt('请输入新的邮箱地址', email.value)
  if (newEmail) {
    if (confirm('是否保存新的邮箱地址？')) {
      try { await saveProfile(nickname.value, newEmail) }
      catch (e) { alert(e.response?.data?.message || '保存失败') }
    }
  }
}

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-time { color: var(--text-secondary, #667085); font-size: .88rem; }
.profile-stats { display: grid; grid-template-columns: repeat(4, minmax(110px, 1fr)); gap: 12px; margin: 20px 0; }
.profile-stats div { padding: 16px; border-radius: 12px; background: var(--card-bg, #fff); text-align: center; box-shadow: 0 4px 18px rgba(0,0,0,.08); }
.profile-stats strong, .profile-stats span { display: block; }
.profile-stats strong { font-size: 1.65rem; color: var(--primary-color, #4f46e5); }
.profile-stats span { margin-top: 5px; color: var(--text-secondary, #667085); }
.ability-preview { width:100%; display:grid; gap:9px; margin:0 0 20px; padding:16px; border:0; border-radius:12px; background:var(--card-bg,#fff); color:var(--text-color,#1f2937); box-shadow:0 4px 18px rgba(0,0,0,.08); cursor:pointer; text-align:left; }
.ability-preview>span { display:grid; grid-template-columns:72px 1fr 34px; gap:8px; align-items:center; }.ability-preview i{height:8px;border-radius:99px;background:#e2e8f0;overflow:hidden}.ability-preview b{display:block;height:100%;background:var(--primary-color,#4f46e5)}.ability-preview em{text-align:right;color:var(--primary-color,#4f46e5);font-style:normal;font-size:.85rem}
@media (max-width: 700px) { .profile-stats { grid-template-columns: repeat(2, 1fr); } }
</style>

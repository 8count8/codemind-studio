<template>
  <div class="user-menu" id="user-menu">
    <!-- 已登录：显示用户头像 -->
    <div v-if="userStore.isLoggedIn" class="user-avatar-container" id="user-avatar-container">
      <img
        src="/img/user_icon.png"
        alt="用户头像"
        class="user-avatar"
        id="user-avatar"
        @click.stop="toggleDropdown"
      >
      <span class="username" v-if="userStore.user">{{ userStore.user.username }}</span>
    </div>
    <!-- 未登录：显示登录按钮 -->
    <button v-else class="btn btn-login" id="login-btn" @click="goLogin">登录</button>

    <!-- 用户下拉菜单 -->
    <div class="user-dropdown" :class="{ active: dropdownVisible }" id="user-dropdown">
      <div>
        <div>
          <router-link to="/profile" class="dropdown-link" @click="dropdownVisible = false">
            个人中心
          </router-link>
        </div>
        <div>
          <button class="btn btn-info btn-logout" id="logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const router = useRouter()
const dropdownVisible = ref(false)

function toggleDropdown() {
  dropdownVisible.value = !dropdownVisible.value
}

function goLogin() {
  router.push('/login')
}

async function handleLogout() {
  await userStore.logout()
  dropdownVisible.value = false
  router.push('/login')
}

// 点击外部关闭下拉菜单
function handleClickOutside(e) {
  const isInside = e.target.closest('#user-avatar') || e.target.closest('.user-dropdown')
  if (!isInside) {
    dropdownVisible.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

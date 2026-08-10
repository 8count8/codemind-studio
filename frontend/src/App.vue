<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})
</script>

<style>
/* 全局工具类 —— 替代原模板中的内联 style */
.flex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-avatar-container {
  display: flex !important;
  align-items: center;
}

.dropdown-link {
  text-decoration: none;
  color: var(--shadow);
}

.hidden-input {
  display: none;
}
</style>

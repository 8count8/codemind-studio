<template>
  <button class="btn btn-theme" id="theme-toggle" @click="themeStore.toggleTheme()">
    <span id="theme-icon">{{ themeStore.getThemeIcon() }}</span>
    <span id="theme-text">{{ themeStore.getThemeText() }}</span>
  </button>
</template>

<script setup>
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

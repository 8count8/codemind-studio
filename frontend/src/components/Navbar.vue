<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="logo">
        <img src="/img/logo.jpg" alt="Logo">
        <span>CodeMind Studio</span>
      </router-link>
      <div class="nav-controls">
        <ThemeToggle />
        <UserMenu v-if="showUserMenu" />
      </div>
    </div>
  </nav>
</template>

<script setup>
import ThemeToggle from './ThemeToggle.vue'
import UserMenu from './UserMenu.vue'

defineProps({
  showUserMenu: {
    type: Boolean,
    default: true
  }
})
</script>

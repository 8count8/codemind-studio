import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light')

  /**
   * 初始化主题（从 localStorage 读取）
   */
  function initTheme() {
    const saved = localStorage.getItem('theme') || 'light'
    setTheme(saved)
  }

  /**
   * 设置主题
   */
  function setTheme(newTheme) {
    theme.value = newTheme
    document.body.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  /**
   * 切换主题
   */
  function toggleTheme() {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  /**
   * 获取主题图标
   */
  function getThemeIcon() {
    return theme.value === 'dark' ? '🌙' : '🌞'
  }

  function getThemeText() {
    return theme.value === 'dark' ? '暗色' : '亮色'
  }

  return {
    theme,
    initTheme,
    setTheme,
    toggleTheme,
    getThemeIcon,
    getThemeText
  }
})

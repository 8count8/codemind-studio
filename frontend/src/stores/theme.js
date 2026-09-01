import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light')
  const customColors = ref({ primary: '#6366f1', secondary: '#10b981', accent: '#f43f5e' })

  /**
   * 初始化主题（从 localStorage 读取）
   */
  function initTheme() {
    const saved = localStorage.getItem('theme') || 'light'
    try {
      customColors.value = { ...customColors.value, ...JSON.parse(localStorage.getItem('customThemeColors') || '{}') }
    } catch { /* ignore invalid legacy value */ }
    setTheme(saved)
  }

  /**
   * 设置主题
   */
  function setTheme(newTheme) {
    theme.value = newTheme
    document.body.setAttribute('data-theme', newTheme)
    const root = document.documentElement.style
    if (newTheme === 'custom') {
      root.setProperty('--primary-color', customColors.value.primary)
      root.setProperty('--secondary-color', customColors.value.secondary)
      root.setProperty('--accent-color', customColors.value.accent)
    } else {
      root.removeProperty('--primary-color')
      root.removeProperty('--secondary-color')
      root.removeProperty('--accent-color')
    }
    localStorage.setItem('theme', newTheme)
  }

  function setCustomTheme(colors) {
    customColors.value = { ...customColors.value, ...colors }
    localStorage.setItem('customThemeColors', JSON.stringify(customColors.value))
    setTheme('custom')
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
    return theme.value === 'dark' ? '🌙' : (theme.value === 'custom' ? '🎨' : '🌞')
  }

  function getThemeText() {
    return theme.value === 'dark' ? '暗色' : (theme.value === 'custom' ? '自定义' : '亮色')
  }

  return {
    theme,
    initTheme,
    setTheme,
    setCustomTheme,
    customColors,
    toggleTheme,
    getThemeIcon,
    getThemeText
  }
})

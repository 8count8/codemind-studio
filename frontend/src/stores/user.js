import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '../utils/http'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(false)

  /**
   * 检查登录状态
   */
  async function checkAuth() {
    try {
      const res = await http.get('/auth/status')
      const data = res.data
      isLoggedIn.value = data.isAuthenticated
      user.value = data.isAuthenticated ? data.user : null
      return data.isAuthenticated
    } catch (e) {
      console.error('检查登录状态失败:', e)
      isLoggedIn.value = false
      user.value = null
      return false
    }
  }

  /**
   * 登录
   */
  async function login(username, password) {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const res = await http.post('/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data = res.data
      if (data.status === 200) {
        isLoggedIn.value = true
        user.value = { username, is_admin: username.trim().toLowerCase() === 'admin' }
        return { success: true, redirect: data.redirect }
      } else {
        return { success: false, message: data.message }
      }
    } catch (e) {
      const msg = e.response?.data?.message || '登录失败，请重试'
      return { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  /**
   * 退出登录
   */
  async function logout() {
    try {
      await http.post('/logout')
    } catch (e) {
      console.error('退出登录请求失败:', e)
    } finally {
      isLoggedIn.value = false
      user.value = null
    }
  }

  /**
   * 注册
   */
  async function register(username, password, email, verificationCode) {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('new-username', username)
      formData.append('new-password', password)
      formData.append('new-email', email)
      formData.append('verification-code', verificationCode)

      const res = await http.post('/register', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data = res.data
      if (data.status === 200) {
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (e) {
      const msg = e.response?.data?.message || '注册失败，请重试'
      return { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  /**
   * 发送验证码
   */
  async function sendVerificationCode(email) {
    try {
      const formData = new FormData()
      formData.append('email', email)

      const res = await http.post('/get_verification_code', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return res.data
    } catch (e) {
      return { status: 'error', message: '发送验证码失败' }
    }
  }

  /**
   * 发送忘记密码验证码
   */
  async function sendForgotPasswordCode(email) {
    try {
      const formData = new FormData()
      formData.append('email', email)

      const res = await http.post('/get_forgot_password_code', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return res.data
    } catch (e) {
      return { status: 'error', message: '发送验证码失败' }
    }
  }

  /**
   * 重置密码
   */
  async function resetPassword(email, newPassword, verificationCode) {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('email', email)
      formData.append('new_password', newPassword)
      formData.append('verification_code', verificationCode)

      const res = await http.post('/reset_password', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data = res.data
      if (data.status === 200) {
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (e) {
      const msg = e.response?.data?.message || '重置密码失败'
      return { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    isLoggedIn,
    loading,
    checkAuth,
    login,
    logout,
    register,
    sendVerificationCode,
    sendForgotPasswordCode,
    resetPassword
  }
})

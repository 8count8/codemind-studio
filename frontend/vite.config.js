import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // Flask 认证端点
      '/login': { target: 'http://localhost:5000', changeOrigin: true },
      '/logout': { target: 'http://localhost:5000', changeOrigin: true },
      '/register': { target: 'http://localhost:5000', changeOrigin: true },
      '/reset': { target: 'http://localhost:5000', changeOrigin: true },
      '/reset_password': { target: 'http://localhost:5000', changeOrigin: true },
      '/get_verification_code': { target: 'http://localhost:5000', changeOrigin: true },
      '/get_forgot_password_code': { target: 'http://localhost:5000', changeOrigin: true },
      '/auth': { target: 'http://localhost:5000', changeOrigin: true },
      // CSRF token 端点
      '/api/csrf-token': { target: 'http://localhost:5000', changeOrigin: true },
      // Flask API 端点
      '/api': { target: 'http://localhost:5000', changeOrigin: true },
      // 代码审查表单提交（非 /api 前缀）
      '/process_code': { target: 'http://localhost:5000', changeOrigin: true },
      // Flask 静态资源（图片等）
      '/static': { target: 'http://localhost:5000', changeOrigin: true }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})

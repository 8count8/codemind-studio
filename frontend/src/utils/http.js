import axios from 'axios'

let csrfToken = null

/**
 * 从后端获取 CSRF token
 */
async function fetchCsrfToken() {
  try {
    const res = await axios.get('/api/csrf-token', { withCredentials: true })
    csrfToken = res.data.csrf_token
  } catch (e) {
    console.error('获取 CSRF token 失败:', e)
  }
}

// 创建 Axios 实例
const http = axios.create({
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动附加 CSRF token
http.interceptors.request.use(async (config) => {
  // 对非 GET 请求附加 CSRF token
  if (config.method && config.method !== 'get') {
    if (!csrfToken) {
      await fetchCsrfToken()
    }
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 403) {
        // CSRF 验证失败或权限不足，刷新 token
        csrfToken = null
      }
    }
    return Promise.reject(error)
  }
)

export default http

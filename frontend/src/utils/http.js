import axios from 'axios'

let csrfToken = null

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

async function fetchCsrfToken() {
  try {
    const res = await axios.get(`${API_BASE}/api/csrf-token`, { withCredentials: true })
    csrfToken = res.data.csrf_token
  } catch (e) {
    console.error('获取 CSRF token 失败:', e)
  }
}

const http = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use(async (config) => {
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

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 403) {
        csrfToken = null
      }
    }
    return Promise.reject(error)
  }
)

export default http

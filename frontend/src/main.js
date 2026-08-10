import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { marked } from 'marked'
import App from './App.vue'
import router from './router'

// 全局 CSS（home.css 包含全局变量和基础样式）
import './assets/css/home.css'
import './assets/css/dashboard.css'

// 配置 marked 库（与原项目保持一致）
marked.setOptions({
  breaks: true,
  gfm: true,
  tables: true
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')

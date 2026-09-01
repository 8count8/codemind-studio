<template>
  <div class="settings-wrapper">
    <!-- 导航栏 -->
    <nav class="navbar">
      <router-link to="/dashboard" class="logo">
        <img src="/img/logo.jpg" alt="Logo" id="logo-img" />
        <span>CodeMind Studio — ⚙️ 设置</span>
      </router-link>
      <div class="nav-buttons">
        <ThemeToggle />
      </div>
    </nav>

    <div class="container settings-body">
      <header class="page-header">
        <h2>⚙️ 系统设置 — 本地大模型 (Ollama)</h2>
        <p class="muted">
          CodeMind Studio 的 AI 能力完全由本地 Ollama 提供，无需 API Token，模型下载完毕后可完全离线使用。
          详细安装教程见：<router-link to="/docs/ollama" @click.prevent="openGuide">《Ollama 安装与加速指南》</router-link>
        </p>
      </header>

      <section class="card">
        <div class="card-header"><h3>界面主题</h3></div>
        <div class="theme-colors">
          <label>主色 <input v-model="themeColors.primary" type="color" /></label>
          <label>辅助色 <input v-model="themeColors.secondary" type="color" /></label>
          <label>强调色 <input v-model="themeColors.accent" type="color" /></label>
          <button class="mini-btn" @click="applyCustomTheme">应用自定义主题</button>
          <button class="mini-btn" @click="themeStore.setTheme('light')">恢复亮色</button>
        </div>
      </section>

      <!-- 1. Ollama 运行状态卡片 -->
      <section class="card">
        <div class="card-header">
          <h3>1. Ollama 连接状态</h3>
          <button class="mini-btn" @click="loadStatus" :disabled="loadingStatus">
            {{ loadingStatus ? '刷新中…' : '🔄 立即刷新' }}
          </button>
        </div>

        <div class="status-row">
          <div class="status-chip" :class="status?.reachable ? 'chip-ok' : 'chip-err'">
            <i class="status-dot"></i>
            {{ status?.reachable ? '✅ 服务已连接' : '❌ 服务未连接' }}
          </div>
          <div class="kv"><label>管理地址</label><code>{{ status?.manage_url || '—' }}</code></div>
          <div class="kv"><label>API 地址 (/v1)</label><code>{{ status?.base_url || '—' }}</code></div>
          <div class="kv"><label>Ollama 版本</label><code>{{ status?.version || '未知' }}</code></div>
          <div class="kv"><label>默认模型</label><code>{{ status?.default_model || 'qwen2.5:7b' }}</code></div>
        </div>

        <div v-if="!status?.reachable" class="hint-box">
          <strong>💡 未检测到 Ollama，请按以下步骤启动：</strong>
          <ol>
            <li>下载安装 Ollama：<a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a>（Windows 点 OllamaSetup.exe，下一步到底）</li>
            <li>启动 Ollama 后台服务（安装完会自动运行，托盘可见图标）</li>
            <li>打开 PowerShell 运行：<code>ollama pull qwen2.5:7b</code> 拉取默认模型（约 4.7 GB）</li>
            <li>Docker 用户可直接执行：<code>docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama:latest</code></li>
          </ol>
        </div>
      </section>

      <!-- 2. 已安装模型 -->
      <section class="card">
        <div class="card-header">
          <h3>2. 已安装的模型</h3>
        </div>
        <div v-if="!status?.models || status.models.length === 0" class="empty-box">
          暂无已安装模型，请到下方选择一个模型下载（推荐 <code>qwen2.5:7b</code>，约 4.7 GB）。
        </div>
        <table v-else class="model-table">
          <thead>
            <tr><th>模型名</th><th>ID / digest</th><th>大小 (MB)</th><th>修改时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="m in status.models" :key="m.digest || m.name">
              <td><code>{{ m.name }}</code></td>
              <td class="mono small">{{ (m.digest || '').slice(0, 20) }}…</td>
              <td>{{ m.size ? (m.size / 1024 / 1024).toFixed(1) : '—' }}</td>
              <td class="small">{{ formatDate(m.modified_at) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 3. 推荐模型 & 一键拉取 -->
      <section class="card">
        <div class="card-header">
          <h3>3. 拉取 AI 模型</h3>
        </div>

        <div class="pull-row">
          <div class="pull-left">
            <label>要拉取的模型 tag：</label>
            <select v-model="selectedModel" class="sel">
              <option v-for="m in recommendedModels" :key="m.tag" :value="m.tag">
                {{ m.tag }}  ·  {{ m.size_gb }}GB  ·  {{ m.desc }}
              </option>
            </select>
            <input v-model="customModel" v-show="showCustom" class="sel" placeholder="或手动输入自定义模型，例如 qwen2.5:3b" />
            <label class="inline-checkbox">
              <input type="checkbox" v-model="showCustom" /> 手动输入自定义模型
            </label>
          </div>
          <div class="pull-right">
            <button
              class="primary-btn"
              :disabled="pullingNow || !status?.reachable"
              @click="startPull"
            >
              {{ pullingNow ? '拉取中…' : '⬇️ 开始下载模型' }}
            </button>
            <p v-if="!status?.reachable" class="tiny-err">⚠️ Ollama 未连接，无法开始下载</p>
          </div>
        </div>

        <!-- 拉取进度日志 -->
        <div v-if="pulling.state || pullLog.length" class="log-box">
          <div class="log-header">
            <strong>📜 下载 / 拉取日志</strong>
            <span class="muted small">{{ pulling.state ? '（后台运行中…）' : (pulling.success === true ? '✅ 完成' : (pulling.success === false ? '❌ 失败，请查看日志' : '')) }}</span>
          </div>
          <pre ref="logPreRef" class="log-content">{{ pullLogText || '（暂无日志）' }}</pre>
        </div>
      </section>

      <!-- 4. 运行环境 & 沙箱 -->
      <section class="card">
        <div class="card-header">
          <h3>4. 代码运行环境（答题板 / 代码审查用）</h3>
        </div>
        <p class="muted">
          代码执行支持 <strong>Docker 沙箱</strong>（优先，隔离最安全）与 <strong>本机解释器/编译器</strong>（无 Docker 时自动兜底）。
          你无需在此页配置任何东西，运行代码时系统会自动检测：
        </p>
        <ul class="muted env-list">
          <li>🐍 Python — 需要本机 <code>python3</code> 或 Docker</li>
          <li>📜 JavaScript / Node — 需要本机 <code>node</code> 或 Docker</li>
          <li>☕ Java — 需要本机 <code>javac</code> + <code>java</code> 或 Docker</li>
          <li>⚡ C / C++ — 需要本机 <code>gcc</code> / <code>g++</code>（MinGW） 或 Docker</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
const themeColors = ref({ ...themeStore.customColors })

function applyCustomTheme() {
  themeStore.setCustomTheme(themeColors.value)
}

const loadingStatus = ref(false)
const status = ref(null)
const recommendedModels = ref([])

const selectedModel = ref('qwen2.5:7b')
const customModel = ref('')
const showCustom = ref(false)
const pullingNow = ref(false)
const pulling = ref({ state: false, started: null, finished: null, success: null, model: null })
const pullLog = ref([])
const logPreRef = ref(null)
let pollTimer = null

const finalModel = computed(() => (showCustom.value && customModel.value.trim()) ? customModel.value.trim() : selectedModel.value)
const pullLogText = computed(() => pullLog.value.join('\n'))

function formatDate(s) {
  if (!s) return '—'
  try { return new Date(s).toLocaleString() } catch { return String(s) }
}

async function loadStatus() {
  loadingStatus.value = true
  try {
    const res = await http.get('/api/ollama/status')
    const p = res.data?.data || {}
    status.value = p
    if (Array.isArray(p.downloads?.recommended_models) && p.downloads.recommended_models.length) {
      recommendedModels.value = p.downloads.recommended_models
    }
    // 如果正在拉，立刻同步一次日志并开启轮询
    if (p.pulling?.running && !pollTimer) {
      pulling.value = {
        state: true,
        started: p.pulling.started_at,
        finished: null,
        success: null,
        model: p.pulling.model,
      }
      pullLog.value = p.pulling.log_tail || []
      startLogPolling()
    }
  } catch (e) {
    console.error('加载 Ollama 状态失败', e)
  } finally {
    loadingStatus.value = false
  }
}

async function startPull() {
  pullingNow.value = true
  pullLog.value = ['> 正在向后端提交拉取任务...']
  try {
    const res = await http.post('/api/ollama/pull', { model: finalModel.value })
    if (res.data?.status !== 200 && res.data?.status !== 409) {
      pullLog.value.push('❌ ' + (res.data?.message || '请求失败'))
      return
    }
    pulling.value = {
      state: true,
      started: new Date().toLocaleString(),
      finished: null,
      success: null,
      model: finalModel.value,
    }
    startLogPolling()
  } catch (e) {
    pullLog.value.push('❌ 请求失败: ' + (e.response?.data?.message || e.message))
  } finally {
    pullingNow.value = false
  }
}

function startLogPolling() {
  if (pollTimer) return
  pollTimer = setInterval(async () => {
    try {
      const res = await http.get('/api/ollama/pull_log?tail=200')
      const d = res.data?.data || {}
      pullLog.value = d.log || []
      pulling.value = {
        state: !!d.running,
        started: d.started_at || pulling.value.started,
        finished: d.finished_at,
        success: d.success,
        model: d.model || pulling.value.model,
      }
      await nextTick()
      if (logPreRef.value) {
        logPreRef.value.scrollTop = logPreRef.value.scrollHeight
      }
      if (!d.running) {
        clearInterval(pollTimer); pollTimer = null
        // 拉取完成后顺带刷新模型列表
        await loadStatus()
      }
    } catch (e) {
      console.warn('拉模型日志轮询失败', e)
    }
  }, 1500)
}

function openGuide() {
  window.open('/docs/Ollama安装与加速指南.md', '_blank', 'noopener')
}

onMounted(() => { loadStatus() })
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.settings-wrapper { min-height: 100vh; background: var(--bg, #f7f8fb); color: var(--text, #0f172a); }
.navbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 22px;
  background: #fff; border-bottom: 1px solid var(--border, #e5e7eb); position: sticky; top: 0; z-index: 10; }
.logo { display: flex; align-items: center; gap: 10px; text-decoration: none; color: inherit; font-weight: 700; }
.logo img { width: 32px; height: 32px; border-radius: 6px; object-fit: cover; }
.nav-buttons { display: flex; align-items: center; gap: 10px; }
.theme-colors { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; }
.theme-colors label { display: inline-flex; align-items: center; gap: 8px; }
.theme-colors input[type="color"] { width: 42px; height: 32px; border: 0; background: transparent; cursor: pointer; }

.settings-body { max-width: 1040px; margin: 0 auto; padding: 24px 20px 80px 20px; }
.page-header h2 { margin: 0 0 8px 0; }
.page-header .muted { color: #64748b; font-size: 14px; line-height: 1.7; }
.page-header a { color: #2563eb; }

.card { background: #fff; border: 1px solid var(--border, #e5e7eb); border-radius: 10px;
  padding: 18px 20px; margin-top: 20px; box-shadow: 0 1px 2px rgba(15,23,42,.03); }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 16px; }
.mini-btn { padding: 6px 12px; border-radius: 6px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer; }
.mini-btn:hover:not(:disabled) { background: #f1f5f9; }
.mini-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.status-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 20px; }
.status-chip { grid-column: 1 / -1; display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px; border-radius: 999px; font-weight: 600; width: fit-content; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.chip-ok { background: #dcfce7; color: #166534; } .chip-ok .status-dot { background: #22c55e; }
.chip-err{ background: #fee2e2; color: #991b1b; } .chip-err .status-dot{ background: #ef4444; }
.kv { display: flex; align-items: center; gap: 10px; font-size: 14px; min-width: 0; }
.kv label { color: #64748b; width: 110px; flex: 0 0 auto; }
.kv code { background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-size: 12.5px;
  word-break: break-all; }

.hint-box { margin-top: 14px; padding: 12px 16px; background: #fff7ed; border: 1px solid #fdba74;
  border-radius: 8px; font-size: 13.5px; line-height: 1.8; color: #7c2d12; }
.hint-box ol { padding-left: 20px; margin: 8px 0 0 0; }
.hint-box code { background: #fff; padding: 1px 6px; border-radius: 4px; font-size: 12.5px; }

.empty-box { padding: 24px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px;
  color: #475569; font-size: 14px; }
.empty-box code { background: #fff; padding: 1px 6px; border-radius: 4px; }

.model-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.model-table th, .model-table td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.model-table th { background: #f8fafc; color: #475569; font-weight: 600; }
.model-table .mono { font-family: 'JetBrains Mono', Consolas, monospace; }
.model-table .small { color: #64748b; font-size: 12.5px; }

.pull-row { display: grid; grid-template-columns: 1.3fr 1fr; gap: 20px; align-items: start; }
@media (max-width: 760px) { .pull-row { grid-template-columns: 1fr; } }
.pull-left label { display: block; margin: 6px 0 4px 0; font-size: 13.5px; color: #334155; }
.sel { width: 100%; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px;
  font-size: 14px; background: #fff; box-sizing: border-box; }
.inline-checkbox { display: inline-flex; align-items: center; gap: 6px; margin-top: 8px;
  font-size: 13px; color: #475569; cursor: pointer; }
.pull-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.primary-btn { padding: 10px 18px; font-size: 14px; font-weight: 600; color: #fff;
  background: #2563eb; border: none; border-radius: 6px; cursor: pointer; }
.primary-btn:hover:not(:disabled) { background: #1d4ed8; }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.tiny-err { margin: 0; font-size: 12.5px; color: #b91c1c; }

.log-box { margin-top: 14px; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; }
.log-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  background: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-size: 13.5px; }
.muted { color: #64748b; }
.small { font-size: 12px; }
.log-content { margin: 0; padding: 10px 12px; background: #0f172a; color: #cbd5e1;
  font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12.5px; line-height: 1.6;
  white-space: pre-wrap; word-break: break-word; max-height: 360px; overflow: auto; }

.env-list { padding-left: 20px; font-size: 14px; line-height: 1.9; }
.env-list code { background: #f1f5f9; padding: 1px 6px; border-radius: 4px; font-size: 12.5px; }
</style>

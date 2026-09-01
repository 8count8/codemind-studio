<template>
  <!-- 导航栏 -->
  <nav class="navbar">
    <a class="logo">
      <img src="/img/logo.jpg" alt="Logo" id="logo-img">
      <span>CodeMind Studio</span>
    </a>
    <div class="nav-buttons">
      <ThemeToggle />
    </div>
  </nav>

  <!-- 主内容区域 -->
  <div class="code-review-container container-fluid">
    <div class="row p-1">
      <!-- 用户代码展示区 -->
      <div v-show="showResults" class="Submit-code-display col-md-6 col-12 p-3" id="Submit-code-display">
        <div class="Card-content">
          <h4>提交的代码</h4>
          <div id="Submit-code-container">
            <pre id="Submit-code-display-text">{{ submittedCode }}</pre>
          </div>
        </div>
      </div>

      <!-- 审查结果区 -->
      <div v-show="showResults" class="Result-display col-md-6 col-12 p-3" id="Result-display">
        <div class="Card-content">
          <h4>审查结果</h4>
          <template v-if="reviewReport">
            <div class="quality-score-grid">
              <div><strong>{{ reviewReport.scores?.style || 0 }}</strong><span>代码规范</span></div>
              <div><strong>{{ reviewReport.scores?.performance || 0 }}</strong><span>性能质量</span></div>
              <div><strong>{{ reviewReport.scores?.security || 0 }}</strong><span>安全质量</span></div>
              <div class="total"><strong>{{ reviewReport.total_score || 0 }}</strong><span>综合评分</span></div>
            </div>
            <p class="review-summary">{{ reviewReport.summary }}</p>
            <div class="annotation-list">
              <p v-for="(item, index) in reviewReport.annotations" :key="index">
                <b>{{ item.type }}</b><span v-if="item.line"> 第 {{ item.line }} 行</span>：{{ item.message }}
              </p>
            </div>
            <details class="optimized-code" open>
              <summary>优化后代码</summary><pre><code>{{ reviewReport.optimized_code }}</code></pre>
            </details>
          </template>
          <div id="result-container">
            <div v-for="(r, idx) in reviewResults" :key="idx" class="result-item">
              <h4>{{ r.function }}</h4>
              <pre>{{ r.result }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 提交表单区 -->
      <div v-show="!showResults" class="Submit-code col-md-6 col-12 p-3 el-col-md-offset-3" id="Submit-code-form">
        <div class="Card-content row">
          <h2>代码审查说明</h2>
          <p>请选择要审查的代码文件，并根据需要选择功能说明文档。</p>

          <form id="main-form" @submit.prevent="handleSubmit">
            <!-- 功能选择导航栏 -->
            <ul class="nav nav-tabs" id="functionTabs" role="tablist">
              <li class="nav-item" role="presentation" v-for="tab in tabs" :key="tab.id">
                <a
                  class="nav-link"
                  :class="{ active: activeTab === tab.id }"
                  :id="tab.tabId"
                  href="#"
                  @click.prevent="activeTab = tab.id"
                  role="tab"
                >{{ tab.label }}</a>
              </li>
            </ul>

            <!-- 功能内容区域 -->
            <div class="tab-content" id="functionTabsContent">
              <!-- 代码注释校对 Tab -->
              <div v-show="activeTab === 'code-commenting'" class="tab-pane fade show active" id="code-commenting">
                <div class="form-group">
                  <label for="code-file-comment">选择代码文件：</label>
                  <input type="file" class="form-control-file" id="code-file-comment" accept=".java,.py,.js" @change="onFileChange">
                </div>
                <div class="form-group">
                  <label for="code-paste-comment">或粘贴代码：</label>
                  <textarea class="form-control" id="code-paste-comment" v-model="pasteCode" rows="10" placeholder="在此粘贴需要检查注释的代码..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary mt-3">开始审查</button>
              </div>

              <!-- 代码文档校对 Tab -->
              <div v-show="activeTab === 'code-documentation'" class="tab-pane fade" id="code-documentation">
                <div class="form-group">
                  <label for="code-file-doc">选择代码文件：</label>
                  <input type="file" class="form-control-file" id="code-file-doc" accept=".java,.py,.js" @change="onFileChange">
                </div>
                <div class="form-group">
                  <label for="doc-file-doc">选择文档文件：</label>
                  <input type="file" class="form-control-file" id="doc-file-doc" accept=".md,.pdf">
                </div>
                <button type="submit" class="btn btn-primary mt-3">文档校验</button>
              </div>

              <!-- 缺失注释预警 Tab -->
              <div v-show="activeTab === 'missing-comment'" class="tab-pane fade" id="missing-comment">
                <div class="form-group">
                  <label for="code-file-missing">选择代码文件：</label>
                  <input type="file" class="form-control-file" id="code-file-missing" accept=".java,.py,.js" @change="onFileChange">
                </div>
                <button type="submit" class="btn btn-primary mt-3">扫描缺失</button>
              </div>

              <!-- 代码规范预警 Tab -->
              <div v-show="activeTab === 'code-conformance'" class="tab-pane fade" id="code-conformance">
                <div class="form-group">
                  <label for="code-file-standard">选择代码文件：</label>
                  <input type="file" class="form-control-file" id="code-file-standard" accept=".java,.py,.js" @change="onFileChange">
                </div>
                <div class="form-group">
                  <label>规范标准：</label>
                  <select class="form-select" v-model="codeStandard" aria-label="选择规范标准">
                    <option value="google">Google代码规范</option>
                    <option value="alibaba">阿里巴巴开发规范</option>
                    <option value="iso">ISO/IEC标准</option>
                  </select>
                </div>
                <button type="submit" class="btn btn-primary mt-3">规范检查</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
    <section class="review-history-panel">
      <div class="history-heading"><h3>最近审查记录</h3><button class="btn btn-outline-primary btn-sm" @click="loadHistory">刷新</button></div>
      <p v-if="reviewHistory.length === 0" class="history-empty">暂无审查记录</p>
      <button v-for="item in reviewHistory.slice(0, 8)" :key="item.id" class="history-entry" @click="openHistory(item)">
        <span>{{ item.name }}</span><small>{{ formatTime(item.timestamp) }}</small>
      </button>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const tabs = [
  { id: 'code-commenting', label: '代码注释和功能校对', tabId: 'code-commenting-tab' },
  { id: 'code-documentation', label: '代码文档和功能校对', tabId: 'code-documentation-tab' },
  { id: 'missing-comment', label: '缺失注释和文档预警', tabId: 'missing-comment-tab' },
  { id: 'code-conformance', label: '代码规范性预警', tabId: 'code-conformance-tab' }
]

const activeTab = ref('code-commenting')
const pasteCode = ref('')
const codeStandard = ref('google')
const selectedFile = ref(null)
const showResults = ref(false)
const submittedCode = ref('')
const reviewResults = ref([])
const reviewHistory = ref([])
const reviewReport = ref(null)

function onFileChange(e) {
  selectedFile.value = e.target.files[0] || null
}

async function handleSubmit() {
  // 验证：至少选择文件或输入代码
  if (!selectedFile.value && !pasteCode.value.trim()) {
    alert('请选择文件或输入代码！')
    return
  }

  // 先渲染用户代码
  if (selectedFile.value) {
    const reader = new FileReader()
    reader.onload = (e) => { submittedCode.value = e.target.result }
    reader.readAsText(selectedFile.value)
  } else {
    submittedCode.value = pasteCode.value
  }

  showResults.value = true

  // 构建 FormData 提交
  const formData = new FormData()
  if (selectedFile.value) {
    formData.append('code-file', selectedFile.value)
  }
  if (pasteCode.value) {
    formData.append('paste_code', pasteCode.value)
  }
  formData.append('tab_type', activeTab.value)
  if (activeTab.value === 'code-conformance') {
    formData.append('code_standard', codeStandard.value)
  }

  try {
    const res = await http.post('/api/code-review/review', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const data = res.data
    if (data.status === 200) {
      reviewResults.value = data.results || []
      reviewReport.value = data.review || null
      await loadHistory()
    } else {
      alert(data.message || '提交失败，请重试')
    }
  } catch (e) {
    console.error('提交失败:', e)
    alert('提交失败: ' + (e.response?.data?.message || e.message))
  }
}

function formatTime(value) { return value ? new Date(value).toLocaleString('zh-CN') : '-' }

async function loadHistory() {
  try {
    const res = await http.get('/api/code-review/history')
    reviewHistory.value = res.data?.data || []
  } catch (e) { console.error('加载审查历史失败:', e) }
}

function openHistory(item) {
  try {
    const parsed = typeof item.content === 'string' ? JSON.parse(item.content) : item.content
    if (parsed?.review) {
      reviewReport.value = parsed.review
      reviewResults.value = parsed.legacy ? [parsed.legacy] : []
    } else {
      reviewReport.value = null
      reviewResults.value = Array.isArray(parsed) ? parsed : [parsed]
    }
  } catch {
    reviewReport.value = null
    reviewResults.value = [{ function: '历史审查结果', result: item.content || '无内容' }]
  }
  submittedCode.value = item.original_code || '该历史记录未包含原始代码。'
  showResults.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadHistory)
</script>

<style>
@import '../assets/css/code_review.css';
@import '../assets/css/bootstrap/bootstrap.css';

.review-history-panel { max-width: 980px; margin: 10px auto 30px; padding: 18px; border-radius: 12px; background: var(--card-bg, #fff); box-shadow: 0 4px 18px rgba(0,0,0,.08); }
.history-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.history-entry { width:100%; display:flex; align-items:center; justify-content:space-between; padding:10px 12px; border:0; border-bottom:1px solid #e2e8f0; background:transparent; color:var(--text-color,#1f2937); cursor:pointer; text-align:left; }
.history-entry:hover { background:rgba(37,99,235,.06); }.history-entry small,.history-empty{color:#64748b}
.quality-score-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:10px 0 14px; }.quality-score-grid div{padding:10px;border-radius:8px;background:#eff6ff;text-align:center}.quality-score-grid strong,.quality-score-grid span{display:block}.quality-score-grid strong{font-size:1.4rem;color:#1d4ed8}.quality-score-grid span{font-size:.75rem;color:#64748b}.quality-score-grid .total{background:#1d4ed8}.quality-score-grid .total strong,.quality-score-grid .total span{color:#fff}.review-summary{padding:10px;border-left:3px solid #2563eb;background:#f8fafc}.annotation-list p{margin:5px 0;font-size:.85rem}.optimized-code summary{cursor:pointer;font-weight:700;margin:12px 0}.optimized-code pre{max-height:320px;overflow:auto;background:#0f172a;color:#e2e8f0;padding:12px;border-radius:8px;white-space:pre-wrap}
</style>

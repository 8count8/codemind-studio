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

  <div class="main-container">
    <!-- 左侧题目信息区域 -->
    <div class="left-panel">
      <div class="question-header">
        <div class="flex-header">
          <h3>题目信息</h3>
          <button id="favorite-btn" class="btn-favorite" @click="handleFavorite">收藏题目</button>
        </div>
      </div>
      <div class="question-content" id="question-content">
        <h2 id="question-title">{{ question.title || '加载中...' }}</h2>
        <div id="question-description" class="markdown-body" v-html="renderedContent"></div>
        <div class="question-meta" v-if="question.title">
          <span>难度：{{ question.difficulty }}</span>
          <span>标签：{{ question.tags }}</span>
        </div>
      </div>

      <!-- 异步结果显示区域 -->
      <div class="backend-results" id="backend-results">
        <!-- 单跑结果（点"运行代码"） -->
        <div class="result-section" id="single-run-container" v-if="singleRunResult || runBusy">
          <h3>▶ 单次运行结果（{{ runBusy ? '运行中…' : '已完成' }}）</h3>
          <div class="result-content">
            <div v-if="runBusy" class="ai-processing">
              <span>代码执行中，请稍候…</span>
              <div class="ai-loading-dots"></div>
            </div>
            <div v-else-if="singleRunResult" class="result-container overall-result">
              <div class="result-header">
                <div class="result-status" :class="singleRunResult.success ? 'status-success' : 'status-failed'">
                  <span>{{ singleRunResult.success ? '运行成功' : '运行失败' }}<i class="status-icon"></i></span>
                </div>
                <div class="result-metrics">
                  <span class="metric-item metric-style">耗时: {{ Number(singleRunResult.run_time || 0).toFixed(6) }}s</span>
                  <span v-if="singleRunResult.sandbox_mode" class="metric-item metric-style">沙箱: {{ singleRunResult.sandbox_mode }}</span>
                  <span class="metric-item">内存峰值: {{ singleRunResult.memory_peak_mb ?? '未采样' }} MB / {{ singleRunResult.memory_limit_mb || 256 }} MB</span>
                </div>
              </div>
              <div class="result-output">
                <h4 class="detail-info-style">标准输出 stdout</h4>
                <pre class="output-pre">{{ singleRunResult.output || '(无输出)' }}</pre>
                <h4 v-if="singleRunResult.error" class="detail-info-style" style="margin-top:10px;color:#d9534f">错误信息 stderr</h4>
                <pre v-if="singleRunResult.error" class="output-pre error-pre">{{ singleRunResult.error }}</pre>
                <h4 v-if="singleRunResult.runtime_check && !singleRunResult.runtime_check.available" class="detail-info-style" style="margin-top:10px;color:#ec971f">运行环境提示</h4>
                <div v-if="singleRunResult.runtime_check && !singleRunResult.runtime_check.available" class="ai-feedback-content">
                  {{ singleRunResult.runtime_check.message }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="result-section" id="run-result-container">
          <h3>代码运行结果</h3>
          <div class="result-content" id="run-result">
            <!-- 运行结果概览 -->
            <div v-if="runResult" class="result-container overall-result" @click="showDetails = !showDetails">
              <div class="result-header">
                <div class="result-status" :class="runResultStatusClass">
                  <span>{{ runResultStatus }}<i class="status-icon"></i></span>
                </div>
                <div class="result-metrics">
                  <span class="metric-item metric-style">总测试用例数: {{ runResult.total_cases }}</span>
                  <span class="metric-item metric-style">通过测试用例数: {{ runResult.passed_cases }}</span>
                  <span class="metric-item metric-style">失败测试用例数: {{ runResult.failed_cases }}</span>
                  <span class="metric-item metric-style">总执行时间: {{ totalExecTime }}</span>
                </div>
              </div>
              <div class="result-output">
                <h4 class="detail-info-style">
                  详细信息<i :class="showDetails ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down'" class="expand-icon"></i>
                </h4>
              </div>
              <div class="test-cases-wrapper" v-show="showDetails">
                <div v-for="(tc, idx) in runResult.results" :key="idx" class="result-container">
                  <div class="result-header">
                    <div class="result-status" :class="tc.success ? 'status-success' : 'status-failed'">
                      <i class="status-icon"></i>
                      <span>{{ tc.success ? '成功' : '失败' }}</span>
                    </div>
                    <div class="result-metrics">
                      <span class="metric-item">执行时间: {{ tc.run_time.toFixed(6) }}</span>
                    </div>
                  </div>
                  <div class="result-output">
                    <h4>输出:</h4>
                    <pre class="output-content">{{ tc.actual_output || tc.error || '暂无输出' }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="result-section" id="ai-review-container">
          <h3>AI批改结果</h3>
          <div class="result-content" id="ai-review-result">
            <!-- AI 处理中 -->
            <div v-if="aiStatus === 'processing'" class="ai-processing">
              <span>AI批改处理中 ({{ pollingCount }}/{{ maxPollAttempts }})</span>
              <div class="ai-loading-dots"></div>
            </div>
            <!-- AI 完成 -->
            <div v-else-if="aiStatus === 'complete'" class="ai-review-container">
              <div class="ai-review-header">
                <h3 class="ai-review-title">AI代码评估</h3>
                <div class="ai-score"><span class="ai-score-value">{{ aiResult.score }}</span><span>分</span></div>
              </div>
              <div class="ai-feedback-section">
                <h4 class="ai-feedback-title">评价反馈</h4>
                <div class="ai-feedback-content">{{ aiResult.feedback }}</div>
              </div>
              <div class="ai-feedback-section">
                <h4 class="ai-feedback-title">改进建议</h4>
                <div v-if="aiResult.improvements && aiResult.improvements.length > 0">
                  <div v-for="(imp, i) in aiResult.improvements" :key="i" class="ai-improvement-item">{{ imp }}</div>
                </div>
                <div v-else class="ai-feedback-content">无具体改进建议</div>
              </div>
              <!-- 代码对比 -->
              <div v-if="aiResult.original_code && aiResult.reviewed_code" class="code-comparison-container">
                <div class="code-comparison-header">
                  <div class="code-tab" :class="{ active: codeTab === 'original' }" @click="codeTab = 'original'">原始代码</div>
                  <div class="code-tab" :class="{ active: codeTab === 'reviewed' }" @click="codeTab = 'reviewed'">带批注代码</div>
                </div>
                <div class="code-editors-container">
                  <div class="code-editor-wrapper" v-show="codeTab === 'original'">
                    <div class="code-editor-label">您提交的代码</div>
                    <pre><code>{{ aiResult.original_code }}</code></pre>
                  </div>
                  <div class="code-editor-wrapper" v-show="codeTab === 'reviewed'">
                    <div class="code-editor-label">带批注的代码</div>
                    <pre><code>{{ aiResult.reviewed_code }}</code></pre>
                  </div>
                </div>
              </div>
            </div>
            <!-- AI 错误 -->
            <div v-else-if="aiStatus === 'error'" class="ai-review-container">
              <div class="ai-error">
                <h4>AI批改失败</h4>
                <p>错误信息: {{ aiError }}</p>
                <p><button class="btn-retry" @click="submitCode">重试批改</button></p>
              </div>
            </div>
            <!-- AI 超时 -->
            <div v-else-if="aiStatus === 'timeout'" class="ai-review-container">
              <div class="ai-warning">
                <h4>AI批改超时</h4>
                <p>请稍后刷新页面查看结果</p>
                <p><button class="btn-retry" @click="submitCode">重试批改</button></p>
              </div>
            </div>
            <span v-else>还没有内容哦！</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧答题区域 -->
    <div class="right-panel">
      <div class="container">
        <section class="coding-section">
          <div class="toolbar">
            <select id="language-select" class="language-select" v-model="selectedLanguage" @change="onLanguageChange" aria-label="选择编程语言">
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="c++">C++</option>
            </select>
            <button id="save-status" class="save-btn">{{ saveStatusText }}</button>
          </div>

          <!-- 输入面板：用户运行前可填 stdin 示例输入 -->
          <div class="sample-input-wrapper">
            <div class="sample-input-header">
              <span><strong>📥 示例输入 (stdin，可选)</strong></span>
              <button class="mini-btn" @click="fillSampleFromQuestion" :disabled="!hasQuestionSample">从题目填充</button>
            </div>
            <textarea
              v-model="sampleInput"
              class="sample-input-textarea"
              rows="3"
              placeholder="这里的内容会通过 stdin 传入你的程序。只影响「▶ 运行代码」按钮；提交判分使用题库内的测试用例。"
            ></textarea>
          </div>

          <div class="editor-container">
            <div ref="editorRef" id="editor" class="code-editor"></div>
          </div>

          <div class="action-row">
            <button class="run-btn" id="run-btn" @click="runCode" :disabled="runBusy">
              {{ runBusy ? '运行中…' : '▶ 运行代码' }}
            </button>
            <button class="submit-btn" id="submit-btn" @click="submitCode" :disabled="submitBusy">
              {{ submitBusy ? '提交中…' : '✅ 提交评估（判分+AI批改）' }}
            </button>
          </div>
        </section>

        <section class="diagnosis-section">
          <div class="weakness-analysis">
            <h3>知识薄弱点分析</h3>
            <div id="weakness-list">
              <p v-if="recommendations.length === 0">提交评估后生成薄弱点诊断。</p>
              <article v-for="item in recommendations" :key="item.dimension" class="diagnosis-item">
                <strong>{{ item.label }} · {{ item.current_score }} 分</strong>
                <p>{{ item.suggestion }}</p>
              </article>
            </div>
            <button id="export-pdf" @click="exportAbilityReport">导出诊断报告</button>
          </div>
          <div class="recommendations">
            <h3>推荐练习题目</h3>
            <div id="recommended-questions">
              <template v-for="item in recommendations" :key="item.dimension">
                <button v-for="task in item.recommended_tasks" :key="task.title" class="recommended-task" @click="$router.push('/quizbank')">
                  {{ task.title }} <small>{{ task.difficulty }}</small>
                </button>
              </template>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-python'
import 'ace-builds/src-noconflict/mode-javascript'
import 'ace-builds/src-noconflict/mode-java'
import 'ace-builds/src-noconflict/mode-c_cpp'
import 'ace-builds/src-noconflict/theme-monokai'
import 'ace-builds/src-noconflict/ext-language_tools'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'
import { sanitizeHtml } from '../utils/sanitizeHtml'
import { AI_POLL_INTERVAL, AI_MAX_POLL_ATTEMPTS, AUTO_SAVE_INTERVAL } from '../utils/constants'

const route = useRoute()
const editorRef = ref(null)
let editor = null
let autoSaveTimer = null
let aiPollingTimer = null

const question = ref({})
const selectedLanguage = ref('python')
const saveStatusText = ref('已保存')
const showDetails = ref(false)
const codeTab = ref('original')

// 运行（单次）
const sampleInput = ref('')
const runBusy = ref(false)
const singleRunResult = ref(null)            // { success, output, error, run_time, sandbox_mode, runtime_check }

// 提交判分
const submitBusy = ref(false)

// 运行结果（测试用例）
const runResult = ref(null)

// AI 批改状态
const aiStatus = ref('') // '', 'processing', 'complete', 'error', 'timeout'
const aiResult = ref({})
const aiError = ref('')
const recommendations = ref([])
const pollingCount = ref(0)
const maxPollAttempts = AI_MAX_POLL_ATTEMPTS

const renderedContent = computed(() => {
  if (!question.value.content) return ''
  try {
    return sanitizeHtml(marked.parse(question.value.content))
  } catch {
    return sanitizeHtml(question.value.content)
  }
})

// 题目是否有可用的示例输入（从 description 里简单抓取）
const hasQuestionSample = computed(() => {
  const c = (question.value.content || '') + '\n' + (question.value.sample_input || '')
  return c.trim().length > 0
})

// 从题目里粗略提取「示例输入」：匹配 ```...``` 或者 Markdown 表格，优先用 sample_input 字段
function fillSampleFromQuestion() {
  if (question.value.sample_input) {
    sampleInput.value = String(question.value.sample_input)
    return
  }
  const c = question.value.content || ''
  const m = c.match(/```(?:input)?\s*\n([\s\S]*?)```/i)
  if (m) {
    sampleInput.value = m[1].replace(/\r\n/g, '\n').trimEnd() + '\n'
    return
  }
  const m2 = c.match(/输入[：:]\s*\n?([\s\S]{0,400}?)(?:\n\s*\n|输出|$)/i)
  if (m2) sampleInput.value = m2[1].trim()
}

const runResultStatus = computed(() => {
  if (!runResult.value) return ''
  return runResult.value.success ? '成功' : '失败'
})

const runResultStatusClass = computed(() => {
  if (!runResult.value) return 'status-processing'
  return runResult.value.success ? 'status-success' : 'status-failed'
})

const totalExecTime = computed(() => {
  if (!runResult.value || !runResult.value.results) return '0'
  const total = runResult.value.results.reduce((acc, tc) => acc + tc.run_time, 0)
  return total.toFixed(6)
})

function getAceMode(lang) {
  const map = { python: 'ace/mode/python', javascript: 'ace/mode/javascript', java: 'ace/mode/java', 'c++': 'ace/mode/c_cpp' }
  return map[lang] || 'ace/mode/python'
}

function initEditor() {
  if (!editorRef.value) return
  editor = ace.edit(editorRef.value)
  editor.setTheme('ace/theme/monokai')

  const savedData = JSON.parse(localStorage.getItem(draftKey()) || localStorage.getItem('currentQuestion')) || {}
  const lang = savedData.language || 'python'
  selectedLanguage.value = lang
  editor.session.setMode(getAceMode(lang))
  editor.setOptions({
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    fontSize: '14px',
    fontFamily: "'JetBrains Mono', 'Consolas', 'Courier New', monospace",
    showLineNumbers: true,
    showGutter: true,
    highlightActiveLine: true,
    showPrintMargin: false,
    scrollPastEnd: 0.5,
    highlightSelectedWord: true,
    animatedScroll: true
  })
  editor.setValue(savedData.code || '// 开始编写你的代码.....', -1)
  setupAutoSave()
}

function onLanguageChange() {
  if (editor) {
    editor.session.setMode(getAceMode(selectedLanguage.value))
  }
  saveToLocal()
}

function saveToLocal() {
  const payload = JSON.stringify({
    code: editor ? editor.getValue() : '',
    language: selectedLanguage.value
  })
  localStorage.setItem(draftKey(), payload)
  localStorage.setItem('currentQuestion', payload)
}

function draftKey() { return `codemind:draft:${route.query.questionId || question.value.id || 'current'}` }

async function saveToServer() {
  const questionId = route.query.questionId || question.value.id
  if (!questionId || !editor) return
  try {
    await http.post('/api/answerpad/auto-save', {
      question_id: questionId, language: selectedLanguage.value, code: editor.getValue(),
    })
  } catch (e) { console.error('服务端草稿保存失败:', e) }
}

async function restoreServerDraft() {
  const questionId = route.query.questionId || question.value.id
  if (!questionId || !editor || localStorage.getItem(draftKey())) return
  try {
    const res = await http.get('/api/answerpad/restore', { params: { question_id: questionId } })
    const draft = res.data?.data
    if (draft?.code) {
      selectedLanguage.value = draft.language || 'python'
      editor.session.setMode(getAceMode(selectedLanguage.value))
      editor.setValue(draft.code, -1)
      saveToLocal()
    }
  } catch (e) { console.error('服务端草稿恢复失败:', e) }
}

function setupAutoSave() {
  clearInterval(autoSaveTimer)
  autoSaveTimer = setInterval(() => {
    saveToLocal()
    saveToServer()
    saveStatusText.value = `已保存 ${new Date().toLocaleTimeString()}`
  }, AUTO_SAVE_INTERVAL)
}

async function loadQuestion() {
  const questionId = route.query.questionId
  if (!questionId) return
  try {
    const res = await http.get(`/api/questions/${questionId}`)
    if (res.data && res.data.status === 200) {
      question.value = res.data.data
    }
  } catch (e) {
    console.error('加载题目失败:', e)
  }
}

async function runCode() {
  if (!editor) return
  const code = editor.getValue()
  if (!code || !code.trim()) {
    alert('请先输入代码再运行')
    return
  }
  runBusy.value = true
  singleRunResult.value = null
  try {
    const res = await http.post('/api/answer/run', {
      code,
      language: selectedLanguage.value,
      sample_input: sampleInput.value || null,
    })
    const payload = res.data || {}
    if (payload.status !== 200) {
      singleRunResult.value = {
        success: false,
        output: null,
        error: payload.message || '运行失败',
        run_time: 0,
        sandbox_mode: null,
        runtime_check: null,
      }
    } else {
      singleRunResult.value = payload.data || {}
    }
  } catch (e) {
    singleRunResult.value = {
      success: false,
      output: null,
      error: '请求失败: ' + (e.response?.data?.message || e.message),
      run_time: 0,
      sandbox_mode: null,
      runtime_check: null,
    }
  } finally {
    runBusy.value = false
  }
}

async function submitCode() {
  if (!editor) return
  const code = editor.getValue()
  const questionId = route.query.questionId || question.value.id || null

  if (!code || !code.trim()) {
    alert('请先输入代码再提交')
    return
  }

  submitBusy.value = true
  try {
    const res = await http.post('/api/answer/submit', {
      code,
      language: selectedLanguage.value,
      question_id: questionId,
    })
    const result = res.data
    runResult.value = result.run_result
    await loadRecommendations()
    showDetails.value = false
    if (result.task_id) {
      startAIPolling(result.task_id)
    }
  } catch (e) {
    console.error('提交代码时出错:', e)
    alert('提交失败: ' + (e.response?.data?.message || e.message))
  } finally {
    submitBusy.value = false
  }
}

function startAIPolling(taskId) {
  if (aiPollingTimer) clearInterval(aiPollingTimer)
  pollingCount.value = 0
  aiStatus.value = 'processing'

  aiPollingTimer = setInterval(async () => {
    try {
      pollingCount.value++
      const res = await http.get(`/api/ai_review_status/${taskId}`)
      const result = res.data

      if (result.status === 'complete') {
        clearInterval(aiPollingTimer)
        aiStatus.value = 'complete'
        aiResult.value = {
          score: result.score || 0,
          feedback: (result.feedback || '无评价反馈').replace(/\n/g, ' ').trim(),
          improvements: (result.improvements || []).map(i => i.replace(/\n/g, ' ').trim()).filter(i => i.length > 0),
          original_code: result.original_code,
          reviewed_code: result.reviewed_code,
          language: result.language || 'python'
        }
        codeTab.value = 'original'
      } else if (result.status === 'error') {
        clearInterval(aiPollingTimer)
        aiStatus.value = 'error'
        let msg = result.message || '未知错误'
        if (msg.includes('JSON解析失败') || msg.includes('JSON格式错误')) msg = 'AI批改处理失败：响应格式错误'
        else if (msg.includes('代码审查异常')) msg = 'AI批改过程中出现问题'
        aiError.value = msg.replace(/\n/g, ' ').trim()
      } else if (result.status === 'processing') {
        if (pollingCount.value >= maxPollAttempts) {
          clearInterval(aiPollingTimer)
          aiStatus.value = 'timeout'
        }
      }
    } catch (e) {
      console.error('获取AI批改结果失败:', e)
      if (pollingCount.value >= maxPollAttempts) {
        clearInterval(aiPollingTimer)
        aiStatus.value = 'error'
        aiError.value = e.message.replace(/\n/g, ' ').trim()
      }
    }
  }, AI_POLL_INTERVAL)
}

async function loadRecommendations() {
  try {
    const res = await http.get('/api/ability-matrix/recommendations')
    recommendations.value = res.data?.data?.recommendations || []
  } catch (e) { console.error('加载推荐失败:', e) }
}

async function exportAbilityReport() {
  try {
    const res = await http.get('/api/ability-matrix/export?format=pdf', { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'codemind-ability-report.pdf'
    link.click()
    URL.revokeObjectURL(url)
  } catch { alert('诊断报告导出失败') }
}

async function handleFavorite() {
  const id = question.value.id || route.query.questionId
  if (!id) { alert('请先选择题目'); return }
  try {
    await http.post('/api/user/favorites', { questionId: id, action: 'add' })
    alert(`题目“${question.value.title || id}”已收藏`)
  } catch (e) { alert(e.response?.data?.message || '收藏失败') }
}

onMounted(async () => {
  await nextTick()
  initEditor()
  await loadQuestion()
  await restoreServerDraft()
  await loadRecommendations()
})

onUnmounted(() => {
  clearInterval(autoSaveTimer)
  if (aiPollingTimer) clearInterval(aiPollingTimer)
  if (editor) editor.destroy()
})
</script>

<style>
@import '../assets/css/answerpad.css';
@import '../assets/css/ai_review.css';
@import '../assets/css/Marked/github-markdown.min.css';
</style>

<style scoped>
.sample-input-wrapper {
  margin: 6px 0 12px 0;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 6px;
  padding: 8px 10px;
  background: var(--bg-subtle, #f8fafc);
}
.sample-input-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}
.mini-btn {
  padding: 2px 10px;
  border: 1px solid var(--primary, #2563eb);
  color: var(--primary, #2563eb);
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.mini-btn:hover:not(:disabled) { background: var(--primary, #2563eb); color: #fff; }
.mini-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.sample-input-textarea {
  width: 100%;
  min-height: 64px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13px;
  border: 1px solid var(--border, #e2e8f0);
  background: #fff;
  border-radius: 4px;
  padding: 6px 8px;
  resize: vertical;
  box-sizing: border-box;
}

.action-row {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.run-btn {
  flex: 0 0 auto;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  background: #10b981;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background .15s ease;
}
.run-btn:hover:not(:disabled) { background: #059669; }
.run-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.submit-btn {
  flex: 1 1 auto;
  min-width: 220px;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  background: var(--primary, #2563eb);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.submit-btn:hover:not(:disabled) { filter: brightness(0.92); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.output-pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 12.5px;
  line-height: 1.55;
  margin: 0;
  max-height: 340px;
  overflow: auto;
}
.error-pre {
  background: #3f0d0d;
  color: #fecaca;
}
.diagnosis-item { padding: 10px; margin: 8px 0; border-left: 3px solid var(--primary, #2563eb); background: rgba(37, 99, 235, .07); border-radius: 5px; }
.diagnosis-item p { margin: 5px 0 0; font-size: 13px; line-height: 1.5; }
#recommended-questions { display: grid; gap: 7px; }
.recommended-task { display: flex; justify-content: space-between; border: 1px solid #cbd5e1; border-radius: 7px; padding: 8px 10px; background: var(--card-bg, #fff); color: var(--text-color, #1f2937); cursor: pointer; text-align: left; }
</style>

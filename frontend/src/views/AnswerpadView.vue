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
                    <div class="output-content" v-html="(tc.actual_output || tc.error || '暂无输出').replace(/\n/g, '<br>')"></div>
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
          <div class="editor-container">
            <div ref="editorRef" id="editor" class="code-editor"></div>
          </div>
          <button class="submit-btn" id="submit-btn" @click="submitCode">提交评估</button>
        </section>

        <section class="diagnosis-section">
          <div class="weakness-analysis">
            <h3>知识薄弱点分析</h3>
            <div id="weakness-list"></div>
            <button id="export-pdf" @click="alert('PDF导出功能需集成jsPDF库')">导出诊断报告</button>
          </div>
          <div class="recommendations">
            <h3>推荐练习题目</h3>
            <div id="recommended-questions"></div>
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

// 运行结果
const runResult = ref(null)

// AI 批改状态
const aiStatus = ref('') // '', 'processing', 'complete', 'error', 'timeout'
const aiResult = ref({})
const aiError = ref('')
const pollingCount = ref(0)
const maxPollAttempts = AI_MAX_POLL_ATTEMPTS

const renderedContent = computed(() => {
  if (!question.value.content) return ''
  try {
    return marked.parse(question.value.content)
  } catch {
    return question.value.content
  }
})

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

  const savedData = JSON.parse(localStorage.getItem('currentQuestion')) || {}
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
  localStorage.setItem('currentQuestion', JSON.stringify({
    code: editor ? editor.getValue() : '',
    language: selectedLanguage.value
  }))
}

function setupAutoSave() {
  clearInterval(autoSaveTimer)
  autoSaveTimer = setInterval(() => {
    saveToLocal()
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

async function submitCode() {
  if (!editor) return
  const code = editor.getValue()
  const questionId = route.query.questionId || question.value.id || null

  try {
    const res = await http.post('/api/process_algorithm_code', {
      code,
      language: selectedLanguage.value,
      question_id: questionId
    })
    const result = res.data
    runResult.value = result.run_result
    showDetails.value = false
    startAIPolling(result.task_id)
  } catch (e) {
    console.error('提交代码时出错:', e)
    alert('提交失败: ' + (e.response?.data?.message || e.message))
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

function handleFavorite() {
  const favorites = JSON.parse(localStorage.getItem('favorites')) || []
  const id = question.value.id || 'current'
  const title = question.value.title || '当前题目'
  if (!favorites.find(f => f.id === id)) {
    favorites.push({ id, title })
    localStorage.setItem('favorites', JSON.stringify(favorites))
    alert(`题目 "${title}" 已收藏！`)
  } else {
    alert(`题目 "${title}" 已经在收藏列表中。`)
  }
}

onMounted(async () => {
  await nextTick()
  initEditor()
  await loadQuestion()
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
@import '../assets/css/Ace/ace.css';
@import '../assets/css/Ace/theme/monokai.css';
@import '../assets/css/Marked/github-markdown.min.css';
</style>

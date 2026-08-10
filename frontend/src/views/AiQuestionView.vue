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
    <!-- 左侧区域 -->
    <div class="left-panel">
      <!-- AI出题设置表单 -->
      <div class="question-header">
        <h3>AI出题设置</h3>
      </div>
      <div class="capsule-form">
        <div class="form-section">
          <h3>选择难度</h3>
          <div class="difficulty-filter">
            <label><input type="radio" name="difficulty" value="简单" v-model="difficulty" checked> 简单</label>
            <label><input type="radio" name="difficulty" value="中等" v-model="difficulty"> 中等</label>
            <label><input type="radio" name="difficulty" value="困难" v-model="difficulty"> 困难</label>
          </div>
        </div>
        <div class="form-section">
          <h3>选择算法类型</h3>
          <select id="algorithm-type" v-model="algorithmType" aria-label="选择算法类型">
            <option value="排序算法">排序算法</option>
            <option value="查找算法">查找算法</option>
            <option value="图算法">图算法</option>
            <option value="动态规划">动态规划</option>
            <option value="贪心算法">贪心算法</option>
            <option value="回溯算法">回溯算法</option>
            <option value="分治算法">分治算法</option>
            <option value="数据结构">数据结构</option>
          </select>
        </div>
        <button id="generate-btn" class="btn-primary" @click="generateQuestion" :disabled="generating">
          {{ generating ? generatingText : '生成题目' }}
        </button>
      </div>

      <!-- 题目信息区域 -->
      <div v-show="currentQuestion" id="question-container">
        <div class="question-header">
          <div class="flex-header">
            <h3>题目信息</h3>
            <button id="favorite-btn" class="btn-favorite" @click="handleFavorite">收藏题目</button>
          </div>
        </div>
        <div class="question-content" id="question-content">
          <h2 id="question-title">{{ currentQuestion?.title }}</h2>
          <div id="question-details" class="markdown-body" v-html="renderedContent"></div>
        </div>
      </div>

      <!-- 运行结果显示区域 -->
      <div v-show="currentQuestion" class="backend-results" id="backend-results">
        <div class="result-section" id="run-result-container">
          <h3>代码运行结果</h3>
          <div class="result-content" id="run-result">
            <div v-if="runResult" class="result-container overall-result" @click="showDetails = !showDetails">
              <div class="result-header">
                <div class="result-status" :class="runResult.success ? 'status-success' : 'status-failed'">
                  <span>{{ runResult.success ? '成功' : '失败' }}<i class="status-icon"></i></span>
                </div>
                <div class="result-metrics">
                  <span class="metric-item">总: {{ runResult.total_cases }}</span>
                  <span class="metric-item">通过: {{ runResult.passed_cases }}</span>
                  <span class="metric-item">失败: {{ runResult.failed_cases }}</span>
                </div>
              </div>
              <div class="result-output">
                <h4>详细信息<i :class="showDetails ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down'"></i></h4>
              </div>
              <div class="test-cases-wrapper" v-show="showDetails">
                <div v-for="(tc, idx) in runResult.results" :key="idx" class="result-container">
                  <div class="result-header">
                    <div class="result-status" :class="tc.success ? 'status-success' : 'status-failed'">
                      <i class="status-icon"></i><span>{{ tc.success ? '成功' : '失败' }}</span>
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
            <div v-if="aiStatus === 'processing'" class="ai-processing">
              <span>AI批改处理中 ({{ pollingCount }}/{{ maxPollAttempts }})</span>
              <div class="ai-loading-dots"></div>
            </div>
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
            <div v-else-if="aiStatus === 'error'" class="ai-review-container">
              <div class="ai-error">
                <h4>AI批改失败</h4>
                <p>{{ aiError }}</p>
                <button class="btn-retry" @click="submitCode">重试</button>
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

const editorRef = ref(null)
let editor = null
let autoSaveTimer = null
let aiPollingTimer = null

const difficulty = ref('简单')
const algorithmType = ref('排序算法')
const generating = ref(false)
const generatingText = ref('生成中...')
const currentQuestion = ref(null)
const selectedLanguage = ref('python')
const saveStatusText = ref('已保存')
const showDetails = ref(false)
const codeTab = ref('original')
const runResult = ref(null)
const aiStatus = ref('')
const aiResult = ref({})
const aiError = ref('')
const pollingCount = ref(0)
const maxPollAttempts = AI_MAX_POLL_ATTEMPTS

const renderedContent = computed(() => {
  if (!currentQuestion.value?.content) return ''
  try { return marked.parse(currentQuestion.value.content) } catch { return currentQuestion.value.content }
})

function getAceMode(lang) {
  const map = { python: 'ace/mode/python', javascript: 'ace/mode/javascript', java: 'ace/mode/java', 'c++': 'ace/mode/c_cpp' }
  return map[lang] || 'ace/mode/python'
}

function initEditor() {
  if (!editorRef.value) return
  editor = ace.edit(editorRef.value)
  editor.setTheme('ace/theme/monokai')
  const savedData = JSON.parse(localStorage.getItem('currentAIQuestion')) || {}
  const lang = savedData.language || 'python'
  selectedLanguage.value = lang
  editor.session.setMode(getAceMode(lang))
  editor.setOptions({
    enableBasicAutocompletion: true, enableLiveAutocompletion: true, enableSnippets: true,
    fontSize: '14px', fontFamily: "'JetBrains Mono', 'Consolas', monospace",
    showLineNumbers: true, showGutter: true, highlightActiveLine: true, showPrintMargin: false, scrollPastEnd: 0.5
  })
  editor.setValue(savedData.code || '# 生成题目后开始编写你的代码...', -1)
}

function onLanguageChange() {
  if (editor) editor.session.setMode(getAceMode(selectedLanguage.value))
}

function setupAutoSave() {
  clearInterval(autoSaveTimer)
  autoSaveTimer = setInterval(() => {
    localStorage.setItem('currentAIQuestion', JSON.stringify({
      code: editor.getValue(), language: selectedLanguage.value,
      questionId: currentQuestion.value?.id
    }))
    saveStatusText.value = `已保存 ${new Date().toLocaleTimeString()}`
  }, AUTO_SAVE_INTERVAL)
}

async function generateQuestion() {
  generating.value = true
  let dots = ''
  const loadingInterval = setInterval(() => {
    dots = dots.length >= 3 ? '' : dots + '.'
    generatingText.value = `生成中${dots}`
  }, 500)

  try {
    const res = await http.post('/api/generate-question', {
      algorithm_type: algorithmType.value,
      difficulty_level: difficulty.value
    })
    clearInterval(loadingInterval)
    generating.value = false
    const data = res.data
    if (data.error) throw new Error(data.error)
    currentQuestion.value = data.question
    editor.setValue('# 请在此编写你的代码\n', -1)
    setupAutoSave()
  } catch (e) {
    clearInterval(loadingInterval)
    generating.value = false
    generatingText.value = '重新生成'
    alert(`生成题目失败: ${e.message}`)
  }
}

async function submitCode() {
  if (!editor || !currentQuestion.value) { alert('请先生成题目！'); return }
  try {
    const res = await http.post('/api/process_algorithm_code', {
      code: editor.getValue(), language: selectedLanguage.value,
      question_id: currentQuestion.value.id || 'ai_generated_temp'
    })
    runResult.value = res.data.run_result
    showDetails.value = false
    startAIPolling(res.data.task_id)
  } catch (e) {
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
          original_code: result.original_code, reviewed_code: result.reviewed_code
        }
      } else if (result.status === 'error') {
        clearInterval(aiPollingTimer); aiStatus.value = 'error'
        aiError.value = (result.message || '未知错误').replace(/\n/g, ' ').trim()
      } else if (result.status === 'processing' && pollingCount.value >= maxPollAttempts) {
        clearInterval(aiPollingTimer); aiStatus.value = 'error'; aiError.value = 'AI批改超时'
      }
    } catch (e) {
      if (pollingCount.value >= maxPollAttempts) { clearInterval(aiPollingTimer); aiStatus.value = 'error'; aiError.value = e.message }
    }
  }, AI_POLL_INTERVAL)
}

function handleFavorite() {
  if (!currentQuestion.value) return
  const favorites = JSON.parse(localStorage.getItem('favorites')) || []
  const id = currentQuestion.value.id || 'ai_temp'
  const title = currentQuestion.value.title || 'AI生成题目'
  if (!favorites.find(f => f.id === id)) {
    favorites.push({ id, title }); localStorage.setItem('favorites', JSON.stringify(favorites))
    alert(`题目 "${title}" 已收藏！`)
  } else { alert(`题目 "${title}" 已经在收藏列表中。`) }
}

onMounted(async () => { await nextTick(); initEditor() })
onUnmounted(() => { clearInterval(autoSaveTimer); if (aiPollingTimer) clearInterval(aiPollingTimer); if (editor) editor.destroy() })
</script>

<style>
@import '../assets/css/answerpad.css';
@import '../assets/css/ai_review.css';
@import '../assets/css/Ace/ace.css';
@import '../assets/css/Ace/theme/monokai.css';
@import '../assets/css/Marked/github-markdown.min.css';
</style>

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
  </div>
</template>

<script setup>
import { ref } from 'vue'
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
    const res = await http.post('/process_code', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const data = res.data
    if (data.status === 200) {
      reviewResults.value = data.results || []
    } else {
      alert(data.message || '提交失败，请重试')
    }
  } catch (e) {
    console.error('提交失败:', e)
    alert('提交失败: ' + (e.response?.data?.message || e.message))
  }
}
</script>

<style>
@import '../assets/css/code_review.css';
@import '../assets/css/bootstrap/bootstrap.css';
</style>

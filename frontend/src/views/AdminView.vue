<template>
  <div class="admin-wrapper">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <router-link to="/dashboard" class="logo">
        <img src="/img/logo.jpg" alt="Logo" />
        <span>CodeMind Studio — 🛠 管理员后台</span>
      </router-link>
      <div class="nav-buttons"><ThemeToggle /></div>
    </nav>

    <div class="container admin-body">
      <!-- 概览 -->
      <header class="overview">
        <div v-for="(v, k) in summary" :key="k" class="stat-card">
          <div class="stat-label">{{ statLabel(k) }}</div>
          <div class="stat-value">{{ Number(v || 0).toLocaleString() }}</div>
        </div>
      </header>

      <!-- Tab 切换 -->
      <div class="tabs">
        <button class="tab" :class="{active:tab==='users'}" @click="tab='users'">👥 用户列表</button>
        <button class="tab" :class="{active:tab==='questions'}" @click="tab='questions'">📚 题目管理</button>
        <button class="tab" :class="{active:tab==='audit'}" @click="tab='audit'">📝 操作记录审计</button>
      </div>

      <!-- ============== Tab 1: 用户列表 ============== -->
      <section v-if="tab==='users'" class="panel">
        <div class="panel-header">
          <input v-model="userQ" class="inp" placeholder="🔍 搜索用户名 / 邮箱" @input="loadUsers" />
          <span class="muted">共 {{ users.length }} 条</span>
        </div>
        <table class="tbl">
          <thead>
            <tr>
              <th>ID</th><th>用户名</th><th>邮箱</th>
              <th>注册时间</th><th>最后登录</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td class="mono">{{ u.username }}</td>
              <td>{{ u.email }}</td>
              <td class="small">{{ u.created_at || '—' }}</td>
              <td class="small">{{ u.last_login || '（从未登录）' }}</td>
            </tr>
            <tr v-if="!users.length"><td colspan="5" class="empty">暂无数据</td></tr>
          </tbody>
        </table>
      </section>

      <!-- ============== Tab 2: 题目管理 ============== -->
      <section v-if="tab==='questions'" class="panel">
        <div class="panel-header">
          <input v-model="qQ" class="inp" placeholder="🔍 搜索题目" @input="loadQuestions" />
          <button class="primary-btn" @click="openNewQuestion">➕ 新增题目</button>
        </div>
        <table class="tbl">
          <thead>
            <tr>
              <th style="width:64px">ID</th>
              <th>标题</th>
              <th style="width:80px">难度</th>
              <th>标签</th>
              <th style="width:160px">创建时间</th>
              <th style="width:180px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questions" :key="q.id">
              <td>{{ q.id }}</td>
              <td class="title-cell">{{ q.title }}</td>
              <td>
                <span class="badge" :class="'diff-'+diffClass(q.difficulty)">{{ q.difficulty || '—' }}</span>
              </td>
              <td class="small">{{ q.tags || '—' }}</td>
              <td class="small">{{ (q.created_at||'').toString().slice(0,19) }}</td>
              <td>
                <button class="mini-btn ok" @click="editQuestion(q)">编辑</button>
                <button class="mini-btn danger" @click="deleteQuestion(q)">删除</button>
              </td>
            </tr>
            <tr v-if="!questions.length"><td colspan="6" class="empty">暂无题目</td></tr>
          </tbody>
        </table>
      </section>

      <!-- ============== Tab 3: 审计记录 ============== -->
      <section v-if="tab==='audit'" class="panel">
        <div class="panel-header audit-filters">
          <select v-model="auditType" class="sel" @change="loadAudit">
            <option value="">全部类型</option>
            <option value="function">功能使用</option>
            <option value="upload">文件上传</option>
            <option value="api_response">API 响应</option>
          </select>
          <input v-model.number="auditUserId" type="number" min="0" class="inp inp-num"
                 placeholder="按 user_id 筛选（留空=全部）" @change="loadAudit" />
          <span class="muted">共 {{ auditItems.length }} 条</span>
          <button class="mini-btn" @click="loadAudit">🔄 刷新</button>
        </div>
        <table class="tbl">
          <thead>
            <tr>
              <th>时间</th><th>类型</th><th>用户ID</th><th>对象 / 名称</th><th>备注</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in auditItems" :key="r.record_type+'_'+r.id+'_'+(r.timestamp||'')">
              <td class="small">{{ r.timestamp || '—' }}</td>
              <td><span class="badge" :class="'type-'+r.record_type">{{ typeLabel(r.record_type) }}</span></td>
              <td>{{ r.user_id ?? '—' }}</td>
              <td class="mono small">{{ r.name }}</td>
              <td class="small extra-cell">{{ r.extra || '—' }}</td>
            </tr>
            <tr v-if="!auditItems.length"><td colspan="5" class="empty">暂无记录</td></tr>
          </tbody>
        </table>
      </section>
    </div>

    <!-- ============ 题目编辑 / 新增 弹窗 ============ -->
    <div v-if="editor.visible" class="modal-backdrop" @click.self="closeEditor">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editor.id ? '编辑题目 #'+editor.id : '新增题目' }}</h3>
          <button class="mini-btn" @click="closeEditor">✕ 关闭</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>标题 *</label>
            <input v-model="editor.title" class="inp" maxlength="200" />
          </div>
          <div class="form-row two-col">
            <div>
              <label>难度 *</label>
              <select v-model="editor.difficulty" class="sel">
                <option>简单</option><option>中等</option><option>困难</option>
              </select>
            </div>
            <div>
              <label>标签（逗号或数组，最多255字符）</label>
              <input v-model="editor.tags" class="inp" placeholder="数组,排序,双指针" />
            </div>
          </div>
          <div class="form-row">
            <label>题目描述 (Markdown) *</label>
            <textarea v-model="editor.content" rows="8" class="inp textarea"
                      placeholder="## 题目描述&#10;给定一个数组...&#10;&#10;## 示例输入&#10;```&#10;1 2 3&#10;```"></textarea>
          </div>

          <div class="form-row">
            <label>测试用例（每条包含输入 & 预期输出）</label>
            <div v-for="(tc, i) in editor.test_cases" :key="i" class="tc-row">
              <div class="tc-head">
                <strong>用例 {{ i + 1 }}</strong>
                <button class="mini-btn danger" :disabled="editor.test_cases.length <= 1"
                        @click="editor.test_cases.splice(i, 1)">🗑 删除</button>
              </div>
              <textarea v-model="tc.input" rows="2" class="inp textarea small-textarea"
                        placeholder="输入 (stdin，可为空字符串)" />
              <textarea v-model="tc.output" rows="2" class="inp textarea small-textarea"
                        placeholder="预期输出 (stdout)" />
              <input v-model="tc.description" class="inp" placeholder="备注（可选，如示例）" />
            </div>
            <button class="mini-btn ok" style="margin-top:6px" @click="addTestCase()">+ 添加测试用例</button>
          </div>
        </div>
        <div class="modal-footer">
          <span v-if="editor.error" class="tiny-err">{{ editor.error }}</span>
          <div>
            <button class="mini-btn" @click="closeEditor">取消</button>
            <button class="primary-btn" :disabled="editor.saving" @click="saveQuestion">
              {{ editor.saving ? '保存中…' : '💾 保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import ThemeToggle from '../components/ThemeToggle.vue'
import http from '../utils/http'

const tab = ref('users')
const summary = ref({})

// 用户
const users = ref([])
const userQ = ref('')

// 题目
const questions = ref([])
const qQ = ref('')

// 审计
const auditItems = ref([])
const auditType = ref('')
const auditUserId = ref('')

// 题目编辑器
const emptyEditor = () => ({
  visible: false,
  id: null,
  title: '',
  difficulty: '中等',
  tags: '',
  content: '',
  test_cases: [{ input: '', output: '', description: '' }],
  saving: false,
  error: '',
})
const editor = reactive(emptyEditor())

function statLabel(k) {
  return ({
    users: '注册用户数',
    problems: '题目总数',
    test_cases: '测试用例数',
    functions_used: '功能使用记录',
    user_uploads: '上传文件数',
    answer_records: '答题记录数',
  })[k] || k
}
function diffClass(d) {
  if (d === '简单') return 'easy'
  if (d === '困难') return 'hard'
  return 'medium'
}
function typeLabel(t) {
  return ({ function: '功能使用', upload: '文件上传', api_response: 'API 响应' })[t] || t
}

async function loadSummary() {
  try {
    const r = await http.get('/api/admin/summary')
    summary.value = r.data?.data || {}
  } catch (e) { console.error(e) }
}
async function loadUsers() {
  try {
    const r = await http.get('/api/admin/users', { params: { q: userQ.value, limit: 500 } })
    users.value = (r.data?.data && r.data.data.items) || []
  } catch (e) { console.error(e) }
}
async function loadQuestions() {
  try {
    const r = await http.get('/api/admin/questions', { params: { q: qQ.value, limit: 1500 } })
    questions.value = (r.data?.data && r.data.data.items) || []
  } catch (e) { console.error(e) }
}
async function loadAudit() {
  try {
    const params = { limit: 1000 }
    if (auditType.value) params.type = auditType.value
    if (Number(auditUserId.value) > 0) params.user_id = Number(auditUserId.value)
    const r = await http.get('/api/admin/audit_logs', { params })
    auditItems.value = (r.data?.data && r.data.data.items) || []
  } catch (e) { console.error(e) }
}

/* --------- 题目弹窗 --------- */
function openNewQuestion() {
  Object.assign(editor, emptyEditor(), { visible: true })
}
async function editQuestion(q) {
  try {
    const r = await http.get(`/api/admin/questions/${q.id}`)
    const d = r.data?.data || {}
    Object.assign(editor, emptyEditor(), {
      visible: true,
      id: d.id,
      title: d.title || '',
      difficulty: d.difficulty || '中等',
      tags: d.tags || '',
      content: d.content || '',
      test_cases: (d.test_cases && d.test_cases.length)
        ? d.test_cases.map(tc => ({
            input: tc.input ?? '',
            output: tc.output ?? '',
            description: tc.description ?? '',
          }))
        : [{ input: '', output: '', description: '' }],
    })
  } catch (e) {
    alert('加载题目详情失败: ' + (e.response?.data?.message || e.message))
  }
}
function closeEditor() { Object.assign(editor, emptyEditor()) }
function addTestCase() {
  editor.test_cases.push({ input: '', output: '', description: '' })
}
async function saveQuestion() {
  editor.error = ''
  if (!editor.title.trim()) { editor.error = '请填写标题'; return }
  if (!editor.content.trim()) { editor.error = '请填写题目描述'; return }

  const payload = {
    title: editor.title.trim(),
    difficulty: editor.difficulty,
    tags: editor.tags,
    content: editor.content,
    test_cases: editor.test_cases.map(tc => ({
      input: String(tc.input ?? ''),
      output: String(tc.output ?? ''),
      description: (tc.description || '').slice(0, 255),
    })),
  }
  try {
    editor.saving = true
    if (editor.id) {
      await http.put(`/api/admin/questions/${editor.id}`, payload)
      alert('题目已更新 ✅')
    } else {
      await http.post('/api/admin/questions', payload)
      alert('题目已创建 ✅')
    }
    closeEditor()
    await loadQuestions()
    await loadSummary()
  } catch (e) {
    editor.error = e.response?.data?.message || e.message || '保存失败'
  } finally {
    editor.saving = false
  }
}
async function deleteQuestion(q) {
  if (!confirm(`确定删除题目「${q.title}」(#${q.id}) 吗？此操作不可恢复。`)) return
  try {
    await http.delete(`/api/admin/questions/${q.id}`)
    alert('已删除')
    await loadQuestions()
    await loadSummary()
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.message || e.message))
  }
}

onMounted(async () => {
  await Promise.all([loadSummary(), loadUsers(), loadQuestions(), loadAudit()])
})
</script>

<style scoped>
.admin-wrapper { min-height: 100vh; background: var(--bg, #f7f8fb); color: #0f172a; }
.navbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 22px;
  background: #fff; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; z-index: 10; }
.logo { display: flex; align-items: center; gap: 10px; text-decoration: none; color: inherit; font-weight: 700; }
.logo img { width: 32px; height: 32px; border-radius: 6px; object-fit: cover; }
.nav-buttons { display: flex; align-items: center; gap: 10px; }

.admin-body { max-width: 1240px; margin: 0 auto; padding: 20px 20px 80px 20px; }

.overview { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.stat-card { background: linear-gradient(135deg, #2563eb, #4f46e5); color: #fff;
  border-radius: 10px; padding: 14px 16px; box-shadow: 0 2px 8px rgba(37,99,235,.18); }
.stat-card:nth-child(2){ background: linear-gradient(135deg,#10b981,#059669); box-shadow: 0 2px 8px rgba(16,185,129,.18); }
.stat-card:nth-child(3){ background: linear-gradient(135deg,#f59e0b,#d97706); box-shadow: 0 2px 8px rgba(245,158,11,.18); }
.stat-card:nth-child(4){ background: linear-gradient(135deg,#ef4444,#dc2626); box-shadow: 0 2px 8px rgba(239,68,68,.18); }
.stat-card:nth-child(5){ background: linear-gradient(135deg,#8b5cf6,#7c3aed); box-shadow: 0 2px 8px rgba(139,92,246,.18); }
.stat-card:nth-child(6){ background: linear-gradient(135deg,#0ea5e9,#0284c7); box-shadow: 0 2px 8px rgba(14,165,233,.18); }
.stat-label { font-size: 12.5px; opacity: .9; }
.stat-value { font-size: 24px; font-weight: 700; margin-top: 4px; }

.tabs { display: flex; gap: 6px; margin: 20px 0 8px 0; flex-wrap: wrap; }
.tab { padding: 10px 16px; border: 1px solid #cbd5e1; background: #fff; border-radius: 8px 8px 0 0;
  cursor: pointer; font-weight: 600; color: #334155; }
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; }

.panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 0 10px 10px 10px; padding: 16px; }
.panel-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.audit-filters { justify-content: flex-start; }
.muted { color: #64748b; font-size: 13px; margin-left: auto; }

.inp { padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;
  background: #fff; min-width: 220px; }
.inp-num { min-width: 240px; }
.sel { padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px; background: #fff; font-size: 14px; }
.textarea { font-family: 'JetBrains Mono', Consolas, monospace; min-height: 100px; resize: vertical; }
.small-textarea { min-height: 48px; }
.primary-btn { padding: 8px 14px; border-radius: 6px; border: none; background: #2563eb; color: #fff;
  font-weight: 600; cursor: pointer; }
.primary-btn:hover:not(:disabled){ background:#1d4ed8; }
.primary-btn:disabled { opacity: .5; cursor: not-allowed; }

.mini-btn { padding: 4px 10px; border-radius: 5px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer; font-size: 13px; }
.mini-btn.ok { border-color: #10b981; color: #047857; }
.mini-btn.ok:hover:not(:disabled) { background: #10b981; color: #fff; }
.mini-btn.danger { border-color: #ef4444; color: #b91c1c; }
.mini-btn.danger:hover:not(:disabled) { background: #ef4444; color: #fff; }
.mini-btn:disabled { opacity: .4; cursor: not-allowed; }

.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th, .tbl td { padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }
.tbl th { background: #f8fafc; color: #334155; font-weight: 600; }
.tbl .empty { text-align: center; color: #64748b; padding: 24px; }
.mono { font-family: 'JetBrains Mono', Consolas, monospace; }
.small { font-size: 12.5px; color: #475569; }
.title-cell { max-width: 420px; }
.extra-cell { max-width: 480px; word-break: break-word; }

.badge { padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; display: inline-block; }
.diff-easy { background:#dcfce7; color:#166534; }
.diff-medium{ background:#fef9c3; color:#854d0e; }
.diff-hard  { background:#fee2e2; color:#991b1b; }
.type-function     { background:#dbeafe; color:#1e40af; }
.type-upload       { background:#ede9fe; color:#5b21b6; }
.type-api_response { background:#fae8ff; color:#86198f; }

/* ====== Modal ====== */
.modal-backdrop { position: fixed; inset: 0; background: rgba(15,23,42,.5); z-index: 100;
  display: flex; align-items: flex-start; justify-content: center; padding: 30px 16px; overflow-y: auto; }
.modal { width: 100%; max-width: 860px; background: #fff; border-radius: 12px; box-shadow: 0 20px 40px rgba(15,23,42,.25); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px;
  border-bottom: 1px solid #e5e7eb; }
.modal-header h3 { margin: 0; }
.modal-body { padding: 18px; display: flex; flex-direction: column; gap: 14px; max-height: 70vh; overflow-y: auto; }
.modal-footer { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px;
  border-top: 1px solid #e5e7eb; gap: 10px; }
.form-row { display: flex; flex-direction: column; gap: 6px; }
.form-row.two-col { flex-direction: row; gap: 14px; }
.form-row.two-col > div { flex: 1; }
.form-row label { font-size: 13px; font-weight: 600; color: #334155; }
.tc-row { border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; margin-top: 8px;
  display: flex; flex-direction: column; gap: 6px; background: #fafbff; }
.tc-head { display: flex; justify-content: space-between; align-items: center; }
.tiny-err { margin: 0; font-size: 12.5px; color: #b91c1c; }

@media (max-width: 760px) {
  .form-row.two-col { flex-direction: column; }
  .inp { min-width: 0; width: 100%; box-sizing: border-box; }
}
</style>

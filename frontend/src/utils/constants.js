// API 基础路径（通过 Vite proxy 代理，无需指定完整 URL）
export const API_BASE = ''

// 编程语言选项
export const LANGUAGES = [
  { value: 'python', label: 'Python', aceMode: 'ace/mode/python' },
  { value: 'javascript', label: 'JavaScript', aceMode: 'ace/mode/javascript' },
  { value: 'java', label: 'Java', aceMode: 'ace/mode/java' },
  { value: 'c++', label: 'C++', aceMode: 'ace/mode/c_cpp' }
]

// 难度选项
export const DIFFICULTIES = [
  { value: 'easy', label: '简单' },
  { value: 'medium', label: '中等' },
  { value: 'hard', label: '困难' }
]

// 算法类型选项
export const ALGORITHM_TYPES = [
  { value: 'sorting', label: '排序算法' },
  { value: 'searching', label: '搜索算法' },
  { value: 'dynamic_programming', label: '动态规划' },
  { value: 'graph', label: '图论算法' },
  { value: 'string', label: '字符串算法' },
  { value: 'tree', label: '树形算法' },
  { value: 'greedy', label: '贪心算法' },
  { value: 'recursion', label: '递归算法' },
  { value: 'backtracking', label: '回溯算法' },
  { value: 'hashing', label: '哈希算法' },
  { value: 'linked_list', label: '链表算法' }
]

// 能力矩阵维度
export const ABILITY_DIMENSIONS = [
  { key: 'syntax_score', label: '语法能力' },
  { key: 'algorithm_score', label: '算法能力' },
  { key: 'project_score', label: '项目能力' },
  { key: 'debug_score', label: '调试能力' },
  { key: 'security_score', label: '安全能力' }
]

// AI 批改轮询配置
export const AI_POLL_INTERVAL = 2000
export const AI_MAX_POLL_ATTEMPTS = 30

// 自动保存间隔（毫秒）
export const AUTO_SAVE_INTERVAL = 30000

// 代码审查功能 Tab
export const CODE_REVIEW_TABS = [
  { id: 'code-commenting', label: '代码注释', tabId: 'code-commenting-tab' },
  { id: 'code-documentation', label: '代码文档', tabId: 'code-documentation-tab' },
  { id: 'missing-comment', label: '缺失注释', tabId: 'missing-comment-tab' },
  { id: 'code-conformance', label: '代码规范', tabId: 'code-conformance-tab' }
]

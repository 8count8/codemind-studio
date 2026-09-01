-- ============================================================
-- CodeMind Studio - 完整数据库初始化脚本
-- 目标数据库: MySQL 8.0+
-- 包含: 建表 + 种子数据（题目/测试用例/管理员账户）
-- 用法: 在 MySQL 客户端中整段执行
-- ============================================================

SET NAMES utf8mb4;

-- ============================================================
-- 第一部分：建表
-- ============================================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 验证码表
CREATE TABLE IF NOT EXISTS verification_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) NOT NULL,
    sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 功能使用日志表
CREATE TABLE IF NOT EXISTS functions_used (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    function_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 用户上传文件表
CREATE TABLE IF NOT EXISTS user_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_path TEXT,
    file_content LONGTEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. API 响应记录表
CREATE TABLE IF NOT EXISTS api_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_upload_id INT NOT NULL,
    response_file_name VARCHAR(255),
    response_file_content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 收藏夹表
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    question_title VARCHAR(255),
    question_content TEXT,
    topic_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6.1 收藏题单
CREATE TABLE IF NOT EXISTS favorite_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(80) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    tags VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_favorite_topics_user_name (user_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 答题记录表
CREATE TABLE IF NOT EXISTS answer_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    user_answer TEXT,
    is_correct INT DEFAULT 0,
    time_spent INT,
    language VARCHAR(30) DEFAULT 'python',
    execution_result LONGTEXT,
    score FLOAT DEFAULT 0,
    run_time_ms INT DEFAULT 0,
    task_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7.1 答题草稿（服务端兜底；前端同时使用 localStorage）
CREATE TABLE IF NOT EXISTS user_drafts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    language VARCHAR(30) DEFAULT 'python',
    code LONGTEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_user_drafts_user_question (user_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 能力矩阵表
CREATE TABLE IF NOT EXISTS ability_matrix (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    syntax_score FLOAT DEFAULT 0,
    algorithm_score FLOAT DEFAULT 0,
    project_score FLOAT DEFAULT 0,
    debug_score FLOAT DEFAULT 0,
    security_score FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 题目表
CREATE TABLE IF NOT EXISTS problems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    difficulty VARCHAR(20),
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    problem_id INT NOT NULL,
    input_data TEXT,
    expected_output TEXT,
    description VARCHAR(255) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. 能力评估提交记录表
CREATE TABLE IF NOT EXISTS ability_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(100),
    scores_json TEXT,
    detail_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ============================================================
-- 子维度细化表（对应文档 §1.2.1 子维度细化设计）
-- 存储每个主维度下的子维度分数，支持子雷达图展示
-- ============================================================
CREATE TABLE IF NOT EXISTS ability_subscores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dimension VARCHAR(50) NOT NULL COMMENT '主维度字段名，如 algorithm_score',
    sub_dimension VARCHAR(50) NOT NULL COMMENT '子维度名，如 排序/查找/动态规划',
    score DECIMAL(5,2) DEFAULT 0.00 COMMENT '子维度分数 0-100',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_sub (user_id, dimension, sub_dimension),
    INDEX idx_user (user_id),
    INDEX idx_dimension (dimension),
    CONSTRAINT fk_subscores_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='能力矩阵子维度细分';


-- ============================================================
-- 成就/勋章定义表（对应文档 §十一 成就与勋章系统）
-- ============================================================
CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '成就代码，如 syntax_master',
    name VARCHAR(100) NOT NULL COMMENT '成就名称，如 语法达人',
    description TEXT COMMENT '成就描述',
    icon VARCHAR(50) DEFAULT 'medal' COMMENT '图标名称',
    category VARCHAR(50) DEFAULT 'ability' COMMENT '成就类别：ability/submission/streak/special',
    condition_type VARCHAR(50) NOT NULL COMMENT '条件类型：dimension_score/submission_count/streak_days',
    condition_value DECIMAL(8,2) NOT NULL COMMENT '条件阈值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成就勋章定义';


-- ============================================================
-- 用户成就解锁记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    achievement_id INT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_achievement (user_id, achievement_id),
    INDEX idx_user (user_id),
    CONSTRAINT fk_ua_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ua_achievement FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户成就解锁记录';


-- 成就定义种子数据（INSERT IGNORE 保证重复执行安全）
INSERT IGNORE INTO achievements (code, name, description, icon, category, condition_type, condition_value) VALUES
('syntax_master',    '语法达人',   '语法基础维度达到 80 分以上',           'code',        'ability',   'dimension_score', 80),
('algorithm_expert', '算法专家',   '算法思维维度达到 80 分以上',           'cpu',         'ability',   'dimension_score', 80),
('project_architect','架构师',     '项目实践维度达到 80 分以上',           'cube',        'ability',   'dimension_score', 80),
('debug_master',     '调试大师',   '调试能力维度达到 80 分以上',           'bug',         'ability',   'dimension_score', 80),
('security_guard',   '安全卫士',   '安全意识维度达到 80 分以上',           'shield-alt',  'ability',   'dimension_score', 80),
('all_round',        '全面发展',   '所有 5 个维度均达到 60 分以上',        'star',        'ability',   'all_dimensions_60', 60),
('first_blood',      '初出茅庐',   '完成首次代码评估提交',                 'flag',        'submission','submission_count', 1),
('persistent',       '坚持不懈',   '累计完成 10 次代码评估提交',           'fire',        'submission','submission_count', 10);


-- ============================================================
-- 第二部分：种子数据 —— 题目（problems）
-- ============================================================

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '两数之和',
    '### 题目描述
给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

### 示例
- 输入：nums = [2,7,11,15], target = 9 → 输出：[0,1]
- 输入：nums = [3,2,4], target = 6 → 输出：[1,2]
- 输入：nums = [3,3], target = 6 → 输出：[0,1]

### 提示
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- 只会存在一个有效答案',
    '简单',
    '数组,哈希表'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '反转链表',
    '### 题目描述
给你单链表的头节点 head，请你反转链表，并返回反转后的链表。

### 示例
- 输入：head = [1,2,3,4,5] → 输出：[5,4,3,2,1]
- 输入：head = [1,2] → 输出：[2,1]
- 输入：head = [] → 输出：[]

### 提示
- 链表中节点的数目范围是 [0, 5000]
- -5000 <= Node.val <= 5000

### 进阶
链表可以选用迭代或递归方式完成反转。你能否用两种方法解决这道题？',
    '简单',
    '链表,递归'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '有效的括号',
    '### 题目描述
给定一个只包括 ''('')''{''}''['']'' 的字符串 s，判断字符串是否有效。

有效字符串需满足：
1. 左括号必须用相同类型的右括号闭合。
2. 左括号必须以正确的顺序闭合。
3. 每个右括号都有一个对应的相同类型的左括号。

### 示例
- 输入：s = "()" → 输出：true
- 输入：s = "()[]{}" → 输出：true
- 输入：s = "(]" → 输出：false
- 输入：s = "([)]" → 输出：false
- 输入：s = "{[]}" → 输出：true

### 提示
- 1 <= s.length <= 10^4
- s 仅由括号 ''()[]{}'' 组成',
    '简单',
    '栈,字符串'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '最长回文子串',
    '### 题目描述
给你一个字符串 s，找到 s 中最长的回文子串。

### 示例
- 输入：s = "babad" → 输出："bab"（"aba" 同样是有效答案）
- 输入：s = "cbbd" → 输出："bb"

### 提示
- 1 <= s.length <= 1000
- s 仅由数字和英文字母组成',
    '中等',
    '字符串,动态规划'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '三数之和',
    '### 题目描述
给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k，同时还满足 nums[i] + nums[j] + nums[k] == 0。

请你返回所有和为 0 且不重复的三元组。

### 示例
- 输入：nums = [-1,0,1,2,-1,-4] → 输出：[[-1,-1,2],[-1,0,1]]
- 输入：nums = [0,1,1] → 输出：[]
- 输入：nums = [0,0,0] → 输出：[[0,0,0]]

### 提示
- 3 <= nums.length <= 3000
- -10^5 <= nums[i] <= 10^5',
    '中等',
    '数组,双指针,排序'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '合并区间',
    '### 题目描述
以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [starti, endi]。

请你合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。

### 示例
- 输入：intervals = [[1,3],[2,6],[8,10],[15,18]] → 输出：[[1,6],[8,10],[15,18]]
- 输入：intervals = [[1,4],[4,5]] → 输出：[[1,5]]

### 提示
- 1 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= starti <= endi <= 10^4',
    '中等',
    '数组,排序'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '二叉树的层序遍历',
    '### 题目描述
给你二叉树的根节点 root，返回其节点值的层序遍历。（即逐层地，从左到右访问所有节点）。

### 示例
- 输入：root = [3,9,20,null,null,15,7] → 输出：[[3],[9,20],[15,7]]
- 输入：root = [1] → 输出：[[1]]
- 输入：root = [] → 输出：[]

### 提示
- 树中节点数目在范围 [0, 2000] 内
- -1000 <= Node.val <= 1000',
    '中等',
    '树,广度优先搜索,二叉树'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '快速排序',
    '### 题目描述
实现快速排序算法，对一个整数数组进行升序排序。

### 要求
- 手写快速排序的 partition 过程
- 平均时间复杂度 O(n log n)
- 空间复杂度 O(log n)

### 示例
- 输入：[3,6,8,10,1,2,1] → 输出：[1,1,2,3,6,8,10]
- 输入：[5,4,3,2,1] → 输出：[1,2,3,4,5]

### 提示
- 选择基准元素时有多种策略（首元素/末元素/随机/三数取中），注意最坏情况退化',
    '中等',
    '排序,分治,递归'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    'LRU 缓存',
    '### 题目描述
请你设计并实现一个满足 LRU (最近最少使用) 缓存约束的数据结构。

实现 LRUCache 类：
- LRUCache(int capacity) 以正整数作为容量 capacity 初始化 LRU 缓存
- int get(int key) 如果关键字 key 存在于缓存中，则返回关键字的值，否则返回 -1
- void put(int key, int value) 如果关键字 key 已经存在，则变更其数据值 value；如果不存在，则向缓存中插入该组 key-value。如果插入操作导致关键字数量超过 capacity，则应该逐出最久未使用的关键字。

函数 get 和 put 必须以 O(1) 的平均时间复杂度运行。

### 示例
- 输入：["LRUCache","put","put","get","put","get","put","get","get","get"], [[2],[1,1],[2,2],[1],[3,3],[2],[4,4],[1],[3],[4]]
- 输出：[null,null,null,1,null,-1,null,-1,3,4]

### 提示
- 1 <= capacity <= 3000
- 0 <= key <= 10000
- 0 <= value <= 10^5
- 最多调用 2 * 10^5 次 get 和 put',
    '中等',
    '设计,哈希表,链表,双向链表'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '二叉树的最大路径和',
    '### 题目描述
二叉树中的路径被定义为一条节点序列，序列中每对相邻节点之间都存在一条边。

同一个节点在一条路径序列中至多出现一次。该路径至少包含一个节点，且不一定经过根节点。

路径和是路径中各节点值的总和。

给你一个二叉树的根节点 root，返回其最大路径和。

### 示例
- 输入：root = [1,2,3] → 输出：6（路径 2 -> 1 -> 3）
- 输入：root = [-10,9,20,null,null,15,7] → 输出：42（路径 15 -> 20 -> 7）

### 提示
- 树中节点数目范围是 [1, 3 * 10^4]
- -1000 <= Node.val <= 1000',
    '困难',
    '树,深度优先搜索,动态规划,二叉树'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '接雨水',
    '### 题目描述
给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。

### 示例
- 输入：height = [0,1,0,2,1,0,1,3,2,1,2,1] → 输出：6
- 输入：height = [4,2,0,3,2,5] → 输出：9

### 提示
- n == height.length
- 1 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

### 进阶
能否用 O(n) 时间复杂度和 O(1) 空间复杂度解决？',
    '困难',
    '数组,双指针,动态规划,栈'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '编辑距离',
    '### 题目描述
给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。

你可以对一个单词进行如下三种操作：
1. 插入一个字符
2. 删除一个字符
3. 替换一个字符

### 示例
- 输入：word1 = "horse", word2 = "ros" → 输出：3
  horse -> rorse (替换 h 为 r) -> rose (删除 r) -> ros (删除 e)
- 输入：word1 = "intention", word2 = "execution" → 输出：5

### 提示
- 0 <= word1.length, word2.length <= 500
- word1 和 word2 由小写英文字母组成',
    '困难',
    '字符串,动态规划'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '爬楼梯',
    '### 题目描述
假设你正在爬楼梯。需要 n 阶你才能到达楼顶。

每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？

### 示例
- 输入：n = 2 → 输出：2（方法：1+1 或 2）
- 输入：n = 3 → 输出：3（方法：1+1+1 或 1+2 或 2+1）

### 提示
- 1 <= n <= 45',
    '简单',
    '动态规划,数学'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '买卖股票的最佳时机',
    '### 题目描述
给定一个数组 prices，它的第 i 个元素 prices[i] 表示一支给定股票第 i 天的价格。

你只能选择某一天买入这只股票，并选择在未来的某一个不同的日子卖出该股票。设计一个算法来计算你所能获取的最大利润。

返回你可以从这笔交易中获取的最大利润。如果你不能获取任何利润，返回 0。

### 示例
- 输入：[7,1,5,3,6,4] → 输出：5（在第 2 天买入，在第 5 天卖出，利润 = 6-1 = 5）
- 输入：[7,6,4,3,1] → 输出：0（在这种情况下，没有交易完成，最大利润为 0）

### 提示
- 1 <= prices.length <= 10^5
- 0 <= prices[i] <= 10^4',
    '简单',
    '数组,动态规划'
) ON DUPLICATE KEY UPDATE title=title;

INSERT INTO problems (title, content, difficulty, tags) VALUES
(
    '无重复字符的最长子串',
    '### 题目描述
给定一个字符串 s，请你找出其中不含有重复字符的最长子串的长度。

### 示例
- 输入：s = "abcabcbb" → 输出：3（最长子串 "abc"）
- 输入：s = "bbbbb" → 输出：1（最长子串 "b"）
- 输入：s = "pwwkew" → 输出：3（最长子串 "wke"）

### 提示
- 0 <= s.length <= 5 * 10^4
- s 由英文字母、数字、符号和空格组成',
    '中等',
    '哈希表,字符串,滑动窗口'
) ON DUPLICATE KEY UPDATE title=title;


-- ============================================================
-- 第三部分：种子数据 —— 测试用例（test_cases）
-- ============================================================

-- 题目 1: 两数之和
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(1, '[2,7,11,15]\n9', '[0,1]'),
(1, '[3,2,4]\n6', '[1,2]'),
(1, '[3,3]\n6', '[0,1]');

-- 题目 2: 反转链表
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(2, '[1,2,3,4,5]', '[5,4,3,2,1]'),
(2, '[1,2]', '[2,1]'),
(2, '[]', '[]');

-- 题目 3: 有效的括号
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(3, '()', 'true'),
(3, '()[]{}', 'true'),
(3, '(]', 'false'),
(3, '([)]', 'false'),
(3, '{[]}', 'true');

-- 题目 4: 最长回文子串
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(4, 'babad', 'bab'),
(4, 'cbbd', 'bb');

-- 题目 5: 三数之和
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(5, '[-1,0,1,2,-1,-4]', '[[-1,-1,2],[-1,0,1]]'),
(5, '[0,1,1]', '[]'),
(5, '[0,0,0]', '[[0,0,0]]');

-- 题目 6: 合并区间
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(6, '[[1,3],[2,6],[8,10],[15,18]]', '[[1,6],[8,10],[15,18]]'),
(6, '[[1,4],[4,5]]', '[[1,5]]');

-- 题目 7: 二叉树的层序遍历
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(7, '[3,9,20,null,null,15,7]', '[[3],[9,20],[15,7]]'),
(7, '[1]', '[[1]]'),
(7, '[]', '[]');

-- 题目 8: 快速排序
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(8, '[3,6,8,10,1,2,1]', '[1,1,2,3,6,8,10]'),
(8, '[5,4,3,2,1]', '[1,2,3,4,5]'),
(8, '[1]', '[1]'),
(8, '[]', '[]');

-- 题目 9: LRU 缓存
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(9, 'LRUCache(2); put(1,1); put(2,2); get(1); put(3,3); get(2); put(4,4); get(1); get(3); get(4)',
 '[null,null,null,1,null,-1,null,-1,3,4]');

-- 题目 10: 二叉树的最大路径和
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(10, '[1,2,3]', '6'),
(10, '[-10,9,20,null,null,15,7]', '42');

-- 题目 11: 接雨水
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(11, '[0,1,0,2,1,0,1,3,2,1,2,1]', '6'),
(11, '[4,2,0,3,2,5]', '9');

-- 题目 12: 编辑距离
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(12, 'horse\nros', '3'),
(12, 'intention\nexecution', '5');

-- 题目 13: 爬楼梯
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(13, '2', '2'),
(13, '3', '3'),
(13, '5', '8');

-- 题目 14: 买卖股票的最佳时机
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(14, '[7,1,5,3,6,4]', '5'),
(14, '[7,6,4,3,1]', '0');

-- 题目 15: 无重复字符的最长子串
INSERT INTO test_cases (problem_id, input_data, expected_output) VALUES
(15, 'abcabcbb', '3'),
(15, 'bbbbb', '1'),
(15, 'pwwkew', '3');


-- ============================================================
-- 第四部分：预置账户
-- ============================================================

-- 管理员账户: admin / admin123456
INSERT INTO users (username, password, email) VALUES
(
    'admin',
    '$2b$12$lneFaHZ/E/1Fhwb9nVlI5OUhzocw8Z0YHKvorYqqfZN8JzOevcb/a',
    'admin@codemind.studio'
) ON DUPLICATE KEY UPDATE username=username;

-- 测试账户: testuser / test123456
INSERT INTO users (username, password, email) VALUES
(
    'testuser',
    '$2b$12$F9GfopyoCTNkmYc7vjEJ5.92YWums0a7NRdgrah/IPL4cXI5YZRQ6',
    'testuser@codemind.studio'
) ON DUPLICATE KEY UPDATE username=username;


-- ============================================================
-- 第五部分：创建索引
-- ============================================================

CREATE INDEX idx_problems_difficulty ON problems(difficulty);
CREATE INDEX idx_problems_tags ON problems(tags(191));
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_topic_id ON favorites(topic_id);
CREATE INDEX idx_favorite_topics_user_id ON favorite_topics(user_id);
CREATE UNIQUE INDEX idx_favorites_user_question ON favorites(user_id, question_id);
CREATE INDEX idx_answer_records_user_id ON answer_records(user_id);
CREATE INDEX idx_user_drafts_user_id ON user_drafts(user_id);
CREATE INDEX idx_functions_used_user_id ON functions_used(user_id);
CREATE INDEX idx_user_uploads_user_id ON user_uploads(user_id);
CREATE INDEX idx_api_responses_upload_id ON api_responses(user_upload_id);
CREATE INDEX idx_ability_matrix_user_id ON ability_matrix(user_id);
CREATE INDEX idx_ability_submissions_user_id ON ability_submissions(user_id);
CREATE INDEX idx_test_cases_problem_id ON test_cases(problem_id);


-- ============================================================
-- 验证
-- ============================================================
SELECT '--- 建表+种子数据完成 ---' AS message;
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'problems', COUNT(*) FROM problems
UNION ALL SELECT 'test_cases', COUNT(*) FROM test_cases
UNION ALL SELECT 'ability_matrix', COUNT(*) FROM ability_matrix
UNION ALL SELECT 'ability_submissions', COUNT(*) FROM ability_submissions
UNION ALL SELECT 'favorites', COUNT(*) FROM favorites
UNION ALL SELECT 'favorite_topics', COUNT(*) FROM favorite_topics
UNION ALL SELECT 'answer_records', COUNT(*) FROM answer_records
UNION ALL SELECT 'user_drafts', COUNT(*) FROM user_drafts
UNION ALL SELECT 'functions_used', COUNT(*) FROM functions_used
UNION ALL SELECT 'user_uploads', COUNT(*) FROM user_uploads
UNION ALL SELECT 'api_responses', COUNT(*) FROM api_responses
UNION ALL SELECT 'verification_codes', COUNT(*) FROM verification_codes;

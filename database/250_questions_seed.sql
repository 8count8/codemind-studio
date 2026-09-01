-- 此文件由 database/generate_questions_seed.py 自动生成，请勿手工编辑。
-- 来源: 250_questions.json; 题目: 250; 测试用例: 637
SET NAMES utf8mb4;
SET @has_description = (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'test_cases' AND COLUMN_NAME = 'description');
SET @migration_sql = IF(@has_description = 0,
  'ALTER TABLE test_cases ADD COLUMN description VARCHAR(255) DEFAULT ''''', 'SELECT 1');
PREPARE migration_stmt FROM @migration_sql;
EXECUTE migration_stmt;
DEALLOCATE PREPARE migration_stmt;
START TRANSACTION;
DELETE FROM test_cases;
DELETE FROM problems;
ALTER TABLE test_cases AUTO_INCREMENT = 1;
ALTER TABLE problems AUTO_INCREMENT = 1;

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'A+B 问题', '# A+B 问题

## 题目描述
输入两个整数 `a` 和 `b`，输出它们的和。

## 输入格式
一行输入两个整数 `a b`。

## 输出格式
输出一个整数，表示 `a+b`。

## 数据范围
`-10^9 ≤ a,b ≤ 10^9`。',
  '简单', '["基础语法","输入输出","算术"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2', '3',
  '基础用例'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-5 8', '3',
  '包含负数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1000000000 1000000000', '2000000000',
  '大数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '计算长方形面积与周长', '# 计算长方形面积与周长

## 题目描述
给定长方形的长 `a` 和宽 `b`，输出面积与周长。

## 输入格式
一行输入两个正整数 `a b`。

## 输出格式
一行输出两个整数：面积和周长，中间用一个空格分隔。

## 数据范围
`1 ≤ a,b ≤ 10^6`。',
  '简单', '["基础语法","算术","几何"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4', '12 14',
  '基础用例'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1', '1 4',
  '正方形'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 2', '20 24',
  '长条矩形'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '摄氏度转华氏度', '# 摄氏度转华氏度

## 题目描述
输入摄氏温度 `C`，按公式 `F=C×9/5+32` 转换为华氏温度。

## 输入格式
输入一个实数 `C`。

## 输出格式
输出华氏温度，保留两位小数。

## 数据范围
`-1000 ≤ C ≤ 1000`。',
  '简单', '["基础语法","浮点数","公式"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '32.00',
  '冰点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100', '212.00',
  '沸点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-40', '-40.00',
  '相同温度点'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '判断奇偶性', '# 判断奇偶性

## 题目描述
输入一个整数，判断它是奇数还是偶数。

## 输入格式
输入一个整数 `n`。

## 输出格式
若为偶数输出 `EVEN`，否则输出 `ODD`。

## 数据范围
`-10^18 ≤ n ≤ 10^18`。',
  '简单', '["条件判断","整数","取模"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8', 'EVEN',
  '偶数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-3', 'ODD',
  '负奇数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', 'EVEN',
  '零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '三个数中的最大值', '# 三个数中的最大值

## 题目描述
输入三个整数，输出其中的最大值。

## 输入格式
一行输入三个整数 `a b c`。

## 输出格式
输出一个整数，表示最大值。

## 数据范围
`-10^9 ≤ a,b,c ≤ 10^9`。',
  '简单', '["条件判断","基础语法","比较"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 9 3', '9',
  '一般情况'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-1 -5 -3', '-1',
  '全为负数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 7 7', '7',
  '相等'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '成绩等级判定', '# 成绩等级判定

## 题目描述
输入一个 0 到 100 的整数成绩：90~100 为 A，80~89 为 B，70~79 为 C，60~69 为 D，其余为 F。

## 输入格式
输入一个整数 `score`。

## 输出格式
输出对应等级字符。

## 数据范围
`0 ≤ score ≤ 100`。',
  '简单', '["条件判断","分支","基础语法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '95', 'A',
  '优秀'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '60', 'D',
  '及格线'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '59', 'F',
  '不及格'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '闰年判断', '# 闰年判断

## 题目描述
判断给定年份是否为闰年。能被 400 整除，或能被 4 整除但不能被 100 整除的年份是闰年。

## 输入格式
输入一个正整数年份 `y`。

## 输出格式
闰年输出 `YES`，否则输出 `NO`。

## 数据范围
`1 ≤ y ≤ 9999`。',
  '简单', '["条件判断","数学","日期"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2000', 'YES',
  '世纪闰年'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1900', 'NO',
  '世纪平年'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2024', 'YES',
  '普通闰年'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '绝对值', '# 绝对值

## 题目描述
输入一个整数，输出它的绝对值。

## 输入格式
输入一个整数 `n`。

## 输出格式
输出 `|n|`。

## 数据范围
`-10^18 < n < 10^18`。',
  '简单', '["基础语法","数学","条件判断"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-7', '7',
  '负数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '42', '42',
  '正数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '两数交换', '# 两数交换

## 题目描述
输入两个整数 `a`、`b`，交换它们的值后输出。

## 输入格式
一行输入两个整数 `a b`。

## 输出格式
输出交换后的 `a b`。

## 数据范围
`-10^9 ≤ a,b ≤ 10^9`。',
  '简单', '["基础语法","变量","输入输出"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 5', '5 3',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-1 8', '8 -1',
  '含负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '整数商与余数', '# 整数商与余数

## 题目描述
输入两个整数 `a` 与正整数 `b`，输出 `a` 除以 `b` 的整数商和非负余数。按数学上的欧几里得除法定义，使 `a=q×b+r` 且 `0≤r<b`。

## 输入格式
一行输入 `a b`。

## 输出格式
输出 `q r`。

## 数据范围
`-10^9 ≤ a ≤ 10^9, 1 ≤ b ≤ 10^9`。',
  '简单', '["基础语法","整除","取模"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '17 5', '3 2',
  '正数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-17 5', '-4 3',
  '负被除数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '1 到 N 求和', '# 1 到 N 求和

## 题目描述
计算 `1+2+...+N`。

## 输入格式
输入正整数 `N`。

## 输出格式
输出一个整数表示总和。

## 数据范围
`1 ≤ N ≤ 10^9`。',
  '简单', '["循环","数学","等差数列"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5', '15',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '边界'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100', '5050',
  '较大'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'N 的阶乘', '# N 的阶乘

## 题目描述
计算 `N!`。

## 输入格式
输入一个整数 `N`。

## 输出格式
输出 `N!`。

## 数据范围
`0 ≤ N ≤ 20`。',
  '简单', '["循环","数学","大整数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5', '120',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '1',
  '零阶乘'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10', '3628800',
  '较大'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '输出乘法表的一行', '# 输出乘法表的一行

## 题目描述
输入整数 `n`，输出 `n×1` 到 `n×9` 的结果。

## 输入格式
输入一个整数 `n`。

## 输出格式
一行输出 9 个整数，依次为 `n*1 ... n*9`，空格分隔。

## 数据范围
`1 ≤ n ≤ 1000`。',
  '简单', '["循环","格式化","乘法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', '2 4 6 8 10 12 14 16 18',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9', '9 18 27 36 45 54 63 72 81',
  '九九表'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计数字位数', '# 统计数字位数

## 题目描述
输入一个非负整数，统计它的十进制位数。特别地，0 的位数为 1。

## 输入格式
输入整数 `n`。

## 输出格式
输出位数。

## 数据范围
`0 ≤ n ≤ 10^18`。',
  '简单', '["循环","整数","数位"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '1',
  '零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7', '1',
  '一位数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '123456', '6',
  '多位数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '整数各位数字之和', '# 整数各位数字之和

## 题目描述
输入一个非负整数，求其十进制各位数字之和。

## 输入格式
输入整数 `n`。

## 输出格式
输出一个整数。

## 数据范围
`0 ≤ n ≤ 10^18`。',
  '简单', '["循环","数位","取模"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12345', '15',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9999', '36',
  '全九'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '反转整数数字', '# 反转整数数字

## 题目描述
输入一个非负整数，去掉前导零地输出其数字反转结果。例如 1200 反转后为 21。

## 输入格式
输入整数 `n`。

## 输出格式
输出反转后的整数。

## 数据范围
`0 ≤ n ≤ 10^18`。',
  '简单', '["循环","数位","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1200', '21',
  '尾部零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12345', '54321',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '回文整数判断', '# 回文整数判断

## 题目描述
判断一个非负整数的十进制表示是否为回文。

## 输入格式
输入整数 `n`。

## 输出格式
是回文输出 `YES`，否则输出 `NO`。

## 数据范围
`0 ≤ n ≤ 10^18`。',
  '简单', '["循环","字符串","回文"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1221', 'YES',
  '回文'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1230', 'NO',
  '非回文'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7', 'YES',
  '单个数字'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '求两个数的最大公约数', '# 求两个数的最大公约数

## 题目描述
求两个正整数的最大公约数。

## 输入格式
一行输入两个正整数 `a b`。

## 输出格式
输出 `gcd(a,b)`。

## 数据范围
`1 ≤ a,b ≤ 10^18`。',
  '简单', '["数学","欧几里得算法","循环"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12 18', '6',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '17 13', '1',
  '互质'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100 10', '10',
  '整除'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '求两个数的最小公倍数', '# 求两个数的最小公倍数

## 题目描述
求两个正整数的最小公倍数。

## 输入格式
一行输入两个正整数 `a b`。

## 输出格式
输出 `lcm(a,b)`。

## 数据范围
`1 ≤ a,b ≤ 10^9`。',
  '简单', '["数学","最大公约数","整数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12 18', '36',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 5', '35',
  '互质'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 4', '8',
  '整除'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '素数判断', '# 素数判断

## 题目描述
判断给定正整数是否为素数。

## 输入格式
输入整数 `n`。

## 输出格式
若为素数输出 `YES`，否则输出 `NO`。

## 数据范围
`1 ≤ n ≤ 10^9`。',
  '简单', '["数学","质数","循环"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', 'YES',
  '最小素数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '97', 'YES',
  '素数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100', 'NO',
  '合数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间内素数个数', '# 区间内素数个数

## 题目描述
统计闭区间 `[L,R]` 中素数的个数。

## 输入格式
一行输入两个整数 `L R`。

## 输出格式
输出素数数量。

## 数据范围
`1 ≤ L ≤ R ≤ 10^6`。',
  '中等', '["数学","质数","筛法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 10', '4',
  '2,3,5,7'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 20', '4',
  '11,13,17,19'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '斐波那契数列第 N 项', '# 斐波那契数列第 N 项

## 题目描述
定义 `F0=0, F1=1, Fn=F(n-1)+F(n-2)`，求第 `N` 项。

## 输入格式
输入整数 `N`。

## 输出格式
输出 `F_N`。

## 数据范围
`0 ≤ N ≤ 90`。',
  '简单', '["循环","斐波那契","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '边界'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10', '55',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '20', '6765',
  '较大'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计 1 到 N 中 3 的倍数', '# 统计 1 到 N 中 3 的倍数

## 题目描述
统计 `1..N` 中能被 3 整除的整数个数。

## 输入格式
输入正整数 `N`。

## 输出格式
输出个数。

## 数据范围
`1 ≤ N ≤ 10^18`。',
  '简单', '["循环","数学","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10', '3',
  '3,6,9'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3', '1',
  '边界'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100', '33',
  '较大'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数字三角形输出', '# 数字三角形输出

## 题目描述
输入 `N`，输出 N 行数字三角形。第 i 行输出 i 个数字 i，以单个空格分隔。

## 输入格式
输入正整数 `N`。

## 输出格式
输出 N 行。

## 数据范围
`1 ≤ N ≤ 20`。',
  '简单', '["循环","嵌套循环","输出格式"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3', '1
2 2
3 3 3',
  '三行'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '单行'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '求区间整数平均值', '# 求区间整数平均值

## 题目描述
给定 `L` 与 `R`，求闭区间内所有整数的平均值。

## 输入格式
一行输入两个整数 `L R`。

## 输出格式
输出平均值，保留两位小数。

## 数据范围
`-10^9 ≤ L ≤ R ≤ 10^9`。',
  '简单', '["循环","浮点数","平均值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 5', '3.00',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-3 3', '0.00',
  '对称区间'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 3', '2.50',
  '小数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '找零钱最少硬币数', '# 找零钱最少硬币数

## 题目描述
只使用面值 100、50、20、10、5、1 的硬币，对给定正整数金额找零，求最少硬币数。

## 输入格式
输入整数金额 `x`。

## 输出格式
输出最少硬币数。

## 数据范围
`0 ≤ x ≤ 10^9`。',
  '简单', '["贪心","数学","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零金额'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '186', '6',
  '100+50+20+10+5+1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '99', '7',
  '50+20+20+5+1+1+1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '判断三角形合法性', '# 判断三角形合法性

## 题目描述
给定三条正整数边长，判断能否组成三角形。

## 输入格式
输入 `a b c`。

## 输出格式
可以输出 `YES`，否则输出 `NO`。

## 数据范围
`1 ≤ a,b,c ≤ 10^9`。',
  '简单', '["条件判断","几何","数学"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4 5', 'YES',
  '直角三角形'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2 3', 'NO',
  '退化'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5 9', 'YES',
  '等腰'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '三角形类型判定', '# 三角形类型判定

## 题目描述
给定可组成三角形的三条边，按边分类：三边相等输出 `EQUILATERAL`；两边相等输出 `ISOSCELES`；否则输出 `SCALENE`。

## 输入格式
输入 `a b c`。

## 输出格式
输出分类字符串。

## 数据范围
`1 ≤ a,b,c ≤ 10^9`，且保证能组成三角形。',
  '简单', '["条件判断","几何","排序"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3 3', 'EQUILATERAL',
  '等边'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3 4', 'ISOSCELES',
  '等腰'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4 5', 'SCALENE',
  '不等边'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '分段函数计算', '# 分段函数计算

## 题目描述
计算分段函数：当 `x<0` 时 `f(x)=x^2`；当 `x=0` 时 `f(x)=0`；当 `x>0` 时 `f(x)=2x+1`。

## 输入格式
输入整数 `x`。

## 输出格式
输出整数 `f(x)`。

## 数据范围
`-10^9 ≤ x ≤ 10^9`。',
  '简单', '["条件判断","数学","分支"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '-3', '9',
  '负数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5', '11',
  '正数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '时间换算为秒', '# 时间换算为秒

## 题目描述
输入小时、分钟、秒，计算从当天 00:00:00 起经过的总秒数。

## 输入格式
一行输入 `h m s`。

## 输出格式
输出总秒数。

## 数据范围
`0≤h≤23, 0≤m,s≤59`。',
  '简单', '["基础语法","时间","算术"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2 3', '3723',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0 0 0', '0',
  '午夜'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '23 59 59', '86399',
  '一天末尾'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组元素求和', '# 数组元素求和

## 题目描述
给定 N 个整数，求它们的总和。

## 输入格式
第一行输入 `N`，第二行输入 N 个整数。

## 输出格式
输出总和。

## 数据范围
`1≤N≤2×10^5`，元素绝对值不超过 `10^9`。',
  '简单', '["数组","循环","基础语法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5', '15',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
-1 2 -3 4', '2',
  '含负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组最大值与位置', '# 数组最大值与位置

## 题目描述
给定 N 个整数，输出最大值以及它第一次出现的 1-based 位置。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出 `max pos`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","遍历","最大值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 7 3 7 2', '7 2',
  '重复最大值'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
-5 -2 -9', '-2 2',
  '全负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组最小值与位置', '# 数组最小值与位置

## 题目描述
给定 N 个整数，输出最小值以及它第一次出现的 1-based 位置。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出 `min pos`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","遍历","最小值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
3 1 4 1 5', '1 2',
  '重复最小值'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
8 9', '8 1',
  '首位'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计正负零', '# 统计正负零

## 题目描述
统计数组中正数、负数和零的个数。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出三个整数 `positive negative zero`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","计数","遍历"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
-1 0 3 4 0 -2', '2 2 2',
  '均有'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2 3', '3 0 0',
  '全正'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组逆序输出', '# 数组逆序输出

## 题目描述
将输入数组按逆序输出。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出逆序后的 N 个整数，空格分隔。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","遍历","反转"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5', '5 4 3 2 1',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
9', '9',
  '单元素'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '删除数组中的指定值', '# 删除数组中的指定值

## 题目描述
给定数组和整数 x，删除所有等于 x 的元素并保持其余元素原顺序。

## 输入格式
第一行 `N x`，第二行 N 个整数。

## 输出格式
第一行输出剩余元素个数；第二行输出剩余元素，若为空则输出空行。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","过滤","双指针"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2
1 2 3 2 4', '3
1 3 4',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 7
7 7 7', '0
',
  '全部删除'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组去重保序', '# 数组去重保序

## 题目描述
删除数组中的重复元素，只保留每个值第一次出现的位置。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出去重后的元素，空格分隔。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","哈希集合","去重"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 1 3 2 4 4', '1 2 3 4',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
5 5 5 5', '5',
  '全相同'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '第二大不同元素', '# 第二大不同元素

## 题目描述
找出数组中的第二大不同元素。若不存在，输出 `NONE`。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出第二大不同值或 `NONE`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","最大值","遍历"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
3 5 1 5 4', '4',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
7 7 7', 'NONE',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组是否严格递增', '# 数组是否严格递增

## 题目描述
判断数组是否严格递增。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
若严格递增输出 `YES`，否则输出 `NO`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","遍历","有序性"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 7 9', 'YES',
  '递增'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 2 3', 'NO',
  '有相等'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '相邻元素最大差', '# 相邻元素最大差

## 题目描述
给定数组，求所有相邻元素绝对差的最大值。N=1 时答案为 0。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出最大相邻绝对差。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","遍历","绝对值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 5 2 8 7', '6',
  '|2-8|'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
10', '0',
  '单元素'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '前缀和查询', '# 前缀和查询

## 题目描述
给定长度 N 的数组和 Q 次查询，每次询问闭区间 `[l,r]` 的元素和。

## 输入格式
第一行 `N Q`；第二行 N 个整数；接下来 Q 行每行 `l r`，下标从 1 开始。

## 输出格式
每个查询输出一行区间和。

## 数据范围
`1≤N,Q≤2×10^5`。',
  '中等', '["数组","前缀和","区间查询"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 2 3 4 5
1 3
2 5
4 4', '6
14
4',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间增量后的数组', '# 区间增量后的数组

## 题目描述
初始数组全为 0。执行 Q 次操作，每次给区间 `[l,r]` 的所有元素加上整数 v，最后输出数组。

## 输入格式
第一行 `N Q`；之后 Q 行 `l r v`。

## 输出格式
输出最终 N 个整数。

## 数据范围
`1≤N,Q≤2×10^5`，`|v|≤10^9`。',
  '中等', '["数组","差分","区间修改"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 3 2
2 5 1
4 4 -3', '2 3 3 -2 1',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '移动零到末尾', '# 移动零到末尾

## 题目描述
将数组中的所有 0 移到末尾，同时保持非零元素的相对顺序。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出处理后的数组。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","双指针","稳定移动"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
0 1 0 3 12 0', '1 3 12 0 0 0',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2 3', '1 2 3',
  '无零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '合并两个有序数组', '# 合并两个有序数组

## 题目描述
给定两个非递减数组，将它们合并为一个非递减数组。

## 输入格式
第一行 `N M`；第二行 N 个整数；第三行 M 个整数。

## 输出格式
输出合并后的数组。

## 数据范围
`0≤N,M≤2×10^5` 且 `N+M≥1`。',
  '简单', '["数组","双指针","归并"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
1 3 5
2 3 4 8', '1 2 3 3 4 5 8',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0 3

1 2 2', '1 2 2',
  '一侧为空'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组循环右移 K 位', '# 数组循环右移 K 位

## 题目描述
将数组循环右移 K 位。例如 `[1,2,3,4,5]` 右移 2 位后为 `[4,5,1,2,3]`。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出右移后的数组。

## 数据范围
`1≤N≤2×10^5, 0≤K≤10^18`。',
  '简单', '["数组","模拟","取模"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2
1 2 3 4 5', '4 5 1 2 3',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
7 8 9', '9 7 8',
  'K大于N'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '奇偶下标元素和', '# 奇偶下标元素和

## 题目描述
下标从 1 开始，分别计算奇数下标元素之和与偶数下标元素之和。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出 `odd_sum even_sum`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","下标","遍历"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5', '9 6',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
10 -10', '10 -10',
  '两项'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组中出现次数最多的数', '# 数组中出现次数最多的数

## 题目描述
找出出现次数最多的整数；若有多个并列，输出数值最小的那个。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出 `value count`。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["数组","哈希表","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 2 3 3 3 2', '2 3',
  '并列取小'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
5 5 6 7', '5 2',
  '唯一'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '两数之和是否存在', '# 两数之和是否存在

## 题目描述
给定数组和目标值 T，判断是否存在两个不同位置的元素之和等于 T。

## 输入格式
第一行 `N T`；第二行 N 个整数。

## 输出格式
存在输出 `YES`，否则输出 `NO`。

## 数据范围
`2≤N≤2×10^5`。',
  '简单', '["数组","哈希表","双指针"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 9
2 7 11 15', 'YES',
  '2+7'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 10
1 2 3', 'NO',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '两数之和下标', '# 两数之和下标

## 题目描述
给定数组和目标值 T，保证恰好存在一组答案。输出两个元素的 1-based 下标，要求较小下标在前。

## 输入格式
第一行 `N T`；第二行 N 个整数。

## 输出格式
输出两个下标。

## 数据范围
`2≤N≤2×10^5`。',
  '中等', '["数组","哈希表","索引"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 9
2 7 11 15', '1 2',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 6
3 2 4 8 1', '2 3',
  '2+4'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长连续相同元素段', '# 最长连续相同元素段

## 题目描述
求数组中最长的连续相同元素段长度。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出最长长度。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["数组","扫描","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8
1 1 2 2 2 3 3 2', '3',
  '连续三个2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
5 5 5 5', '4',
  '全相同'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '连续子数组最大和', '# 连续子数组最大和

## 题目描述
求非空连续子数组的最大元素和。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出最大连续子数组和。

## 数据范围
`1≤N≤2×10^5`，元素绝对值不超过 `10^9`。',
  '中等', '["数组","动态规划","Kadane"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9
-2 1 -3 4 -1 2 1 -5 4', '6',
  '4,-1,2,1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
-5 -2 -7 -3', '-2',
  '全负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '固定长度窗口最大和', '# 固定长度窗口最大和

## 题目描述
给定长度 N 的数组和整数 K，求长度恰好为 K 的连续子数组最大和。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出最大和。

## 数据范围
`1≤K≤N≤2×10^5`。',
  '中等', '["数组","滑动窗口","前缀和"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 3
1 5 2 3 7 1', '12',
  '2+3+7'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4
-1 2 3 -2', '2',
  '全数组'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计逆序对', '# 统计逆序对

## 题目描述
若 `i<j` 且 `a[i]>a[j]`，则 `(i,j)` 是一个逆序对。求逆序对总数。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出逆序对数量。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["数组","归并排序","分治"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 4 1 3 5', '3',
  '(2,1)(4,1)(4,3)'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
3 2 1', '3',
  '完全逆序'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数组中的多数元素', '# 数组中的多数元素

## 题目描述
给定数组，保证存在一个元素出现次数严格超过 `N/2`，输出它。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出多数元素。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["数组","Boyer-Moore","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
2 2 1 1 1 2 2', '2',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
9', '9',
  '单元素'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最短无序连续子数组', '# 最短无序连续子数组

## 题目描述
找出最短连续子数组，使得只要对该子数组排序，整个数组就会非递减。已经有序则输出 0。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出最短长度。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["数组","排序","双向扫描"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
2 6 4 8 10 9 15', '5',
  '6,4,8,10,9'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5', '0',
  '已排序'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符串长度', '# 字符串长度

## 题目描述
输入一行字符串，输出其字符数量。测试数据仅包含 ASCII 可见字符且不含首尾空格。

## 输入格式
输入一行字符串。

## 输出格式
输出长度。

## 数据范围
长度 `0..10^6`。',
  '简单', '["字符串","基础语法","输入输出"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello', '5',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'A B C', '5',
  '包含空格'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符串反转', '# 字符串反转

## 题目描述
输入一行字符串，输出其反转结果。

## 输入格式
输入一行 ASCII 字符串。

## 输出格式
输出反转后的字符串。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","遍历","反转"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcde', 'edcba',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a b', 'b a',
  '含空格'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '回文字符串判断', '# 回文字符串判断

## 题目描述
判断字符串是否为回文，区分大小写。

## 输入格式
输入一个不含空格的字符串。

## 输出格式
是输出 `YES`，否则输出 `NO`。

## 数据范围
长度 `1..10^6`。',
  '简单', '["字符串","双指针","回文"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'level', 'YES',
  '回文'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'Level', 'NO',
  '大小写不同'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '忽略大小写的回文判断', '# 忽略大小写的回文判断

## 题目描述
判断字符串是否为回文，比较时忽略英文字母大小写。

## 输入格式
输入一个只含英文字母的字符串。

## 输出格式
是输出 `YES`，否则输出 `NO`。

## 数据范围
长度 `1..10^6`。',
  '简单', '["字符串","双指针","大小写"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'Level', 'YES',
  '忽略大小写'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'OpenAI', 'NO',
  '非回文'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计元音字母', '# 统计元音字母

## 题目描述
统计字符串中英文字母 `a,e,i,o,u` 的出现次数，忽略大小写。

## 输入格式
输入一行字符串。

## 输出格式
输出元音总数。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","计数","字符"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'Hello World', '3',
  'e,o,o'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'rhythm', '0',
  '无元音'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计字符种类数', '# 统计字符种类数

## 题目描述
统计字符串中不同 ASCII 字符的种类数。

## 输入格式
输入一行字符串。

## 输出格式
输出不同字符数量。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","集合","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abca', '3',
  'a,b,c'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaa', '1',
  '一种'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符出现次数', '# 字符出现次数

## 题目描述
给定字符串 S 和单个字符 c，统计 c 在 S 中出现的次数。

## 输入格式
第一行字符串 S；第二行字符 c。

## 输出格式
输出次数。

## 数据范围
S 长度不超过 `10^6`。',
  '简单', '["字符串","计数","字符"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'banana
a', '3',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'Hello
l', '2',
  '字符l'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '删除字符串中的空格', '# 删除字符串中的空格

## 题目描述
删除输入字符串中的所有普通空格字符 `'' ''`。

## 输入格式
输入一行字符串。

## 输出格式
输出删除空格后的字符串。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","过滤","字符"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a b  c', 'abc',
  '多个空格'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello', 'hello',
  '无空格'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '单词数量统计', '# 单词数量统计

## 题目描述
统计一行英文文本中的单词数量。单词由连续非空格字符组成，可能有多个连续空格。

## 输入格式
输入一行字符串。

## 输出格式
输出单词数量。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","分词","扫描"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello world', '2',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '  one   two three  ', '3',
  '多空格'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长单词', '# 最长单词

## 题目描述
输入一行仅由英文单词和空格组成的文本，输出最长单词；若并列，输出最先出现的。

## 输入格式
输入一行文本。

## 输出格式
输出最长单词。

## 数据范围
文本长度不超过 `10^6`。',
  '简单', '["字符串","分词","扫描"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'I love programming', 'programming',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aa b cc', 'aa',
  '并列取先'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '大小写转换', '# 大小写转换

## 题目描述
将字符串中的小写英文字母转为大写，大写转为小写，其他字符保持不变。

## 输入格式
输入一行字符串。

## 输出格式
输出转换结果。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","字符处理","ASCII"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'Hello123', 'hELLO123',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aBc!', 'AbC!',
  '含符号'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '首字母大写', '# 首字母大写

## 题目描述
将英文句子中每个单词的第一个字母转换为大写，其余字符保持不变。单词由空格分隔。

## 输入格式
输入一行字符串。

## 输出格式
输出处理后的字符串。

## 数据范围
长度不超过 `10^6`。',
  '简单', '["字符串","分词","字符处理"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello world', 'Hello World',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'java python c', 'Java Python C',
  '多单词'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符串压缩计数', '# 字符串压缩计数

## 题目描述
对字符串做连续字符计数压缩，例如 `aaabbc` 变为 `a3b2c1`。

## 输入格式
输入一个不含空格的字符串 S。

## 输出格式
输出压缩结果。

## 数据范围
`1≤|S|≤10^6`。',
  '中等', '["字符串","扫描","编码"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaabbc', 'a3b2c1',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcd', 'a1b1c1d1',
  '无连续重复'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '解压缩计数字符串', '# 解压缩计数字符串

## 题目描述
输入按 `字符+正整数次数` 组成的压缩串，将其解压。例如 `a3b2c1` 变为 `aaabbc`。次数可能是多位数。

## 输入格式
输入一个合法压缩串。

## 输出格式
输出解压后的字符串。

## 数据范围
解压后长度不超过 `10^6`。',
  '中等', '["字符串","解析","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a3b2c1', 'aaabbc',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'x10', 'xxxxxxxxxx',
  '多位次数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '判断两个字符串是否为字母异位词', '# 判断两个字符串是否为字母异位词

## 题目描述
判断两个只含小写字母的字符串是否由完全相同数量的字母组成。

## 输入格式
输入两行字符串 S 和 T。

## 输出格式
是输出 `YES`，否则输出 `NO`。

## 数据范围
长度均不超过 `10^6`。',
  '简单', '["字符串","哈希表","排序"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'listen
silent', 'YES',
  '异位词'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'apple
appeal', 'NO',
  '不同'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '第一个只出现一次的字符', '# 第一个只出现一次的字符

## 题目描述
找出字符串中第一个只出现一次的字符。不存在则输出 `NONE`。

## 输入格式
输入一个不含空格的字符串。

## 输出格式
输出字符或 `NONE`。

## 数据范围
长度不超过 `10^6`。',
  '中等', '["字符串","哈希表","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'swiss', 'w',
  'w最先唯一'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aabb', 'NONE',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长公共前缀', '# 最长公共前缀

## 题目描述
给定 N 个字符串，求它们的最长公共前缀。若不存在，输出空行。

## 输入格式
第一行 N，之后 N 行每行一个字符串。

## 输出格式
输出最长公共前缀。

## 数据范围
`1≤N≤10^5`，总字符数不超过 `10^6`。',
  '中等', '["字符串","数组","扫描"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
flower
flow
flight', 'fl',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
dog
cat', '',
  '无公共前缀'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '子串出现次数（允许重叠）', '# 子串出现次数（允许重叠）

## 题目描述
统计模式串 P 在文本串 S 中出现的次数，允许重叠。

## 输入格式
第一行 S，第二行 P。

## 输出格式
输出出现次数。

## 数据范围
`1≤|P|≤|S|≤10^6`。',
  '中等', '["字符串","匹配","KMP"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaaa
aa', '4',
  '重叠'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcabcabc
abc', '3',
  '多次'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长无重复字符子串', '# 最长无重复字符子串

## 题目描述
求字符串中不含重复字符的最长连续子串长度。

## 输入格式
输入一个 ASCII 字符串 S。

## 输出格式
输出最大长度。

## 数据范围
`1≤|S|≤10^6`。',
  '中等', '["字符串","滑动窗口","哈希表"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcabcbb', '3',
  'abc'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'bbbbb', '1',
  '单字符'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '括号字符串合法性', '# 括号字符串合法性

## 题目描述
输入仅由 `()[]{}` 构成的字符串，判断括号是否正确匹配。

## 输入格式
输入字符串 S。

## 输出格式
合法输出 `YES`，否则输出 `NO`。

## 数据范围
`1≤|S|≤10^6`。',
  '简单', '["字符串","栈","括号匹配"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '([]{})', 'YES',
  '合法'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '([)]', 'NO',
  '交叉'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '移除相邻重复字符', '# 移除相邻重复字符

## 题目描述
不断删除相邻且相同的一对字符，直到不能删除，输出最终字符串。若为空输出 `EMPTY`。

## 输入格式
输入一个不含空格的字符串。

## 输出格式
输出最终结果。

## 数据范围
`1≤|S|≤10^6`。',
  '中等', '["字符串","栈","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abbaca', 'ca',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'azxxzy', 'ay',
  '连锁删除'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符串循环左移', '# 字符串循环左移

## 题目描述
将字符串循环左移 K 位。

## 输入格式
第一行字符串 S；第二行整数 K。

## 输出格式
输出结果。

## 数据范围
`1≤|S|≤10^6, 0≤K≤10^18`。',
  '简单', '["字符串","模拟","取模"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcdef
2', 'cdefab',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abc
4', 'bca',
  'K大于长度'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '反转句子中的单词顺序', '# 反转句子中的单词顺序

## 题目描述
给定由单个空格分隔的英文单词序列，反转单词顺序。

## 输入格式
输入一行句子。

## 输出格式
输出反转后的句子。

## 数据范围
总长度不超过 `10^6`。',
  '中等', '["字符串","分词","反转"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'I love coding', 'coding love I',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello', 'hello',
  '单词'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '字符串最小表示', '# 字符串最小表示

## 题目描述
给定字符串 S，把它看作环。对所有循环移位结果，输出字典序最小的那个。

## 输入格式
输入一个只含小写字母的字符串 S。

## 输出格式
输出字典序最小循环表示。

## 数据范围
`1≤|S|≤2×10^5`。',
  '困难', '["字符串","循环字符串","双指针"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'baca', 'abac',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaa', 'aaaa',
  '全相同'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长回文子串长度', '# 最长回文子串长度

## 题目描述
求字符串中最长回文子串的长度。

## 输入格式
输入一个不含空格的字符串 S。

## 输出格式
输出最大长度。

## 数据范围
`1≤|S|≤5000`。',
  '中等', '["字符串","回文","中心扩展"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'babad', '3',
  'bab或aba'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'cbbd', '2',
  'bb'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '快速幂', '# 快速幂

## 题目描述
计算 `a^b mod m`。

## 输入格式
输入三个非负整数 `a b m`。

## 输出格式
输出结果。

## 数据范围
`0≤a≤10^18, 0≤b≤10^18, 1≤m≤10^18`。',
  '中等', '["数学","快速幂","模运算"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 10 1000', '24',
  '1024 mod 1000'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 0 7', '1',
  '零次幂'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '质因数分解', '# 质因数分解

## 题目描述
将正整数 N 分解为质因数乘积，并按从小到大输出所有质因数，重复出现。

## 输入格式
输入整数 N。

## 输出格式
输出质因数序列，空格分隔；若 N=1 输出 `1`。

## 数据范围
`1≤N≤10^12`。',
  '中等', '["数学","质因数","枚举"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '60', '2 2 3 5',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '13', '13',
  '质数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '约数个数', '# 约数个数

## 题目描述
求正整数 N 的正约数个数。

## 输入格式
输入 N。

## 输出格式
输出约数数量。

## 数据范围
`1≤N≤10^12`。',
  '中等', '["数学","质因数分解","约数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12', '6',
  '1,2,3,4,6,12'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '13', '2',
  '质数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '约数之和', '# 约数之和

## 题目描述
求正整数 N 的所有正约数之和。

## 输入格式
输入 N。

## 输出格式
输出约数和。

## 数据范围
`1≤N≤10^9`。',
  '中等', '["数学","约数","枚举"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12', '28',
  '1+2+3+4+6+12'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '欧拉函数', '# 欧拉函数

## 题目描述
求 `1..N` 中与 N 互质的整数个数 `φ(N)`。

## 输入格式
输入正整数 N。

## 输出格式
输出 `φ(N)`。

## 数据范围
`1≤N≤10^12`。',
  '中等', '["数学","数论","欧拉函数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9', '6',
  '1,2,4,5,7,8'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '定义'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '组合数 C(n,k)', '# 组合数 C(n,k)

## 题目描述
计算组合数 `C(n,k)`。

## 输入格式
输入 `n k`。

## 输出格式
输出精确值。

## 数据范围
`0≤k≤n≤60`。',
  '中等', '["数学","组合数学","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2', '10',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 0', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '组合数取模', '# 组合数取模

## 题目描述
计算 `C(n,k) mod 1000000007`。

## 输入格式
输入 `n k`。

## 输出格式
输出结果。

## 数据范围
`0≤k≤n≤10^6`。',
  '困难', '["数学","组合数学","模逆元"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2', '10',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1000000 0', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '杨辉三角第 N 行', '# 杨辉三角第 N 行

## 题目描述
输出杨辉三角第 N 行（从第 0 行开始）。

## 输入格式
输入整数 N。

## 输出格式
输出 `C(N,0)` 到 `C(N,N)`，空格分隔。

## 数据范围
`0≤N≤30`。',
  '简单', '["数学","组合","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4', '1 4 6 4 1',
  '第4行'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '1',
  '第0行'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '进制转换：十进制转二进制', '# 进制转换：十进制转二进制

## 题目描述
将非负十进制整数转换为二进制表示。

## 输入格式
输入非负整数 N。

## 输出格式
输出二进制字符串。

## 数据范围
`0≤N≤10^18`。',
  '简单', '["数学","进制转换","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10', '1010',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '进制转换：二进制转十进制', '# 进制转换：二进制转十进制

## 题目描述
将二进制字符串转换为十进制整数。

## 输入格式
输入一个二进制字符串 S。

## 输出格式
输出十进制值。

## 数据范围
`1≤|S|≤60`。',
  '简单', '["数学","进制转换","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1010', '10',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '任意进制转十进制', '# 任意进制转十进制

## 题目描述
给定 2~16 进制的非负整数，转换为十进制。数字字符使用 `0-9A-F`。

## 输入格式
第一行输入进制 B，第二行输入字符串 S。

## 输出格式
输出十进制值。

## 数据范围
`2≤B≤16`，转换结果不超过 `10^18`。',
  '中等', '["数学","进制转换","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '16
FF', '255',
  '十六进制'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
1111', '15',
  '二进制'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '十进制转任意进制', '# 十进制转任意进制

## 题目描述
将非负十进制整数转为 B 进制，B 为 2~16，数字字符使用大写 `A-F`。

## 输入格式
输入 `N B`。

## 输出格式
输出 B 进制字符串。

## 数据范围
`0≤N≤10^18, 2≤B≤16`。',
  '中等', '["数学","进制转换","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '255 16', 'FF',
  '十六进制'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '15 2', '1111',
  '二进制'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最大公约数序列', '# 最大公约数序列

## 题目描述
给定 N 个正整数，求它们整体的最大公约数。

## 输入格式
第一行 N，第二行 N 个正整数。

## 输出格式
输出最大公约数。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["数学","GCD","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
12 18 24 30', '6',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
7 11 13', '1',
  '互质'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小公倍数序列', '# 最小公倍数序列

## 题目描述
给定 N 个正整数，求它们整体的最小公倍数。保证答案不超过 `10^18`。

## 输入格式
第一行 N，第二行 N 个正整数。

## 输出格式
输出最小公倍数。

## 数据范围
`1≤N≤10^5`。',
  '中等', '["数学","LCM","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
2 3 4', '12',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
6 8', '24',
  '两数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '完全数判断', '# 完全数判断

## 题目描述
一个正整数若等于其所有真因子（不含自身）之和，则称为完全数。判断 N 是否为完全数。

## 输入格式
输入正整数 N。

## 输出格式
是输出 `YES`，否则输出 `NO`。

## 数据范围
`1≤N≤10^9`。',
  '简单', '["数学","约数","枚举"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6', 'YES',
  '1+2+3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '28', 'YES',
  '经典完全数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12', 'NO',
  '不是'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '阿姆斯特朗数判断', '# 阿姆斯特朗数判断

## 题目描述
设 N 的十进制位数为 k。若 N 等于其每一位数字的 k 次方之和，则称为阿姆斯特朗数。判断 N。

## 输入格式
输入非负整数 N。

## 输出格式
是输出 `YES`，否则输出 `NO`。

## 数据范围
`0≤N≤10^9`。',
  '简单', '["数学","数位","幂"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '153', 'YES',
  '1^3+5^3+3^3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9474', 'YES',
  '四位'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '123', 'NO',
  '否'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '连续整数求和表示数', '# 连续整数求和表示数

## 题目描述
统计正整数 N 能表示为一个或多个连续正整数之和的方案数。

## 输入格式
输入正整数 N。

## 输出格式
输出方案数。

## 数据范围
`1≤N≤10^12`。',
  '中等', '["数学","枚举","前缀思想"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '15', '4',
  '15,7+8,4+5+6,1+2+3+4+5'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '9', '3',
  '9,4+5,2+3+4'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '鸡兔同笼', '# 鸡兔同笼

## 题目描述
笼中有鸡和兔共 H 个头、F 只脚，求鸡和兔各多少只。若无非负整数解输出 `NO`。

## 输入格式
输入 `H F`。

## 输出格式
有解输出 `chicken rabbit`，否则输出 `NO`。

## 数据范围
`0≤H≤10^9, 0≤F≤4×10^9`。',
  '简单', '["数学","方程","枚举"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '35 94', '23 12',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 3', 'NO',
  '无解'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '解一元二次方程的判别式', '# 解一元二次方程的判别式

## 题目描述
给定整数 a,b,c 且 a≠0，计算判别式 `D=b^2-4ac`，判断实根数量。

## 输入格式
输入 `a b c`。

## 输出格式
若 D>0 输出 `2`，D=0 输出 `1`，D<0 输出 `0`。

## 数据范围
`|a|,|b|,|c|≤10^9`。',
  '简单', '["数学","方程","判别式"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 -3 2', '2',
  '两个实根'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2 1', '1',
  '重根'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0 1', '0',
  '无实根'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '矩阵乘法', '# 矩阵乘法

## 题目描述
计算矩阵 A(N×M) 与 B(M×K) 的乘积 C。

## 输入格式
第一行 `N M K`；接下来 N 行是 A；再接下来 M 行是 B。

## 输出格式
输出 N 行，每行 K 个整数。

## 数据范围
`1≤N,M,K≤100`，元素绝对值不超过 1000。',
  '中等', '["数学","矩阵","三重循环"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2 2
1 2
3 4
5 6
7 8', '19 22
43 50',
  '2x2'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '升序排序', '# 升序排序

## 题目描述
将 N 个整数按非递减顺序输出。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出排序后的数组。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["排序","数组","基础算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
5 2 3 1 4', '1 2 3 4 5',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
2 2 -1 3', '-1 2 2 3',
  '重复与负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '降序排序', '# 降序排序

## 题目描述
将 N 个整数按非递增顺序输出。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出排序后的数组。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["排序","数组","基础算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
5 2 3 1 4', '5 4 3 2 1',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
-1 -3 -2', '-1 -2 -3',
  '负数'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '按绝对值排序', '# 按绝对值排序

## 题目描述
按绝对值从小到大排序；绝对值相同时按原值从小到大。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出排序结果。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["排序","自定义比较","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
-3 1 -1 2 -2 0', '0 -1 1 -2 2 -3',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '学生成绩排序', '# 学生成绩排序

## 题目描述
给定学生姓名和成绩，按成绩降序；成绩相同按姓名字典序升序。

## 输入格式
第一行 N；接下来 N 行 `name score`。

## 输出格式
按排序后顺序每行输出 `name score`。

## 数据范围
`1≤N≤10^5`，姓名仅含英文字母。',
  '简单', '["排序","结构体","多关键字"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
Tom 90
Amy 95
Bob 90
Ann 95', 'Amy 95
Ann 95
Bob 90
Tom 90',
  '多关键字'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '第 K 小元素', '# 第 K 小元素

## 题目描述
给定 N 个整数，求第 K 小的元素（重复元素按出现次数计）。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出第 K 小值。

## 数据范围
`1≤K≤N≤2×10^5`。',
  '中等', '["排序","选择算法","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
4 1 2 2 9', '2',
  '重复'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1
7 8 9', '7',
  '最小'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '第 K 大不同元素', '# 第 K 大不同元素

## 题目描述
给定数组，去重后求第 K 大元素。若不同元素不足 K 个，输出 `NONE`。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出答案或 `NONE`。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["排序","集合","选择"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
5 1 5 3 3 2', '3',
  '不同值5,3,2,1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 1 2', 'NONE',
  '不足'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二分查找是否存在', '# 二分查找是否存在

## 题目描述
给定非递减数组和 Q 个查询，判断每个目标值是否存在。

## 输入格式
第一行 `N Q`；第二行 N 个整数；之后 Q 行每行一个 x。

## 输出格式
每个查询输出 `YES` 或 `NO`。

## 数据范围
`1≤N,Q≤2×10^5`。',
  '简单', '["二分查找","有序数组","搜索"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 3 5 7 9
3
4
9', 'YES
NO
YES',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二分查找第一个位置', '# 二分查找第一个位置

## 题目描述
给定非递减数组与目标 x，输出 x 第一次出现的 1-based 下标；不存在输出 -1。

## 输入格式
第一行 `N x`；第二行 N 个整数。

## 输出格式
输出位置或 -1。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二分查找","有序数组","lower_bound"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
1 2 2 2 3 4', '2',
  '重复'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 5
1 2 3', '-1',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二分查找最后一个位置', '# 二分查找最后一个位置

## 题目描述
给定非递减数组与目标 x，输出 x 最后一次出现的 1-based 下标；不存在输出 -1。

## 输入格式
第一行 `N x`；第二行 N 个整数。

## 输出格式
输出位置或 -1。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二分查找","有序数组","upper_bound"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
1 2 2 2 3 4', '4',
  '重复'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 5
1 2 3', '-1',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '统计目标值出现次数', '# 统计目标值出现次数

## 题目描述
给定非递减数组与目标 x，统计 x 的出现次数。

## 输入格式
第一行 `N x`；第二行 N 个整数。

## 输出格式
输出次数。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二分查找","有序数组","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 2
1 2 2 2 3 4 5', '3',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 9
1 2 3', '0',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '搜索插入位置', '# 搜索插入位置

## 题目描述
给定严格递增数组和目标值 x，若 x 存在则输出其 0-based 下标；否则输出应插入的位置。

## 输入格式
第一行 `N x`；第二行 N 个整数。

## 输出格式
输出 0-based 位置。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["二分查找","有序数组","lower_bound"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 3 5 6', '2',
  '存在'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2
1 3 5 6', '1',
  '插入'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '旋转数组中的最小值', '# 旋转数组中的最小值

## 题目描述
一个严格递增数组经过若干次循环旋转后得到当前数组，求最小元素。

## 输入格式
第一行 N，第二行 N 个互不相同的整数。

## 输出格式
输出最小值。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二分查找","旋转数组","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
4 5 1 2 3', '1',
  '旋转'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 3 4', '1',
  '未旋转'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '旋转数组查找目标', '# 旋转数组查找目标

## 题目描述
严格递增数组被循环旋转后，给定目标值 x，求其 0-based 下标，不存在输出 -1。

## 输入格式
第一行 `N x`；第二行 N 个互不相同的整数。

## 输出格式
输出下标或 -1。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["二分查找","旋转数组","搜索"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 0
4 5 6 7 0 1 2', '4',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 3
4 5 6 7 0 1 2', '-1',
  '不存在'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '排序后相邻最小差', '# 排序后相邻最小差

## 题目描述
给定 N 个整数，排序后求相邻元素差值的最小值。

## 输入格式
第一行 N，第二行 N 个整数。

## 输出格式
输出最小差。

## 数据范围
`2≤N≤2×10^5`。',
  '简单', '["排序","数组","差值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
8 1 5 3 10', '2',
  '排序后1,3,5,8,10'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
4 4 9', '0',
  '有重复'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间合并', '# 区间合并

## 题目描述
给定 N 个闭区间 `[l,r]`，合并所有重叠或相接的区间，按左端点升序输出。

## 输入格式
第一行 N；接下来 N 行 `l r`。

## 输出格式
第一行输出合并后区间数量，之后每行一个区间。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["排序","区间","贪心"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 3
2 6
8 10
10 12', '2
1 6
8 12',
  '重叠和相接'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '会议室最多安排', '# 会议室最多安排

## 题目描述
给定 N 个会议的开始和结束时间 `[s,e)`，同一会议室最多能安排多少个互不重叠会议。

## 输入格式
第一行 N；之后 N 行 `s e`。

## 输出格式
输出最大会议数。

## 数据范围
`1≤N≤2×10^5, s<e`。',
  '中等', '["排序","贪心","区间调度"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 3
2 5
4 7
6 8', '2',
  '例如1-3与4-7'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2
2 3
3 4', '3',
  '首尾相接'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最少会议室数量', '# 最少会议室数量

## 题目描述
给定 N 个会议区间 `[s,e)`，求全部安排所需的最少会议室数量。

## 输入格式
第一行 N；之后 N 行 `s e`。

## 输出格式
输出最少会议室数。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["排序","优先队列","扫描线"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
0 30
5 10
15 20', '2',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2
2 3
3 4', '1',
  '首尾相接'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '按频率排序', '# 按频率排序

## 题目描述
按元素出现频率降序排序；频率相同按数值升序。重复元素全部保留。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出排序后的数组。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["排序","哈希表","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8
4 4 1 2 2 2 3 3', '2 2 2 3 3 4 4 1',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '荷兰国旗问题', '# 荷兰国旗问题

## 题目描述
数组只含 0、1、2，要求原地思想将其按 0、1、2 排序并输出。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出排序结果。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["排序","双指针","三路划分"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
2 0 2 1 1 0', '0 0 1 1 2 2',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '寻找峰值', '# 寻找峰值

## 题目描述
若元素严格大于其相邻元素则为峰值。边界外视为负无穷。保证相邻元素不相等，输出任意一个峰值的 0-based 下标。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出任意合法峰值下标。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二分查找","数组","局部最优"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 3 1', '2',
  '唯一峰值'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
1 2', '1',
  '边界峰值'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '模拟栈', '# 模拟栈

## 题目描述
实现一个整数栈，支持 `PUSH x`、`POP`、`TOP`、`SIZE`。对空栈 POP/TOP 输出 `EMPTY`。

## 输入格式
第一行 Q；之后 Q 行一个操作。

## 输出格式
对 POP 输出被弹出的值；TOP 输出栈顶；SIZE 输出大小；PUSH 不输出。

## 数据范围
`1≤Q≤2×10^5`。',
  '简单', '["栈","数据结构","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
PUSH 3
PUSH 5
TOP
SIZE
POP
POP
POP', '5
2
5
3
EMPTY',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '模拟队列', '# 模拟队列

## 题目描述
实现整数队列，支持 `PUSH x`、`POP`、`FRONT`、`SIZE`。空队列 POP/FRONT 输出 `EMPTY`。

## 输入格式
第一行 Q；之后 Q 行操作。

## 输出格式
按操作规则输出。

## 数据范围
`1≤Q≤2×10^5`。',
  '简单', '["队列","数据结构","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
PUSH 3
PUSH 5
FRONT
SIZE
POP
POP
POP', '3
2
3
5
EMPTY',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小栈', '# 最小栈

## 题目描述
实现栈，支持 `PUSH x`、`POP`、`MIN`，MIN 返回当前最小值。保证执行 MIN 时栈非空，空栈 POP 输出 `EMPTY`。

## 输入格式
第一行 Q；之后 Q 行操作。

## 输出格式
对 POP 输出弹出值，对 MIN 输出最小值。

## 数据范围
`1≤Q≤2×10^5`。',
  '中等', '["栈","数据结构","最小值"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
PUSH 3
PUSH 5
MIN
PUSH 2
MIN
POP
MIN', '3
2
2
3',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '后缀表达式求值', '# 后缀表达式求值

## 题目描述
计算合法的逆波兰表达式。运算符为 `+ - * /`，除法向零截断。

## 输入格式
第一行 N，第二行 N 个 token，空格分隔。

## 输出格式
输出计算结果。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["栈","表达式","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 1 + 3 *', '9',
  '(2+1)*3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
4 13 5 / +', '6',
  '13/5=2'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '中缀括号表达式求值', '# 中缀括号表达式求值

## 题目描述
计算只包含非负整数、`+ - * /` 和圆括号的合法表达式，忽略空格，整数除法向零截断。

## 输入格式
输入一行表达式。

## 输出格式
输出整数结果。

## 数据范围
表达式长度不超过 `2×10^5`。',
  '困难', '["栈","表达式","解析"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2*(3+4)', '14',
  '括号'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 + 6 / 4', '11',
  '整数除法'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '单调栈：下一个更大元素', '# 单调栈：下一个更大元素

## 题目描述
对数组中每个位置，找到右侧第一个严格大于它的元素值；不存在输出 -1。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出 N 个答案。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["单调栈","数组","数据结构"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
2 1 2 4', '4 2 4 -1',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
3 2 1', '-1 -1 -1',
  '递减'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '单调栈：每日温度', '# 单调栈：每日温度

## 题目描述
给定每天温度，对每一天输出还需等待多少天才会出现更高温度；之后没有更高温度则为 0。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出 N 个整数。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["单调栈","数组","距离"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8
73 74 75 71 69 72 76 73', '1 1 4 2 1 1 0 0',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '滑动窗口最大值', '# 滑动窗口最大值

## 题目描述
给定数组和窗口大小 K，输出每个长度为 K 的窗口中的最大值。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出 `N-K+1` 个最大值。

## 数据范围
`1≤K≤N≤2×10^5`。',
  '困难', '["单调队列","滑动窗口","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 3
1 3 -1 -3 5 3 6 7', '3 3 5 5 6 7',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '滑动窗口最小值', '# 滑动窗口最小值

## 题目描述
给定数组和窗口大小 K，输出每个长度为 K 的窗口中的最小值。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出 `N-K+1` 个最小值。

## 数据范围
`1≤K≤N≤2×10^5`。',
  '困难', '["单调队列","滑动窗口","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 3
1 3 -1 -3 5 3 6 7', '-1 -3 -3 -3 3 3',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'LRU 缓存模拟', '# LRU 缓存模拟

## 题目描述
模拟容量为 C 的 LRU 缓存。操作 `PUT k v` 写入，`GET k` 查询。GET 不存在输出 -1；访问或更新会使键成为最近使用。超容量淘汰最久未使用键。

## 输入格式
第一行 `C Q`；之后 Q 行操作。

## 输出格式
每个 GET 输出一行结果。

## 数据范围
`1≤C≤10^5, 1≤Q≤2×10^5`。',
  '困难', '["哈希表","双向链表","缓存"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 6
PUT 1 1
PUT 2 2
GET 1
PUT 3 3
GET 2
GET 3', '1
-1
3',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '并查集连通性', '# 并查集连通性

## 题目描述
维护 N 个元素的动态集合。`UNION a b` 合并，`ASK a b` 查询是否同一集合。

## 输入格式
第一行 `N Q`；之后 Q 行操作。

## 输出格式
对每个 ASK 输出 `YES` 或 `NO`。

## 数据范围
`1≤N,Q≤2×10^5`。',
  '中等', '["并查集","数据结构","连通性"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5
UNION 1 2
ASK 1 2
ASK 1 3
UNION 2 3
ASK 1 3', 'YES
NO
YES',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '并查集集合数量', '# 并查集集合数量

## 题目描述
初始有 N 个独立集合，执行 Q 次合并后输出剩余集合数量。

## 输入格式
第一行 `N Q`；之后 Q 行 `a b`。

## 输出格式
输出最终集合数量。

## 数据范围
`1≤N,Q≤2×10^5`。',
  '中等', '["并查集","计数","数据结构"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 2
2 3
4 5', '2',
  '两个连通块'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 2
1 1
2 2', '3',
  '无有效合并'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '哈希表键值存取', '# 哈希表键值存取

## 题目描述
实现键值表，支持 `SET key value`、`GET key`、`DEL key`。GET 不存在输出 `NULL`；DEL 无输出。

## 输入格式
第一行 Q；之后 Q 行操作，key 为无空格字符串，value 为整数。

## 输出格式
每个 GET 输出一行。

## 数据范围
`1≤Q≤2×10^5`。',
  '简单', '["哈希表","字典","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
SET a 1
GET a
SET a 2
GET a
DEL a
GET a', '1
2
NULL',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '词频统计', '# 词频统计

## 题目描述
给定 N 个只含小写字母的单词，统计每个不同单词的出现次数，并按单词字典序输出。

## 输入格式
第一行 N；之后 N 行单词。

## 输出格式
每行输出 `word count`。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["哈希表","字符串","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
apple
banana
apple
cat
banana', 'apple 2
banana 2
cat 1',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'Top K 高频元素', '# Top K 高频元素

## 题目描述
给定整数数组，输出出现频率最高的 K 个不同元素。频率相同按数值升序；最终按“频率降序、数值升序”输出。

## 输入格式
第一行 `N K`；第二行 N 个整数。

## 输出格式
输出 K 个整数。

## 数据范围
`1≤K≤不同元素数≤N≤2×10^5`。',
  '中等', '["哈希表","堆","排序"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
1 1 1 2 2 3', '1 2',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 2
4 4 1 1 2 2 3 3', '1 2',
  '并列取数值小'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数据流中第 K 大元素', '# 数据流中第 K 大元素

## 题目描述
维护数据流的第 K 大元素。先给初始数组，之后每次 ADD x 后输出当前第 K 大元素。保证每次查询时元素总数至少 K。

## 输入格式
第一行 `N K Q`；第二行 N 个整数；之后 Q 行 `ADD x`。

## 输出格式
每次 ADD 后输出一行答案。

## 数据范围
`1≤K≤N+Q≤2×10^5`。',
  '困难', '["堆","优先队列","数据流"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3 3
4 5 8 2
ADD 3
ADD 5
ADD 10', '4
5
5',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '合并 K 个有序序列', '# 合并 K 个有序序列

## 题目描述
给定 K 个非递减整数序列，将它们合并成一个非递减序列。

## 输入格式
第一行 K；接下来 K 行，每行先输入长度 L，再输入 L 个整数。

## 输出格式
输出合并后的所有整数。

## 数据范围
总元素数不超过 `2×10^5`。',
  '困难', '["堆","多路归并","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
3 1 4 7
2 2 6
4 0 3 5 8', '0 1 2 3 4 5 6 7 8',
  '三路归并'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '优先队列任务调度', '# 优先队列任务调度

## 题目描述
有 N 个任务，每个任务有优先级 p 和编号 id。按 p 越大优先级越高；p 相同编号越小优先。输出执行顺序。

## 输入格式
第一行 N；之后 N 行 `id p`。

## 输出格式
一行输出任务编号顺序。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["堆","优先队列","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
10 2
3 5
7 5
1 1', '3 7 10 1',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '循环队列报数淘汰', '# 循环队列报数淘汰

## 题目描述
N 个人编号 1..N 围成一圈，从 1 开始报数，每数到 K 的人淘汰，从下一人重新从 1 报数。输出淘汰顺序。

## 输入格式
输入 `N K`。

## 输出格式
输出 N 个编号，空格分隔。

## 数据范围
`1≤N≤10^5, 1≤K≤10^9`。',
  '中等', '["队列","约瑟夫环","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2', '2 4 1 5 3',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1', '1 2 3',
  'K=1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小堆操作', '# 最小堆操作

## 题目描述
支持 `PUSH x`、`TOP`、`POP`。TOP 输出最小值，POP 删除并输出最小值；空堆 TOP/POP 输出 `EMPTY`。

## 输入格式
第一行 Q；之后 Q 行操作。

## 输出格式
按规则输出。

## 数据范围
`1≤Q≤2×10^5`。',
  '中等', '["堆","优先队列","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
PUSH 5
PUSH 2
TOP
POP
POP
POP', '2
2
5
EMPTY',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '递归求和', '# 递归求和

## 题目描述
使用递归思想计算 `1+2+...+N`。判题只检查结果，不限制实现方式。

## 输入格式
输入 N。

## 输出格式
输出总和。

## 数据范围
`1≤N≤10^5`。',
  '简单', '["递归","基础算法","数学"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5', '15',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '递归反转字符串', '# 递归反转字符串

## 题目描述
输出输入字符串的逆序结果。可使用递归实现。

## 输入格式
输入一个不含空格的字符串。

## 输出格式
输出逆序字符串。

## 数据范围
`1≤|S|≤10^4`。',
  '简单', '["递归","字符串","基础算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'hello', 'olleh',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a', 'a',
  '单字符'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '汉诺塔移动次数', '# 汉诺塔移动次数

## 题目描述
给定 N 个盘子，求汉诺塔问题的最少移动次数。

## 输入格式
输入 N。

## 输出格式
输出最少次数。

## 数据范围
`1≤N≤60`。',
  '简单', '["递归","数学","汉诺塔"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '一个盘'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3', '7',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '汉诺塔移动方案', '# 汉诺塔移动方案

## 题目描述
给定 N 个盘子，从柱 A 移到 C，B 为辅助柱。输出最少移动方案，每行格式 `A->C`。

## 输入格式
输入 N。

## 输出格式
输出 `2^N-1` 行移动。

## 数据范围
`1≤N≤15`。',
  '中等', '["递归","汉诺塔","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', 'A->B
A->C
B->C',
  '两个盘'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '生成所有二进制串', '# 生成所有二进制串

## 题目描述
按字典序输出长度 N 的所有二进制串。

## 输入格式
输入 N。

## 输出格式
每行输出一个二进制串。

## 数据范围
`1≤N≤20`。',
  '简单', '["回溯","递归","枚举"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', '00
01
10
11',
  'N=2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '0
1',
  'N=1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '全排列', '# 全排列

## 题目描述
按字典序输出 1..N 的所有排列。

## 输入格式
输入 N。

## 输出格式
每行输出一个排列，数字间空格分隔。

## 数据范围
`1≤N≤8`。',
  '中等', '["回溯","排列","递归"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3', '1 2 3
1 3 2
2 1 3
2 3 1
3 1 2
3 2 1',
  'N=3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '组合枚举', '# 组合枚举

## 题目描述
从 1..N 中选 K 个数，按字典序输出所有组合。

## 输入格式
输入 `N K`。

## 输出格式
每行一个组合。

## 数据范围
`1≤K≤N≤20`。',
  '中等', '["回溯","组合","递归"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2', '1 2
1 3
1 4
2 3
2 4
3 4',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '子集枚举', '# 子集枚举

## 题目描述
按二进制掩码从 0 到 `2^N-1` 的顺序输出集合 `{1..N}` 的所有子集。空集输出 `EMPTY`。

## 输入格式
输入 N。

## 输出格式
每行一个子集，元素递增并用空格分隔。

## 数据范围
`1≤N≤20`。',
  '中等', '["回溯","子集","位运算"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', 'EMPTY
1
2
1 2',
  '按掩码00,01,10,11'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'N 皇后方案数', '# N 皇后方案数

## 题目描述
在 N×N 棋盘放置 N 个皇后，使任意两个皇后不在同一行、列或对角线上，求方案数。

## 输入格式
输入 N。

## 输出格式
输出方案数。

## 数据范围
`1≤N≤14`。',
  '困难', '["回溯","搜索","N皇后"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4', '2',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '1',
  '边界'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数独有效性判断', '# 数独有效性判断

## 题目描述
给定一个 9×9 数独局面，数字 `1-9` 表示已填，`.` 表示空。判断当前已填数字是否违反行、列、3×3 宫规则。

## 输入格式
输入 9 行，每行 9 个字符。

## 输出格式
合法输出 `YES`，否则输出 `NO`。

## 数据范围
固定 9×9。',
  '中等', '["回溯","哈希","矩阵"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79', 'YES',
  '合法局面'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
5...8..79', 'NO',
  '第1列重复5'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '迷宫路径数量', '# 迷宫路径数量

## 题目描述
N×M 网格中，`0` 可走、`1` 障碍。从左上角到右下角，每步只能向右或向下，求不同路径数量。

## 输入格式
第一行 `N M`；之后 N 行每行 M 个 0/1。

## 输出格式
输出路径数。

## 数据范围
`1≤N,M≤20`，答案不超过 `10^18`。',
  '中等', '["回溯","DFS","网格"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
0 0 0
0 1 0
0 0 0', '2',
  '中央障碍'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
0 1
0 0', '1',
  '唯一路径'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '单词搜索', '# 单词搜索

## 题目描述
给定字符网格和单词 W，判断能否通过上下左右相邻单元格依次拼出 W，同一单元格不能重复使用。

## 输入格式
第一行 `N M`；之后 N 行字符串；最后一行 W。

## 输出格式
存在输出 `YES`，否则输出 `NO`。

## 数据范围
`1≤N,M≤20, 1≤|W|≤100`。',
  '困难', '["回溯","DFS","网格"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
ABCE
SFCS
ADEE
ABCCED', 'YES',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
ABCE
SFCS
ADEE
ABCB', 'NO',
  '重复使用限制'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '括号生成', '# 括号生成

## 题目描述
给定 N 对括号，按字典序输出所有合法括号序列。字符 `''(''` 的字典序小于 `'')''`。

## 输入格式
输入 N。

## 输出格式
每行一个合法序列。

## 数据范围
`1≤N≤10`。',
  '中等', '["回溯","字符串","括号"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3', '((()))
(()())
(())()
()(())
()()()',
  'N=3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '电话号码字母组合', '# 电话号码字母组合

## 题目描述
数字 2~9 对应手机键盘字母：2=abc,3=def,4=ghi,5=jkl,6=mno,7=pqrs,8=tuv,9=wxyz。给定数字串，按字典序输出所有字母组合。

## 输入格式
输入一个只含 2~9 的字符串。

## 输出格式
每行一个组合。

## 数据范围
`1≤长度≤8`。',
  '中等', '["回溯","字符串","组合"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '23', 'ad
ae
af
bd
be
bf
cd
ce
cf',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '表达式加运算符', '# 表达式加运算符

## 题目描述
给定只含数字的字符串 S 和目标值 T，在数字之间插入 `+` 或 `-`（也可以不插入以形成多位数），统计结果等于 T 的表达式数量。不允许形成有前导零的多位数。

## 输入格式
第一行 S，第二行 T。

## 输出格式
输出方案数。

## 数据范围
`1≤|S|≤12`。',
  '困难', '["回溯","表达式","搜索"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '123
6', '1',
  '1+2+3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '105
5', '1',
  '10-5'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '爬楼梯', '# 爬楼梯

## 题目描述
一次可以爬 1 或 2 级台阶，求爬到第 N 级有多少种不同方法。

## 输入格式
输入 N。

## 输出格式
输出方法数。

## 数据范围
`1≤N≤90`。',
  '简单', '["动态规划","斐波那契","基础算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2', '2',
  '1+1,2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5', '8',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小花费爬楼梯', '# 最小花费爬楼梯

## 题目描述
给定 cost[i] 表示踩到第 i 级台阶的花费。可以从 0 或 1 开始，每次爬 1 或 2 级，求到达楼顶（越过最后一级）的最小花费。

## 输入格式
第一行 N；第二行 N 个非负整数 cost。

## 输出格式
输出最小花费。

## 数据范围
`2≤N≤2×10^5`。',
  '中等', '["动态规划","数组","最优化"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
10 15 20', '15',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10
1 100 1 1 1 100 1 1 100 1', '6',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '打家劫舍', '# 打家劫舍

## 题目描述
一排房屋中第 i 间有金额 a[i]，相邻两间不能同时选择，求最大金额。

## 输入格式
第一行 N；第二行 N 个非负整数。

## 输出格式
输出最大金额。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["动态规划","数组","最优化"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 3 1', '4',
  '1+3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 7 9 3 1', '12',
  '2+9+1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '零钱兑换最少硬币', '# 零钱兑换最少硬币

## 题目描述
给定 N 种正整数面值和金额 A，每种硬币无限使用，求凑成 A 的最少硬币数，无法凑成输出 -1。

## 输入格式
第一行 `N A`；第二行 N 个面值。

## 输出格式
输出最少硬币数。

## 数据范围
`1≤N≤100, 0≤A≤10^5`。',
  '中等', '["动态规划","完全背包","最短路径思想"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 11
1 2 5', '3',
  '5+5+1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 3
2 4', '-1',
  '无法'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '零钱兑换方案数', '# 零钱兑换方案数

## 题目描述
给定 N 种硬币面值，每种无限使用，求凑成金额 A 的组合方案数。不同顺序视为同一方案。

## 输入格式
第一行 `N A`；第二行 N 个不同正整数面值。

## 输出格式
输出方案数。

## 数据范围
`1≤N≤100, 0≤A≤10^4`，答案不超过 `10^18`。',
  '中等', '["动态规划","完全背包","计数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 5
1 2 5', '4',
  '5;2+2+1;2+1+1+1;全1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 3
2 4', '0',
  '无法'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '0-1 背包最大价值', '# 0-1 背包最大价值

## 题目描述
有 N 件物品，每件最多选一次，第 i 件重量 w[i]、价值 v[i]，背包容量 C，求最大总价值。

## 输入格式
第一行 `N C`；之后 N 行 `w v`。

## 输出格式
输出最大价值。

## 数据范围
`1≤N≤200, 0≤C≤10^5`。',
  '中等', '["动态规划","0-1背包","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
2 3
1 2
3 4', '6',
  '选重量1和3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 1
2 10
3 20', '0',
  '都放不下'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长递增子序列长度', '# 最长递增子序列长度

## 题目描述
求数组的最长严格递增子序列长度，子序列不要求连续。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出长度。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["动态规划","二分查找","LIS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8
10 9 2 5 3 7 101 18', '4',
  '2,3,7,101'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
4 3 2 1', '1',
  '递减'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长公共子序列长度', '# 最长公共子序列长度

## 题目描述
给定两个字符串，求最长公共子序列长度。

## 输入格式
输入两行字符串 A、B。

## 输出格式
输出长度。

## 数据范围
`1≤|A|,|B|≤2000`。',
  '中等', '["动态规划","字符串","LCS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcde
ace', '3',
  'ace'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abc
def', '0',
  '无公共字符'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '编辑距离', '# 编辑距离

## 题目描述
将字符串 A 转换为 B，每次可插入、删除或替换一个字符，求最少操作数。

## 输入格式
输入两行字符串 A、B。

## 输出格式
输出最小编辑距离。

## 数据范围
`0≤|A|,|B|≤2000`。',
  '困难', '["动态规划","字符串","最短编辑"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'horse
ros', '3',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'intention
execution', '5',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长回文子序列', '# 最长回文子序列

## 题目描述
求字符串的最长回文子序列长度。

## 输入格式
输入字符串 S。

## 输出格式
输出长度。

## 数据范围
`1≤|S|≤2000`。',
  '中等', '["动态规划","字符串","回文"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'bbbab', '4',
  'bbbb'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'cbbd', '2',
  'bb'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数字三角形最大路径和', '# 数字三角形最大路径和

## 题目描述
给定 N 层数字三角形，从顶点出发每次走到下一行相邻两个位置之一，求最大路径和。

## 输入格式
第一行 N；之后第 i 行有 i 个整数。

## 输出格式
输出最大路径和。

## 数据范围
`1≤N≤1000`。',
  '中等', '["动态规划","路径","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
2
3 4
6 5 7
4 1 8 3', '21',
  '2+4+7+8'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格最小路径和', '# 网格最小路径和

## 题目描述
N×M 非负网格，从左上角到右下角，每次只能向右或向下，求路径上数字之和的最小值。

## 输入格式
第一行 `N M`；之后 N 行 M 个整数。

## 输出格式
输出最小路径和。

## 数据范围
`1≤N,M≤1000`。',
  '中等', '["动态规划","网格","路径"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 3 1
1 5 1
4 2 1', '7',
  '1-3-1-1-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最大正方形', '# 最大正方形

## 题目描述
给定只含 0/1 的矩阵，求只由 1 组成的最大正方形面积。

## 输入格式
第一行 `N M`；之后 N 行每行 M 个 0/1。

## 输出格式
输出最大面积。

## 数据范围
`1≤N,M≤1000`。',
  '困难', '["动态规划","矩阵","二维DP"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 0 1 0 0
1 0 1 1 1
1 1 1 1 1
1 0 0 1 0', '4',
  '2x2'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间调度最大权重', '# 区间调度最大权重

## 题目描述
给定 N 个任务，每个任务有开始 s、结束 e、收益 w，选择互不重叠任务使收益最大。区间按 `[s,e)`。

## 输入格式
第一行 N；之后 N 行 `s e w`。

## 输出格式
输出最大收益。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["动态规划","排序","二分查找"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 3 5
2 5 6
4 6 5
6 7 4', '14',
  '1-3,4-6,6-7'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '跳跃游戏', '# 跳跃游戏

## 题目描述
数组 nums[i] 表示从位置 i 最多可向右跳多少步，判断能否从下标 0 到达最后位置。

## 输入格式
第一行 N；第二行 N 个非负整数。

## 输出格式
能到达输出 `YES`，否则输出 `NO`。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["贪心","数组","可达性"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 3 1 1 4', 'YES',
  '可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
3 2 1 0 4', 'NO',
  '被0阻断'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '跳跃游戏最少次数', '# 跳跃游戏最少次数

## 题目描述
保证可以到达末尾，求从下标 0 到最后位置的最少跳跃次数。

## 输入格式
第一行 N；第二行 N 个非负整数。

## 输出格式
输出最少次数。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["贪心","数组","最短跳跃"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 3 1 1 4', '2',
  '0->1->4'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
0', '0',
  '起点即终点'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '分糖果', '# 分糖果

## 题目描述
N 个孩子排成一列，每人有评分。每人至少 1 颗糖；若某孩子评分高于相邻孩子，则糖果数也必须更多。求最少糖果总数。

## 输入格式
第一行 N；第二行 N 个评分。

## 输出格式
输出最少糖果数。

## 数据范围
`1≤N≤2×10^5`。',
  '困难', '["贪心","双向扫描","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 0 2', '5',
  '2,1,2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2 2', '4',
  '1,2,1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '加油站环形一周', '# 加油站环形一周

## 题目描述
N 个加油站环形排列，gas[i] 为可加油量，cost[i] 为驶向下一站所需油量。油箱初始为 0，若存在唯一可完成一圈的起点，输出其 0-based 下标，否则 -1。

## 输入格式
第一行 N；第二行 gas；第三行 cost。

## 输出格式
输出起点下标或 -1。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["贪心","数组","模拟"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5
3 4 5 1 2', '3',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
2 3 4
3 4 3', '-1',
  '不可完成'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最大子数组乘积', '# 最大子数组乘积

## 题目描述
求非空连续子数组的最大乘积。

## 输入格式
第一行 N；第二行 N 个整数。

## 输出格式
输出最大乘积。

## 数据范围
`1≤N≤2×10^5`，保证答案在 64 位有符号整数范围内。',
  '困难', '["动态规划","数组","最大最小状态"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
2 3 -2 4', '6',
  '2*3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
-2 0 -1', '0',
  '零'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '股票一次交易最大利润', '# 股票一次交易最大利润

## 题目描述
给定每天股票价格，只允许买入一次并在未来卖出一次，求最大利润；若无法获利输出 0。

## 输入格式
第一行 N；第二行 N 个价格。

## 输出格式
输出最大利润。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["贪心","数组","股票"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
7 1 5 3 6 4', '5',
  '1买6卖'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
7 6 4 3 1', '0',
  '下降'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树前序遍历', '# 二叉树前序遍历

## 题目描述
给定一棵二叉树的层序数组表示，`null` 表示空节点，输出前序遍历。输入保证表示合法。

## 输入格式
第一行 N；第二行 N 个 token。

## 输出格式
输出节点值，空格分隔。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["二叉树","遍历","DFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 3 null 4 5 6', '1 2 4 3 5 6',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树中序遍历', '# 二叉树中序遍历

## 题目描述
给定二叉树层序表示，输出中序遍历。

## 输入格式
第一行 N；第二行 N 个 token，`null` 为空。

## 输出格式
输出节点值。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["二叉树","遍历","DFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 3 null 4 5 6', '2 4 1 5 3 6',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树后序遍历', '# 二叉树后序遍历

## 题目描述
给定二叉树层序表示，输出后序遍历。

## 输入格式
第一行 N；第二行 N 个 token，`null` 为空。

## 输出格式
输出节点值。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["二叉树","遍历","DFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 3 null 4 5 6', '4 2 5 6 3 1',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树层序遍历', '# 二叉树层序遍历

## 题目描述
给定二叉树层序表示，输出按层从左到右的所有非空节点。

## 输入格式
第一行 N；第二行 N 个 token，`null` 为空。

## 输出格式
输出节点值。

## 数据范围
`1≤N≤2×10^5`。',
  '简单', '["二叉树","BFS","队列"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 3 null 4 5 6', '1 2 3 4 5 6',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树最大深度', '# 二叉树最大深度

## 题目描述
求二叉树最大深度。只有根节点时深度为 1，空树深度为 0。

## 输入格式
第一行 N；若 N>0，第二行 N 个层序 token。

## 输出格式
输出最大深度。

## 数据范围
`0≤N≤2×10^5`。',
  '简单', '["二叉树","DFS","递归"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
3 9 20 null null 15 7', '3',
  '经典'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0', '0',
  '空树'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉树是否对称', '# 二叉树是否对称

## 题目描述
判断二叉树是否关于根节点轴对称。

## 输入格式
第一行 N；第二行 N 个层序 token。

## 输出格式
对称输出 `YES`，否则 `NO`。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二叉树","递归","镜像"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 2 3 4 4 3', 'YES',
  '对称'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
1 2 2 null 3 null 3', 'NO',
  '非对称'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉搜索树验证', '# 二叉搜索树验证

## 题目描述
判断给定二叉树是否为严格二叉搜索树：每个节点左子树值都小于它，右子树值都大于它。

## 输入格式
第一行 N；第二行层序 token。

## 输出格式
是输出 `YES`，否则 `NO`。

## 数据范围
`1≤N≤2×10^5`。',
  '中等', '["二叉搜索树","DFS","中序遍历"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
2 1 3 null null null null', 'YES',
  '合法'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7
5 1 4 null null 3 6', 'NO',
  '3在5的右子树但小于5'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '二叉搜索树第 K 小', '# 二叉搜索树第 K 小

## 题目描述
给定一棵二叉搜索树和 K，输出第 K 小节点值。

## 输入格式
第一行 `N K`；第二行层序 token。

## 输出格式
输出节点值。

## 数据范围
`1≤K≤节点数≤2×10^5`。',
  '中等', '["二叉搜索树","中序遍历","选择"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 3
5 3 6 2 4 null null', '4',
  '中序2,3,4,5,6'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '无向图 BFS 最短路', '# 无向图 BFS 最短路

## 题目描述
给定无权无向图，求节点 S 到 T 的最短边数，不可达输出 -1。

## 输入格式
第一行 `N M S T`；之后 M 行边 `u v`。

## 输出格式
输出最短距离。

## 数据范围
`1≤N,M≤2×10^5`。',
  '中等', '["图论","BFS","最短路"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5 1 5
1 2
2 3
3 5
1 4
4 5', '2',
  '1-4-5'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1 1 3
1 2', '-1',
  '不可达'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '无向图连通分量', '# 无向图连通分量

## 题目描述
统计无向图的连通分量数量。

## 输入格式
第一行 `N M`；之后 M 行边。

## 输出格式
输出连通分量数。

## 数据范围
`1≤N≤2×10^5, 0≤M≤2×10^5`。',
  '中等', '["图论","DFS","BFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2
1 2
4 5', '3',
  '{1,2},{3},{4,5}'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
1 3', '1',
  '全连通'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '无向图是否有环', '# 无向图是否有环

## 题目描述
判断无向图中是否存在环。

## 输入格式
第一行 `N M`；之后 M 行边。

## 输出格式
有环输出 `YES`，否则 `NO`。

## 数据范围
`1≤N≤2×10^5, 0≤M≤2×10^5`。',
  '中等', '["图论","DFS","并查集"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
3 1', 'YES',
  '三角环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 2
2 3
3 4', 'NO',
  '树'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '有向图是否有环', '# 有向图是否有环

## 题目描述
判断有向图中是否存在有向环。

## 输入格式
第一行 `N M`；之后 M 行有向边 `u v`。

## 输出格式
有环输出 `YES`，否则 `NO`。

## 数据范围
`1≤N,M≤2×10^5`。',
  '中等', '["图论","拓扑排序","DFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
3 1', 'YES',
  '有环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 2
1 2
2 3', 'NO',
  'DAG'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '拓扑排序', '# 拓扑排序

## 题目描述
给定有向无环图，输出一个拓扑序。若有多个，要求每次选择当前入度为 0 的最小编号节点。

## 输入格式
第一行 `N M`；之后 M 行有向边。

## 输出格式
输出 N 个节点编号。

## 数据范围
`1≤N,M≤2×10^5`。',
  '中等', '["图论","拓扑排序","队列"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 2
1 3
3 4', '1 2 3 4',
  '按最小编号'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'Dijkstra 最短路', '# Dijkstra 最短路

## 题目描述
给定非负权有向图，求源点 S 到所有节点的最短距离。不可达输出 -1。

## 输入格式
第一行 `N M S`；之后 M 行 `u v w`。

## 输出格式
输出 N 个距离，按节点 1..N。

## 数据范围
`1≤N,M≤2×10^5, 0≤w≤10^9`。',
  '困难', '["图论","Dijkstra","优先队列"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4 1
1 2 2
1 3 5
2 3 1
3 4 3', '0 2 3 6',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  'Floyd 多源最短路', '# Floyd 多源最短路

## 题目描述
给定带非负权的有向图和 Q 次查询，求每对节点最短距离，不可达输出 -1。

## 输入格式
第一行 `N M Q`；之后 M 行 `u v w`；再之后 Q 行 `s t`。

## 输出格式
每个查询输出一行。

## 数据范围
`1≤N≤300, M≤2×10^4, Q≤10^5`。',
  '困难', '["图论","Floyd","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3 3
1 2 4
2 3 5
1 3 20
1 3
3 1
1 1', '9
-1
0',
  '基础'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小生成树 Kruskal', '# 最小生成树 Kruskal

## 题目描述
给定连通无向带权图，求最小生成树总权值。

## 输入格式
第一行 `N M`；之后 M 行 `u v w`。

## 输出格式
输出最小生成树权值。

## 数据范围
`1≤N,M≤2×10^5`，权值可为负。',
  '困难', '["图论","最小生成树","并查集"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 2 1
1 3 4
2 3 2
2 4 5
3 4 3', '6',
  '1+2+3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格岛屿数量', '# 网格岛屿数量

## 题目描述
给定 0/1 网格，1 表示陆地，按上下左右相邻连通，统计岛屿数量。

## 输入格式
第一行 `N M`；之后 N 行每行 M 个字符 0/1。

## 输出格式
输出岛屿数。

## 数据范围
`1≤N,M≤1000`。',
  '中等', '["图论","DFS","BFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
11000
11000
00100
00011', '3',
  '三座岛'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格最短路径', '# 网格最短路径

## 题目描述
0/1 网格中 0 可走、1 障碍，从左上角走到右下角，每步上下左右，求最少步数，不可达输出 -1。

## 输入格式
第一行 `N M`；之后 N 行每行 M 个 0/1。

## 输出格式
输出最少步数。

## 数据范围
`1≤N,M≤1000`。',
  '中等', '["图论","BFS","网格"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
000
110
000', '4',
  '右右下下'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
01
10', '-1',
  '不可达'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '多源 BFS 最近零距离', '# 多源 BFS 最近零距离

## 题目描述
给定 0/1 矩阵，对每个位置输出它到最近 0 的曼哈顿最短距离，只能上下左右移动。保证至少有一个 0。

## 输入格式
第一行 `N M`；之后 N 行 M 个 0/1。

## 输出格式
输出 N 行距离矩阵。

## 数据范围
`1≤N,M≤1000`。',
  '困难', '["图论","BFS","矩阵"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
0 0 0
0 1 0
1 1 1', '0 0 0
0 1 0
1 2 1',
  '经典'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '课程先修是否可完成', '# 课程先修是否可完成

## 题目描述
有 N 门课程编号 0..N-1，给出 M 个先修关系 `a b` 表示学习 a 前必须先学 b。判断是否能完成所有课程。

## 输入格式
第一行 `N M`；之后 M 行 `a b`。

## 输出格式
可以完成输出 `YES`，否则 `NO`。

## 数据范围
`1≤N,M≤2×10^5`。',
  '中等', '["图论","拓扑排序","有向图"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 1
1 0', 'YES',
  '可完成'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
1 0
0 1', 'NO',
  '循环依赖'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '日志中的最活跃用户', '# 日志中的最活跃用户

## 题目描述
给定 N 条登录日志，每条包含用户名。统计出现次数最多的用户；若并列，输出字典序最小者及次数。

## 输入格式
第一行 N；之后 N 行每行一个用户名。

## 输出格式
输出 `username count`。

## 数据范围
`1≤N≤2×10^5`，用户名只含字母数字下划线。',
  '中等', '["哈希表","排序","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
alice
bob
alice
carol
bob
alice', 'alice 3',
  '基础'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
z
a
z
a', 'a 2',
  '并列取字典序小'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '服务器请求峰值并发', '# 服务器请求峰值并发

## 题目描述
给定 N 个请求的开始时刻 s 和结束时刻 e，区间按 `[s,e)` 占用服务器，求任意时刻最大并发请求数。

## 输入格式
第一行 N；之后 N 行 `s e`。

## 输出格式
输出最大并发数。

## 数据范围
`1≤N≤2×10^5, 0≤s<e≤10^18`。',
  '中等', '["扫描线","排序","区间"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 5
2 6
4 7
7 8', '3',
  '时刻4附近三并发'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2
2 3
3 4', '1',
  '无重叠'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '版本号比较', '# 版本号比较

## 题目描述
比较两个版本号。版本号由若干十进制整数段用 `.` 分隔，前导零忽略，缺失段视为 0。若 v1>v2 输出 1，v1<v2 输出 -1，相等输出 0。

## 输入格式
输入两行版本号 v1、v2。

## 输出格式
输出 -1、0 或 1。

## 数据范围
总长度不超过 `10^5`。',
  '中等', '["字符串","解析","比较"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1.01
1.001', '0',
  '前导零'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1.0.1
1', '1',
  '缺失段视0'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1.2
1.10', '-1',
  '数值比较'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '简单路径规范化', '# 简单路径规范化

## 题目描述
给定 Unix 风格绝对路径，规范化规则：多个 `/` 合并；`.` 忽略；`..` 返回上一级但不能越过根目录。输出规范路径。

## 输入格式
输入一行绝对路径。

## 输出格式
输出规范路径。

## 数据范围
长度不超过 `2×10^5`。',
  '中等', '["字符串","栈","路径"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '/home//foo/', '/home/foo',
  '重复斜杠'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '/a/./b/../../c/', '/c',
  '点路径'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '/../', '/',
  '不能越根'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '依赖任务的最短完成时间', '# 依赖任务的最短完成时间

## 题目描述
有 N 个任务，每个任务耗时 t[i]。给定 M 条依赖 `u v`，表示 v 必须在 u 完成后才能开始。可并行执行任意无依赖任务。保证无环，求完成全部任务的最短总时间。

## 输入格式
第一行 `N M`；第二行 N 个任务耗时；之后 M 行 `u v`。

## 输出格式
输出最短完成时间。

## 数据范围
`1≤N,M≤2×10^5, 1≤t[i]≤10^9`。',
  '困难', '["图论","拓扑排序","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5
2 3 4 2 1
1 3
2 3
3 4
3 5
4 5', '10',
  '关键路径2->3->4->5为3+4+2+1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 0
5 2 7', '7',
  '全部并行'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '补给站最小最大间距', '# 补给站最小最大间距

## 题目描述
一条长度为 `L` 的直线赛道上已经有若干补给站。你还可以新建至多 `K` 个补给站。请最小化任意两个相邻补给站之间的最大距离。起点 `0` 和终点 `L` 也视为补给站。

## 输入格式
第一行输入 `L N K`。第二行输入 `N` 个严格递增的已有补给站位置。

## 输出格式
输出最小可能的最大相邻距离。

## 数据范围
`1 ≤ L ≤ 10^9`，`0 ≤ N ≤ 2×10^5`，`0 ≤ K ≤ 10^9`。',
  '中等', '["竞赛题","二分答案","贪心","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 2 1
3 7', '3',
  '在最长区间中增加一个补给站'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '20 0 3
', '5',
  '只有起点和终点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0 0
', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '100 1 0
50', '50',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12 2 10
4 8', '1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '连续签到修复计划', '# 连续签到修复计划

## 题目描述
给定长度为 `N` 的 01 序列，`1` 表示当天签到，`0` 表示缺签。你最多可以补签 `K` 天。求补签后最长连续签到天数。

## 输入格式
第一行输入 `N K`，第二行输入 `N` 个 `0/1`。

## 输出格式
输出最长连续签到天数。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ K ≤ N`。',
  '中等', '["竞赛题","滑动窗口","双指针"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 2
1 0 1 1 0 0 1 1', '6',
  '窗口中最多允许两个 0（已由参考算法校正）'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5
0 0 0 0 0', '5',
  '全部补签'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0
1', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 0
1 1 0 1 1 1', '3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 2
0 0 1 0 1 0 0', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '服务器峰值并发', '# 服务器峰值并发

## 题目描述
有 `N` 个任务，第 `i` 个任务在时刻 `s_i` 开始，在时刻 `e_i` 结束，占用一台服务器，时间区间按 `[s_i,e_i)` 计算。求至少需要多少台服务器才能保证所有任务都立即运行。

## 输入格式
第一行输入 `N`，随后 `N` 行每行输入 `s_i e_i`。

## 输出格式
输出最少服务器数量。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ s_i < e_i ≤ 10^9`。',
  '中等', '["竞赛题","差分","扫描线","区间"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 4
2 5
4 7
3 6', '3',
  '端点相同不重复占用'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2
2 3
3 4', '1',
  '任务首尾衔接'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
0 1', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 10
1 10
1 10
1 10', '4',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2
2 5
2 3
3 4', '2',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '循环赛道补给', '# 循环赛道补给

## 题目描述
环形赛道上有 `N` 个补给点。到达第 `i` 个点可获得 `gas_i` 单位燃料，从 `i` 到下一个点消耗 `cost_i`。初始燃料为 0。若存在一个起点能完整绕行一周，输出编号最小的可行起点，否则输出 `-1`。编号从 1 开始。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个 `gas_i`，第三行输入 `N` 个 `cost_i`。

## 输出格式
输出可行起点编号，若不存在输出 `-1`。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ gas_i,cost_i ≤ 10^9`。',
  '中等', '["竞赛题","贪心","前缀和","数组"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5
3 4 5 1 2', '4',
  '经典可行环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 1 1
2 2 2', '-1',
  '总燃料不足'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
5
5', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
2 2 2 2
2 2 2 2', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
4 0 0 0
1 1 1 1', '1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最长不降观景路线', '# 最长不降观景路线

## 题目描述
一条观景路线依次经过 `N` 个地点，第 `i` 个地点海拔为 `h_i`。你可以跳过任意地点，但保留的地点顺序不能改变。求最长的海拔不下降子序列长度。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个整数 `h_i`。

## 输出格式
输出最长不下降子序列长度。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`-10^9 ≤ h_i ≤ 10^9`。',
  '中等', '["竞赛题","动态规划","二分查找","LIS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8
3 1 2 2 5 4 6 6', '6',
  '允许相等'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
5 4 3 2 1', '1',
  '严格下降'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
-5', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 2 2 2 2', '5',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
1 3 2 4 3 5', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '仓库选址总距离', '# 仓库选址总距离

## 题目描述
数轴上有 `N` 个配送点，位置分别为 `x_i`。要建立一个仓库，仓库位置必须是整数。所有配送点到仓库距离之和应尽可能小。输出最小距离和。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个整数 `x_i`。

## 输出格式
输出最小距离和。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`|x_i| ≤ 10^9`。',
  '中等', '["竞赛题","贪心","中位数","排序"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 10 11 12', '20',
  '中位数最优'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 0 100 100', '200',
  '偶数个点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
999', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
-10 0 10', '20',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
1 2 3 100 101 102', '297',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最大平均产量', '# 最大平均产量

## 题目描述
给定 `N` 天的产量 `a_i`，请选择长度至少为 `K` 的连续区间，使区间平均产量最大。输出最大平均值，允许绝对误差或相对误差不超过 `1e-5`。

## 输入格式
第一行输入 `N K`，第二行输入 `N` 个实数 `a_i`。

## 输出格式
输出最大平均值。

## 数据范围
`1 ≤ K ≤ N ≤ 10^5`，`|a_i| ≤ 10^4`。',
  '困难', '["竞赛题","二分答案","浮点","前缀和"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 4
1 12 -5 -6 50 3', '12.750000',
  '选择长度 4 的最佳区间'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1
-2 -1 -3', '-1.000000',
  '允许负数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1
7', '7.000000',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 2
1 2 3 4 5', '4.500000',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4
-5 -4 -3 -2', '-3.500000',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最短覆盖子数组', '# 最短覆盖子数组

## 题目描述
给定长度为 `N` 的整数数组和 `M` 个必须出现的目标值。求最短连续子数组，使得这 `M` 个目标值每个至少出现一次。若不存在输出 `-1`。目标值互不相同。

## 输入格式
第一行输入 `N M`，第二行输入数组，第三行输入 `M` 个目标值。

## 输出格式
输出最短长度，不存在则输出 `-1`。

## 数据范围
`1 ≤ N,M ≤ 2×10^5`。',
  '中等', '["竞赛题","滑动窗口","哈希表"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 3
1 2 3 2 4 1 3 5
1 3 4', '3',
  '区间 4 1 3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2
1 1 1 1
1 2', '-1',
  '缺少目标值'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 1
1 2 3 4 5
3', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
1 2 1 2 1 2
1 2', '2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2 3
1 2 3', '3',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间任务最大收益', '# 区间任务最大收益

## 题目描述
有 `N` 个任务，每个任务有开始时间 `s_i`、结束时间 `e_i` 和收益 `w_i`。任意两个被选择任务不能时间重叠，区间按 `[s_i,e_i)` 计算。求最大总收益。

## 输入格式
第一行输入 `N`，随后 `N` 行输入 `s_i e_i w_i`。

## 输出格式
输出最大总收益。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ s_i < e_i ≤ 10^9`，`0 ≤ w_i ≤ 10^9`。',
  '中等', '["竞赛题","动态规划","二分查找","区间调度"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 3 5
2 5 6
4 6 5
6 7 4', '14',
  '选择 1-3、4-6、6-7'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 10 20
2 3 5
3 4 6', '20',
  '长任务更优'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
0 1 7', '7',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 2 5
2 4 6
4 6 7
0 6 17', '18',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 5 10
2 3 100
3 4 100', '200',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '能量石合并', '# 能量石合并

## 题目描述
一排有 `N` 堆能量石，第 `i` 堆重量为 `a_i`。每次只能合并相邻两堆，代价等于两堆重量之和，合并后重量也为两者之和。求合并成一堆的最小总代价。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个正整数 `a_i`。

## 输出格式
输出最小总代价。

## 数据范围
`1 ≤ N ≤ 500`，`1 ≤ a_i ≤ 10^6`。',
  '困难', '["竞赛题","区间DP","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 3 4', '19',
  '区间 DP 示例'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
10 10 10', '50',
  '三堆相同'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
100', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
5 7', '12',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 1 1 1 1', '12',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '课程最小学期数', '# 课程最小学期数

## 题目描述
有 `N` 门课程和 `M` 条先修关系 `u -> v`，表示修完 `u` 后才能修 `v`。每学期可同时修任意多门已满足先修条件的课程。若依赖图无环，求修完全部课程至少需要多少学期；若存在环输出 `-1`。

## 输入格式
第一行输入 `N M`，随后 `M` 行输入 `u v`。

## 输出格式
输出最小学期数，存在环则输出 `-1`。

## 数据范围
`1 ≤ N,M ≤ 2×10^5`。',
  '中等', '["竞赛题","图论","拓扑排序","DAG"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4
1 3
2 3
3 4
3 5', '3',
  '最长依赖链长度为 3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
3 1', '-1',
  '存在依赖环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 0', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 2
2 3
3 4', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '城市最短通信延迟', '# 城市最短通信延迟

## 题目描述
有 `N` 个城市、`M` 条双向通信线路，每条线路有非负延迟。给定起点 `S` 和终点 `T`，求最小通信延迟，不可达输出 `-1`。

## 输入格式
第一行输入 `N M S T`，随后 `M` 行输入 `u v w`。

## 输出格式
输出 `S` 到 `T` 的最短距离。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`1 ≤ M ≤ 4×10^5`，`0 ≤ w ≤ 10^9`。',
  '中等', '["竞赛题","图论","Dijkstra","最短路"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 6 1 5
1 2 2
2 5 5
1 3 4
3 4 1
4 5 1
2 3 1', '5',
  '1-2-3-4-5'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1 1 3
1 2 7', '-1',
  '终点不可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0 1 1', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4 1 4
1 2 0
2 3 0
3 4 0
1 4 5', '0',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2 2 4
1 2 3
3 4 4', '-1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '零一传送门迷宫', '# 零一传送门迷宫

## 题目描述
有 `N` 个点、`M` 条有向边，每条边的代价只能是 `0` 或 `1`。求从 `S` 到 `T` 的最小总代价，不可达输出 `-1`。

## 输入格式
第一行输入 `N M S T`，随后 `M` 行输入 `u v w`，其中 `w` 为 0 或 1。

## 输出格式
输出最小总代价。

## 数据范围
`1 ≤ N,M ≤ 5×10^5`。',
  '困难', '["竞赛题","0-1 BFS","图论","最短路"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5 1 4
1 2 1
1 3 0
3 2 0
2 4 1
3 4 1', '1',
  '使用 0 权边减少代价'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 1 1 3
1 2 0', '-1',
  '不可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0 1 1', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4 1 4
1 2 0
2 3 0
3 4 1
1 4 1', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3 1 4
1 2 1
2 3 1
3 4 1', '3',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '低成本城市联网', '# 低成本城市联网

## 题目描述
有 `N` 个城市和 `M` 条候选双向线路，每条线路建设费用为 `w`。请选择若干线路使所有城市连通且总费用最小。若无法全部连通输出 `-1`。

## 输入格式
第一行输入 `N M`，随后 `M` 行输入 `u v w`。

## 输出格式
输出最小总费用。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`1 ≤ M ≤ 4×10^5`。',
  '中等', '["竞赛题","最小生成树","Kruskal","并查集"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 2 1
2 3 2
3 4 3
1 4 10
1 3 4', '6',
  '最小生成树'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2
1 2 1
3 4 1', '-1',
  '图不连通'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2 5
2 3 1
1 3 2', '3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4
1 2 1
2 3 1
3 4 1
4 5 1', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '动态社团关系', '# 动态社团关系

## 题目描述
初始有 `N` 名互不相连的成员。共有 `Q` 次操作：`1 a b` 表示合并 `a,b` 所在社团；`2 a b` 表示询问两人当前是否属于同一社团。对每个查询输出 `YES` 或 `NO`。

## 输入格式
第一行输入 `N Q`，随后 `Q` 行为操作。

## 输出格式
对每个类型 2 的操作输出一行答案。

## 数据范围
`1 ≤ N,Q ≤ 5×10^5`。',
  '中等', '["竞赛题","并查集","离线算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 6
2 1 2
1 1 2
2 1 2
1 2 3
2 1 3
2 4 5', 'NO
YES
YES
NO',
  '基本合并查询'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 3
2 1 1
1 1 1
2 1 1', 'YES
YES',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 1 2
1 3 4
2 1 4
1 2 3
2 1 4', 'NO
YES',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
2 1 3
1 1 3
2 1 3
2 2 3', 'NO
YES
NO',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 6
2 1 2
1 1 2
2 1 2
1 2 3
2 1 3
2 4 5
', 'NO
YES
YES
NO',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '紧急广播最早到达', '# 紧急广播最早到达

## 题目描述
无权图中有多个广播源，它们在时刻 0 同时开始传播，每经过一条边耗时 1。求每个节点最早收到广播的时间，不可达输出 `-1`。

## 输入格式
第一行输入 `N M K`，第二行输入 `K` 个广播源，随后 `M` 行输入无向边 `u v`。

## 输出格式
输出 `N` 个整数，第 `i` 个表示节点 `i` 的最早到达时间。

## 数据范围
`1 ≤ N,M ≤ 2×10^5`，`1 ≤ K ≤ N`。',
  '中等', '["竞赛题","多源BFS","图论","队列"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 5 2
1 6
1 2
2 3
3 4
4 5
5 6', '0 1 2 2 1 0',
  '两个源从两端传播'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0 1
1', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 0 2
1 4', '0 -1 -1 0',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4 1
3
1 2
2 3
3 4
4 5', '2 1 0 1 2',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 5 2
1 6
1 2
2 3
3 4
4 5
5 6
', '0 1 2 2 1 0',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '强连通通信组', '# 强连通通信组

## 题目描述
给定一个有向图。若一组节点中任意两点都能互相到达，则它们属于同一个强连通分量。求图中强连通分量的数量以及最大强连通分量的节点数。

## 输入格式
第一行输入 `N M`，随后 `M` 行输入有向边 `u v`。

## 输出格式
输出两个整数：强连通分量数量和最大分量大小。

## 数据范围
`1 ≤ N,M ≤ 5×10^5`。',
  '困难', '["竞赛题","Tarjan","强连通分量","图论"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 6
1 2
2 1
2 3
3 4
4 3
4 5', '3 2',
  '分量为 {1,2},{3,4},{5}'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
3 1', '1 3',
  '全部互相可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 0', '1 1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 0', '4 1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 5
1 2
2 1
2 3
3 4
4 3', '2 2',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '关键桥梁数量', '# 关键桥梁数量

## 题目描述
在一个无向连通图中，一条边若被删除后会使图不再连通，则称为桥。请统计图中桥的数量。

## 输入格式
第一行输入 `N M`，随后 `M` 行输入无向边 `u v`。允许存在重边。

## 输出格式
输出桥的数量。

## 数据范围
`1 ≤ N,M ≤ 5×10^5`。',
  '困难', '["竞赛题","Tarjan","桥","无向图"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5
1 2
2 3
3 1
3 4
4 5', '2',
  '3-4 和 4-5 为桥'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
1 2
2 3
1 3', '0',
  '三角形没有桥'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 1
1 2', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
1 2
1 2', '0',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 2
2 3
3 4', '3',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '树上最大独立集', '# 树上最大独立集

## 题目描述
给定一棵 `N` 个节点的树，每个节点有权值 `w_i`。请选择若干节点，使任意两个被选节点都不直接相邻，并使权值总和最大。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个权值，随后 `N-1` 行输入树边 `u v`。

## 输出格式
输出最大权值和。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ w_i ≤ 10^9`。',
  '困难', '["竞赛题","树形DP","树","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
5 1 4 3 6
1 2
1 3
3 4
3 5', '14',
  '选择 1、4、5'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
10 20
1 2', '20',
  '只能选一个端点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
7', '7',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 100 1
1 2
2 3', '100',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
5 5 5 5
1 2
1 3
1 4', '15',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '树的直径长度', '# 树的直径长度

## 题目描述
给定一棵带非负边权的树，求任意两节点间路径长度的最大值，即树的直径长度。

## 输入格式
第一行输入 `N`，随后 `N-1` 行输入 `u v w`。

## 输出格式
输出树的直径长度。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ w ≤ 10^9`。',
  '中等', '["竞赛题","树","DFS","BFS"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3
2 3 4
2 4 2
4 5 6', '12',
  '路径 3-2-4-5'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1', '0',
  '单节点树'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
1 2 0', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 1
2 3 2
3 4 3', '6',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 10
1 3 10
1 4 10
1 5 10', '20',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最低公共祖先查询', '# 最低公共祖先查询

## 题目描述
给定一棵以节点 1 为根的树，有 `Q` 次查询，每次给出两个节点 `u,v`，求它们的最低公共祖先。

## 输入格式
第一行输入 `N Q`，随后 `N-1` 行输入树边，再输入 `Q` 行查询 `u v`。

## 输出格式
每个查询输出一行最低公共祖先节点编号。

## 数据范围
`1 ≤ N,Q ≤ 2×10^5`。',
  '困难', '["竞赛题","LCA","倍增","树"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 3
1 2
1 3
2 4
2 5
3 6
3 7
4 5
4 6
6 7', '2
1
3',
  '三组 LCA 查询'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2
1 1
1 1', '1
1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 2
2 3
3 4
4 2
3 4
2 2', '2
3
2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 2
1 3
3 4
3 5
2 4
4 5
1 5', '1
3
1',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 3
1 2
1 3
2 4
2 5
3 6
3 7
4 5
4 6
6 7
', '2
1
3',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '精确装载背包', '# 精确装载背包

## 题目描述
有 `N` 件物品，每件物品重量为 `w_i`、价值为 `v_i`，每件最多选一次。背包容量为 `C`，要求总重量恰好等于 `C`，求最大总价值；若无法恰好装满输出 `-1`。

## 输入格式
第一行输入 `N C`，随后 `N` 行输入 `w_i v_i`。

## 输出格式
输出最大价值，无法恰好装满输出 `-1`。

## 数据范围
`1 ≤ N ≤ 200`，`1 ≤ C ≤ 10^5`。',
  '中等', '["竞赛题","动态规划","01背包"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 7
3 4
4 5
2 3
5 8', '11',
  '3+4 恰好装满（已由参考算法校正）'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 5
2 10
4 20', '-1',
  '无法恰好装满'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 5
5 10', '10',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 0
1 2
2 3
3 4', '0',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 6
1 1
2 10
4 20', '30',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '限量物资采购', '# 限量物资采购

## 题目描述
有 `N` 种物资，第 `i` 种单件成本 `c_i`、收益 `v_i`，最多购买 `m_i` 件。预算不超过 `B`，求最大收益。

## 输入格式
第一行输入 `N B`，随后 `N` 行输入 `c_i v_i m_i`。

## 输出格式
输出最大收益。

## 数据范围
`1 ≤ N ≤ 200`，`1 ≤ B ≤ 10^5`，`1 ≤ m_i ≤ 10^9`。',
  '困难', '["竞赛题","多重背包","动态规划","单调队列优化"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 10
3 5 2
4 7 2', '17',
  '购买两个第一种和一个第二种'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 5
2 3 10', '6',
  '最多买两件'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1
2 10 5', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 7
2 3 3
3 5 2', '11',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 10
6 20 1
5 17 2
2 5 10', '34',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '双序列最长公共子序列', '# 双序列最长公共子序列

## 题目描述
给定两个字符串 `A` 和 `B`，求它们最长公共子序列的长度。子序列不要求连续，但字符相对顺序不能改变。

## 输入格式
输入两行字符串 `A`、`B`。

## 输出格式
输出最长公共子序列长度。

## 数据范围
`1 ≤ |A|,|B| ≤ 3000`，字符串仅含小写英文字母。',
  '中等', '["竞赛题","动态规划","LCS","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcde
ace', '3',
  '公共子序列 ace'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abc
def', '0',
  '无公共字符'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a
a', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaa
aa', '2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcabc
acbac', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最少回文切割', '# 最少回文切割

## 题目描述
给定一个字符串，将其切分成若干个非空连续子串，要求每个子串都是回文串。求最少切割次数。

## 输入格式
输入一行字符串 `S`。

## 输出格式
输出最少切割次数。

## 数据范围
`1 ≤ |S| ≤ 3000`。',
  '困难', '["竞赛题","字符串DP","回文","动态规划"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aab', '1',
  'aa|b'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'racecar', '0',
  '整个字符串已经是回文'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'ab', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abbaeae', '1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '旅行商最短环路', '# 旅行商最短环路

## 题目描述
有 `N` 个城市，给出任意两城市间的旅行费用矩阵。旅行者从城市 1 出发，恰好访问每个城市一次后回到城市 1。求最小总费用。

## 输入格式
第一行输入 `N`，随后输入 `N` 行费用矩阵 `d[i][j]`。

## 输出格式
输出最小总费用。

## 数据范围
`2 ≤ N ≤ 20`，`0 ≤ d[i][j] ≤ 10^9`，`d[i][i]=0`。',
  '困难', '["竞赛题","状态压缩DP","位运算","TSP"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 10 15 20
10 0 35 25
15 35 0 30
20 25 30 0', '80',
  '经典 TSP 示例'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
0 5
7 0', '12',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
0 1 9
2 0 3
4 5 0', '8',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 1 1 1
1 0 1 1
1 1 0 1
1 1 1 0', '4',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 10 15 20
10 0 35 25
15 35 0 30
20 25 30 0
', '80',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '无重复数字计数', '# 无重复数字计数

## 题目描述
给定两个整数 `L,R`，统计区间 `[L,R]` 中十进制表示不含重复数字的非负整数个数。数字 0 视为一个合法数。

## 输入格式
输入两个整数 `L R`。

## 输出格式
输出满足条件的整数个数。

## 数据范围
`0 ≤ L ≤ R ≤ 10^18`。',
  '困难', '["竞赛题","数位DP","状态压缩","数学"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 20', '19',
  '只有 11 含重复数字'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '98 102', '2',
  '98 和 102 合法'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '0 0', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 12', '2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '120 130', '9',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格炮台部署', '# 网格炮台部署

## 题目描述
给定 `N×M` 网格，`.` 表示可部署位置，`#` 表示障碍。每行部署的炮台之间不能相邻，且相邻两行同一列不能同时部署炮台。求最多能部署多少个炮台。

## 输入格式
第一行输入 `N M`，随后 `N` 行输入网格。

## 输出格式
输出最多部署数量。

## 数据范围
`1 ≤ N ≤ 100`，`1 ≤ M ≤ 12`。',
  '困难', '["竞赛题","状态压缩DP","网格DP"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
...
...
...', '5',
  '棋盘式部署'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 4
.#..
....', '4',
  '存在障碍'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1
.', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 5
.....', '3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
#...
....
...#', '5',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '模式串最少周期', '# 模式串最少周期

## 题目描述
给定字符串 `S`，求它的最短周期长度 `p`，使得整个字符串可以由长度为 `p` 的字符串重复若干次得到；若不存在更短周期，则答案为 `|S|`。

## 输入格式
输入一行字符串 `S`。

## 输出格式
输出最短周期长度。

## 数据范围
`1 ≤ |S| ≤ 2×10^5`。',
  '中等', '["竞赛题","KMP","字符串","前缀函数"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abababab', '2',
  '周期为 ab'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'ababa', '5',
  '不能整段重复构成'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaaaa', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcabcabc', '3',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '子串相等查询', '# 子串相等查询

## 题目描述
给定字符串 `S`，回答 `Q` 次查询。每次给出 `l1 r1 l2 r2`，判断两个子串 `S[l1..r1]` 与 `S[l2..r2]` 是否完全相同。下标从 1 开始。

## 输入格式
第一行输入字符串 `S`，第二行输入 `Q`，随后 `Q` 行输入四个下标。

## 输出格式
每个查询输出 `YES` 或 `NO`。

## 数据范围
`1 ≤ |S|,Q ≤ 2×10^5`。',
  '中等', '["竞赛题","字符串哈希","前缀哈希"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abacaba
3
1 3 5 7
1 2 2 3
3 3 5 5', 'YES
NO
YES',
  '三次子串比较'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a
2
1 1 1 1
1 1 1 1', 'YES
YES',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'aaaa
3
1 2 3 4
1 3 2 4
2 2 4 4', 'YES
YES
YES',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abcdef
2
1 3 4 6
2 4 2 4', 'NO
YES',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'abacaba
3
1 3 5 7
1 2 2 3
3 3 5 5
', 'YES
NO
YES',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '多模式文本统计', '# 多模式文本统计

## 题目描述
给定 `N` 个模式串和一个文本串。对每个模式串，统计它在文本中出现的次数，允许出现位置重叠。

## 输入格式
第一行输入 `N`，随后 `N` 行为模式串，最后一行为文本串。

## 输出格式
按输入顺序输出 `N` 行，每行一个出现次数。

## 数据范围
`1 ≤ N ≤ 2×10^5`，模式串总长度和文本长度均不超过 `5×10^5`，仅含小写字母。',
  '困难', '["竞赛题","AC自动机","Trie","字符串"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
a
ab
ba
ababa', '3
2
2',
  '统计重叠出现'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
a
aaaa', '4',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
aa
aaa
b
aaaaa', '4
3
0',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
abc
bc
abcabc', '2
2',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
a
ab
ba
ababa
', '3
2
2',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '通配符文件匹配', '# 通配符文件匹配

## 题目描述
给定模式串 `P` 和文本串 `S`。模式中 `?` 可匹配任意一个字符，`*` 可匹配任意长度（包括 0）的字符序列。判断模式能否完整匹配文本。

## 输入格式
第一行输入模式串 `P`，第二行输入文本串 `S`。

## 输出格式
匹配输出 `YES`，否则输出 `NO`。

## 数据范围
`1 ≤ |P|,|S| ≤ 5000`。',
  '中等', '["竞赛题","动态规划","字符串匹配"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a*b?d
axxbcd', 'YES',
  '星号匹配多个字符'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a?c
ac', 'NO',
  '问号必须匹配一个字符'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '*
abc', 'YES',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '?
a', 'YES',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, 'a*b*c
abc', 'YES',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '区间加与区间和', '# 区间加与区间和

## 题目描述
维护长度为 `N` 的数组，支持两种操作：`1 l r x` 将区间 `[l,r]` 每个数加上 `x`；`2 l r` 查询区间 `[l,r]` 的元素和。

## 输入格式
第一行输入 `N Q`，第二行输入初始数组，随后 `Q` 行输入操作。

## 输出格式
对每个查询操作输出一行区间和。

## 数据范围
`1 ≤ N,Q ≤ 2×10^5`，数值及操作后结果范围在 64 位有符号整数内。',
  '困难', '["竞赛题","线段树","懒标记","数据结构"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4
1 2 3 4 5
2 1 5
1 2 4 10
2 2 3
2 4 5', '15
25
19',
  '区间修改与查询'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 4
5
2 1 1
1 1 1 -10
2 1 1
2 1 1', '5
-5
-5',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4
0 0 0 0
1 1 4 3
2 1 4
1 2 3 -1
2 2 3', '12
4',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 -1 1 -1 1
2 1 5
1 1 5 2
2 2 4', '1
5',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4
1 2 3 4 5
2 1 5
1 2 4 10
2 2 3
2 4 5
', '15
25
19',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '动态最大子段和', '# 动态最大子段和

## 题目描述
给定长度为 `N` 的整数数组。支持单点修改 `1 pos x`，以及查询 `2 l r`：求子数组 `[l,r]` 内非空连续子段的最大和。

## 输入格式
第一行输入 `N Q`，第二行输入数组，随后 `Q` 行输入操作。

## 输出格式
对每个类型 2 查询输出一行答案。

## 数据范围
`1 ≤ N,Q ≤ 2×10^5`，`|a_i|,|x| ≤ 10^9`。',
  '困难', '["竞赛题","线段树","最大子段和","分治"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
-2 3 -1 4 -5
2 1 5
1 1 10
2 1 4', '6
16',
  '维护 sum/prefix/suffix/best'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 3
-5
2 1 1
1 1 4
2 1 1', '-5
4',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 2
-1 -2 -3 -4
2 1 4
2 2 3', '-1
-2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 2 -10 3 4
2 1 5
1 3 5
2 1 5', '7
15',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
-2 3 -1 4 -5
2 1 5
1 1 10
2 1 4
', '6
16',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '数据流中位数', '# 数据流中位数

## 题目描述
依次读入 `N` 个整数。每读入一个数后，输出当前所有数的中位数。若当前元素个数为偶数，定义中位数为中间两个数中较小的那个。

## 输入格式
第一行输入 `N`，第二行输入 `N` 个整数。

## 输出格式
输出 `N` 个整数，依次表示每一步的中位数。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`|a_i| ≤ 10^9`。',
  '中等', '["竞赛题","堆","优先队列","在线算法"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
5 2 10 1 3 8', '5 2 5 2 3 3',
  '双堆维护'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
9', '9',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
1 2 3 4 5', '1 1 2 2 3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
5 4 3 2 1', '5 4 4 3 3',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
5 2 10 1 3 8
', '5 2 5 2 3 3',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '滑动窗口最值', '# 滑动窗口最值

## 题目描述
给定长度为 `N` 的数组和窗口大小 `K`。窗口从左到右每次移动一格，分别输出每个窗口的最小值序列和最大值序列。

## 输入格式
第一行输入 `N K`，第二行输入数组。

## 输出格式
第一行输出各窗口最小值，第二行输出各窗口最大值。

## 数据范围
`1 ≤ K ≤ N ≤ 2×10^5`。',
  '中等', '["竞赛题","单调队列","滑动窗口"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 3
1 3 -1 -3 5 3 6 7', '-1 -3 -3 -3 3 3
3 3 5 5 6 7',
  '经典窗口最值'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1
7', '7
7',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 5
5 4 3 2 1', '1
5',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
2 2 1 3 3 0', '2 1 1 3 0
2 2 3 3 3',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 3
1 3 -1 -3 5 3 6 7
', '-1 -3 -3 -3 3 3
3 3 5 5 6 7',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '第 K 小区间查询', '# 第 K 小区间查询

## 题目描述
给定静态数组 `a`，回答 `Q` 次查询。每次给出 `l r k`，求子数组 `a[l..r]` 中第 `k` 小的数。

## 输入格式
第一行输入 `N Q`，第二行输入数组，随后 `Q` 行输入 `l r k`。

## 输出格式
每个查询输出一行答案。

## 数据范围
`1 ≤ N,Q ≤ 2×10^5`，`1 ≤ k ≤ r-l+1`，`|a_i| ≤ 10^9`。',
  '困难', '["竞赛题","主席树","可持久化线段树","离散化"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 5 2 6 3
1 5 3
2 4 2
3 5 1', '3
5
2',
  '三次区间第 k 小'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2
7
1 1 1
1 1 1', '7
7',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
5 5 1 1 3
1 5 4
2 4 2
3 5 1', '5
1
1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
-3 8 0 -1 8 2
1 6 2
2 5 3', '-1
8',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
1 5 2 6 3
1 5 3
2 4 2
3 5 1
', '3
5
2',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '线性递推第 N 项', '# 线性递推第 N 项

## 题目描述
定义数列 `F_1=a`，`F_2=b`，当 `n≥3` 时 `F_n = p*F_{n-1} + q*F_{n-2}`。给定 `n,a,b,p,q,mod`，求 `F_n mod mod`。

## 输入格式
输入一行 `n a b p q mod`。

## 输出格式
输出 `F_n mod mod`。

## 数据范围
`1 ≤ n ≤ 10^18`，`1 ≤ mod ≤ 2×10^9`，其余参数绝对值不超过 `10^9`。',
  '中等', '["竞赛题","矩阵快速幂","快速幂","数学"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 1 1 1 1 1000000007', '55',
  '斐波那契'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 2 3 2 1 100', '8',
  '2*3+2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 7 9 2 3 100', '7',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 7 9 2 3 100', '9',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 1 2 2 0 1000', '32',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '组合数模质数', '# 组合数模质数

## 题目描述
给定质数 `P` 和 `Q` 次询问，每次给出 `n,k`，求组合数 `C(n,k) mod P`。保证所有询问中的 `n < P`。

## 输入格式
第一行输入 `P Q`，随后 `Q` 行输入 `n k`。

## 输出格式
每个询问输出一行答案。

## 数据范围
`2 ≤ P ≤ 2×10^6` 且 `P` 为质数，`1 ≤ Q ≤ 2×10^5`。',
  '困难', '["竞赛题","组合数学","费马小定理","逆元"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1000003 3
5 2
10 0
6 3', '10
1
20',
  '预处理阶乘与逆阶乘'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '7 4
0 0
6 3
6 6
5 1', '1
6
1
5',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '11 3
10 5
9 4
8 2', '10
5
6',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 3
4 2
3 1
2 0', '1
3
1',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1000003 3
5 2
10 0
6 3
', '10
1
20',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '同余方程合并', '# 同余方程合并

## 题目描述
给定 `N` 个同余方程 `x ≡ a_i (mod m_i)`，模数不保证两两互质。求最小非负解 `x`；若无解输出 `-1`。

## 输入格式
第一行输入 `N`，随后 `N` 行输入 `m_i a_i`。

## 输出格式
输出最小非负解或 `-1`。

## 数据范围
`1 ≤ N ≤ 10^5`，`1 ≤ m_i ≤ 10^12`，保证计算过程中的合法答案不超过 64 位有符号整数。',
  '困难', '["竞赛题","中国剩余定理","扩展欧几里得","数论"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
3 2
5 3', '8',
  '互质模数'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
4 1
2 0', '-1',
  '方程冲突'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
7 5', '5',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
4 2
6 2', '2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
2 1
3 2
5 3', '23',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '素数区间查询', '# 素数区间查询

## 题目描述
给定 `Q` 次查询，每次给出 `[L,R]`，统计区间内素数数量。

## 输入格式
第一行输入 `Q`，随后 `Q` 行输入 `L R`。

## 输出格式
每个查询输出一行素数数量。

## 数据范围
`1 ≤ Q ≤ 2×10^5`，`1 ≤ L ≤ R ≤ 10^7`。',
  '中等', '["竞赛题","筛法","前缀和","数论"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 10
10 20
2 2', '4
4
1',
  '埃氏筛加前缀和'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 1
2 3
4 4
1 100', '0
2
0
25',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
17 17
18 18
19 23', '1
0
2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2
999 1000
90 110', '0
5',
  '隐藏判题增强-3'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 10
10 20
2 2
', '4
4
1',
  '输入边界兼容-1'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格最少转弯次数', '# 网格最少转弯次数

## 题目描述
在 `N×M` 网格中，`.` 可通行，`#` 不可通行。机器人从 `S` 到 `T`，每次向上下左右相邻格移动。连续沿同一方向移动不增加转弯次数，改变方向时转弯次数加 1。求最少转弯次数。第一次选择方向不计转弯。

## 输入格式
第一行输入 `N M`，随后 `N` 行网格，网格中恰有一个 `S` 和一个 `T`。

## 输出格式
输出最少转弯次数，不可达输出 `-1`。

## 数据范围
`1 ≤ N,M ≤ 1000`。',
  '困难', '["竞赛题","BFS","状态图","最短路"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 4
S...
##..
...T', '1',
  '先向右再向下'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
S#
#T', '-1',
  '不可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2
ST', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
S..
...
..T', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3
S#.
.#.
..T', '1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '骑士最短汇合', '# 骑士最短汇合

## 题目描述
国际象棋棋盘大小为 `N×M`，有两名骑士分别位于 `(x1,y1)` 和 `(x2,y2)`。每一步按标准马步移动。求两名骑士移动总步数最少的汇合方案；允许某个骑士原地不动。无法汇合输出 `-1`。

## 输入格式
输入 `N M x1 y1 x2 y2`。

## 输出格式
输出最小总步数。

## 数据范围
`1 ≤ N,M ≤ 200`。',
  '中等', '["竞赛题","BFS","网格","多源思想"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 8 1 1 8 8', '6',
  '可在最短路径上的位置汇合'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2 1 1 1 2', '-1',
  '无法移动且不同点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 8 1 1 1 1', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3 1 1 2 3', '1',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 4 1 1 4 4', '2',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最少交换完成排列', '# 最少交换完成排列

## 题目描述
给定一个 `1..N` 的排列。每次可交换任意两个位置的元素。求把排列变为升序 `1,2,...,N` 所需的最少交换次数。

## 输入格式
第一行输入 `N`，第二行输入排列。

## 输出格式
输出最少交换次数。

## 数据范围
`1 ≤ N ≤ 2×10^5`。',
  '中等', '["竞赛题","置换","环分解","贪心"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 1 5 3 4', '3',
  '两个置换环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 2 3 4', '0',
  '已经有序'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
1', '0',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
2 3 4 5 1', '4',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6
2 1 4 3 6 5', '3',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小字典序拓扑序', '# 最小字典序拓扑序

## 题目描述
给定一个有向无环图，请输出所有合法拓扑序中字典序最小的一种。若输入图实际上存在环，则输出 `-1`。

## 输入格式
第一行输入 `N M`，随后 `M` 行输入边 `u v`。

## 输出格式
输出拓扑序，节点编号之间用空格分隔；存在环输出 `-1`。

## 数据范围
`1 ≤ N,M ≤ 2×10^5`。',
  '中等', '["竞赛题","拓扑排序","优先队列","图论"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 4
1 3
2 3
3 5
4 5', '1 2 3 4 5',
  '小根堆选择当前最小节点'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2
1 2
2 1', '-1',
  '存在环'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 0', '1 2 3 4',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 3
1 4
2 4
3 4', '1 2 3 4',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 2
3 2
3 1', '3 1 2',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '会议室最少数量', '# 会议室最少数量

## 题目描述
有 `N` 场会议，每场会议占用时间区间 `[s_i,e_i)`。同一会议室中的会议不能重叠。求安排全部会议所需的最少会议室数量。

## 输入格式
第一行输入 `N`，随后 `N` 行输入 `s_i e_i`。

## 输出格式
输出最少会议室数量。

## 数据范围
`1 ≤ N ≤ 2×10^5`。',
  '中等', '["竞赛题","贪心","优先队列","区间"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5
0 30
5 10
15 20
20 25
25 35', '2',
  '复用已结束会议室'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3
1 2
2 3
3 4', '1',
  '首尾衔接'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1
0 100', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
1 5
1 5
1 5
1 5', '4',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4
0 10
2 3
3 4
4 5', '2',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '带冷却的任务调度', '# 带冷却的任务调度

## 题目描述
有若干任务，每个任务用一个大写字母表示。相同类型任务之间至少需要间隔 `K` 个时间单位；每个任务执行耗时 1，空闲也耗时 1。求完成全部任务的最短总时间。

## 输入格式
第一行输入 `N K`，第二行输入 `N` 个大写字母任务。

## 输出格式
输出最短总时间。

## 数据范围
`1 ≤ N ≤ 2×10^5`，`0 ≤ K ≤ 10^9`。',
  '中等', '["竞赛题","贪心","计数","堆"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '6 2
A A A B B B', '8',
  'A B idle A B idle A B'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '4 0
A A B C', '4',
  '无需冷却'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 100
A', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '5 1
A A A A A', '9',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '8 2
A A A B B C C D', '8',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '最小覆盖圆环区间', '# 最小覆盖圆环区间

## 题目描述
圆环长度为 `L`，有 `N` 个覆盖区间，每个区间沿顺时针方向从 `l_i` 覆盖到 `r_i`，允许跨越 0 点。请选择尽可能少的区间覆盖整个圆环，若无法覆盖输出 `-1`。

## 输入格式
第一行输入 `L N`，随后 `N` 行输入 `l_i r_i`，位置范围为 `[0,L)`。

## 输出格式
输出最少区间数量。

## 数据范围
`1 ≤ L ≤ 10^9`，`1 ≤ N ≤ 2×10^5`。',
  '困难', '["竞赛题","贪心","倍增","环形区间"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 3
0 4
4 8
8 0', '3',
  '三个区间刚好覆盖'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 2
0 3
5 8', '-1',
  '存在空隙'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 1
0 0', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '10 2
8 3
3 8', '2',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '12 4
10 2
2 5
5 9
9 10', '4',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '网格路径异或值', '# 网格路径异或值

## 题目描述
给定 `N×M` 整数网格，从左上角出发，每次只能向右或向下移动，直到右下角。路径异或值定义为经过所有格子数值的按位异或。给定目标 `K`，统计异或值恰好为 `K` 的路径数量。

## 输入格式
第一行输入 `N M K`，随后 `N` 行输入网格。

## 输出格式
输出路径数量。

## 数据范围
`1 ≤ N,M ≤ 20`，`N+M ≤ 40`，格子值和 `K` 在 32 位非负整数范围内。',
  '困难', '["竞赛题","状态压缩","Meet-in-the-middle","异或"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 2 6
1 2
4 3', '1',
  '两条路径中恰有一条满足'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1 5
5', '1',
  '只有一条路径'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 1 0
0', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 3 0
1 1 1
1 1 1', '3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 3 1
1 2 3
4 5 6
7 8 9', '1',
  '隐藏判题增强-3'
);

INSERT INTO problems (title, content, difficulty, tags) VALUES (
  '钥匙与门的迷宫', '# 钥匙与门的迷宫

## 题目描述
在 `N×M` 网格中，`.` 表示空地，`#` 表示墙，`S` 为起点，`T` 为终点。小写字母 `a` 到 `f` 表示钥匙，大写字母 `A` 到 `F` 表示对应的门，只有持有对应钥匙才能通过门。拾取钥匙后永久持有。求从 `S` 到 `T` 的最少移动步数。

## 输入格式
第一行输入 `N M`，随后 `N` 行输入网格。

## 输出格式
输出最少移动步数，不可达输出 `-1`。

## 数据范围
`1 ≤ N,M ≤ 200`，钥匙种类最多 6 种。',
  '困难', '["竞赛题","BFS","状态压缩","最短路"]'
);
SET @problem_id = LAST_INSERT_ID();
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '3 5
S.aA.
##.#T
.....', '5',
  '先取得钥匙再通过门'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 3
S#T
###', '-1',
  '终点不可达'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 2
ST', '1',
  '隐藏判题增强-1'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '1 4
SaAT', '3',
  '隐藏判题增强-2'
);
INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (
  @problem_id, '2 4
S.A.T
#a###', '-1',
  '隐藏判题增强-3'
);

COMMIT;
SELECT COUNT(*) AS question_count FROM problems;
SELECT COUNT(*) AS test_case_count FROM test_cases;

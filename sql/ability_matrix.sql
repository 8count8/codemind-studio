-- 能力矩阵数据库建表脚本
-- 创建日期: 2026-08-09

-- 1. 用户能力矩阵表（存储每个用户的当前能力评估结果）
CREATE TABLE IF NOT EXISTS `user_ability_matrix` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `user_id` VARCHAR(128) NOT NULL COMMENT '用户ID（关联users表）',
    `syntax_score` FLOAT NOT NULL DEFAULT 0 COMMENT '语法基础得分 (0-100)',
    `algorithm_score` FLOAT NOT NULL DEFAULT 0 COMMENT '算法思维得分 (0-100)',
    `project_score` FLOAT NOT NULL DEFAULT 0 COMMENT '项目实践得分 (0-100)',
    `debug_score` FLOAT NOT NULL DEFAULT 0 COMMENT '调试能力得分 (0-100)',
    `security_score` FLOAT NOT NULL DEFAULT 0 COMMENT '安全意识得分 (0-100)',
    `total_submissions` INT NOT NULL DEFAULT 0 COMMENT '累计提交次数',
    `level` VARCHAR(20) NOT NULL DEFAULT '初学者' COMMENT '综合等级: 初学者/初级/中级/高级/专家',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_user_id` (`user_id`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户能力矩阵表';

-- 2. 能力评估提交记录表（记录每次提交的评分详情）
CREATE TABLE IF NOT EXISTS `ability_submissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `user_id` VARCHAR(128) NOT NULL COMMENT '用户ID',
    `source_type` VARCHAR(50) NOT NULL DEFAULT 'code_submit' COMMENT '数据来源: code_submit/ai_review/quiz_answer',
    `source_id` VARCHAR(128) DEFAULT NULL COMMENT '来源ID（题目ID/审查ID等）',
    `syntax_score` FLOAT NOT NULL DEFAULT 0 COMMENT '本次语法基础得分 (0-100)',
    `algorithm_score` FLOAT NOT NULL DEFAULT 0 COMMENT '本次算法思维得分 (0-100)',
    `project_score` FLOAT NOT NULL DEFAULT 0 COMMENT '本次项目实践得分 (0-100)',
    `debug_score` FLOAT NOT NULL DEFAULT 0 COMMENT '本次调试能力得分 (0-100)',
    `security_score` FLOAT NOT NULL DEFAULT 0 COMMENT '本次安全意识得分 (0-100)',
    `detail` TEXT DEFAULT NULL COMMENT '评分详情（JSON格式，包含具体扣分项）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_source_type` (`source_type`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='能力评估提交记录表';

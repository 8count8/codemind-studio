"""
ML 评分模型（对应文档 §3.2 机器学习评分模型 V1.2+）

功能：使用随机森林模型基于代码特征向量输出 5 维评分，替代线性加权。

设计原则：
1. sklearn 为可选依赖，未安装时自动降级到启发式评分
2. 模型文件持久化到 models/ 目录，支持热加载
3. 特征提取与模型推理解耦，便于独立测试

对应文档：能力矩阵.md §3.2 机器学习评分模型
"""

import os
import logging
import math

# 可选导入 sklearn（未安装时降级到启发式）
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    import numpy as np
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# 模型文件路径
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'ability_scorer.pkl')

# 5 个维度的模型文件名
DIMENSION_MODELS = {
    'syntax_score': 'syntax_model.pkl',
    'algorithm_score': 'algorithm_model.pkl',
    'project_score': 'project_model.pkl',
    'debug_score': 'debug_model.pkl',
    'security_score': 'security_model.pkl',
}


def extract_code_features(code):
    """
    从代码文本提取特征向量

    特征维度（对应文档 §3.2）：
    1. code_lines: 代码行数
    2. comment_count: 注释行数
    3. loop_count: 循环数(for/while)
    4. condition_count: 条件数(if/elif/else)
    5. function_count: 函数数(def/function)
    6. class_count: 类数(class)
    7. exception_count: 异常处理数(try/except/raise)
    8. log_count: 日志数(print/logging)
    9. security_hits: 安全关键词命中数
    10. cyclomatic_complexity: 圈复杂度

    参数:
        code (str): 代码文本
    返回:
        list[float]: 10 维特征向量
    """
    if not code:
        return [0.0] * 10

    lines = code.strip().split('\n')
    code_lines = len(lines)
    comment_count = sum(1 for l in lines if '#' in l or '//' in l or '"""' in l)
    loop_count = code.count('for ') + code.count('while ')
    condition_count = code.count('if ') + code.count('elif ') + code.count('else:')
    function_count = code.count('def ') + code.count('function ')
    class_count = code.count('class ')
    exception_count = code.count('try') + code.count('except') + code.count('raise')
    log_count = code.count('print') + code.count('logging')

    security_keywords = ['sanitize', 'validate', 'escape', 'hash', 'encrypt',
                         '%s', 'parameter', 'prepare', 'bind']
    security_hits = sum(1 for kw in security_keywords if kw.lower() in code.lower())

    # 圈复杂度 ≈ 条件数 + 循环数 + 1
    cyclomatic_complexity = condition_count + loop_count + 1

    return [
        float(code_lines),
        float(comment_count),
        float(loop_count),
        float(condition_count),
        float(function_count),
        float(class_count),
        float(exception_count),
        float(log_count),
        float(security_hits),
        float(cyclomatic_complexity),
    ]


def predict_scores_with_ml(code):
    """
    使用 ML 模型预测 5 维评分

    若 sklearn 不可用或模型文件不存在，降级到启发式评分。

    参数:
        code (str): 代码文本
    返回:
        dict: {dimension: score} 5 维评分
    """
    features = extract_code_features(code)

    if not SKLEARN_AVAILABLE:
        return _heuristic_fallback(features)

    # 尝试加载已训练的模型
    scores = {}
    all_loaded = True
    for dim, model_file in DIMENSION_MODELS.items():
        model_path = os.path.join(MODEL_DIR, model_file)
        if not os.path.exists(model_path):
            all_loaded = False
            break
        try:
            model = joblib.load(model_path)
            pred = model.predict([features])[0]
            scores[dim] = max(0.0, min(100.0, float(pred)))
        except Exception as e:
            logging.warning(f"ML 模型 {dim} 加载失败: {e}")
            all_loaded = False
            break

    if not all_loaded:
        return _heuristic_fallback(features)

    return scores


def _heuristic_fallback(features):
    """
    启发式降级评分（sklearn 不可用或模型未训练时使用）

    基于特征向量的线性加权，与 evaluate_code_with_ai 逻辑一致。

    参数:
        features (list): extract_code_features 返回的特征向量
    返回:
        dict: 5 维评分
    """
    (code_lines, comment_count, loop_count, condition_count,
     function_count, class_count, exception_count, log_count,
     security_hits, complexity) = features

    return {
        'syntax_score': min(60 + code_lines * 2 + comment_count * 3, 100),
        'algorithm_score': min(40 + loop_count * 10 + condition_count * 5, 100),
        'project_score': min(35 + function_count * 15 + class_count * 20, 100),
        'debug_score': min(40 + exception_count * 12 + log_count * 5, 100),
        'security_score': min(30 + security_hits * 15, 100),
    }


def train_models(training_data):
    """
    训练 5 个维度的随机森林模型（需要标注样本）

    参数:
        training_data (list[dict]): 标注样本列表，每个样本含:
            - code: 代码文本
            - scores: {dimension: score} 专家标注分数
    返回:
        dict: 训练结果 {dimension: {'r2': float, 'trained': bool}}
    """
    if not SKLEARN_AVAILABLE:
        logging.warning("sklearn 不可用，无法训练 ML 模型")
        return {dim: {'r2': 0.0, 'trained': False} for dim in DIMENSION_MODELS}

    if len(training_data) < 10:
        logging.warning(f"训练样本不足（{len(training_data)} < 10），跳过训练")
        return {dim: {'r2': 0.0, 'trained': False} for dim in DIMENSION_MODELS}

    # 提取特征和标签
    X = [extract_code_features(item['code']) for item in training_data]
    results = {}

    os.makedirs(MODEL_DIR, exist_ok=True)

    for dim, model_file in DIMENSION_MODELS.items():
        y = [float(item['scores'].get(dim, 0)) for item in training_data]

        if len(set(y)) < 2:
            results[dim] = {'r2': 0.0, 'trained': False}
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        r2 = model.score(X_test, y_test) if X_test else 0.0

        model_path = os.path.join(MODEL_DIR, model_file)
        joblib.dump(model, model_path)

        results[dim] = {'r2': round(r2, 4), 'trained': True}
        logging.info(f"ML 模型 {dim} 训练完成，R²={r2:.4f}")

    return results


def is_ml_available():
    """检查 ML 模型是否可用（sklearn 已安装且模型文件存在）"""
    if not SKLEARN_AVAILABLE:
        return False
    return all(
        os.path.exists(os.path.join(MODEL_DIR, model_file))
        for model_file in DIMENSION_MODELS.values()
    )

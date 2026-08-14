from .user_login import (
    check_user_exists,
    register_user,
    send_verification_code,
    generate_code,
    handle_get_verification_code,
    handle_register,
    handle_login,
    handle_forgot_password_get_code,
    handle_forgot_password_reset,
    get_user_profile
)
# 导入常用的功能函数和类
from .user_operation_records import (
    log_function_usage,          # 记录用户功能使用日志
    upload_file_to_db,           # 处理上传文件并存储到数据库
    log_api_response,            # 记录后端 API 返回的代码文件
    get_user_history_combined,   # 查询用户的历史记录（整合版）
    delete_history_record        # 删除某条历史记录
)
from .user_code import save_code_to_db
from .favorites_topics import (
    get_favorites_with_question,      # 获取按时间排序的收藏列表（包含题目具体内容）
    get_favorites_without_question,   # 获取按时间排序的收藏列表（不包含题目具体内容）
    search_favorites_by_title         # 根据标题进行高级搜索（支持模糊匹配）
)
from .save_problem import save_problem_to_database

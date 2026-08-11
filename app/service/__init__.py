# 导入常用的功能函数和类
from .processing_operations import (
    detect_language,  # 判断文件内容的语言类型
    convert_to_code,  # 将非代码文件转换为对应的代码内容
    process_uploaded_file  # 处理上传文件，判断语言类型并生成代码文件
)
from .UserLoginService import UserLoginService
from .algorithm_service import generate_and_save_algorithm_problem  #AI算法题目生成并保存到数据库
from .QuestionService import QuestionService
from .FavoriteService import FavoriteService
from .ability_matrix_service import AbilityMatrixService  # 能力矩阵服务

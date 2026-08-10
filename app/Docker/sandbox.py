import subprocess
import tempfile
import os
import time
import logging

# 提取镜像名作为全局变量
PYTHON_IMAGE = 'python:3.9-slim'
JAVA_IMAGE = 'openjdk:17-slim'
JS_IMAGE = 'node:18-slim'
CPP_IMAGE = 'gcc:latest'

# 最小内存
MIN_MEMORY = '128m'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_python(code, input_data=None):
    """执行给定的Python代码，并通过Docker容器运行。

    Args:
        code (str): 要执行的Python代码字符串。
        input_data (Optional[Any]): 可选输入数据（当前未被使用）。

    Returns:
        tuple[float, bool, str, str]:
            - run_time: 执行时间（秒）
            - success: 执行是否成功（返回码是否为0）
            - output: 前20行输出内容（或None）
            - error: 错误信息/超时信息/异常信息
    """
    try:
        # 执行Docker容器中的Python代码并捕获输出/错误
        start_time = time.time()
        result = subprocess.run(['docker', 'run', '--rm', '-i', '--memory', MIN_MEMORY, PYTHON_IMAGE, 'python', '-c', code],
                                input=input_data, capture_output=True, text=True, timeout=10)
        end_time = time.time()
        run_time = end_time - start_time

        # 处理输出内容（截取前20行）
        output = result.stdout.strip().split('\n')[:20]
        output = '\n'.join(output)
        error = result.stderr
        success = result.returncode == 0
        return run_time, success, output, error
    except subprocess.TimeoutExpired:
        # 处理执行超时情况（10秒限制）
        return time.time() - start_time, False, None, "Execution timed out"
    except Exception as e:
        # 捕获其他异常并返回错误信息
        return 0, False, None, str(e)



def run_java(code, input_data=None):
    # 提取类名
    class_name = None
    for line in code.splitlines():
        if line.strip().startswith("public class"):
            class_name = line.strip().split(" ")[2]  # 提取类名
            break
    if not class_name:
        return 0, False, None, "No public class found in the code"

    file_name = f"{class_name}.java"  # 动态生成文件名
    with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False, dir=os.getcwd()) as f:
        f.write(code)
        original_file_path = f.name
        new_file_path = os.path.join(os.getcwd(), file_name)
        os.rename(original_file_path, new_file_path)
        file_path = new_file_path
    try:
        start_time = time.time()

        # 编译阶段
        logging.info(f"Compiling Java file: {os.path.basename(file_path)}")
        compile_result = subprocess.run(['docker', 'run', '--rm', '-v', f'{os.getcwd()}:/app', '--memory', MIN_MEMORY,
                                         JAVA_IMAGE, 'javac', f'/app/{os.path.basename(file_path)}'],
                                        capture_output=True, text=True, timeout=10)
        if compile_result.returncode != 0:
            end_time = time.time()
            run_time = end_time - start_time
            error_message = compile_result.stderr.strip()
            logging.error(f"Compilation failed: {error_message}")
            return run_time, False, None, f"Compilation error: {error_message}"

        # 运行阶段
        logging.info(f"Running Java class: {class_name}")
        run_result = subprocess.run(['docker', 'run', '--rm', '-v', f'{os.getcwd()}:/app', '--memory', MIN_MEMORY,
                                     JAVA_IMAGE, 'java', '-cp', '/app', class_name], input=input_data, capture_output=True, text=True,
                                    timeout=30)
        end_time = time.time()
        run_time = end_time - start_time
        output = run_result.stdout.strip().split('\n')[:20]
        output = '\n'.join(output)
        error = run_result.stderr
        success = run_result.returncode == 0
        return run_time, success, output, error
    except subprocess.TimeoutExpired:
        return time.time() - start_time, False, None, "Execution timed out"
    except Exception as e:
        return 0, False, None, str(e)
    finally:
        os.remove(file_path)
        class_file = os.path.splitext(file_path)[0] + '.class'
        if os.path.exists(class_file):
            os.remove(class_file)


def run_js(code, input_data=None):
    try:
        start_time = time.time()
        result = subprocess.run(['docker', 'run', '--rm', '--memory', MIN_MEMORY, '-i',
                                 JS_IMAGE, 'node', '-e', code], input=input_data, capture_output=True, text=True, timeout=30)
        end_time = time.time()
        run_time = end_time - start_time
        output = result.stdout.strip().split('\n')[:20]
        output = '\n'.join(output)
        error = result.stderr
        success = result.returncode == 0
        return run_time, success, output, error
    except subprocess.TimeoutExpired:
        return time.time() - start_time, False, None, "Execution timed out"
    except Exception as e:
        return 0, False, None, str(e)


def run_cpp(code, input_data=None):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, dir=os.getcwd()) as f:
        f.write(code)
        file_path = f.name
        output_file = os.path.splitext(file_path)[0]
    try:
        start_time = time.time()

        # 编译阶段
        logging.info(f"Compiling C++ file: {os.path.basename(file_path)}")
        compile_result = subprocess.run(['docker', 'run', '--rm', '-v', f'{os.getcwd()}:/app', '--memory', MIN_MEMORY,
                                         CPP_IMAGE, 'g++', f'/app/{os.path.basename(file_path)}', '-o',
                                         f'/app/{os.path.basename(output_file)}'], capture_output=True, text=True,
                                        timeout=30)
        if compile_result.returncode != 0:
            end_time = time.time()
            run_time = end_time - start_time
            error_message = compile_result.stderr.strip()
            logging.error(f"Compilation failed: {error_message}")
            return run_time, False, None, f"Compilation error: {error_message}"

        # 运行阶段
        logging.info(f"Running C++ binary: {os.path.basename(output_file)}")
        run_result = subprocess.run(['docker', 'run', '--rm', '-v', f'{os.getcwd()}:/app', '--memory', MIN_MEMORY,
                                     CPP_IMAGE, f'/app/{os.path.basename(output_file)}'], input=input_data, capture_output=True,
                                    text=True, timeout=10)
        end_time = time.time()
        run_time = end_time - start_time
        output = run_result.stdout.strip().split('\n')[:20]
        output = '\n'.join(output)
        error = run_result.stderr
        success = run_result.returncode == 0
        return run_time, success, output, error
    except subprocess.TimeoutExpired:
        return time.time() - start_time, False, None, "Execution timed out"
    except Exception as e:
        return 0, False, None, str(e)
    finally:
        os.remove(file_path)
        if os.path.exists(output_file):
            os.remove(output_file)




LANGUAGE_RUNNERS = {
    'python': run_python,
    'java': run_java,
    'javascript': run_js,
    'cpp': run_cpp
}


def execute_code(code: str, language: str, task_id: str, input_data=None) -> dict:
    """纯函数调用入口"""
    if not all([code, language, task_id]):
        raise ValueError("Code, language and uuid are required")

    runner = LANGUAGE_RUNNERS.get(language)
    if not runner:
        raise ValueError(f"Unsupported language: {language}")

    run_time, success, output, error = runner(code, input_data)
    return {
        "id": task_id,
        "run_time": run_time,
        "success": success,
        "output": output,
        "error": error
    }


# 测试方法
def test_run_python():
    input_data = "Nice to meet you!"
    code = "a=input()\nprint(f'Hello, Python!{a}')"
    result = run_python(code, input_data)
    print(f"Python test result: {result}")


def test_run_java():
    code = """
    public class HelloWorld {
        public static void main(String[] args) {
            System.out.println("Hello, World!");
        }
    }
    """
    result = run_java(code)
    print(f"Java test result: {result}")


def test_run_js():
    code = "console.log('Hello, JavaScript!');"
    result = run_js(code)
    print(f"JavaScript test result: {result}")


def test_run_cpp():
    code = """
    #include <iostream>
    int main() {
        std::cout << "Hello, C++!" << std::endl;
        return 0;
    }
    """
    result = run_cpp(code)
    print(f"C++ test result: {result}")


if __name__ == '__main__':
    test_run_python()
    test_run_java()
    test_run_js()
    test_run_cpp()
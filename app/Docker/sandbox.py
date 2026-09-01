"""
代码沙箱执行器（双模式：Docker 隔离优先 / 本机兜底）

两种模式自动切换：
  A) DOCKER 模式：检测到 `docker info` 成功时使用 → 真正隔离（内存/CPU/文件系统）
     推荐：开发机、服务器部署、需要隔离用户代码的任何生产环境
  B) NATIVE 模式：用户电脑没有装 Docker Desktop → 用 subprocess 直接调本机解释器
     适用：方案 C 桌面版发给普通 Windows 用户（不要求他们装 Docker）
     安全：使用临时目录 + 进程 timeout + 环境变量清理；仍允许访问本机文件系统，
           仅用于"已知用户自己的代码"场景（CodeMind Studio 本来就是自用/教学机）。
"""

import os
import re
import io
import sys
import shutil
import time
import uuid
import shlex
import signal
import logging
import tempfile
import subprocess
import threading
import base64
from typing import Tuple, Optional, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger('sandbox')

# -----------------------------------------------------------------------------
# 镜像（Docker 模式使用）
# -----------------------------------------------------------------------------
PYTHON_IMAGE = os.environ.get('SANDBOX_PYTHON_IMAGE', 'python:3.11-slim')
JAVA_IMAGE   = os.environ.get('SANDBOX_JAVA_IMAGE',   'eclipse-temurin:17-jdk-jammy')
JS_IMAGE     = os.environ.get('SANDBOX_JS_IMAGE',     'node:20-slim')
CPP_IMAGE    = os.environ.get('SANDBOX_CPP_IMAGE',    'gcc:12')
C_IMAGE      = os.environ.get('SANDBOX_C_IMAGE',      'gcc:12')

MIN_MEMORY = '256m'

# NATIVE 模式超时（Docker 模式用 subprocess timeout 参数即可）
# Reserve time for forced container cleanup so the end-to-end sandbox API stays
# within the documented 6-second SLA while the execution budget remains <= 5s.
DEFAULT_TIMEOUT = min(5.0, max(1.0, float(os.environ.get('SANDBOX_TIMEOUT', '5'))))

# 输出截断：避免用户代码死循环打印把进程内存打爆
OUTPUT_MAX_LINES = 50
OUTPUT_MAX_BYTES = 64 * 1024  # 64KB


# -----------------------------------------------------------------------------
# 运行时检测：有 Docker 用 Docker；否则本机
# -----------------------------------------------------------------------------
_SANDBOX_MODE_CACHE: Optional[str] = None
_EXECUTION_METRICS = threading.local()

def get_sandbox_mode(force: bool = False) -> str:
    """返回 'docker' 或 'native'；结果缓存到进程内"""
    global _SANDBOX_MODE_CACHE
    if _SANDBOX_MODE_CACHE is None or force:
        override = (os.environ.get('SANDBOX_MODE') or '').strip().lower()
        if override in ('docker', 'native'):
            _SANDBOX_MODE_CACHE = override
            return _SANDBOX_MODE_CACHE
        try:
            r = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=8)
            _SANDBOX_MODE_CACHE = 'docker' if r.returncode == 0 else 'native'
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            _SANDBOX_MODE_CACHE = 'native'
        log.info(f"Sandbox mode auto-detect: {_SANDBOX_MODE_CACHE}")
    return _SANDBOX_MODE_CACHE


# -----------------------------------------------------------------------------
# 工具函数：统一运行结果格式
# -----------------------------------------------------------------------------
def _trim_output(text: Optional[str]) -> Optional[str]:
    """截断输出并保留尾部（避免超长输出污染日志/前端）"""
    if text is None:
        return None
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if len(text) > OUTPUT_MAX_BYTES:
        head = text[: OUTPUT_MAX_BYTES // 2]
        tail = text[-OUTPUT_MAX_BYTES // 2:]
        text = head + f"\n... [truncated, total {len(text)} chars] ...\n" + tail
    lines = text.split('\n')
    if len(lines) > OUTPUT_MAX_LINES:
        lines = lines[: OUTPUT_MAX_LINES // 2] + \
                [f"... [truncated, total {len(lines)} lines] ..."] + \
                lines[-OUTPUT_MAX_LINES // 2:]
        text = '\n'.join(lines)
    return text.strip()


def _runner_return(start_ts: float, success: bool, output: Optional[str], error: Optional[str]) -> Tuple[float, bool, Optional[str], Optional[str]]:
    return (round(time.time() - start_ts, 3), bool(success), _trim_output(output), _trim_output(error))


# =============================================================================
#                        D O C K E R   R U N N E R S
# =============================================================================

def _docker_run(cmd: list, input_data: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT, **run_kwargs) -> subprocess.CompletedProcess:
    container_name = f"codemind-sandbox-{uuid.uuid4().hex[:12]}"
    base = [
        'docker', 'run', '--rm', '--name', container_name, '-i',
        '--memory', MIN_MEMORY,
        '--cpus', '0.5',
        '--pids-limit', '64',
        '--network', 'none',
        '--read-only',
        '--tmpfs', '/tmp:rw,exec,nosuid,size=64m',
        '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges',
        '--user', '65534:65534',
    ]
    for key in ('-v', '-w', '--entrypoint', '-e'):
        if key in run_kwargs:
            v = run_kwargs.pop(key)
            if isinstance(v, list):
                for item in v:
                    base += [key, item]
            else:
                base += [key, v]
    full = base + cmd
    log.info("Docker exec: %s", " ".join(shlex.quote(x) for x in full[:12]) + (" ..." if len(full) > 12 else ""))
    proc = subprocess.Popen(full, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, **run_kwargs)
    stop_stats = threading.Event()
    peak = [0.0]

    def sample_memory():
        unit_scale = {'B': 1 / (1024 * 1024), 'KiB': 1 / 1024, 'MiB': 1, 'GiB': 1024}
        while not stop_stats.wait(0.08):
            try:
                stat = subprocess.run(
                    ['docker', 'stats', '--no-stream', '--format', '{{.MemUsage}}', container_name],
                    capture_output=True, text=True, timeout=0.6,
                )
                match = re.search(r'([0-9.]+)\s*(B|KiB|MiB|GiB)', stat.stdout or '')
                if match:
                    peak[0] = max(peak[0], float(match.group(1)) * unit_scale[match.group(2)])
            except Exception:
                pass

    monitor = threading.Thread(target=sample_memory, daemon=True)
    monitor.start()
    try:
        stdout, stderr = proc.communicate(input=input_data, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(['docker', 'rm', '-f', container_name], capture_output=True, timeout=0.75)
        except Exception:
            pass
        try:
            proc.kill()
            proc.wait(timeout=0.2)
        except Exception:
            pass
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            try:
                stream.close()
            except Exception:
                pass
        raise
    finally:
        stop_stats.set()
        monitor.join(timeout=0.1)
        _EXECUTION_METRICS.memory_peak_mb = round(peak[0], 2)
    return subprocess.CompletedProcess(full, proc.returncode, stdout, stderr)


def run_python_docker(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    try:
        r = _docker_run([PYTHON_IMAGE, 'python', '-c', code], input_data=input_data, timeout=DEFAULT_TIMEOUT)
        return _runner_return(t0, r.returncode == 0, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return _runner_return(t0, False, None, f"Execution timed out (>{DEFAULT_TIMEOUT}s)")
    except Exception as e:
        return _runner_return(t0, False, None, str(e))


def run_js_docker(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    try:
        r = _docker_run([JS_IMAGE, 'node', '-e', code], input_data=input_data, timeout=DEFAULT_TIMEOUT)
        return _runner_return(t0, r.returncode == 0, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return _runner_return(t0, False, None, f"Execution timed out (>{DEFAULT_TIMEOUT}s)")
    except Exception as e:
        return _runner_return(t0, False, None, str(e))


def _extract_java_class(code: str) -> Optional[str]:
    m = re.search(r'\bpublic\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', code)
    return m.group(1) if m else None


def run_java_docker(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    class_name = _extract_java_class(code)
    if not class_name:
        return _runner_return(t0, False, None, "No public class found in Java code")
    try:
        encoded = base64.b64encode(code.encode('utf-8')).decode('ascii')
        script = (
            f'printf "%s" "$CODE_B64" | base64 -d > /tmp/{class_name}.java && '
            # Java 11+ source-file mode compiles and runs in one JVM startup,
            # which keeps the 0.5-CPU sandbox inside the 5-second budget.
            f'java /tmp/{class_name}.java'
        )
        r = _docker_run(
            [JAVA_IMAGE, 'sh', '-lc', script], input_data=input_data,
            timeout=DEFAULT_TIMEOUT, **{'-e': [f'CODE_B64={encoded}']}
        )
        return _runner_return(t0, r.returncode == 0, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return _runner_return(t0, False, None, "Execution timed out")
    except Exception as e:
        return _runner_return(t0, False, None, str(e))


def _run_compiled_lang_docker(code: str, compiler: str, src_ext: str, image: str, input_data: Optional[str] = None,
                              cxx_flags: Optional[list] = None):
    t0 = time.time()
    try:
        encoded = base64.b64encode(code.encode('utf-8')).decode('ascii')
        flags = ' '.join(shlex.quote(flag) for flag in (cxx_flags or []))
        script = (
            f'printf "%s" "$CODE_B64" | base64 -d > /tmp/main.{src_ext} && '
            f'{compiler} /tmp/main.{src_ext} -o /tmp/main {flags} && /tmp/main'
        )
        r = _docker_run(
            [image, 'sh', '-lc', script], input_data=input_data,
            timeout=DEFAULT_TIMEOUT, **{'-e': [f'CODE_B64={encoded}']}
        )
        return _runner_return(t0, r.returncode == 0, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return _runner_return(t0, False, None, "Execution timed out")
    except Exception as e:
        return _runner_return(t0, False, None, str(e))


def run_cpp_docker(code: str, input_data: Optional[str] = None):
    return _run_compiled_lang_docker(code, 'g++', 'cpp', CPP_IMAGE, input_data=input_data,
                                     cxx_flags=['-std=c++17', '-O2', '-Wall'])


def run_c_docker(code: str, input_data: Optional[str] = None):
    return _run_compiled_lang_docker(code, 'gcc', 'c', C_IMAGE, input_data=input_data,
                                     cxx_flags=['-std=c11', '-O2', '-Wall'])


# =============================================================================
#                        N A T I V E   R U N N E R S
# =============================================================================

def _find_exe(names, default=None):
    """在 PATH 里找命令；第一个找到就返回"""
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return default


def _python_executable():
    """优先复用当前解释器，避开 WindowsApps 中不可执行的商店占位符。"""
    current = os.path.abspath(sys.executable or '')
    if (
        current
        and os.path.isfile(current)
        and not getattr(sys, 'frozen', False)
        and 'python' in os.path.basename(current).lower()
    ):
        return current
    candidates = ['python3', 'python']
    if os.name == 'nt':
        candidates.insert(0, 'py')
    return _find_exe(candidates, None)


def _safe_env():
    """返回一个清理过的环境变量 dict（避免沙箱进程读到敏感 env）"""
    env = os.environ.copy()
    for k in list(env.keys()):
        if k.upper() in (
            'DB_PASSWORD', 'SECRET_KEY', 'EMAIL_PASSWORD', 'VOLCENGINE_API_KEY',
            'OLLAMA_API_KEY', 'ADMIN_PASSWORD', 'PASSWORD', 'COOKIE_SECRET'
        ):
            env.pop(k, None)
    # 固定 LC_ALL 防止不同机器的默认 locale 导致 stdout 乱码
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    env.setdefault('LANG', 'en_US.UTF-8')
    return env


def _subprocess_run_native(cmd: list, input_data: Optional[str],
                           timeout: int, cwd: Optional[str],
                           extra_env: Optional[dict] = None) -> Tuple[int, str, str]:
    """带 kill 的 subprocess；timeout 超时强制终止（Unix:SIGKILL / Win:TerminateProcess）

    返回 (returncode, stdout, stderr)；
    如果在 timeout 内没有结束 → 返回码 -999，stderr = "Execution timed out (>Ns)"
    """
    env = _safe_env()
    if extra_env:
        env.update(extra_env)
    # Windows：CREATE_NO_WINDOW；Unix：新进程组
    creationflags = 0
    start_new_session = False
    if os.name == 'nt':
        creationflags = 0x08000000  # CREATE_NO_WINDOW
    else:
        start_new_session = True

    try:
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace',
            cwd=cwd, env=env,
            creationflags=creationflags, start_new_session=start_new_session,
        )
    except FileNotFoundError as e:
        return 127, '', f"Required interpreter/compiler not found in PATH: {e}"

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    def _copy_stream(src, dst, limit: int):
        written = 0
        try:
            for line in src:
                if written >= limit:
                    continue
                dst.write(line)
                written += len(line)
        except Exception:
            pass

    out_t = threading.Thread(target=_copy_stream, args=(proc.stdout, stdout_buf, OUTPUT_MAX_BYTES), daemon=True)
    err_t = threading.Thread(target=_copy_stream, args=(proc.stderr, stderr_buf, OUTPUT_MAX_BYTES), daemon=True)
    out_t.start(); err_t.start()

    timed_out = threading.Event()  # 明确的超时标记：被 killer 触发后设为 True

    def _timeout_killer():
        # 等主流程 proc.wait() 在指定 timeout 内完成；没有完成就强杀 + 打标记
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out.set()
            try:
                if os.name == 'nt':
                    proc.kill()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass

    killer = threading.Thread(target=_timeout_killer, daemon=True)
    killer.start()

    if input_data:
        try:
            proc.stdin.write(input_data)
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
    try:
        proc.stdin.close()
    except Exception:
        pass

    # 真正等进程结束 + killer 会保证不超过 timeout
    try:
        rc = proc.wait(timeout=timeout + 5)
    except subprocess.TimeoutExpired:
        timed_out.set()
        try:
            proc.kill()
        except Exception:
            pass
        rc = proc.wait()

    killer.join(timeout=1)
    out_t.join(timeout=1)
    err_t.join(timeout=1)

    if timed_out.is_set():
        return -999, stdout_buf.getvalue(), f"Execution timed out (>{timeout}s)"
    return rc, stdout_buf.getvalue(), stderr_buf.getvalue()


# --- Python native ---
def run_python_native(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    exe = _python_executable()
    if not exe:
        return _runner_return(t0, False, None,
                              "Python interpreter not found in PATH. Please install Python 3.9+.")
    tmp = tempfile.mkdtemp(prefix='py_sandbox_')
    src = os.path.join(tmp, 'main.py')
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        cmd = [exe, src]
        rc, out, err = _subprocess_run_native(cmd, input_data, timeout=DEFAULT_TIMEOUT, cwd=tmp)
        if rc == -999:
            return _runner_return(t0, False, None, err or f"Execution timed out (>{DEFAULT_TIMEOUT}s)")
        return _runner_return(t0, rc == 0, out, err)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- JS native ---
def run_js_native(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    exe = _find_exe(['node'])
    if not exe:
        return _runner_return(t0, False, None,
                              "Node.js not found in PATH. Please install Node.js LTS (18/20).")
    tmp = tempfile.mkdtemp(prefix='js_sandbox_')
    src = os.path.join(tmp, 'main.mjs')
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        rc, out, err = _subprocess_run_native([exe, src], input_data, timeout=DEFAULT_TIMEOUT, cwd=tmp)
        if rc == -999:
            return _runner_return(t0, False, None, err or "Execution timed out")
        return _runner_return(t0, rc == 0, out, err)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- Java native ---
def run_java_native(code: str, input_data: Optional[str] = None):
    t0 = time.time()
    javac = _find_exe(['javac'])
    java = _find_exe(['java'])
    if not (javac and java):
        return _runner_return(t0, False, None,
                              "JDK (javac+java) not found in PATH. Please install JDK 17+.")
    class_name = _extract_java_class(code)
    if not class_name:
        return _runner_return(t0, False, None, "No public class found in Java code")
    tmp = tempfile.mkdtemp(prefix='java_sandbox_')
    src = os.path.join(tmp, f"{class_name}.java")
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        rc, out, err = _subprocess_run_native([javac, f"{class_name}.java"], None,
                                               timeout=20, cwd=tmp)
        if rc != 0:
            return _runner_return(t0, False, None, f"Compilation error: {err}")
        rc, out, err = _subprocess_run_native([java, '-cp', '.', class_name], input_data,
                                               timeout=DEFAULT_TIMEOUT, cwd=tmp)
        if rc == -999:
            return _runner_return(t0, False, None, err or "Execution timed out")
        return _runner_return(t0, rc == 0, out, err)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _native_compile_run(code, compiler, src_ext, bin_name, compile_flags, runner, input_data):
    """C/C++ 公用：编译 → 运行"""
    t0 = time.time()
    cc = _find_exe([compiler])
    if not cc:
        if compiler == 'g++':
            msg = ("g++ not found in PATH. On Windows install MinGW-w64 or "
                   "Visual Studio Build Tools and add g++ to PATH.")
        else:
            msg = ("gcc not found in PATH. On Windows install MinGW-w64 or "
                   "Visual Studio Build Tools and add gcc to PATH.")
        return _runner_return(t0, False, None, msg)
    tmp = tempfile.mkdtemp(prefix=f'{compiler}_sandbox_')
    src = os.path.join(tmp, f"main.{src_ext}")
    try:
        with open(src, 'w', encoding='utf-8') as f:
            f.write(code)
        bin_path = os.path.join(tmp, bin_name)
        compile_cmd = [cc, src, '-o', bin_path] + list(compile_flags)
        rc, out, err = _subprocess_run_native(compile_cmd, None, timeout=30, cwd=tmp)
        if rc != 0:
            return _runner_return(t0, False, None, f"Compilation error: {err}")
        rc, out, err = _subprocess_run_native([bin_path], input_data, timeout=DEFAULT_TIMEOUT, cwd=tmp)
        if rc == -999:
            return _runner_return(t0, False, None, err or "Execution timed out")
        return _runner_return(t0, rc == 0, out, err)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_cpp_native(code: str, input_data: Optional[str] = None):
    return _native_compile_run(code, 'g++', 'cpp', 'main.exe' if os.name == 'nt' else 'main',
                               ['-std=c++17', '-O2', '-Wall'], None, input_data)


def run_c_native(code: str, input_data: Optional[str] = None):
    return _native_compile_run(code, 'gcc', 'c', 'main.exe' if os.name == 'nt' else 'main',
                               ['-std=c11', '-O2', '-Wall'], None, input_data)


# =============================================================================
#   D I S P A T C H :   根据 get_sandbox_mode() 自动选择 Docker / Native
# =============================================================================

def _dispatch(docker_runner: Callable, native_runner: Callable, code: str, input_data: Optional[str]):
    mode = get_sandbox_mode()
    _EXECUTION_METRICS.memory_peak_mb = None
    if mode == 'docker':
        try:
            return docker_runner(code, input_data)
        except Exception as e:
            if (os.environ.get('SANDBOX_MODE') or '').strip().lower() == 'docker':
                raise RuntimeError(f"Docker sandbox unavailable: {e}") from e
            log.warning("Docker runner failed (%s); fallback to native: %s", type(e).__name__, e)
            return native_runner(code, input_data)
    return native_runner(code, input_data)


def run_python(code, input_data=None):
    return _dispatch(run_python_docker, run_python_native, code, input_data)

def run_java(code, input_data=None):
    return _dispatch(run_java_docker, run_java_native, code, input_data)

def run_js(code, input_data=None):
    return _dispatch(run_js_docker, run_js_native, code, input_data)

def run_cpp(code, input_data=None):
    return _dispatch(run_cpp_docker, run_cpp_native, code, input_data)

def run_c(code, input_data=None):
    """额外支持 C 语言（题库里可能有 C）"""
    return _dispatch(run_c_docker, run_c_native, code, input_data)


LANGUAGE_RUNNERS = {
    'python':     run_python,
    'python3':    run_python,
    'java':       run_java,
    'javascript': run_js,
    'js':         run_js,
    'node':       run_js,
    'cpp':        run_cpp,
    'c++':        run_cpp,
    'c':          run_c,
}


def _normalize_lang(lang: str) -> str:
    key = (lang or '').strip().lower()
    if key in LANGUAGE_RUNNERS:
        return key
    # 常见别名
    aliases = {
        'py': 'python', 'python3': 'python',
        'javascript': 'javascript', 'typescript': 'javascript',  # ts 暂按 node 跑会失败，但至少进同一条链路
        'c++': 'cpp', 'cxx': 'cpp', 'g++': 'cpp',
    }
    if key in aliases:
        return aliases[key]
    raise ValueError(f"Unsupported language: {lang}")


def execute_code(code: str, language: str, task_id: str, input_data=None) -> dict:
    """对外统一入口（task_id 仅作审计用途）"""
    if not code or not language or not task_id:
        raise ValueError("Code, language and task_id are required")
    runner = LANGUAGE_RUNNERS[_normalize_lang(language)]
    run_time, success, output, error = runner(code, input_data)
    return {
        "id": task_id,
        "run_time": run_time,
        "success": success,
        "output": output,
        "error": error,
        "sandbox_mode": get_sandbox_mode(),
        "memory_peak_mb": getattr(_EXECUTION_METRICS, 'memory_peak_mb', None),
        "memory_limit_mb": 256,
    }


def check_runtime_requirements(language: str) -> dict:
    """
    返回给前端"当前用户电脑能不能跑该语言"的诊断结果。
    用于方案 C 桌面版：弹窗告诉用户"你本机缺 Node/JDK/g++"并给出安装指引。
    """
    lang = (language or '').strip().lower()
    mode = get_sandbox_mode()
    if mode == 'docker':
        return {"available": True, "mode": "docker",
                "message": "Using Docker sandbox (fully isolated; no local compiler needed)."}
    spec = {
        # key: lang -> (exe_groups_list[每组是 OR 关系], 需求描述文字)
        # exe_groups_list: 外层 AND（每组都要命中）；组内多个名称 OR
        'python':     ([['python3', 'py -3', 'python']],           "Python 3.9+"),
        'javascript': ([['node']],                                    "Node.js 18/20 LTS"),
        'java':       ([['javac'], ['java']],                         "JDK 17+ (javac + java)"),
        'cpp':        ([['g++']],                                     "MinGW-w64 g++ or Visual C++"),
        'c':          ([['gcc']],                                     "MinGW-w64 gcc or Visual C++"),
    }
    if lang not in spec:
        return {"available": False, "mode": mode, "message": f"Unknown language: {language}"}
    exe_groups, need = spec[lang]
    if lang == 'python':
        ok = _python_executable() is not None
    else:
        ok = all(
            _find_exe(group if isinstance(group, list) else [group]) is not None
            for group in exe_groups
        )
    return {
        "available": ok,
        "mode": mode,
        "need": need,
        "message": "OK" if ok else (
            f"{need} not found in PATH (native sandbox). "
            "Recommended: install Docker Desktop (fully isolated, no local compiler needed), "
            f"or install {need} locally and add to PATH."
        ),
    }


# =============================================================================
# 本地测试：python -m app.Docker.sandbox
# =============================================================================
def _selftest():
    samples = [
        ('python',     "print('hello from python:', sum(range(10)))"),
        ('javascript', "console.log('hello from js', 1+2+3);"),
        ('cpp',        "#include <iostream>\nint main(){std::cout << \"hello from cpp\" << std::endl; return 0;}"),
    ]
    print(f"[selftest] sandbox_mode={get_sandbox_mode()}")
    for lang, code in samples:
        try:
            t = time.time()
            rt, ok, out, err = LANGUAGE_RUNNERS[lang](code)
            print(f"[{lang:10s}] ok={ok} time={rt:6.2f}s elapsed={time.time()-t:6.2f}s")
            if out: print("  stdout:", out.replace("\n", " ⏎ "))
            if err: print("  stderr:", err.replace("\n", " ⏎ ")[:500])
        except Exception as e:
            print(f"[{lang:10s}] EXCEPTION: {e}")


if __name__ == '__main__':
    _selftest()

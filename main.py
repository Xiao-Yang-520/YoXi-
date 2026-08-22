import flet as ft
import urllib.request
import json
import os
import sys
import importlib.util
import tempfile
import time
import shutil

# ── 读取配置 ──
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "app_name": "YoXi邮箱",
            "app_version": "1.0.0",
            "window_width": 375,
            "window_height": 812,
        }

APP_CONFIG = load_config()

# ── 下载远程代码 ──
def download_remote_code():
    url = APP_CONFIG.get("remote_code_url", "")
    if not url:
        return None, "未配置远程代码地址"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                return None, f"HTTP {resp.status}"
            code = resp.read().decode("utf-8")
            if len(code) < 100:
                return None, "远程代码内容过短"
            # 验证是否是有效的 Python 代码（必须包含 flet 导入和 main 函数）
            if "import flet" not in code and "from flet" not in code:
                return None, "远程代码不是有效的 Flet 应用"
            if "def main" not in code:
                return None, "远程代码缺少 main 函数"
            # 保存到本地缓存
            cache_dir = os.path.join(tempfile.gettempdir(), "yoxi_cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, "app_code.py")
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(code)
            # 把 config.json 也复制到缓存目录，让远程代码能找到配置
            builtin_dir = os.path.dirname(os.path.abspath(__file__))
            config_src = os.path.join(builtin_dir, "config.json")
            config_dst = os.path.join(cache_dir, "config.json")
            if os.path.exists(config_src):
                shutil.copy2(config_src, config_dst)
            return cache_path, "远程代码加载成功"
    except Exception as e:
        return None, f"下载失败：{str(e)[:50]}"

# ── 加载本地缓存代码 ──
def load_cached_code():
    cache_dir = os.path.join(tempfile.gettempdir(), "yoxi_cache")
    cache_path = os.path.join(cache_dir, "app_code.py")
    if os.path.exists(cache_path):
        # 确保 config.json 也在缓存目录
        builtin_dir = os.path.dirname(os.path.abspath(__file__))
        config_src = os.path.join(builtin_dir, "config.json")
        config_dst = os.path.join(cache_dir, "config.json")
        if os.path.exists(config_src):
            shutil.copy2(config_src, config_dst)
        return cache_path
    return None

# ── 加载内置代码 ──
def load_builtin_code():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_code.py")

# ── 动态加载模块 ──
def load_module_from_path(path):
    spec = importlib.util.spec_from_file_location("app_module", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["app_module"] = module
    spec.loader.exec_module(module)
    return module

def main(page: ft.Page):
    page.title = APP_CONFIG.get("app_name", "YoXi邮箱")
    page.window_width = APP_CONFIG.get("window_width", 375)
    page.window_height = APP_CONFIG.get("window_height", 812)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    # ── 加载界面 ──
    app_name = APP_CONFIG.get("app_name", "YoXi邮箱")
    app_version = APP_CONFIG.get("app_version", "1.0.0")

    title_text = ft.Text(app_name, size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    subtitle_text = ft.Text(f"v{app_version}", size=14, color=ft.colors.GREY_400, text_align=ft.TextAlign.CENTER)
    status_text = ft.Text("正在检查更新...", size=14, text_align=ft.TextAlign.CENTER)
    progress = ft.ProgressBar(width=280, value=0)

    loading_view = ft.Container(
        content=ft.Column([
            ft.Container(height=80),
            ft.Container(content=title_text, alignment=ft.alignment.center),
            ft.Container(content=subtitle_text, alignment=ft.alignment.center),
            ft.Container(height=40),
            ft.Container(
                content=ft.Column([
                    ft.Container(content=status_text, alignment=ft.alignment.center, padding=ft.padding.symmetric(vertical=10)),
                    ft.Container(content=progress, alignment=ft.alignment.center, padding=ft.padding.symmetric(horizontal=20)),
                ], spacing=0),
                alignment=ft.alignment.center,
            ),
            ft.Container(expand=True),
            ft.Container(content=ft.Text("远程热更新模式", size=12, color=ft.colors.GREY_300, text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center, padding=ft.padding.only(bottom=30)),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        padding=ft.padding.all(20),
    )

    page.add(loading_view)
    page.update()

    # ── 进度动画 ──
    for i in range(1, 31):
        progress.value = i / 100
        page.update()
        time.sleep(0.02)

    # ── 下载远程代码 ──
    status_text.value = "正在下载最新代码..."
    page.update()

    code_path, msg = download_remote_code()

    for i in range(31, 61):
        progress.value = i / 100
        page.update()
        time.sleep(0.02)

    if code_path:
        status_text.value = msg
        source = "remote"
    else:
        # 尝试加载本地缓存
        cached = load_cached_code()
        if cached:
            code_path = cached
            status_text.value = "使用缓存代码"
            source = "cache"
        else:
            code_path = load_builtin_code()
            status_text.value = f"{msg}，使用内置代码"
            source = "builtin"

    page.update()

    for i in range(61, 91):
        progress.value = i / 100
        page.update()
        time.sleep(0.02)

    # ── 动态加载并启动应用 ──
    try:
        status_text.value = "正在启动应用..."
        page.update()

        module = load_module_from_path(code_path)

        for i in range(91, 101):
            progress.value = i / 100
            page.update()
            time.sleep(0.02)

        if hasattr(module, "main"):
            # 清空加载界面，启动实际应用
            page.clean()
            module.main(page)
        else:
            status_text.value = "错误：代码中没有 main 函数"
            page.update()
    except Exception as e:
        # 如果远程/缓存代码加载失败，回退到内置代码
        if source != "builtin":
            try:
                status_text.value = f"加载失败，回退内置代码..."
                page.update()
                builtin_path = load_builtin_code()
                module = load_module_from_path(builtin_path)
                if hasattr(module, "main"):
                    page.clean()
                    module.main(page)
                else:
                    status_text.value = "内置代码也无法加载"
                    page.update()
            except Exception as e2:
                status_text.value = f"启动失败：{str(e2)[:60]}"
                page.update()
        else:
            status_text.value = f"启动失败：{str(e)[:60]}"
            page.update()

if __name__ == "__main__":
    ft.app(target=main)

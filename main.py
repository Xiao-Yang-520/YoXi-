import flet as ft
import importlib.util
import os
import sys

# ── 加载内置应用代码 ──
def load_app_module():
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_code.py")
    spec = importlib.util.spec_from_file_location("app_code", app_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["app_code"] = module
    spec.loader.exec_module(module)
    return module

def main(page: ft.Page):
    module = load_app_module()
    module.main(page)

if __name__ == "__main__":
    ft.app(target=main)

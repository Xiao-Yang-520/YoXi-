import flet as ft
import os
import sys
import traceback

# 把当前目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main(page: ft.Page):
    try:
        # 直接导入 app_code 模块
        import app_code
        app_code.main(page)
    except Exception as e:
        # 如果出错，显示错误信息，避免白屏
        error_text = ft.Text(
            f"启动错误:\n{str(e)}\n\n{traceback.format_exc()}",
            size=12, color=ft.colors.RED, selectable=True
        )
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.RED),
                    ft.Container(height=20),
                    ft.Text("应用启动失败", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Container(
                        content=error_text,
                        padding=10,
                        bgcolor=ft.colors.GREY_100,
                        border_radius=8,
                        width=350,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
        )
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
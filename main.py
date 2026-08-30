import flet as ft
import os
import sys
import traceback
import threading

# 把当前目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main(page: ft.Page):
    # 先显示一个简单的加载页面，避免Flet默认加载页
    try:
        page.title = "YoXi邮箱"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.spacing = 0
        page.bgcolor = ft.colors.BLACK
        
        # 显示加载中
        loading_text = ft.Text("正在加载...", size=16, color=ft.colors.WHITE)
        progress = ft.ProgressBar(width=200, color="#007AFF", bgcolor=ft.colors.with_opacity(0.3, ft.colors.WHITE))
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Container(height=200),
                    ft.Text("YoXi邮箱", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Container(height=20),
                    progress,
                    ft.Container(height=10),
                    loading_text,
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.colors.BLACK,
            )
        )
        page.update()
    except Exception as e:
        print(f"显示加载页失败: {e}")
    
    # 在后台线程中导入app_code并执行
    def load_and_run():
        try:
            loading_text.value = "正在初始化..."
            progress.value = 0.3
            page.update()
            
            # 导入app_code模块
            import app_code
            
            loading_text.value = "正在启动..."
            progress.value = 0.7
            page.update()
            
            # 执行app_code的main函数
            app_code.main(page)
            
        except Exception as e:
            # 如果出错，显示错误信息
            error_detail = traceback.format_exc()
            print(f"启动错误: {e}")
            print(error_detail)
            
            def show_error():
                try:
                    page.controls.clear()
                    page.bgcolor = ft.colors.WHITE
                    page.padding = 20
                    page.add(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.RED),
                                ft.Container(height=20),
                                ft.Text("应用启动失败", size=20, weight=ft.FontWeight.BOLD),
                                ft.Container(height=10),
                                ft.Container(
                                    content=ft.Text(
                                        f"错误: {str(e)}\n\n{error_detail}",
                                        size=11, color=ft.colors.RED, selectable=True
                                    ),
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
                except Exception as e2:
                    print(f"显示错误页面失败: {e2}")
            
            page.run_thread(show_error)
    
    # 启动后台加载线程
    threading.Thread(target=load_and_run, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main)
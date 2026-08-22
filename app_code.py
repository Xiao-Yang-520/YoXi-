import flet as ft
import urllib.request
import json
import os
import time
import threading
import ssl

# iOS 上跳过 SSL 证书验证，避免 urllib  HTTPS 请求失败
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

# ── 用标准库 urllib 实现 requests 兼容层（避免 iOS 上 C 扩展编译失败）──
class _Response:
    def __init__(self, status_code, text, headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}
    def json(self):
        return json.loads(self.text)
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

def _request(method, url, headers=None, json_data=None, timeout=10):
    data = None
    req_headers = dict(headers or {})
    req_headers.setdefault('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)')
    if json_data is not None:
        data = json.dumps(json_data).encode('utf-8')
        req_headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _Response(resp.status, resp.read().decode('utf-8'), dict(resp.headers))

class _Requests:
    def get(self, url, headers=None, timeout=10):
        return _request('GET', url, headers=headers, timeout=timeout)
    def post(self, url, headers=None, json=None, timeout=10):
        return _request('POST', url, headers=headers, json_data=json, timeout=timeout)
    def patch(self, url, headers=None, json=None, timeout=10):
        return _request('PATCH', url, headers=headers, json_data=json, timeout=timeout)

requests = _Requests()

# ─────────────────────── 配置加载 ───────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DATA_PATH = os.path.join(BASE_DIR, "data.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    APP_CONFIG = json.load(f)

API_BASE = "https://api.mail.tm"
EMAIL_LIFETIME = APP_CONFIG["email_lifetime_seconds"]
THEME_COLOR = APP_CONFIG["theme_color"]

# ─────────────────────── 数据存储 ───────────────────────
def load_data():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("emails", [])
                data.setdefault("users", [])
                data.setdefault("current_user", None)
                return data
        except:
            pass
    return {"emails": [], "users": [], "current_user": None}

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─────────────────────── mail.tm API ───────────────────────
def api_get_domains():
    r = requests.get(f"{API_BASE}/domains", timeout=10)
    r.raise_for_status()
    return r.json()["hydra:member"]

def api_create_account(address, password):
    r = requests.post(f"{API_BASE}/accounts", json={
        "address": address, "password": password
    }, timeout=10)
    r.raise_for_status()
    return r.json()

def api_get_token(address, password):
    r = requests.post(f"{API_BASE}/token", json={
        "address": address, "password": password
    }, timeout=10)
    r.raise_for_status()
    return r.json()["token"]

def api_get_messages(token):
    r = requests.get(f"{API_BASE}/messages", headers={
        "Authorization": f"Bearer {token}"
    }, timeout=10)
    r.raise_for_status()
    return r.json()["hydra:member"]

def api_get_message(token, msg_id):
    r = requests.get(f"{API_BASE}/messages/{msg_id}", headers={
        "Authorization": f"Bearer {token}"
    }, timeout=10)
    r.raise_for_status()
    return r.json()

# ─────────────────────── 主应用 ───────────────────────
class TempMailApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.data = load_data()
        self.current_user = self.data.get("current_user", None)
        self.current_tab = 0
        self.current_email = None
        self.current_messages = []
        self.view = "list"  # list / inbox / detail
        self.current_msg = None
        self.create_cooldown = False
        self.refresh_timer = None
        self.countdown_timer = None
        self.remote_config_timer = None
        self.is_disabled = False
        self._pending_update = None
        self._pending_announcement = None
        self.remote_config = {
            "enabled": "是",
            "maintenance": "否",
            "force_update": "否",
            "latest_version": APP_CONFIG["app_version"],
            "announcement": "",
        }

        page.title = APP_CONFIG["app_name"]
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=THEME_COLOR)
        page.window_width = APP_CONFIG["window_width"]
        page.window_height = APP_CONFIG["window_height"]
        page.padding = 0
        page.spacing = 0

        # 先显示加载界面
        self.show_splash()
        self.start_loading()

    # ────────── 启动加载界面 ──────────
    def show_splash(self):
        self.page.controls.clear()
        self.splash_progress = ft.ProgressBar(value=0, width=280, color=THEME_COLOR)
        self.splash_text = ft.Text("正在初始化...", size=13, color=ft.colors.GREY_500)
        self.splash_percent = ft.Text("0%", size=15, weight=ft.FontWeight.BOLD, color=THEME_COLOR)

        splash = ft.Column([
            ft.Container(height=100),
            ft.Text(APP_CONFIG["app_name"], size=34, weight=ft.FontWeight.BOLD),
            ft.Text("临时邮箱 · 隐私保护", size=14, color=ft.colors.GREY_400),
            ft.Container(expand=True),
            self.splash_progress,
            ft.Container(height=8),
            ft.Row([
                self.splash_text,
                self.splash_percent,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=280),
            ft.Container(height=50),
        ], expand=True, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.add(splash)
        self.page.update()

    def start_loading(self):
        def load():
            try:
                self.update_splash(15, "初始化本地数据...")
                self.data = load_data()
                time.sleep(0.4)

                self.update_splash(50, "获取远程配置...")
                self.fetch_remote_config()
                time.sleep(0.3)

                enabled = self.remote_config.get("enabled", "是")
                maintenance = self.remote_config.get("maintenance", "否")
                force_update = self.remote_config.get("force_update", "否")
                latest_version = self.remote_config.get("latest_version", APP_CONFIG["app_version"])
                announcement = self.remote_config.get("announcement", "")

                # 1. 停用/维护检查
                if enabled == "否" or maintenance == "是":
                    status_text = "应用维护中" if maintenance == "是" else "应用已停用"
                    self.update_splash(100, status_text)
                    time.sleep(0.3)
                    self.is_disabled = True
                    self.page.run_thread(lambda: self.show_disabled_page_in_splash(maintenance == "是"))
                    return

                # 2. 强制更新检查
                if force_update == "是" and latest_version != APP_CONFIG["app_version"]:
                    self.update_splash(100, "发现新版本")
                    time.sleep(0.3)
                    self.page.run_thread(lambda: self.show_force_update_prompt(latest_version))
                    return

                # 3. 版本更新提示（非强制）
                if latest_version != APP_CONFIG["app_version"]:
                    self._pending_update = latest_version
                else:
                    self._pending_update = None

                # 4. 公告
                self._pending_announcement = announcement if announcement else None

                self.update_splash(75, "检查更新与公告...")
                time.sleep(0.3)

                self.update_splash(90, "准备就绪...")
                time.sleep(0.2)

                self.update_splash(100, "加载完成")
                time.sleep(0.3)

                self.page.run_thread(self.finish_loading)
            except:
                self.page.run_thread(self.finish_loading)

        threading.Thread(target=load, daemon=True).start()

    def show_disabled_page_in_splash(self, is_maintenance=False):
        """在加载界面直接显示停用页面，不构建主界面"""
        self.page.controls.clear()
        title = "应用维护中" if is_maintenance else "应用已停用"
        desc = "应用正在维护，请稍后再试" if is_maintenance else "该应用已被管理员停用"
        emoji = "⚠️" if is_maintenance else "🚫"
        color = ft.colors.ORANGE if is_maintenance else ft.colors.RED

        disabled_page = ft.Column([
            ft.Container(expand=True),
            ft.Text(emoji, size=80),
            ft.Container(height=20),
            ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=color),
            ft.Container(height=10),
            ft.Text(desc, size=14, color=ft.colors.GREY_500),
            ft.Container(height=8),
            ft.Text("当前状态会自动更新，请保持网络连接", size=12, color=ft.colors.GREY_400),
            ft.Container(expand=True),
        ], expand=True, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.add(disabled_page)
        self.page.update()

        # 启动后台线程持续检查远程配置，恢复后自动进入主界面
        def watch():
            while True:
                time.sleep(10)
                try:
                    self.fetch_remote_config()
                    enabled = self.remote_config.get("enabled", "是")
                    maintenance = self.remote_config.get("maintenance", "否")
                    if enabled == "是" and maintenance == "否":
                        self.is_disabled = False
                        self.page.run_thread(self.finish_loading)
                        return
                except:
                    pass
        threading.Thread(target=watch, daemon=True).start()

    def update_splash(self, percent, text):
        try:
            self.splash_progress.value = percent / 100
            self.splash_percent.value = f"{percent}%"
            self.splash_text.value = text
            self.page.update()
        except:
            pass

    def finish_loading(self):
        self.build_ui()
        self.start_countdown()
        self.start_remote_config_check()
        # 显示待处理的公告和更新提示
        if self._pending_announcement:
            self.show_announcement(self._pending_announcement)
        elif self._pending_update:
            self.show_update_prompt(self._pending_update)

    def build_ui(self):
        self.page.controls.clear()
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.fab = ft.Container(
            content=ft.FloatingActionButton(
                icon=ft.icons.ADD,
                on_click=self.create_email,
                bgcolor=THEME_COLOR,
            ),
            bottom=20,
            right=20,
            visible=False,
        )
        self.content_stack = ft.Stack([self.content, self.fab], expand=True)
        self.page.add(self.content_stack)
        self.page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.MAIL_OUTLINE, selected_icon=ft.icons.MAIL, label="邮箱"),
                ft.NavigationDestination(icon=ft.icons.PHONE_OUTLINED, selected_icon=ft.icons.PHONE, label="号码"),
                ft.NavigationDestination(icon=ft.icons.PERSON_OUTLINE, selected_icon=ft.icons.PERSON, label="我的"),
            ],
            on_change=self.on_tab_change,
            selected_index=0,
        )
        self.render_email_list()

    def on_tab_change(self, e):
        # 如果应用被停用，任何切换都显示停用页面
        if self.is_disabled:
            self.show_disabled_page(self.remote_config.get("maintenance", "否") == "是")
            return
        self.current_tab = e.control.selected_index
        self.view = "list"
        self.current_email = None
        self.stop_refresh()
        if self.current_tab == 0:
            self.render_email_list()
        elif self.current_tab == 1:
            self.render_phone_page()
        elif self.current_tab == 2:
            self.render_me_page()

    # ────────── 邮箱列表页 ──────────
    def render_email_list(self):
        if self.is_disabled:
            self.show_disabled_page(self.remote_config.get("maintenance", "否") == "是")
            return
        emails = self.data.get("emails", [])
        self.content.scroll = ft.ScrollMode.AUTO if emails else None
        self.fab.visible = True
        self.content.controls.clear()
        self.content.controls.append(ft.Container(
            content=ft.Text("临时邮箱", size=28, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(20, 40, 20, 10),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text("创建1小时有效期临时邮箱，自动接收邮件", size=13, color=ft.colors.GREY_500),
            padding=ft.padding.only(20, 0, 20, 10),
        ))

        emails = self.data.get("emails", [])
        if not emails:
            self.content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📫", size=80),
                    ft.Text("暂无邮箱", size=20, weight=ft.FontWeight.W_500, color=ft.colors.GREY_600),
                    ft.Text("点击右下角按钮创建临时邮箱", size=13, color=ft.colors.GREY_400),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                expand=True,
                alignment=ft.alignment.center,
            ))
        else:
            for email in emails:
                self.content.controls.append(self.build_email_card(email))

        self.fab.visible = True
        self.page.update()

    def build_email_card(self, email):
        remaining = email["expires_at"] - time.time()
        expired = remaining <= 0
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        time_text = f"剩余: {mins}分{secs:02d}秒" if not expired else "已过期"
        time_color = ft.colors.RED if expired else ft.colors.GREY_500

        unread = email.get("unread", 0)
        unread_badge = ft.Container(
            content=ft.Text(str(unread), size=11, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED,
            border_radius=10,
            padding=ft.padding.only(6, 2, 6, 2),
            visible=unread > 0,
        )

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(email["address"], size=15, weight=ft.FontWeight.W_500, expand=True),
                    ft.IconButton(
                        icon=ft.icons.COPY,
                        icon_color=ft.colors.GREY_400,
                        icon_size=18,
                        on_click=lambda e, addr=email["address"]: self.copy_text(addr),
                    ),
                    unread_badge,
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=ft.colors.RED_300,
                        icon_size=20,
                        on_click=lambda e, eid=email["id"]: self.delete_email(eid),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(time_text, size=12, color=time_color),
                    ft.Text("查看", size=13, color=THEME_COLOR),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=4),
            bgcolor=ft.colors.WHITE,
            border_radius=14,
            padding=16,
            margin=ft.margin.only(16, 6, 16, 6),
            on_click=lambda e, eid=email["id"]: self.open_inbox(eid),
        )
        return card

    def create_email(self, e):
        if self.create_cooldown:
            return
        self.create_cooldown = True
        self.fab.content.disabled = True
        # 显示加载提示
        loading_dlg = ft.AlertDialog(
            content=ft.Row([
                ft.ProgressRing(width=20, height=20, stroke_width=2),
                ft.Text("正在创建邮箱..."),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        )
        self.page.dialog = loading_dlg
        loading_dlg.open = True
        self.page.update()

        def task():
            try:
                domains = api_get_domains()
                domain = domains[0]["domain"]
                import random, string
                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                address = f"{username}@{domain}"
                api_create_account(address, password)
                token = api_get_token(address, password)
                email_data = {
                    "id": str(int(time.time() * 1000)),
                    "address": address,
                    "domain": domain,
                    "password": password,
                    "token": token,
                    "created_at": time.time(),
                    "expires_at": time.time() + EMAIL_LIFETIME,
                    "expired": False,
                    "unread": 0,
                }
                self.data["emails"].insert(0, email_data)
                save_data(self.data)
                loading_dlg.open = False
                self.page.update()
                self.render_email_list()
            except Exception as ex:
                loading_dlg.open = False
                self.page.update()
                self.show_error("创建失败", str(ex))
            finally:
                def cooldown():
                    for i in range(5, 0, -1):
                        time.sleep(1)
                    self.fab.content.disabled = False
                    self.create_cooldown = False
                    self.page.update()
                threading.Thread(target=cooldown, daemon=True).start()

        threading.Thread(target=task, daemon=True).start()

    def delete_email(self, email_id):
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        def confirm(e):
            self.data["emails"] = [e for e in self.data["emails"] if e["id"] != email_id]
            save_data(self.data)
            dlg.open = False
            self.page.update()
            self.render_email_list()
        dlg = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text("确定要删除这个邮箱吗？"),
            actions=[
                ft.TextButton("取消", on_click=close_dlg),
                ft.TextButton("删除", on_click=confirm),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ────────── 收件箱页 ──────────
    def open_inbox(self, email_id):
        email = next((e for e in self.data["emails"] if e["id"] == email_id), None)
        if not email:
            return
        if email["expires_at"] <= time.time():
            self.show_error("邮箱已过期", "该邮箱已超过1小时有效期")
            return
        self.current_email = email
        self.current_messages = []
        self.view = "inbox"
        self.render_inbox()
        self.start_refresh()

    def render_inbox(self):
        self.fab.visible = False
        self.content.scroll = None
        self.content.controls.clear()
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.back_to_list()),
                ft.Text(self.current_email["address"], size=16, weight=ft.FontWeight.W_500, expand=True),
                ft.IconButton(icon=ft.icons.REFRESH, icon_size=24, on_click=lambda e: self.refresh_inbox()),
            ]),
            padding=ft.padding.only(8, 55, 8, 12),
        ))
        self.msg_list = ft.Column(spacing=8, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content.controls.append(self.msg_list)
        self.render_messages()
        self.refresh_inbox()
        self.page.update()

    def refresh_inbox(self):
        if not self.current_email:
            return
        def task():
            try:
                token = api_get_token(self.current_email["address"], self.current_email["password"])
                self.current_email["token"] = token
                messages = api_get_messages(token)
                self.current_messages = messages
                unread = sum(1 for m in messages if not m.get("seen", False))
                self.current_email["unread"] = unread
                save_data(self.data)
                self.render_messages()
            except Exception as ex:
                pass
        threading.Thread(target=task, daemon=True).start()

    def render_messages(self):
        self.msg_list.controls.clear()
        if not self.current_messages:
            self.msg_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📭", size=80),
                    ft.Text("暂无邮件", size=20, weight=ft.FontWeight.W_500, color=ft.colors.GREY_600),
                    ft.Text("发送邮件到这个邮箱地址\n新邮件会自动显示在这里", size=13, color=ft.colors.GREY_400, text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                padding=ft.padding.only(0, 80, 0, 80),
                alignment=ft.alignment.center,
            ))
        else:
            for msg in self.current_messages:
                sender = msg.get("from", {}).get("address", "未知") if isinstance(msg.get("from"), dict) else str(msg.get("from", "未知"))
                subject = msg.get("subject", "(无主题)")
                is_unread = not msg.get("seen", False)
                self.msg_list.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(sender, size=14, weight=ft.FontWeight.W_500 if is_unread else ft.FontWeight.NORMAL, expand=True),
                            ft.Text(msg.get("createdAt", "")[5:16], size=11, color=ft.colors.GREY_400),
                        ]),
                        ft.Text(subject, size=13, color=ft.colors.GREY_700 if is_unread else ft.colors.GREY_400),
                    ], spacing=3),
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    padding=14,
                    margin=ft.margin.only(16, 4, 16, 4),
                    on_click=lambda e, m=msg: self.open_message(m),
                ))
        self.page.update()

    def open_message(self, msg):
        self.current_msg = msg
        self.view = "detail"
        self.stop_refresh()
        self.render_message_detail()

    def render_message_detail(self):
        self.fab.visible = False
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.controls.clear()
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.back_to_inbox()),
                ft.Text("邮件详情", size=16, weight=ft.FontWeight.W_500),
            ]),
            padding=ft.padding.only(8, 55, 8, 12),
        ))
        sender = self.current_msg.get("from", {}).get("address", "未知") if isinstance(self.current_msg.get("from"), dict) else str(self.current_msg.get("from", "未知"))
        self.content.controls.append(ft.Container(
            content=ft.Column([
                ft.Text(self.current_msg.get("subject", "(无主题)"), size=18, weight=ft.FontWeight.BOLD),
                ft.Text(f"发件人：{sender}", size=13, color=ft.colors.GREY_500),
                ft.Text(f"时间：{self.current_msg.get('createdAt', '')}", size=12, color=ft.colors.GREY_400),
                ft.Divider(height=20),
                ft.Text(self.current_msg.get("text", self.current_msg.get("intro", "")), size=14),
            ], spacing=8),
            padding=20,
        ))
        self.page.update()
        # 标记已读
        def mark_read():
            try:
                requests.patch(f"{API_BASE}/messages/{self.current_msg['id']}",
                    headers={"Authorization": f"Bearer {self.current_email['token']}"},
                    json={"seen": True}, timeout=5)
            except:
                pass
        threading.Thread(target=mark_read, daemon=True).start()

    def back_to_list(self):
        self.view = "list"
        self.current_email = None
        self.stop_refresh()
        self.render_email_list()

    def back_to_inbox(self):
        self.view = "inbox"
        self.render_inbox()

    def start_refresh(self):
        self.stop_refresh()
        def timer():
            while self.view == "inbox":
                time.sleep(APP_CONFIG["auto_refresh_seconds"])
                if self.view == "inbox":
                    self.refresh_inbox()
        self.refresh_timer = threading.Thread(target=timer, daemon=True)
        self.refresh_timer.start()

    def stop_refresh(self):
        self.refresh_timer = None

    # ────────── 号码页面 ──────────
    def render_phone_page(self):
        if self.is_disabled:
            self.show_disabled_page(self.remote_config.get("maintenance", "否") == "是")
            return
        self.fab.visible = False
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.controls.clear()
        self.content.controls.append(ft.Container(
            content=ft.Text("临时号码", size=28, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(20, 40, 20, 10),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text("公开免费接码号码，所有人可见短信，请勿用于重要账号", size=13, color=ft.colors.GREY_500),
            padding=ft.padding.only(20, 0, 20, 16),
        ))
        for item in APP_CONFIG.get("phone_numbers", []):
            self.content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(item["country"], size=12, color=ft.colors.GREY_500),
                        ft.Text(item["number"], size=16, weight=ft.FontWeight.W_500),
                    ], spacing=2, expand=True),
                    ft.ElevatedButton(
                        "复制",
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_50,
                            color=THEME_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda e, num=item["number"]: self.copy_text(num),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.colors.WHITE,
                border_radius=12,
                padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))
        self.content.controls.append(ft.Container(height=30))
        self.page.update()

    def copy_text(self, text):
        self.page.set_clipboard(text)
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            content=ft.Text(f"已复制：{text}"),
            actions=[ft.TextButton("知道了", on_click=close_dlg)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ────────── Supabase 认证 ──────────
    def _supabase_headers(self):
        return {
            "apikey": APP_CONFIG.get("supabase_anon_key", ""),
            "Content-Type": "application/json",
        }

    def _supabase_url(self):
        return APP_CONFIG.get("supabase_url", "").rstrip("/")

    def supabase_signup(self, email, password, qq=""):
        try:
            r = requests.post(
                f"{self._supabase_url()}/auth/v1/signup",
                headers=self._supabase_headers(),
                json={"email": email, "password": password, "data": {"qq": qq}},
                timeout=15,
            )
            data = r.json()
            if r.status_code in (200, 201):
                return True, data
            return False, data.get("msg", data.get("error_description", "注册失败"))
        except Exception as e:
            return False, str(e)

    def supabase_login(self, email, password):
        try:
            r = requests.post(
                f"{self._supabase_url()}/auth/v1/token?grant_type=password",
                headers=self._supabase_headers(),
                json={"email": email, "password": password},
                timeout=15,
            )
            data = r.json()
            if r.status_code == 200:
                return True, data
            return False, data.get("msg", data.get("error_description", "登录失败"))
        except Exception as e:
            return False, str(e)

    def supabase_send_otp(self, email):
        try:
            r = requests.post(
                f"{self._supabase_url()}/auth/v1/otp",
                headers=self._supabase_headers(),
                json={"email": email},
                timeout=15,
            )
            if r.status_code in (200, 201):
                return True, "验证码已发送"
            data = r.json()
            return False, data.get("msg", data.get("error_description", "发送失败"))
        except Exception as e:
            return False, str(e)

    def supabase_verify_otp(self, email, token):
        try:
            r = requests.post(
                f"{self._supabase_url()}/auth/v1/verify",
                headers=self._supabase_headers(),
                json={"email": email, "token": token, "type": "email"},
                timeout=15,
            )
            data = r.json()
            if r.status_code == 200:
                return True, data
            return False, data.get("msg", data.get("error_description", "验证失败"))
        except Exception as e:
            return False, str(e)

    def _save_supabase_session(self, auth_data):
        user = auth_data.get("user", {})
        self.current_user = {
            "id": user.get("id"),
            "email": user.get("email"),
            "qq": (user.get("user_metadata") or {}).get("qq", ""),
            "nickname": (user.get("user_metadata") or {}).get("qq", user.get("email", "用户"))[:8],
            "access_token": auth_data.get("access_token"),
            "refresh_token": auth_data.get("refresh_token"),
        }
        self.data["current_user"] = self.current_user
        save_data(self.data)

    # ────────── 账号登录页面 ──────────
    def show_login_page(self):
        self.fab.visible = False
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.controls.clear()

        login_mode = {"value": "password"}  # password / otp

        email_field = ft.TextField(
            hint_text="邮箱地址",
            prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        password_field = ft.TextField(
            hint_text="密码",
            prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        otp_field = ft.TextField(
            hint_text="验证码",
            prefix_icon=ft.icons.VERIFIED_USER_OUTLINED,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
            width=150,
        )
        error_text = ft.Text("", size=13, color=ft.colors.RED, text_align=ft.TextAlign.CENTER)
        success_text = ft.Text("", size=13, color=ft.colors.GREEN, text_align=ft.TextAlign.CENTER)

        otp_row = ft.Row([], visible=False, alignment=ft.MainAxisAlignment.CENTER)
        password_row = ft.Row([password_field], visible=True, alignment=ft.MainAxisAlignment.CENTER)

        countdown = {"value": 0}
        send_btn = ft.TextButton("发送验证码", style=ft.ButtonStyle(color=THEME_COLOR))

        def update_mode(mode):
            login_mode["value"] = mode
            if mode == "password":
                password_row.visible = True
                otp_row.visible = False
                password_tab.bgcolor = THEME_COLOR
                password_tab.content.color = ft.colors.WHITE
                otp_tab.bgcolor = ft.colors.TRANSPARENT
                otp_tab.content.color = ft.colors.GREY_600
            else:
                password_row.visible = False
                otp_row.visible = True
                otp_tab.bgcolor = THEME_COLOR
                otp_tab.content.color = ft.colors.WHITE
                password_tab.bgcolor = ft.colors.TRANSPARENT
                password_tab.content.color = ft.colors.GREY_600
            self.page.update()

        password_tab = ft.Container(
            content=ft.Text("密码登录", size=14, weight=ft.FontWeight.W_500, color=ft.colors.WHITE),
            bgcolor=THEME_COLOR,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            on_click=lambda e: update_mode("password"),
        )
        otp_tab = ft.Container(
            content=ft.Text("验证码登录", size=14, weight=ft.FontWeight.W_500, color=ft.colors.GREY_600),
            bgcolor=ft.colors.TRANSPARENT,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            on_click=lambda e: update_mode("otp"),
        )

        def do_send_otp(e):
            email = email_field.value.strip()
            if not email:
                error_text.value = "请输入邮箱地址"
                success_text.value = ""
                self.page.update()
                return
            if "@" not in email:
                error_text.value = "请输入有效的邮箱地址"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "正在发送..."
            self.page.update()
            ok, msg = self.supabase_send_otp(email)
            if ok:
                success_text.value = "验证码已发送，请查收邮箱"
                countdown["value"] = 60
                send_btn.disabled = True
                def tick():
                    while countdown["value"] > 0:
                        time.sleep(1)
                        countdown["value"] -= 1
                        send_btn.text = f"{countdown['value']}s后重发"
                        self.page.update()
                    send_btn.text = "发送验证码"
                    send_btn.disabled = False
                    self.page.update()
                threading.Thread(target=tick, daemon=True).start()
            else:
                success_text.value = ""
                error_text.value = f"发送失败：{msg}"
            self.page.update()

        send_btn.on_click = do_send_otp
        otp_row.controls = [otp_field, send_btn]

        def do_login(e):
            email = email_field.value.strip()
            if not email:
                error_text.value = "请输入邮箱地址"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "登录中..."
            self.page.update()

            if login_mode["value"] == "password":
                password = password_field.value
                if not password:
                    error_text.value = "请输入密码"
                    success_text.value = ""
                    self.page.update()
                    return
                ok, data = self.supabase_login(email, password)
                if ok:
                    self._save_supabase_session(data)
                    success_text.value = ""
                    self.render_me_page()
                else:
                    success_text.value = ""
                    error_text.value = f"登录失败：{data}"
                    self.page.update()
            else:
                token = otp_field.value.strip()
                if not token:
                    error_text.value = "请输入验证码"
                    success_text.value = ""
                    self.page.update()
                    return
                ok, data = self.supabase_verify_otp(email, token)
                if ok:
                    self._save_supabase_session(data)
                    success_text.value = ""
                    self.render_me_page()
                else:
                    success_text.value = ""
                    error_text.value = f"验证失败：{data}"
                    self.page.update()

        login_card = ft.Container(
            content=ft.Column([
                ft.Container(height=20),
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.LOCK, size=28, color=ft.colors.WHITE),
                        width=56, height=56,
                        bgcolor=THEME_COLOR,
                        border_radius=14,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text("欢迎回来", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("登录后可同步你的邮箱数据", size=13, color=ft.colors.GREY_500),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=20),
                ft.Row([password_tab, otp_tab], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                ft.Container(height=16),
                email_field,
                ft.Container(height=10),
                password_row,
                otp_row,
                ft.Container(height=8),
                error_text,
                success_text,
                ft.Container(height=8),
                ft.Container(
                    content=ft.ElevatedButton(
                        "登录",
                        expand=True,
                        height=52,
                        style=ft.ButtonStyle(
                            bgcolor=THEME_COLOR,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                        ),
                        on_click=do_login,
                    ),
                ),
                ft.Container(height=14),
                ft.TextButton(
                    "没有账号，立即注册",
                    on_click=lambda e: self.show_register_page(),
                    style=ft.ButtonStyle(color=THEME_COLOR),
                ),
                ft.Container(height=2),
                ft.TextButton(
                    "忘记密码？",
                    on_click=lambda e: self.show_forgot_password_page(),
                    style=ft.ButtonStyle(color=ft.colors.GREY_500),
                ),
                ft.Container(height=16),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            padding=ft.padding.only(24, 20, 24, 20),
            margin=ft.margin.only(20, 50, 20, 20),
        )

        self.content.controls.append(ft.Container(
            content=login_card,
            expand=True,
            alignment=ft.alignment.center,
        ))
        self.page.update()

    def show_register_page(self):
        self.fab.visible = False
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.controls.clear()

        email_field = ft.TextField(
            hint_text="邮箱地址",
            prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        qq_field = ft.TextField(
            hint_text="QQ号（选填）",
            prefix_icon=ft.icons.PERSON_OUTLINE,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        password_field = ft.TextField(
            hint_text="设置密码（至少6位）",
            prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        confirm_field = ft.TextField(
            hint_text="确认密码",
            prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        error_text = ft.Text("", size=13, color=ft.colors.RED, text_align=ft.TextAlign.CENTER)
        success_text = ft.Text("", size=13, color=ft.colors.GREEN, text_align=ft.TextAlign.CENTER)

        def do_register(e):
            email = email_field.value.strip()
            qq = qq_field.value.strip()
            password = password_field.value
            confirm = confirm_field.value
            if not email:
                error_text.value = "请输入邮箱地址"
                success_text.value = ""
                self.page.update()
                return
            if "@" not in email:
                error_text.value = "请输入有效的邮箱地址"
                success_text.value = ""
                self.page.update()
                return
            if not password or len(password) < 6:
                error_text.value = "密码至少6位"
                success_text.value = ""
                self.page.update()
                return
            if password != confirm:
                error_text.value = "两次密码不一致"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "注册中..."
            self.page.update()
            ok, data = self.supabase_signup(email, password, qq)
            if ok:
                if data.get("user") and data.get("session"):
                    self._save_supabase_session(data)
                    success_text.value = ""
                    self.render_me_page()
                else:
                    success_text.value = "注册成功！请去邮箱验证后登录"
                    self.page.update()
            else:
                success_text.value = ""
                error_text.value = f"注册失败：{data}"
                self.page.update()

        register_card = ft.Container(
            content=ft.Column([
                ft.Container(height=16),
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.PERSON_ADD, size=26, color=ft.colors.WHITE),
                        width=52, height=52,
                        bgcolor=THEME_COLOR,
                        border_radius=14,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text("创建账号", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("注册后可同步你的邮箱数据", size=12, color=ft.colors.GREY_500),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=20),
                email_field,
                ft.Container(height=10),
                qq_field,
                ft.Container(height=10),
                password_field,
                ft.Container(height=10),
                confirm_field,
                ft.Container(height=8),
                error_text,
                success_text,
                ft.Container(height=8),
                ft.Container(
                    content=ft.ElevatedButton(
                        "注册",
                        expand=True,
                        height=52,
                        style=ft.ButtonStyle(
                            bgcolor=THEME_COLOR,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                        ),
                        on_click=do_register,
                    ),
                ),
                ft.Container(height=12),
                ft.TextButton(
                    "已有账号，返回登录",
                    on_click=lambda e: self.show_login_page(),
                    style=ft.ButtonStyle(color=THEME_COLOR),
                ),
                ft.Container(height=16),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            padding=ft.padding.only(24, 20, 24, 20),
            margin=ft.margin.only(20, 40, 20, 20),
        )

        self.content.controls.append(ft.Container(
            content=register_card,
            expand=True,
            alignment=ft.alignment.center,
        ))
        self.page.update()

    def show_forgot_password_page(self):
        self.fab.visible = False
        self.content.scroll = None
        self.content.controls.clear()

        email_field = ft.TextField(
            hint_text="输入注册邮箱",
            prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=12,
            bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT,
            height=52,
            text_size=15,
        )
        result_text = ft.Text("", size=14, color=ft.colors.GREEN, text_align=ft.TextAlign.CENTER)
        error_text = ft.Text("", size=13, color=ft.colors.RED, text_align=ft.TextAlign.CENTER)

        def do_recover(e):
            email = email_field.value.strip()
            if not email or "@" not in email:
                error_text.value = "请输入有效的邮箱地址"
                result_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            result_text.value = "发送中..."
            self.page.update()
            try:
                r = requests.post(
                    f"{self._supabase_url()}/auth/v1/recover",
                    headers=self._supabase_headers(),
                    json={"email": email},
                    timeout=15,
                )
                if r.status_code in (200, 201):
                    result_text.value = "重置密码邮件已发送，请去邮箱点击链接重置密码"
                else:
                    data = r.json()
                    result_text.value = ""
                    error_text.value = f"发送失败：{data.get('msg', data.get('error_description', '未知错误'))}"
            except Exception as ex:
                result_text.value = ""
                error_text.value = f"发送失败：{str(ex)}"
            self.page.update()

        card = ft.Container(
            content=ft.Column([
                ft.Container(height=30),
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.HELP_OUTLINE, size=28, color=ft.colors.WHITE),
                        width=56, height=56,
                        bgcolor=ft.colors.ORANGE,
                        border_radius=14,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text("找回密码", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("输入邮箱，我们将发送重置链接", size=13, color=ft.colors.GREY_500),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=30),
                email_field,
                ft.Container(height=12),
                result_text,
                error_text,
                ft.Container(height=12),
                ft.Container(
                    content=ft.ElevatedButton(
                        "发送重置邮件",
                        expand=True,
                        height=52,
                        style=ft.ButtonStyle(
                            bgcolor=THEME_COLOR,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                        ),
                        on_click=do_recover,
                    ),
                ),
                ft.Container(height=16),
                ft.TextButton(
                    "返回登录",
                    on_click=lambda e: self.show_login_page(),
                    style=ft.ButtonStyle(color=THEME_COLOR),
                ),
                ft.Container(height=20),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            padding=ft.padding.only(24, 20, 24, 20),
            margin=ft.margin.only(20, 60, 20, 20),
        )

        self.content.controls.append(ft.Container(
            content=card,
            expand=True,
            alignment=ft.alignment.center,
        ))
        self.page.update()

    def logout_user(self, e=None):
        self.current_user = None
        self.data["current_user"] = None
        save_data(self.data)
        self.render_me_page()

    # ────────── 我的页面 ──────────
    def render_me_page(self):
        if self.is_disabled:
            self.show_disabled_page(self.remote_config.get("maintenance", "否") == "是")
            return
        self.fab.visible = False
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.controls.clear()
        self.content.controls.append(ft.Container(
            content=ft.Text("我的", size=28, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(20, 40, 20, 16),
        ))
        # 用户卡片
        email_count = len(self.data.get("emails", []))
        total_unread = sum(e.get("unread", 0) for e in self.data.get("emails", []))
        if self.current_user:
            # 已登录：显示用户信息
            user = self.current_user
            nickname = user.get("nickname", "用户")
            qq = user.get("qq", "")
            email = user.get("email", "")
            account_display = f"QQ: {qq}" if qq else f"邮箱: {email}"
            self.content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(nickname[0].upper() if nickname else "U", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        width=56, height=56,
                        bgcolor=THEME_COLOR,
                        border_radius=28,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text(nickname, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(account_display, size=13, color=ft.colors.GREY_500),
                    ], spacing=4, expand=True),
                    ft.TextButton("退出", on_click=self.logout_user, style=ft.ButtonStyle(color=ft.colors.GREY_500)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.colors.WHITE,
                border_radius=14,
                padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))
        else:
            # 未登录：显示登录按钮
            self.content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.icons.PERSON_OUTLINE, size=28, color=ft.colors.GREY_400),
                            width=56, height=56,
                            bgcolor=ft.colors.GREY_100,
                            border_radius=28,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(width=14),
                        ft.Column([
                            ft.Text("未登录", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("登录后可同步数据", size=13, color=ft.colors.GREY_500),
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        "登录 / 注册",
                        expand=True,
                        height=44,
                        style=ft.ButtonStyle(
                            bgcolor=THEME_COLOR,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                        ),
                        on_click=lambda e: self.show_login_page(),
                    ),
                ], spacing=0),
                bgcolor=ft.colors.WHITE,
                border_radius=14,
                padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))
        # 统计卡片
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(str(email_count), size=24, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Text("邮箱数量", size=12, color=ft.colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                ft.VerticalDivider(width=1),
                ft.Column([
                    ft.Text(str(total_unread), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN),
                    ft.Text("未读邮件", size=12, color=ft.colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
            ]),
            bgcolor=ft.colors.WHITE,
            border_radius=14,
            padding=16,
            margin=ft.margin.only(16, 6, 16, 6),
        ))
        # 设置列表
        settings = [
            ("邮箱有效期", f"{EMAIL_LIFETIME//3600}小时"),
            ("自动刷新", f"{APP_CONFIG['auto_refresh_seconds']}秒"),
            ("数据存储", "本地保存"),
            ("关于", f"{APP_CONFIG['app_name']} v{APP_CONFIG['app_version']}"),
        ]
        for label, value in settings:
            self.content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Text(label, size=15),
                    ft.Text(value, size=14, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=ft.colors.WHITE,
                padding=ft.padding.only(20, 16, 20, 16),
                margin=ft.margin.only(16, 1, 16, 1),
            ))
        # 清除数据按钮
        self.content.controls.append(ft.Container(height=20))
        self.content.controls.append(ft.Container(
            content=ft.ElevatedButton(
                "清除所有数据",
                expand=True,
                height=48,
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                on_click=self.clear_all_data,
            ),
            padding=ft.padding.only(16, 0, 16, 30),
        ))
        self.page.update()

    def clear_all_data(self, e):
        def confirm(e):
            self.data = {"emails": []}
            save_data(self.data)
            self.page.dialog.open = False
            self.render_me_page()
        dlg = ft.AlertDialog(
            title=ft.Text("确认清除"),
            content=ft.Text("确定要清除所有邮箱数据吗？此操作不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.TextButton("清除", on_click=confirm),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ────────── 倒计时 ──────────
    def start_countdown(self):
        def timer():
            while True:
                time.sleep(1)
                if self.current_tab == 0 and self.view == "list":
                    self.update_email_times()
        self.countdown_timer = threading.Thread(target=timer, daemon=True)
        self.countdown_timer.start()

    # ────────── 远程配置 ──────────
    def start_remote_config_check(self):
        # 启动时立即检查一次
        try:
            self.fetch_remote_config()
            self.check_remote_config()
        except:
            pass

        def timer():
            while True:
                try:
                    self.fetch_remote_config()
                    self.check_remote_config()
                except:
                    pass
                time.sleep(10)
        self.remote_config_timer = threading.Thread(target=timer, daemon=True)
        self.remote_config_timer.start()

    def fetch_remote_config(self):
        try:
            # 添加缓存控制头，避免 Gitee 缓存
            headers = {
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "If-Modified-Since": "0",
            }
            r = requests.get(APP_CONFIG["remote_config_url"], timeout=8, headers=headers)
            r.raise_for_status()
            config = r.json()
            # 忽略说明字段
            config.pop("_说明", None)
            config.pop("_comment", None)
            self.remote_config.update(config)
        except:
            pass

    def check_remote_config(self):
        enabled = self.remote_config.get("enabled", "是")
        maintenance = self.remote_config.get("maintenance", "否")

        # 运行时停用/维护检查
        if enabled == "否" or maintenance == "是":
            if not self.is_disabled:
                self.is_disabled = True
                self.show_disabled_page(maintenance == "是")
        else:
            if self.is_disabled:
                self.is_disabled = False
                self.hide_disabled_page()

    def show_disabled_page(self, is_maintenance=False):
        try:
            self.stop_refresh()
            self.fab.visible = False
            self.content.scroll = None
            self.content.controls.clear()
            title = "应用维护中" if is_maintenance else "应用已停用"
            desc = "应用正在维护，请稍后再试" if is_maintenance else "该应用已被管理员停用"
            emoji = "⚠️" if is_maintenance else "🚫"
            color = ft.colors.ORANGE if is_maintenance else ft.colors.RED

            self.content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text(emoji, size=80),
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(desc, size=14, color=ft.colors.GREY_500),
                    ft.Text("当前状态会自动更新，请保持网络连接", size=12, color=ft.colors.GREY_400),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                padding=ft.padding.only(0, 120, 0, 0),
                alignment=ft.alignment.center,
            ))
            self.page.update()
        except:
            pass

    def hide_disabled_page(self):
        self.current_tab = 0
        self.page.navigation_bar.selected_index = 0
        self.render_email_list()

    def show_update_prompt(self, latest_version):
        """普通更新提示，用户可以选择更新或稍后再说"""
        def update_now(e):
            dlg.open = False
            self.page.update()
            self.open_update_url()
        def later(e):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            title=ft.Text("发现新版本"),
            content=ft.Text(f"当前版本：{APP_CONFIG['app_version']}\n最新版本：{latest_version}\n\n更新网盘密码:YoXi"),
            actions=[
                ft.TextButton("稍后再说", on_click=later),
                ft.TextButton("立马更新", on_click=update_now),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def show_force_update_prompt(self, latest_version):
        """强制更新，不更新就用不了"""
        def update_now(e):
            dlg.open = False
            self.page.update()
            self.open_update_url()
        def exit_app(e):
            # 退出应用
            self.page.window_close()
        dlg = ft.AlertDialog(
            title=ft.Text("⚠️ 需要更新"),
            content=ft.Text(f"当前版本：{APP_CONFIG['app_version']}\n最新版本：{latest_version}\n\n网盘密码:YoXi"),
            actions=[
                ft.TextButton("退出应用", on_click=exit_app),
                ft.TextButton("立马更新", on_click=update_now),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def open_update_url(self):
        """打开更新下载链接"""
        update_url = APP_CONFIG.get("update_url", "https://wwawd.lanzouw.com/b01euptxsh")
        try:
            self.page.launch_url(update_url)
        except:
            pass

    def show_announcement(self, announcement):
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            title=ft.Text("📢 公告"),
            content=ft.Text(announcement),
            actions=[ft.TextButton("知道了", on_click=close_dlg)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def update_email_times(self):
        for i, ctrl in enumerate(self.content.controls):
            if hasattr(ctrl, 'data') and ctrl.data == 'email_card':
                pass
        # 简单方式：重新渲染列表（但会闪烁，这里只更新时间文字）
        # 为了简单，每10秒重新渲染一次
        if int(time.time()) % 10 == 0:
            self.render_email_list()

    # ────────── 弹窗 ──────────
    def show_error(self, title, message):
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("好的", on_click=lambda e: setattr(self.page.dialog, 'open', False))],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()


def main(page: ft.Page):
    TempMailApp(page)

if __name__ == "__main__":
    ft.app(target=main)

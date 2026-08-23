import flet as ft
import json
import time
import threading
import urllib.request
import urllib.parse
import ssl
import os
import random

ssl._create_default_https_context = ssl._create_unverified_context

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    APP_CONFIG = json.load(f)

THEME_COLOR = APP_CONFIG.get("theme_color", "#007AFF")
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def load_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"emails": [], "current_user": None, "qq_email_map": {}}


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def supabase_request(method, path, body=None, token=None):
    url = APP_CONFIG["supabase_url"] + path
    headers = {
        "apikey": APP_CONFIG["supabase_anon_key"],
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read().decode("utf-8"))
        except:
            return False, str(e)
    except Exception as e:
        return False, str(e)


def send_email_code(to_email, code):
    """通过 EmailJS 发送数字验证码邮件"""
    service_id = APP_CONFIG.get("emailjs_service_id", "")
    template_id = APP_CONFIG.get("emailjs_template_id", "")
    public_key = APP_CONFIG.get("emailjs_public_key", "")
    if not service_id or not template_id or not public_key or "YOUR_" in service_id:
        return False, "EmailJS 未配置"
    url = "https://api.emailjs.com/api/v1.0/email/send"
    body = json.dumps({
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,
        "template_params": {
            "to_email": to_email,
            "code": code,
        }
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body,
        headers={
            "Content-Type": "application/json",
            "Origin": "https://emailjs.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, "发送成功"
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            return False, f"HTTP {e.code}: {body}"
        except:
            return False, f"HTTP {e.code}: {str(e)}"
    except Exception as e:
        return False, f"错误: {str(e)}"


# ========== mail.tm 临时邮箱 API ==========
def mailtm_request(method, path, body=None, token=None):
    url = "https://api.mail.tm" + path
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read().decode("utf-8"))
        except:
            return False, str(e)
    except Exception as e:
        return False, str(e)


def mailtm_get_domain():
    """获取可用域名"""
    ok, data = mailtm_request("GET", "/domains")
    if ok and isinstance(data, list) and len(data) > 0:
        return True, data[0]["domain"]
    return False, data


def mailtm_create():
    """创建随机临时邮箱"""
    import random, string
    ok, domain = mailtm_get_domain()
    if not ok:
        return False, domain
    login = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    password = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    address = login + "@" + domain
    # 创建账号
    ok, data = mailtm_request("POST", "/accounts", {"address": address, "password": password})
    if not ok:
        return False, data
    # 获取 token
    ok2, data2 = mailtm_request("POST", "/token", {"address": address, "password": password})
    if not ok2:
        return False, data2
    return True, {
        "address": address,
        "login": login,
        "domain": domain,
        "password": password,
        "token": data2.get("token", ""),
        "account_id": data.get("id", ""),
    }


def mailtm_get_messages(token):
    """获取收件箱邮件列表"""
    return mailtm_request("GET", "/messages", token=token)


def mailtm_read_message(token, msg_id):
    """读取邮件详情"""
    return mailtm_request("GET", "/messages/" + msg_id, token=token)


# ========== Guerrilla Mail 临时邮箱 API ==========
def guerrilla_get_address():
    """获取临时邮箱地址"""
    url = "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.guerrillamail.com/",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data
    except Exception as e:
        return False, str(e)


def guerrilla_get_messages(sid_token):
    """获取邮件列表"""
    url = "https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token=" + sid_token + "&lang=en"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.guerrillamail.com/",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data.get("list", [])
    except Exception as e:
        return False, str(e)


def guerrilla_read_message(sid_token, msg_id):
    """读取邮件详情"""
    url = "https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=" + str(msg_id) + "&sid_token=" + sid_token + "&lang=en"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.guerrillamail.com/",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)


# ========== maildrop 临时邮箱 API ==========
def maildrop_graphql(query):
    """调用 maildrop GraphQL API"""
    url = "https://api.maildrop.cc/graphql"
    body = json.dumps({"query": query}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)


def maildrop_get_messages(mailbox):
    """获取邮件列表"""
    query = '{ inbox(mailbox:"' + mailbox + '") { id subject date mailfrom } }'
    ok, data = maildrop_graphql(query)
    if ok:
        return True, data.get("data", {}).get("inbox", [])
    return False, data


def maildrop_read_message(mailbox, msg_id):
    """读取邮件详情"""
    query = '{ email(mailbox:"' + mailbox + '", id:"' + str(msg_id) + '") { id subject date mailfrom data } }'
    ok, data = maildrop_graphql(query)
    if ok:
        return True, data.get("data", {}).get("email", {})
    return False, data


# ========== temp-mail.io 临时邮箱 API ==========
def temp_mail_io_create():
    """创建临时邮箱"""
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    body = json.dumps({"min_name_length": 10, "max_name_length": 10}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            email = data.get("email", "")
            login = email.split("@")[0] if "@" in email else ""
            domain = email.split("@")[1] if "@" in email else ""
            return True, {
                "address": email,
                "login": login,
                "domain": domain,
                "token": data.get("token", ""),
            }
    except Exception as e:
        return False, str(e)


def temp_mail_io_get_messages(email):
    """获取邮件列表"""
    url = "https://api.internal.temp-mail.io/api/v3/email/" + email + "/messages"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)


def temp_mail_io_read_message(email, msg_id):
    """读取邮件详情"""
    url = "https://api.internal.temp-mail.io/api/v3/email/" + email + "/messages/" + str(msg_id)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)


# ========== 免费短信接收爬虫 (free-sms-receive.com) ==========
def sms_fetch_page(url, timeout=30):
    """获取网页内容"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def sms_parse_numbers(html_content):
    """解析号码列表"""
    numbers = []
    # 直接提取号码、国家、链接
    nums = re.findall(r'<h4 class="number-boxes-item-number">([^<]+)</h4>', html_content)
    countries = re.findall(r'<h5 class="number-boxes-item-country">([^<]+)</h5>', html_content)
    links = re.findall(r'href="(/message/\d+\.html)"', html_content)
    
    for i in range(min(len(nums), len(links))):
        number = html.unescape(nums[i].strip())
        country = html.unescape(countries[i].strip()) if i < len(countries) else ""
        # 去除国家中的换行和多余空格
        country = " ".join(country.split())
        link = "https://www.free-sms-receive.com" + links[i]
        
        if number and link:
            numbers.append({
                "number": number,
                "country": country,
                "url": link,
            })
    
    return numbers


def sms_parse_messages(html_content):
    """解析短信列表"""
    messages = []
    # 直接提取发件人、时间、内容
    senders = re.findall(r'<div class="mobile_hide">([^<]+)</div>', html_content)
    times = re.findall(r'<div class="col-xs-0 col-md-2">([^<]+)</div>', html_content)
    contents = re.findall(r'<div class="col-xs-12 col-md-8"[^>]*>(.*?)</div>', html_content, re.DOTALL)
    
    for i in range(len(senders)):
        sender = html.unescape(senders[i].strip())
        time = html.unescape(times[i].strip()) if i < len(times) else ""
        msg_content = ""
        if i < len(contents):
            msg_content = html.unescape(contents[i].strip())
            msg_content = re.sub(r'<[^>]+>', '', msg_content)
        
        if sender or msg_content:
            messages.append({
                "sender": sender,
                "time": time,
                "content": msg_content,
            })
    
    return messages


class TempMailApp:
    def __init__(self, page):
        self.page = page
        self.data = load_data()
        self.current_user = self.data.get("current_user", None)
        self.qq_email_map = self.data.get("qq_email_map", {})
        self.current_tab = 0
        self._pending_announcement = None
        self._pending_update = None

    def main(self):
        self.page.title = APP_CONFIG["app_name"]
        self.page.window_width = APP_CONFIG.get("window_width", 375)
        self.page.window_height = APP_CONFIG.get("window_height", 812)
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.show_loading()

    # ========== 加载页 ==========
    def show_loading(self):
        self.page.controls.clear()
        self.progress = ft.ProgressBar(width=280, value=0, color=THEME_COLOR)
        self.status_text = ft.Text("正在加载...", size=14, color=ft.colors.GREY_500)
        loading_page = ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.MAIL, size=64, color=THEME_COLOR),
                    width=120, height=120, bgcolor=ft.colors.BLUE_50,
                    border_radius=60, alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.Row([ft.Text(APP_CONFIG["app_name"], size=24, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.Row([self.progress], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            ft.Row([self.status_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(expand=True),
        ], expand=True, spacing=0)
        self.page.add(loading_page)
        self.page.update()
        threading.Thread(target=self.load_thread, daemon=True).start()

    def update_splash(self, value, text):
        try:
            self.progress.value = value / 100
            self.status_text.value = text
            self.page.update()
        except:
            pass

    def load_thread(self):
        try:
            self.update_splash(20, "检查网络..."); time.sleep(0.3)
            self.update_splash(50, "加载配置..."); time.sleep(0.3)
            # 加载远程配置
            self._remote_config = self._fetch_remote_config()
            self.update_splash(80, "准备就绪..."); time.sleep(0.3)
            self.update_splash(100, "加载完成"); time.sleep(0.3)
            self.page.run_thread(self.after_loading)
        except:
            self._remote_config = {}
            self.page.run_thread(self.after_loading)

    def _fetch_remote_config(self):
        """加载远程配置"""
        url = APP_CONFIG.get("remote_config_url", "")
        if not url:
            return {}
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except:
            return {}

    def after_loading(self):
        # 先检查版本更新，版本号不一样就强制更新
        remote_config = getattr(self, '_remote_config', {})
        latest_version = remote_config.get("latest_version", "")
        current_version = APP_CONFIG.get("app_version", "1.0.0")
        
        if latest_version and latest_version != current_version:
            self._show_force_update(remote_config)
            return
        
        # 进入主界面
        if self.current_user:
            self.build_main_ui()
            self.render_email_list()
        else:
            self.show_fullscreen_login()
        
        # 显示公告（如果有）
        announcement = remote_config.get("announcement", "")
        if announcement:
            self._show_announcement(announcement)

    def _show_announcement(self, text):
        """显示公告弹窗"""
        try:
            # QQ群链接（等用户提供后替换）
            qq_group_url = "https://qun.qq.com/universal-share/share?ac=1&authKey=%2BV5%2BNIvhemn1ucdgZCuJ9yKQv0AaU%2FVBzknLlvlpROd62RHd2fwTniQ9M5r98u44&busi_data=eyJncm91cENvZGUiOiIxMDkzOTI3NjQzIiwidG9rZW4iOiJVY2x2a2x6YTAwdDBFTmJHL1JjbXBzN1JnODJyS3ZPc3NSbzNxMi9YUEtOZ1BhaXR2OTZualVUT1RkRjJIQm82IiwidWluIjoiMzI5NzA0Nzk2MSJ9&data=6ldRotVZ1SRNLWwi8JzUgl5NzFWAL2XkHohHMi60HsbbSSBXbFcwV9AMceiYFAvUd2_zu6p4bo2F0UA6AxWggg&svctype=4&tempid=h5_group_info"
            
            def join_qq_group(e):
                if qq_group_url and qq_group_url != "https://qm.qq.com/qq-group-placeholder":
                    try:
                        import webbrowser
                        webbrowser.open(qq_group_url)
                    except:
                        pass
                self._close_dialog()
            
            self.page.dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.CAMPAIGN, size=24, color=THEME_COLOR),
                    ft.Container(width=8),
                    ft.Text("公告", size=20, weight=ft.FontWeight.BOLD),
                ]),
                content=ft.Container(
                    content=ft.Text(text, size=14, color=ft.colors.GREY_700),
                    width=280,
                    padding=ft.padding.all(10),
                ),
                actions=[
                    ft.TextButton("加入QQ群", on_click=join_qq_group,
                        style=ft.ButtonStyle(color=THEME_COLOR)),
                    ft.TextButton("我知道了", on_click=lambda e: self._close_dialog()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except:
            pass

    def _show_force_update(self, remote_config):
        """显示强制更新弹窗"""
        update_url = remote_config.get("update_url", APP_CONFIG.get("update_url", ""))
        latest_version = remote_config.get("latest_version", "")
        update_desc = remote_config.get("update_description", "发现新版本，请更新后使用")
        
        def do_update(e):
            if update_url:
                try:
                    import webbrowser
                    webbrowser.open(update_url)
                except:
                    pass
        
        self.page.controls.clear()
        self.page.navigation_bar = None
        update_page = ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.SYSTEM_UPDATE, size=64, color=THEME_COLOR),
                    width=120, height=120, bgcolor=ft.colors.BLUE_50,
                    border_radius=60, alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.Row([ft.Text("发现新版本", size=24, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([ft.Text(f"最新版本：v{latest_version}", size=14, color=ft.colors.GREY_500)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Container(
                content=ft.Text(update_desc, size=14, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                padding=ft.padding.symmetric(0, 30),
            ),
            ft.Container(height=30),
            ft.Container(
                content=ft.ElevatedButton(
                    "立即更新", width=200, height=50,
                    style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
                    on_click=do_update,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(expand=True),
        ], expand=True, spacing=0)
        self.page.add(update_page)
        self.page.update()

    # ========== 全屏登录页 ==========
    def show_fullscreen_login(self):
        self.page.controls.clear()
        self.page.navigation_bar = None
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page.add(self.content)
        self.page.update()
        self.show_login_page()

    # ========== 登录页（QQ号+密码）==========
    def show_login_page(self):
        self.content.controls.clear()
        qq_field = ft.TextField(
            hint_text="QQ号", prefix_icon=ft.icons.PERSON_OUTLINE,
            border_radius=12, bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT, height=52, text_size=15,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        password_field = ft.TextField(
            hint_text="密码", prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True,
            border_radius=12, bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT, height=52, text_size=15,
        )
        error_text = ft.Text("", size=13, color=ft.colors.RED)
        success_text = ft.Text("", size=13, color=ft.colors.GREEN)

        def do_login(e):
            qq = qq_field.value.strip()
            password = password_field.value
            if not qq or not password:
                error_text.value = "请填写QQ号和密码"
                success_text.value = ""
                self.page.update()
                return
            email = self.qq_email_map.get(qq)
            if not email:
                error_text.value = "该QQ号未注册，请先注册"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "登录中..."
            self.page.update()

            def login_thread():
                ok, data = supabase_request("POST", "/auth/v1/token?grant_type=password",
                    {"email": email, "password": password})
                if ok and data.get("access_token"):
                    self._save_session(data, qq)
                    self.page.run_thread(lambda: self.go_to_main())
                else:
                    self.page.run_thread(lambda: self._show_error(data, error_text, success_text, "登录失败"))
            threading.Thread(target=login_thread, daemon=True).start()

        def go_register(e):
            self.show_register_page()

        login_btn = ft.ElevatedButton(
            "登录", expand=True, height=50,
            style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
            on_click=do_login,
        )
        register_btn = ft.OutlinedButton(
            "注册", expand=True, height=50,
            style=ft.ButtonStyle(color=THEME_COLOR),
            on_click=go_register,
        )

        self.content.controls.append(ft.Container(height=60))
        self.content.controls.append(ft.Row([
            ft.Container(content=ft.Icon(ft.icons.LOCK_OUTLINE, size=48, color=THEME_COLOR),
                width=90, height=90, bgcolor=ft.colors.BLUE_50,
                border_radius=45, alignment=ft.alignment.center),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=20))
        self.content.controls.append(ft.Row([ft.Text("欢迎回来", size=24, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=8))
        self.content.controls.append(ft.Row([ft.Text("用QQ号和密码登录", size=14, color=ft.colors.GREY_500)], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=30))
        self.content.controls.append(ft.Container(content=qq_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=12))
        self.content.controls.append(ft.Container(content=password_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=8))
        self.content.controls.append(ft.Container(content=error_text, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(content=success_text, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=16))
        self.content.controls.append(ft.Container(
            content=ft.Row([login_btn, register_btn], spacing=12),
            padding=ft.padding.symmetric(horizontal=24),
        ))
        self.content.controls.append(ft.Container(height=16))
        self.page.update()

    # ========== 注册页（QQ号+邮箱+数字验证码+密码）==========
    def show_register_page(self):
        self.content.controls.clear()
        self._pending_code = None  # 保存生成的验证码
        qq_field = ft.TextField(hint_text="QQ号", prefix_icon=ft.icons.PERSON_OUTLINE,
            border_radius=12, bgcolor=ft.colors.GREY_100, border_color=ft.colors.TRANSPARENT,
            height=52, text_size=15, keyboard_type=ft.KeyboardType.NUMBER)
        email_field = ft.TextField(hint_text="邮箱地址", prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=12, bgcolor=ft.colors.GREY_100, border_color=ft.colors.TRANSPARENT,
            height=52, text_size=15)
        code_field = ft.TextField(hint_text="邮箱验证码", prefix_icon=ft.icons.VERIFIED_USER_OUTLINED,
            border_radius=12, bgcolor=ft.colors.GREY_100, border_color=ft.colors.TRANSPARENT,
            height=52, text_size=15, width=170, keyboard_type=ft.KeyboardType.NUMBER)
        password_field = ft.TextField(hint_text="密码（至少6位）", prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, border_radius=12, bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT, height=52, text_size=15)
        confirm_field = ft.TextField(hint_text="确认密码", prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, border_radius=12, bgcolor=ft.colors.GREY_100,
            border_color=ft.colors.TRANSPARENT, height=52, text_size=15)
        error_text = ft.Text("", size=13, color=ft.colors.RED)
        success_text = ft.Text("", size=13, color=ft.colors.GREEN)
        countdown = {"value": 0}

        def send_code(e):
            email = email_field.value.strip()
            if not email:
                error_text.value = "请先输入邮箱"
                success_text.value = ""
                self.page.update()
                return
            if countdown["value"] > 0:
                return
            # 生成 6 位随机数字验证码
            self._pending_code = str(random.randint(100000, 999999))
            error_text.value = ""
            success_text.value = "发送中..."
            self.page.update()

            def send_thread():
                ok, msg = send_email_code(email, self._pending_code)
                if ok:
                    self.page.run_thread(lambda: self._code_sent(send_btn, countdown, success_text))
                else:
                    self.page.run_thread(lambda: self._show_error(msg, error_text, success_text, "发送失败"))
            threading.Thread(target=send_thread, daemon=True).start()

        send_btn = ft.TextButton("发送验证码", on_click=send_code)

        def do_register(e):
            qq = qq_field.value.strip()
            email = email_field.value.strip()
            code = code_field.value.strip()
            password = password_field.value
            confirm = confirm_field.value
            if not qq or not email or not code or not password or not confirm:
                error_text.value = "请填写完整信息"
                success_text.value = ""
                self.page.update()
                return
            if not self._pending_code:
                error_text.value = "请先获取验证码"
                success_text.value = ""
                self.page.update()
                return
            if code != self._pending_code:
                error_text.value = "验证码错误"
                success_text.value = ""
                self.page.update()
                return
            if password != confirm:
                error_text.value = "两次密码不一致"
                success_text.value = ""
                self.page.update()
                return
            if len(password) < 6:
                error_text.value = "密码至少6位"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "注册中..."
            self.page.update()

            def reg_thread():
                ok, data = supabase_request("POST", "/auth/v1/signup",
                    {"email": email, "password": password, "data": {"qq": qq}})
                if ok and data.get("access_token"):
                    # 注册成功且自动登录
                    self.qq_email_map[qq] = email
                    self.data["qq_email_map"] = self.qq_email_map
                    self._save_session(data, qq)
                    self.page.run_thread(lambda: self.go_to_main())
                elif ok and (data.get("id") or data.get("user")):
                    # 注册成功，但 Supabase 需要邮箱验证
                    # 我们已经通过 EmailJS 验证了邮箱，所以直接用密码登录
                    ok2, data2 = supabase_request("POST", "/auth/v1/token?grant_type=password",
                        {"email": email, "password": password})
                    if ok2 and data2.get("access_token"):
                        self.qq_email_map[qq] = email
                        self.data["qq_email_map"] = self.qq_email_map
                        self._save_session(data2, qq)
                        self.page.run_thread(lambda: self.go_to_main())
                    else:
                        # 登录失败，提示注册成功
                        self.qq_email_map[qq] = email
                        self.data["qq_email_map"] = self.qq_email_map
                        save_data(self.data)
                        self.page.run_thread(lambda: self._reg_success(error_text, success_text))
                else:
                    self.page.run_thread(lambda: self._show_error(data, error_text, success_text, "注册失败"))
            threading.Thread(target=reg_thread, daemon=True).start()

        def back(e):
            self.show_login_page()

        reg_btn = ft.ElevatedButton("注册", expand=True, height=50,
            style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE), on_click=do_register)

        self.content.controls.append(ft.Container(height=50))
        self.content.controls.append(ft.Row([ft.Text("注册账号", size=24, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=25))
        self.content.controls.append(ft.Container(content=qq_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=12))
        self.content.controls.append(ft.Container(content=email_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=12))
        self.content.controls.append(ft.Container(
            content=ft.Row([code_field, send_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=24),
        ))
        self.content.controls.append(ft.Container(height=12))
        self.content.controls.append(ft.Container(content=password_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=12))
        self.content.controls.append(ft.Container(content=confirm_field, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=8))
        self.content.controls.append(ft.Container(content=error_text, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(content=success_text, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=16))
        self.content.controls.append(ft.Container(content=reg_btn, padding=ft.padding.symmetric(horizontal=24)))
        self.content.controls.append(ft.Container(height=16))
        self.content.controls.append(ft.Row([ft.TextButton("已有账号？返回登录", on_click=back)], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

    def _code_sent(self, send_btn, countdown, success_text):
        success_text.value = "验证码已发送，请查收邮箱（6位数字）"
        countdown["value"] = 60
        send_btn.disabled = True

        def tick():
            while countdown["value"] > 0:
                time.sleep(1)
                countdown["value"] -= 1
                try:
                    send_btn.text = f"重新发送({countdown['value']}s)"
                    self.page.update()
                except:
                    pass
            try:
                send_btn.text = "发送验证码"
                send_btn.disabled = False
                self.page.update()
            except:
                pass
        threading.Thread(target=tick, daemon=True).start()

    def _reg_success(self, error_text, success_text):
        success_text.value = "注册成功！正在登录..."
        error_text.value = ""
        self.page.update()
        time.sleep(1)
        self.go_to_main()

    def _show_error(self, data, error_text, success_text, prefix):
        if isinstance(data, dict):
            msg = data.get("msg") or data.get("error_description") or data.get("message") or str(data)
        else:
            msg = str(data)
        error_text.value = prefix + "：" + str(msg)[:80] if prefix else str(msg)[:80]
        success_text.value = ""
        self.page.update()

    def _save_session(self, data, qq=""):
        user = data.get("user", {})
        email = user.get("email", "")
        if qq and qq not in self.qq_email_map:
            self.qq_email_map[qq] = email
            self.data["qq_email_map"] = self.qq_email_map
        self.current_user = {
            "email": email, "qq": qq, "id": user.get("id", ""),
            "access_token": data.get("access_token", ""),
        }
        self.data["current_user"] = self.current_user
        save_data(self.data)

    # ========== 云端邮箱同步 ==========
    def _load_emails_from_cloud(self):
        """从云端加载用户的邮箱"""
        if not self.current_user or not self.current_user.get("access_token"):
            return
        token = self.current_user["access_token"]
        user_id = self.current_user.get("id", "")
        try:
            ok, data = supabase_request("GET", 
                f"/rest/v1/user_emails?user_id=eq.{user_id}&select=email_data",
                token=token)
            if ok and isinstance(data, list):
                cloud_emails = []
                for item in data:
                    email_data = item.get("email_data", {})
                    if email_data:
                        cloud_emails.append(email_data)
                # 合并云端和本地邮箱，去重
                local_emails = self.data.get("emails", [])
                local_addresses = {e.get("address", "") for e in local_emails}
                for ce in cloud_emails:
                    if ce.get("address", "") not in local_addresses:
                        local_emails.append(ce)
                self.data["emails"] = local_emails
                save_data(self.data)
        except:
            pass

    def _save_email_to_cloud(self, email_data):
        """保存邮箱到云端"""
        if not self.current_user or not self.current_user.get("access_token"):
            return
        token = self.current_user["access_token"]
        user_id = self.current_user.get("id", "")
        address = email_data.get("address", "")
        if not address or not user_id:
            return
        try:
            # 先检查是否已存在
            ok, data = supabase_request("GET",
                f"/rest/v1/user_emails?user_id=eq.{user_id}&email_address=eq.{address}&select=id",
                token=token)
            if ok and isinstance(data, list) and len(data) > 0:
                # 已存在，更新
                record_id = data[0].get("id", "")
                supabase_request("PATCH",
                    f"/rest/v1/user_emails?id=eq.{record_id}",
                    body={"email_data": email_data},
                    token=token)
            else:
                # 不存在，插入
                supabase_request("POST",
                    "/rest/v1/user_emails",
                    body={
                        "user_id": user_id,
                        "email_address": address,
                        "email_data": email_data,
                    },
                    token=token)
        except:
            pass

    def _delete_email_from_cloud(self, email_address):
        """从云端删除邮箱"""
        if not self.current_user or not self.current_user.get("access_token"):
            return
        token = self.current_user["access_token"]
        user_id = self.current_user.get("id", "")
        if not email_address or not user_id:
            return
        try:
            supabase_request("DELETE",
                f"/rest/v1/user_emails?user_id=eq.{user_id}&email_address=eq.{email_address}",
                token=token)
        except:
            pass

    def go_to_main(self):
        self.current_tab = 0
        self.build_main_ui()
        self.render_email_list()
        # 从云端加载邮箱
        threading.Thread(target=self._load_emails_from_cloud, daemon=True).start()

    # ========== 主界面 ==========
    def build_main_ui(self):
        self.page.controls.clear()
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self.page.add(self.content)
        self.page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.MAIL_OUTLINE, selected_icon=ft.icons.MAIL, label="邮箱"),
                ft.NavigationDestination(icon=ft.icons.PHONE_OUTLINED, selected_icon=ft.icons.PHONE, label="号码"),
                ft.NavigationDestination(icon=ft.icons.PERSON_OUTLINE, selected_icon=ft.icons.PERSON, label="主页"),
            ],
            on_change=self.on_tab_change, selected_index=0,
        )
        self.page.update()

    def on_tab_change(self, e):
        idx = e.control.selected_index
        self.current_tab = idx
        if idx == 0:
            self.render_email_list()
        elif idx == 1:
            self.render_phone_page()
        elif idx == 2:
            self.render_me_page()

    # ========== 邮箱列表 ==========
    def render_email_list(self):
        self.content.controls.clear()
        self._stop_countdown()
        # 标题固定，不可滑动
        self.content.scroll = None
        emails = self.data.get("emails", [])
        # 标题区域（固定）
        header = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("临时邮箱", size=28, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(20, 50, 20, 5),
                ),
                ft.Container(
                    content=ft.Text("创建临时邮箱，自动接收邮件", size=13, color=ft.colors.GREY_500),
                    padding=ft.padding.only(20, 0, 20, 10),
                ),
            ], spacing=0),
            bgcolor=ft.colors.GREY_50,
        )
        self.content.controls.append(header)
        # 邮箱列表区域（可滑动）
        self._email_list_container = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._email_list_container)
        self._render_email_items()
        self.content.controls.append(ft.Container(height=80))
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, bgcolor=THEME_COLOR, on_click=self.create_email)
        self.page.update()
        self._start_countdown()

    def _render_email_items(self):
        """渲染邮箱列表项"""
        self._email_list_container.controls.clear()
        emails = self.data.get("emails", [])
        if not emails:
            self._email_list_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📭", size=80),
                    ft.Text("暂无邮箱", size=20, weight=ft.FontWeight.W_500, color=ft.colors.GREY_600),
                    ft.Text("点击右下角按钮创建临时邮箱", size=13, color=ft.colors.GREY_400),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 80, 0, 0),
            ))
            return
        for em in emails:
            addr = em.get("address", "")
            expires_at = em.get("expires_at", 0)
            is_permanent = em.get("is_permanent", False)
            remaining = expires_at - time.time()
            if is_permanent:
                exp_time = "永久有效"
                exp_color = ft.colors.GREEN
            elif remaining > 0:
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                if mins > 0:
                    exp_time = f"还剩 {mins} 分 {secs} 秒"
                else:
                    exp_time = f"还剩 {secs} 秒"
                exp_color = ft.colors.ORANGE if remaining < 300 else ft.colors.GREY_500
            else:
                exp_time = "已过期"
                exp_color = ft.colors.RED
            msg_count = len(em.get("messages", []))
            email_id = em.get("id", "")
            is_real = em.get("is_real", True)
            domain = em.get("domain", "")
            type_names = {"emalupe.com": "mail.tm", "guerrillamailblock.com": "Guerrilla", "maildrop.cc": "maildrop", "temp-mail.io": "temp-mail.io"}
            type_name = type_names.get(domain, domain)
            self._email_list_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Text(type_name, size=10, color=ft.colors.WHITE),
                            bgcolor=ft.colors.GREEN if is_real else ft.colors.ORANGE,
                            border_radius=6, padding=ft.padding.symmetric(2, 6),
                            alignment=ft.alignment.center),
                        ft.Container(width=8),
                        ft.Text(addr, size=15, weight=ft.FontWeight.W_500, expand=True),
                        ft.Container(content=ft.Text(str(msg_count), size=12, color=ft.colors.WHITE),
                            bgcolor=THEME_COLOR, border_radius=10, padding=ft.padding.symmetric(4, 8),
                            alignment=ft.alignment.center) if msg_count > 0 else ft.Container(),
                    ]),
                    ft.Text(exp_time, size=12, color=exp_color),
                    ft.Row([
                        ft.TextButton("查看收件箱", on_click=lambda e, email=em: self.show_inbox(email),
                            style=ft.ButtonStyle(color=THEME_COLOR)),
                        ft.TextButton("复制", on_click=lambda e, a=addr: self._copy_email(a),
                            style=ft.ButtonStyle(color=ft.colors.GREY_600)),
                        ft.TextButton("删除", on_click=lambda e, eid=email_id: self._delete_email(eid),
                            style=ft.ButtonStyle(color=ft.colors.RED)),
                    ], spacing=0),
                ], spacing=4),
                bgcolor=ft.colors.WHITE, border_radius=12, padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))

    def _start_countdown(self):
        """启动实时倒计时"""
        if self._countdown_running:
            return
        self._countdown_running = True
        self._on_email_page = True
        def countdown_loop():
            while self._countdown_running and self._on_email_page:
                try:
                    time.sleep(1)
                    if not self._countdown_running or not self._on_email_page:
                        break
                    # 直接更新邮箱列表，每秒刷新倒计时
                    self.page.run_thread(self._render_email_items)
                except Exception as e:
                    pass
        self._countdown_thread = threading.Thread(target=countdown_loop, daemon=True)
        self._countdown_thread.start()

    def _stop_countdown(self):
        """停止实时倒计时"""
        self._countdown_running = False
        self._on_email_page = False
        self._remote_config = {}
        self._countdown_thread = None

    def create_email(self, e):
        # 弹出选择邮箱类型的弹窗
        email_types = [
            {"name": "mail.tm 临时邮箱", "domain": "emalupe.com", "icon": "📧", "real": True, "provider": "mailtm"},
            {"name": "Guerrilla 临时邮箱", "domain": "guerrillamailblock.com", "icon": "📨", "real": True, "provider": "guerrilla"},
            {"name": "maildrop 临时邮箱", "domain": "maildrop.cc", "icon": "📬", "real": True, "provider": "maildrop"},
            {"name": "temp-mail.io 临时邮箱", "domain": "temp-mail.io", "icon": "📮", "real": True, "provider": "tempmailio"},
        ]
        type_buttons = []
        for et in email_types:
            type_buttons.append(ft.Container(
                content=ft.Row([
                    ft.Text(et["icon"], size=24),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text(et["name"], size=16, weight=ft.FontWeight.W_500),
                        ft.Text("@" + et["domain"], size=12, color=ft.colors.GREY_500),
                    ], spacing=2, expand=True),
                    ft.Text("可收信" if et["real"] else "模拟", size=11,
                        color=ft.colors.GREEN if et["real"] else ft.colors.ORANGE),
                ], alignment=ft.MainAxisAlignment.START),
                bgcolor=ft.colors.WHITE, border_radius=12, padding=16,
                margin=ft.margin.only(0, 4, 0, 4),
                on_click=lambda e, t=et: self._select_email_type(t),
            ))
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("选择邮箱类型", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(type_buttons, spacing=0, tight=True, scroll=ft.ScrollMode.AUTO, height=400),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _select_email_type(self, email_type):
        self._close_dialog()
        self._pending_email_type = email_type
        # 弹出选择有效期的弹窗
        duration_options = [
            {"name": "1小时", "hours": 1, "icon": "⏱️"},
            {"name": "2小时", "hours": 2, "icon": "⏰"},
            {"name": "永久", "hours": -1, "icon": "♾️"},
        ]
        dur_buttons = []
        for d in duration_options:
            dur_buttons.append(ft.Container(
                content=ft.Row([
                    ft.Text(d["icon"], size=24),
                    ft.Container(width=12),
                    ft.Text(d["name"], size=16, weight=ft.FontWeight.W_500, expand=True),
                ], alignment=ft.MainAxisAlignment.START),
                bgcolor=ft.colors.WHITE, border_radius=12, padding=16,
                margin=ft.margin.only(0, 4, 0, 4),
                on_click=lambda e, dur=d: self._select_email_duration(dur),
            ))
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("选择有效期", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(dur_buttons, spacing=0, tight=True),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _select_email_duration(self, duration):
        self._close_dialog()
        email_type = self._pending_email_type
        domain = email_type["domain"]
        provider = email_type.get("provider", "mailtm")
        hours = duration.get("hours", 1)
        is_permanent = hours == -1

        # 显示小弹窗加载动画
        self.page.dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=30, height=30, color=THEME_COLOR, stroke_width=3),
                    ft.Container(height=8),
                    ft.Text("创建中...", size=12, color=ft.colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                width=120,
                height=100,
                padding=ft.padding.all(10),
            ),
        )
        self.page.dialog.open = True
        self.page.update()

        def create_thread():
            import random, string
            if provider == "mailtm":
                # mail.tm API
                ok, result = mailtm_create()
                if ok:
                    new_email = {
                        "id": str(int(time.time() * 1000)),
                        "address": result["address"],
                        "login": result["login"],
                        "domain": result["domain"],
                        "password": result["password"],
                        "token": result["token"],
                        "account_id": result["account_id"],
                        "provider": "mailtm",
                        "created_at": time.time(),
                        "expires_at": time.time() + (hours * 3600 if not is_permanent else 9999999999),
                        "is_permanent": is_permanent,
                        "messages": [],
                        "is_real": True,
                    }
                    self.data["emails"].insert(0, new_email)
                    save_data(self.data)
                    threading.Thread(target=lambda: self._save_email_to_cloud(new_email), daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(self.render_email_list)
                else:
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(lambda: self._show_create_error(result))
                    self.page.run_thread(self.render_email_list)
            elif provider == "guerrilla":
                # Guerrilla Mail API
                ok, result = guerrilla_get_address()
                if ok:
                    addr = result.get("email_addr", "")
                    login = addr.split("@")[0] if "@" in addr else ""
                    new_email = {
                        "id": str(int(time.time() * 1000)),
                        "address": addr,
                        "login": login,
                        "domain": domain,
                        "password": "",
                        "token": result.get("sid_token", ""),
                        "account_id": "",
                        "provider": "guerrilla",
                        "created_at": time.time(),
                        "expires_at": time.time() + (hours * 3600 if not is_permanent else 9999999999),
                        "is_permanent": is_permanent,
                        "messages": [],
                        "is_real": True,
                    }
                    self.data["emails"].insert(0, new_email)
                    save_data(self.data)
                    threading.Thread(target=lambda: self._save_email_to_cloud(new_email), daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(self.render_email_list)
                else:
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(lambda: self._show_create_error(result))
                    self.page.run_thread(self.render_email_list)
            elif provider == "maildrop":
                # maildrop API - 自定义邮箱名
                login = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
                addr = login + "@" + domain
                new_email = {
                    "id": str(int(time.time() * 1000)),
                    "address": addr,
                    "login": login,
                    "domain": domain,
                    "password": "",
                    "token": "",
                    "account_id": "",
                    "provider": "maildrop",
                    "created_at": time.time(),
                    "expires_at": time.time() + (hours * 3600 if not is_permanent else 9999999999),
                        "is_permanent": is_permanent,
                    "messages": [],
                    "is_real": True,
                }
                time.sleep(0.5)
                self.data["emails"].insert(0, new_email)
                save_data(self.data)
                threading.Thread(target=lambda: self._save_email_to_cloud(new_email), daemon=True).start()
                self.page.run_thread(self._close_loading_dialog)
                self.page.run_thread(self.render_email_list)
            elif provider == "tempmailio":
                # temp-mail.io API
                ok, result = temp_mail_io_create()
                if ok:
                    new_email = {
                        "id": str(int(time.time() * 1000)),
                        "address": result["address"],
                        "login": result["login"],
                        "domain": result["domain"],
                        "password": "",
                        "token": result["token"],
                        "account_id": "",
                        "provider": "tempmailio",
                        "created_at": time.time(),
                        "expires_at": time.time() + (hours * 3600 if not is_permanent else 9999999999),
                        "is_permanent": is_permanent,
                        "messages": [],
                        "is_real": True,
                    }
                    self.data["emails"].insert(0, new_email)
                    save_data(self.data)
                    threading.Thread(target=lambda: self._save_email_to_cloud(new_email), daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(self.render_email_list)
                else:
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(lambda: self._show_create_error(result))
                    self.page.run_thread(self.render_email_list)
        threading.Thread(target=create_thread, daemon=True).start()

    def _close_loading_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _show_create_error(self, err):
        self.page.snack_bar = ft.SnackBar(ft.Text("创建邮箱失败：" + str(err)[:50]))
        self.page.snack_bar.open = True
        self.page.update()

    def _copy_email(self, addr):
        self.page.set_clipboard(addr)
        self.page.snack_bar = ft.SnackBar(ft.Text("已复制：" + addr))
        self.page.snack_bar.open = True
        self.page.update()

    def _delete_email(self, email_id):
        email_to_delete = None
        for e in self.data.get("emails", []):
            if e.get("id") == email_id:
                email_to_delete = e
                break
        self.data["emails"] = [e for e in self.data.get("emails", []) if e.get("id") != email_id]
        save_data(self.data)
        # 从云端删除
        if email_to_delete:
            threading.Thread(target=lambda: self._delete_email_from_cloud(email_to_delete.get("address", "")), daemon=True).start()
        self.page.snack_bar = ft.SnackBar(ft.Text("已删除邮箱"))
        self.page.snack_bar.open = True
        self.render_email_list()

    # ========== 收件箱页面 ==========
    def show_inbox(self, email):
        self.current_email = email
        self.content.controls.clear()
        self.page.floating_action_button = None
        # 顶部栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.render_email_list()),
                ft.Text("收件箱", size=20, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_inbox()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text(email.get("address", ""), size=13, color=ft.colors.GREY_500),
            padding=ft.padding.only(20, 0, 20, 10),
        ))
        self._inbox_list = ft.Column([], spacing=0)
        self.content.controls.append(self._inbox_list)
        self.content.controls.append(ft.Container(height=20))
        self.page.update()
        self.refresh_inbox()

    def refresh_inbox(self):
        email = self.current_email
        provider = email.get("provider", "mailtm")

        def refresh_thread():
            if provider == "mailtm":
                token = email.get("token", "")
                ok, result = mailtm_get_messages(token)
                if ok:
                    messages = result.get("hydra:member", []) if isinstance(result, dict) else result
                else:
                    self.page.run_thread(lambda: self._show_inbox_error(str(result)))
                    return
            elif provider == "guerrilla":
                token = email.get("token", "")
                ok, messages = guerrilla_get_messages(token)
                if not ok:
                    self.page.run_thread(lambda: self._show_inbox_error(str(messages)))
                    return
            elif provider == "maildrop":
                login = email.get("login", "")
                ok, messages = maildrop_get_messages(login)
                if not ok:
                    self.page.run_thread(lambda: self._show_inbox_error(str(messages)))
                    return
            elif provider == "tempmailio":
                addr = email.get("address", "")
                ok, messages = temp_mail_io_get_messages(addr)
                if not ok:
                    self.page.run_thread(lambda: self._show_inbox_error(str(messages)))
                    return
            else:
                messages = []

            email["messages"] = messages
            for em in self.data.get("emails", []):
                if em.get("id") == email.get("id"):
                    em["messages"] = messages
                    break
            save_data(self.data)
            self.page.run_thread(lambda: self._render_inbox_messages(messages))
        threading.Thread(target=refresh_thread, daemon=True).start()

    def _render_inbox_messages(self, messages):
        self._inbox_list.controls.clear()
        if not messages:
            self._inbox_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📭", size=60),
                    ft.Text("暂无邮件", size=16, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
        else:
            for msg in messages:
                # 适配不同 provider 的数据格式
                if "mail_from" in msg:
                    # Guerrilla Mail 格式
                    sender = msg.get("mail_from", "未知")
                    subject = msg.get("mail_subject", "(无主题)")
                    date = msg.get("mail_date", "")
                elif "from" in msg and isinstance(msg.get("from"), dict):
                    # mail.tm 格式
                    sender = msg.get("from", {}).get("address", "未知")
                    subject = msg.get("subject", "(无主题)")
                    date = msg.get("createdAt", "")
                elif "from" in msg and isinstance(msg.get("from"), str) and "to" in msg:
                    # temp-mail.io 格式
                    sender = msg.get("from", "未知")
                    subject = msg.get("subject", "(无主题)")
                    date = msg.get("created_at", msg.get("date", ""))
                else:
                    # maildrop 或其他格式
                    sender = msg.get("mailfrom", msg.get("from", "未知"))
                    subject = msg.get("subject", "(无主题)")
                    date = msg.get("date", "")
                self._inbox_list.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(str(sender), size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(str(date)[5:16] if len(str(date)) > 16 else str(date), size=11, color=ft.colors.GREY_400),
                        ]),
                        ft.Text(str(subject), size=13, color=ft.colors.GREY_700, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=4),
                    bgcolor=ft.colors.WHITE, border_radius=10, padding=14,
                    margin=ft.margin.only(12, 4, 12, 4),
                    on_click=lambda e, m=msg: self.show_email_detail(m),
                ))
        self.page.update()

    def _show_inbox_error(self, err):
        self._inbox_list.controls.clear()
        self._inbox_list.controls.append(ft.Container(
            content=ft.Text("加载失败：" + err[:50], size=14, color=ft.colors.RED),
            padding=ft.padding.only(20, 20, 20, 0),
        ))
        self.page.update()

    # ========== 邮件详情页面 ==========
    def show_email_detail(self, msg):
        email = self.current_email
        provider = email.get("provider", "mailtm")
        msg_id = msg.get("id", "")

        self.content.controls.clear()
        self.page.floating_action_button = None
        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.show_inbox(email)),
                ft.Text("邮件详情", size=20, weight=ft.FontWeight.BOLD, expand=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
            bgcolor=ft.colors.WHITE,
        ))
        # 分隔线
        self.content.controls.append(ft.Container(height=1, bgcolor=ft.colors.GREY_200))
        # 内容区域（可滑动）
        self._detail_content = ft.ListView([
            ft.ProgressBar(width=280, color=THEME_COLOR),
            ft.Text("加载中...", size=14, color=ft.colors.GREY_500),
        ], spacing=12, expand=True, padding=20)
        self.content.controls.append(self._detail_content)
        self.page.update()

        def load_thread():
            if provider == "mailtm":
                token = email.get("token", "")
                ok, detail = mailtm_read_message(token, msg_id)
            elif provider == "guerrilla":
                token = email.get("token", "")
                ok, detail = guerrilla_read_message(token, msg_id)
            elif provider == "maildrop":
                login = email.get("login", "")
                ok, detail = maildrop_read_message(login, msg_id)
            elif provider == "tempmailio":
                addr = email.get("address", "")
                ok, detail = temp_mail_io_read_message(addr, msg_id)
            else:
                ok, detail = False, "未知邮箱类型"

            if ok:
                self.page.run_thread(lambda: self._render_email_detail(detail))
            else:
                self.page.run_thread(lambda: self._show_detail_error(str(detail)))
        threading.Thread(target=load_thread, daemon=True).start()

    def _render_email_detail(self, detail):
        self._detail_content.controls.clear()
        # 适配不同 provider 的数据格式
        if "mail_from" in detail:
            # Guerrilla Mail 格式
            sender = detail.get("mail_from", "未知")
            subject = detail.get("mail_subject", "(无主题)")
            date = detail.get("mail_date", "")
            body = detail.get("mail_body", detail.get("mail_excerpt", "(无内容)"))
        elif "from" in detail and isinstance(detail.get("from"), dict):
            # mail.tm 格式
            sender = detail.get("from", {}).get("address", "未知")
            subject = detail.get("subject", "(无主题)")
            date = detail.get("createdAt", "")
            body = detail.get("text", detail.get("html", "(无内容)"))
            if isinstance(body, list):
                body = body[0].get("text", "") if body else "(无内容)"
        elif "from" in detail and isinstance(detail.get("from"), str) and "to" in detail:
            # temp-mail.io 格式
            sender = detail.get("from", "未知")
            subject = detail.get("subject", "(无主题)")
            date = detail.get("created_at", detail.get("date", ""))
            body = detail.get("body_text", detail.get("body", "(无内容)"))
        else:
            # maildrop 或其他格式
            sender = detail.get("mailfrom", detail.get("from", "未知"))
            subject = detail.get("subject", "(无主题)")
            date = detail.get("date", "")
            body = detail.get("data", detail.get("body", "(无内容)"))

        if "<" in str(body) and ">" in str(body):
            import re
            body = re.sub(r'<[^>]+>', '', str(body))
        self._detail_content.controls.clear()
        self._detail_content.controls.append(ft.Text(str(subject), size=18, weight=ft.FontWeight.BOLD))
        self._detail_content.controls.append(ft.Container(height=8))
        self._detail_content.controls.append(ft.Text("发件人：" + str(sender), size=13, color=ft.colors.GREY_600))
        self._detail_content.controls.append(ft.Text("时间：" + str(date), size=13, color=ft.colors.GREY_600))
        self._detail_content.controls.append(ft.Container(height=12))
        self._detail_content.controls.append(ft.Container(height=1, bgcolor=ft.colors.GREY_200))
        self._detail_content.controls.append(ft.Container(height=12))
        self._detail_content.controls.append(ft.Text(str(body), size=14, color=ft.colors.GREY_800))
        self.page.update()

    def _show_detail_error(self, err):
        self._detail_content.controls.clear()
        self._detail_content.controls.append(ft.Text("加载失败：" + err[:50], size=14, color=ft.colors.RED))
        self.page.update()

    # ========== 号码页面 ==========
    def render_phone_page(self):
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("临时号码", size=28, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_phone_numbers()),
            ]),
            padding=ft.padding.only(20, 50, 20, 10),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text("免费接收短信验证码", size=13, color=ft.colors.GREY_500),
            padding=ft.padding.only(20, 0, 20, 10),
        ))
        self._phone_list = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._phone_list)
        
        # 如果有缓存的号码，直接显示
        if hasattr(self, '_cached_phone_numbers') and self._cached_phone_numbers:
            self._render_phone_numbers(self._cached_phone_numbers)
        else:
            self._phone_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, color=THEME_COLOR, stroke_width=3),
                    ft.Container(height=12),
                    ft.Text("正在获取号码列表...", size=14, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
            self.page.update()
            self.refresh_phone_numbers()

    def refresh_phone_numbers(self):
        """刷新号码列表"""
        def refresh_thread():
            try:
                html_content = sms_fetch_page("https://www.free-sms-receive.com/")
                numbers = sms_parse_numbers(html_content)
                self._cached_phone_numbers = numbers
                self.page.run_thread(lambda: self._render_phone_numbers(numbers))
            except Exception as e:
                self.page.run_thread(lambda: self._show_phone_error(str(e)))
        threading.Thread(target=refresh_thread, daemon=True).start()

    def _render_phone_numbers(self, numbers):
        """渲染号码列表"""
        self._phone_list.controls.clear()
        if not numbers:
            self._phone_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📱", size=60),
                    ft.Text("暂无号码", size=16, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
        else:
            for p in numbers:
                self._phone_list.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.icons.PHONE, size=24, color=THEME_COLOR),
                            width=48, height=48, bgcolor=ft.colors.BLUE_50,
                            border_radius=24, alignment=ft.alignment.center),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(p.get("country", ""), size=14, weight=ft.FontWeight.W_500),
                            ft.Text(p.get("number", ""), size=16, weight=ft.FontWeight.BOLD),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.icons.CHEVRON_RIGHT, size=20, color=ft.colors.GREY_400),
                    ]),
                    bgcolor=ft.colors.WHITE, border_radius=12, padding=16,
                    margin=ft.margin.only(0, 4, 0, 4),
                    on_click=lambda e, phone=p: self.show_phone_messages(phone),
                ))
        self.page.update()

    def _show_phone_error(self, err):
        """显示号码错误"""
        self._phone_list.controls.clear()
        self._phone_list.controls.append(ft.Container(
            content=ft.Column([
                ft.Text("❌", size=60),
                ft.Text("获取失败", size=16, color=ft.colors.RED),
                ft.Text(str(err)[:50], size=12, color=ft.colors.GREY_500),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.alignment.center,
            padding=ft.padding.only(0, 60, 0, 0),
        ))
        self.page.update()

    def show_phone_messages(self, phone):
        """显示号码收到的短信"""
        self.current_phone = phone
        self.content.controls.clear()
        self.page.floating_action_button = None
        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.render_phone_page()),
                ft.Column([
                    ft.Text(phone.get("number", ""), size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(phone.get("country", ""), size=12, color=ft.colors.GREY_500),
                ], expand=True, spacing=2),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_phone_messages()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
            bgcolor=ft.colors.WHITE,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=ft.colors.GREY_200))
        # 短信列表（可滑动）
        self._sms_list = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._sms_list)
        self.page.update()
        self.refresh_phone_messages()

    def refresh_phone_messages(self):
        """刷新短信列表"""
        phone = self.current_phone
        url = phone.get("url", "")
        
        def refresh_thread():
            try:
                html_content = sms_fetch_page(url)
                messages = sms_parse_messages(html_content)
                self.page.run_thread(lambda: self._render_sms_messages(messages))
            except Exception as e:
                self.page.run_thread(lambda: self._show_sms_error(str(e)))
        threading.Thread(target=refresh_thread, daemon=True).start()

    def _render_sms_messages(self, messages):
        """渲染短信列表"""
        self._sms_list.controls.clear()
        if not messages:
            self._sms_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📭", size=60),
                    ft.Text("暂无短信", size=16, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
        else:
            for msg in messages:
                self._sms_list.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(msg.get("sender", "未知"), size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(msg.get("time", ""), size=11, color=ft.colors.GREY_400),
                        ]),
                        ft.Container(height=4),
                        ft.Text(msg.get("content", ""), size=13, color=ft.colors.GREY_700),
                    ], spacing=0),
                    bgcolor=ft.colors.WHITE, border_radius=10, padding=14,
                    margin=ft.margin.only(0, 4, 0, 4),
                ))
        self.page.update()

    def _show_sms_error(self, err):
        """显示短信错误"""
        self._sms_list.controls.clear()
        self._sms_list.controls.append(ft.Container(
            content=ft.Column([
                ft.Text("❌", size=60),
                ft.Text("获取失败", size=16, color=ft.colors.RED),
                ft.Text(str(err)[:50], size=12, color=ft.colors.GREY_500),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.alignment.center,
            padding=ft.padding.only(0, 60, 0, 0),
        ))
        self.page.update()

    # ========== 我的页面 ==========
    def render_me_page(self):
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.controls.append(ft.Container(
            content=ft.Text("主页", size=28, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(20, 50, 20, 10),
        ))
        if self.current_user:
            qq = self.current_user.get("qq", "")
            email = self.current_user.get("email", "")
            avatar_text = (qq[0] if qq else "U").upper()
            self.content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Text(avatar_text, size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        width=56, height=56, bgcolor=THEME_COLOR,
                        border_radius=28, alignment=ft.alignment.center),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text("QQ: " + qq, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(email, size=13, color=ft.colors.GREY_500),
                    ], spacing=4),
                ]),
                bgcolor=ft.colors.WHITE, border_radius=14, padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))
            self.content.controls.append(ft.Container(
                content=ft.ElevatedButton("退出登录", expand=True, height=48,
                    style=ft.ButtonStyle(bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                    on_click=self.logout),
                padding=ft.padding.symmetric(horizontal=16),
                margin=ft.margin.only(0, 20, 0, 0),
            ))
        else:
            self.content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.PERSON_OUTLINE, size=28, color=ft.colors.GREY_400),
                        width=56, height=56, bgcolor=ft.colors.GREY_100,
                        border_radius=28, alignment=ft.alignment.center),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text("未登录", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("登录后可同步数据", size=13, color=ft.colors.GREY_500),
                    ], spacing=4),
                ]),
                bgcolor=ft.colors.WHITE, border_radius=14, padding=16,
                margin=ft.margin.only(16, 6, 16, 6),
            ))
            self.content.controls.append(ft.Container(
                content=ft.ElevatedButton("登录 / 注册", expand=True, height=48,
                    style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
                    on_click=lambda e: self.show_fullscreen_login()),
                padding=ft.padding.symmetric(horizontal=16),
                margin=ft.margin.only(0, 20, 0, 0),
            ))
        email_count = len(self.data.get("emails", []))
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(str(email_count), size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("邮箱", size=12, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.colors.WHITE, border_radius=14, padding=20,
            margin=ft.margin.only(16, 16, 16, 6),
        ))
        self.page.update()

    def logout(self, e):
        # 显示加载中页面
        self.page.controls.clear()
        self.page.navigation_bar = None
        loading_page = ft.Column([
            ft.Container(expand=True),
            ft.Row([
                ft.Container(
                    content=ft.ProgressRing(width=50, height=50, color=THEME_COLOR, stroke_width=4),
                    width=120, height=120, alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([ft.Text("正在退出登录...", size=16, color=ft.colors.GREY_600)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(expand=True),
        ], expand=True, spacing=0)
        self.page.add(loading_page)
        self.page.update()
        
        # 延迟后退出
        def do_logout():
            time.sleep(1.2)
            self.current_user = None
            self.data["current_user"] = None
            save_data(self.data)
            self.page.run_thread(self.show_fullscreen_login)
        threading.Thread(target=do_logout, daemon=True).start()


def main(page: ft.Page):
    app = TempMailApp(page)
    app.main()


if __name__ == "__main__":
    ft.app(target=main)

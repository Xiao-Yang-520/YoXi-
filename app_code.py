import flet as ft
import json
import time
import threading
import urllib.request
import urllib.parse
import ssl
import os
import random
import email.header
import base64


def decode_mime(s):
    """解码MIME编码的字符串（如 =?UTF-8?B?...?=）"""
    if not s:
        return s
    s = str(s)
    # 如果不包含MIME编码标记，直接返回
    if "=?" not in s:
        return s
    try:
        import re
        def replace_mime(m):
            charset = m.group(1)
            encoding = m.group(2).upper()
            text = m.group(3)
            try:
                if encoding == "B":
                    return base64.b64decode(text).decode(charset or "utf-8", errors="replace")
                elif encoding == "Q":
                    # Quoted-Printable解码
                    text = text.replace("_", " ")
                    import quopri
                    return quopri.decodestring(text).decode(charset or "utf-8", errors="replace")
            except:
                pass
            return m.group(0)
        # 使用正则表达式替换所有MIME编码部分
        result = re.sub(r'=\?([^?]+)\?([BQbq])\?([^?]+)\?=', replace_mime, s)
        return result
    except:
        return s

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

DEFAULT_CONFIG = {
    "app_name": "YoXi邮箱",
    "app_version": "1.0.0",
    "theme_color": "#007AFF",
    "window_width": 375,
    "window_height": 812,
    "supabase_url": "https://ojgydrkxdhfmlqgvumnm.supabase.co",
    "supabase_anon_key": "sb_publishable_8MYiMk5lCid2owRD9OzSXQ_2Y4nfv3a",
    "emailjs_service_id": "service_olj8cs4",
    "emailjs_template_id": "template_f2l2zsl",
    "emailjs_public_key": "t5u_Xr0_qw1IHjuSq",
    "remote_api_base": "https://o1415520.pythonanywhere.com",
    "remote_app_key": "85e27f37695041bc83f9e8cc1b322567ac336c22bc004513",
    "update_url": "https://wwawd.lanzouw.com/b01euptxsh",
    "default_app_icon": "assets/cute_email_icon.png",
}

try:
    _base_dir = os.path.dirname(os.path.abspath(__file__))
except:
    _base_dir = os.getcwd()

CONFIG_PATH = os.path.join(_base_dir, "config.json")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        APP_CONFIG = json.load(f)
except:
    APP_CONFIG = DEFAULT_CONFIG.copy()

# 确保所有必要的键都存在
for k, v in DEFAULT_CONFIG.items():
    if k not in APP_CONFIG:
        APP_CONFIG[k] = v

THEME_COLOR = APP_CONFIG.get("theme_color", "#007AFF")
DATA_PATH = os.path.join(_base_dir, "data.json")

# ========== 统一设计系统 ==========
# 圆角
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_XL = 24
RADIUS_PILL = 999

# 间距
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
SPACE_2XL = 32

# 字体大小
FONT_XS = 10
FONT_SM = 12
FONT_MD = 14
FONT_LG = 16
FONT_XL = 18
FONT_2XL = 22
FONT_3XL = 28

# 字重
FONT_REGULAR = ft.FontWeight.NORMAL
FONT_MEDIUM = ft.FontWeight.W_500
FONT_SEMIBOLD = ft.FontWeight.W_600
FONT_BOLD = ft.FontWeight.BOLD

# 辅助色
COLOR_SUCCESS = "#34C759"
COLOR_WARNING = "#FF9500"
COLOR_DANGER = "#FF3B30"
COLOR_INFO = "#5AC8FA"
COLOR_PURPLE = "#AF52DE"
COLOR_PINK = "#FF2D55"
COLOR_TEAL = "#30B0C7"
COLOR_INDIGO = "#5856D6"

# 浅色主题色阶
LIGHT_BG = "#F2F2F7"
LIGHT_CARD = "#FFFFFF"
LIGHT_HEADER = "#F9F9FB"
LIGHT_TEXT = "#1C1C1E"
LIGHT_TEXT2 = "#8E8E93"
LIGHT_TEXT3 = "#C7C7CC"
LIGHT_BORDER = "#E5E5EA"
LIGHT_INPUT = "#F2F2F7"

# 深色主题色阶
DARK_BG = "#000000"
DARK_CARD = "#1C1C1E"
DARK_HEADER = "#2C2C2E"
DARK_TEXT = "#FFFFFF"
DARK_TEXT2 = "#8E8E93"
DARK_TEXT3 = "#636366"
DARK_BORDER = "#38383A"
DARK_INPUT = "#2C2C2E"

# 动画时长
ANIM_FAST = 150
ANIM_NORMAL = 250
ANIM_SLOW = 400


def load_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"emails": [], "current_user": None, "qq_email_map": {}}


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


SETTINGS_PATH = os.path.join(_base_dir, "settings.json")
DEFAULT_SETTINGS = {
    "inbox_auto_refresh": True,
    "refresh_interval": 10,
    "default_duration_hours": 1,
    "theme_mode": "system",
}


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            s = json.load(f)
        # 补全缺失的键
        for k, v in DEFAULT_SETTINGS.items():
            if k not in s:
                s[k] = v
        return s
    except:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except:
        pass


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
    import urllib.parse
    return mailtm_request("GET", "/messages/" + urllib.parse.quote(str(msg_id)), token=token)


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
    import urllib.parse
    url = "https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=" + urllib.parse.quote(str(msg_id)) + "&sid_token=" + urllib.parse.quote(sid_token) + "&lang=en"
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
    # 对参数进行转义，防止GraphQL查询语法错误
    def escape_graphql(s):
        return str(s).replace("\\", "\\\\").replace('"', '\\"')
    safe_mailbox = escape_graphql(mailbox)
    safe_id = escape_graphql(msg_id)
    query = '{ message(mailbox:"' + safe_mailbox + '", id:"' + safe_id + '") { id subject date mailfrom data } }'
    ok, data = maildrop_graphql(query)
    if ok:
        return True, data.get("data", {}).get("message", {})
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
    import urllib.parse
    # 对邮箱地址进行URL编码
    encoded_email = urllib.parse.quote(email.strip())
    url = "https://api.internal.temp-mail.io/api/v3/email/" + encoded_email + "/messages"
    # 重试机制，最多重试3次
    for retry in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                return True, json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if retry < 2:
                time.sleep(1)
                continue
            return False, str(e)
    return False, "获取邮件失败"


def temp_mail_io_read_message(email, msg_id):
    """读取邮件详情"""
    import urllib.parse
    url = "https://api.internal.temp-mail.io/api/v3/email/" + urllib.parse.quote(email) + "/messages/" + urllib.parse.quote(str(msg_id))
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)


class TempMailApp:
    def __init__(self, page):
        self.page = page
        self.data = load_data()
        self.current_user = self.data.get("current_user", None)
        self.qq_email_map = self.data.get("qq_email_map", {})
        self.current_tab = 0
        self._pending_announcement = None
        self._pending_update = None
        self._msg_counts = {}
        self.settings = load_settings()
        # 动态主题颜色（iOS风格现代配色）
        self.clr_bg = LIGHT_BG
        self.clr_card = LIGHT_CARD
        self.clr_header_bg = LIGHT_HEADER
        self.clr_text = LIGHT_TEXT
        self.clr_text2 = LIGHT_TEXT2
        self.clr_text3 = LIGHT_TEXT3
        self.clr_border = LIGHT_BORDER
        self.clr_input_bg = LIGHT_INPUT

    def format_user_id(self, raw_id):
        """格式化用户ID：原始ID=1显示为930001，以此类推"""
        try:
            num_id = int(raw_id)
            return str(930000 + num_id)
        except:
            return str(raw_id)

    def main(self):
        self.page.title = APP_CONFIG["app_name"]
        try:
            self.page.window_width = APP_CONFIG.get("window_width", 375)
            self.page.window_height = APP_CONFIG.get("window_height", 812)
        except Exception as e:
            print(f"[窗口尺寸] 设置失败: {e}")
        # 设置窗口标题栏和任务栏图标（Windows API方式，确保任务栏也生效）
        try:
            ico_path = os.path.join(_base_dir, "assets", "app_icon.ico")
            if os.path.exists(ico_path):
                self.page.window_icon = ico_path
                print(f"[窗口图标] Flet属性已设置: {ico_path}")
                # 用Windows API设置任务栏图标（延迟到窗口创建后）
                import threading
                threading.Thread(target=self._set_win_taskbar_icon, args=(ico_path,), daemon=True).start()
            else:
                print(f"[窗口图标] 文件不存在: {ico_path}")
        except Exception as e:
            print(f"[窗口图标] 设置失败: {e}")
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self._apply_theme_mode()
        self.show_loading()

    def _set_win_taskbar_icon(self, ico_path):
        """用Windows API设置窗口任务栏图标（轮询方式，窗口一创建好就立即设置）"""
        try:
            import time
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            win_title = APP_CONFIG.get("app_name", "YoXi邮箱")
            # 轮询查找窗口句柄（最多等5秒，每100ms查一次）
            hwnd = 0
            for _ in range(50):
                hwnd = user32.FindWindowW(None, win_title)
                if hwnd:
                    break
                time.sleep(0.1)
            if not hwnd:
                print(f"[任务栏图标] 未找到窗口: {win_title}")
                return
            # 加载ICO文件为HICON
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            hicon_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
            hicon_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
            WM_SETICON = 0x0080
            ICON_BIG = 1
            ICON_SMALL = 0
            if hicon_big:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
            if hicon_small:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
            # 刷新任务栏
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0020 | 0x0001 | 0x0002 | 0x0040)
            print(f"[任务栏图标] Windows API设置成功, hwnd={hwnd}")
        except Exception as e:
            print(f"[任务栏图标] 设置失败: {e}")

    # ========== 加载页 ==========
    def show_loading(self):
        """加载页（整体化设计：背景图铺满 + 毛玻璃卡片 + 呼吸动画 + 进度条）"""
        self.page.controls.clear()
        self.page.navigation_bar = None
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = ft.colors.BLACK
        self._skipped = False
        self._breathing_running = True

        # 判断当前主题（用于文字颜色适配）
        mode = self.settings.get("theme_mode", "system")
        is_dark = mode == "dark"
        text_on_bg = ft.colors.WHITE  # 背景图上统一用白色
        text_glass = ft.colors.WHITE if is_dark else ft.colors.BLACK
        glass_bg = ft.colors.with_opacity(0.25, ft.colors.BLACK if is_dark else ft.colors.WHITE)

        # 进度条和状态文字（修复：之前创建了但没显示）
        self.progress = ft.ProgressBar(
            width=260, value=0, color=THEME_COLOR,
            bgcolor=ft.colors.with_opacity(0.3, ft.colors.WHITE),
            border_radius=4,
        )
        self.status_text = ft.Text("正在加载...", size=12, color=text_on_bg, weight=FONT_MEDIUM)

        # 右上角跳过按钮（毛玻璃半透明 + 胶囊 + 阴影）
        self._skip_text = ft.Text("跳过 5s", size=13, color=text_on_bg, weight=FONT_MEDIUM)
        skip_btn = ft.GestureDetector(
            content=ft.Container(
                content=ft.Row([
                    self._skip_text,
                    ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=12, color=text_on_bg),
                ], spacing=3),
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                border_radius=RADIUS_PILL,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=10,
                    color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            ),
            on_tap=self._skip_loading,
        )

        # 中心应用图标（带呼吸动画容器）
        app_name = APP_CONFIG.get("app_name", "YoXi邮箱")
        app_version = APP_CONFIG.get("app_version", "1.0.0")
        center_icon_widget = self._build_app_icon_widget(size=72)
        self._splash_icon = ft.Container(
            content=center_icon_widget,
            width=96, height=96,
            bgcolor=ft.colors.with_opacity(0.25, ft.colors.WHITE),
            border_radius=24,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=20,
                color=ft.colors.with_opacity(0.4, ft.colors.BLACK),
                offset=ft.Offset(0, 6),
            ),
        )

        # 本地背景图路径
        local_bg_path = os.path.join(_base_dir, "assets", "app_background.jpg")

        # 底部毛玻璃卡片（进度条 + 状态文字 + 应用信息）
        # 图标用COVER填满，去掉透明边距，看起来更大
        _bottom_icon_path = self._get_current_app_icon()
        bottom_icon_widget = ft.Image(
            src=_bottom_icon_path, width=56, height=56,
            fit=ft.ImageFit.COVER,
        )
        bottom_card = ft.Container(
            content=ft.Column([
                # 进度条
                self.progress,
                ft.Container(height=8),
                # 状态文字
                self.status_text,
                ft.Container(height=14),
                # 分割线
                ft.Container(height=1, bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE)),
                ft.Container(height=12),
                # 应用信息（图标放大，去掉右侧slogan）
                ft.Row([
                    ft.Container(
                        content=bottom_icon_widget,
                        width=56, height=56,
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.WHITE),
                        border_radius=16,
                        alignment=ft.alignment.center,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text(app_name, size=17, weight=FONT_BOLD, color=text_on_bg),
                        ft.Container(height=2),
                        ft.Text(f"版本 {app_version}", size=12, color=ft.colors.with_opacity(0.7, text_on_bg)),
                    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            border_radius=RADIUS_XL,
            padding=ft.padding.only(top=20, bottom=20, left=22, right=22),
            margin=ft.margin.only(left=20, right=20, bottom=24),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=25,
                color=ft.colors.with_opacity(0.4, ft.colors.BLACK),
                offset=ft.Offset(0, -4),
            ),
        )

        # 整体布局：背景图铺满 + 右上角跳过 + 底部毛玻璃卡片
        full_page = ft.Container(
            content=ft.Stack([
                # 背景图（铺满全屏）
                ft.Container(
                    expand=True,
                    image_src=local_bg_path,
                    image_fit=ft.ImageFit.COVER,
                ),
                # 黑色半透明遮罩（增强文字可读性）
                ft.Container(
                    expand=True,
                    bgcolor=ft.colors.with_opacity(0.35, ft.colors.BLACK),
                ),
                # 内容层（背景图干净，只保留顶部跳过和底部卡片）
                ft.Column([
                    # 顶部：跳过按钮
                    ft.Container(
                        content=ft.Row([skip_btn], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(top=50, right=16),
                    ),
                    ft.Container(expand=True),
                    # 底部：毛玻璃卡片
                    bottom_card,
                ], spacing=0, expand=True),
            ]),
            expand=True,
            bgcolor=ft.colors.BLACK,
        )

        self.page.navigation_bar = None
        self.page.add(full_page)
        self.page.update()

        # 启动呼吸动画
        threading.Thread(target=self._breathing_animation, daemon=True).start()
        # 跳过倒计时
        threading.Thread(target=self._skip_countdown, daemon=True).start()
        # 立即获取远程配置
        threading.Thread(target=self._fetch_remote_config_and_bg, daemon=True).start()
        # 加载线程
        threading.Thread(target=self.load_thread, daemon=True).start()

    def _breathing_animation(self):
        """中心图标呼吸缩放动画"""
        try:
            import time
            scale = 1.0
            direction = 1
            while getattr(self, '_breathing_running', False):
                try:
                    scale += 0.008 * direction
                    if scale >= 1.08:
                        direction = -1
                    elif scale <= 0.95:
                        direction = 1
                    # 通过调整padding实现缩放效果（Flet Container不支持直接scale）
                    pad = int((1 - scale) * 8)
                    self._splash_icon.padding = ft.padding.all(max(0, pad))
                    self.page.update()
                except:
                    pass
                time.sleep(0.05)
        except:
            pass
    
    def _fetch_remote_config_and_bg(self):
        """立即获取远程配置（使用本地背景图，不再更新背景图）"""
        try:
            # 立即获取远程配置
            self._remote_config = self._fetch_remote_config()
        except:
            pass

    def _skip_countdown(self):
        """倒计时 5 秒，5秒后需要用户点击才能进入程序"""
        try:
            self._can_enter = False  # 标记是否可以进入
            for i in range(5, 0, -1):
                if getattr(self, '_skipped', False):
                    return
                self._skip_text.value = f"{i}s"
                self.page.update()
                time.sleep(1)
            if not getattr(self, '_skipped', False):
                self._can_enter = True  # 5秒后可以点击进入
                self._skip_text.value = "跳过"
                self.page.update()
        except:
            pass

    def _skip_loading(self, e):
        """点击进入程序（5秒后且加载完成才能点击，5秒前点击无反应）"""
        if getattr(self, '_skipped', False):
            return
        if not getattr(self, '_can_enter', False):
            # 还没到5秒，不弹出提示，直接返回
            return
        if not getattr(self, '_load_completed', False):
            # 加载还没完成，不弹出提示，直接返回
            return
        self._skipped = True
        self.after_loading()

    def _update_splash_background(self):
        """使用本地背景图，不再从远程获取（保留函数避免报错）"""
        pass

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
            # 检查是否已经获取了远程配置（由_fetch_remote_config_and_bg线程获取）
            if not hasattr(self, '_remote_config') or not self._remote_config:
                # 如果还没有获取到，再获取一次
                self._remote_config = self._fetch_remote_config()
            # 确保背景图已更新（如果_fetch_remote_config_and_bg还没完成，这里再更新一次）
            self._update_splash_background()
            self.update_splash(70, "验证账号..."); time.sleep(0.2)
            # 验证本地登录的账号是否还存在（如果在网站被删除，就清除登录状态）
            self._verify_local_user()
            # 从网站实时获取当前用户的最新角色（只保存在内存，不保存到本地，不显示进度）
            self._fetch_user_role_on_load()
            self.update_splash(90, "准备就绪..."); time.sleep(0.2)
            self.update_splash(100, "加载完成"); time.sleep(0.2)
            # 加载完成后不自动进入，等待用户点击右上角"点击进入"按钮
            self._load_completed = True
        except:
            if not hasattr(self, '_remote_config'):
                self._remote_config = {}
            # 加载失败也不自动进入，等待用户点击
            self._load_completed = True

    def _fetch_user_role_on_load(self):
        """在加载页从网站实时获取当前用户的最新角色（只保存在内存，不保存到本地）"""
        try:
            if not self.current_user:
                return
            user_id = str(self.current_user.get("id", ""))
            if not user_id:
                return
            # 调用 user-role 接口获取最新角色
            ok, result = self._remote_api_request("GET", "user-role", params={"user_id": user_id})
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                if isinstance(data, dict):
                    # 优先使用 chat_role（聊天频道显示角色），如果没有则使用 role
                    new_role = data.get("chat_role", data.get("role", ""))
                    if new_role:
                        # 只更新内存中的 current_user，不保存到本地 data.json
                        self.current_user["role"] = str(new_role)
                    # 同步更新用户名和邮箱（只在内存）
                    new_name = data.get("name", data.get("username", ""))
                    if new_name:
                        self.current_user["name"] = str(new_name)
                    new_email = data.get("email", "")
                    if new_email:
                        self.current_user["email"] = str(new_email)
        except Exception as e:
            pass

    def _verify_local_user(self):
        """验证本地登录的账号是否还存在（如果在网站被删除，就清除登录状态）"""
        try:
            if not self.current_user:
                return
            user_id = self.current_user.get("id", "")
            if not user_id:
                return
            # 调用用户邮箱接口验证用户是否存在
            # 如果用户被删除，接口会返回错误或空数据
            ok, result = self._remote_api_request("GET", "user-emails", params={"user_id": user_id})
            # 如果接口返回ok:false，且错误信息表明用户不存在，就清除登录状态
            if not ok:
                if isinstance(result, dict):
                    msg = str(result.get("msg", "")).lower()
                    # 如果错误信息包含"用户不存在"、"not found"、"不存在"等，就清除登录状态
                    if "用户不存在" in msg or "not found" in msg or "不存在" in msg or "user" in msg and "not" in msg:
                        self._clear_local_login()
                        return
                # 网络错误不清除登录状态
                return
            # 如果接口返回ok:true，但data为空，也可能用户被删除了
            # 不过这种情况可能是用户还没有创建邮箱，所以不清除登录状态
        except Exception as e:
            # 验证出错不清除登录状态，避免误判
            pass

    def _clear_local_login(self):
        """清除本地登录状态"""
        try:
            self.current_user = None
            self.data["current_user"] = None
            save_data(self.data)
        except:
            pass

    def _fetch_remote_config(self):
        """加载远程配置（同时获取status和app-config，合并后使用）"""
        base_url = APP_CONFIG.get("remote_api_base", "")
        app_key = APP_CONFIG.get("remote_app_key", "")
        if not base_url or not app_key:
            return {}
        try:
            # 1. 获取status（应用状态）
            status_data = {}
            try:
                url = f"{base_url}/api/remote/{app_key}/status"
                req = urllib.request.Request(url, headers={
                    "User-Agent": "YoXiEmail/1.0",
                    "Accept": "application/json",
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status_data = json.loads(resp.read().decode("utf-8"))
            except:
                pass
            
            # 2. 获取app-config（应用配置，包含splash_image和app_icon）
            config_data = {}
            try:
                url = f"{base_url}/api/remote/{app_key}/app-config"
                req = urllib.request.Request(url, headers={
                    "User-Agent": "YoXiEmail/1.0",
                    "Accept": "application/json",
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    if result.get("ok"):
                        config_data = result.get("data", {})
            except:
                pass
            
            # 3. 合并两个数据源
            merged = {}
            # 先放status的数据
            merged.update(status_data)
            # 再放app-config的数据（覆盖status中相同的字段）
            merged.update(config_data)
            
            # 4. 统一字段名（兼容应用端中使用的字段名）
            # app-config中的app_version -> status中的current_version
            if "app_version" in config_data and "current_version" not in merged:
                merged["current_version"] = config_data["app_version"]
            # app-config中的current_notice -> status中的notice
            if "current_notice" in config_data and "notice" not in merged:
                merged["notice"] = config_data["current_notice"]
            
            # 保存远程状态供后续使用
            self._remote_status = merged
            return merged
        except Exception as e:
            self._remote_status = {}
            return {}

    def _remote_api_request(self, method, path, body=None, params=None, get_with_body=False):
        """通用远程API请求
        get_with_body: True时GET请求参数放在JSON body中，不放在URL中（用于用户管理等API）
        """
        base_url = APP_CONFIG.get("remote_api_base", "")
        app_key = APP_CONFIG.get("remote_app_key", "")
        if not base_url or not app_key:
            return False, "未配置远程API"
        try:
            url = f"{base_url}/api/remote/{app_key}/{path}"
            # get_with_body模式：GET请求参数放在body中，不放在URL中
            if params and not get_with_body:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            headers = {
                "User-Agent": "YoXiEmail/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            # get_with_body模式：把params合并到body中
            request_body = body
            if get_with_body and params:
                request_body = body if body else {}
                if isinstance(request_body, dict):
                    for k, v in params.items():
                        if k not in request_body:
                            request_body[k] = v
            data = json.dumps(request_body).encode("utf-8") if request_body else None
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return True, result
        except urllib.error.HTTPError as e:
            try:
                result = json.loads(e.read().decode("utf-8"))
                return False, result
            except:
                return False, str(e)
        except Exception as e:
            return False, str(e)

    # ========== 用户邮箱云端同步 ==========
    def _load_user_emails_from_cloud(self):
        """从云端加载用户邮箱列表"""
        if not self.current_user:
            return []
        user_id = self.current_user.get("id", "")
        if not user_id:
            return []
        ok, result = self._remote_api_request("GET", "user-emails", params={"user_id": user_id})
        if ok and result.get("ok"):
            cloud_emails = result.get("data", [])
            # 转换为应用内邮箱格式
            local_emails = []
            for ce in cloud_emails:
                # 使用网站返回的完整邮箱地址、类型、域名信息
                email_addr = ce.get("email", "")
                provider = ce.get("provider", "cloud")
                domain = ce.get("domain", "")
                provider_name = ce.get("provider_name", "")
                if not domain and "@" in email_addr:
                    domain = email_addr.split("@")[1]
                # 把字符串格式的expires_at转换为数字时间戳
                expires_at_str = ce.get("expires_at", "")
                expires_at_ts = 0
                if expires_at_str:
                    try:
                        expires_at_ts = time.mktime(time.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S"))
                    except:
                        try:
                            expires_at_ts = time.mktime(time.strptime(expires_at_str, "%Y-%m-%dT%H:%M:%S"))
                        except:
                            expires_at_ts = 0
                local_emails.append({
                    "id": str(ce.get("id", "")),
                    "cloud_id": ce.get("id", ""),
                    "address": email_addr,
                    "login": ce.get("login", email_addr.split("@")[0] if "@" in email_addr else ""),
                    "domain": domain,
                    "provider": provider,
                    "provider_name": provider_name,
                    "token": ce.get("token", ""),
                    "password": ce.get("password", ""),
                    "account_id": ce.get("account_id", ""),
                    "base_gmail": ce.get("base_gmail", ""),
                    "created_at": ce.get("created_at", ""),
                    "expires_at": expires_at_ts,
                    "is_permanent": ce.get("status") == "permanent",
                    "messages": [],
                    "is_real": True,
                })
            # 按照创建时间排序，最早的放在最上面
            local_emails.sort(key=lambda x: x.get("created_at", ""))
            return local_emails
        return []

    def _save_email_to_cloud(self, email_data):
        """保存邮箱到云端"""
        if not self.current_user:
            print("保存邮箱到云端失败: 未登录")
            return False
        user_id = self.current_user.get("id", "")
        if not user_id:
            print("保存邮箱到云端失败: 用户ID为空")
            return False
        # 确保用户ID是整数
        try:
            user_id = int(user_id)
        except:
            print("保存邮箱到云端失败: 用户ID格式错误")
            return False
        # 从邮箱地址提取前缀
        email_addr = email_data.get("address", "")
        prefix = email_addr.split("@")[0] if "@" in email_addr else "user"
        # 注意：Gmail别名邮箱前缀包含"+"号，需要网站后端支持，不要替换
        # 计算有效期天数（保留兼容）
        expires_at = email_data.get("expires_at", 0)
        expire_days = 7
        if expires_at and expires_at > time.time():
            expire_days = max(1, int((expires_at - time.time()) / 86400))
        # 把精确的过期时间转换成字符串格式传递给云端
        expires_at_str = ""
        if expires_at and expires_at > 0:
            try:
                expires_at_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
            except:
                expires_at_str = ""
        print(f"保存邮箱到云端: user_id={user_id}, prefix={prefix}, valid_days={expire_days}, expires_at={expires_at_str}")
        # 把完整的邮箱地址、类型、token、password等信息传给云端
        ok, result = self._remote_api_request("POST", "user-emails", body={
            "user_id": user_id,
            "prefix": prefix,
            "valid_days": expire_days,
            "expires_at": expires_at_str,  # 精确的过期时间
            "email": email_addr,  # 完整邮箱地址
            "provider": email_data.get("provider", ""),  # 邮箱类型
            "domain": email_data.get("domain", ""),  # 域名
            "login": email_data.get("login", ""),  # 登录名
            "token": email_data.get("token", ""),  # token
            "password": email_data.get("password", ""),  # 密码
            "account_id": email_data.get("account_id", ""),  # 账号ID
            "base_gmail": email_data.get("base_gmail", ""),  # Gmail主邮箱
        })
        print(f"保存邮箱到云端返回: ok={ok}, result={result}")
        if ok and isinstance(result, dict) and result.get("ok"):
            # 保存云端邮箱ID，但保留原始邮箱地址，不被云端地址覆盖
            cloud_email = result.get("data", {})
            email_data["cloud_id"] = cloud_email.get("id", "")
            # 保留原始邮箱地址，不使用云端返回的地址覆盖
            # 确保邮箱类型和域名信息保留
            print(f"保存邮箱到云端成功: cloud_id={email_data['cloud_id']}, address={email_data['address']}, provider={email_data.get('provider', '')}")
            return True
        print("保存邮箱到云端失败")
        return False

    def _delete_email_from_cloud(self, email_id):
        """从云端删除邮箱"""
        if not self.current_user:
            return False
        user_id = self.current_user.get("id", "")
        if not user_id or not email_id:
            return False
        ok, result = self._remote_api_request("DELETE", f"user-emails/{email_id}", body={
            "user_id": user_id,
        })
        return ok and result.get("ok", False)

    # ========== 频道消息 ==========
    def _load_channel_messages_from_cloud(self):
        """从云端加载频道消息"""
        ok, result = self._remote_api_request("GET", "chat/messages")
        if ok and result.get("ok"):
            return result.get("data", [])
        return []

    def _send_channel_message_to_cloud(self, content):
        """发送频道消息到云端"""
        if not self.current_user:
            return False
        user_id = self.current_user.get("id", "")
        username = self.current_user.get("username", "")
        if not user_id:
            return False
        ok, result = self._remote_api_request("POST", "chat/messages", body={
            "user_id": user_id,
            "username": username,
            "content": content,
            "type": "text",
        })
        return ok and result.get("ok", False)

    def _send_heartbeat(self):
        """发送心跳上报（后台线程）"""
        try:
            base_url = APP_CONFIG.get("remote_api_base", "")
            app_key = APP_CONFIG.get("remote_app_key", "")
            if not base_url or not app_key:
                return
            url = f"{base_url}/api/remote/{app_key}/heartbeat"
            payload = json.dumps({
                "version": APP_CONFIG.get("app_version", "1.0.0"),
                "status": "running",
                "platform": "mobile",
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "User-Agent": "YoXiEmail/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # 更新远程状态
                if isinstance(data, dict):
                    self._remote_status = data
        except:
            pass

    def _report_update_done(self, version):
        """更新完成后上报"""
        try:
            base_url = APP_CONFIG.get("remote_api_base", "")
            app_key = APP_CONFIG.get("remote_app_key", "")
            if not base_url or not app_key:
                return
            url = f"{base_url}/api/remote/{app_key}/update-done"
            payload = json.dumps({"version": version}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "User-Agent": "YoXiEmail/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                pass
        except:
            pass

    def _remote_api_call(self, endpoint, body=None):
        """调用远程API通用方法"""
        try:
            base_url = APP_CONFIG.get("remote_api_base", "")
            app_key = APP_CONFIG.get("remote_app_key", "")
            if not base_url or not app_key:
                return False, "未配置远程API"
            url = f"{base_url}/api/remote/{app_key}/{endpoint}"
            data = json.dumps(body).encode("utf-8") if body else None
            req = urllib.request.Request(url, data=data, headers={
                "User-Agent": "YoXiEmail/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("ok", False), result
        except urllib.error.HTTPError as e:
            try:
                result = json.loads(e.read().decode("utf-8"))
                return result.get("ok", False), result
            except:
                return False, {"msg": f"HTTP错误 {e.code}"}
        except Exception as e:
            return False, {"msg": str(e)}

    def remote_send_code(self, email):
        """发送邮箱验证码"""
        return self._remote_api_call("send-code", {"email": email})

    def remote_verify_code(self, email, code):
        """验证邮箱验证码"""
        return self._remote_api_call("verify-code", {"email": email, "code": code})

    def remote_register(self, username, password, email, qq=""):
        """注册用户"""
        body = {"username": username, "password": password, "email": email}
        if qq:
            body["qq"] = qq
        return self._remote_api_call("register", body)

    def remote_login(self, qq, password):
        """用户登录（支持QQ号+密码）"""
        return self._remote_api_call("login", {"qq": qq, "password": password})

    def _start_heartbeat_loop(self):
        """启动心跳循环（每30秒一次）"""
        def heartbeat_loop():
            while True:
                try:
                    self._send_heartbeat()
                except:
                    pass
                time.sleep(30)
        threading.Thread(target=heartbeat_loop, daemon=True).start()

    def _show_error_page(self, title, error_msg):
        """显示错误页面（确保不会白屏）"""
        try:
            self.page.controls.clear()
            self.page.navigation_bar = None
            self.page.floating_action_button = None
            error_col = ft.Column([
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.RED),
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=20),
                ft.Text(title or "出错了", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(str(error_msg)[:200] if error_msg else "未知错误", size=13, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    padding=ft.padding.symmetric(horizontal=30),
                ),
                ft.Container(height=30),
                ft.Row([
                    ft.ElevatedButton("重新加载", on_click=lambda e: self._retry_loading()),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True),
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.page.add(error_col)
            self.page.update()
        except Exception as e2:
            # 最后的兜底：直接添加一个简单的文本
            try:
                self.page.add(ft.Text("出错了: " + str(e2), size=16, color=ft.colors.RED))
                self.page.update()
            except:
                pass

    def _retry_loading(self):
        """重新加载"""
        try:
            self.show_loading()
        except:
            pass

    def after_loading(self):
        try:
            # 获取远程状态（新API格式）
            remote_config = getattr(self, '_remote_config', {})
            current_version = APP_CONFIG.get("app_version", "1.0.0")

            # 1. 检查应用状态（stopped=不可用）
            app_status = remote_config.get("app_status", "running")
            if app_status == "stopped":
                self._show_app_stopped()
                return

            # 2. 检查是否需要更新
            need_update = remote_config.get("need_update", False)
            target_version = remote_config.get("target_version", "")
            if need_update and target_version and target_version != current_version:
                self._show_force_update(remote_config)
                return

            # 3. 进入主界面
            if self.current_user:
                self.go_to_main()
            else:
                self.show_fullscreen_login()

            # 4. 启动心跳循环
            self._start_heartbeat_loop()

            # 5. 显示公告（如果有），延迟一点确保页面加载完成
            notice = remote_config.get("notice")
            if notice and isinstance(notice, dict):
                notice_title = notice.get("title", "公告")
                notice_content = notice.get("content", "")
                if notice_content:
                    def show_announcement_delayed():
                        time.sleep(0.5)
                        self.page.run_thread(lambda: self._show_announcement(notice_title, notice_content))
                    threading.Thread(target=show_announcement_delayed, daemon=True).start()
        except Exception as e:
            # 如果出错，显示错误页面，避免白屏
            self._show_error_page("启动失败", str(e))

    def _show_announcement(self, title, content):
        """显示公告弹窗（新API格式：title + content）"""
        try:
            # QQ群号
            qq_group_number = "1093927643"
            # 直接跳转QQ群的协议链接
            qq_group_url = f"mqqwpa://im/chat?chat_type=group&uin={qq_group_number}&version=1"

            def join_qq_group(e):
                if qq_group_url:
                    try:
                        self.page.launch_url(qq_group_url)
                    except:
                        try:
                            import webbrowser
                            webbrowser.open(qq_group_url)
                        except:
                            # 如果跳转失败，复制群号
                            self._copy_text(qq_group_number, "QQ群号已复制，请手动添加")
                self._close_dialog()

            dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.CAMPAIGN, size=24, color=THEME_COLOR),
                    ft.Container(width=8),
                    ft.Text(title or "公告", size=20, weight=ft.FontWeight.BOLD),
                ]),
                content=ft.Container(
                    content=ft.Text(content, size=14, color=ft.colors.GREY_700),
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
            dialog.open = True
            self.page.dialog = dialog
            self.page.update()
        except:
            pass

    def _show_app_stopped(self):
        """显示应用已停止使用"""
        try:
            self.page.controls.clear()
            self.page.navigation_bar = None
            stopped_page = ft.Column([
                ft.Container(expand=True),
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.BLOCK, size=64, color=ft.colors.RED),
                        width=120, height=120, bgcolor=ft.colors.RED_50,
                        border_radius=60, alignment=ft.alignment.center,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=30),
                ft.Row([ft.Text("应用暂不可用", size=24, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row([ft.Text("请联系管理员或稍后再试", size=14, color=ft.colors.GREY_500)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True),
            ], expand=True, spacing=0)
            self.page.add(stopped_page)
            self.page.update()
        except:
            pass

    def _show_force_update(self, remote_config):
        """显示更新弹窗（新API格式）"""
        download_url = remote_config.get("download_url", "") or APP_CONFIG.get("update_url", "")
        target_version = remote_config.get("target_version", "")
        force_update = remote_config.get("force_update", False)
        current_version = APP_CONFIG.get("app_version", "1.0.0")

        def do_update(e):
            if download_url:
                try:
                    self.page.launch_url(download_url)
                except:
                    try:
                        import webbrowser
                        webbrowser.open(download_url)
                    except:
                        pass

        def skip_update(e):
            # 非强制更新可以跳过
            if not force_update:
                if self.current_user:
                    self.build_main_ui()
                    self.render_email_list()
                else:
                    self.show_fullscreen_login()
                self._start_heartbeat_loop()

        self.page.controls.clear()
        self.page.navigation_bar = None

        actions = [
            ft.Container(
                content=ft.ElevatedButton(
                    "立即更新", width=200, height=50,
                    style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
                    on_click=do_update,
                ),
                alignment=ft.alignment.center,
            ),
        ]

        # 非强制更新显示"稍后再说"按钮
        if not force_update:
            actions.append(ft.Container(height=10))
            actions.append(ft.Container(
                content=ft.TextButton("稍后再说", on_click=skip_update),
                alignment=ft.alignment.center,
            ))

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
            ft.Row([ft.Text(f"当前版本：v{current_version} → 最新版本：v{target_version}", size=14, color=ft.colors.GREY_500)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Container(
                content=ft.Text("发现新版本，请更新后使用" if force_update else "发现新版本，建议更新", size=14, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                padding=ft.padding.symmetric(0, 30),
            ),
            ft.Container(height=30),
        ] + actions + [
            ft.Container(expand=True),
        ], expand=True, spacing=0)
        self.page.add(update_page)
        self.page.update()

    # ========== 全屏登录页 ==========
    def show_fullscreen_login(self):
        self.page.controls.clear()
        self.page.navigation_bar = None
        # 登录页强制白天模式背景
        self.page.bgcolor = ft.colors.WHITE
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

        # ========== 滑动拼图验证 ==========
        captcha_verified = {"value": False}
        slider_pos = {"value": 0.0}  # 滑块位置 0.0 ~ 1.0
        SLIDER_WIDTH = 50
        TRACK_WIDTH = 280

        # 拼图块（可拖动）
        puzzle_piece = ft.Container(
            width=SLIDER_WIDTH,
            height=44,
            bgcolor=THEME_COLOR,
            border_radius=8,
            content=ft.Icon(ft.icons.ARROW_FORWARD_IOS, color=ft.colors.WHITE, size=20),
            alignment=ft.alignment.center,
        )

        # 滑道背景
        track_bg = ft.Container(
            width=TRACK_WIDTH,
            height=44,
            bgcolor=ft.colors.GREY_200,
            border_radius=8,
            content=ft.Row([
                ft.Container(width=SLIDER_WIDTH),  # 占位，给滑块留位置
                ft.Text("向右滑动完成验证", size=13, color=ft.colors.GREY_500, expand=True, text_align=ft.TextAlign.CENTER),
            ], spacing=0),
        )

        # 已滑过的进度条
        progress_bar = ft.Container(
            width=0,
            height=44,
            bgcolor=ft.colors.with_opacity(0.2, THEME_COLOR),
            border_radius=8,
        )

        # 滑块的 Stack 布局
        slider_stack = ft.Stack([
            track_bg,
            ft.Container(
                content=ft.Row([progress_bar], spacing=0),
                width=TRACK_WIDTH,
                height=44,
            ),
            ft.Container(
                content=puzzle_piece,
                left=0,
                top=0,
            ),
        ], width=TRACK_WIDTH, height=44)

        def on_slider_pan(e: ft.DragUpdateEvent):
            if captcha_verified["value"]:
                return
            # 计算新位置
            delta_x = e.delta_x
            new_left = slider_stack.controls[2].left + delta_x
            # 限制范围
            max_left = TRACK_WIDTH - SLIDER_WIDTH
            if new_left < 0:
                new_left = 0
            if new_left > max_left:
                new_left = max_left
            slider_stack.controls[2].left = new_left
            # 更新进度条
            progress_bar.width = new_left
            slider_pos["value"] = new_left / max_left if max_left > 0 else 0
            self.page.update()

        def on_slider_pan_end(e):
            if captcha_verified["value"]:
                return
            max_left = TRACK_WIDTH - SLIDER_WIDTH
            current_left = slider_stack.controls[2].left
            # 如果滑到接近末端（90%以上），验证成功
            if current_left >= max_left * 0.9:
                # 吸附到末端
                slider_stack.controls[2].left = max_left
                progress_bar.width = max_left
                captcha_verified["value"] = True
                # 改变样式表示成功
                puzzle_piece.bgcolor = ft.colors.GREEN
                puzzle_piece.content = ft.Icon(ft.icons.CHECK, color=ft.colors.WHITE, size=20)
                track_bg.content = ft.Row([
                    ft.Container(width=SLIDER_WIDTH),
                    ft.Text("验证成功", size=13, color=ft.colors.GREEN, expand=True, text_align=ft.TextAlign.CENTER),
                ], spacing=0)
                error_text.value = ""
            else:
                # 弹回起始位置
                slider_stack.controls[2].left = 0
                progress_bar.width = 0
                captcha_verified["value"] = False
            self.page.update()

        # 用 GestureDetector 包裹滑块
        slider_detector = ft.GestureDetector(
            content=slider_stack,
            on_pan_update=on_slider_pan,
            on_pan_end=on_slider_pan_end,
        )

        captcha_container = ft.Container(
            content=ft.Column([
                ft.Row([slider_detector], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=24),
        )

        def do_login(e):
            qq = qq_field.value.strip()
            password = password_field.value
            if not qq or not password:
                error_text.value = "请填写QQ号和密码"
                success_text.value = ""
                self.page.update()
                return
            if not captcha_verified["value"]:
                error_text.value = "请先完成滑动验证"
                success_text.value = ""
                self.page.update()
                return
            error_text.value = ""
            success_text.value = "登录中..."
            self.page.update()

            def login_thread():
                # 直接用QQ号作为用户名调用后台登录接口
                ok, result = self.remote_login(qq, password)
                if ok and isinstance(result, dict) and result.get("ok"):
                    # 登录成功，保存用户信息（新格式：user_id在顶层）
                    user_id = result.get("user_id", result.get("data", {}).get("id", ""))
                    try:
                        user_id = int(user_id) if user_id else ""
                    except:
                        pass
                    # 先保存登录接口返回的用户信息
                    user_info = {
                        "id": user_id,
                        "username": result.get("username", qq),
                        "name": result.get("name", result.get("username", qq)),
                        "email": result.get("email", ""),
                        "qq": result.get("qq", qq),
                        "role": result.get("role", ""),
                    }
                    # 登录成功后，再调用 user-role 接口获取最新的角色（确保角色是最新的）
                    try:
                        role_ok, role_result = self._remote_api_request("GET", "user-role", params={"user_id": str(user_id)})
                        if role_ok and isinstance(role_result, dict) and role_result.get("ok"):
                            role_data = role_result.get("data", {})
                            if isinstance(role_data, dict):
                                # 优先使用 chat_role（聊天频道显示角色），如果没有则使用 role
                                latest_role = role_data.get("chat_role", role_data.get("role", ""))
                                if latest_role:
                                    user_info["role"] = str(latest_role)
                                # 同步更新用户名和邮箱
                                latest_name = role_data.get("name", role_data.get("username", ""))
                                if latest_name:
                                    user_info["name"] = str(latest_name)
                                latest_email = role_data.get("email", "")
                                if latest_email:
                                    user_info["email"] = str(latest_email)
                    except:
                        pass  # 获取角色失败，使用登录接口返回的角色
                    # 保存用户信息（角色已经是最新的）
                    self._save_local_user(user_info)
                    # 清空本地邮箱列表，只从云端加载当前用户的邮箱（确保用户不互通）
                    self.data["emails"] = []
                    save_data(self.data)
                    # 重置邮箱同步时间，确保进入主界面后立即从云端同步
                    self._last_email_sync_time = 0
                    self.page.run_thread(lambda: self.go_to_main())
                else:
                    # 登录失败，显示错误信息
                    if isinstance(result, dict):
                        msg = result.get("msg", "登录失败")
                    else:
                        msg = str(result)
                    self.page.run_thread(lambda: self._show_error(msg, error_text, success_text, "登录失败"))
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

        # ===== 美化后的登录页 =====
        app_name = APP_CONFIG.get("app_name", "YoXi邮箱")
        _login_icon_path = self._get_current_app_icon()
        # 顶部品牌区：应用图标 + 名字 + slogan
        self.content.controls.append(ft.Container(height=70))
        self.content.controls.append(ft.Row([
            ft.Container(
                content=ft.Image(src=_login_icon_path, width=64, height=64, fit=ft.ImageFit.COVER),
                width=76, height=76,
                bgcolor=ft.colors.with_opacity(0.08, THEME_COLOR),
                border_radius=20,
                alignment=ft.alignment.center,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=20,
                    color=ft.colors.with_opacity(0.25, THEME_COLOR),
                    offset=ft.Offset(0, 6),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=16))
        self.content.controls.append(ft.Row([
            ft.Text(app_name, size=26, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=6))
        self.content.controls.append(ft.Row([
            ft.Text("临时邮箱，触手可及", size=14, color=ft.colors.GREY_500),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=36))

        # 输入卡片（白色圆角卡片 + 阴影）
        input_card = ft.Container(
            content=ft.Column([
                ft.Container(content=qq_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=12),
                ft.Container(content=password_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=14),
                # 滑动验证（嵌入卡片内）
                ft.Row([slider_detector], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=4),
                ft.Container(content=error_text, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(content=success_text, padding=ft.padding.symmetric(horizontal=4)),
            ], spacing=0),
            bgcolor=ft.colors.WHITE,
            border_radius=18,
            padding=ft.padding.all(18),
            margin=ft.margin.symmetric(horizontal=24),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=24,
                color=ft.colors.with_opacity(0.10, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
        self.content.controls.append(input_card)
        self.content.controls.append(ft.Container(height=28))

        # 登录按钮（渐变 + 阴影 + 圆角）
        _login_gradient_btn = ft.GestureDetector(
            content=ft.Container(
                content=ft.Row([
                    ft.Text("登录", size=17, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                height=52,
                bgcolor=THEME_COLOR,
                border_radius=16,
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=16,
                    color=ft.colors.with_opacity(0.35, THEME_COLOR),
                    offset=ft.Offset(0, 4),
                ),
            ),
            on_tap=do_login,
        )
        self.content.controls.append(ft.Container(
            content=_login_gradient_btn,
            padding=ft.padding.symmetric(horizontal=24),
        ))
        self.content.controls.append(ft.Container(height=16))

        # 注册入口（文字链接）
        self.content.controls.append(ft.Row([
            ft.Text("还没有账号？", size=14, color=ft.colors.GREY_500),
            ft.TextButton("立即注册", style=ft.ButtonStyle(color=THEME_COLOR),
                on_click=go_register),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2))
        self.content.controls.append(ft.Container(height=24))
        self.page.update()

    # ========== 注册页（用户名+QQ号+邮箱+数字验证码+密码）==========
    def show_register_page(self):
        self.content.controls.clear()
        # 注册页强制白天模式背景
        self.page.bgcolor = ft.colors.WHITE
        username_field = ft.TextField(hint_text="用户名", prefix_icon=ft.icons.PERSON_OUTLINE,
            border_radius=12, bgcolor=ft.colors.GREY_100, border_color=ft.colors.TRANSPARENT,
            height=52, text_size=15)
        qq_field = ft.TextField(hint_text="QQ号", prefix_icon=ft.icons.CHAT_OUTLINED,
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
            error_text.value = ""
            success_text.value = "发送中..."
            self.page.update()

            def send_thread():
                ok, result = self.remote_send_code(email)
                if ok:
                    self.page.run_thread(lambda: self._code_sent(send_btn, countdown, success_text))
                else:
                    msg = result.get("msg", "发送失败") if isinstance(result, dict) else str(result)
                    self.page.run_thread(lambda: self._show_error(msg, error_text, success_text, "发送失败"))
            threading.Thread(target=send_thread, daemon=True).start()

        send_btn = ft.TextButton("发送验证码", on_click=send_code)

        def do_register(e):
            username = username_field.value.strip()
            qq = qq_field.value.strip()
            email = email_field.value.strip()
            code = code_field.value.strip()
            password = password_field.value
            confirm = confirm_field.value
            if not username or not qq or not email or not code or not password or not confirm:
                error_text.value = "请填写完整信息（用户名、QQ号、邮箱、验证码、密码）"
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
                # 第一步：验证验证码
                ok_verify, result_verify = self.remote_verify_code(email, code)
                if not ok_verify:
                    msg = result_verify.get("msg", "验证码错误") if isinstance(result_verify, dict) else str(result_verify)
                    self.page.run_thread(lambda: self._show_error(msg, error_text, success_text, "注册失败"))
                    return
                # 第二步：如果填写了QQ号，用QQ号作为用户名（这样可以用QQ号登录）
                reg_username = qq if qq else username
                # 第三步：注册用户
                ok_reg, result_reg = self.remote_register(reg_username, password, email, qq)
                if ok_reg:
                    # 注册成功，保存用户信息到本地（新格式：user_id在顶层）
                    user_id = result_reg.get("user_id", result_reg.get("data", {}).get("id", "")) if isinstance(result_reg, dict) else ""
                    try:
                        user_id = int(user_id) if user_id else ""
                    except:
                        pass
                    self._save_local_user({
                        "id": user_id,
                        "username": result_reg.get("username", reg_username) if isinstance(result_reg, dict) else reg_username,
                        "name": result_reg.get("name", result_reg.get("username", reg_username)) if isinstance(result_reg, dict) else reg_username,
                        "email": email,
                        "qq": qq,
                        "role": result_reg.get("role", "用户") if isinstance(result_reg, dict) else "用户",
                    }, password=password)
                    # 清空本地邮箱列表，只从云端加载当前用户的邮箱（确保用户不互通）
                    self.data["emails"] = []
                    save_data(self.data)
                    # 重置邮箱同步时间，确保进入主界面后立即从云端同步
                    self._last_email_sync_time = 0
                    self.page.run_thread(lambda: self.go_to_main())
                else:
                    msg = result_reg.get("msg", "注册失败") if isinstance(result_reg, dict) else str(result_reg)
                    self.page.run_thread(lambda: self._show_error(msg, error_text, success_text, "注册失败"))
            threading.Thread(target=reg_thread, daemon=True).start()

        def back(e):
            self.show_login_page()

        reg_btn = ft.ElevatedButton("注册", expand=True, height=50,
            style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE), on_click=do_register)

        # ===== 美化后的注册页 =====
        app_name = APP_CONFIG.get("app_name", "YoXi邮箱")
        _reg_icon_path = self._get_current_app_icon()
        # 顶部品牌区
        self.content.controls.append(ft.Container(height=50))
        self.content.controls.append(ft.Row([
            ft.Container(
                content=ft.Image(src=_reg_icon_path, width=52, height=52, fit=ft.ImageFit.COVER),
                width=64, height=64,
                bgcolor=ft.colors.with_opacity(0.08, THEME_COLOR),
                border_radius=18,
                alignment=ft.alignment.center,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=16,
                    color=ft.colors.with_opacity(0.25, THEME_COLOR),
                    offset=ft.Offset(0, 4),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=14))
        self.content.controls.append(ft.Row([
            ft.Text("注册账号", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=4))
        self.content.controls.append(ft.Row([
            ft.Text(f"加入{app_name}，开启临时邮箱之旅", size=13, color=ft.colors.GREY_500),
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.content.controls.append(ft.Container(height=24))

        # 输入卡片
        reg_input_card = ft.Container(
            content=ft.Column([
                ft.Container(content=username_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=10),
                ft.Container(content=qq_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=10),
                ft.Container(content=email_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=10),
                ft.Row([code_field, send_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Container(content=password_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=10),
                ft.Container(content=confirm_field, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=6),
                ft.Container(content=error_text, padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(content=success_text, padding=ft.padding.symmetric(horizontal=4)),
            ], spacing=0),
            bgcolor=ft.colors.WHITE,
            border_radius=18,
            padding=ft.padding.all(16),
            margin=ft.margin.symmetric(horizontal=24),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=24,
                color=ft.colors.with_opacity(0.10, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
        self.content.controls.append(reg_input_card)
        self.content.controls.append(ft.Container(height=24))

        # 注册按钮
        _reg_gradient_btn = ft.GestureDetector(
            content=ft.Container(
                content=ft.Row([
                    ft.Text("注册", size=17, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                height=52,
                bgcolor=THEME_COLOR,
                border_radius=16,
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=16,
                    color=ft.colors.with_opacity(0.35, THEME_COLOR),
                    offset=ft.Offset(0, 4),
                ),
            ),
            on_tap=do_register,
        )
        self.content.controls.append(ft.Container(
            content=_reg_gradient_btn,
            padding=ft.padding.symmetric(horizontal=24),
        ))
        self.content.controls.append(ft.Container(height=14))
        self.content.controls.append(ft.Row([
            ft.Text("已有账号？", size=14, color=ft.colors.GREY_500),
            ft.TextButton("返回登录", style=ft.ButtonStyle(color=THEME_COLOR), on_click=back),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2))
        self.content.controls.append(ft.Container(height=24))
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

    def _save_local_user(self, user_info, password=""):
        """保存本地用户信息（新后台注册方式）"""
        self.current_user = {
            "id": user_info.get("id", ""),
            "username": user_info.get("username", ""),
            "name": user_info.get("name", user_info.get("username", "")),
            "email": user_info.get("email", ""),
            "qq": user_info.get("qq", ""),
            "role": user_info.get("role", ""),
            "access_token": "",  # 新后台暂不返回token
            "login_type": "remote",  # 标记为远程后台登录
        }
        self.data["current_user"] = self.current_user
        # 保存到本地用户列表，用于后续登录验证
        if "local_users" not in self.data:
            self.data["local_users"] = []
        # 检查是否已存在
        existing = False
        for u in self.data["local_users"]:
            if u.get("username") == user_info.get("username") or u.get("email") == user_info.get("email"):
                u.update(user_info)
                if password:
                    u["password"] = password
                existing = True
                break
        if not existing:
            user_record = dict(user_info)
            if password:
                user_record["password"] = password
            self.data["local_users"].append(user_record)
        save_data(self.data)

    def go_to_main(self):
        try:
            self.current_tab = 0
            # 先清除登录页的dialog
            if self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
            self.build_main_ui()
            self.render_email_list()
        except Exception as e:
            # 如果出错，显示错误页面，避免白屏
            self._show_error_page("加载主界面失败", str(e))

    # ========== 主界面 ==========
    def build_main_ui(self):
        self.page.controls.clear()
        # 恢复用户设置的主题背景（登录/注册页强制白色，进入主界面恢复）
        self._apply_theme_mode()
        self.content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        # 底部胶囊导航栏（Column布局，稳定不白屏；此环境Stack悬浮渲染失败）
        self._navbar_area = ft.Container(
            content=self._build_custom_navbar(),
            alignment=ft.alignment.center,
            padding=ft.padding.only(bottom=16, top=8),
            bgcolor=ft.colors.TRANSPARENT,
        )
        main_col = ft.Column([
            ft.Container(content=self.content, expand=True),
            self._navbar_area,
        ], spacing=0, expand=True)
        self.page.add(main_col)
        self.page.navigation_bar = None
        self.page.update()

    def _build_custom_navbar(self):
        """构建浮动胶囊形状的底部导航栏（毛玻璃半透明 + 选中项高亮）"""
        mode = self.settings.get("theme_mode", "system")
        is_dark = mode == "dark"
        navbar_bg = ft.colors.with_opacity(0.65, ft.colors.BLACK if is_dark else ft.colors.WHITE)
        unselected_color = ft.colors.GREY_400 if is_dark else ft.colors.GREY_500
        items = [
            {"index": 0, "icon": ft.icons.MAIL_OUTLINE, "selected_icon": ft.icons.MAIL, "label": "邮箱"},
            {"index": 1, "icon": ft.icons.MESSAGE_OUTLINED, "selected_icon": ft.icons.MESSAGE, "label": "频道"},
            {"index": 2, "icon": ft.icons.PERSON_OUTLINE, "selected_icon": ft.icons.PERSON, "label": "主页"},
        ]
        nav_items = []
        for item in items:
            selected = self.current_tab == item["index"]
            if selected:
                nav_items.append(ft.Container(
                    content=ft.Column([
                        ft.Icon(item["selected_icon"], size=22, color=ft.colors.WHITE),
                        ft.Container(height=2),
                        ft.Text(item["label"], size=11, color=ft.colors.WHITE, weight=ft.FontWeight.W_600),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=10),
                    bgcolor=THEME_COLOR, border_radius=18,
                    on_click=lambda e, idx=item["index"]: self._on_custom_tab_change(idx),
                ))
            else:
                nav_items.append(ft.Container(
                    content=ft.Column([
                        ft.Icon(item["icon"], size=22, color=unselected_color),
                        ft.Container(height=2),
                        ft.Text(item["label"], size=11, color=unselected_color),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=10),
                    border_radius=18,
                    on_click=lambda e, idx=item["index"]: self._on_custom_tab_change(idx),
                ))
        return ft.Container(
            content=ft.Row(nav_items, spacing=4),
            bgcolor=navbar_bg, border_radius=30,
            padding=ft.padding.all(6), width=310,
        )

    def _on_custom_tab_change(self, idx):
        """自定义导航栏切换"""
        self.current_tab = idx
        try:
            self._stop_page_tasks()
        except:
            pass
        try:
            if idx == 0:
                self.render_email_list()
            elif idx == 1:
                self.render_channel_page()
            elif idx == 2:
                self.render_me_page()
        except:
            pass
        # 更新导航栏选中状态
        try:
            self._navbar_area.content = self._build_custom_navbar()
            self.page.update()
        except:
            pass

    def on_tab_change(self, e):
        idx = e.control.selected_index
        self.current_tab = idx
        try:
            # 停止之前页面的后台任务
            self._stop_page_tasks()
        except:
            pass
        try:
            if idx == 0:
                self.render_email_list()
            elif idx == 1:
                self.render_channel_page()
            elif idx == 2:
                self.render_me_page()
        except Exception as ex:
            # 页面渲染失败时显示错误，避免导航无响应
            try:
                self._show_error_page("页面加载失败", str(ex))
            except:
                pass
    
    def _stop_page_tasks(self):
        """停止当前页面的后台任务"""
        try:
            # 停止邮箱倒计时
            self._stop_countdown()
        except:
            pass
        try:
            # 停止收件箱自动刷新
            self._stop_inbox_auto_refresh()
        except:
            pass

    # ========== 邮箱列表 ==========
    def render_email_list(self):
        self.content.controls.clear()
        self._stop_countdown()
        # 标题固定，不可滑动
        self.content.scroll = None
        # 加载状态文本
        self._loading_status = ft.Text("⏳ 正在获取邮件...", size=12, color=THEME_COLOR)
        # 标题区域（固定，背景和页面一致，顶部留空给灵动岛）
        header = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("临时邮箱", size=28, weight=ft.FontWeight.BOLD, color=self.clr_text),
                        ft.Container(width=8),
                        self._loading_status,
                        ft.Container(expand=True),
                        ft.IconButton(ft.icons.ADD_CIRCLE, icon_size=30, icon_color=THEME_COLOR, on_click=self.create_email),
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(20, 50, 10, 5),
                ),
                ft.Container(
                    content=ft.Text("创建临时邮箱，自动接收邮件", size=13, color=self.clr_text2),
                    padding=ft.padding.only(20, 0, 20, 10),
                ),
            ], spacing=0),
        )
        self.content.controls.append(header)
        # 邮箱列表区域（可滑动）
        self._email_list_container = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._email_list_container)
        # 先显示本地邮箱
        self._render_email_items()
        # 去掉底部悬浮按钮（改用标题栏右侧加号，避免和自定义底部导航栏冲突）
        self.page.floating_action_button = None
        self.page.update()
        self._start_countdown()
        # 从云端加载用户邮箱（带缓存，避免频繁切换时重复加载）
        current_time = time.time()
        last_sync = getattr(self, '_last_email_sync_time', 0)
        if current_time - last_sync > 10:  # 10秒内不重复同步
            self._last_email_sync_time = current_time
            threading.Thread(target=self._sync_emails_from_cloud, daemon=True).start()
        else:
            # 10秒内不重复同步，直接隐藏加载状态
            self._hide_loading_status()

    def _hide_loading_status(self):
        """隐藏加载状态"""
        try:
            if hasattr(self, '_loading_status') and self._loading_status:
                self._loading_status.value = "✓ 已同步"
                self._loading_status.color = ft.colors.GREEN
                self.page.update()
        except:
            pass

    def _sync_emails_from_cloud(self):
        """从云端同步用户邮箱（不保存到本地，直接更新UI）"""
        try:
            if not self.current_user:
                self.page.run_thread(self._hide_loading_status)
                return
            cloud_emails = self._load_user_emails_from_cloud()
            # 不保存到本地，直接用云端邮箱更新UI
            self._cloud_emails_cache = cloud_emails if cloud_emails else []
            self.page.run_thread(self._render_email_items)
            # 隐藏加载状态
            self.page.run_thread(self._hide_loading_status)
        except Exception as e:
            self._cloud_emails_cache = []
            self.page.run_thread(self._render_email_items)
            self.page.run_thread(self._hide_loading_status)
            pass
        # 同步完成后，后台获取每个邮箱的真实邮件数量
        self.page.run_thread(self._fetch_all_message_counts)

    # ========== 邮件数量统计 ==========
    def _get_email_message_count(self, em):
        """获取单个邮箱的真实邮件数量（不阻塞UI）"""
        try:
            provider = str(em.get("provider", "")).lower()
            token = em.get("token", "")
            addr = em.get("address", "")
            login = em.get("login", addr.split("@")[0] if "@" in addr else "")
            if provider in ["gmail", "gmail别名", "gmail_alias"]:
                # Gmail别名无法在应用内获取，返回-1表示"去Gmail查看"
                return -1
            elif provider in ["mailtm", "mail.tm", "mail_tm"]:
                if token:
                    ok, result = mailtm_get_messages(token)
                    if ok:
                        if isinstance(result, dict):
                            return len(result.get("hydra:member", []))
                        return len(result) if isinstance(result, list) else 0
                return 0
            elif provider in ["guerrilla", "guerrillamail", "guerrilla_mail"]:
                if token:
                    ok, messages = guerrilla_get_messages(token)
                    return len(messages) if ok and isinstance(messages, list) else 0
                return 0
            elif provider in ["maildrop", "mail_drop"]:
                if login:
                    ok, messages = maildrop_get_messages(login)
                    return len(messages) if ok and isinstance(messages, list) else 0
                return 0
            elif provider in ["tempmailio", "temp-mail.io", "temp_mail_io", "tempmail"]:
                if addr:
                    ok, messages = temp_mail_io_get_messages(addr)
                    return len(messages) if ok and isinstance(messages, list) else 0
                return 0
            elif provider in ["internal", "cloud", "内部邮箱", "云端邮箱"]:
                ok, result = self._remote_api_request("GET", "messages", params={"email": addr})
                if ok and isinstance(result, dict) and result.get("ok"):
                    return len(result.get("data", []))
                return 0
            return 0
        except:
            return 0

    def _fetch_all_message_counts(self):
        """后台获取所有邮箱的真实邮件数量，更新UI"""
        try:
            emails = getattr(self, '_cloud_emails_cache', [])
            if not emails:
                return
            # 初始化数量缓存
            if not hasattr(self, '_msg_counts'):
                self._msg_counts = {}
            changed = False
            for em in emails:
                email_id = em.get("id", "") or em.get("cloud_id", "")
                if not email_id:
                    continue
                # 如果已经有缓存且在60秒内，不重复获取
                last_fetch = self._msg_counts.get(email_id + "_time", 0)
                if time.time() - last_fetch < 60:
                    continue
                count = self._get_email_message_count(em)
                self._msg_counts[email_id] = count
                self._msg_counts[email_id + "_time"] = time.time()
                changed = True
            if changed:
                self.page.run_thread(self._render_email_items)
        except:
            pass

    def _get_total_message_count(self):
        """计算所有邮箱的邮件总数（用于主页统计）"""
        try:
            emails = getattr(self, '_cloud_emails_cache', [])
            if not emails:
                return 0
            total = 0
            for em in emails:
                email_id = em.get("id", "") or em.get("cloud_id", "")
                count = getattr(self, '_msg_counts', {}).get(email_id, 0)
                if count > 0:
                    total += count
                else:
                    # 没有缓存的，用messages列表长度
                    total += len(em.get("messages", []))
            return total
        except:
            return 0

    def _render_email_items(self):
        """渲染邮箱列表项（从云端缓存获取，不使用本地存储）"""
        self._email_list_container.controls.clear()
        # 从云端缓存获取邮箱列表，不使用本地存储
        emails = getattr(self, '_cloud_emails_cache', [])
        if not emails:
            empty_icon_path = self._get_empty_email_icon_path()
            self._email_list_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Image(src=empty_icon_path, width=100, height=100, fit=ft.ImageFit.CONTAIN),
                    ft.Text("暂无邮箱", size=20, weight=ft.FontWeight.W_500, color=self.clr_text2),
                    ft.Text("点击右下角按钮创建临时邮箱", size=13, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 80, 0, 0),
            ))
            return
        for idx, em in enumerate(emails):
            addr = em.get("address", "")
            expires_at = em.get("expires_at", 0)
            is_permanent = em.get("is_permanent", False)
            # 处理expires_at格式：如果是字符串，转换为时间戳
            if isinstance(expires_at, str):
                try:
                    # 尝试解析 "2026-09-04 18:41:52" 格式
                    expires_at = time.mktime(time.strptime(expires_at, "%Y-%m-%d %H:%M:%S"))
                except:
                    try:
                        # 尝试解析ISO格式
                        expires_at = time.mktime(time.strptime(expires_at, "%Y-%m-%dT%H:%M:%S"))
                    except:
                        expires_at = 0
            try:
                remaining = float(expires_at) - time.time()
            except:
                remaining = 0
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
            email_id = em.get("id", "")
            cloud_id = em.get("cloud_id", email_id)
            # 优先使用后台获取的真实邮件数量，其次用messages列表长度
            cache_key = email_id or cloud_id
            cached_count = getattr(self, '_msg_counts', {}).get(cache_key, None)
            if cached_count is not None:
                msg_count = cached_count
            else:
                msg_count = len(em.get("messages", []))
            is_real = em.get("is_real", True)
            domain = em.get("domain", "")
            type_names = {"emalupe.com": "mail.tm", "guerrillamailblock.com": "Guerrilla", "maildrop.cc": "maildrop", "temp-mail.io": "temp-mail.io", "admin.local": "云端邮箱"}
            type_name = type_names.get(domain, domain)
            # ID显示（从1开始排序，按照创建时间顺序）
            id_display = f"ID:{idx + 1}"
            self._email_list_container.controls.append(ft.Container(
                content=ft.Column([
                    # 第一行：标签行（邮箱类型 + 邮件数量 + ID）
                    ft.Row([
                        ft.Container(content=ft.Text(type_name, size=FONT_XS, color=ft.colors.WHITE, weight=FONT_MEDIUM),
                            bgcolor=COLOR_SUCCESS if is_real else COLOR_WARNING,
                            border_radius=RADIUS_PILL, padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            alignment=ft.alignment.center),
                        ft.Container(width=6),
                        ft.Container(content=ft.Text("Gmail收信" if msg_count == -1 else f"{msg_count}封邮件", size=FONT_XS, color=ft.colors.WHITE, weight=FONT_MEDIUM),
                            bgcolor=COLOR_WARNING if msg_count == -1 else THEME_COLOR,
                            border_radius=RADIUS_PILL, padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            alignment=ft.alignment.center),
                        ft.Container(width=6),
                        ft.Container(content=ft.Text(id_display, size=FONT_XS, color=ft.colors.WHITE, weight=FONT_MEDIUM),
                            bgcolor=self.clr_text2,
                            border_radius=RADIUS_PILL, padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            alignment=ft.alignment.center),
                    ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=SPACE_SM),
                    # 第二行：邮箱地址
                    ft.Text(addr, size=FONT_LG, weight=FONT_SEMIBOLD, color=self.clr_text),
                    ft.Container(height=SPACE_XS),
                    # 第三行：过期时间
                    ft.Text(exp_time, size=FONT_SM, color=exp_color, weight=FONT_MEDIUM),
                    ft.Row([
                        ft.TextButton("查看收件箱", on_click=lambda e, email=em: self.show_inbox(email),
                            style=ft.ButtonStyle(color=THEME_COLOR)),
                        ft.TextButton("复制", on_click=lambda e, a=addr: self._copy_email(a),
                            style=ft.ButtonStyle(color=self.clr_text2)),
                        ft.TextButton("删除", on_click=lambda e, eid=email_id: self._delete_email(eid),
                            style=ft.ButtonStyle(color=COLOR_DANGER)),
                    ], spacing=0),
                ], spacing=SPACE_XS),
                bgcolor=self.clr_card, border_radius=RADIUS_LG, padding=SPACE_LG,
                margin=ft.margin.only(SPACE_LG, 6, SPACE_LG, 6),
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=10,
                    color=ft.colors.with_opacity(0.07, ft.colors.BLACK),
                    offset=ft.Offset(0, 3),
                ),
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
        # 弹出选择邮箱类型的弹窗（只保留可以正常使用的邮箱类型）
        email_types = [
            {"name": "Gmail 邮箱", "domain": "gmail.com", "icon_file": "gmail_icon.png", "real": True, "provider": "gmail"},
            {"name": "mail.tm 邮箱", "domain": "emalupe.com", "icon_file": "mailtm_icon.png", "real": True, "provider": "mailtm"},
        ]
        type_buttons = []
        for et in email_types:
            # 所有邮箱类型都用官方图标图片
            icon_widget = ft.Image(src=et["icon_file"], width=28, height=28, fit=ft.ImageFit.CONTAIN)
            type_buttons.append(ft.Container(
                content=ft.Row([
                    icon_widget,
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
        # 如果是 Gmail 类型，直接使用默认的 Gmail 地址，不弹出输入框
        if email_type.get("provider") == "gmail":
            self._pending_gmail = "yoxiyouxiang@gmail.com"
            self._show_duration_options()
            return
        # 其他类型直接弹出选择有效期的弹窗
        self._show_duration_options()

    def _show_gmail_input(self):
        """显示 Gmail 地址输入框"""
        self._gmail_input = ft.TextField(
            label="输入你的 Gmail 地址",
            hint_text="例如：yourname@gmail.com",
            width=300,
        )
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Gmail 无限别名", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("输入你的 Gmail 地址，将生成 + 别名邮箱", size=13, color=ft.colors.GREY_600),
                ft.Container(height=10),
                self._gmail_input,
                ft.Container(height=10),
                ft.Text("💡 所有发送到别名的邮件都会到你的主 Gmail", size=11, color=ft.colors.BLUE_500),
            ], spacing=0, tight=True),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("下一步", on_click=lambda e: self._confirm_gmail()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _confirm_gmail(self):
        """确认 Gmail 地址"""
        gmail = self._gmail_input.value.strip() if self._gmail_input.value else ""
        if not gmail or "@" not in gmail:
            self.page.snack_bar = ft.SnackBar(ft.Text("请输入有效的邮箱地址"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        # 放宽验证，只要是邮箱格式都可以（支持 gmail.com、googlemail.com 等）
        self._pending_gmail = gmail.lower()
        self._close_dialog()
        self._show_duration_options()

    def _show_duration_options(self):
        """显示有效期选择（只能使用默认的，其他的变灰色不可点击，需要在设置中更改默认值）"""
        duration_options = [
            {"name": "1小时", "hours": 1, "icon": "⏱️"},
            {"name": "2小时", "hours": 2, "icon": "⏰"},
            {"name": "永久", "hours": -1, "icon": "♾️"},
        ]
        # 获取设置中的默认有效期
        default_hours = self.settings.get("default_duration_hours", 1)
        dur_buttons = []
        for d in duration_options:
            is_default = d["hours"] == default_hours
            if is_default:
                # 默认选项：正常显示，可点击
                dur_buttons.append(ft.Container(
                    content=ft.Row([
                        ft.Text(d["icon"], size=24),
                        ft.Container(width=12),
                        ft.Text(d["name"], size=16, weight=ft.FontWeight.W_500, expand=True,
                            color=THEME_COLOR),
                        ft.Container(content=ft.Text("默认", size=10, color=ft.colors.WHITE),
                            bgcolor=THEME_COLOR, border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            alignment=ft.alignment.center),
                    ], alignment=ft.MainAxisAlignment.START),
                    bgcolor=ft.colors.WHITE, border_radius=12, padding=16,
                    margin=ft.margin.only(0, 4, 0, 4),
                    border=ft.border.all(2, THEME_COLOR),
                    on_click=lambda e, dur=d: self._select_email_duration(dur),
                ))
            else:
                # 非默认选项：变灰色，不可点击，提示需要在设置中更改
                dur_buttons.append(ft.Container(
                    content=ft.Row([
                        ft.Text(d["icon"], size=24, color=ft.colors.GREY_400),
                        ft.Container(width=12),
                        ft.Text(d["name"], size=16, weight=ft.FontWeight.W_500, expand=True,
                            color=ft.colors.GREY_400),
                        ft.Container(content=ft.Text("需在设置中更改", size=9, color=ft.colors.GREY_400),
                            bgcolor=ft.colors.GREY_200, border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            alignment=ft.alignment.center),
                    ], alignment=ft.MainAxisAlignment.START),
                    bgcolor=ft.colors.GREY_100, border_radius=12, padding=16,
                    margin=ft.margin.only(0, 4, 0, 4),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    # 不可点击，点击时提示
                    on_click=lambda e: self._show_toast("该有效期未启用，请在设置中更改默认有效期"),
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
            if provider == "gmail":
                # Gmail 无限别名 - 真正能收邮件
                gmail = getattr(self, '_pending_gmail', '')
                if not gmail:
                    self.page.run_thread(self._close_loading_dialog)
                    self.page.run_thread(lambda: self._show_create_error("未设置 Gmail 地址"))
                    return
                # 生成 + 别名（所有发送到别名的邮件都会到主 Gmail）
                base = gmail.split("@")[0]
                alias = base + "+" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "@gmail.com"
                new_email = {
                    "id": str(int(time.time() * 1000)),
                    "address": alias,
                    "login": alias.split("@")[0],
                    "domain": "gmail.com",
                    "password": "",
                    "token": "",
                    "account_id": "",
                    "provider": "gmail",
                    "base_gmail": gmail,
                    "created_at": time.time(),
                    "expires_at": time.time() + (hours * 3600 if not is_permanent else 9999999999),
                    "is_permanent": is_permanent,
                    "messages": [],
                    "is_real": True,
                }
                time.sleep(0.3)
                # 不保存到本地，直接保存到云端，然后从云端重新加载（和其他类型保持一致）
                def save_and_reload():
                    self._save_email_to_cloud(new_email)
                    time.sleep(0.5)
                    self._sync_emails_from_cloud()
                threading.Thread(target=save_and_reload, daemon=True).start()
                self.page.run_thread(self._close_loading_dialog)
                self.page.run_thread(self.render_email_list)
            elif provider == "mailtm":
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
                    # 不保存到本地，直接保存到云端，然后从云端重新加载
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                    threading.Thread(target=save_and_reload, daemon=True).start()
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
                    # 不保存到本地，直接保存到云端，然后从云端重新加载
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                    threading.Thread(target=save_and_reload, daemon=True).start()
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
                self.data["emails"].append(new_email)
                save_data(self.data)
                threading.Thread(target=lambda: self._save_email_to_cloud(new_email), daemon=True).start()
                self.page.run_thread(self._close_loading_dialog)
                self.page.run_thread(self.render_email_list)
            elif provider == "tempmailio":
                # temp-mail.io API - 恢复原来的创建逻辑
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
                    # 不保存到本地，直接保存到云端，然后从云端重新加载
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                    threading.Thread(target=save_and_reload, daemon=True).start()
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
        # 从云端缓存中找到要删除的邮箱
        email_to_delete = None
        cloud_emails = getattr(self, '_cloud_emails_cache', [])
        for e in cloud_emails:
            if e.get("id") == email_id or e.get("cloud_id") == email_id:
                email_to_delete = e
                break
        # 不修改本地，直接从云端删除，然后从云端重新加载
        if email_to_delete:
            cloud_id = email_to_delete.get("cloud_id", email_to_delete.get("id", ""))
            if cloud_id:
                def delete_and_reload():
                    self._delete_email_from_cloud(cloud_id)
                    time.sleep(0.5)
                    self._sync_emails_from_cloud()
                threading.Thread(target=delete_and_reload, daemon=True).start()
        self.page.snack_bar = ft.SnackBar(ft.Text("已删除邮箱"))
        self.page.snack_bar.open = True
        self.render_email_list()

    # ========== 收件箱页面 ==========
    def _back_to_email_list(self):
        """返回邮箱列表，停止自动刷新"""
        self._stop_inbox_auto_refresh()
        self.render_email_list()

    def show_inbox(self, email):
        self.current_email = email
        self.content.controls.clear()
        self.page.floating_action_button = None
        # 顶部栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self._back_to_email_list()),
                ft.Text("收件箱", size=20, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_inbox()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text(email.get("address", ""), size=13, color=ft.colors.GREY_500),
            padding=ft.padding.only(20, 0, 20, 10),
        ))
        self._inbox_list = ft.ListView([], spacing=0, expand=True, padding=10)
        self.content.controls.append(self._inbox_list)
        self.page.update()
        self.refresh_inbox()
        # 启动自动刷新（每10秒刷新一次收件箱）
        self._start_inbox_auto_refresh()

    def refresh_inbox(self):
        email = self.current_email
        provider = email.get("provider", "mailtm")

        def refresh_thread():
            messages = []
            try:
                # 兼容各种provider类型名称
                provider_lower = str(provider).lower()
                if provider_lower in ["gmail", "gmail别名", "gmail_alias"]:
                    # Gmail 别名 - 先尝试从网站后端获取邮件，如果获取不到再提示用户去 Gmail 查看
                    base_gmail = email.get("base_gmail", "")
                    gmail_addr = email.get("address", "")
                    try:
                        ok, result = self._remote_api_request("GET", "messages", params={"email": gmail_addr})
                        if ok and isinstance(result, dict) and result.get("ok"):
                            messages = result.get("data", [])
                            # 成功从网站后端获取到邮件，继续渲染
                        else:
                            # 网站后端没有实现messages API，提示用户去Gmail查看
                            self.page.run_thread(lambda: self._show_gmail_inbox_hint(base_gmail))
                            return
                    except:
                        # 获取异常，提示用户去Gmail查看
                        self.page.run_thread(lambda: self._show_gmail_inbox_hint(base_gmail))
                        return
                elif provider_lower in ["mailtm", "mail.tm", "mail_tm"]:
                    token = email.get("token", "")
                    if token:
                        ok, result = mailtm_get_messages(token)
                        if ok:
                            messages = result.get("hydra:member", []) if isinstance(result, dict) else result
                        else:
                            self.page.run_thread(lambda: self._show_inbox_error(str(result)))
                            return
                    else:
                        self.page.run_thread(lambda: self._show_inbox_error("邮箱token为空，无法获取邮件"))
                        return
                elif provider_lower in ["guerrilla", "guerrillamail", "guerrilla_mail"]:
                    token = email.get("token", "")
                    if token:
                        ok, messages = guerrilla_get_messages(token)
                        if not ok:
                            self.page.run_thread(lambda: self._show_inbox_error(str(messages)))
                            return
                    else:
                        self.page.run_thread(lambda: self._show_inbox_error("邮箱token为空，无法获取邮件"))
                        return
                elif provider_lower in ["maildrop", "mail_drop"]:
                    login = email.get("login", "")
                    if login:
                        ok, messages = maildrop_get_messages(login)
                        if not ok:
                            self.page.run_thread(lambda: self._show_inbox_error(str(messages)))
                            return
                    else:
                        self.page.run_thread(lambda: self._show_inbox_error("邮箱登录名为空，无法获取邮件"))
                        return
                elif provider_lower in ["tempmailio", "temp-mail.io", "temp_mail_io", "tempmail"]:
                    addr = email.get("address", "")
                    if addr:
                        ok, messages = temp_mail_io_get_messages(addr)
                        if not ok:
                            # 检查是否是邮箱不存在的错误（400 Bad Request, Email not found）
                            error_msg = str(messages)
                            if "400" in error_msg or "not found" in error_msg.lower() or "Email not found" in error_msg:
                                self.page.run_thread(lambda: self._show_inbox_error("邮箱已过期或不存在，请删除后重新创建邮箱"))
                            else:
                                self.page.run_thread(lambda: self._show_inbox_error(error_msg))
                            return
                    else:
                        self.page.run_thread(lambda: self._show_inbox_error("邮箱地址为空，无法获取邮件"))
                        return
                elif provider_lower in ["internal", "cloud", "内部邮箱", "云端邮箱"]:
                    # 内部邮箱或云端邮箱，尝试从网站API获取邮件列表
                    ok, result = self._remote_api_request("GET", "messages", params={"email": email.get("address", "")})
                    if ok and isinstance(result, dict) and result.get("ok"):
                        messages = result.get("data", [])
                    else:
                        messages = []
                else:
                    messages = []
            except Exception as e:
                self.page.run_thread(lambda: self._show_inbox_error(f"获取邮件异常: {str(e)}"))
                return

            email["messages"] = messages
            # 更新云端缓存中的邮件列表
            cloud_emails = getattr(self, '_cloud_emails_cache', [])
            for em in cloud_emails:
                if em.get("id") == email.get("id") or em.get("cloud_id") == email.get("cloud_id"):
                    em["messages"] = messages
                    break
            self.page.run_thread(lambda: self._render_inbox_messages(messages))
        threading.Thread(target=refresh_thread, daemon=True).start()

    def _start_inbox_auto_refresh(self):
        """启动收件箱自动刷新（间隔由设置决定，可在设置中关闭）"""
        # 检查设置中是否开启了自动刷新
        if not self.settings.get("inbox_auto_refresh", True):
            return
        self._inbox_refresh_running = True
        def auto_refresh_loop():
            while getattr(self, '_inbox_refresh_running', False):
                interval = self.settings.get("refresh_interval", 10)
                time.sleep(interval)
                # 每次循环都检查设置，用户在设置中关闭后立即停止
                if not self.settings.get("inbox_auto_refresh", True):
                    break
                if getattr(self, '_inbox_refresh_running', False) and self.current_email:
                    try:
                        self.refresh_inbox()
                    except:
                        pass
        threading.Thread(target=auto_refresh_loop, daemon=True).start()

    def _stop_inbox_auto_refresh(self):
        """停止收件箱自动刷新"""
        self._inbox_refresh_running = False

    def _render_inbox_messages(self, messages):
        self._inbox_list.controls.clear()
        if not messages:
            empty_icon_path = self._get_empty_email_icon_path()
            self._inbox_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Image(src=empty_icon_path, width=80, height=80, fit=ft.ImageFit.CONTAIN),
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
                    sender = decode_mime(msg.get("mail_from", "未知"))
                    subject = decode_mime(msg.get("mail_subject", "(无主题)"))
                    date = msg.get("mail_date", "")
                elif "from" in msg and isinstance(msg.get("from"), dict):
                    # mail.tm 格式
                    from_name = decode_mime(msg.get("from", {}).get("name", ""))
                    from_addr = decode_mime(msg.get("from", {}).get("address", "未知"))
                    sender = from_name + " <" + from_addr + ">" if from_name else from_addr
                    subject = decode_mime(msg.get("subject", "(无主题)"))
                    date = msg.get("createdAt", "")
                elif "from" in msg and isinstance(msg.get("from"), str) and "to" in msg:
                    # temp-mail.io 格式
                    sender = decode_mime(msg.get("from", "未知"))
                    subject = decode_mime(msg.get("subject", "(无主题)"))
                    date = msg.get("created_at", msg.get("date", ""))
                else:
                    # maildrop 或其他格式
                    sender = decode_mime(msg.get("mailfrom", msg.get("from", "未知")))
                    subject = decode_mime(msg.get("subject", "(无主题)"))
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

    def _show_gmail_inbox_hint(self, base_gmail):
        """显示 Gmail 收件箱提示"""
        self._inbox_list.controls.clear()
        self._inbox_list.controls.append(ft.Container(
            content=ft.Column([
                ft.Text("📬", size=60),
                ft.Container(height=10),
                ft.Text("Gmail 别名邮箱", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                ft.Text("所有发送到此别名的邮件都会到你的主 Gmail", size=13, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("主邮箱：" + base_gmail, size=12, color=ft.colors.BLUE_500),
                    bgcolor=ft.colors.BLUE_50,
                    border_radius=8,
                    padding=10,
                ),
                ft.Container(height=15),
                ft.Container(
                    content=ft.Text("💡 请登录 Gmail 查看邮件", size=13, color=ft.colors.ORANGE_600),
                    alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            alignment=ft.alignment.center,
            padding=ft.padding.only(0, 60, 0, 0),
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
            ok = False
            detail = "未知邮箱类型"
            try:
                # 兼容各种provider类型名称
                provider_lower = str(provider).lower()
                addr = email.get("address", "")
                login = email.get("login", addr.split("@")[0] if "@" in addr else "")
                
                if provider_lower in ["mailtm", "mail.tm", "mail_tm"]:
                    token = email.get("token", "")
                    if token:
                        ok, detail = mailtm_read_message(token, msg_id)
                    else:
                        # token为空，尝试用邮箱地址重新获取token
                        try:
                            password = email.get("password", "")
                            if addr and password:
                                ok2, token_data = mailtm_request("POST", "/token", {"address": addr, "password": password})
                                if ok2 and isinstance(token_data, dict) and token_data.get("token"):
                                    new_token = token_data.get("token")
                                    email["token"] = new_token
                                    ok, detail = mailtm_read_message(new_token, msg_id)
                                else:
                                    detail = "邮箱token已失效，且无法重新获取，请重新创建邮箱"
                            else:
                                detail = "邮箱token为空，且缺少密码无法重新获取，请重新创建邮箱"
                        except:
                            detail = "邮箱token为空，无法读取邮件，请重新创建邮箱"
                elif provider_lower in ["guerrilla", "guerrillamail", "guerrilla_mail"]:
                    token = email.get("token", "")
                    if token:
                        ok, detail = guerrilla_read_message(token, msg_id)
                    else:
                        # token为空，尝试用邮箱地址重新获取
                        try:
                            if addr:
                                ok2, addr_data = guerrilla_get_address()
                                if ok2:
                                    # Guerrilla邮箱需要sid_token，尝试重新获取
                                    ok3, msg_data = guerrilla_get_messages(addr_data.get("sid_token", ""))
                                    if ok3 and isinstance(msg_data, list):
                                        for m in msg_data:
                                            if str(m.get("mail_id", "")) == str(msg_id) or str(m.get("id", "")) == str(msg_id):
                                                detail = m
                                                ok = True
                                                break
                                if not ok:
                                    detail = "邮箱会话已失效，请返回收件箱刷新后重试"
                            else:
                                detail = "邮箱地址为空，无法读取邮件"
                        except:
                            detail = "邮箱会话已失效，请返回收件箱刷新后重试"
                elif provider_lower in ["maildrop", "mail_drop"]:
                    if login:
                        ok, detail = maildrop_read_message(login, msg_id)
                    elif addr:
                        # 没有login，尝试从地址提取
                        login = addr.split("@")[0] if "@" in addr else ""
                        if login:
                            ok, detail = maildrop_read_message(login, msg_id)
                        else:
                            detail = "邮箱登录名为空，无法读取邮件"
                    else:
                        detail = "邮箱登录名为空，无法读取邮件"
                elif provider_lower in ["tempmailio", "temp-mail.io", "temp_mail_io", "tempmail"]:
                    if addr:
                        ok, detail = temp_mail_io_read_message(addr, msg_id)
                        if not ok:
                            # 检查是否是邮箱不存在的错误
                            error_msg = str(detail)
                            if "400" in error_msg or "not found" in error_msg.lower() or "Email not found" in error_msg:
                                detail = "邮箱已过期或不存在，请删除后重新创建邮箱"
                    else:
                        detail = "邮箱地址为空，无法读取邮件"
                elif provider_lower in ["gmail", "gmail别名", "gmail_alias"]:
                    # Gmail别名邮箱，尝试从网站API获取邮件详情（和内部邮箱一样）
                    ok, detail = self._load_internal_email_detail(msg_id)
                    if not ok:
                        # 如果获取失败，设置ok=False，让后面的回退逻辑尝试显示邮件列表中的基本信息
                        ok = False
                        detail = "Gmail别名邮箱，获取邮件详情失败"
                elif provider_lower in ["internal", "cloud", "内部邮箱", "云端邮箱"]:
                    # 内部邮箱或云端邮箱，尝试从网站API获取邮件详情
                    ok, detail = self._load_internal_email_detail(msg_id)
                else:
                    detail = f"不支持的邮箱类型: {provider}"
                
                # 如果还是失败，尝试直接显示邮件列表中的基本信息
                if not ok and msg:
                    try:
                        subject = msg.get("subject", msg.get("mail_subject", "(无主题)"))
                        sender = msg.get("from", msg.get("mail_from", msg.get("sender", "未知")))
                        date = msg.get("date", msg.get("mail_date", msg.get("created_at", "")))
                        # 兼容多种字段格式（包括网站后端返回的content、body、snippet）
                        body = msg.get("body", 
                            msg.get("content", 
                            msg.get("intro", 
                            msg.get("excerpt", 
                            msg.get("preview", 
                            msg.get("snippet", "(无法获取邮件正文，请返回收件箱查看)"))))))
                        # 只要有邮件内容就显示（即使主题为空）
                        detail = {
                            "subject": subject if subject else "(无主题)",
                            "from": sender,
                            "date": date,
                            "body": body,
                        }
                        ok = True
                    except:
                        pass
            except Exception as e:
                ok = False
                detail = f"读取邮件异常: {str(e)}"

            if ok:
                self.page.run_thread(lambda: self._render_email_detail(detail))
            else:
                self.page.run_thread(lambda: self._show_detail_error(str(detail)))
        threading.Thread(target=load_thread, daemon=True).start()

    def _load_internal_email_detail(self, msg_id):
        """从网站API获取内部邮箱的邮件详情"""
        try:
            # 尝试从网站API获取邮件详情
            ok, result = self._remote_api_request("GET", f"messages/{msg_id}")
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                # 转换为统一格式
                return True, {
                    "subject": data.get("subject", "(无主题)"),
                    "from": data.get("from", data.get("sender", "未知")),
                    "date": data.get("date", data.get("created_at", "")),
                    "body": data.get("body", data.get("content", "(无内容)")),
                }
            # 如果网站没有这个接口，返回友好提示
            return False, "内部邮箱暂不支持在线查看邮件详情"
        except Exception as e:
            return False, f"获取内部邮箱邮件失败: {str(e)}"

    def _render_email_detail(self, detail):
        self._detail_content.controls.clear()
        # 适配不同 provider 的数据格式
        if "mail_from" in detail:
            # Guerrilla Mail 格式
            sender = decode_mime(detail.get("mail_from", "未知"))
            subject = decode_mime(detail.get("mail_subject", "(无主题)"))
            date = detail.get("mail_date", "")
            body = detail.get("mail_body", detail.get("mail_excerpt", "(无内容)"))
        elif "from" in detail and isinstance(detail.get("from"), dict):
            # mail.tm 格式
            from_name = decode_mime(detail.get("from", {}).get("name", ""))
            from_addr = decode_mime(detail.get("from", {}).get("address", "未知"))
            sender = from_name + " <" + from_addr + ">" if from_name else from_addr
            subject = decode_mime(detail.get("subject", "(无主题)"))
            date = detail.get("createdAt", "")
            body = detail.get("text", detail.get("html", "(无内容)"))
            if isinstance(body, list):
                body = body[0].get("text", "") if body else "(无内容)"
        elif "from" in detail and isinstance(detail.get("from"), str) and "to" in detail:
            # temp-mail.io 格式
            sender = decode_mime(detail.get("from", "未知"))
            subject = decode_mime(detail.get("subject", "(无主题)"))
            date = detail.get("created_at", detail.get("date", ""))
            body = detail.get("body_text", detail.get("body", "(无内容)"))
        else:
            # maildrop 或其他格式
            sender = decode_mime(detail.get("mailfrom", detail.get("from", "未知")))
            subject = decode_mime(detail.get("subject", "(无主题)"))
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
    def render_channel_page(self):
        """频道列表页面"""
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("邮箱频道", size=28, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_channels()),
            ]),
            padding=ft.padding.only(20, 50, 20, 10),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text("加入频道，和大家一起交流", size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 0, 20, 10),
        ))

        # 管理员/超级管理员专属：管理卡片（在线人数、用户管理、黑名单）
        if self.current_user:
            user_role = str(self.current_user.get("role", ""))
            is_admin = user_role in ["超级管理员", "管理员", "admin", "Admin", "超级管理", "频道主"]
            if is_admin:
                # 在线人数卡片
                self._online_count_text = ft.Text("--", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text)
                online_card = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.icons.PEOPLE_OUTLINE, size=24, color=ft.colors.GREEN),
                            width=44, height=44, bgcolor=ft.colors.GREEN_50,
                            border_radius=22, alignment=ft.alignment.center,
                        ),
                        ft.Container(height=8),
                        ft.Text("在线人数", size=12, color=self.clr_text2),
                        self._online_count_text,
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
                    on_click=lambda e: self._show_toast("在线人数功能开发中"),
                )
                # 用户管理卡片
                user_mgmt_card = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.icons.MANAGE_ACCOUNTS, size=24, color=ft.colors.BLUE),
                            width=44, height=44, bgcolor=ft.colors.BLUE_50,
                            border_radius=22, alignment=ft.alignment.center,
                        ),
                        ft.Container(height=8),
                        ft.Text("用户管理", size=12, color=self.clr_text2),
                        ft.Text("管理", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
                    on_click=lambda e: self.show_user_management(),
                )
                # 黑名单卡片
                blacklist_card = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.icons.BLOCK, size=24, color=ft.colors.RED),
                            width=44, height=44, bgcolor=ft.colors.RED_50,
                            border_radius=22, alignment=ft.alignment.center,
                        ),
                        ft.Container(height=8),
                        ft.Text("黑名单", size=12, color=self.clr_text2),
                        ft.Text("封禁", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
                    on_click=lambda e: self.show_blacklist(),
                )
                self.content.controls.append(ft.Container(
                    content=ft.Row([online_card, user_mgmt_card, blacklist_card], spacing=10),
                    padding=ft.padding.symmetric(horizontal=16),
                ))
                self.content.controls.append(ft.Container(height=10))
                # 异步获取在线人数
                threading.Thread(target=self._fetch_online_count, daemon=True).start()

        self._channel_list = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._channel_list)
        self.page.update()
        # 加载频道列表（API待对接）
        self._load_channels()

    def _fetch_online_count(self):
        """获取在线人数（异步）"""
        try:
            # 这里以后对接获取在线人数的API，现在先显示注册用户数
            ok, result = self._remote_api_request("GET", "register-count")
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                if isinstance(data, dict):
                    count = data.get("register_count", 0)
                    # 更新在线人数显示（这里暂时用注册数代替，以后对接真实在线人数）
                    def update_count():
                        try:
                            if hasattr(self, '_online_count_text') and self._online_count_text:
                                self._online_count_text.value = str(count)
                                self.page.update()
                        except:
                            pass
                    self.page.run_thread(update_count)
        except:
            pass

    def _load_channels(self):
        """加载频道列表"""
        # 只留一个邮箱交流群，频道列表页面显示512个成员
        channels = [
            {"id": "1", "name": "邮箱交流群", "desc": "临时邮箱使用交流", "icon": "📧", "members": 512},
        ]
        self._render_channels(channels)

    def refresh_channels(self):
        """刷新频道列表"""
        self._load_channels()

    # ========== 用户管理 ==========
    def show_user_management(self):
        """用户管理页面（管理员/超级管理员专属）"""
        if not self.current_user:
            self._show_toast("请先登录")
            return
        user_role = str(self.current_user.get("role", ""))
        is_admin = user_role in ["超级管理员", "管理员", "admin", "Admin", "超级管理", "频道主"]
        if not is_admin:
            self._show_toast("无权限访问")
            return

        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None

        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_channel_page()),
                ft.Text("用户管理", size=20, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22,
                    on_click=lambda e: self._load_user_list()),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # 统计信息
        self._user_stats_text = ft.Text("加载中...", size=13, color=self.clr_text2)
        self.content.controls.append(ft.Container(
            content=self._user_stats_text,
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        # 用户列表（可滚动）
        self._user_list_container = ft.ListView([], spacing=8, expand=True, padding=16)
        self.content.controls.append(self._user_list_container)

        # 加载中提示
        self._user_list_container.controls.append(ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, color=THEME_COLOR),
                ft.Container(height=12),
                ft.Text("正在加载用户列表...", size=14, color=self.clr_text2),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=ft.padding.only(0, 60, 0, 0),
        ))

        self.page.update()
        # 异步加载用户列表
        threading.Thread(target=self._load_user_list, daemon=True).start()

    def show_blacklist(self):
        """黑名单页面（显示所有被封禁的用户）"""
        if not self.current_user:
            self._show_toast("请先登录")
            return
        user_role = str(self.current_user.get("role", ""))
        is_admin = user_role in ["超级管理员", "管理员", "admin", "Admin", "超级管理", "频道主"]
        if not is_admin:
            self._show_toast("无权限访问")
            return

        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None

        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_channel_page()),
                ft.Text("黑名单", size=20, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22,
                    on_click=lambda e: self._load_blacklist()),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # 统计信息
        self._blacklist_stats_text = ft.Text("加载中...", size=13, color=self.clr_text2)
        self.content.controls.append(ft.Container(
            content=self._blacklist_stats_text,
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        # 用户列表（可滚动）
        self._blacklist_container = ft.ListView([], spacing=8, expand=True, padding=16)
        self.content.controls.append(self._blacklist_container)

        # 加载中提示
        self._blacklist_container.controls.append(ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, color=ft.colors.RED),
                ft.Container(height=12),
                ft.Text("正在加载黑名单...", size=14, color=self.clr_text2),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=ft.padding.only(0, 60, 0, 0),
        ))

        self.page.update()
        # 异步加载黑名单
        threading.Thread(target=self._load_blacklist, daemon=True).start()

    def _load_blacklist(self):
        """从网站加载黑名单（只显示被封禁的用户）"""
        try:
            operator_id = self.current_user.get("id", "")
            # 获取用户总数（用于显示已封禁数量）
            count_ok, count_result = self._remote_api_request("GET", "users/count",
                body={"operator_id": operator_id}, get_with_body=True)
            banned = 0
            if count_ok and isinstance(count_result, dict) and count_result.get("ok"):
                data = count_result.get("data", {})
                banned = data.get("banned", 0)

            # 获取所有用户列表（API的status参数可能不生效，所以在应用端筛选）
            list_ok, list_result = self._remote_api_request("GET", "users",
                body={"page": 1, "page_size": 100, "status": "all", "operator_id": operator_id},
                get_with_body=True)

            users = []
            if list_ok and isinstance(list_result, dict) and list_result.get("ok"):
                data = list_result.get("data", {})
                all_users = data.get("users", [])
                # 在应用端筛选出status为banned的用户（API的status参数可能不生效）
                for user in all_users:
                    user_status = str(user.get("status", "")).lower()
                    if user_status in ["banned", "disabled", "blocked"]:
                        users.append(user)

            # 更新UI
            def update_ui():
                # 更新统计信息（使用实际筛选出的已封禁用户数，如果count接口返回的banned为0）
                actual_banned = len(users) if banned == 0 else banned
                self._blacklist_stats_text.value = f"共 {actual_banned} 个被封禁的用户"
                # 渲染黑名单列表
                self._render_blacklist(users)
                self.page.update()

            self.page.run_thread(update_ui)
        except Exception as e:
            self.page.run_thread(lambda: self._show_toast(f"加载失败: {str(e)[:30]}"))

    def _render_blacklist(self, users):
        """渲染黑名单列表"""
        self._blacklist_container.controls.clear()
        if not users:
            # 没有被封禁的用户
            self._blacklist_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=60, color=ft.colors.GREEN),
                        width=80, height=80, bgcolor=ft.colors.GREEN_50,
                        border_radius=40, alignment=ft.alignment.center,
                    ),
                    ft.Container(height=16),
                    ft.Text("没有封禁的用户", size=18, weight=ft.FontWeight.BOLD, color=self.clr_text),
                    ft.Container(height=6),
                    ft.Text("所有用户都在正常使用中", size=13, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 80, 0, 0),
            ))
            return

        is_super_admin = str(self.current_user.get("role", "")) in ["超级管理员", "超级管理"]

        for user in users:
            user_id = user.get("user_id", "")
            username = user.get("username", "")
            name = user.get("name", username)
            email = user.get("email", "")
            qq = user.get("qq", "")
            role = user.get("role", "用户")
            chat_role = user.get("chat_role", role)
            status = user.get("status", "banned")
            last_login = user.get("last_login", "-")

            # 角色颜色
            role_color = ft.colors.AMBER if chat_role in ["频道主", "频道组"] else (
                ft.colors.PURPLE if chat_role in ["运营", "管理员", "admin", "Admin", "超级管理", "超级管理员"] else (
                ft.colors.BLUE if chat_role == "测试" else ft.colors.GREY))
            role_badge = ft.Container(content=ft.Text(chat_role, size=10, color=ft.colors.WHITE),
                bgcolor=role_color, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.alignment.center)

            # 状态标签（已封禁）
            status_badge = ft.Container(content=ft.Text("已封禁", size=10, color=ft.colors.WHITE),
                bgcolor=ft.colors.RED, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.alignment.center)

            # 操作按钮
            unban_btn = ft.TextButton("解封",
                style=ft.ButtonStyle(color=ft.colors.GREEN),
                on_click=lambda e, uid=user_id, uname=username:
                    self._toggle_ban_user(uid, uname, True))

            delete_btn = ft.Container()
            if is_super_admin:
                delete_btn = ft.TextButton("删除",
                    style=ft.ButtonStyle(color=ft.colors.RED),
                    on_click=lambda e, uid=user_id, uname=username:
                        self._delete_user(uid, uname))

            # 用户卡片（半透明，表示已封禁）
            user_card = ft.Container(
                content=ft.Column([
                    # 第一行：用户名 + 角色 + 状态
                    ft.Row([
                        ft.Text(name or username, size=15, weight=ft.FontWeight.BOLD, color=self.clr_text, expand=True),
                        role_badge,
                        ft.Container(width=4),
                        status_badge,
                    ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=6),
                    # 第二行：QQ号 + 邮箱
                    ft.Row([
                        ft.Text(f"QQ: {qq or '-'}", size=12, color=self.clr_text2, expand=True),
                        ft.Text(f"ID: {user_id}", size=12, color=self.clr_text2),
                    ], spacing=0),
                    ft.Container(height=2),
                    ft.Text(f"邮箱: {email or '-'}", size=12, color=self.clr_text2),
                    ft.Container(height=2),
                    ft.Text(f"最近登录: {last_login}", size=11, color=self.clr_text2),
                    ft.Container(height=8),
                    # 第三行：操作按钮
                    ft.Row([unban_btn, delete_btn], spacing=4, alignment=ft.MainAxisAlignment.END),
                ], spacing=0),
                bgcolor=self.clr_card, border_radius=12, padding=14,
                opacity=0.7,
                border=ft.border.all(1, ft.colors.RED_200),
            )
            self._blacklist_container.controls.append(user_card)

    def _load_user_list(self):
        """从网站加载用户列表"""
        try:
            operator_id = self.current_user.get("id", "")
            # 获取用户总数
            count_ok, count_result = self._remote_api_request("GET", "users/count",
                body={"operator_id": operator_id}, get_with_body=True)
            total = active = banned = 0
            if count_ok and isinstance(count_result, dict) and count_result.get("ok"):
                data = count_result.get("data", {})
                total = data.get("total", 0)
                active = data.get("active", 0)
                banned = data.get("banned", 0)

            # 获取用户列表
            list_ok, list_result = self._remote_api_request("GET", "users",
                body={"page": 1, "page_size": 100, "status": "all", "operator_id": operator_id},
                get_with_body=True)

            users = []
            if list_ok and isinstance(list_result, dict) and list_result.get("ok"):
                data = list_result.get("data", {})
                users = data.get("users", [])

            # 更新UI
            def update_ui():
                # 更新统计信息
                self._user_stats_text.value = f"共 {total} 个用户 | 正常 {active} | 已封禁 {banned}"
                # 渲染用户列表
                self._render_user_list(users)
                self.page.update()

            self.page.run_thread(update_ui)
        except Exception as e:
            self.page.run_thread(lambda: self._show_toast(f"加载失败: {str(e)[:30]}"))

    def _render_user_list(self, users):
        """渲染用户列表"""
        self._user_list_container.controls.clear()
        if not users:
            self._user_list_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("👥", size=60),
                    ft.Text("暂无用户", size=16, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
            return

        is_super_admin = str(self.current_user.get("role", "")) in ["超级管理员", "超级管理"]
        current_user_id = self.current_user.get("id", "")

        for user in users:
            user_id = user.get("user_id", "")
            username = user.get("username", "")
            name = user.get("name", username)
            email = user.get("email", "")
            qq = user.get("qq", "")
            role = user.get("role", "用户")
            chat_role = user.get("chat_role", role)
            status = user.get("status", "active")
            last_login = user.get("last_login", "-")

            # 判断目标用户是否是管理员（管理员、超级管理员、频道主、运营）
            target_is_admin = chat_role in ["管理员", "admin", "Admin", "超级管理", "超级管理员", "频道主", "频道组", "运营"]
            # 判断是否是当前登录用户自己
            is_self = str(user_id) == str(current_user_id)
            # 普通管理员不能操作其他管理员（只能操作普通用户和自己）
            # 超级管理员可以操作所有人
            can_manage = is_super_admin or (not target_is_admin) or is_self

            # 角色颜色
            role_color = ft.colors.AMBER if chat_role in ["频道主", "频道组"] else (
                ft.colors.PURPLE if chat_role in ["运营", "管理员", "admin", "Admin", "超级管理", "超级管理员"] else (
                ft.colors.BLUE if chat_role == "测试" else ft.colors.GREY))
            role_badge = ft.Container(content=ft.Text(chat_role, size=10, color=ft.colors.WHITE),
                bgcolor=role_color, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.alignment.center)

            # 状态标签
            is_banned = status == "banned"
            status_text = "已封禁" if is_banned else "正常"
            status_color = ft.colors.RED if is_banned else ft.colors.GREEN
            status_badge = ft.Container(content=ft.Text(status_text, size=10, color=ft.colors.WHITE),
                bgcolor=status_color, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.alignment.center)

            # 操作按钮（普通管理员不能操作其他管理员）
            if can_manage:
                ban_btn_text = "解封" if is_banned else "封禁"
                ban_btn_color = ft.colors.GREEN if is_banned else ft.colors.RED
                ban_btn = ft.TextButton(ban_btn_text,
                    style=ft.ButtonStyle(color=ban_btn_color),
                    on_click=lambda e, uid=user_id, uname=username, banned=is_banned:
                        self._toggle_ban_user(uid, uname, banned))

                edit_btn = ft.TextButton("编辑",
                    style=ft.ButtonStyle(color=ft.colors.BLUE),
                    on_click=lambda e, u=user: self._show_edit_user_dialog(u))
            else:
                # 没有权限操作，显示灰色的"无权限"提示
                ban_btn = ft.Container()
                edit_btn = ft.Container(content=ft.Text("无权限", size=11, color=ft.colors.GREY_400),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4))

            delete_btn = ft.Container()
            if is_super_admin and can_manage:
                delete_btn = ft.TextButton("删除",
                    style=ft.ButtonStyle(color=ft.colors.RED),
                    on_click=lambda e, uid=user_id, uname=username:
                        self._delete_user(uid, uname))

            # 用户卡片
            user_card = ft.Container(
                content=ft.Column([
                    # 第一行：用户名 + 角色 + 状态
                    ft.Row([
                        ft.Text(name or username, size=15, weight=ft.FontWeight.BOLD, color=self.clr_text, expand=True),
                        role_badge,
                        ft.Container(width=4),
                        status_badge,
                    ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=6),
                    # 第二行：QQ号 + 邮箱
                    ft.Row([
                        ft.Text(f"QQ: {qq or '-'}", size=12, color=self.clr_text2, expand=True),
                        ft.Text(f"ID: {user_id}", size=12, color=self.clr_text2),
                    ], spacing=0),
                    ft.Container(height=2),
                    ft.Text(f"邮箱: {email or '-'}", size=12, color=self.clr_text2),
                    ft.Container(height=2),
                    ft.Text(f"最近登录: {last_login}", size=11, color=self.clr_text2),
                    ft.Container(height=8),
                    # 第三行：操作按钮
                    ft.Row([edit_btn, ban_btn, delete_btn], spacing=4, alignment=ft.MainAxisAlignment.END),
                ], spacing=0),
                bgcolor=self.clr_card, border_radius=12, padding=14,
                opacity=0.6 if is_banned else 1.0,
            )
            self._user_list_container.controls.append(user_card)

    def _toggle_ban_user(self, user_id, username, is_banned):
        """封禁/解封用户"""
        action = "解封" if is_banned else "封禁"
        def do_action():
            try:
                operator_id = self.current_user.get("id", "")
                path = f"users/{user_id}/unban" if is_banned else f"users/{user_id}/ban"
                ok, result = self._remote_api_request("POST", path,
                    body={"operator_id": operator_id})
                if ok and isinstance(result, dict) and result.get("ok"):
                    self.page.run_thread(lambda: self._show_toast(f"{action}成功"))
                    self.page.run_thread(self._load_user_list)
                else:
                    msg = ""
                    if isinstance(result, dict):
                        msg = result.get("msg", "")
                    self.page.run_thread(lambda: self._show_toast(f"{action}失败: {msg or '未知错误'}"))
            except Exception as e:
                self.page.run_thread(lambda: self._show_toast(f"{action}失败: {str(e)[:30]}"))
        threading.Thread(target=do_action, daemon=True).start()

    def _delete_user(self, user_id, username):
        """删除用户（仅超级管理员）"""
        def confirm_delete():
            def do_delete():
                try:
                    operator_id = self.current_user.get("id", "")
                    ok, result = self._remote_api_request("DELETE", f"users/{user_id}",
                        body={"operator_id": operator_id})
                    if ok and isinstance(result, dict) and result.get("ok"):
                        self.page.run_thread(lambda: self._show_toast("删除成功"))
                        self.page.run_thread(self._load_user_list)
                    else:
                        msg = ""
                        if isinstance(result, dict):
                            msg = result.get("msg", "")
                        self.page.run_thread(lambda: self._show_toast(f"删除失败: {msg or '未知错误'}"))
                except Exception as e:
                    self.page.run_thread(lambda: self._show_toast(f"删除失败: {str(e)[:30]}"))
            threading.Thread(target=do_delete, daemon=True).start()

        # 确认删除对话框
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text(f"确定要删除用户「{username}」吗？\n删除后该用户的所有数据（邮箱、聊天记录等）将被清除，不可恢复！"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("确认删除", style=ft.ButtonStyle(color=ft.colors.RED),
                    on_click=lambda e: [self._close_dialog(), confirm_delete()]),
            ],
        )
        self.page.dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """关闭对话框"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _show_edit_user_dialog(self, user):
        """显示编辑用户信息对话框（权限检查：普通管理员不能编辑其他管理员）"""
        user_id = user.get("user_id", "")
        username = user.get("username", "")
        name = user.get("name", username)
        email = user.get("email", "")
        qq = user.get("qq", "")
        role = user.get("role", "用户")
        chat_role = user.get("chat_role", role)

        # 权限检查
        is_super_admin = str(self.current_user.get("role", "")) in ["超级管理员", "超级管理"]
        current_user_id = self.current_user.get("id", "")
        target_is_admin = chat_role in ["管理员", "admin", "Admin", "超级管理", "超级管理员", "频道主", "频道组", "运营"]
        is_self = str(user_id) == str(current_user_id)
        can_edit = is_super_admin or (not target_is_admin) or is_self

        if not can_edit:
            self._show_toast("无权限编辑管理员信息")
            return

        username_field = ft.TextField(label="用户名", value=username, width=300, border_radius=8)
        name_field = ft.TextField(label="昵称", value=name, width=300, border_radius=8)
        email_field = ft.TextField(label="邮箱", value=email, width=300, border_radius=8)
        qq_field = ft.TextField(label="QQ号", value=qq, width=300, border_radius=8)

        # 角色下拉框：
        # 超级管理员：可以更改所有用户的角色
        # 普通管理员：可以将普通用户更改为管理员（但不能更改其他管理员的角色）
        if is_super_admin:
            role_field = ft.Dropdown(
                label="角色",
                value=role,
                options=[
                    ft.dropdown.Option("用户"),
                    ft.dropdown.Option("管理员"),
                ],
                width=300, border_radius=8,
            )
        else:
            # 普通管理员编辑普通用户时，可以将用户更改为管理员
            # （普通管理员不能编辑其他管理员，所以能到这里的都是普通用户）
            role_field = ft.Dropdown(
                label="角色（可提升为管理员）",
                value=role,
                options=[
                    ft.dropdown.Option("用户"),
                    ft.dropdown.Option("管理员"),
                ],
                width=300, border_radius=8,
            )

        # 有效期权限设置（管理员可以给普通用户开通2小时和永久有效期权限）
        can_use_2h = user.get("can_use_2h", False)
        can_use_permanent = user.get("can_use_permanent", False)
        # 兼容字符串类型的布尔值
        if isinstance(can_use_2h, str):
            can_use_2h = can_use_2h.lower() in ["true", "1", "yes"]
        if isinstance(can_use_permanent, str):
            can_use_permanent = can_use_permanent.lower() in ["true", "1", "yes"]

        duration_perm_label = ft.Container(
            content=ft.Text("临时邮箱有效期权限", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            padding=ft.padding.only(0, 8, 0, 4),
        )

        can_2h_switch = ft.Switch(
            label="2小时有效期",
            value=bool(can_use_2h),
            active_color=THEME_COLOR,
        )
        can_permanent_switch = ft.Switch(
            label="永久有效期",
            value=bool(can_use_permanent),
            active_color=THEME_COLOR,
        )

        duration_perm_container = ft.Container(
            content=ft.Column([
                duration_perm_label,
                can_2h_switch,
                can_permanent_switch,
            ], spacing=4, tight=True),
            padding=ft.padding.only(0, 4, 0, 4),
        )

        def do_save(e):
            self._close_dialog()
            self._show_toast("正在保存...")
            def save_thread():
                try:
                    operator_id = self.current_user.get("id", "")
                    body = {
                        "username": username_field.value,
                        "name": name_field.value,
                        "email": email_field.value,
                        "qq": qq_field.value,
                        "operator_id": operator_id,
                        # 有效期权限
                        "can_use_2h": can_2h_switch.value,
                        "can_use_permanent": can_permanent_switch.value,
                    }
                    # 超级管理员和普通管理员都可以更改角色
                    # （普通管理员只能在编辑普通用户时更改角色，不能编辑其他管理员）
                    if isinstance(role_field, ft.Dropdown):
                        body["role"] = role_field.value
                    ok, result = self._remote_api_request("PUT", f"users/{user_id}", body=body)
                    if ok and isinstance(result, dict) and result.get("ok"):
                        self.page.run_thread(lambda: self._show_toast("保存成功"))
                        self.page.run_thread(self._load_user_list)
                    else:
                        msg = ""
                        if isinstance(result, dict):
                            msg = result.get("msg", "")
                        self.page.run_thread(lambda: self._show_toast(f"保存失败: {msg or '未知错误'}"))
                except Exception as e:
                    self.page.run_thread(lambda: self._show_toast(f"保存失败: {str(e)[:30]}"))
            threading.Thread(target=save_thread, daemon=True).start()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"编辑用户 - {name or username}"),
            content=ft.Column([
                username_field, name_field, email_field, qq_field, role_field,
                duration_perm_container
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("保存", on_click=do_save),
            ],
        )
        self.page.dialog.open = True
        self.page.update()

    def _render_channels(self, channels):
        """渲染频道列表"""
        self._channel_list.controls.clear()
        if not channels:
            self._channel_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("📺", size=60),
                    ft.Text("暂无频道", size=16, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
        else:
            for ch in channels:
                # 获取未读消息数量（从本地缓存计算，或者默认0）
                unread_count = getattr(self, '_channel_unread_count', 0)
                # 未读消息红圈（有未读消息时显示）
                unread_badge = ft.Container()
                if unread_count > 0:
                    unread_badge = ft.Container(
                        content=ft.Text(str(unread_count), size=12, color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED, border_radius=12,
                        width=24, height=24, alignment=ft.alignment.center,
                    )
                self._channel_list.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Text(ch.get("icon", "📺"), size=22),
                            width=48, height=48,
                            bgcolor=ft.colors.with_opacity(0.12, THEME_COLOR),
                            border_radius=RADIUS_PILL, alignment=ft.alignment.center),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(ch.get("name", ""), size=FONT_MD, weight=FONT_SEMIBOLD, color=self.clr_text),
                            ft.Text(ch.get("desc", ""), size=FONT_SM, color=self.clr_text2),
                        ], spacing=2, expand=True),
                        unread_badge,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=RADIUS_MD, padding=SPACE_MD,
                    margin=ft.margin.only(0, 4, 0, 4),
                    shadow=ft.BoxShadow(
                        spread_radius=0, blur_radius=8,
                        color=ft.colors.with_opacity(0.05, ft.colors.BLACK),
                        offset=ft.Offset(0, 2),
                    ),
                    on_click=lambda e, channel=ch: self.show_channel_chat(channel),
                ))
        self.page.update()

    def show_channel_chat(self, channel):
        """频道聊天页面"""
        self.current_channel = channel
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None  # 关闭整体滚动，确保布局稳定
        # 成员数量文本（后续从网站API获取实际数量后更新）
        self._channel_members_text = ft.Text("加载中... 成员", size=12, color=self.clr_text2)
        # 底部输入框（现代风格：胶囊形状+填充背景）
        self._chat_input = ft.TextField(
            hint_text="输入消息...", expand=True,
            hint_style=ft.TextStyle(color=self.clr_text2, size=FONT_MD),
            text_style=ft.TextStyle(color=self.clr_text, size=FONT_MD),
            border_radius=RADIUS_PILL, bgcolor=self.clr_card,
            border_color=self.clr_border, border_width=1,
            focused_border_color=THEME_COLOR, focused_border_width=1.5,
            height=44,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=10),
            suffix_text="0/500",
            suffix_style=ft.TextStyle(color=self.clr_text2, size=11),
            cursor_color=THEME_COLOR,
            on_change=self._on_chat_input_change,
        )
        send_btn = ft.Container(
            content=ft.Icon(ft.icons.SEND, size=20, color=ft.colors.WHITE),
            width=44, height=44,
            bgcolor=THEME_COLOR,
            border_radius=RADIUS_PILL,
            alignment=ft.alignment.center,
            on_click=lambda e: self.send_channel_message(),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8,
                color=ft.colors.with_opacity(0.3, THEME_COLOR),
                offset=ft.Offset(0, 2),
            ),
        )
        # 消息列表（可滑动，初始显示加载提示）
        self._chat_message_list = ft.ListView([
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=30, height=30, color=THEME_COLOR, stroke_width=3),
                    ft.Container(height=12),
                    ft.Text("加载消息中...", size=14, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 80, 0, 0),
            )
        ], spacing=8, expand=True, padding=16, auto_scroll=True)
        # 使用Column布局，确保顶部栏、消息列表、输入框位置稳定
        self.content.controls.append(ft.Column([
            # 顶部固定栏
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, on_click=lambda e: self.render_channel_page()),
                    ft.Column([
                        ft.Text(channel.get("name", ""), size=18, weight=ft.FontWeight.BOLD, color=self.clr_text),
                        self._channel_members_text,
                    ], expand=True, spacing=2),
                    ft.IconButton(ft.icons.REFRESH, icon_size=22, on_click=lambda e: self.refresh_channel_messages()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(10, 45, 10, 5),
                bgcolor=self.clr_bg,
            ),
            ft.Container(height=1, bgcolor=self.clr_border),
            # 消息列表（占据中间剩余空间）
            self._chat_message_list,
            # 底部分割线
            ft.Container(height=1, bgcolor=self.clr_border),
            # 底部输入框（固定在底部）
            ft.Container(
                content=ft.Row([self._chat_input, send_btn], spacing=8),
                padding=ft.padding.only(12, 8, 12, 12),
                bgcolor=self.clr_bg,
            ),
        ], spacing=0, expand=True))
        self.page.update()
        # 从网站API获取实际的注册数量（成员数量）
        def load_members_count():
            try:
                # 调用 register-count 接口获取注册数量
                ok, result = self._remote_api_request("GET", "register-count")
                user_count = 0
                if ok and isinstance(result, dict) and result.get("ok"):
                    data = result.get("data", {})
                    if isinstance(data, dict):
                        user_count = data.get("register_count", 0)
                # 更新成员数量显示
                def update_text():
                    if hasattr(self, '_channel_members_text') and self._channel_members_text:
                        self._channel_members_text.value = f"{user_count} 成员"
                        self.page.update()
                self.page.run_thread(update_text)
            except Exception as e:
                pass
        threading.Thread(target=load_members_count, daemon=True).start()
        # 加载消息列表（带缓存，避免频繁切换时重复加载）
        current_time = time.time()
        last_load = getattr(self, '_last_channel_msg_load_time', 0)
        if current_time - last_load > 5:  # 5秒内不重复加载
            self._last_channel_msg_load_time = current_time
            self._load_channel_messages()
        elif hasattr(self, '_cached_channel_messages'):
            # 使用缓存的消息
            self._render_chat_messages(self._cached_channel_messages)

    def _fetch_all_user_roles(self, messages):
        """从网站实时获取所有用户的最新角色（不缓存，每次都实时获取）"""
        user_roles = {}
        try:
            # 提取所有不重复的用户ID
            user_ids = set()
            for msg in messages:
                uid = str(msg.get("user_id", ""))
                if uid and uid != "0":
                    user_ids.add(uid)
            if not user_ids:
                return user_roles
            # 逐个获取用户角色（实时从网站获取，不缓存）
            for uid in user_ids:
                try:
                    ok, result = self._remote_api_request("GET", "user-role", params={"user_id": uid})
                    if ok and isinstance(result, dict) and result.get("ok"):
                        data = result.get("data", {})
                        if isinstance(data, dict):
                            # 优先使用 chat_role（聊天频道显示角色），如果没有则使用 role
                            role = data.get("chat_role", data.get("role", ""))
                            if role:
                                user_roles[uid] = role
                except Exception as e:
                    pass
        except Exception as e:
            pass
        return user_roles

    def _load_channel_messages(self):
        """加载频道消息列表"""
        def load_thread():
            try:
                cloud_messages = self._load_channel_messages_from_cloud()
                if cloud_messages:
                    # 转换为应用内消息格式
                    current_user = self.current_user or {}
                    current_user_id = current_user.get("id", "")
                    # 获取所有用户的最新角色（实时从网站获取）
                    user_roles = self._fetch_all_user_roles(cloud_messages)
                    formatted_messages = []
                    # 添加系统欢迎消息
                    formatted_messages.append({
                        "id": "0",
                        "user": "系统",
                        "content": "欢迎来到 " + self.current_channel.get("name", "") + " 频道！",
                        "time": "",
                        "is_system": True,
                    })
                    for msg in cloud_messages:
                        user_id = msg.get("user_id", "")
                        username = msg.get("name", msg.get("username", "匿名"))
                        # 优先使用从网站实时获取的最新角色，如果没有则使用消息中的角色
                        role = user_roles.get(str(user_id), msg.get("role", ""))
                        is_me = str(user_id) == str(current_user_id)
                        # 如果是当前用户自己的消息，同步角色到本地（实时获取后台角色）
                        if is_me and role and str(role) != str(self.current_user.get("role", "")):
                            self.current_user["role"] = str(role)
                            self.data["current_user"] = self.current_user
                            save_data(self.data)
                        created_at = msg.get("created_at", "")
                        # 提取时间
                        time_str = ""
                        if created_at:
                            try:
                                time_str = created_at.split(" ")[1][:5] if " " in created_at else created_at[11:16]
                            except:
                                time_str = ""
                        # 角色颜色：频道主金色，用户红色，运营紫色，测试蓝色，管理员/超级管理紫色
                        role_color = ft.colors.RED  # 默认用户红色
                        if role == "频道主" or role == "频道组":
                            role_color = ft.colors.AMBER  # 频道主金色
                        elif role == "运营":
                            role_color = ft.colors.PURPLE  # 运营紫色
                        elif role in ["管理员", "admin", "Admin", "超级管理", "超级管理员"]:
                            role_color = ft.colors.PURPLE  # 管理员/超级管理紫色
                        elif role == "测试":
                            role_color = ft.colors.BLUE  # 测试蓝色
                        formatted_messages.append({
                            "id": str(msg.get("id", "")),
                            "user": username,
                            "role": role,
                            "role_color": role_color,
                            "content": msg.get("content", ""),
                            "time": time_str,
                            "is_me": is_me,
                            "is_system": False,
                        })
                    # 缓存消息
                    self._cached_channel_messages = formatted_messages
                    self.page.run_thread(lambda: self._render_chat_messages(formatted_messages))
                else:
                    # 没有消息，显示空状态
                    self._cached_channel_messages = []
                    self.page.run_thread(lambda: self._render_chat_messages([]))
            except Exception as e:
                # 加载失败，显示空状态
                self._cached_channel_messages = []
                self.page.run_thread(lambda: self._render_chat_messages([]))
        threading.Thread(target=load_thread, daemon=True).start()

    def refresh_channel_messages(self):
        """刷新频道消息"""
        self._load_channel_messages()

    def _render_chat_messages(self, messages):
        """渲染聊天消息"""
        self._chat_message_list.controls.clear()
        if not messages:
            self._chat_message_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("💬", size=60),
                    ft.Text("暂无消息，发个消息吧", size=14, color=ft.colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0, 60, 0, 0),
            ))
        else:
            for msg in messages:
                if msg.get("is_system"):
                    # 系统消息居中
                    self._chat_message_list.controls.append(ft.Container(
                        content=ft.Text(msg.get("content", ""), size=12, color=ft.colors.GREY_500, text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(vertical=8),
                    ))
                elif msg.get("is_me"):
                    # 我的消息靠右（名字和角色在气泡外面）
                    username = msg.get("user", "")
                    role = msg.get("role", "")
                    role_color = msg.get("role_color", ft.colors.RED)
                    # 名字和角色行（在气泡外面）
                    name_row = ft.Row([
                        ft.Container(width=40),
                        ft.Text(username, size=11, color=self.clr_text2),
                        ft.Container(width=4),
                        ft.Container(content=ft.Text(role, size=9, color=ft.colors.WHITE),
                            bgcolor=role_color, border_radius=4, padding=ft.padding.symmetric(1, 4),
                            alignment=ft.alignment.center) if role else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.END, spacing=0)
                    # 气泡（根据文字内容自适应大小，短消息气泡短，长消息自动换行，长按可复制）
                    msg_content = msg.get("content", "")
                    # 根据文字长度动态设置气泡最大宽度，短消息不设固定宽度
                    if len(msg_content) > 20:
                        # 长消息设置最大宽度让文字换行
                        text_widget = ft.Text(msg_content, size=14, color=ft.colors.WHITE, width=240)
                    else:
                        # 短消息不设固定宽度，气泡根据内容自适应
                        text_widget = ft.Text(msg_content, size=14, color=ft.colors.WHITE)
                    bubble = ft.Container(
                        content=text_widget,
                        bgcolor=THEME_COLOR, border_radius=12, padding=12,
                        on_long_press=lambda e, content=msg_content: self._copy_chat_message(content),
                    )
                    self._chat_message_list.controls.append(ft.Container(
                        content=ft.Column([
                            name_row,
                            ft.Container(height=4),
                            ft.Row([ft.Container(width=40), bubble], alignment=ft.MainAxisAlignment.END, spacing=0),
                            ft.Container(height=2),
                            ft.Text(msg.get("time", ""), size=10, color=self.clr_text2, text_align=ft.TextAlign.RIGHT),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                        alignment=ft.alignment.center_right,
                    ))
                else:
                    # 别人的消息靠左（名字和角色在气泡外面）
                    username = msg.get("user", "")
                    role = msg.get("role", "")
                    role_color = msg.get("role_color", ft.colors.RED)
                    # 名字和角色行（在气泡外面）
                    name_row = ft.Row([
                        ft.Text(username, size=11, color=self.clr_text2),
                        ft.Container(width=4),
                        ft.Container(content=ft.Text(role, size=9, color=ft.colors.WHITE),
                            bgcolor=role_color, border_radius=4, padding=ft.padding.symmetric(1, 4),
                            alignment=ft.alignment.center) if role else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.START, spacing=0)
                    # 气泡（根据文字内容自适应大小，短消息气泡短，长消息自动换行，长按可复制）
                    msg_content = msg.get("content", "")
                    # 根据文字长度动态设置气泡最大宽度，短消息不设固定宽度
                    if len(msg_content) > 20:
                        # 长消息设置最大宽度让文字换行
                        text_widget = ft.Text(msg_content, size=14, color=self.clr_text, width=240)
                    else:
                        # 短消息不设固定宽度，气泡根据内容自适应
                        text_widget = ft.Text(msg_content, size=14, color=self.clr_text)
                    bubble = ft.Container(
                        content=text_widget,
                        bgcolor=self.clr_card, border_radius=12, padding=12,
                        on_long_press=lambda e, content=msg_content: self._copy_chat_message(content),
                    )
                    self._chat_message_list.controls.append(ft.Container(
                        content=ft.Column([
                            name_row,
                            ft.Container(height=4),
                            ft.Row([bubble, ft.Container(width=40)], alignment=ft.MainAxisAlignment.START, spacing=0),
                            ft.Container(height=2),
                            ft.Text(msg.get("time", ""), size=10, color=self.clr_text2),
                        ], spacing=0),
                        alignment=ft.alignment.center_left,
                    ))
        self.page.update()

    def _copy_chat_message(self, content):
        """复制聊天消息内容"""
        self.page.set_clipboard(content)
        self.page.snack_bar = ft.SnackBar(ft.Text("已复制消息内容"))
        self.page.snack_bar.open = True
        self.page.update()

    def _on_chat_input_change(self, e):
        """输入框字数变化时更新内部计数器，超过500字自动截断"""
        try:
            val = e.control.value or ""
            if len(val) > 500:
                e.control.value = val[:500]
            count = len(e.control.value or "")
            e.control.suffix_text = f"{count}/500"
        except:
            pass

    def send_channel_message(self):
        """发送频道消息"""
        content = self._chat_input.value.strip() if self._chat_input.value else ""
        if not content:
            return
        if len(content) > 500:
            self._show_toast("消息不能超过500字")
            return
        if not self.current_user:
            self.page.snack_bar = ft.SnackBar(ft.Text("请先登录"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        # 清空输入框
        self._chat_input.value = ""
        self._chat_input.suffix_text = "0/500"
        self.page.update()
        # 发送消息到云端
        def send_thread():
            try:
                ok = self._send_channel_message_to_cloud(content)
                if ok:
                    # 发送成功，重新加载消息
                    time.sleep(0.5)
                    self._load_channel_messages()
                else:
                    self.page.run_thread(lambda: self._show_chat_error("发送失败，请重试"))
            except Exception as e:
                self.page.run_thread(lambda: self._show_chat_error("发送失败：" + str(e)[:50]))
        threading.Thread(target=send_thread, daemon=True).start()

    def _show_chat_error(self, err):
        """显示聊天错误"""
        try:
            self.page.snack_bar = ft.SnackBar(ft.Text(err))
            self.page.snack_bar.open = True
            self.page.update()
        except:
            pass

    # ========== 我的页面 ==========
    def _refresh_current_user_role(self):
        """从网站实时获取当前用户的最新角色并更新本地缓存"""
        try:
            if not self.current_user:
                return
            user_id = str(self.current_user.get("id", ""))
            if not user_id:
                return
            # 调用 user-role 接口获取最新角色（每次都获取，确保实时）
            ok, result = self._remote_api_request("GET", "user-role", params={"user_id": user_id})
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                if isinstance(data, dict):
                    changed = False
                    # 优先使用 chat_role（聊天频道显示角色），如果没有则使用 role
                    new_role = data.get("chat_role", data.get("role", ""))
                    old_role = self.current_user.get("role", "")
                    if new_role and str(new_role) != str(old_role):
                        self.current_user["role"] = str(new_role)
                        changed = True
                    # 同步更新用户名和邮箱
                    new_name = data.get("name", data.get("username", ""))
                    old_name = self.current_user.get("name", "")
                    if new_name and str(new_name) != str(old_name):
                        self.current_user["name"] = str(new_name)
                        changed = True
                    new_email = data.get("email", "")
                    old_email = self.current_user.get("email", "")
                    if new_email and str(new_email) != str(old_email):
                        self.current_user["email"] = str(new_email)
                        changed = True
                    if changed:
                        self.data["current_user"] = self.current_user
                        save_data(self.data)
                        # 重新渲染个人主页
                        self.page.run_thread(self.render_me_page)
        except Exception as e:
            pass

    def render_me_page(self):
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None  # 关闭整体滚动，标题固定

        # 角色已经在加载页从网站实时获取，这里直接使用内存中的 current_user

        # ---- 顶部固定标题（带设置齿轮） ----
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("我的", size=28, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
                ft.IconButton(ft.icons.SETTINGS_OUTLINED, icon_size=24,
                    icon_color=self.clr_text2, on_click=lambda e: self.render_settings_page()),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 50, 12, 10),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # ---- 可滚动内容区域 ----
        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # ---- 用户信息卡片（彩色头部） ----
        if self.current_user:
            qq = self.current_user.get("qq", "")
            email = self.current_user.get("email", "")
            username = self.current_user.get("username", "")
            name = self.current_user.get("name", username)
            role = self.current_user.get("role", "")
            user_id = str(self.current_user.get("id", ""))
            avatar_text = (name[0] if name else (qq[0] if qq else "U")).upper()

            # 构建头像：有QQ号则显示QQ头像，否则用文字首字母兜底
            qq_clean = qq.strip() if qq else ""
            if qq_clean:
                avatar_widget = ft.Container(
                    content=ft.Image(
                        src=f"https://q1.qlogo.cn/g?b=qq&nk={qq_clean}&s=100",
                        width=64, height=64, fit=ft.ImageFit.COVER,
                        border_radius=32,
                        error_content=ft.Container(
                            content=ft.Text(avatar_text, size=28, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                            width=64, height=64, bgcolor=ft.colors.WHITE,
                            alignment=ft.alignment.center,
                        ),
                    ),
                    width=64, height=64, border_radius=32,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                )
            else:
                avatar_widget = ft.Container(
                    content=ft.Text(avatar_text, size=28, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    width=64, height=64, bgcolor=ft.colors.WHITE,
                    border_radius=32, alignment=ft.alignment.center,
                )

            # 角色标签（从网站获取，为空则默认"用户"）
            display_role = role if role else "用户"
            role_color = ft.colors.AMBER if display_role in ["频道主", "频道组"] else (
                ft.colors.PURPLE if display_role in ["运营", "管理员", "admin", "Admin", "超级管理", "超级管理员"] else (
                ft.colors.BLUE if display_role == "测试" else ft.colors.RED))
            role_widget = ft.Container(content=ft.Text(display_role, size=10, color=ft.colors.WHITE),
                bgcolor=role_color, border_radius=4,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.alignment.center)

            # 用户ID行（格式化显示：原始ID=1显示为930001）
            display_id = self.format_user_id(user_id)
            id_row = ft.Row([
                ft.Icon(ft.icons.FINGERPRINT, size=12, color=ft.colors.WHITE70),
                ft.Container(width=4),
                ft.Text("ID: " + display_id, size=11, color=ft.colors.WHITE70),
                ft.Container(width=6),
                ft.Container(
                    content=ft.Text("复制", size=10, color=ft.colors.WHITE, weight=ft.FontWeight.W_500),
                    on_click=lambda e: self._copy_text(display_id, "用户ID已复制"),
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    bgcolor=ft.colors.WHITE24,
                    border_radius=6,
                ),
            ], spacing=0)

            scroll_content.controls.append(ft.Container(
                content=ft.Row([
                    avatar_widget,
                    ft.Container(width=14),
                    ft.Column([
                        ft.Row([
                            ft.Text(name or username or qq or "用户", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                            ft.Container(width=8),
                            role_widget,
                        ], spacing=0),
                        ft.Container(height=4),
                        ft.Text("QQ: " + qq if qq else (email or "未绑定邮箱"), size=12, color=ft.colors.WHITE70),
                        ft.Container(height=2),
                        id_row,
                    ], spacing=0, expand=True),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, size=20, color=ft.colors.WHITE70),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=THEME_COLOR, border_radius=16, padding=18,
                margin=ft.margin.only(16, 4, 16, 6),
                on_click=self.show_user_profile,
            ))
        else:
            # 未登录状态
            scroll_content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.PERSON_OUTLINE, size=32, color=ft.colors.GREY_400),
                        width=64, height=64, bgcolor=ft.colors.WHITE,
                        border_radius=32, alignment=ft.alignment.center),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text("未登录", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Container(height=4),
                        ft.Text("登录后可同步邮箱数据", size=12, color=ft.colors.WHITE70),
                    ], spacing=0, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=THEME_COLOR, border_radius=16, padding=18,
                margin=ft.margin.only(16, 4, 16, 6),
            ))

        # ---- 统计卡片（2列） ----
        email_count = len(getattr(self, '_cloud_emails_cache', []))
        msg_total = self._get_total_message_count()
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Column([
                    ft.Text(str(email_count), size=26, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Container(height=2),
                    ft.Text("邮箱数量", size=12, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, alignment=ft.alignment.center, padding=14),
                ft.Container(width=1, bgcolor=self.clr_border, height=50),
                ft.Container(content=ft.Column([
                    ft.Text(str(msg_total), size=26, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE),
                    ft.Container(height=2),
                    ft.Text("收到邮件", size=12, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, alignment=ft.alignment.center, padding=14),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14,
            margin=ft.margin.only(16, 6, 16, 6),
        ))

        # ---- 外观（主题切换） ----
        scroll_content.controls.append(ft.Container(
            content=ft.Text("外观", size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 14, 20, 6),
        ))
        current_mode = self.settings.get("theme_mode", "system")
        theme_options = [
            {"key": "light", "label": "白天", "icon": ft.icons.WB_SUNNY_OUTLINED},
            {"key": "dark", "label": "夜间", "icon": ft.icons.NIGHTLIGHT_OUTLINED},
            {"key": "system", "label": "跟随系统", "icon": ft.icons.BRIGHTNESS_AUTO_OUTLINED},
        ]
        theme_buttons = []
        for opt in theme_options:
            selected = current_mode == opt["key"]
            theme_buttons.append(ft.Container(
                content=ft.Column([
                    ft.Icon(opt["icon"], size=22,
                        color=THEME_COLOR if selected else ft.colors.GREY_500),
                    ft.Container(height=4),
                    ft.Text(opt["label"], size=12,
                        color=THEME_COLOR if selected else ft.colors.GREY_600,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.NORMAL),
                ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True, alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=14),
                bgcolor=ft.colors.BLUE_50 if selected else ft.colors.TRANSPARENT,
                border_radius=12,
                on_click=lambda e, m=opt["key"]: self._set_theme_mode(m),
            ))
        scroll_content.controls.append(ft.Container(
            content=ft.Row(theme_buttons, spacing=8),
            bgcolor=self.clr_card, border_radius=14, padding=8,
            margin=ft.margin.only(16, 2, 16, 6),
        ))

        # 未登录时显示登录入口
        if not self.current_user:
            scroll_content.controls.append(ft.Container(height=10))
            scroll_content.controls.append(ft.Container(
                content=ft.ElevatedButton("登录 / 注册", expand=True, height=48,
                    style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
                    on_click=lambda e: self.show_fullscreen_login()),
                padding=ft.padding.symmetric(horizontal=16),
            ))

        scroll_content.controls.append(ft.Container(height=20))
        # 把可滚动内容区域添加到页面中
        self.content.controls.append(scroll_content)
        self.page.update()

        # 角色已经在加载页从 user-role 接口获取了最新角色，不需要再从消息中同步旧角色
        # （去掉了 _sync_role_from_chat 调用，避免用消息中的旧角色覆盖最新角色）

    # ========== 设置页面 ==========
    def render_settings_page(self):
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None  # 关闭整体滚动，标题固定

        # ---- 顶部固定栏 ----
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_me_page()),
                ft.Text("设置", size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # ---- 可滚动内容区域 ----
        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # ---- 通用设置 ----
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=THEME_COLOR, border_radius=2),
                ft.Container(width=6),
                ft.Text("通用", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 12, 20, 6),
        ))

        # 收件箱自动刷新开关
        auto_refresh = self.settings.get("inbox_auto_refresh", True)
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.REFRESH, size=18, color=ft.colors.BLUE),
                    width=32, height=32, bgcolor=ft.colors.BLUE_50,
                    border_radius=8, alignment=ft.alignment.center),
                ft.Container(width=10),
                ft.Text("收件箱自动刷新", size=15, expand=True, color=self.clr_text),
                ft.Switch(value=auto_refresh, active_color=THEME_COLOR,
                    on_change=lambda e: self._toggle_auto_refresh(e.control.value)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=12, padding=ft.padding.only(14, 4, 14, 4),
            margin=ft.margin.only(16, 2, 16, 2),
        ))

        # 刷新间隔
        interval = self.settings.get("refresh_interval", 10)
        scroll_content.controls.append(self._build_option_row(
            icon=ft.icons.TIMER, icon_color=ft.colors.ORANGE,
            label="刷新间隔",
            options=[{"label": "5秒", "value": 5}, {"label": "10秒", "value": 10}, {"label": "30秒", "value": 30}],
            current_value=interval,
            on_select=lambda v: self._set_refresh_interval(v),
        ))

        # 默认邮箱有效期
        default_dur = self.settings.get("default_duration_hours", 1)
        scroll_content.controls.append(self._build_option_row(
            icon=ft.icons.SCHEDULE, icon_color=ft.colors.PURPLE,
            label="默认有效期",
            options=[{"label": "1小时", "value": 1}, {"label": "2小时", "value": 2}, {"label": "永久", "value": -1}],
            current_value=default_dur,
            on_select=lambda v: self._set_default_duration(v),
        ))

        # 有效期权限状态显示
        self._permission_status_text = ft.Text("正在获取权限状态...", size=12, color=ft.colors.GREY_500)
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.VERIFIED_USER, size=14, color=ft.colors.GREEN),
                    width=24, height=24, alignment=ft.alignment.center),
                self._permission_status_text,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=12, padding=ft.padding.symmetric(horizontal=14, vertical=10),
            margin=ft.margin.only(16, 0, 16, 2),
        ))
        # 进入设置页面时就获取权限状态
        threading.Thread(target=self._fetch_and_display_permission_status, daemon=True).start()

        # 应用图标（支持图片图标和远程图标）
        app_icon_widget = self._build_app_icon_widget(size=24)
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.IMAGE, size=18, color=ft.colors.TEAL),
                    width=32, height=32, bgcolor=ft.colors.TEAL_50,
                    border_radius=8, alignment=ft.alignment.center),
                ft.Container(width=10),
                ft.Text("应用图标", size=15, expand=True, color=self.clr_text),
                app_icon_widget,
                ft.Icon(ft.icons.CHEVRON_RIGHT, size=18, color=self.clr_text2),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=12, padding=14,
            margin=ft.margin.only(16, 2, 16, 2),
            on_click=lambda e: self._show_app_icon_selector(),
        ))

        # ---- 数据与缓存 ----
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.GREEN, border_radius=2),
                ft.Container(width=6),
                ft.Text("数据", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 14, 20, 6),
        ))
        scroll_content.controls.append(self._build_menu_item(
            icon=ft.icons.CLEANING_SERVICES, icon_color=ft.colors.GREEN,
            label="清理缓存", on_click=self._clear_cache,
        ))

        # ---- 关于 ----
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.BLUE, border_radius=2),
                ft.Container(width=6),
                ft.Text("关于", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 14, 20, 6),
        ))
        scroll_content.controls.append(self._build_menu_item(
            icon=ft.icons.UPDATE, icon_color=ft.colors.BLUE,
            label="检查更新", on_click=self._check_update,
        ))
        scroll_content.controls.append(self._build_menu_item(
            icon=ft.icons.GROUP, icon_color=ft.colors.PURPLE,
            label="加入QQ群", on_click=self._join_qq_group,
        ))
        scroll_content.controls.append(self._build_menu_item(
            icon=ft.icons.INFO_OUTLINE, icon_color=ft.colors.GREY_600,
            label="关于应用", on_click=self._show_about_dialog,
        ))

        # ---- 账户（修改密码、退出登录） ----
        if self.current_user:
            scroll_content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(width=3, height=12, bgcolor=ft.colors.ORANGE, border_radius=2),
                    ft.Container(width=6),
                    ft.Text("账户", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(20, 14, 20, 6),
            ))
            # 修改密码
            scroll_content.controls.append(self._build_menu_item(
                icon=ft.icons.LOCK, icon_color=ft.colors.BLUE,
                label="修改密码", on_click=self._show_change_password_dialog,
            ))
            # 退出登录
            scroll_content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.LOGOUT, size=18, color=ft.colors.RED),
                        width=32, height=32, bgcolor=ft.colors.RED_50,
                        border_radius=8, alignment=ft.alignment.center),
                    ft.Container(width=10),
                    ft.Text("退出登录", size=15, color=ft.colors.RED, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.clr_card, border_radius=12, padding=14,
                margin=ft.margin.only(16, 2, 16, 2),
                on_click=self.logout,
            ))

        # 底部版本信息
        _app_ver = APP_CONFIG.get("app_version", "1.0.0")
        scroll_content.controls.append(ft.Container(height=16))
        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Text(f"YoXi邮箱 v{_app_ver}", size=12, color=self.clr_text2,
                    text_align=ft.TextAlign.CENTER),
                ft.Container(height=2),
                ft.Text("临时邮箱，触手可及", size=11,
                    color=ft.colors.with_opacity(0.5, self.clr_text2),
                    text_align=ft.TextAlign.CENTER),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=10),
        ))
        scroll_content.controls.append(ft.Container(height=20))
        self.content.controls.append(scroll_content)
        self.page.update()

    def _show_app_icon_selector(self):
        """显示应用图标选择弹窗"""
        # 本地图标路径
        local_icon_path = os.path.join(_base_dir, "assets", "cute_email_icon.png")
        qq_icon_path = os.path.join(_base_dir, "assets", "qq_email_icon.png")
        netease_icon_path = os.path.join(_base_dir, "assets", "netease_email_icon.png")
        gmail_icon_path = os.path.join(_base_dir, "assets", "gmail_icon.png")
        custom_icon_1 = os.path.join(_base_dir, "assets", "custom_icon_1.png")
        custom_icon_2 = os.path.join(_base_dir, "assets", "custom_icon_2.png")
        custom_icon_3 = os.path.join(_base_dir, "assets", "custom_icon_3.png")
        custom_icon_4 = os.path.join(_base_dir, "assets", "custom_icon_4.png")
        custom_icon_5 = os.path.join(_base_dir, "assets", "custom_icon_5.png")
        custom_icon_6 = os.path.join(_base_dir, "assets", "custom_icon_6.png")
        # 第一个：默认图标，然后是QQ邮箱、网易邮箱、谷歌邮箱、移动邮箱、未知邮箱、自定义图标
        app_icons = [
            {"name": "默认图标", "type": "image", "image_path": local_icon_path},
            {"name": "QQ邮箱", "type": "image", "image_path": qq_icon_path},
            {"name": "网易邮箱", "type": "image", "image_path": custom_icon_2},
            {"name": "谷歌邮箱", "type": "image", "image_path": custom_icon_3},
            {"name": "移动邮箱", "type": "image", "image_path": custom_icon_4},
            {"name": "未知邮箱", "type": "image", "image_path": custom_icon_5},
            {"name": "未知邮箱", "type": "image", "image_path": custom_icon_6},
            {"name": "自定义", "type": "custom"},
        ]

        current_icon = self.settings.get("app_icon", local_icon_path)
        current_icon_type = self.settings.get("app_icon_type", "image")

        # 用三行Row布局（每行3个，3行3列）
        row1 = ft.Row([], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        row2 = ft.Row([], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        row3 = ft.Row([], spacing=12, alignment=ft.MainAxisAlignment.CENTER)

        for i, icon_info in enumerate(app_icons):
            icon_type = icon_info.get("type", "image")
            # 判断是否选中
            if icon_type == "image":
                is_selected = current_icon_type == "image" and current_icon == icon_info.get("image_path", "")
            elif icon_type == "custom":
                is_selected = current_icon_type == "custom"
            else:
                is_selected = False
            # 正方形56x56，圆角16
            if icon_type == "image":
                # 图片图标（全部默认图标）
                icon_content = ft.Container(
                    content=ft.Image(src=icon_info["image_path"], width=44, height=44, fit=ft.ImageFit.CONTAIN),
                    width=56, height=56,
                    bgcolor=ft.colors.WHITE if is_selected else ft.colors.GREY_100,
                    border_radius=16,
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, THEME_COLOR) if is_selected else None,
                )
            elif icon_type == "custom":
                # 自定义图标（加号）
                icon_content = ft.Container(
                    content=ft.Text("+", size=36, color=ft.colors.GREY_400),
                    width=56, height=56,
                    bgcolor=ft.colors.GREY_100,
                    border_radius=16,
                    alignment=ft.alignment.center,
                    border=ft.border.all(2, ft.colors.GREY_300),
                )
            else:
                icon_content = ft.Container(width=56, height=56)
            icon_item = ft.Container(
                content=ft.Column([
                    icon_content,
                    ft.Container(height=4),
                    ft.Text(icon_info["name"], size=10, color=self.clr_text2,
                        text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                width=68, height=84,
                alignment=ft.alignment.center,
                on_click=lambda e, ic=icon_info: self._select_app_icon(ic),
            )
            if i < 3:
                row1.controls.append(icon_item)
            elif i < 6:
                row2.controls.append(icon_item)
            else:
                row3.controls.append(icon_item)

        icon_col = ft.Column([row1, row2, row3], spacing=12, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # 当前图标显示（支持图片和自定义图标）
        if current_icon_type in ("image", "custom"):
            current_icon_widget = ft.Image(src=current_icon, width=28, height=28, fit=ft.ImageFit.CONTAIN)
        else:
            current_icon_widget = ft.Text(current_icon, size=24, weight=ft.FontWeight.BOLD)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("选择应用图标", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("当前图标:", size=14, color=self.clr_text2),
                        ft.Container(width=8),
                        current_icon_widget,
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.only(0, 0, 0, 10),
                ),
                icon_col,
            ], tight=True, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.dialog.open = True
        self.page.update()

    def _select_app_icon(self, icon_info):
        """选择应用图标（支持图片和自定义）"""
        icon_type = icon_info.get("type", "image")
        if icon_type == "custom":
            # 自定义图标：打开文件选择器
            self._close_dialog()
            self._pick_custom_icon()
            return
        icon_value = icon_info.get("image_path", "")
        self.settings["app_icon"] = icon_value
        self.settings["app_icon_type"] = "image"
        save_settings(self.settings)
        self._close_dialog()
        self._show_toast("应用图标已更新")
        self.render_settings_page()

    def _pick_custom_icon(self):
        """打开文件选择器，让用户选择自定义图标"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="选择应用图标",
                filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")]
            )
            root.destroy()
            if file_path:
                # 复制用户选择的图片到assets目录
                import shutil
                custom_icon_path = os.path.join(_base_dir, "assets", "user_custom_icon.png")
                shutil.copy(file_path, custom_icon_path)
                # 保存自定义图标
                self.settings["app_icon"] = custom_icon_path
                self.settings["app_icon_type"] = "custom"
                save_settings(self.settings)
                self._show_toast("自定义图标已设置")
                # 刷新设置页面
                self.render_settings_page()
        except Exception as e:
            self._show_toast("选择图片失败，请重试")
    
    def _get_current_app_icon(self):
        """获取当前应用图标（支持图片和emoji）"""
        icon_type = self.settings.get("app_icon_type", "image")
        if icon_type == "image":
            # 图片图标，返回图片路径
            local_icon_path = os.path.join(_base_dir, "assets", "cute_email_icon.png")
            return self.settings.get("app_icon", local_icon_path)
        else:
            # emoji图标
            return self.settings.get("app_icon", "📧")

    def _get_current_app_icon_type(self):
        """获取当前应用图标类型"""
        return self.settings.get("app_icon_type", "image")

    def _get_empty_email_icon_path(self):
        """获取当前主题对应的空邮箱图标路径（白天/夜间自适应）"""
        mode = self.settings.get("theme_mode", "system")
        if mode == "dark":
            # 夜间模式：黑色背景，白色邮箱
            return os.path.join(_base_dir, "assets", "empty_email_icon_dark.png")
        else:
            # 白天模式或跟随系统（默认白天）：白色背景，黑色邮箱
            return os.path.join(_base_dir, "assets", "empty_email_icon.png")

    def _build_app_icon_widget(self, size=28):
        """构建应用图标组件（支持图片、emoji和自定义）"""
        icon_type = self._get_current_app_icon_type()
        icon_value = self._get_current_app_icon()
        if icon_type in ("image", "custom"):
            # 图片图标和自定义图标都用Image显示
            return ft.Image(src=icon_value, width=size, height=size, fit=ft.ImageFit.CONTAIN)
        else:
            return ft.Text(icon_value, size=size)
        icon_value = self._get_current_app_icon()
        return ft.Text(icon_value, size=size, weight=ft.FontWeight.BOLD)

    def _build_menu_item(self, icon, icon_color, label, on_click):
        """构建设置菜单项（现代风格：阴影+圆角+图标背景）"""
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, size=18, color=icon_color),
                    width=30, height=30,
                    bgcolor=ft.colors.with_opacity(0.12, icon_color),
                    border_radius=9, alignment=ft.alignment.center),
                ft.Container(width=8),
                ft.Text(label, size=FONT_MD, expand=True, color=self.clr_text, weight=FONT_MEDIUM),
                ft.Icon(ft.icons.CHEVRON_RIGHT, size=18, color=self.clr_text3),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=RADIUS_MD, padding=14,
            margin=ft.margin.only(SPACE_LG, 3, SPACE_LG, 3),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8,
                color=ft.colors.with_opacity(0.06, ft.colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=on_click,
        )

    def _show_change_password_dialog(self, e=None):
        """显示修改密码弹窗"""
        print("[修改密码] 点击了修改密码按钮")
        if not self.current_user:
            print("[修改密码] 未登录，显示提示")
            self.page.snack_bar = ft.SnackBar(ft.Text("请先登录"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        print("[修改密码] 已登录，显示弹窗")
        self._old_password_input = ft.TextField(
            label="原密码",
            password=True,
            can_reveal_password=True,
            width=280,
        )
        self._new_password_input = ft.TextField(
            label="新密码",
            password=True,
            can_reveal_password=True,
            width=280,
        )
        self._confirm_password_input = ft.TextField(
            label="确认新密码",
            password=True,
            can_reveal_password=True,
            width=280,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("修改密码", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self._old_password_input,
                ft.Container(height=8),
                self._new_password_input,
                ft.Container(height=8),
                self._confirm_password_input,
                ft.Container(height=8),
                ft.Text("密码长度至少6位", size=11, color=ft.colors.GREY_500),
            ], spacing=0, tight=True, width=280),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("确认修改", on_click=lambda e: self._do_change_password()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        print("[修改密码] 弹窗已显示")

    def _do_change_password(self):
        """执行修改密码"""
        old_password = self._old_password_input.value or ""
        new_password = self._new_password_input.value or ""
        confirm_password = self._confirm_password_input.value or ""

        # 验证输入
        if not old_password:
            self.page.snack_bar = ft.SnackBar(ft.Text("请输入原密码"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not new_password:
            self.page.snack_bar = ft.SnackBar(ft.Text("请输入新密码"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        if len(new_password) < 6:
            self.page.snack_bar = ft.SnackBar(ft.Text("新密码长度至少6位"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        if new_password != confirm_password:
            self.page.snack_bar = ft.SnackBar(ft.Text("两次输入的新密码不一致"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # 关闭弹窗
        self._close_dialog()

        # 显示加载中
        self.page.dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=30, height=30, color=THEME_COLOR, stroke_width=3),
                    ft.Container(height=8),
                    ft.Text("修改中...", size=12, color=ft.colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                width=120,
                height=100,
                padding=ft.padding.all(10),
            ),
        )
        self.page.dialog.open = True
        self.page.update()

        def change_thread():
            try:
                user_id = self.current_user.get("id", "")
                # 调用网站后端的修改密码API
                ok, result = self._remote_api_request("POST", "change-password", body={
                    "user_id": user_id,
                    "old_password": old_password,
                    "new_password": new_password,
                })

                self.page.run_thread(self._close_loading_dialog)

                if ok and isinstance(result, dict) and result.get("ok"):
                    self.page.run_thread(self._close_loading_dialog)
                    # 修改成功后立马退出登录，跳转到登录页，让用户用新密码重新登录
                    self.page.run_thread(self._logout_immediately)
                else:
                    error_msg = "修改失败"
                    if isinstance(result, dict):
                        error_msg = result.get("msg", "修改失败")
                    self.page.snack_bar = ft.SnackBar(ft.Text(error_msg))
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception as e:
                self.page.run_thread(self._close_loading_dialog)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"修改失败: {str(e)}"))
                self.page.snack_bar.open = True
                self.page.update()

        threading.Thread(target=change_thread, daemon=True).start()

    def _close_loading_dialog(self):
        """关闭加载弹窗"""
        try:
            if self.page.dialog:
                self.page.dialog.open = False
                self.page.update()
        except:
            pass

    def _logout_immediately(self):
        """立马退出登录，跳转到登录页（不显示加载页面，不等待）"""
        try:
            # 清除当前用户信息
            self.current_user = None
            self.data["current_user"] = None
            save_data(self.data)
            # 清除页面内容和导航栏
            self.page.controls.clear()
            self.page.navigation_bar = None
            self.page.floating_action_button = None
            # 跳转到登录页
            self.show_fullscreen_login()
            # 显示提示
            self.page.snack_bar = ft.SnackBar(ft.Text("密码修改成功，请用新密码登录"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            print(f"立即退出登录失败: {e}")

    def _build_option_row(self, icon, icon_color, label, options, current_value, on_select):
        """构建带选项按钮的设置行"""
        option_buttons = []
        for opt in options:
            is_selected = opt["value"] == current_value
            option_buttons.append(ft.Container(
                content=ft.Text(opt["label"], size=12,
                    color=ft.colors.WHITE if is_selected else self.clr_text2),
                bgcolor=THEME_COLOR if is_selected else self.clr_input_bg,
                border_radius=8, padding=ft.padding.symmetric(horizontal=10, vertical=5),
                on_click=lambda e, v=opt["value"]: on_select(v),
            ))
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, size=18, color=icon_color),
                    width=30, height=30, bgcolor=self.clr_input_bg,
                    border_radius=8, alignment=ft.alignment.center),
                ft.Container(width=8),
                ft.Text(label, size=15, expand=True, color=self.clr_text),
                ft.Row(option_buttons, spacing=4),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=12, padding=14,
            margin=ft.margin.only(16, 2, 16, 2),
        )

    def _toggle_auto_refresh(self, value):
        """切换收件箱自动刷新"""
        self.settings["inbox_auto_refresh"] = value
        save_settings(self.settings)
        self.page.snack_bar = ft.SnackBar(ft.Text("已开启自动刷新" if value else "已关闭自动刷新"))
        self.page.snack_bar.open = True
        self.page.update()

    def _set_refresh_interval(self, seconds):
        """设置刷新间隔"""
        self.settings["refresh_interval"] = seconds
        save_settings(self.settings)
        self.render_settings_page()

    def _fetch_latest_user_info(self):
        """从网站后端获取用户的最新信息（包括权限），并更新当前用户信息"""
        try:
            if not self.current_user:
                return
            user_id = self.current_user.get("id", "")
            if not user_id:
                return
            # 调用新的"获取我的权限"API（不需要管理员权限）
            ok, result = self._remote_api_request("GET", "my-permissions",
                body={"user_id": user_id}, get_with_body=True)
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                # 更新当前用户信息中的权限字段
                if "can_use_2h" in data:
                    self.current_user["can_use_2h"] = data.get("can_use_2h", False)
                if "can_use_permanent" in data:
                    self.current_user["can_use_permanent"] = data.get("can_use_permanent", False)
                # 同步更新到data中并保存
                if self.data.get("current_user"):
                    self.data["current_user"]["can_use_2h"] = self.current_user.get("can_use_2h", False)
                    self.data["current_user"]["can_use_permanent"] = self.current_user.get("can_use_permanent", False)
                    save_data(self.data)
        except:
            pass

    def _get_user_duration_permissions(self):
        """获取用户的有效期权限（2小时、永久）
        管理员默认就有权限，只有普通用户需要开通
        直接从API返回结果中获取权限，更可靠
        """
        try:
            if not self.current_user:
                return {"can_use_2h": False, "can_use_permanent": False}
            
            # 检查用户角色，管理员默认就有权限
            user_role = self.current_user.get("role", "") or self.current_user.get("chat_role", "")
            is_admin = user_role in ["管理员", "超级管理员", "频道主"] or self.current_user.get("is_admin") or self.current_user.get("is_super_admin")
            if is_admin:
                return {"can_use_2h": True, "can_use_permanent": True}
            
            # 普通用户：调用新的"获取我的权限"API获取最新权限
            user_id = self.current_user.get("id", "")
            if not user_id:
                return {"can_use_2h": False, "can_use_permanent": False}
            
            # 调用"获取我的权限"API（不需要管理员权限）
            ok, result = self._remote_api_request("GET", "my-permissions",
                body={"user_id": user_id}, get_with_body=True)
            
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                can_use_2h = data.get("can_use_2h", False)
                can_use_permanent = data.get("can_use_permanent", False)
                
                # 兼容字符串类型的布尔值
                if isinstance(can_use_2h, str):
                    can_use_2h = can_use_2h.lower() in ["true", "1", "yes"]
                if isinstance(can_use_permanent, str):
                    can_use_permanent = can_use_permanent.lower() in ["true", "1", "yes"]
                
                # 同时更新到当前用户信息中，方便其他地方使用
                self.current_user["can_use_2h"] = bool(can_use_2h)
                self.current_user["can_use_permanent"] = bool(can_use_permanent)
                if self.data.get("current_user"):
                    self.data["current_user"]["can_use_2h"] = bool(can_use_2h)
                    self.data["current_user"]["can_use_permanent"] = bool(can_use_permanent)
                    save_data(self.data)
                
                return {
                    "can_use_2h": bool(can_use_2h),
                    "can_use_permanent": bool(can_use_permanent),
                }
            
            # API调用失败，返回本地保存的权限（如果有的话）
            can_use_2h = self.current_user.get("can_use_2h", False)
            can_use_permanent = self.current_user.get("can_use_permanent", False)
            if isinstance(can_use_2h, str):
                can_use_2h = can_use_2h.lower() in ["true", "1", "yes"]
            if isinstance(can_use_permanent, str):
                can_use_permanent = can_use_permanent.lower() in ["true", "1", "yes"]
            
            return {
                "can_use_2h": bool(can_use_2h),
                "can_use_permanent": bool(can_use_permanent),
            }
        except Exception as e:
            # 出错时返回本地保存的权限
            can_use_2h = self.current_user.get("can_use_2h", False) if self.current_user else False
            can_use_permanent = self.current_user.get("can_use_permanent", False) if self.current_user else False
            return {
                "can_use_2h": bool(can_use_2h) if not isinstance(can_use_2h, str) else can_use_2h.lower() in ["true", "1", "yes"],
                "can_use_permanent": bool(can_use_permanent) if not isinstance(can_use_permanent, str) else can_use_permanent.lower() in ["true", "1", "yes"],
            }

    def _set_default_duration(self, hours):
        """设置默认邮箱有效期（需要权限检查，无弹窗，直接在后台检查）"""
        # 1小时默认所有用户都可以使用
        if hours == 1:
            self.settings["default_duration_hours"] = hours
            save_settings(self.settings)
            self.render_settings_page()
            return
        
        # 2小时和永久需要权限，直接在后台检查权限
        duration_name = "2小时" if hours == 2 else "永久"
        
        # 显示"正在检查权限..."提示（toast，不是弹窗）
        self._show_toast(f"正在检查{duration_name}权限...")
        
        # 在后台线程中检查权限
        def check_permission_thread():
            try:
                permissions = self._get_user_duration_permissions()
                has_permission = False
                if hours == 2 and permissions.get("can_use_2h"):
                    has_permission = True
                elif hours == -1 and permissions.get("can_use_permanent"):
                    has_permission = True
                
                # 检查完成后，在主线程中处理结果
                def handle_result():
                    if has_permission:
                        # 有权限，设置默认有效期
                        self.settings["default_duration_hours"] = hours
                        save_settings(self.settings)
                        self.render_settings_page()
                        self._show_toast(f"已设置默认有效期为{duration_name}")
                    else:
                        # 没有权限，弹出提示
                        self._show_permission_required_dialog(duration_name)
                
                self.page.run_thread(handle_result)
            except Exception as e:
                def handle_error():
                    self._show_toast(f"权限检查失败: {str(e)[:20]}")
                self.page.run_thread(handle_error)
        
        threading.Thread(target=check_permission_thread, daemon=True).start()

    def _fetch_and_display_permission_status(self):
        """获取并显示当前用户的有效期权限状态"""
        try:
            if not self.current_user:
                def update_no_login():
                    if hasattr(self, '_permission_status_text'):
                        self._permission_status_text.value = "未登录"
                        self._permission_status_text.color = ft.colors.GREY_500
                        self.page.update()
                self.page.run_thread(update_no_login)
                return
            
            # 检查用户角色，管理员默认就有权限
            user_role = str(self.current_user.get("role", "") or self.current_user.get("chat_role", ""))
            is_admin = user_role in ["管理员", "超级管理员", "频道主", "admin", "Admin", "超级管理"] or self.current_user.get("is_admin") or self.current_user.get("is_super_admin")
            
            if is_admin:
                def update_admin():
                    if hasattr(self, '_permission_status_text'):
                        self._permission_status_text.value = "管理员：已开通全部权限 ✓"
                        self._permission_status_text.color = ft.colors.GREEN
                        self.page.update()
                self.page.run_thread(update_admin)
                return
            
            # 普通用户：先检查本地是否有权限信息
            local_2h = self.current_user.get("can_use_2h", False)
            local_permanent = self.current_user.get("can_use_permanent", False)
            if isinstance(local_2h, str):
                local_2h = local_2h.lower() in ["true", "1", "yes"]
            if isinstance(local_permanent, str):
                local_permanent = local_permanent.lower() in ["true", "1", "yes"]
            
            # 先显示本地权限状态
            def show_local_status():
                if hasattr(self, '_permission_status_text'):
                    parts = []
                    parts.append(f"2小时{'✓' if local_2h else '✗'}")
                    parts.append(f"永久{'✓' if local_permanent else '✗'}")
                    self._permission_status_text.value = " | ".join(parts) + " (刷新中)"
                    self._permission_status_text.color = ft.colors.GREY_500
                    self.page.update()
            self.page.run_thread(show_local_status)
            
            # 普通用户：调用新的"获取我的权限"API获取最新权限状态
            user_id = self.current_user.get("id", "")
            if not user_id:
                def update_no_id():
                    if hasattr(self, '_permission_status_text'):
                        self._permission_status_text.value = "用户ID为空"
                        self._permission_status_text.color = ft.colors.RED
                        self.page.update()
                self.page.run_thread(update_no_id)
                return
            
            ok, result = self._remote_api_request("GET", "my-permissions",
                body={"user_id": user_id}, get_with_body=True)
            
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                can_use_2h = data.get("can_use_2h", False)
                can_use_permanent = data.get("can_use_permanent", False)
                
                # 兼容字符串类型的布尔值
                if isinstance(can_use_2h, str):
                    can_use_2h = can_use_2h.lower() in ["true", "1", "yes"]
                if isinstance(can_use_permanent, str):
                    can_use_permanent = can_use_permanent.lower() in ["true", "1", "yes"]
                
                # 更新当前用户信息中的权限字段
                self.current_user["can_use_2h"] = bool(can_use_2h)
                self.current_user["can_use_permanent"] = bool(can_use_permanent)
                if self.data.get("current_user"):
                    self.data["current_user"]["can_use_2h"] = bool(can_use_2h)
                    self.data["current_user"]["can_use_permanent"] = bool(can_use_permanent)
                    save_data(self.data)
                
                # 构建权限状态文本
                status_parts = []
                status_parts.append(f"2小时{'✓' if can_use_2h else '✗'}")
                status_parts.append(f"永久{'✓' if can_use_permanent else '✗'}")
                
                status_text = " | ".join(status_parts)
                all_permissions = can_use_2h and can_use_permanent
                color = ft.colors.GREEN if all_permissions else (ft.colors.ORANGE if can_use_2h or can_use_permanent else ft.colors.GREY_500)
                
                def update_status():
                    if hasattr(self, '_permission_status_text'):
                        self._permission_status_text.value = status_text
                        self._permission_status_text.color = color
                        self.page.update()
                self.page.run_thread(update_status)
            else:
                # API调用失败，显示本地权限状态
                error_msg = ""
                if isinstance(result, dict):
                    error_msg = result.get("msg", "")
                def update_fail():
                    if hasattr(self, '_permission_status_text'):
                        parts = []
                        parts.append(f"2小时{'✓' if local_2h else '✗'}")
                        parts.append(f"永久{'✓' if local_permanent else '✗'}")
                        self._permission_status_text.value = " | ".join(parts)
                        self._permission_status_text.color = ft.colors.GREY_500
                        self.page.update()
                self.page.run_thread(update_fail)
        except Exception as e:
            def update_error():
                if hasattr(self, '_permission_status_text'):
                    self._permission_status_text.value = f"错误: {str(e)[:10]}"
                    self._permission_status_text.color = ft.colors.RED
                    self.page.update()
            self.page.run_thread(update_error)

    def _show_permission_required_dialog(self, duration_name):
        """显示需要权限的提示弹窗"""
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("需要管理员权限", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.icons.LOCK, size=48, color=ft.colors.ORANGE),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(0, 10, 0, 10),
                ),
                ft.Text(f"您当前没有使用「{duration_name}」有效期的权限", size=14, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text("请联系管理员开通权限后再使用", size=13, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text("管理员QQ群：1093927643", size=12, color=ft.colors.BLUE_500),
                    alignment=ft.alignment.center,
                ),
            ], spacing=0, tight=True, width=280, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("我知道了", on_click=lambda e: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.dialog.open = True
        self.page.update()

    def _apply_theme_mode(self):
        """应用保存的主题模式及对应颜色"""
        mode = self.settings.get("theme_mode", "system")
        if mode == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self._set_light_colors()
            self.page.bgcolor = LIGHT_BG
        elif mode == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
            self._set_dark_colors()
            self.page.bgcolor = DARK_BG
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            self._set_light_colors()
            self.page.bgcolor = LIGHT_BG
        self._update_navbar_theme()

    def _update_navbar_theme(self):
        """更新自定义导航栏主题（白天/夜间切换时重建）"""
        try:
            if hasattr(self, '_navbar_area') and self._navbar_area:
                self._navbar_area.content = self._build_custom_navbar()
        except:
            pass

    def _set_light_colors(self):
        """浅色主题（iOS风格）"""
        self.clr_bg = LIGHT_BG
        self.clr_card = LIGHT_CARD
        self.clr_header_bg = LIGHT_HEADER
        self.clr_text = LIGHT_TEXT
        self.clr_text2 = LIGHT_TEXT2
        self.clr_text3 = LIGHT_TEXT3
        self.clr_border = LIGHT_BORDER
        self.clr_input_bg = LIGHT_INPUT

    def _set_dark_colors(self):
        """深色主题（iOS风格）"""
        self.clr_bg = DARK_BG
        self.clr_card = DARK_CARD
        self.clr_header_bg = DARK_HEADER
        self.clr_text = DARK_TEXT
        self.clr_text2 = DARK_TEXT2
        self.clr_text3 = DARK_TEXT3
        self.clr_border = DARK_BORDER
        self.clr_input_bg = DARK_INPUT

    def _set_theme_mode(self, mode):
        """设置主题模式并保存，同时刷新当前页面"""
        self.settings["theme_mode"] = mode
        save_settings(self.settings)
        self._apply_theme_mode()
        label = "白天模式" if mode == "light" else ("夜间模式" if mode == "dark" else "跟随系统")
        self._show_toast("已切换到" + label)
        self.page.update()
        # 重新渲染当前页面以应用新颜色
        try:
            if self.current_tab == 0:
                self.render_email_list()
            elif self.current_tab == 1:
                self.render_channel_page()
            elif self.current_tab == 2:
                self.render_me_page()
        except:
            pass

    # ========== 个人主页详情 ==========
    def show_user_profile(self, e=None):
        """显示个人主页详细信息"""
        if not self.current_user:
            return
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = None  # 关闭整体滚动，标题固定

        qq = self.current_user.get("qq", "")
        email = self.current_user.get("email", "")
        username = self.current_user.get("username", "")
        name = self.current_user.get("name", username)
        role = self.current_user.get("role", "")
        user_id = str(self.current_user.get("id", ""))
        login_type = self.current_user.get("login_type", "remote")
        avatar_text = (name[0] if name else (qq[0] if qq else "U")).upper()

        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_me_page()),
                ft.Text("个人主页", size=20, weight=ft.FontWeight.BOLD, expand=True),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # 可滚动内容区域
        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 头像和用户名区域（彩色头部）
        qq_clean = qq.strip() if qq else ""
        if qq_clean:
            big_avatar = ft.Container(
                content=ft.Image(
                    src=f"https://q1.qlogo.cn/g?b=qq&nk={qq_clean}&s=140",
                    width=96, height=96, fit=ft.ImageFit.COVER, border_radius=48,
                    error_content=ft.Container(
                        content=ft.Text(avatar_text, size=36, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                        width=96, height=96, bgcolor=ft.colors.WHITE, alignment=ft.alignment.center,
                    ),
                ),
                width=96, height=96, border_radius=48,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        else:
            big_avatar = ft.Container(
                content=ft.Text(avatar_text, size=36, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                width=96, height=96, bgcolor=ft.colors.WHITE,
                border_radius=48, alignment=ft.alignment.center,
            )

        # 角色标签（从网站获取，为空默认"用户"）
        display_role = role if role else "用户"
        role_color = ft.colors.AMBER if display_role in ["频道主", "频道组"] else (
            ft.colors.PURPLE if display_role in ["运营", "管理员", "admin", "Admin", "超级管理", "超级管理员"] else (
            ft.colors.BLUE if display_role == "测试" else ft.colors.RED))
        role_badge = ft.Container(content=ft.Text(display_role, size=11, color=ft.colors.WHITE),
            bgcolor=role_color, border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            alignment=ft.alignment.center)

        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Row([big_avatar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=12),
                ft.Row([
                    ft.Text(name or username or "用户", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Container(width=8),
                    role_badge,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                ft.Container(height=4),
                ft.Text("ID: " + self.format_user_id(user_id), size=12, color=ft.colors.WHITE70),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            bgcolor=THEME_COLOR, border_radius=16, padding=24,
            margin=ft.margin.only(16, 4, 16, 6),
        ))

        # 账户信息
        scroll_content.controls.append(ft.Container(
            content=ft.Text("账户信息", size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        info_items = []
        info_items.append({"label": "昵称", "value": name or username or "未设置", "edit": True})
        if qq:
            info_items.append({"label": "QQ号", "value": qq, "copy": True})
        info_items.append({"label": "用户ID", "value": self.format_user_id(user_id), "copy": True})
        if email:
            info_items.append({"label": "邮箱", "value": email, "copy": True})

        for item in info_items:
            row_content = [
                ft.Text(item["label"], size=14, color=self.clr_text2, expand=True),
                ft.Text(item["value"], size=14, weight=ft.FontWeight.W_500, color=self.clr_text),
            ]
            if item.get("copy"):
                row_content.append(ft.Container(width=8))
                row_content.append(ft.Container(
                    content=ft.Text("复制", size=11, color=THEME_COLOR, weight=ft.FontWeight.W_500),
                    on_click=lambda e, v=item["value"], l=item["label"]: self._copy_text(v, l + "已复制"),
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    bgcolor=ft.colors.BLUE_50, border_radius=6,
                ))
            if item.get("edit"):
                row_content.append(ft.Container(width=8))
                row_content.append(ft.Container(
                    content=ft.Text("修改", size=11, color=THEME_COLOR, weight=ft.FontWeight.W_500),
                    on_click=lambda e: self._show_edit_name_dialog(),
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    bgcolor=ft.colors.BLUE_50, border_radius=6,
                ))
            scroll_content.controls.append(ft.Container(
                content=ft.Row(row_content, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.clr_card, border_radius=12, padding=14,
                margin=ft.margin.only(16, 2, 16, 2),
            ))

        # 数据统计
        scroll_content.controls.append(ft.Container(
            content=ft.Text("数据统计", size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 14, 20, 6),
        ))
        email_count = len(getattr(self, '_cloud_emails_cache', []))
        msg_total = self._get_total_message_count()
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Column([
                    ft.Text(str(email_count), size=24, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Container(height=2),
                    ft.Text("邮箱数量", size=12, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, alignment=ft.alignment.center, padding=14),
                ft.Container(width=1, bgcolor=self.clr_border, height=50),
                ft.Container(content=ft.Column([
                    ft.Text(str(msg_total), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE),
                    ft.Container(height=2),
                    ft.Text("收到邮件", size=12, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, alignment=ft.alignment.center, padding=14),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14,
            margin=ft.margin.only(16, 2, 16, 6),
        ))

        scroll_content.controls.append(ft.Container(height=20))
        # 把可滚动内容区域添加到页面中
        self.content.controls.append(scroll_content)
        self.page.update()

    def _show_toast(self, msg, msg_type="success"):
        """右上角弹出提示（现代风格：阴影+圆角+图标）"""
        try:
            self.page.snack_bar = None
            # 根据类型选择图标和颜色
            icon_map = {
                "success": (ft.icons.CHECK_CIRCLE, COLOR_SUCCESS),
                "error": (ft.icons.ERROR, COLOR_DANGER),
                "warning": (ft.icons.WARNING, COLOR_WARNING),
                "info": (ft.icons.INFO, COLOR_INFO),
            }
            icon, icon_color = icon_map.get(msg_type, icon_map["success"])
            toast = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=18, color=ft.colors.WHITE),
                        width=28, height=28,
                        bgcolor=icon_color,
                        border_radius=14,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=6),
                    ft.Text(msg, size=FONT_MD, color=self.clr_text, weight=FONT_MEDIUM),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.clr_card,
                border_radius=RADIUS_LG,
                padding=ft.padding.symmetric(horizontal=SPACE_LG, vertical=SPACE_MD),
                bottom=100, right=SPACE_LG,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.colors.with_opacity(0.15, ft.colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
            )
            self.page.overlay.append(toast)
            self.page.update()
            def remove_toast():
                time.sleep(2.2)
                try:
                    if toast in self.page.overlay:
                        self.page.overlay.remove(toast)
                        self.page.update()
                except:
                    pass
            threading.Thread(target=remove_toast, daemon=True).start()
        except:
            pass

    def _show_edit_name_dialog(self):
        """显示修改昵称对话框"""
        current_name = self.current_user.get("name", self.current_user.get("username", ""))
        name_field = ft.TextField(
            label="新昵称",
            value=current_name,
            width=300,
            border_radius=8,
            hint_text="2-20个字符，不能与他人重复",
        )
        def on_confirm(e):
            new_name = (name_field.value or "").strip()
            if not new_name:
                self._show_toast("昵称不能为空")
                return
            if len(new_name) < 2:
                self._show_toast("昵称至少2个字符")
                return
            if len(new_name) > 20:
                self._show_toast("昵称不能超过20个字符")
                return
            self.page.dialog.open = False
            self.page.update()
            self._show_toast("正在检查并更新...")
            threading.Thread(target=self._do_update_name, args=(new_name,), daemon=True).start()
        def on_cancel(e):
            self.page.dialog.open = False
            self.page.update()
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("修改昵称"),
            content=ft.Column([name_field], tight=True),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.TextButton("确定", on_click=on_confirm),
            ],
        )
        self.page.dialog.open = True
        self.page.update()

    def _do_update_name(self, new_name):
        """更新昵称（直接调用 update-profile 接口，不检查重复）"""
        try:
            user_id = str(self.current_user.get("id", ""))
            if not user_id:
                self.page.run_thread(lambda: self._show_toast("用户信息异常，请重新登录"))
                return
            # 直接调用 update-profile 接口更新昵称
            update_ok, update_result = self._remote_api_request("POST", "update-profile", body={
                "user_id": user_id,
                "name": new_name,
            })
            if update_ok and isinstance(update_result, dict) and update_result.get("ok"):
                # 更新本地缓存（只更新内存中的 current_user，不保存到本地）
                self.current_user["name"] = new_name
                self.page.run_thread(lambda: self._show_toast("昵称修改成功"))
                self.page.run_thread(self.show_user_profile)
            else:
                # 更新失败，显示错误信息
                err_msg = ""
                if isinstance(update_result, dict):
                    err_msg = update_result.get("msg", update_result.get("message", ""))
                self.page.run_thread(lambda: self._show_toast("修改失败：" + (err_msg or "请稍后重试")))
        except Exception as ex:
            self.page.run_thread(lambda: self._show_toast("修改失败：" + str(ex)[:30]))

    # ========== 主页功能方法 ==========
    def _copy_text(self, text, label="已复制"):
        """复制文本到剪贴板并提示"""
        try:
            self.page.set_clipboard(str(text))
            self.page.snack_bar = ft.SnackBar(ft.Text(label + ": " + str(text)[:30]))
            self.page.snack_bar.open = True
            self.page.update()
        except:
            pass

    def _check_update(self, e=None):
        """检查更新"""
        try:
            current_version = APP_CONFIG.get("app_version", "1.0.0")
            update_url = APP_CONFIG.get("update_url", "")
            remote_config = getattr(self, '_remote_config', {})
            need_update = remote_config.get("need_update", False)
            target_version = remote_config.get("target_version", "")

            if need_update and target_version and target_version != current_version:
                content_text = f"发现新版本 {target_version}\n当前版本 {current_version}\n\n点击确定前往下载"
            else:
                content_text = f"当前已是最新版本\n版本号: {current_version}"

            def go_update(ev):
                self._close_dialog()
                if update_url:
                    try:
                        self.page.launch_url(update_url)
                    except:
                        try:
                            import webbrowser
                            webbrowser.open(update_url)
                        except:
                            pass

            actions = [ft.TextButton("关闭", on_click=lambda ev: self._close_dialog())]
            if need_update and target_version and target_version != current_version:
                actions.append(ft.TextButton("去更新", on_click=go_update))

            self.page.dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.UPDATE, size=22, color=THEME_COLOR),
                    ft.Container(width=8),
                    ft.Text("检查更新", size=18, weight=ft.FontWeight.BOLD),
                ]),
                content=ft.Text(content_text, size=14, color=ft.colors.GREY_700),
                actions=actions,
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text("检查更新失败: " + str(ex)[:30]))
            self.page.snack_bar.open = True
            self.page.update()

    def _clear_cache(self, e=None):
        """清理缓存并重新同步"""
        try:
            # 清除各类缓存
            self._cloud_emails_cache = []
            self._msg_counts = {}
            self._last_email_sync_time = 0
            if hasattr(self, '_cached_channel_messages'):
                self._cached_channel_messages = []
            if hasattr(self, '_last_channel_msg_load_time'):
                self._last_channel_msg_load_time = 0

            self.page.snack_bar = ft.SnackBar(ft.Text("缓存已清理，正在重新同步..."))
            self.page.snack_bar.open = True
            self.page.update()

            # 后台重新同步邮箱数据（不跳转页面）
            def reload_background():
                time.sleep(0.3)
                try:
                    self._sync_emails_from_cloud()
                except:
                    pass
            threading.Thread(target=reload_background, daemon=True).start()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text("清理缓存失败: " + str(ex)[:30]))
            self.page.snack_bar.open = True
            self.page.update()

    def _join_qq_group(self, e=None):
        """加入QQ群（直接跳转QQ群，不打开浏览器）"""
        try:
            qq_group_number = "1093927643"
            # 直接跳转QQ群的协议链接
            qq_group_url = f"mqqwpa://im/chat?chat_type=group&uin={qq_group_number}&version=1"
            try:
                self.page.launch_url(qq_group_url)
            except:
                try:
                    import webbrowser
                    webbrowser.open(qq_group_url)
                except:
                    self._copy_text(qq_group_number, "QQ群号已复制，请手动添加")
        except:
            self._copy_text("1093927643", "QQ群号已复制，请手动添加")

    def _show_about_dialog(self, e=None):
        """显示关于应用弹窗"""
        try:
            app_name = APP_CONFIG.get("app_name", "YoXi邮箱")
            app_version = APP_CONFIG.get("app_version", "1.0.0")
            # 获取当前应用图标组件（支持图片图标和远程图标）
            app_icon_widget = self._build_app_icon_widget(size=28)
            self.page.dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Container(content=app_icon_widget,
                        width=44, height=44, bgcolor=ft.colors.WHITE,
                        border_radius=12, alignment=ft.alignment.center),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text(app_name, size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("版本 " + app_version, size=12, color=ft.colors.GREY_500),
                    ], spacing=2),
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("临时邮箱工具，支持多种邮箱服务商", size=13, color=ft.colors.GREY_600),
                        ft.Container(height=8),
                        ft.Text("支持: mail.tm / Guerrilla / maildrop / temp-mail.io / Gmail别名", size=11, color=ft.colors.GREY_500),
                        ft.Container(height=8),
                        ft.Text("免费接收短信验证码", size=11, color=ft.colors.GREY_500),
                        ft.Container(height=12),
                        ft.Container(height=1, bgcolor=ft.colors.GREY_200),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text("邮箱交流群: ", size=12, color=ft.colors.GREY_600),
                            ft.Text("1093927643", size=12, color=THEME_COLOR, weight=ft.FontWeight.W_500),
                        ], spacing=0),
                    ], spacing=0, tight=True),
                    width=280,
                ),
                actions=[
                    ft.TextButton("关闭", on_click=lambda ev: self._close_dialog()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog.open = True
            self.page.update()
        except Exception as ex:
            pass

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


def _pre_set_window_icon():
    """在ft.app启动前就开始监控窗口，一创建就立马设置图标（几乎看不到默认图标）"""
    try:
        import time
        import ctypes
        from ctypes import wintypes
        import os as _os
        ico_path = _os.path.join(_base_dir, "assets", "app_icon.ico")
        if not _os.path.exists(ico_path):
            return
        user32 = ctypes.windll.user32
        win_title = APP_CONFIG.get("app_name", "YoXi邮箱")
        # 高频轮询：每50ms查一次，最多等10秒
        for _ in range(200):
            hwnd = user32.FindWindowW(None, win_title)
            if hwnd:
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                hicon_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
                hicon_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                WM_SETICON = 0x0080
                ICON_BIG = 1
                ICON_SMALL = 0
                if hicon_big:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
                if hicon_small:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
                user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0020 | 0x0001 | 0x0002 | 0x0040)
                print(f"[预启动图标] 窗口一创建就设置成功, hwnd={hwnd}")
                return
            time.sleep(0.05)
    except Exception as e:
        print(f"[预启动图标] 失败: {e}")

if __name__ == "__main__":
    import threading
    # 在ft.app启动前就开始监控窗口，一创建就立马设置图标
    threading.Thread(target=_pre_set_window_icon, daemon=True).start()
    ft.app(target=main)

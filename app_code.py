import flet as ft
try:
    from flet_core import WebView as FletWebView
except ImportError:
    FletWebView = None
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
    "app_name": "YoXi网盘",
    "app_version": "1.1.0",
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
    "default_app_icon": "assets/default_icon.png",
    "smtp_host": "smtp.qq.com",
    "smtp_port": 465,
    "smtp_user": "",
    "smtp_password": "",
    "feedback_to_email": "o1415520@qq.com",
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


def mailtm_create(domain=None):
    """创建随机临时邮箱，可指定域名"""
    import random, string
    if domain:
        # 使用指定域名
        domain = domain
    else:
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


def guerrilla_set_email_user(email_user):
    """用邮箱用户名重新建立Guerrilla会话，返回新的sid_token"""
    import urllib.parse
    url = "https://api.guerrillamail.com/ajax.php?f=set_email_user&email_user=" + urllib.parse.quote(email_user) + "&lang=en"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.guerrillamail.com/",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data.get("sid_token", ""), data.get("email_addr", "")
    except Exception as e:
        return False, str(e), ""


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


def guerrilla_delete_email(sid_token, email_id):
    """删除Guerrilla Mail邮件"""
    import urllib.parse
    url = "https://api.guerrillamail.com/ajax.php?f=del_email&email_ids=" + urllib.parse.quote(str(email_id)) + "&sid_token=" + urllib.parse.quote(sid_token) + "&lang=en"
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
        # 网盘数据缓存（加载页预加载，避免每次进入都重新请求）
        self._cached_cloud_files = None
        self._cached_cloud_used_mb = 0
        self._cached_cloud_stats = None  # 网盘统计：folder_count, file_count 等
        self._cloud_files_loading = False
        self.current_folder_id = 0  # 当前所在文件夹ID，0表示根目录
        self.folder_path = []  # 文件夹路径栈，用于返回上级
        # 昵称颜色配置（运行时初始化，ft.colors在类定义时不可用）
        self.NAME_COLORS = {
            "purple": {"name": "紫色名字", "color": ft.colors.PURPLE, "points": 50, "icon": ft.icons.PALETTE},
            "red": {"name": "红色名字", "color": ft.colors.RED, "points": 50, "icon": ft.icons.FAVORITE},
            "green": {"name": "绿色名字", "color": ft.colors.GREEN, "points": 50, "icon": ft.icons.ECO},
            "rainbow": {"name": "彩色名字", "color": "rainbow", "points": 200, "icon": ft.icons.AUTO_AWESOME},
        }
        self.RAINBOW_COLORS = [ft.colors.RED, ft.colors.ORANGE, ft.colors.YELLOW, ft.colors.GREEN, ft.colors.BLUE, ft.colors.PURPLE]

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
        # 安卓返回键处理：子页面返回上一页，主页面退出应用
        self.page.on_view_pop = self._on_view_pop
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
            win_title = APP_CONFIG.get("app_name", "YoXi网盘")
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
        """加载页（简单可靠布局，兼容安卓）"""
        self.page.controls.clear()
        self.page.navigation_bar = None
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = ft.colors.BLACK
        self._skipped = False
        self._breathing_running = False

        app_name = APP_CONFIG.get("app_name", "YoXi网盘")
        app_version = APP_CONFIG.get("app_version", "1.0.0")

        # 进度条和状态文字
        self.progress = ft.ProgressBar(
            width=260, value=0, color=THEME_COLOR,
            bgcolor=ft.colors.with_opacity(0.3, ft.colors.WHITE),
            border_radius=4,
        )
        self.status_text = ft.Text("正在加载...", size=12, color=ft.colors.WHITE, weight=FONT_MEDIUM)

        # 右上角跳过按钮
        self._skip_text = ft.Text("跳过 5s", size=13, color=ft.colors.WHITE, weight=FONT_MEDIUM)
        skip_btn = ft.GestureDetector(
            content=ft.Container(
                content=ft.Row([
                    self._skip_text,
                    ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=12, color=ft.colors.WHITE),
                ], spacing=3),
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                border_radius=RADIUS_PILL,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            on_tap=self._skip_loading,
        )

        # 底部卡片
        _bottom_icon_path = self._get_current_app_icon()
        bottom_icon_widget = ft.Container(
            content=ft.Image(src=_bottom_icon_path, width=44, height=44, fit=ft.ImageFit.COVER),
            width=44, height=44, border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            alignment=ft.alignment.center,
        )
        bottom_card = ft.Container(
            content=ft.Column([
                self.progress,
                ft.Container(height=8),
                self.status_text,
                ft.Container(height=12),
                ft.Container(height=1, bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE)),
                ft.Container(height=10),
                ft.Row([
                    bottom_icon_widget,
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text(app_name, size=16, weight=FONT_BOLD, color=ft.colors.WHITE),
                        ft.Container(height=2),
                        ft.Text(f"版本 {app_version}", size=11, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.with_opacity(0.25, ft.colors.BLACK),
            border_radius=RADIUS_XL,
            padding=ft.padding.only(top=18, bottom=18, left=20, right=20),
            margin=ft.margin.only(left=20, right=20, bottom=24),
        )

        # 背景图路径（多路径尝试）
        candidate_bg_paths = [
            os.path.join(_base_dir, "assets", "app_background.jpg"),
            os.path.join(os.getcwd(), "assets", "app_background.jpg"),
            "assets/app_background.jpg",
        ]
        local_bg_path = candidate_bg_paths[0]
        for path in candidate_bg_paths:
            if os.path.exists(path):
                local_bg_path = path
                break

        # 简单布局：背景Container + Column内容（不用Stack，兼容安卓）
        full_page = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([skip_btn], alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.only(top=50, right=16),
                ),
                ft.Container(expand=True),
                bottom_card,
            ], spacing=0, expand=True),
            expand=True,
            image_src=local_bg_path,
            image_fit=ft.ImageFit.COVER,
            bgcolor=ft.colors.BLACK,
        )

        self.page.navigation_bar = None
        self.page.add(full_page)
        self.page.update()

        # 跳过倒计时（5秒后自动进入）
        threading.Thread(target=self._skip_countdown, daemon=True).start()
        # 获取远程配置
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
        """倒计时 5 秒，5秒后显示"进入"按钮，需用户手动点击进入"""
        try:
            self._can_enter = False
            self._load_completed = True  # 提前标记加载完成，避免等待
            for i in range(5, 0, -1):
                if getattr(self, '_skipped', False):
                    return
                try:
                    self._skip_text.value = f"{i}s"
                    self.page.update()
                except:
                    pass
                time.sleep(1)
            if not getattr(self, '_skipped', False):
                self._can_enter = True
                try:
                    self._skip_text.value = "进入"
                    self.page.update()
                except:
                    pass
                # 不自动进入，等待用户点击"进入"按钮
        except Exception as e:
            # 出错也显示进入按钮
            try:
                self._can_enter = True
                self._skip_text.value = "进入"
                self.page.update()
            except:
                pass

    def _skip_loading(self, e):
        """点击进入程序（5秒后即可点击进入，不等待后台加载完成）"""
        if getattr(self, '_skipped', False):
            return
        if not getattr(self, '_can_enter', False):
            # 还没到5秒，不弹出提示，直接返回
            return
        self._skipped = True
        # 标记加载完成（即使后台load_thread还在运行，也允许进入）
        self._load_completed = True
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
            self._load_completed = False
            self.update_splash(20, "检查网络..."); time.sleep(0.3)
            self.update_splash(50, "加载配置..."); time.sleep(0.3)
            # 检查是否已经获取了远程配置（由_fetch_remote_config_and_bg线程获取）
            if not hasattr(self, '_remote_config') or not self._remote_config:
                # 如果还没有获取到，再获取一次（带超时保护）
                try:
                    self._remote_config = self._fetch_remote_config()
                except:
                    self._remote_config = {}
            # 确保背景图已更新
            try:
                self._update_splash_background()
            except:
                pass
            self.update_splash(70, "验证账号..."); time.sleep(0.2)
            # 验证本地登录的账号（带超时保护，最多3秒）
            try:
                import threading as _th
                _result = {"done": False}
                def _verify():
                    try:
                        self._verify_local_user()
                    except:
                        pass
                    _result["done"] = True
                _th.Thread(target=_verify, daemon=True).start()
                for _ in range(30):
                    if _result["done"]:
                        break
                    time.sleep(0.1)
            except:
                pass
            # 从网站实时获取当前用户的最新角色（带超时保护，最多3秒）
            try:
                import threading as _th2
                _result2 = {"done": False}
                def _fetch_role():
                    try:
                        self._fetch_user_role_on_load()
                    except:
                        pass
                    _result2["done"] = True
                _th2.Thread(target=_fetch_role, daemon=True).start()
                for _ in range(30):
                    if _result2["done"]:
                        break
                    time.sleep(0.1)
            except:
                pass
            # 预加载网盘数据到缓存（后台线程，不阻塞加载）
            try:
                def _preload_cloud():
                    try:
                        if self.current_user:
                            self._cached_cloud_files = self._fetch_cloud_files_from_remote()
                            self._cached_cloud_used_mb = self._fetch_cloud_used_mb_from_remote()
                    except:
                        pass
                threading.Thread(target=_preload_cloud, daemon=True).start()
            except:
                pass
            # 预加载积分数据到缓存（后台线程，静默获取，不显示加载文字）
            try:
                def _preload_points():
                    try:
                        if self.current_user:
                            self._load_points_data_silent()
                    except:
                        pass
                threading.Thread(target=_preload_points, daemon=True).start()
            except:
                pass
            self.update_splash(90, "准备就绪..."); time.sleep(0.2)
            self.update_splash(100, "加载完成"); time.sleep(0.2)
            # 加载完成
            self._load_completed = True
        except Exception as e:
            if not hasattr(self, '_remote_config'):
                self._remote_config = {}
            # 加载失败也标记完成，避免卡住
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
                    if "用户不存在" in msg or "user not found" in msg or "not found" in msg and "user" in msg:
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
            data = json.dumps(request_body).encode("utf-8") if request_body is not None else None
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
        try:
            user_id = int(self.current_user.get("id", 0))
        except (ValueError, TypeError):
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
                    # 判断是否永久：优先看is_permanent字段，其次看status，最后看过期时间是否超过10年
                    "is_permanent": ce.get("is_permanent", False) or ce.get("status") == "permanent" or (expires_at_ts > time.time() + 10 * 365 * 24 * 3600),
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
            "is_permanent": email_data.get("is_permanent", False),  # 是否永久
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
        """发送频道消息到云端，返回 (成功, 错误信息)"""
        if not self.current_user:
            return False, "未登录"
        user_id = self.current_user.get("id", "")
        # 优先使用群昵称，否则用用户昵称，最后用username
        username = getattr(self, '_channel_nickname', "")
        if not username:
            username = self.current_user.get("name", self.current_user.get("username", ""))
        if not user_id:
            return False, "用户ID无效"
        try:
            ok, result = self._remote_api_request("POST", "chat/messages", body={
                "user_id": user_id,
                "username": username,
                "name": username,
                "content": content,
                "type": "text",
            })
            if ok and result.get("ok", False):
                return True, ""
            else:
                error_msg = result.get("msg", "发送失败") if isinstance(result, dict) else str(result)
                return False, error_msg
        except Exception as e:
            return False, str(e)[:50]

    def _send_heartbeat(self):
        """发送心跳上报（后台线程）"""
        try:
            base_url = APP_CONFIG.get("remote_api_base", "")
            app_key = APP_CONFIG.get("remote_app_key", "")
            if not base_url or not app_key:
                return
            url = f"{base_url}/api/remote/{app_key}/heartbeat"
            dev = self._get_device_info()
            payload = json.dumps({
                "version": APP_CONFIG.get("app_version", "1.0.0"),
                "status": "running",
                "platform": dev["platform"],
                "os_version": dev["os_version"],
                "device_model": dev["device_model"],
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

    def remote_register(self, username, password, email, qq="", name=""):
        """注册用户"""
        body = {"username": username, "password": password, "email": email}
        if qq:
            body["qq"] = qq
        if name:
            body["name"] = name
        return self._remote_api_call("register", body)

    def _get_device_info(self):
        """获取当前设备信息"""
        import platform
        return {
            "platform": "windows",
            "os_version": f"{platform.system()} {platform.release()}",
            "device_model": platform.node(),
        }

    def remote_login(self, qq, password):
        """用户登录（支持QQ号+密码，附带设备信息）"""
        dev = self._get_device_info()
        body = {"qq": qq, "password": password}
        body.update(dev)
        return self._remote_api_call("login", body)

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
                    # 检查今天是否已经选择了"今日不再提醒"
                    today_str = time.strftime("%Y-%m-%d")
                    last_dismiss_date = self.settings.get("announcement_dismiss_date", "")
                    if last_dismiss_date != today_str:
                        def show_announcement_delayed():
                            time.sleep(0.5)
                            self.page.run_thread(lambda: self._show_announcement(notice_title, notice_content))
                        threading.Thread(target=show_announcement_delayed, daemon=True).start()
        except Exception as e:
            # 如果出错，显示错误页面，避免白屏
            self._show_error_page("启动失败", str(e))

    def _show_announcement(self, title, content):
        """显示公告弹窗（新UI：自定义复选框+底部按钮）"""
        try:
            # QQ群号
            qq_group_number = "1093927643"
            qq_group_url = f"https://qm.qq.com/cgi-bin/qm/qr?k={qq_group_number}&jump_from=webapi"

            def join_qq_group(e):
                if qq_group_url:
                    try:
                        self.page.launch_url(qq_group_url)
                    except:
                        try:
                            import webbrowser
                            webbrowser.open(qq_group_url)
                        except:
                            self._copy_text(qq_group_number, "QQ群号已复制，请手动添加")
                self._close_dialog()

            # 自定义复选框状态
            dismiss_checked = {"value": False}
            check_icon = ft.Icon(ft.icons.CHECK, size=14, color=ft.colors.WHITE, visible=False)
            check_box = ft.Container(
                content=check_icon,
                width=18, height=18,
                bgcolor=ft.colors.TRANSPARENT,
                border=ft.border.all(1.5, ft.colors.GREY_400),
                border_radius=4,
                alignment=ft.alignment.center,
            )
            
            def toggle_check(e):
                dismiss_checked["value"] = not dismiss_checked["value"]
                if dismiss_checked["value"]:
                    check_box.bgcolor = THEME_COLOR
                    check_box.border = ft.border.all(1.5, THEME_COLOR)
                    check_icon.visible = True
                else:
                    check_box.bgcolor = ft.colors.TRANSPARENT
                    check_box.border = ft.border.all(1.5, ft.colors.GREY_400)
                    check_icon.visible = False
                self.page.update()
            
            dismiss_row = ft.GestureDetector(
                content=ft.Row([
                    check_box,
                    ft.Container(width=8),
                    ft.Text("今日不再提醒", size=13, color=ft.colors.GREY_700),
                ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                on_tap=toggle_check,
            )

            def on_confirm(e):
                if dismiss_checked["value"]:
                    self.settings["announcement_dismiss_date"] = time.strftime("%Y-%m-%d")
                    save_settings(self.settings)
                self._close_dialog()

            dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.CAMPAIGN, size=22, color=ft.colors.WHITE),
                        width=40, height=40, bgcolor=THEME_COLOR,
                        border_radius=20, alignment=ft.alignment.center,
                    ),
                    ft.Container(width=10),
                    ft.Text(title or "公告", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(content, size=14, color=ft.colors.GREY_700,
                            selectable=True),
                        ft.Container(height=20),
                        dismiss_row,
                    ], spacing=0, tight=True),
                    width=300,
                    padding=ft.padding.only(0, 8, 0, 0),
                ),
                actions=[
                    ft.TextButton("加入QQ群", on_click=join_qq_group,
                        style=ft.ButtonStyle(color=THEME_COLOR)),
                    ft.Container(
                        content=ft.Text("我知道了", size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
                        bgcolor=THEME_COLOR, border_radius=8,
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        on_click=on_confirm,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
                    self.current_tab = 0  # 默认选中网盘
                    self.render_cloud_drive_page()
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
            hint_text="QQ号", prefix_icon=ft.icons.CHAT_OUTLINED,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15),
            border_radius=12, bgcolor=ft.colors.WHITE,
            border_color=ft.colors.GREY_300, height=52, text_size=15, color=ft.colors.BLACK,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        password_field = ft.TextField(
            hint_text="密码", prefix_icon=ft.icons.LOCK_OUTLINE,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15),
            password=True, can_reveal_password=True,
            border_radius=12, bgcolor=ft.colors.WHITE,
            border_color=ft.colors.GREY_300, height=52, text_size=15, color=ft.colors.BLACK,
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
        app_name = APP_CONFIG.get("app_name", "YoXi网盘")
        _login_icon_path = self._get_current_app_icon()
        # 顶部品牌区：应用图标 + 名字 + slogan
        self.content.controls.append(ft.Container(height=70))
        self.content.controls.append(ft.Row([
            ft.Container(
                content=ft.Image(src=_login_icon_path, width=76, height=76, fit=ft.ImageFit.COVER),
                width=76, height=76,
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
        username_field = ft.TextField(hint_text="请输入昵称", prefix_icon=ft.icons.EDIT_NOTE_OUTLINED,
            border_radius=12, bgcolor=ft.colors.WHITE, border_color=ft.colors.GREY_300,
            height=52, text_size=15, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
        qq_field = ft.TextField(hint_text="请输入QQ号", prefix_icon=ft.icons.CHAT_OUTLINED,
            border_radius=12, bgcolor=ft.colors.WHITE, border_color=ft.colors.GREY_300,
            height=52, text_size=15, keyboard_type=ft.KeyboardType.NUMBER, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
        email_field = ft.TextField(hint_text="请输入邮箱地址", prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=12, bgcolor=ft.colors.WHITE, border_color=ft.colors.GREY_300,
            height=52, text_size=15, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
        code_field = ft.TextField(hint_text="请输入验证码", prefix_icon=ft.icons.VERIFIED_USER_OUTLINED,
            border_radius=12, bgcolor=ft.colors.WHITE, border_color=ft.colors.GREY_300,
            height=52, text_size=15, width=170, keyboard_type=ft.KeyboardType.NUMBER, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
        password_field = ft.TextField(hint_text="请设置密码（至少6位）", prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, border_radius=12, bgcolor=ft.colors.WHITE,
            border_color=ft.colors.GREY_300, height=52, text_size=15, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
        confirm_field = ft.TextField(hint_text="请再次输入密码", prefix_icon=ft.icons.LOCK_OUTLINE,
            password=True, can_reveal_password=True, border_radius=12, bgcolor=ft.colors.WHITE,
            border_color=ft.colors.GREY_300, height=52, text_size=15, color=ft.colors.BLACK,
            hint_style=ft.TextStyle(color=ft.colors.GREY_500, size=15))
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
                error_text.value = "请填写完整信息（昵称、QQ号、邮箱、验证码、密码）"
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
                # 第二步：username用QQ号（用于登录），name用用户输入的昵称
                reg_username = qq if qq else username
                # 第三步：注册用户（传递昵称name字段）
                ok_reg, result_reg = self.remote_register(reg_username, password, email, qq, name=username)
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
                        "name": result_reg.get("name", username) if isinstance(result_reg, dict) else username,
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
        app_name = APP_CONFIG.get("app_name", "YoXi网盘")
        _reg_icon_path = self._get_current_app_icon()
        # 顶部品牌区
        self.content.controls.append(ft.Container(height=50))
        self.content.controls.append(ft.Row([
            ft.Container(
                content=ft.Image(src=_reg_icon_path, width=64, height=64, fit=ft.ImageFit.COVER),
                width=64, height=64,
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
            # 默认渲染网盘（current_tab=0对应网盘）
            self.render_cloud_drive_page()
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
             {"index": 0, "icon": ft.icons.CLOUD_OUTLINED, "selected_icon": ft.icons.CLOUD, "label": "网盘"},
             {"index": 1, "icon": ft.icons.APPS_OUTLINED, "selected_icon": ft.icons.APPS, "label": "功能"},
             {"index": 2, "icon": ft.icons.MESSAGE_OUTLINED, "selected_icon": ft.icons.MESSAGE, "label": "频道"},
             {"index": 3, "icon": ft.icons.PERSON_OUTLINE, "selected_icon": ft.icons.PERSON, "label": "主页"},
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
            # 切换导航栏时清除悬浮加号按钮（避免加号位置错误或重复）
            self.page.floating_action_button = None
            if idx == 0:
                self.render_cloud_drive_page()
            elif idx == 1:
                self.render_features_page()
            elif idx == 2:
                self.render_channel_page()
            elif idx == 3:
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
            # 切换导航栏时清除悬浮加号按钮（避免加号位置错误或重复）
            self.page.floating_action_button = None
            if idx == 0:
                # 网盘
                self.render_cloud_drive_page()
            elif idx == 1:
                # 功能
                self.render_features_page()
            elif idx == 2:
                # 频道
                self.render_channel_page()
            elif idx == 3:
                # 主页
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
        # 从功能页面进入的邮箱（显示返回按钮）隐藏导航栏，否则显示
        if getattr(self, "_show_back_to_features", False):
            self._hide_navbar()
        else:
            self._show_navbar()
        self.content.controls.clear()
        self._stop_countdown()
        # 标题固定，不可滑动
        self.content.scroll = None
        # 加载状态（标题栏显示：正在同步时圆圈+未同步，完成后已同步）
        self._loading_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=THEME_COLOR)
        self._loading_status = ft.Text("未同步", size=12, color=self.clr_text2)
        self._loading_row = ft.Row([self._loading_ring, self._loading_status], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        # 标题区域（固定，背景和页面一致，顶部留空给灵动岛）
        header = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW, icon_size=22, icon_color=self.clr_text,
                            on_click=self._back_to_features, visible=getattr(self, "_show_back_to_features", False)),
                        ft.Text("临时邮箱", size=28, weight=ft.FontWeight.BOLD, color=self.clr_text),
                        ft.Container(width=8),
                        self._loading_row,
                        ft.Container(expand=True),
                        ft.IconButton(ft.icons.ADD_CIRCLE, icon_size=28, icon_color=THEME_COLOR, on_click=self.create_email),
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(20, 50, 20, 5),
                ),
                ft.Container(
                    content=ft.Text("创建临时邮箱，自动接收邮件", size=13, color=self.clr_text2),
                    padding=ft.padding.only(20, 0, 20, 10),
                ),
            ], spacing=0),
        )
        self.content.controls.append(header)
        # 邮箱列表区域（可滑动）- 初始显示加载状态，等同步完成后再渲染
        self._email_list_container = ft.ListView([], spacing=0, expand=True, padding=16)
        # 列表区域初始为空，等同步完成后渲染（加载状态显示在标题栏）
        self.content.controls.append(self._email_list_container)
        # 去掉底部悬浮按钮（改用标题栏右侧加号，避免和自定义底部导航栏冲突）
        self.page.floating_action_button = None
        self.page.update()
        self._start_countdown()
        # 先显示缓存的邮箱（如果有），让用户立即看到内容
        if getattr(self, '_cloud_emails_cache', []):
            self._loading_ring.visible = False
            self._loading_status.value = "已同步"
            self._loading_status.color = ft.colors.GREEN
            self._render_email_items()
        # 后台从云端同步最新邮箱（同步完成后自动更新列表）
        self._last_email_sync_time = time.time()
        threading.Thread(target=self._sync_emails_from_cloud, daemon=True).start()

    def _show_sync_dialog(self):
        """显示同步状态（不使用弹窗，避免残留，仅在列表区域显示加载文字）"""
        pass

    def _hide_sync_dialog(self):
        """隐藏同步状态（空操作，列表渲染时自动清除加载文字）"""
        pass

    def _hide_loading_status(self):
        """隐藏加载状态（关闭同步弹窗）"""
        self._hide_sync_dialog()

    def _sync_emails_from_cloud(self):
        """从云端同步用户邮箱（不保存到本地，直接更新UI）"""
        try:
            if not self.current_user:
                self._cloud_emails_cache = []
                self.page.run_thread(self._render_email_items)
                return
            cloud_emails = self._load_user_emails_from_cloud()
            # 不保存到本地，直接用云端邮箱更新UI
            self._cloud_emails_cache = cloud_emails if cloud_emails else []
            # 同步完成，更新标题栏状态为"已同步"并渲染列表
            def finish_sync():
                try:
                    self._loading_ring.visible = False
                    self._loading_status.value = "已同步"
                    self._loading_status.color = ft.colors.GREEN
                    self.page.update()
                except:
                    pass
                self._render_email_items()
            self.page.run_thread(finish_sync)
        except Exception as e:
            self._cloud_emails_cache = []
            def finish_sync_err():
                try:
                    self._loading_ring.visible = False
                    self._loading_status.value = "同步失败"
                    self._loading_status.color = ft.colors.RED
                    self.page.update()
                except:
                    pass
                self._render_email_items()
            self.page.run_thread(finish_sync_err)
            pass
        # 同步完成后，后台获取每个邮箱的真实邮件数量（不阻塞UI）
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
                    ft.Text("点击右上角加号创建临时邮箱", size=13, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.alignment.center,
                height=400,
            ))
            try:
                self.page.update()
            except:
                pass
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
        # 刷新页面，确保列表显示
        try:
            self.page.update()
        except:
            pass

    def _start_countdown(self):
        """启动实时倒计时（每10秒刷新一次，避免UI闪烁）"""
        if self._countdown_running:
            return
        self._countdown_running = True
        self._on_email_page = True
        def countdown_loop():
            while self._countdown_running and self._on_email_page:
                try:
                    time.sleep(10)
                    if not self._countdown_running or not self._on_email_page:
                        break
                    # 只有存在非永久邮箱时才刷新，避免不必要的重绘
                    emails = getattr(self, '_cloud_emails_cache', [])
                    has_expiring = any(not em.get("is_permanent", False) for em in emails)
                    if has_expiring:
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
            {"name": "mail.tm 邮箱", "domain": "emalupe.com", "icon_file": "mailtm_icon.png", "real": True, "provider": "mailtm"},
            {"name": "Guerrilla 邮箱", "domain": "guerrillamailblock.com", "icon_file": "", "real": True, "provider": "guerrilla"},
            {"name": "maildrop 邮箱", "domain": "maildrop.cc", "icon_file": "", "real": True, "provider": "maildrop"},
            {"name": "Gmail 邮箱", "domain": "gmail.com", "icon_file": "gmail_icon.png", "real": True, "provider": "gmail"},
        ]
        type_buttons = []
        for et in email_types:
            # 所有邮箱类型都用官方图标图片（尝试多种路径确保移动端兼容）
            if et.get("icon_file"):
                icon_path = et["icon_file"]
                candidate_paths = [
                    os.path.join(_base_dir, "assets", et["icon_file"]),
                    os.path.join(os.getcwd(), "assets", et["icon_file"]),
                    "assets/" + et["icon_file"],
                    et["icon_file"],
                ]
                for p in candidate_paths:
                    if os.path.exists(p):
                        icon_path = p
                        break
                icon_widget = ft.Container(
                    content=ft.Image(src=icon_path, width=36, height=36, fit=ft.ImageFit.COVER),
                    width=36, height=36, border_radius=10, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    alignment=ft.alignment.center,
                )
            else:
                # 没有图标文件的用默认邮件图标
                icon_widget = ft.Container(
                    content=ft.Icon(ft.icons.EMAIL, size=16, color=ft.colors.WHITE),
                    width=28, height=28, bgcolor=THEME_COLOR, border_radius=8,
                    alignment=ft.alignment.center,
                )
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
        """显示有效期选择（根据用户权限判断可选范围）"""
        duration_options = [
            {"name": "1小时", "hours": 1, "icon": "⏱️"},
            {"name": "2小时", "hours": 2, "icon": "⏰"},
            {"name": "永久", "hours": -1, "icon": "♾️"},
        ]
        # 判断用户权限：管理员全部可用；普通用户检查后台开通的权限字段
        is_admin = False
        can_2h = False
        can_permanent = False
        if self.current_user:
            user_role = str(self.current_user.get("role", ""))
            is_admin = user_role in ["超级管理员", "管理员", "admin", "Admin", "超级管理"]
            # 检查后台权限字段（支持多种字段名）
            can_2h = is_admin or bool(self.current_user.get("email_2h_enabled", 
                self.current_user.get("can_2h_email", self.current_user.get("duration_2h", False))))
            can_permanent = is_admin or bool(self.current_user.get("email_permanent_enabled", 
                self.current_user.get("can_permanent_email", self.current_user.get("duration_permanent", False))))
        dur_buttons = []
        for d in duration_options:
            # 判断该时长是否有权限
            if d["hours"] == 1:
                can_select = True  # 1小时所有用户都可用
            elif d["hours"] == 2:
                can_select = can_2h
            elif d["hours"] == -1:
                can_select = can_permanent
            else:
                can_select = False
            if can_select:
                # 有权限：正常显示
                dur_buttons.append(ft.Container(
                    content=ft.Row([
                        ft.Text(d["icon"], size=24),
                        ft.Container(width=12),
                        ft.Text(d["name"], size=16, weight=ft.FontWeight.W_500, expand=True,
                            color=self.clr_text),
                        ft.Container(content=ft.Text("默认", size=10, color=ft.colors.WHITE),
                            bgcolor=THEME_COLOR, border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            alignment=ft.alignment.center) if d["hours"] == 1 else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.START),
                    bgcolor=self.clr_card, border_radius=12, padding=16,
                    margin=ft.margin.only(0, 4, 0, 4),
                    border=ft.border.all(2, THEME_COLOR) if d["hours"] == 1 else ft.border.all(1, self.clr_border),
                    on_click=lambda e, dur=d: self._select_email_duration(dur),
                ))
            else:
                # 无权限：灰色显示，点击提示联系管理员
                dur_buttons.append(ft.Container(
                    content=ft.Row([
                        ft.Text(d["icon"], size=24, color=ft.colors.GREY_400),
                        ft.Container(width=12),
                        ft.Text(d["name"], size=16, weight=ft.FontWeight.W_500, expand=True,
                            color=ft.colors.GREY_400),
                        ft.Container(content=ft.Text("无权限", size=9, color=ft.colors.GREY_400),
                            bgcolor=ft.colors.GREY_200, border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            alignment=ft.alignment.center),
                    ], alignment=ft.MainAxisAlignment.START),
                    bgcolor=ft.colors.GREY_100, border_radius=12, padding=16,
                    margin=ft.margin.only(0, 4, 0, 4),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    on_click=lambda e: self._show_toast("该有效期无使用权限，请联系管理员开通"),
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
                # 保存到云端，完成后刷新列表确保新邮箱显示
                def save_and_reload():
                    self._save_email_to_cloud(new_email)
                    time.sleep(0.5)
                    self._sync_emails_from_cloud()
                    # 保存同步完成后再刷新一次UI，确保新邮箱显示
                    self.page.run_thread(self.render_email_list)
                threading.Thread(target=save_and_reload, daemon=True).start()
                self.page.run_thread(self._close_loading_dialog)
                # 先乐观显示新邮箱（立即添加到列表），避免闪一下就没了
                try:
                    if not hasattr(self, '_email_list') or self._email_list is None:
                        self._email_list = []
                    self._email_list.insert(0, new_email)
                except:
                    pass
                self.page.run_thread(self.render_email_list)
            elif provider == "mailtm":
                # mail.tm API，传入用户选择的域名
                ok, result = mailtm_create(domain=domain)
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
                    # 保存到云端，完成后刷新列表确保新邮箱显示
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                        # 保存同步完成后再刷新一次UI，确保新邮箱显示
                        self.page.run_thread(self.render_email_list)
                    threading.Thread(target=save_and_reload, daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    # 先乐观显示新邮箱（立即添加到列表），避免闪一下就没了
                    try:
                        if not hasattr(self, '_email_list') or self._email_list is None:
                            self._email_list = []
                        self._email_list.insert(0, new_email)
                    except:
                        pass
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
                    # 保存到云端，完成后刷新列表确保新邮箱显示
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                        # 保存同步完成后再刷新一次UI，确保新邮箱显示
                        self.page.run_thread(self.render_email_list)
                    threading.Thread(target=save_and_reload, daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    # 先乐观显示新邮箱（立即添加到列表），避免闪一下就没了
                    try:
                        if not hasattr(self, '_email_list') or self._email_list is None:
                            self._email_list = []
                        self._email_list.insert(0, new_email)
                    except:
                        pass
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
                    # 保存到云端，完成后刷新列表确保新邮箱显示
                    def save_and_reload():
                        self._save_email_to_cloud(new_email)
                        time.sleep(0.5)
                        self._sync_emails_from_cloud()
                        # 保存同步完成后再刷新一次UI，确保新邮箱显示
                        self.page.run_thread(self.render_email_list)
                    threading.Thread(target=save_and_reload, daemon=True).start()
                    self.page.run_thread(self._close_loading_dialog)
                    # 先乐观显示新邮箱（立即添加到列表），避免闪一下就没了
                    try:
                        if not hasattr(self, '_email_list') or self._email_list is None:
                            self._email_list = []
                        self._email_list.insert(0, new_email)
                    except:
                        pass
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
        # 先从缓存中移除，立即更新UI（不重新同步，不显示加载状态）
        if email_to_delete:
            self._cloud_emails_cache = [e for e in cloud_emails if e.get("id") != email_id and e.get("cloud_id") != email_id]
            self._render_email_items()
            # 后台从云端删除（不阻塞UI）
            cloud_id = email_to_delete.get("cloud_id", email_to_delete.get("id", ""))
            if cloud_id:
                def do_delete():
                    self._delete_email_from_cloud(cloud_id)
                threading.Thread(target=do_delete, daemon=True).start()
        # 右下角浮动提示（小卡片，不占满底部宽度）
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, size=18, color=ft.colors.GREEN),
                ft.Container(width=8),
                ft.Text("已删除邮箱", size=14, color=ft.colors.WHITE),
            ], spacing=0),
            duration=2000,
            behavior=ft.SnackBarBehavior.FLOATING,
            bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
            margin=ft.margin.only(20, 0, 20, 20),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        self.page.snack_bar.open = True
        self.page.update()

    # ========== 收件箱页面 ==========
    def _back_to_email_list(self):
        """返回邮箱列表，停止自动刷新"""
        self._stop_inbox_auto_refresh()
        self._show_navbar()  # 返回主页面显示导航栏
        self.render_email_list()

    def show_inbox(self, email):
        self.current_email = email
        self._hide_navbar()  # 进入收件箱隐藏导航栏
        self.content.controls.clear()
        # 顶部栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, icon_color=self.clr_text, on_click=lambda e: self._back_to_email_list()),
                ft.Text("收件箱", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text, expand=True),
                ft.IconButton(ft.icons.REFRESH, icon_size=22, icon_color=self.clr_text, on_click=lambda e: self.refresh_inbox()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text(email.get("address", ""), size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 0, 20, 10),
            bgcolor=self.clr_bg,
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
                            if isinstance(result, dict):
                                messages = result.get("hydra:member", [])
                            elif isinstance(result, list):
                                messages = result
                            else:
                                messages = []
                        else:
                            self.page.run_thread(lambda: self._show_inbox_error(str(result)))
                            return
                    else:
                        self.page.run_thread(lambda: self._show_inbox_error("邮箱token为空，无法获取邮件"))
                        return
                elif provider_lower in ["guerrilla", "guerrillamail", "guerrilla_mail"]:
                    token = email.get("token", "")
                    addr = email.get("address", "")
                    login = email.get("login", addr.split("@")[0] if "@" in addr else "")
                    # 先用现有token获取邮件
                    if token:
                        ok, messages = guerrilla_get_messages(token)
                        if ok:
                            # 成功，继续
                            pass
                        else:
                            # token失效，用邮箱用户名重新建立会话
                            if login:
                                ok2, new_token, new_addr = guerrilla_set_email_user(login)
                                if ok2 and new_token:
                                    email["token"] = new_token
                                    token = new_token
                                    # 同步更新云端缓存中的token
                                    try:
                                        for em in getattr(self, '_cloud_emails_cache', []):
                                            if em.get("id") == email.get("id") or em.get("address") == addr:
                                                em["token"] = new_token
                                                break
                                    except:
                                        pass
                                    ok, messages = guerrilla_get_messages(token)
                                    if not ok:
                                        self.page.run_thread(lambda: self._show_inbox_error("获取邮件失败，请重试"))
                                        return
                                else:
                                    self.page.run_thread(lambda: self._show_inbox_error("邮箱会话已失效，请删除后重新创建"))
                                    return
                            else:
                                self.page.run_thread(lambda: self._show_inbox_error("邮箱信息不完整，请重新创建"))
                                return
                    else:
                        # token为空，尝试用邮箱用户名建立会话
                        if login:
                            ok2, new_token, new_addr = guerrilla_set_email_user(login)
                            if ok2 and new_token:
                                email["token"] = new_token
                                token = new_token
                                ok, messages = guerrilla_get_messages(token)
                                if not ok:
                                    self.page.run_thread(lambda: self._show_inbox_error("获取邮件失败，请重试"))
                                    return
                            else:
                                self.page.run_thread(lambda: self._show_inbox_error("无法建立邮箱会话，请重新创建"))
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

            # 安全检查：确保messages是列表
            if not isinstance(messages, list):
                messages = []
            # Guerrilla Mail自动删除欢迎邮件
            provider_lower = str(provider).lower()
            if provider_lower in ["guerrilla", "guerrillamail", "guerrilla_mail"] and messages:
                token = email.get("token", "")
                welcome_ids = []
                for m in messages:
                    subj = str(m.get("mail_subject", m.get("subject", "")))
                    sender = str(m.get("mail_from", m.get("from", "")))
                    if "Welcome to Guerrilla Mail" in subj or "no-reply@guerrillamail.com" in sender:
                        mid = m.get("mail_id", m.get("id", ""))
                        if mid:
                            welcome_ids.append(mid)
                # 从列表中移除欢迎邮件
                if welcome_ids:
                    messages = [m for m in messages if m.get("mail_id", m.get("id", "")) not in welcome_ids]
                    # 后台删除服务器上的欢迎邮件
                    if token:
                        for wid in welcome_ids:
                            try:
                                guerrilla_delete_email(token, wid)
                            except:
                                pass
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
        # 安全检查
        if not isinstance(messages, list):
            messages = []
        if not messages:
            empty_icon_path = self._get_empty_email_icon_path()
            self._inbox_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Image(src=empty_icon_path, width=80, height=80, fit=ft.ImageFit.CONTAIN),
                    ft.Text("暂无邮件", size=16, color=self.clr_text2),
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
                            ft.Text(str(sender), size=14, weight=ft.FontWeight.W_500, color=self.clr_text, expand=True),
                            ft.Text(str(date)[5:16] if len(str(date)) > 16 else str(date), size=11, color=self.clr_text2),
                        ]),
                        ft.Text(str(subject), size=13, color=self.clr_text2, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=4),
                    bgcolor=self.clr_card, border_radius=10, padding=14,
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
        # 兼容不同邮箱类型的ID字段（Guerrilla Mail用mail_id，其他用id）
        msg_id = msg.get("id", msg.get("mail_id", ""))

        self._hide_navbar()  # 进入邮件详情隐藏导航栏
        self.content.controls.clear()
        # 顶部固定栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, icon_color=self.clr_text, on_click=lambda e: self.show_inbox(email)),
                ft.Text("邮件详情", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text, expand=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(10, 45, 10, 5),
            bgcolor=self.clr_bg,
        ))
        # 分隔线
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))
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
        # 安全检查：detail必须是字典，否则显示错误
        if not isinstance(detail, dict):
            self._detail_content.controls.append(ft.Text("邮件内容格式异常，无法显示", size=14, color=self.clr_text2))
            self.page.update()
            return
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
            raw_data = detail.get("data", "")
            # maildrop的data字段是原始邮件源码，需要解析出正文
            if raw_data and isinstance(raw_data, str) and ("Received:" in raw_data or "DKIM-Signature:" in raw_data or "Content-Type:" in raw_data):
                try:
                    import email as email_mod
                    from email.header import decode_header
                    msg_obj = email_mod.message_from_string(raw_data)
                    # 解析主题
                    if not subject or subject == "(无主题)":
                        subj_raw = msg_obj.get("Subject", "")
                        if subj_raw:
                            decoded_parts = decode_header(subj_raw)
                            subject = ""
                            for part, enc in decoded_parts:
                                if isinstance(part, bytes):
                                    subject += part.decode(enc or "utf-8", errors="replace")
                                else:
                                    subject += part
                    # 解析发件人
                    if not sender or sender == "未知":
                        from_raw = msg_obj.get("From", "")
                        if from_raw:
                            decoded_parts = decode_header(from_raw)
                            sender = ""
                            for part, enc in decoded_parts:
                                if isinstance(part, bytes):
                                    sender += part.decode(enc or "utf-8", errors="replace")
                                else:
                                    sender += part
                    # 解析正文
                    body = ""
                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            ctype = part.get_content_type()
                            cdisp = str(part.get("Content-Disposition", ""))
                            if ctype == "text/plain" and "attachment" not in cdisp:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    charset = part.get_content_charset() or "utf-8"
                                    body = payload.decode(charset, errors="replace")
                                    break
                        if not body:
                            for part in msg_obj.walk():
                                ctype = part.get_content_type()
                                if ctype == "text/html":
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        charset = part.get_content_charset() or "utf-8"
                                        body = payload.decode(charset, errors="replace")
                                        break
                    else:
                        payload = msg_obj.get_payload(decode=True)
                        if payload:
                            charset = msg_obj.get_content_charset() or "utf-8"
                            body = payload.decode(charset, errors="replace")
                    if not body:
                        body = detail.get("body", "(无内容)")
                except Exception:
                    body = detail.get("body", str(raw_data)[:500] if raw_data else "(无内容)")
            else:
                body = detail.get("body", "(无内容)")

        # 去除HTML标签
        if "<" in str(body) and ">" in str(body):
            import re
            body = re.sub(r'<[^>]+>', '', str(body))
        self._detail_content.controls.clear()
        self._detail_content.controls.append(ft.Text(str(subject), size=18, weight=ft.FontWeight.BOLD, color=self.clr_text))
        self._detail_content.controls.append(ft.Container(height=8))
        self._detail_content.controls.append(ft.Text("发件人：" + str(sender), size=13, color=self.clr_text2))
        self._detail_content.controls.append(ft.Text("时间：" + str(date), size=13, color=self.clr_text2))
        self._detail_content.controls.append(ft.Container(height=12))
        self._detail_content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))
        self._detail_content.controls.append(ft.Container(height=12))
        self._detail_content.controls.append(ft.Text(str(body), size=14, color=self.clr_text))
        self.page.update()

    def _show_detail_error(self, err):
        self._detail_content.controls.clear()
        self._detail_content.controls.append(ft.Text("加载失败：" + err[:50], size=14, color=ft.colors.RED))
        self.page.update()

    # ========== 号码页面 ==========
    def render_channel_page(self):
        """频道列表页面"""
        self._stop_channel_polling()
        self._show_navbar()  # 主页面显示导航栏
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("频道", size=28, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ]),
            padding=ft.padding.only(20, 50, 20, 10),
        ))
        self.content.controls.append(ft.Container(
            content=ft.Text("加入频道，和大家一起交流", size=13, color=self.clr_text2),
            padding=ft.padding.only(20, 0, 20, 10),
        ))

        # 管理员/超级管理员专属：管理卡片（在线人数、用户管理、黑名单）
        # ---- 第一行卡片（所有人可见）：公告、暂存、暂存 ----
        announce_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.icons.CAMPAIGN, size=24, color=ft.colors.ORANGE),
                    width=44, height=44, bgcolor=ft.colors.ORANGE_50,
                    border_radius=22, alignment=ft.alignment.center,
                ),
                ft.Container(height=8),
                ft.Text("公告", size=12, color=self.clr_text2),
                ft.Text("公告", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
            on_click=lambda e: self._show_remote_announcement(),
        )
        placeholder1_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.icons.MORE_HORIZ, size=24, color=ft.colors.GREY_500),
                    width=44, height=44, bgcolor=ft.colors.GREY_100,
                    border_radius=22, alignment=ft.alignment.center,
                ),
                ft.Container(height=8),
                ft.Text("敬请期待", size=12, color=self.clr_text2),
                ft.Text("暂存", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
        )
        placeholder2_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.icons.MORE_HORIZ, size=24, color=ft.colors.GREY_500),
                    width=44, height=44, bgcolor=ft.colors.GREY_100,
                    border_radius=22, alignment=ft.alignment.center,
                ),
                ft.Container(height=8),
                ft.Text("敬请期待", size=12, color=self.clr_text2),
                ft.Text("暂存", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            expand=True, bgcolor=self.clr_card, border_radius=12, padding=14,
        )
        self.content.controls.append(ft.Container(
            content=ft.Row([announce_card, placeholder1_card, placeholder2_card], spacing=10),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.content.controls.append(ft.Container(height=10))

        # ---- 第二行卡片（仅管理员可见）：在线人数、用户管理、黑名单 ----
        if self.current_user:
            user_role = str(self.current_user.get("role", ""))
            is_admin = user_role in ["超级管理员", "管理员", "admin", "Admin", "超级管理", "频道主"]
            if is_admin:
                _cached_online = getattr(self, '_cached_online_count', None)
                self._online_count_text = ft.Text(str(_cached_online) if _cached_online is not None else "--", size=20, weight=ft.FontWeight.BOLD, color=self.clr_text)
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
                )
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
                if getattr(self, "_cached_online_count", None) is None:
                    threading.Thread(target=self._fetch_online_count, daemon=True).start()

        # ---- 频道列表（所有人可见） ----
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=THEME_COLOR, border_radius=2),
                ft.Container(width=6),
                ft.Text("频道列表", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 8, 20, 6),
        ))

        self._channel_list = ft.ListView([], spacing=0, expand=True, padding=16)
        self.content.controls.append(self._channel_list)
        self.page.update()
        # 加载频道列表（API待对接）
        self._load_channels()


    def _show_remote_announcement(self):
        """从网站获取并显示远程公告"""
        def fetch_and_show():
            try:
                # 从远程配置获取公告
                notice = None
                if hasattr(self, '_remote_config') and self._remote_config:
                    notice = self._remote_config.get("notice")
                # 如果缓存没有，重新获取配置
                if not notice:
                    ok, result = self._remote_api_request("GET", "config")
                    if ok and isinstance(result, dict) and result.get("ok"):
                        data = result.get("data", {})
                        notice = data.get("notice")
                        self._remote_config = data
                if notice and isinstance(notice, dict):
                    title = notice.get("title", "公告")
                    body = notice.get("content", "")
                    if body:
                        self.page.run_thread(lambda: self._show_announcement(title, body))
                        return
                self.page.run_thread(lambda: self._show_toast("暂无公告", "info"))
            except Exception as e:
                self.page.run_thread(lambda: self._show_toast("获取公告失败", "error"))
        threading.Thread(target=fetch_and_show, daemon=True).start()

    def _fetch_online_count(self):
        """获取用户总数（异步，用users/count接口，管理员权限）"""
        try:
            operator_id = self.current_user.get("id", "") if self.current_user else ""
            ok, result = self._remote_api_request("GET", "users/count",
                params={"operator_id": operator_id})
            count = 0
            if ok and isinstance(result, dict) and result.get("ok"):
                data = result.get("data", {})
                if isinstance(data, dict):
                    count = data.get("total", 0)
            # 更新显示
            def update_count():
                try:
                    if hasattr(self, '_online_count_text') and self._online_count_text:
                        self._online_count_text.value = str(count)
                        self._cached_online_count = count
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
            {"id": "1", "name": "高级会议", "desc": "高级会员专属交流频道", "icon": "🎯", "members": 0},
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

        self._hide_navbar()  # 进入用户管理隐藏导航栏
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

        self._hide_navbar()  # 进入黑名单隐藏导航栏
        self.content.controls.clear()
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
                params={"operator_id": operator_id})
            banned = 0
            blacklist_error = ""
            if count_ok and isinstance(count_result, dict) and count_result.get("ok"):
                data = count_result.get("data", {})
                banned = data.get("banned", 0)
            elif isinstance(count_result, dict):
                blacklist_error = count_result.get("msg", "获取失败")

            # 获取已封禁用户列表（用status=banned筛选）
            list_ok, list_result = self._remote_api_request("GET", "users",
                params={"operator_id": operator_id, "page": 1, "page_size": 100, "status": "banned"})

            users = []
            if list_ok and isinstance(list_result, dict) and list_result.get("ok"):
                data = list_result.get("data", {})
                users = data.get("users", [])

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
                    ft.Row([unban_btn], spacing=4, alignment=ft.MainAxisAlignment.END),
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
                params={"operator_id": operator_id})
            total = active = banned = 0
            count_error = ""
            if count_ok and isinstance(count_result, dict) and count_result.get("ok"):
                data = count_result.get("data", {})
                total = data.get("total", 0)
                active = data.get("active", 0)
                banned = data.get("banned", 0)
            elif isinstance(count_result, dict):
                count_error = count_result.get("msg", "获取用户数失败")

            # 获取用户列表
            list_ok, list_result = self._remote_api_request("GET", "users",
                params={"operator_id": operator_id, "page": 1, "page_size": 100, "status": "all"})

            users = []
            list_error = ""
            if list_ok and isinstance(list_result, dict) and list_result.get("ok"):
                data = list_result.get("data", {})
                users = data.get("users", [])
            elif isinstance(list_result, dict):
                list_error = list_result.get("msg", "获取用户列表失败")

            # 更新UI
            def update_ui():
                # 更新统计信息
                if count_error:
                    self._user_stats_text.value = f"加载失败: {count_error}"
                else:
                    self._user_stats_text.value = f"共 {total} 个用户 | 正常 {active} | 已封禁 {banned}"
                # 渲染用户列表
                self._render_user_list(users)
                # 如果有错误且用户列表为空，显示错误提示
                if list_error and not users:
                    self._user_list_container.controls.clear()
                    self._user_list_container.controls.append(ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.RED_300),
                            ft.Container(height=12),
                            ft.Text("加载失败", size=16, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Container(height=4),
                            ft.Text(list_error, size=13, color=self.clr_text2, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.Text("请确认当前账号在网站后台有管理员权限", size=11, color=ft.colors.GREY_500),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(0, 60, 0, 0),
                    ))
                self.page.update()

            self.page.run_thread(update_ui)
        except Exception as e:
            self.page.run_thread(lambda: self._show_toast(f"加载失败: {str(e)[:30]}"))

    def _render_user_list(self, users):
        """渲染用户列表（自己的卡片排第一，左上角显示"本人"标签）"""
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

        # 把自己的用户移到列表第一个
        self_user = None
        other_users = []
        for user in users:
            if str(user.get("user_id", "")) == str(current_user_id):
                self_user = user
            else:
                other_users.append(user)
        sorted_users = ([self_user] if self_user else []) + other_users

        for user in sorted_users:
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

            # 本人标签（在卡片外定义）
            _self_badge = ft.Container()
            if is_self:
                _self_badge = ft.Container(content=ft.Text("本人", size=9, color=ft.colors.WHITE),
                    bgcolor=ft.colors.BLUE, border_radius=4,
                    padding=ft.padding.symmetric(horizontal=5, vertical=1),
                    alignment=ft.alignment.center)

            # 用户卡片
            user_card = ft.Container(
                content=ft.Column([
                    # 第一行：本人标签 + 用户名 + 角色 + 状态
                    ft.Row([
                        _self_badge,
                        ft.Container(width=4) if is_self else ft.Container(),
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

        # 根据是否是自己，显示不同的编辑字段
        if is_self:
            # 编辑自己：只能改昵称、邮箱、QQ号
            name_field = ft.TextField(label="昵称", value=name, width=300, border_radius=8)
            email_field = ft.TextField(label="邮箱", value=email, width=300, border_radius=8)
            qq_field = ft.TextField(label="QQ号", value=qq, width=300, border_radius=8)
            username_field = None
            role_field = None
            duration_perm_container = ft.Container()
        else:
            # 编辑其他用户：可以改昵称、邮箱、QQ号、角色
            name_field = ft.TextField(label="昵称", value=name, width=300, border_radius=8)
            username_field = None

        # 角色下拉框：只有编辑其他用户时才显示（编辑自己不显示）
        if not is_self:
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
                role_field = ft.Dropdown(
                    label="角色（可提升为管理员）",
                    value=role,
                    options=[
                        ft.dropdown.Option("用户"),
                        ft.dropdown.Option("管理员"),
                    ],
                    width=300, border_radius=8,
                )
        else:
            role_field = None

        # 编辑其他用户时显示邮箱和QQ号输入框
        if not is_self:
            email_field = ft.TextField(label="邮箱", value=email, width=300, border_radius=8)
            qq_field = ft.TextField(label="QQ号", value=qq, width=300, border_radius=8)

        def do_save(e):
            self._close_dialog()
            self._show_toast("正在保存...")
            def save_thread():
                try:
                    operator_id = self.current_user.get("id", "")
                    body = {
                        "name": name_field.value,
                        "operator_id": operator_id,
                    }
                    # 编辑自己：可以改邮箱和QQ号
                    if is_self:
                        if email_field:
                            body["email"] = email_field.value
                        if qq_field:
                            body["qq"] = qq_field.value
                    else:
                        # 编辑其他用户：可以改邮箱、QQ号、角色
                        if email_field:
                            body["email"] = email_field.value
                        if qq_field:
                            body["qq"] = qq_field.value
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
            title=ft.Text(f"编辑{'自己' if is_self else '用户'} - {name or username}"),
            content=ft.Column(
                ([name_field, email_field, qq_field] if is_self else
                 [name_field, email_field, qq_field] + ([role_field] if isinstance(role_field, ft.Dropdown) else [])),
                tight=True, spacing=10),
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

    def _show_channel_info(self):
        """显示群信息对话框（群头像、群名称、群ID、我的群昵称）"""
        if not self.current_channel:
            return
        channel = self.current_channel
        channel_name = channel.get("name", "高级会议")
        channel_id = channel.get("id", "1")
        channel_icon = channel.get("icon", "🎯")
        # 我的群昵称（优先用本地设置的群昵称，否则用用户昵称）
        my_nickname = getattr(self, '_channel_nickname', "")
        if not my_nickname:
            my_nickname = self.current_user.get("name", self.current_user.get("username", "")) if self.current_user else ""
        # 判断是否超级管理员
        user_role = str(self.current_user.get("role", "")) if self.current_user else ""
        is_super_admin = user_role in ["超级管理员", "super_admin", "SuperAdmin"]

        # 群头像
        group_avatar = ft.Container(
            content=ft.Text(channel_icon, size=40),
            width=80, height=80,
            bgcolor=ft.colors.with_opacity(0.15, THEME_COLOR),
            border_radius=40, alignment=ft.alignment.center,
        )

        # 群名称行（超级管理员可点击修改）
        def edit_group_name(e):
            self._close_dialog()
            self._show_edit_group_name_dialog(channel_name)
        group_name_row = ft.Row([
            ft.Text("群名称", size=14, color=ft.colors.GREY_600, width=70),
            ft.Text(channel_name, size=15, weight=ft.FontWeight.W_500, expand=True),
            ft.IconButton(ft.icons.EDIT, icon_size=18, on_click=edit_group_name, visible=is_super_admin),
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # 群ID行
        group_id_row = ft.Row([
            ft.Text("群ID", size=14, color=ft.colors.GREY_600, width=70),
            ft.Text(channel_id, size=15, expand=True),
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # 我的群昵称行（可点击修改）
        def edit_my_nickname(e):
            self._close_dialog()
            self._show_edit_channel_nickname_dialog(my_nickname)
        my_nickname_row = ft.Row([
            ft.Text("我的昵称", size=14, color=ft.colors.GREY_600, width=70),
            ft.Text(my_nickname or "未设置", size=15, expand=True),
            ft.IconButton(ft.icons.EDIT, icon_size=18, on_click=edit_my_nickname),
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # 成员数量行
        members_count = channel.get("members", 512)
        members_row = ft.Row([
            ft.Text("成员数", size=14, color=ft.colors.GREY_600, width=70),
            ft.Text(str(members_count), size=15, expand=True),
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.dialog = ft.AlertDialog(
            title=ft.Row([
                group_avatar,
                ft.Container(width=12),
                ft.Column([
                    ft.Text(channel_name, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"ID: {channel_id}", size=12, color=ft.colors.GREY_500),
                ], spacing=2),
            ], spacing=0),
            content=ft.Column([
                ft.Container(height=8),
                group_name_row,
                ft.Container(height=4),
                group_id_row,
                ft.Container(height=4),
                my_nickname_row,
                ft.Container(height=4),
                members_row,
            ], spacing=0, tight=True, width=320),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _show_edit_group_name_dialog(self, current_name):
        """修改群名称对话框（仅超级管理员可用）"""
        name_input = ft.TextField(label="新群名称", value=current_name, width=300, border_radius=8)
        def confirm(e):
            new_name = name_input.value.strip()
            if not new_name:
                return
            # 更新频道名称
            if self.current_channel:
                self.current_channel["name"] = new_name
            # 更新本地频道列表缓存
            if hasattr(self, '_channels_cache'):
                for ch in self._channels_cache:
                    if ch.get("id") == self.current_channel.get("id"):
                        ch["name"] = new_name
            self._close_dialog()
            self._show_toast("群名称已修改")
            # 重新进入聊天页更新标题
            self.show_channel_chat(self.current_channel)
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("修改群名称", size=18, weight=ft.FontWeight.BOLD),
            content=name_input,
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("确定", on_click=confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _show_edit_channel_nickname_dialog(self, current_nickname):
        """修改我的群昵称对话框"""
        nick_input = ft.TextField(label="我的群昵称", value=current_nickname, width=300, border_radius=8)
        def confirm(e):
            new_nick = nick_input.value.strip()
            if not new_nick:
                return
            # 保存到本地
            self._channel_nickname = new_nick
            self.data["channel_nickname"] = new_nick
            save_data(self.data)
            self._close_dialog()
            self._show_toast("群昵称已修改")
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("修改我的群昵称", size=18, weight=ft.FontWeight.BOLD),
            content=nick_input,
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_dialog()),
                ft.TextButton("确定", on_click=confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def show_channel_chat(self, channel):
        """频道聊天页面"""
        self.current_channel = channel
        # 加载本地群昵称
        if not hasattr(self, '_channel_nickname') or not self._channel_nickname:
            self._channel_nickname = self.data.get("channel_nickname", "")
        self._hide_navbar()  # 进入聊天页面隐藏导航栏
        self.content.controls.clear()
        self.content.scroll = None  # 关闭整体滚动，确保布局稳定
        # 成员数量文本（从API获取实际数量）
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
        # 消息列表（初始：有缓存显示缓存，没缓存显示加载中）
        _has_cache = hasattr(self, '_cached_channel_messages') and self._cached_channel_messages
        if _has_cache:
            self._chat_message_list = ft.ListView([], spacing=8, expand=True, padding=16, auto_scroll=True)
        else:
            # 第一次打开，显示加载中
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
                    ft.IconButton(ft.icons.MENU, icon_size=24, on_click=lambda e: self._show_channel_info()),
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
        # 成员数量：用 users/count API 获取真实用户总数，消息统计作为兜底
        def load_members_count():
            try:
                api_count = 0
                # 用当前用户ID作为operator_id调用 users/count（管理员可获取全部用户数）
                if self.current_user:
                    operator_id = self.current_user.get("id", "")
                    if operator_id:
                        ok, result = self._remote_api_request(
                            "GET", f"users/count?operator_id={operator_id}", body={}, get_with_body=False
                        )
                        if ok and isinstance(result, dict) and result.get("ok"):
                            data = result.get("data", {})
                            if isinstance(data, dict):
                                api_count = data.get("total", 0)
                # 如果API没拿到（非管理员），从消息统计
                if api_count <= 0:
                    self._update_channel_member_count()
                    return
                # 更新显示
                def update_text():
                    if hasattr(self, '_channel_members_text') and self._channel_members_text:
                        self._channel_members_text.value = f"{api_count} 成员"
                        self.page.update()
                self.page.run_thread(update_text)
            except Exception:
                # 出错时从消息统计兜底
                try:
                    self._update_channel_member_count()
                except Exception:
                    pass
        threading.Thread(target=load_members_count, daemon=True).start()
        # 消息加载逻辑：有缓存直接显示+后台增量加载；没缓存后台加载全部（加载中已显示）
        if hasattr(self, '_cached_channel_messages') and self._cached_channel_messages:
            # 直接显示缓存的消息，不显示加载中
            self._render_chat_messages(self._cached_channel_messages)
            # 后台获取最新消息（增量更新，在已加载基础上追加新消息）
            threading.Thread(target=self._poll_new_channel_messages, daemon=True).start()
        else:
            # 第一次进入，显示加载中，后台加载全部消息，加载完成后保存到本地缓存
            threading.Thread(target=self._load_channel_messages, daemon=True).start()
        # 启动后台实时轮询（每5秒获取最新消息）
        self._start_channel_polling()

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

    def _start_channel_polling(self):
        """启动频道消息实时轮询"""
        self._channel_polling_running = True
        def polling_loop():
            while getattr(self, '_channel_polling_running', False):
                time.sleep(5)
                if not getattr(self, '_channel_polling_running', False):
                    break
                try:
                    self.page.run_thread(self._poll_new_channel_messages)
                except:
                    pass
        threading.Thread(target=polling_loop, daemon=True).start()

    def _stop_channel_polling(self):
        """停止频道消息轮询"""
        self._channel_polling_running = False

    def _poll_new_channel_messages(self):
        """后台获取最新消息，增量更新（只追加新消息，不重新加载全部）"""
        try:
            cloud_messages = self._load_channel_messages_from_cloud()
            if not cloud_messages:
                return
            # 获取缓存中已有的消息ID集合
            cached_ids = set()
            cached_messages = getattr(self, '_cached_channel_messages', [])
            # 去掉发送中的临时消息（发送成功后服务器会返回真实消息）
            cached_messages = [m for m in cached_messages if not m.get('is_sending', False)]
            self._cached_channel_messages = cached_messages
            for msg in cached_messages:
                mid = str(msg.get("id", ""))
                if mid and mid != "0":
                    cached_ids.add(mid)
            # 找出新消息（不在缓存中的）
            new_cloud_messages = []
            for msg in cloud_messages:
                mid = str(msg.get("id", ""))
                if mid and mid not in cached_ids:
                    new_cloud_messages.append(msg)
            if not new_cloud_messages:
                return  # 没有新消息，不更新
            # 获取新消息用户的角色（优先用缓存的角色）
            user_roles = getattr(self, '_cached_user_roles', {})
            current_user = self.current_user or {}
            current_user_id = current_user.get("id", "")
            formatted_new = []
            for msg in new_cloud_messages:
                user_id = msg.get("user_id", "")
                username = msg.get("name", msg.get("username", "匿名"))
                # 优先用缓存的角色，没有则实时获取
                role = user_roles.get(str(user_id), msg.get("role", ""))
                if not role and str(user_id) not in user_roles:
                    try:
                        ok, result = self._remote_api_request("GET", "user-role", params={"user_id": user_id})
                        if ok and isinstance(result, dict) and result.get("ok"):
                            data = result.get("data", {})
                            if isinstance(data, dict):
                                role = data.get("chat_role", data.get("role", ""))
                                if role:
                                    user_roles[str(user_id)] = role
                    except:
                        pass
                is_me = str(user_id) == str(current_user_id)
                created_at = msg.get("created_at", "")
                time_str = ""
                if created_at:
                    try:
                        t = time.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                        time_str = time.strftime("%H:%M", t)
                    except:
                        time_str = created_at[11:16] if len(created_at) > 16 else created_at
                role_color = ft.colors.RED
                role_str = str(role) if role else ""
                if "频道主" in role_str or "主人" in role_str:
                    role_color = ft.colors.AMBER
                elif "管理员" in role_str:
                    role_color = ft.colors.PURPLE
                elif "运营" in role_str:
                    role_color = ft.colors.PINK
                elif "测试" in role_str:
                    role_color = ft.colors.BLUE
                formatted_new.append({
                    "id": str(msg.get("id", "")),
                    "user": username,
                    "content": msg.get("content", ""),
                    "time": time_str,
                    "role": role_str,
                    "role_color": role_color,
                    "is_me": is_me,
                    "is_system": False,
                })
            if not formatted_new:
                return
            # 追加到缓存并渲染
            if not hasattr(self, '_cached_channel_messages'):
                self._cached_channel_messages = []
            self._cached_channel_messages.extend(formatted_new)
            self._cached_user_roles = user_roles
            self._render_chat_messages(self._cached_channel_messages)
            self._update_channel_member_count()
        except Exception as e:
            pass

    def _update_channel_member_count(self):
        """从聊天消息中统计唯一用户数，更新左上角成员显示"""
        try:
            messages = getattr(self, '_cached_channel_messages', [])
            if not messages:
                return
            unique_users = set()
            for msg in messages:
                if msg.get("is_system"):
                    continue
                username = msg.get("user", "")
                if username and username != "系统":
                    unique_users.add(username)
            # 加上当前用户（如果还没发过言）
            if self.current_user:
                my_name = self.current_user.get("name", self.current_user.get("username", ""))
                if my_name:
                    unique_users.add(my_name)
            count = len(unique_users)
            # 至少显示1（当前用户）
            if count < 1:
                count = 1
            if hasattr(self, '_channel_members_text') and self._channel_members_text:
                self._channel_members_text.value = f"{count} 成员"
                self.page.update()
        except Exception:
            pass

    def _load_channel_messages(self):
        """加载频道消息列表（首次加载全部，后续用轮询增量更新）"""
        def load_thread():
            try:
                cloud_messages = self._load_channel_messages_from_cloud()
                if cloud_messages:
                    # 转换为应用内消息格式
                    current_user = self.current_user or {}
                    current_user_id = current_user.get("id", "")
                    # 获取用户角色（优先用缓存，缓存60秒，减少请求）
                    user_roles = getattr(self, '_cached_user_roles', {})
                    roles_cache_time = getattr(self, '_user_roles_cache_time', 0)
                    if time.time() - roles_cache_time > 60 or not user_roles:
                        user_roles = self._fetch_all_user_roles(cloud_messages)
                        self._cached_user_roles = user_roles
                        self._user_roles_cache_time = time.time()
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
                    # 从消息统计成员数
                    self.page.run_thread(self._update_channel_member_count)
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
                    ft.Text("", size=14),
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
                    role_color = msg.get("role_color")
                    if not role_color:
                        # 根据角色动态判断颜色（临时消息没有role_color时）
                        if role in ["频道主", "频道组"]:
                            role_color = ft.colors.AMBER
                        elif role in ["管理员", "admin", "Admin", "超级管理", "超级管理员", "运营"]:
                            role_color = ft.colors.PURPLE
                        elif role == "测试":
                            role_color = ft.colors.BLUE
                        else:
                            role_color = ft.colors.RED
                    # 名字和角色行（在气泡外面，昵称带颜色）
                    my_name_widget = self._get_colored_name_widget(username, size=11)
                    name_row = ft.Row([
                        ft.Container(width=40),
                        my_name_widget,
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
                    # 发送中：气泡前面显示加载图标；发送失败：显示红色感叹号
                    is_sending = msg.get("is_sending", False)
                    is_failed = msg.get("is_failed", False)
                    sending_icon = ft.Container()
                    if is_sending:
                        sending_icon = ft.Container(
                            content=ft.ProgressRing(width=14, height=14, color=ft.colors.WHITE, stroke_width=2),
                            padding=ft.padding.only(right=6),
                            alignment=ft.alignment.center,
                        )
                    elif is_failed:
                        sending_icon = ft.Container(
                            content=ft.Icon(ft.icons.ERROR_OUTLINE, size=14, color=ft.colors.RED),
                            padding=ft.padding.only(right=6),
                            alignment=ft.alignment.center,
                        )
                    bubble = ft.Container(
                        content=text_widget,
                        bgcolor=THEME_COLOR if not is_failed else ft.colors.GREY_400,
                        border_radius=12, padding=12,
                        on_long_press=lambda e, m=msg: self._show_chat_message_menu(m),
                    )
                    # 加载/失败图标放在气泡前面（外面）
                    _msg_row_controls = [ft.Container(width=40)]
                    if is_sending or is_failed:
                        _msg_row_controls.append(sending_icon)
                    _msg_row_controls.append(bubble)
                    self._chat_message_list.controls.append(ft.Container(
                        content=ft.Column([
                            name_row,
                            ft.Container(height=4),
                            ft.Row(_msg_row_controls, alignment=ft.MainAxisAlignment.END, spacing=6),
                            ft.Container(height=2),
                            ft.Text(msg.get("time", ""), size=10, color=self.clr_text2, text_align=ft.TextAlign.RIGHT),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                        alignment=ft.alignment.center_right,
                    ))
                else:
                    # 别人的消息靠左（名字和角色在气泡外面）
                    username = msg.get("user", "")
                    role = msg.get("role", "")
                    role_color = msg.get("role_color")
                    if not role_color:
                        # 根据角色动态判断颜色（临时消息没有role_color时）
                        if role in ["频道主", "频道组"]:
                            role_color = ft.colors.AMBER
                        elif role in ["管理员", "admin", "Admin", "超级管理", "超级管理员", "运营"]:
                            role_color = ft.colors.PURPLE
                        elif role == "测试":
                            role_color = ft.colors.BLUE
                        else:
                            role_color = ft.colors.RED
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
                        on_long_press=lambda e, m=msg: self._show_chat_message_menu(m),
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

    def _is_url(self, text):
        """判断文本是否是链接"""
        if not text:
            return False
        text = text.strip()
        return text.startswith("http://") or text.startswith("https://") or text.startswith("www.")

    def _open_chat_link(self, url):
        """打开消息中的链接"""
        try:
            import webbrowser
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            self._show_toast("正在打开链接...")
        except Exception as e:
            self._show_toast("打开链接失败：" + str(e)[:20])

    def _recall_chat_message(self, msg):
        """撤回消息（3分钟内，自己发的）"""
        try:
            msg_id = msg.get("id")
            if not msg_id:
                self._show_toast("撤回失败：缺少消息ID")
                return
            # 检查是否是自己发的消息
            msg_user_id = msg.get("user_id", "")
            current_user_id = self.current_user.get("id", "") if self.current_user else ""
            if str(msg_user_id) != str(current_user_id):
                self._show_toast("只能撤回自己的消息")
                return
            # 检查是否在3分钟内
            msg_time = msg.get("created_at", "")
            can_recall = True
            if msg_time:
                try:
                    from datetime import datetime, timedelta
                    # 尝试解析时间
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                        try:
                            msg_dt = datetime.strptime(msg_time, fmt)
                            if datetime.now() - msg_dt > timedelta(minutes=3):
                                can_recall = False
                            break
                        except:
                            continue
                except:
                    pass
            if not can_recall:
                self._show_toast("超过3分钟，无法撤回")
                return
            # 调用撤回API（待确认端点，先用常见格式）
            def do_recall():
                try:
                    # TODO: 确认撤回API端点，可能是 DELETE /chat/messages/{id} 或 POST /chat/messages/{id}/recall
                    ok, result = self._remote_api_request("DELETE", f"chat/messages/{msg_id}")
                    if ok and result and result.get("ok"):
                        # 撤回成功，从消息列表中移除
                        def remove_msg():
                            try:
                                for i, m in enumerate(self._chat_message_list.controls):
                                    # 简单匹配：通过消息内容和时间判断
                                    pass
                                # 重新加载消息
                                self._load_chat_messages()
                                self._show_toast("消息已撤回")
                            except:
                                self._show_toast("撤回成功")
                        self.page.run_thread(remove_msg)
                    else:
                        error_msg = result.get("msg", "撤回失败") if isinstance(result, dict) else "撤回失败"
                        self._show_toast(str(error_msg))
                except Exception as e:
                    self._show_toast("撤回失败：" + str(e)[:20])
            import threading
            threading.Thread(target=do_recall, daemon=True).start()
            self._show_toast("正在撤回...")
        except Exception as e:
            self._show_toast("撤回失败：" + str(e)[:20])

    def _show_chat_message_menu(self, msg):
        """长按消息弹出底部菜单（复制/打开链接/撤回）"""
        try:
            msg_content = msg.get("content", "")
            msg_id = msg.get("id")
            msg_user_id = msg.get("user_id", "")
            current_user_id = self.current_user.get("id", "") if self.current_user else ""
            is_own = str(msg_user_id) == str(current_user_id)
            
            # 构建菜单项
            menu_items = []
            
            # 复制
            menu_items.append(ft.ListTile(
                leading=ft.Icon(ft.icons.COPY_OUTLINED, color=self.clr_text),
                title=ft.Text("复制", size=15, color=self.clr_text),
                on_click=lambda e: self._close_bottom_sheet_and_copy(msg_content),
            ))
            
            # 打开链接（如果是链接）
            if self._is_url(msg_content):
                menu_items.append(ft.ListTile(
                    leading=ft.Icon(ft.icons.LINK_OUTLINED, color=self.clr_text),
                    title=ft.Text("打开链接", size=15, color=self.clr_text),
                    on_click=lambda e: self._close_bottom_sheet_and_open(msg_content),
                ))
            
            # 撤回（自己的消息）
            if is_own and msg_id:
                menu_items.append(ft.ListTile(
                    leading=ft.Icon(ft.icons.UNDO_OUTLINED, color=ft.colors.RED),
                    title=ft.Text("撤回", size=15, color=ft.colors.RED),
                    on_click=lambda e: self._close_bottom_sheet_and_recall(msg),
                ))
            
            # 取消按钮
            menu_items.append(ft.Container(
                content=ft.TextButton("取消", on_click=lambda e: self._close_chat_menu_sheet()),
                alignment=ft.alignment.center,
                bgcolor=self.clr_card,
                border_radius=10,
                margin=ft.padding.only(top=8),
            ))
            
            # 底部菜单
            self._chat_menu_sheet = ft.BottomSheet(
                content=ft.Container(
                    content=ft.Column(menu_items, spacing=0, tight=True),
                    padding=ft.padding.only(10, 10, 10, 20),
                    bgcolor=self.clr_bg,
                    border_radius=ft.border_radius.only(top_left=16, top_right=16),
                ),
                open=True,
            )
            self.page.bottom_sheet = self._chat_menu_sheet
            self.page.update()
        except Exception as e:
            # 降级：直接复制
            self._copy_chat_message(msg_content)

    def _close_chat_menu_sheet(self):
        """关闭消息菜单底部弹窗"""
        try:
            if hasattr(self, '_chat_menu_sheet') and self._chat_menu_sheet:
                self._chat_menu_sheet.open = False
                self.page.update()
        except:
            pass

    def _close_bottom_sheet_and_copy(self, content):
        """关闭菜单并复制"""
        self._close_chat_menu_sheet()
        import threading
        threading.Timer(0.2, lambda: self._copy_chat_message(content)).start()

    def _close_bottom_sheet_and_open(self, url):
        """关闭菜单并打开链接"""
        self._close_chat_menu_sheet()
        import threading
        threading.Timer(0.2, lambda: self._open_chat_link(url)).start()

    def _close_bottom_sheet_and_recall(self, msg):
        """关闭菜单并撤回"""
        self._close_chat_menu_sheet()
        import threading
        threading.Timer(0.2, lambda: self._recall_chat_message(msg)).start()

    def _on_chat_input_change(self, e):
        """输入框字数变化时更新内部计数器，超过500字自动截断"""
        try:
            val = e.control.value or ""
            if len(val) > 500:
                e.control.value = val[:500]
                val = e.control.value[:500]
            count = len(val)
            e.control.suffix_text = f"{count}/500"
            e.control.update()
        except:
            pass

    def send_channel_message(self):
        """发送频道消息（乐观发送：先显示带加载图标的消息，后台上传成功后去掉加载图标）"""
        msg_text = self._chat_input.value.strip() if self._chat_input.value else ""
        if not msg_text:
            return
        if len(msg_text) > 500:
            self._show_toast("消息不能超过500字")
            return
        if not self.current_user:
            self.page.snack_bar = ft.SnackBar(ft.Text("请先登录"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # 1. 先在本地缓存添加一条"发送中"的临时消息（乐观显示）
        user_id = self.current_user.get("id", "")
        username = getattr(self, '_channel_nickname', "")
        if not username:
            username = self.current_user.get("name", self.current_user.get("username", ""))
        temp_msg_id = f"temp_{int(time.time()*1000)}"
        temp_msg = {
            "id": temp_msg_id,
            "user_id": user_id,
            "user": username,
            "content": msg_text,
            "is_me": True,
            "is_sending": True,
            "role": str(self.current_user.get("role", "用户")),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if not hasattr(self, '_cached_channel_messages'):
            self._cached_channel_messages = []
        self._cached_channel_messages.append(temp_msg)
        self._render_chat_messages(self._cached_channel_messages)

        # 2. 清空输入框
        self._chat_input.value = ""
        self._chat_input.suffix_text = "0/500"
        self.page.update()

        # 3. 后台发送消息到云端
        def send_thread():
            try:
                ok, error_msg = self._send_channel_message_to_cloud(msg_text)
                if ok:
                    # 发送成功，直接重新加载全部消息（确保临时消息被替换）
                    time.sleep(0.5)
                    def refresh_after_send():
                        try:
                            self._load_channel_messages()
                        except Exception as ex:
                            # 即使刷新失败，也要移除临时消息
                            def cleanup():
                                self._cached_channel_messages = [m for m in self._cached_channel_messages if m.get("id") != temp_msg_id]
                                self._render_chat_messages(self._cached_channel_messages)
                            self.page.run_thread(cleanup)
                    self.page.run_thread(refresh_after_send)
                else:
                    def mark_failed():
                        for m in self._cached_channel_messages:
                            if m.get("id") == temp_msg_id:
                                m["is_sending"] = False
                                m["is_failed"] = True
                        self._render_chat_messages(self._cached_channel_messages)
                        self._show_toast("发送失败：" + (error_msg if error_msg else "请重试"))
                    self.page.run_thread(mark_failed)
            except Exception as e:
                def mark_error():
                    for m in self._cached_channel_messages:
                        if m.get("id") == temp_msg_id:
                            m["is_sending"] = False
                            m["is_failed"] = True
                    self._render_chat_messages(self._cached_channel_messages)
                    self._show_toast("发送失败：" + str(e)[:30])
                self.page.run_thread(mark_error)
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

    def _copy_current_email_addr(self):
        """复制当前选中邮箱地址"""
        try:
            if hasattr(self, 'current_email') and self.current_email:
                addr = self.current_email.get("address", "")
                if addr:
                    self._copy_email(addr)
                    return
            # 尝试从邮箱列表取第一个
            if hasattr(self, 'user_emails') and self.user_emails:
                addr = self.user_emails[0].get("address", "")
                if addr:
                    self._copy_email(addr)
                    return
            self._show_toast("暂无邮箱地址可复制")
        except Exception as e:
            self._show_toast("复制失败")

    def _show_send_email_dialog(self):
        """发送邮件对话框"""
        try:
            from_addr = ""
            if hasattr(self, 'current_email') and self.current_email:
                from_addr = self.current_email.get("address", "")
            to_field = ft.TextField(label="收件人", width=300, border_radius=8, hint_text="example@qq.com")
            subject_field = ft.TextField(label="主题", width=300, border_radius=8)
            body_field = ft.TextField(label="内容", width=300, border_radius=8, multiline=True, min_lines=4, max_lines=8)
            from_field = ft.TextField(label="发件人", width=300, border_radius=8, value=from_addr, read_only=True)

            def do_send(e):
                to = to_field.value.strip()
                subject = subject_field.value.strip()
                body = body_field.value.strip()
                if not to:
                    self._show_toast("请填写收件人")
                    return
                self._close_dialog(dlg)
                self._show_toast("邮件发送功能开发中...")

            dlg = ft.AlertDialog(
                title=ft.Text("发送邮件"),
                content=ft.Column([from_field, to_field, subject_field, body_field], spacing=10, tight=True),
                actions=[
                    ft.TextButton("取消", on_click=lambda e: self._close_dialog(dlg)),
                    ft.TextButton("发送", on_click=do_send),
                ],
            )
            self.page.dialog = dlg
            self.page.update()
        except Exception as e:
            self._show_toast("打开失败：" + str(e)[:20])

    def render_features_page(self):
        """功能页面 - 一排两个长方形卡片"""
        self._show_navbar()  # 主页面显示导航栏
        self.content.controls.clear()
        self.page.floating_action_button = None
        self.content.scroll = ft.ScrollMode.AUTO
        self.content.padding = None
        # 清除返回标志
        self._show_back_to_features = False
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("功能", size=28, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 50, 20, 10), bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border, margin=ft.margin.symmetric(horizontal=20)))
        self.content.controls.append(ft.Container(height=16))

        # 全部本地实现，第一个邮箱不动，后面都是本地工具
        all_features = [
            {"icon": ft.icons.MAIL_OUTLINE, "name": "邮箱", "desc": "管理临时邮箱", "color": ft.colors.BLUE,
             "action": lambda e: self._open_feature_page(self.render_email_list)},
            {"icon": ft.icons.BRUSH, "name": "图片去水印", "desc": "画笔涂抹去除水印", "color": ft.colors.PINK,
             "action": lambda e: self._open_feature_page(self._show_image_watermark)},
            {"icon": ft.icons.QR_CODE_2, "name": "二维码生成", "desc": "文字链接转二维码", "color": ft.colors.GREEN,
             "action": lambda e: self._open_feature_page(self._show_qrcode_generator)},
            {"icon": ft.icons.CALCULATE, "name": "计算器", "desc": "简易科学计算", "color": ft.colors.ORANGE,
             "action": lambda e: self._open_feature_page(self._show_calculator)},
            {"icon": ft.icons.PASSWORD, "name": "密码生成", "desc": "随机安全密码", "color": ft.colors.RED,
             "action": lambda e: self._open_feature_page(self._show_password_gen)},
            {"icon": ft.icons.COLOR_LENS, "name": "颜色工具", "desc": "调色板/屏幕取色/色值转换", "color": ft.colors.AMBER,
             "action": lambda e: self._open_feature_page(self._show_color_tools)},
            {"icon": ft.icons.FEEDBACK_OUTLINED, "name": "问题反馈", "desc": "反馈问题给开发者", "color": ft.colors.PURPLE,
             "action": lambda e: self._open_feature_page(self._show_feedback)},
        ]

        # 构建网格：每行2个卡片，圆角阴影，更好看
        for i in range(0, len(all_features), 2):
            row_cards = []
            for f in all_features[i:i+2]:
                card = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(f["icon"], size=22, color=ft.colors.WHITE),
                            width=42, height=42, bgcolor=f["color"], border_radius=12,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text(f["name"], size=14, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Container(height=2),
                            ft.Text(f["desc"], size=11, color=self.clr_text2, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=0, expand=True, alignment=ft.MainAxisAlignment.CENTER),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, height=68,
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    bgcolor=self.clr_card, border_radius=14,
                    shadow=ft.BoxShadow(spread_radius=0, blur_radius=8,
                        color=ft.colors.with_opacity(0.08, ft.colors.BLACK), offset=ft.Offset(0, 2)),
                    on_click=lambda e, f=f: f["action"](e),
                    ink=True,
                )
                row_cards.append(card)
            if len(row_cards) < 2:
                row_cards.append(ft.Container(expand=True))
            row_container = ft.Container(
                content=ft.Row(row_cards, spacing=12),
                padding=ft.padding.symmetric(horizontal=20),
            )
            self.content.controls.append(row_container)
            self.content.controls.append(ft.Container(height=12))

        self.content.controls.append(ft.Container(height=20))
        self.page.update()

    def _open_feature_page(self, page_func):
        """从功能页打开子页面，标记需要返回键"""
        self._show_back_to_features = True
        page_func()
        # 再次隐藏导航栏（因为page_func如render_email_list可能会显示导航栏）
        if hasattr(self, '_navbar_area') and self._navbar_area:
            self._navbar_area.visible = False
        self.page.floating_action_button = None
        self.page.update()

    def _on_view_pop(self, e):
        """安卓返回键处理：子页面返回上一页，主页面退出应用"""
        try:
            # 如果在功能子页面，返回功能页
            if getattr(self, '_show_back_to_features', False):
                self._back_to_features()
                return
            # 如果在网盘子目录，返回上一级
            if hasattr(self, 'current_folder_id') and self.current_folder_id and self.current_folder_id > 0:
                if hasattr(self, '_go_back_folder'):
                    self._go_back_folder()
                    return
            # 其他情况让默认行为处理（退出应用）
        except Exception as ex:
            print(f"[返回键] 处理失败: {ex}")

    def _back_to_features(self, e=None):
        """从子页面返回功能页"""
        self._close_embedded_webview()
        self._show_navbar()  # 返回主页面显示导航栏
        self._show_back_to_features = False
        self.current_tab = 1  # 功能页索引
        self.render_features_page()

    def _open_in_browser(self, url):
        """用系统浏览器打开网址（功能页工具类卡片用）"""
        try:
            self.page.launch_url(url)
        except Exception:
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                self._show_toast("打开失败，请复制链接手动打开", "error")

    def _get_flet_hwnd(self):
        """获取Flet主窗口句柄"""
        try:
            import win32gui
            # 先尝试用窗口标题查找
            title = getattr(self.page, 'title', None) or "TempMail"
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                return hwnd
            # 尝试查找包含应用名的窗口
            def callback(h, extra):
                t = win32gui.GetWindowText(h)
                if t and ("TempMail" in t or "YoXi" in t or "邮箱" in t):
                    extra.append(h)
                return True
            found = []
            win32gui.EnumWindows(callback, found)
            if found:
                return found[0]
            # 最后用前台窗口
            return win32gui.GetForegroundWindow()
        except Exception:
            return None

    def _close_embedded_webview(self):
        """关闭嵌入的WebView子窗口"""
        try:
            import win32gui
            import win32con
            parent = self._get_flet_hwnd()
            if parent:
                def callback(h, extra):
                    if win32gui.GetParent(h) == parent:
                        extra.append(h)
                    return True
                children = []
                win32gui.EnumWindows(callback, children)
                for h in children:
                    win32gui.SendMessage(h, win32con.WM_CLOSE, 0, 0)
        except Exception:
            pass

    def _open_webview_page(self, url, title):
        """应用内嵌入式打开网页：pywebview窗口嵌入Flet窗口内部"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None
        self.content.padding = None
        self._show_back_to_features = True
        self.page.floating_action_button = None

        # 顶部标题栏（保留返回按钮）
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: (self._close_embedded_webview(), self._back_to_features())),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.padding.only(8, 45, 8, 8), bgcolor=self.clr_bg,
        )
        divider = ft.Container(height=1, bgcolor=self.clr_border)

        # 加载中提示
        loading = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=36, height=36, color=THEME_COLOR, stroke_width=3),
                ft.Container(height=12),
                ft.Text("正在加载...", size=14, color=self.clr_text2),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            alignment=ft.alignment.center, expand=True,
        )

        self.content.controls.append(ft.Column([header, divider, loading], spacing=0, expand=True))
        self.page.update()

        # 启动嵌入式 WebView
        def _launch():
            try:
                import subprocess, time
                parent_hwnd = self._get_flet_hwnd()
                if not parent_hwnd:
                    self.page.run_thread(lambda: self._show_toast("获取窗口失败，用外部浏览器打开", "error"))
                    self.page.run_thread(lambda: self._open_in_browser(url))
                    return
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embedded_webview.py")
                if not os.path.exists(script_path):
                    script_path = os.path.join(_base_dir, "embedded_webview.py")
                proc = subprocess.Popen(
                    [sys.executable, script_path, title, url, str(parent_hwnd)],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
                )
                self._embedded_webview_proc = proc
            except Exception as e:
                self.page.run_thread(lambda: self._show_toast("打开失败: " + str(e)[:15], "error"))
                self.page.run_thread(lambda: self._open_in_browser(url))

        import threading
        threading.Thread(target=_launch, daemon=True).start()


    def _reload_webview(self, webview, url):
        """刷新WebView页面"""
        if webview:
            try:
                webview.url = url
                self.page.update()
                self._show_toast("已刷新", "success")
            except Exception:
                self._show_toast("刷新失败", "error")
        else:
            self._show_toast("无法刷新", "warning")

    def _feature_page_header(self, title, on_back=None):
        """功能子页面通用顶部栏（标题固定，内容区单独滚动）"""
        back_action = on_back if on_back else self._back_to_features
        self.content.scroll = None  # 顶部标题固定，不跟随滚动
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22, on_click=back_action),
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8), bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))
        # 创建可滚动的内容区，后续内容都添加到这里
        self._feature_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self.content.controls.append(self._feature_content)

    def _show_qrcode_generator(self):
        """二维码生成器页面（输入框+生成按钮一行，下方方框展示，可保存）"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("二维码生成")
        qr_input = ft.TextField(
            label="输入文字或链接", multiline=False, height=48, expand=True,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.WHITE),
            border_color=ft.colors.GREY_500, focused_border_color=THEME_COLOR,
            color=self.clr_text, cursor_color=THEME_COLOR,
            label_style=ft.TextStyle(color=self.clr_text2, size=12),
            text_size=14, content_padding=10,
        )
        qr_image = ft.Image(src="", width=220, height=220, fit=ft.ImageFit.CONTAIN, visible=False)
        qr_placeholder = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.QR_CODE_2, size=48, color=ft.colors.GREY_300),
                ft.Container(height=8),
                ft.Text("输入内容后点生成", size=12, color=ft.colors.GREY_400),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            width=220, height=220, alignment=ft.alignment.center,
        )
        qr_error = ft.Text("", size=12, color=ft.colors.RED)
        qr_current_url = {"url": ""}
        save_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.DOWNLOAD, size=16, color=ft.colors.WHITE),
                ft.Container(width=6),
                ft.Text("保存到相册", size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
            height=44, bgcolor=ft.colors.BLUE_500, border_radius=10,
            alignment=ft.alignment.center, visible=False, ink=True,
            on_click=lambda e: self._save_qrcode_image(qr_current_url.get("url", "")),
        )

        def do_generate(e):
            text = qr_input.value.strip() if qr_input.value else ""
            if not text:
                qr_error.value = "请输入内容"
                qr_image.visible = False
                qr_placeholder.visible = True
                save_btn.visible = False
                self.page.update()
                return
            qr_error.value = ""
            import urllib.parse
            encoded = urllib.parse.quote(text)
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data={encoded}"
            qr_current_url["url"] = qr_url
            qr_image.src = qr_url
            qr_image.visible = True
            qr_placeholder.visible = False
            save_btn.visible = True
            self.page.update()

        gen_btn = ft.Container(
            content=ft.Text("生成", size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
            width=64, height=48, bgcolor=ft.colors.GREEN, border_radius=10,
            alignment=ft.alignment.center, on_click=do_generate, ink=True,
        )
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                ft.Row([qr_input, gen_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                qr_error,
                ft.Container(height=10),
                ft.Container(
                    content=ft.Stack([qr_placeholder, qr_image], alignment=ft.alignment.center),
                    alignment=ft.alignment.center, padding=16,
                    bgcolor=self.clr_card, border_radius=14,
                    border=ft.border.all(1, self.clr_border),
                ),
                ft.Container(height=12),
                save_btn,
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _save_qrcode_image(self, qr_url):
        """保存二维码图片到本地相册目录"""
        if not qr_url:
            self._show_toast("请先生成二维码", "warning")
            return
        try:
            import urllib.request, time as _t
            save_dir = os.path.join(_base_dir, "user_data", "qrcodes")
            os.makedirs(save_dir, exist_ok=True)
            filename = f"qrcode_{int(_t.time())}.png"
            filepath = os.path.join(save_dir, filename)
            req = urllib.request.Request(qr_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            self._show_toast(f"已保存到: qrcodes/{filename}", "success")
        except Exception as e:
            self._show_toast("保存失败: " + str(e)[:15], "error")

    def _extract_url_from_text(self, text):
        """从分享文字中自动提取URL"""
        import re
        pattern = r'https?://[^\s一-鿿，。！？、；：""''（）【】]+'
        match = re.search(pattern, text)
        return match.group(0) if match else text.strip()

    def _find_video_url_in_json(self, obj, depth=0):
        """递归从JSON中查找视频地址"""
        if depth > 6:
            return None
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower()
                if isinstance(v, str) and v.startswith("http") and any(x in kl for x in ["url","play","video","addr","src","download","link","nwm"]):
                    if any(ext in v for ext in [".mp4", ".flv", ".m3u8", "video", "play"]):
                        return v
                if isinstance(v, str) and v.startswith("http") and ".mp4" in v:
                    return v
                r = self._find_video_url_in_json(v, depth+1)
                if r:
                    return r
        elif isinstance(obj, list):
            for item in obj:
                r = self._find_video_url_in_json(item, depth+1)
                if r:
                    return r
        return None

    def _find_cover_in_json(self, obj, depth=0):
        """递归从JSON中查找封面图"""
        if depth > 6:
            return None
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower()
                if isinstance(v, str) and v.startswith("http") and any(x in kl for x in ["cover","pic","image","img","thumb","poster"]):
                    if any(ext in v for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                        return v
                r = self._find_cover_in_json(v, depth+1)
                if r:
                    return r
        elif isinstance(obj, list):
            for item in obj:
                r = self._find_cover_in_json(item, depth+1)
                if r:
                    return r
        return None

    def _show_video_watermark(self):
        """视频去水印（自动提取分享链接+多API轮询）"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("视频去水印")
        _input_style = {
            "bgcolor": ft.colors.with_opacity(0.75, ft.colors.WHITE),
            "border_color": ft.colors.GREY_500,
            "focused_border_color": THEME_COLOR,
            "color": self.clr_text,
            "cursor_color": THEME_COLOR,
            "label_style": ft.TextStyle(color=self.clr_text2, size=12),
        }
        video_input = ft.TextField(
            label="粘贴抖音/快手分享内容", multiline=True, min_lines=2, max_lines=3, expand=True,
            text_size=13, content_padding=10, hint_text="直接粘贴复制的分享文字，自动提取链接",
            hint_style=ft.TextStyle(color=ft.colors.GREY_400, size=12),
            **_input_style,
        )
        result_title = ft.Text("", size=14, weight=ft.FontWeight.W_600, color=self.clr_text, max_lines=2)
        result_cover = ft.Image(src="", width=100, height=140, fit=ft.ImageFit.COVER, border_radius=8, visible=False)
        result_url = ft.Text("", size=12, color=THEME_COLOR, selectable=True, max_lines=3)
        result_author = ft.Text("", size=12, color=self.clr_text2)
        result_card = ft.Container(visible=False)
        parse_status = ft.Text("", size=12, color=self.clr_text2)

        def do_parse(e):
            raw = video_input.value.strip() if video_input.value else ""
            if not raw:
                self._show_toast("请粘贴分享内容", "warning")
                return
            url = self._extract_url_from_text(raw)
            if not url.startswith("http"):
                self._show_toast("未找到有效链接", "error")
                return
            video_input.value = url
            result_card.visible = False
            parse_status.value = "正在解析（多接口轮询）..."
            self.page.update()

            def parse_thread():
                import urllib.parse, urllib.request, json as _json, ssl as _ssl
                ctx = _ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = _ssl.CERT_NONE
                encoded = urllib.parse.quote(url, safe="")
                api_list = [
                    f"https://api.vvhan.com/api/douyin?url={encoded}",
                    f"https://api.oioweb.cn/api/douyin.php?url={encoded}",
                    f"https://api.qqsuu.cn/api/dm-douyin?url={encoded}",
                    f"https://api.lolimi.cn/API/dy/jx.php?url={encoded}",
                    f"https://api.gumengya.com/Api/Douyin?url={encoded}",
                    f"https://api.52vmy.cn/api/dy?url={encoded}",
                ]
                found = False
                for idx, api_url in enumerate(api_list):
                    try:
                        parse_status.value = f"尝试接口 {idx+1}/{len(api_list)}..."
                        self.page.run_thread(self.page.update)
                        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                            body = resp.read().decode("utf-8", errors="ignore")
                        try:
                            data = _json.loads(body)
                        except Exception:
                            continue
                        play_url = self._find_video_url_in_json(data)
                        if not play_url:
                            continue
                        cover = self._find_cover_in_json(data)
                        title = ""
                        author = ""
                        def _find_str(o, keys, d=0):
                            if d > 5: return ""
                            if isinstance(o, dict):
                                for k, v in o.items():
                                    if str(k).lower() in keys and isinstance(v, str) and v:
                                        return v
                                for v in o.values():
                                    r = _find_str(v, keys, d+1)
                                    if r: return r
                            elif isinstance(o, list):
                                for item in o:
                                    r = _find_str(item, keys, d+1)
                                    if r: return r
                            return ""
                        title = _find_str(data, ["title","desc","description","文案","标题"]) or "解析成功"
                        author = _find_str(data, ["author","nickname","name","作者","昵称"])
                        result_title.value = title
                        result_url.value = play_url
                        result_author.value = author
                        if cover:
                            result_cover.src = cover
                            result_cover.visible = True
                        result_card.visible = True
                        parse_status.value = ""
                        found = True
                        self.page.run_thread(lambda: self._show_toast("解析成功", "success"))
                        self.page.run_thread(self.page.update)
                        break
                    except Exception:
                        continue
                if not found:
                    # 备用：抖音直连解析
                    if "douyin" in url or "iesdouyin" in url:
                        parse_status.value = "尝试抖音直连解析..."
                        self.page.run_thread(self.page.update)
                        try:
                            import re as _re
                            # 跟随重定向获取真实页面
                            req2 = urllib.request.Request(url, headers={
                                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                                "Referer": "https://www.douyin.com/",
                            })
                            with urllib.request.urlopen(req2, timeout=15, context=ctx) as resp2:
                                final_url = resp2.geturl()
                                html = resp2.read().decode("utf-8", errors="ignore")
                            # 从HTML中提取视频地址
                            play_url = ""
                            # 尝试多种格式
                            patterns = [
                                r'"playAddr"[^}]+?"urlList"\s*:\s*\["([^"]+)"',
                                r'"play_addr"[^}]+?"url_list"\s*:\s*\["([^"]+)"',
                                r'(https?://[^"\s]+\.mp4[^"\s]*)',
                                r'"src"\s*:\s*"([^"]+\.mp4[^"]*)"',
                            ]
                            for pat in patterns:
                                m = _re.search(pat, html)
                                if m:
                                    play_url = m.group(1).replace("\\u002F", "/").replace("\\/", "/")
                                    break
                            if play_url:
                                result_url.value = play_url
                                result_title.value = "抖音直连解析"
                                result_card.visible = True
                                parse_status.value = ""
                                self.page.run_thread(lambda: self._show_toast("解析成功", "success"))
                                self.page.run_thread(self.page.update)
                                found = True
                        except Exception:
                            pass
                if not found:
                    parse_status.value = ""
                    self.page.run_thread(lambda: self._show_toast("所有接口暂不可用，请稍后重试", "error"))
                    self.page.run_thread(self.page.update)
            threading.Thread(target=parse_thread, daemon=True).start()

        def do_open(e):
            if result_url.value:
                try:
                    self.page.launch_url(result_url.value)
                except Exception:
                    self._copy_text(result_url.value, "链接已复制，请在浏览器打开")

        def do_copy_link(e):
            if result_url.value:
                self._copy_text(result_url.value, "无水印链接已复制")

        parse_btn = ft.Container(
            content=ft.Column([ft.Icon(ft.icons.SEARCH, size=20, color=ft.colors.WHITE),
                ft.Container(height=2), ft.Text("解析", size=12, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            width=64, height=64, bgcolor=ft.colors.PURPLE, border_radius=12,
            alignment=ft.alignment.center, on_click=do_parse, ink=True,
        )
        result_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    result_cover,
                    ft.Container(width=10),
                    ft.Column([
                        result_title,
                        ft.Container(height=4),
                        result_author,
                    ], spacing=0, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=10),
                ft.Container(height=1, bgcolor=self.clr_border),
                ft.Container(height=10),
                ft.Text("无水印视频链接", size=11, color=self.clr_text2),
                ft.Container(height=4),
                result_url,
                ft.Container(height=12),
                ft.Row([
                    ft.Container(content=ft.Row([ft.Icon(ft.icons.PLAY_ARROW, size=16, color=ft.colors.WHITE),
                        ft.Container(width=4), ft.Text("打开视频", size=13, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                        expand=True, height=40, bgcolor=THEME_COLOR, border_radius=8,
                        alignment=ft.alignment.center, on_click=do_open, ink=True),
                    ft.Container(width=8),
                    ft.Container(content=ft.Row([ft.Icon(ft.icons.COPY, size=16, color=THEME_COLOR),
                        ft.Container(width=4), ft.Text("复制链接", size=13, weight=ft.FontWeight.W_600, color=THEME_COLOR)],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                        expand=True, height=40, bgcolor=ft.colors.TRANSPARENT, border_radius=8,
                        border=ft.border.all(1, THEME_COLOR),
                        alignment=ft.alignment.center, on_click=do_copy_link, ink=True),
                ], spacing=0),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            visible=False,
        )
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                ft.Row([video_input, parse_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=6),
                parse_status,
                ft.Container(height=8),
                ft.Container(content=ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=12, color=self.clr_text3),
                    ft.Container(width=4),
                    ft.Text("直接粘贴抖音分享文字（含文案），自动提取链接解析", size=11, color=self.clr_text3),
                ], spacing=0), padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=14),
                result_card,
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _show_calculator(self):
        """简易计算器页面"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None
        self._feature_page_header("计算器")
        calc_display = ft.Text("0", size=36, weight=ft.FontWeight.BOLD, color=self.clr_text,
            text_align=ft.TextAlign.RIGHT, selectable=True)
        calc_state = {"expr": "", "just_eval": False}

        def calc_btn(text, color=None, bgcolor=None, expand=1):
            return ft.Container(
                content=ft.Text(text, size=18, weight=ft.FontWeight.W_600,
                    color=color or self.clr_text, text_align=ft.TextAlign.CENTER),
                expand=expand, height=56, bgcolor=bgcolor or self.clr_card,
                border_radius=12, alignment=ft.alignment.center,
                on_click=lambda e: self._calc_input(text, calc_state, calc_display),
                ink=True,
            )

        ops_row1 = ft.Row([calc_btn("C", color=ft.colors.RED), calc_btn("(", color=THEME_COLOR),
            calc_btn(")", color=THEME_COLOR), calc_btn("÷", color=THEME_COLOR)], spacing=8)
        ops_row2 = ft.Row([calc_btn("7"), calc_btn("8"), calc_btn("9"),
            calc_btn("×", color=THEME_COLOR)], spacing=8)
        ops_row3 = ft.Row([calc_btn("4"), calc_btn("5"), calc_btn("6"),
            calc_btn("−", color=THEME_COLOR)], spacing=8)
        ops_row4 = ft.Row([calc_btn("1"), calc_btn("2"), calc_btn("3"),
            calc_btn("+", color=THEME_COLOR)], spacing=8)
        ops_row5 = ft.Row([calc_btn("0", expand=2), calc_btn("."),
            calc_btn("=", bgcolor=THEME_COLOR, color=ft.colors.WHITE)], spacing=8)

        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=16),
                ft.Container(content=calc_display, bgcolor=self.clr_card, border_radius=12,
                    padding=ft.padding.symmetric(horizontal=16, vertical=20),
                    alignment=ft.alignment.center_right),
                ft.Container(height=14),
                ops_row1, ft.Container(height=8),
                ops_row2, ft.Container(height=8),
                ops_row3, ft.Container(height=8),
                ops_row4, ft.Container(height=8),
                ops_row5,
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _calc_input(self, key, state, display):
        """计算器按键处理"""
        try:
            if key == "C":
                state["expr"] = ""
                display.value = "0"
            elif key == "=":
                if not state["expr"]:
                    return
                expr = state["expr"].replace("×", "*").replace("÷", "/").replace("−", "-")
                try:
                    result = eval(expr, {"__builtins__": {}}, {})
                    result = round(float(result), 10)
                    if result == int(result):
                        result = int(result)
                    display.value = str(result)
                    state["expr"] = str(result)
                    state["just_eval"] = True
                except Exception:
                    display.value = "错误"
                    state["expr"] = ""
            else:
                if state.get("just_eval") and key not in "+−×÷":
                    state["expr"] = ""
                state["just_eval"] = False
                state["expr"] += key
                display.value = state["expr"] if state["expr"] else "0"
            self.page.update()
        except Exception:
            pass

    def _show_image_watermark(self):
        """图片去水印（画笔涂抹模式：GestureDetector检测涂抹，动态圆点显示）"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("图片去水印")

        DISPLAY_W = 300
        state = {"img_path": "", "orig_w": 0, "orig_h": 0, "display_h": 300,
                 "scale": 1.0, "painted": [], "result_path": ""}

        brush_text = ft.Text("20", size=14, weight=ft.FontWeight.BOLD, color=THEME_COLOR, width=28)
        brush_slider = ft.Slider(min=8, max=50, value=20, divisions=42,
            active_color=THEME_COLOR,
            on_change=lambda e: (setattr(brush_text, "value", str(int(e.control.value))), self.page.update()))

        img_display = ft.Image(src="", width=DISPLAY_W, fit=ft.ImageFit.FIT_WIDTH, visible=False)
        paint_layer = ft.Stack([], width=DISPLAY_W, height=300)
        placeholder = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.IMAGE_OUTLINED, size=48, color=ft.colors.GREY_300),
                ft.Container(height=8),
                ft.Text("选择图片后用画笔涂抹水印区域", size=12, color=ft.colors.GREY_400),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            width=DISPLAY_W, height=300, alignment=ft.alignment.center,
            bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_100), border_radius=12,
        )
        status_text = ft.Text("选择一张图片开始", size=13, color=self.clr_text2, text_align=ft.TextAlign.CENTER)
        result_img = ft.Image(src="", width=DISPLAY_W, fit=ft.ImageFit.FIT_WIDTH, visible=False)

        def _bs():
            return int(brush_slider.value) if brush_slider.value else 20

        def _add_dot(x, y):
            bs = _bs()
            state["painted"].append((x, y, bs))
            dot = ft.Container(
                width=bs, height=bs, border_radius=bs // 2,
                bgcolor=ft.colors.with_opacity(0.45, ft.colors.RED),
                left=x - bs // 2, top=y - bs // 2,
            )
            paint_layer.controls.append(dot)

        def on_pan_start(e):
            if not state["img_path"]: return
            _add_dot(e.local_x, e.local_y)
            self.page.update()

        def on_pan_update(e):
            if not state["img_path"]: return
            _add_dot(e.local_x, e.local_y)
            self.page.update()

        img_stack = ft.Stack([
            img_display,
            paint_layer,
        ], width=DISPLAY_W, height=300)

        gesture = ft.GestureDetector(
            content=img_stack,
            on_pan_start=on_pan_start,
            on_pan_update=on_pan_update,
        )

        def do_select(e):
            try:
                import tkinter as tk
                from tkinter import filedialog
                from PIL import Image
                root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
                filepath = filedialog.askopenfilename(
                    title="选择图片",
                    filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.webp"), ("所有文件", "*.*")])
                root.destroy()
                if not filepath: return
                img = Image.open(filepath).convert("RGB")
                w, h = img.size
                state["img_path"] = filepath
                state["orig_w"], state["orig_h"] = w, h
                state["scale"] = w / DISPLAY_W
                state["display_h"] = max(100, int(h / state["scale"]))
                state["painted"] = []
                state["result_path"] = ""
                img_display.src = filepath
                img_display.visible = True
                img_display.height = state["display_h"]
                img_display.width = DISPLAY_W
                paint_layer.height = state["display_h"]
                paint_layer.width = DISPLAY_W
                paint_layer.controls.clear()
                placeholder.visible = False
                result_img.visible = False
                img_stack.height = state["display_h"]
                status_text.value = "按住鼠标涂抹水印区域，然后点开始去除"
                self.page.update()
            except Exception as ex:
                status_text.value = "选择失败: " + str(ex)[:25]
                self.page.update()

        def do_clear(e):
            state["painted"] = []
            paint_layer.controls.clear()
            status_text.value = "已清除涂抹"
            self.page.update()

        def do_process(e):
            if not state["img_path"]:
                self._show_toast("请先选择图片", "warning"); return
            if not state["painted"]:
                self._show_toast("请先用画笔涂抹水印区域", "warning"); return
            status_text.value = "处理中..."
            self.page.update()
            def process_thread():
                try:
                    from PIL import Image, ImageFilter
                    import numpy as np
                    img = Image.open(state["img_path"]).convert("RGB")
                    w, h = img.size
                    scale = state["scale"]
                    mask = Image.new("L", (w, h), 0)
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(mask)
                    for (dx, dy, bs) in state["painted"]:
                        ix, iy = int(dx * scale), int(dy * scale)
                        r = int(bs * scale / 2) + 2
                        draw.ellipse([ix-r, iy-r, ix+r, iy+r], fill=255)
                    filtered = img.filter(ImageFilter.MedianFilter(size=7))
                    for _ in range(2):
                        filtered = filtered.filter(ImageFilter.MedianFilter(size=5))
                    arr_orig = np.array(img)
                    arr_filt = np.array(filtered)
                    mask_blur = mask.filter(ImageFilter.GaussianBlur(radius=3))
                    arr_mb = np.array(mask_blur).astype(float) / 255.0
                    arr_mb = arr_mb[:,:,np.newaxis]
                    arr_result = (arr_orig * (1-arr_mb) + arr_filt * arr_mb).astype(np.uint8)
                    result = Image.fromarray(arr_result)
                    save_dir = os.path.join(_base_dir, "user_data", "watermark_removed")
                    os.makedirs(save_dir, exist_ok=True)
                    import time as _t
                    out_path = os.path.join(save_dir, "cleaned_{}.png".format(int(_t.time())))
                    result.save(out_path, "PNG")
                    state["result_path"] = out_path
                    result_img.src = out_path
                    result_img.visible = True
                    result_img.height = state["display_h"]
                    status_text.value = "处理完成！涂抹了{}个点".format(len(state["painted"]))
                    self.page.run_thread(self.page.update)
                except Exception as ex:
                    status_text.value = "处理失败: " + str(ex)[:25]
                    self.page.run_thread(self.page.update)
            import threading
            threading.Thread(target=process_thread, daemon=True).start()

        def do_save(e):
            if state["result_path"]:
                self._show_toast("已保存到 watermark_removed 文件夹", "success")
            else:
                self._show_toast("请先处理图片", "warning")

        def _btn(text, icon, color, on_click):
            return ft.Container(
                content=ft.Row([ft.Icon(icon, size=16, color=ft.colors.WHITE),
                    ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                expand=True, height=44, bgcolor=color, border_radius=10,
                alignment=ft.alignment.center, on_click=on_click, ink=True)

        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                ft.Container(content=ft.Row([
                    ft.Icon(ft.icons.BRUSH, size=18, color=self.clr_text2),
                    ft.Text("画笔大小", size=13, color=self.clr_text, expand=True), brush_text,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.padding.symmetric(horizontal=4)),
                brush_slider,
                ft.Container(height=4),
                ft.Container(content=ft.Stack([placeholder, gesture], alignment=ft.alignment.top_left),
                    alignment=ft.alignment.center),
                ft.Container(height=8),
                status_text,
                ft.Container(height=8),
                ft.Container(content=result_img, alignment=ft.alignment.center),
                ft.Container(height=12),
                ft.Row([_btn("选择图片", ft.icons.IMAGE, ft.colors.BLUE_500, do_select),
                        _btn("清除", ft.icons.CLEAR, ft.colors.GREY, do_clear)], spacing=8),
                ft.Container(height=8),
                ft.Row([_btn("开始去除", ft.icons.BRUSH, THEME_COLOR, do_process),
                        _btn("保存", ft.icons.SAVE, ft.colors.GREEN, do_save)], spacing=8),
                ft.Container(height=10),
                ft.Text("提示：按住鼠标在图片上涂抹，红色覆盖的地方会被去除", size=11,
                    color=self.clr_text3, text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _show_shortlink_tool(self):
        """短链接工具（多API轮询）"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = ft.ScrollMode.AUTO
        self._feature_page_header("短链接")
        link_input = ft.TextField(
            label="输入长链接（https://...）", multiline=False, height=48, expand=True,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.WHITE),
            border_color=ft.colors.GREY_500, focused_border_color=THEME_COLOR,
            color=self.clr_text, cursor_color=THEME_COLOR,
            label_style=ft.TextStyle(color=self.clr_text2, size=12),
            text_size=13, content_padding=10,
        )
        result_card = ft.Container(visible=False)
        result_url = ft.Text("", size=15, weight=ft.FontWeight.W_600, color=THEME_COLOR, selectable=True)
        result_original = ft.Text("", size=12, color=self.clr_text2, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        short_status = ft.Text("", size=12, color=self.clr_text2)

        def do_short(e):
            url = link_input.value.strip() if link_input.value else ""
            if not url:
                self._show_toast("请输入链接", "warning")
                return
            if not url.startswith("http"):
                url = "https://" + url
            result_card.visible = False
            short_status.value = "生成中（多接口轮询）..."
            self.page.update()
            def short_thread():
                import urllib.parse, urllib.request, json as _json, ssl as _ssl
                ctx = _ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = _ssl.CERT_NONE
                encoded = urllib.parse.quote(url, safe="")
                # 多API源，按顺序尝试
                api_list = [
                    ("is.gd", f"https://is.gd/create.php?format=json&url={encoded}", "json", "shorturl"),
                    ("tinyurl", f"https://tinyurl.com/api-create.php?url={encoded}", "text", None),
                    ("ft12", f"https://api.ft12.com/api.php?url={encoded}", "text", None),
                    ("52vmy", f"https://api.52vmy.cn/api/dwz?url={encoded}&type=json", "json", None),
                    ("cenguigui", f"https://api.cenguigui.cn/api/dwz/?url={encoded}", "json", None),
                ]
                found = False
                for idx, (name, api_url, resp_type, key) in enumerate(api_list):
                    try:
                        short_status.value = f"尝试接口 {idx+1}/{len(api_list)} ({name})..."
                        self.page.run_thread(self.page.update)
                        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                            body = resp.read().decode("utf-8", errors="ignore").strip()
                        if not body:
                            continue
                        short_url = ""
                        if resp_type == "json":
                            try:
                                data = _json.loads(body)
                                if key and key in data:
                                    short_url = data[key]
                                else:
                                    # 递归找短链接
                                    def _find_short(o, d=0):
                                        if d > 4: return ""
                                        if isinstance(o, dict):
                                            for k, v in o.items():
                                                if isinstance(v, str) and v.startswith("http") and len(v) < 50:
                                                    return v
                                            for v in o.values():
                                                r = _find_short(v, d+1)
                                                if r: return r
                                        elif isinstance(o, list):
                                            for item in o:
                                                r = _find_short(item, d+1)
                                                if r: return r
                                        return ""
                                    short_url = _find_short(data)
                            except Exception:
                                if body.startswith("http"):
                                    short_url = body
                        else:  # text
                            if body.startswith("http"):
                                short_url = body
                        if short_url and short_url.startswith("http") and short_url != url:
                            result_url.value = short_url
                            result_original.value = "原链接: " + url
                            result_card.visible = True
                            short_status.value = ""
                            found = True
                            self.page.run_thread(lambda: self._show_toast("生成成功", "success"))
                            self.page.run_thread(self.page.update)
                            break
                    except Exception:
                        continue
                if not found:
                    short_status.value = ""
                    self.page.run_thread(lambda: self._show_toast("所有接口暂不可用，请稍后重试", "error"))
                    self.page.run_thread(self.page.update)
            threading.Thread(target=short_thread, daemon=True).start()

        def do_copy(e):
            if result_url.value:
                self._copy_text(result_url.value, "短链接已复制")

        gen_btn = ft.Container(
            content=ft.Text("生成", size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
            width=64, height=48, bgcolor=ft.colors.TEAL, border_radius=10,
            alignment=ft.alignment.center, on_click=do_short, ink=True,
        )
        result_card = ft.Container(
            content=ft.Column([
                ft.Text("短链接", size=12, color=self.clr_text2),
                ft.Container(height=4),
                result_url,
                ft.Container(height=6),
                result_original,
                ft.Container(height=10),
                ft.OutlinedButton("复制链接", expand=True, height=40,
                    style=ft.ButtonStyle(color=THEME_COLOR), on_click=do_copy),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=12, padding=14, visible=False,
        )
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                ft.Row([link_input, gen_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                short_status,
                ft.Container(height=8),
                result_card,
                ft.Container(height=10),
                ft.Text("多接口自动轮询，免费接口可能不稳定", size=11, color=self.clr_text3, text_align=ft.TextAlign.CENTER),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _show_text_tools(self):
        """文本工具：字数统计、大小写转换、去空格、反转"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("文本工具")
        text_input = ft.TextField(
            label="输入或粘贴文本", multiline=True, min_lines=4, max_lines=8, expand=True,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.WHITE),
            border_color=ft.colors.GREY_500, focused_border_color=THEME_COLOR,
            color=self.clr_text, cursor_color=THEME_COLOR,
            label_style=ft.TextStyle(color=self.clr_text2, size=12),
            text_size=13, content_padding=10, hint_text="在这里输入文本...",
            hint_style=ft.TextStyle(color=ft.colors.GREY_400, size=12),
        )
        stats_text = ft.Text("字符数: 0  字数: 0  行数: 0", size=12, color=self.clr_text2)

        def update_stats(e=None):
            t = text_input.value or ""
            chars = len(t)
            words = len(t.split())
            lines = len(t.splitlines()) if t else 0
            stats_text.value = "字符数: {}  字数: {}  行数: {}".format(chars, words, lines)

        text_input.on_change = update_stats

        def make_btn(text, color, on_click):
            return ft.Container(
                content=ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=ft.colors.WHITE, text_align=ft.TextAlign.CENTER),
                expand=True, height=42, bgcolor=color, border_radius=10,
                alignment=ft.alignment.center, on_click=on_click, ink=True,
            )

        def do_upper(e):
            if text_input.value:
                text_input.value = text_input.value.upper()
                update_stats()
                self.page.update()
        def do_lower(e):
            if text_input.value:
                text_input.value = text_input.value.lower()
                update_stats()
                self.page.update()
        def do_title(e):
            if text_input.value:
                text_input.value = text_input.value.title()
                update_stats()
                self.page.update()
        def do_trim(e):
            if text_input.value:
                lines = [l.strip() for l in text_input.value.splitlines()]
                text_input.value = "\n".join(lines)
                update_stats()
                self.page.update()
        def do_reverse(e):
            if text_input.value:
                text_input.value = text_input.value[::-1]
                update_stats()
                self.page.update()
        def do_clear(e):
            text_input.value = ""
            update_stats()
            self.page.update()
        def do_copy(e):
            if text_input.value:
                self._copy_text(text_input.value, "已复制")

        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                text_input,
                ft.Container(height=6),
                stats_text,
                ft.Container(height=12),
                ft.Row([make_btn("大写", ft.colors.BLUE, do_upper), make_btn("小写", ft.colors.TEAL, do_lower)], spacing=8),
                ft.Container(height=8),
                ft.Row([make_btn("首字母大写", ft.colors.PURPLE, do_title), make_btn("去空格", ft.colors.ORANGE, do_trim)], spacing=8),
                ft.Container(height=8),
                ft.Row([make_btn("反转文本", ft.colors.PINK, do_reverse), make_btn("清空", ft.colors.GREY, do_clear)], spacing=8),
                ft.Container(height=8),
                make_btn("复制结果", ft.colors.GREEN, do_copy),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _show_password_gen(self):
        """密码生成器：可配置长度和字符类型"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = ft.ScrollMode.AUTO
        self._feature_page_header("密码生成")
        
        length_text = ft.Text("16", size=22, weight=ft.FontWeight.BOLD, color=THEME_COLOR)
        length_slider = ft.Slider(min=4, max=32, value=16, divisions=28, label="{value}",
            active_color=THEME_COLOR,
            on_change=lambda e: (setattr(length_text, "value", str(int(e.control.value))), self.page.update()))
        
        use_upper = ft.Checkbox(label="大写字母 (A-Z)", value=True, fill_color=THEME_COLOR)
        use_lower = ft.Checkbox(label="小写字母 (a-z)", value=True, fill_color=THEME_COLOR)
        use_digits = ft.Checkbox(label="数字 (0-9)", value=True, fill_color=THEME_COLOR)
        use_symbols = ft.Checkbox(label="特殊符号 (!@#$)", value=False, fill_color=THEME_COLOR)
        
        # 密码结果展示卡片
        result_text = ft.Text("点击下方按钮生成", size=18, weight=ft.FontWeight.W_600, 
            color=self.clr_text2, selectable=True, expand=True)
        result_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PASSWORD, size=20, color=THEME_COLOR),
                ft.Container(width=8),
                result_text,
                ft.IconButton(ft.icons.COPY, icon_size=20, icon_color=self.clr_text2,
                    on_click=lambda e: self._copy_text(result_text.value, "密码已复制") if result_text.value and result_text.value != "点击下方按钮生成" else self._show_toast("请先生成密码")),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=12, padding=ft.padding.all(16),
            border=ft.border.all(1, self.clr_border),
        )
        
        def do_generate(e):
            import random, string
            length = int(length_slider.value)
            chars = ""
            if use_upper.value: chars += string.ascii_uppercase
            if use_lower.value: chars += string.ascii_lowercase
            if use_digits.value: chars += string.digits
            if use_symbols.value: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not chars:
                self._show_toast("至少选择一种字符类型")
                return
            pwd = "".join(random.choice(chars) for _ in range(length))
            result_text.value = pwd
            result_text.color = self.clr_text
            self.page.update()
        
        # 生成按钮
        gen_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.REFRESH, size=20, color=ft.colors.WHITE),
                ft.Container(width=8),
                ft.Text("生成密码", size=16, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            height=52, bgcolor=THEME_COLOR, border_radius=12,
            on_click=do_generate, alignment=ft.alignment.center,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=12,
                color=ft.colors.with_opacity(0.3, THEME_COLOR), offset=ft.Offset(0, 4)),
        )
        
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=16),
                # 密码长度
                ft.Container(content=ft.Row([
                    ft.Text("密码长度", size=14, color=self.clr_text, expand=True),
                    length_text,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.padding.symmetric(horizontal=4)),
                length_slider,
                ft.Container(height=8),
                # 字符类型选项
                ft.Container(content=ft.Column([
                    ft.Row([use_upper, use_lower], spacing=0),
                    ft.Row([use_digits, use_symbols], spacing=0),
                ], spacing=0), padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=16),
                # 结果卡片
                result_card,
                ft.Container(height=16),
                # 生成按钮
                gen_btn,
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

        self.page.update()

    def _show_feedback(self):
        """问题反馈：填写反馈内容后提交到反馈群"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("问题反馈")
        
        # 反馈类型
        type_dropdown = ft.Dropdown(
            label="反馈类型", width=340, border_radius=10,
            options=[
                ft.dropdown.Option("bug", "Bug反馈"),
                ft.dropdown.Option("suggestion", "功能建议"),
                ft.dropdown.Option("complaint", "投诉"),
                ft.dropdown.Option("other", "其他问题"),
            ],
            value="bug",
        )
        
        # 字数统计
        char_count = ft.Text("0/20", size=12, color=self.clr_text2)
        
        # 反馈内容
        content_field = ft.TextField(
            label="问题描述（至少20字）", width=340, border_radius=10,
            multiline=True, min_lines=6, max_lines=12,
            hint_text="请详细描述您遇到的问题或建议，至少20个字...",
            on_change=lambda e: (setattr(char_count, "value", f"{len(e.control.value.strip())}/20"),
                setattr(char_count, "color", THEME_COLOR if len(e.control.value.strip()) >= 20 else self.clr_text2),
                self.page.update()),
        )
        
        # QQ号（可选）
        qq_field = ft.TextField(
            label="QQ号（选填）", width=340, border_radius=10,
            hint_text="方便我们联系您",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        # 邮箱（可选）
        email_field = ft.TextField(
            label="邮箱（选填）", width=340, border_radius=10,
            hint_text="方便我们联系您",
        )
        
        def do_submit(e):
            feedback_type = type_dropdown.value or "bug"
            feedback_content = content_field.value.strip()
            qq = qq_field.value.strip()
            email = email_field.value.strip()
            
            if not feedback_content:
                self._show_toast("请填写问题描述")
                return
            
            if len(feedback_content) < 20:
                self._show_toast(f"问题描述至少需要20个字，当前{len(feedback_content)}字")
                return
            
            # 获取当前用户ID
            user_id = None
            if self.current_user:
                user_id = self.current_user.get("id")
            if not user_id:
                self._show_toast("请先登录")
                return
            
            # 禁用按钮，显示发送中
            submit_btn.disabled = True
            submit_btn.opacity = 0.5
            self.page.update()
            self._show_toast("正在提交反馈...")
            
            # 构建请求体
            body = {
                "user_id": user_id,
                "feedback_type": feedback_type,
                "content": feedback_content,
            }
            if qq:
                body["qq"] = qq
            if email:
                body["email"] = email
            
            # 调用反馈API
            def submit_thread():
                try:
                    success, result = self._remote_api_request("POST", "feedback", body=body)
                    if success and result.get("ok"):
                        def on_success():
                            self._show_toast("反馈提交成功，感谢您的反馈！")
                            # 自动返回上一页
                            self.page.run_thread(self._back_to_features)
                        self.page.run_thread(on_success)
                    else:
                        error_msg = result.get("msg", "提交失败") if isinstance(result, dict) else str(result)
                        def on_fail():
                            self._show_toast(f"提交失败：{error_msg}")
                            submit_btn.disabled = False
                            submit_btn.opacity = 1.0
                            self.page.update()
                        self.page.run_thread(on_fail)
                except Exception as ex:
                    def on_error():
                        self._show_toast(f"提交失败：{str(ex)[:30]}")
                        submit_btn.disabled = False
                        submit_btn.opacity = 1.0
                        self.page.update()
                    self.page.run_thread(on_error)
            
            threading.Thread(target=submit_thread, daemon=True).start()
        
        # 提交按钮
        submit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SEND, size=20, color=ft.colors.WHITE),
                ft.Container(width=8),
                ft.Text("提交反馈", size=16, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            height=52, bgcolor=THEME_COLOR, border_radius=12,
            on_click=do_submit, alignment=ft.alignment.center,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=12,
                color=ft.colors.with_opacity(0.3, THEME_COLOR), offset=ft.Offset(0, 4)),
        )
        
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=16),
                # 说明卡片
                ft.Container(content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.INFO_OUTLINE, size=18, color=THEME_COLOR),
                        ft.Container(width=8),
                        ft.Text("您的反馈将提交到反馈群，我们会尽快处理", size=13, color=self.clr_text2),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=0), padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=16),
                type_dropdown,
                ft.Container(height=12),
                content_field,
                # 字数统计
                ft.Container(content=ft.Row([
                    ft.Container(expand=True),
                    char_count,
                ], spacing=0), padding=ft.padding.only(right=4, top=2)),
                ft.Container(height=12),
                qq_field,
                ft.Container(height=12),
                email_field,
                ft.Container(height=24),
                submit_btn,
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

        self.page.update()

    def _show_color_tools(self):
        """颜色工具：颜色拾取 + 屏幕取色（合并页面）"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("颜色工具")

        cc = {"hex": "#6366F1", "r": 99, "g": 102, "b": 241}
        history_colors = []
        history_row = ft.Row([], spacing=6, wrap=True)

        # ===== 颜色拾取部分 =====
        preview = ft.Container(width=80, height=80, bgcolor="#6366F1", border_radius=40,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=16, color=ft.colors.with_opacity(0.4, "#6366F1")))
        hex_field = ft.TextField(label="HEX", value="#6366F1", text_size=14, height=42,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.WHITE), border_color=ft.colors.GREY_400,
            focused_border_color=THEME_COLOR, color=self.clr_text, content_padding=8)
        rgb_text = ft.Text("rgb(99, 102, 241)", size=13, color=self.clr_text2, selectable=True)

        r_slider = ft.Slider(min=0, max=255, value=99, active_color=ft.colors.RED,
            on_change=lambda e: self._color_slider_change(cc, "r", int(e.control.value), preview, hex_field, rgb_text))
        g_slider = ft.Slider(min=0, max=255, value=102, active_color=ft.colors.GREEN,
            on_change=lambda e: self._color_slider_change(cc, "g", int(e.control.value), preview, hex_field, rgb_text))
        b_slider = ft.Slider(min=0, max=255, value=241, active_color=ft.colors.BLUE,
            on_change=lambda e: self._color_slider_change(cc, "b", int(e.control.value), preview, hex_field, rgb_text))

        def on_hex_submit(e):
            v = (hex_field.value or "").strip()
            if not v.startswith("#"): v = "#" + v
            if len(v) == 7:
                try:
                    h = v.lstrip("#")
                    cc["hex"], cc["r"], cc["g"], cc["b"] = v, int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                    self._color_refresh_ui(cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider)
                except: pass
        hex_field.on_submit = on_hex_submit

        def set_preset(hex_c):
            def handler(e):
                h = hex_c.lstrip("#")
                cc["hex"], cc["r"], cc["g"], cc["b"] = hex_c, int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                self._color_refresh_ui(cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider)
            return handler

        def copy_hex(e): self._copy_text(cc["hex"], "HEX已复制")
        def copy_rgb(e): self._copy_text(rgb_text.value, "RGB已复制")

        # 色板
        palette_colors = ["#FF0000","#FF7F00","#FFFF00","#00FF00","#00FFFF","#0000FF","#8B00FF",
                          "#FF1493","#FF69B4","#FFA07A","#FFD700","#98FB98","#87CEEB","#DDA0DD",
                          "#000000","#333333","#666666","#999999","#CCCCCC","#FFFFFF","#8B4513","#2F4F4F"]
        palette_rows = []
        for i in range(0, len(palette_colors), 7):
            items = []
            for c in palette_colors[i:i+7]:
                items.append(ft.Container(width=34, height=34, bgcolor=c, border_radius=8,
                    border=ft.border.all(1, ft.colors.GREY_300), on_click=set_preset(c), ink=True))
            palette_rows.append(ft.Row(items, spacing=5, alignment=ft.MainAxisAlignment.CENTER))
            palette_rows.append(ft.Container(height=5))

        # ===== 屏幕取色部分 =====
        screen_preview = ft.Container(width=50, height=50, bgcolor="#CCCCCC", border_radius=25,
            border=ft.border.all(2, ft.colors.GREY_300))
        screen_hex = ft.Text("#CCCCCC", size=14, weight=ft.FontWeight.BOLD, color=self.clr_text)
        screen_status = ft.Text("点击按钮开始屏幕取色", size=12, color=self.clr_text2)

        def start_screen_pick(e):
            try:
                import tkinter as tk
                from PIL import ImageGrab
                root = tk.Tk()
                root.attributes("-fullscreen", True)
                root.attributes("-alpha", 0.25)
                root.configure(cursor="crosshair")
                root.attributes("-topmost", True)
                info = tk.Label(root, text="左键点击取色 | 右键/ESC取消", font=("Arial", 16),
                    bg="black", fg="white", padx=20, pady=10)
                info.pack(pady=40)
                result = {"color": None}

                def on_click(event):
                    if event.num == 1:
                        try:
                            img = ImageGrab.grab().load()
                            r, g, b = img[event.x_root, event.y_root][:3]
                            result["color"] = (r, g, b)
                        except: pass
                        root.destroy()
                    elif event.num == 3:
                        root.destroy()
                def on_escape(event): root.destroy()
                root.bind("<Button>", on_click)
                root.bind("<Escape>", on_escape)
                root.mainloop()

                if result["color"]:
                    r, g, b = result["color"]
                    hex_c = "#{:02X}{:02X}{:02X}".format(r, g, b)
                    screen_preview.bgcolor = hex_c
                    screen_hex.value = hex_c
                    screen_status.value = "取色成功！点击复制"
                    # 同步到颜色拾取
                    cc["hex"], cc["r"], cc["g"], cc["b"] = hex_c, r, g, b
                    self._color_refresh_ui(cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider)
                    # 历史记录
                    history_colors.insert(0, hex_c)
                    if len(history_colors) > 10: history_colors.pop()
                    history_row.controls.clear()
                    for hc in history_colors:
                        history_row.controls.append(ft.Container(
                            width=32, height=32, bgcolor=hc, border_radius=8,
                            border=ft.border.all(1, ft.colors.GREY_300),
                            on_click=lambda e, c=hc: self._copy_text(c, "已复制: "+c), ink=True))
                    self.page.update()
                else:
                    screen_status.value = "已取消取色"
                    self.page.update()
            except Exception as ex:
                screen_status.value = "取色失败: " + str(ex)[:20]
                self.page.update()

        pick_btn = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.COLORIZE, size=18, color=ft.colors.WHITE),
                ft.Text("屏幕取色", size=14, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            height=46, bgcolor=ft.colors.CYAN, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=start_screen_pick)

        # ===== 组装页面 =====
        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                # 颜色拾取区
                ft.Container(content=ft.Text("颜色拾取", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text),
                    padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=8),
                ft.Row([preview, ft.Container(width=12),
                    ft.Column([rgb_text, ft.Container(height=4), hex_field], spacing=0, expand=True)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                r_slider, g_slider, b_slider,
                ft.Container(height=4),
                ft.Row([
                    ft.ElevatedButton("复制HEX", height=40, bgcolor=THEME_COLOR,
                        style=ft.ButtonStyle(color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10)), on_click=copy_hex),
                    ft.ElevatedButton("复制RGB", height=40, bgcolor=ft.colors.GREEN,
                        style=ft.ButtonStyle(color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10)), on_click=copy_rgb),
                ], spacing=8),
                ft.Container(height=10),
                ft.Text("色板", size=13, weight=ft.FontWeight.W_600, color=self.clr_text),
                ft.Container(height=6),
                *palette_rows,
                ft.Container(height=16),
                ft.Container(height=1, bgcolor=self.clr_border),
                ft.Container(height=12),
                # 屏幕取色区
                ft.Container(content=ft.Text("屏幕取色", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text),
                    padding=ft.padding.symmetric(horizontal=4)),
                ft.Container(height=8),
                ft.Row([screen_preview, ft.Container(width=10),
                    ft.Column([screen_hex, screen_status], spacing=2, expand=True)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=8),
                pick_btn,
                ft.Container(height=8),
                ft.Text("取色历史（点击复制）", size=12, color=self.clr_text2),
                ft.Container(height=4),
                history_row,
                ft.Container(height=20),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _color_slider_change(self, cc, channel, val, preview, hex_field, rgb_text):
        """RGB滑块变化"""
        cc[channel] = val
        cc["hex"] = "#{:02X}{:02X}{:02X}".format(cc["r"], cc["g"], cc["b"])
        preview.bgcolor = cc["hex"]
        preview.shadow = ft.BoxShadow(spread_radius=2, blur_radius=16, color=ft.colors.with_opacity(0.4, cc["hex"]))
        hex_field.value = cc["hex"]
        rgb_text.value = "rgb({}, {}, {})".format(cc["r"], cc["g"], cc["b"])
        self.page.update()

    def _color_refresh_ui(self, cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider):
        """刷新颜色UI"""
        preview.bgcolor = cc["hex"]
        preview.shadow = ft.BoxShadow(spread_radius=2, blur_radius=16, color=ft.colors.with_opacity(0.4, cc["hex"]))
        hex_field.value = cc["hex"]
        rgb_text.value = "rgb({}, {}, {})".format(cc["r"], cc["g"], cc["b"])
        r_slider.value = cc["r"]; g_slider.value = cc["g"]; b_slider.value = cc["b"]
        self.page.update()

    def _show_color_picker(self):
        """颜色拾取器：大预览+RGB滑块+HEX输入+渐变色板+预设色板"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = ft.ScrollMode.AUTO
        self._feature_page_header("颜色拾取")
        cc = {"hex": "#6366F1", "r": 99, "g": 102, "b": 241}

        # 大预览圆
        preview = ft.Container(width=100, height=100, bgcolor="#6366F1", border_radius=50,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.colors.with_opacity(0.4, "#6366F1")))
        hex_field = ft.TextField(label="HEX", value="#6366F1", text_size=15,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.WHITE), border_color=ft.colors.GREY_400,
            focused_border_color=THEME_COLOR, color=self.clr_text, content_padding=10, height=44)
        rgb_text = ft.Text("rgb(99, 102, 241)", size=14, color=self.clr_text2, selectable=True)

        r_slider = ft.Slider(min=0, max=255, value=99, active_color=ft.colors.RED, on_change=lambda e: self._on_color_slider(cc, "r", int(e.control.value), preview, hex_field, rgb_text, r_val, g_val, b_val))
        g_slider = ft.Slider(min=0, max=255, value=102, active_color=ft.colors.GREEN, on_change=lambda e: self._on_color_slider(cc, "g", int(e.control.value), preview, hex_field, rgb_text, r_val, g_val, b_val))
        b_slider = ft.Slider(min=0, max=255, value=241, active_color=ft.colors.BLUE, on_change=lambda e: self._on_color_slider(cc, "b", int(e.control.value), preview, hex_field, rgb_text, r_val, g_val, b_val))
        r_val = ft.Text("99", size=12, color=ft.colors.RED, width=30, text_align=ft.TextAlign.RIGHT)
        g_val = ft.Text("102", size=12, color=ft.colors.GREEN, width=30, text_align=ft.TextAlign.RIGHT)
        b_val = ft.Text("241", size=12, color=ft.colors.BLUE, width=30, text_align=ft.TextAlign.RIGHT)

        def on_hex_submit(e):
            v = (hex_field.value or "").strip()
            if not v.startswith("#"): v = "#" + v
            if len(v) == 7:
                try:
                    h = v.lstrip("#")
                    cc["hex"], cc["r"], cc["g"], cc["b"] = v, int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                    self._refresh_color_ui(cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val)
                except: pass
        hex_field.on_submit = on_hex_submit

        def copy_hex(e): self._copy_text(cc["hex"], "HEX已复制")
        def copy_rgb(e): self._copy_text(rgb_text.value, "RGB已复制")

        # 渐变色板
        gradient_colors = ["#FF0000","#FF7F00","#FFFF00","#00FF00","#00FFFF","#0000FF","#8B00FF",
                           "#FF1493","#FF69B4","#FFB6C1","#FFA07A","#FFD700","#98FB98","#87CEEB",
                           "#DDA0DD","#F0E68C","#D2B48C","#BC8F8F","#708090","#2F4F4F","#191970","#800000"]
        grad_rows = []
        for i in range(0, len(gradient_colors), 7):
            items = []
            for c in gradient_colors[i:i+7]:
                items.append(ft.Container(width=36, height=36, bgcolor=c, border_radius=8,
                    on_click=lambda e, col=c: self._set_color(cc, col, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val), ink=True))
            grad_rows.append(ft.Row(items, spacing=6, alignment=ft.MainAxisAlignment.CENTER))
            grad_rows.append(ft.Container(height=6))

        # 预设色板
        preset_colors = ["#000000","#333333","#666666","#999999","#CCCCCC","#FFFFFF",
                         "#E53935","#FB8C00","#FDD835","#43A047","#00ACC1","#1E88E5","#5E35B1","#D81B60"]
        preset_rows = []
        for i in range(0, len(preset_colors), 7):
            items = []
            for c in preset_colors[i:i+7]:
                items.append(ft.Container(width=36, height=36, bgcolor=c, border_radius=8,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    on_click=lambda e, col=c: self._set_color(cc, col, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val), ink=True))
            preset_rows.append(ft.Row(items, spacing=6, alignment=ft.MainAxisAlignment.CENTER))
            preset_rows.append(ft.Container(height=6))

        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=12),
                ft.Container(content=preview, alignment=ft.alignment.center),
                ft.Container(height=12),
                ft.Container(content=rgb_text, alignment=ft.alignment.center),
                ft.Container(height=12),
                hex_field,
                ft.Container(height=6),
                ft.Row([ft.Text("R", size=12, color=ft.colors.RED, width=12), r_slider, r_val], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([ft.Text("G", size=12, color=ft.colors.GREEN, width=12), g_slider, g_val], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([ft.Text("B", size=12, color=ft.colors.BLUE, width=12), b_slider, b_val], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Row([
                    ft.Container(content=ft.Text("复制HEX", size=13, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
                        expand=True, height=42, bgcolor=THEME_COLOR, border_radius=10, alignment=ft.alignment.center, on_click=copy_hex, ink=True),
                    ft.Container(content=ft.Text("复制RGB", size=13, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
                        expand=True, height=42, bgcolor=ft.colors.GREEN, border_radius=10, alignment=ft.alignment.center, on_click=copy_rgb, ink=True),
                ], spacing=8),
                ft.Container(height=16),
                ft.Text("渐变色板", size=14, weight=ft.FontWeight.W_600, color=self.clr_text),
                ft.Container(height=8),
                *grad_rows,
                ft.Container(height=8),
                ft.Text("常用色板", size=14, weight=ft.FontWeight.W_600, color=self.clr_text),
                ft.Container(height=8),
                *preset_rows,
                ft.Container(height=20),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def _on_color_slider(self, cc, channel, val, preview, hex_field, rgb_text, r_val, g_val, b_val):
        """RGB滑块变化时更新颜色"""
        cc[channel] = val
        cc["hex"] = "#{:02X}{:02X}{:02X}".format(cc["r"], cc["g"], cc["b"])
        preview.bgcolor = cc["hex"]
        preview.shadow = ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.colors.with_opacity(0.4, cc["hex"]))
        hex_field.value = cc["hex"]
        rgb_text.value = "rgb({}, {}, {})".format(cc["r"], cc["g"], cc["b"])
        r_val.value = str(cc["r"]); g_val.value = str(cc["g"]); b_val.value = str(cc["b"])
        self.page.update()

    def _set_color(self, cc, hex_color, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val):
        """点击色板设置颜色"""
        h = hex_color.lstrip("#")
        cc["hex"], cc["r"], cc["g"], cc["b"] = hex_color, int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        self._refresh_color_ui(cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val)

    def _refresh_color_ui(self, cc, preview, hex_field, rgb_text, r_slider, g_slider, b_slider, r_val, g_val, b_val):
        """刷新所有颜色相关UI"""
        preview.bgcolor = cc["hex"]
        preview.shadow = ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.colors.with_opacity(0.4, cc["hex"]))
        hex_field.value = cc["hex"]
        rgb_text.value = "rgb({}, {}, {})".format(cc["r"], cc["g"], cc["b"])
        r_slider.value = cc["r"]; g_slider.value = cc["g"]; b_slider.value = cc["b"]
        r_val.value = str(cc["r"]); g_val.value = str(cc["g"]); b_val.value = str(cc["b"])
        self.page.update()

    def _show_screen_color_picker(self):
        """屏幕取色器：悬浮窗吸取屏幕任意位置颜色"""
        self._hide_navbar()
        self.content.controls.clear()
        self._feature_page_header("屏幕取色")

        picked_preview = ft.Container(width=80, height=80, bgcolor="#CCCCCC", border_radius=16,
            border=ft.border.all(2, ft.colors.GREY_300))
        picked_hex = ft.Text("#CCCCCC", size=18, weight=ft.FontWeight.BOLD, color=self.clr_text)
        picked_rgb = ft.Text("rgb(204, 204, 204)", size=13, color=self.clr_text2)
        status_text = ft.Text("点击下方按钮开始取色", size=13, color=self.clr_text2)
        history_colors = []
        history_row = ft.Row([], spacing=6, wrap=True)

        def start_picker(e):
            try:
                import tkinter as tk
                from PIL import ImageGrab
                root = tk.Tk()
                root.attributes("-fullscreen", True)
                root.attributes("-alpha", 0.3)
                root.configure(cursor="crosshair")
                root.attributes("-topmost", True)

                info_label = tk.Label(root, text="点击任意位置取色 | 右键或ESC取消",
                    font=("Arial", 14), bg="black", fg="white", padx=20, pady=10)
                info_label.pack(pady=50)

                result = {"color": None, "x": 0, "y": 0}

                def on_click(event):
                    if event.num == 1:  # 左键取色
                        result["x"], result["y"] = event.x_root, event.y_root
                        try:
                            img = ImageGrab.grab().load()
                            r, g, b = img[event.x_root, event.y_root][:3]
                            result["color"] = (r, g, b)
                        except: pass
                        root.destroy()
                    elif event.num == 3:  # 右键取消
                        root.destroy()

                def on_escape(event):
                    root.destroy()

                root.bind("<Button>", on_click)
                root.bind("<Escape>", on_escape)
                root.mainloop()

                if result["color"]:
                    r, g, b = result["color"]
                    hex_c = "#{:02X}{:02X}{:02X}".format(r, g, b)
                    picked_preview.bgcolor = hex_c
                    picked_hex.value = hex_c
                    picked_rgb.value = "rgb({}, {}, {})".format(r, g, b)
                    status_text.value = "取色成功！位置: ({}, {})".format(result["x"], result["y"])
                    # 添加到历史
                    history_colors.insert(0, hex_c)
                    if len(history_colors) > 12: history_colors.pop()
                    history_row.controls.clear()
                    for hc in history_colors:
                        history_row.controls.append(ft.Container(
                            width=36, height=36, bgcolor=hc, border_radius=8,
                            border=ft.border.all(1, ft.colors.GREY_300),
                            on_click=lambda e, c=hc: self._copy_text(c, "已复制: "+c), ink=True,
                            tooltip=hc))
                    self.page.update()
                else:
                    status_text.value = "已取消取色"
                    self.page.update()
            except Exception as ex:
                status_text.value = "取色失败: " + str(ex)[:30]
                self.page.update()

        def copy_picked(e):
            if picked_hex.value and picked_hex.value != "#CCCCCC":
                self._copy_text(picked_hex.value, "颜色已复制")

        start_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.icons.COLORIZE, size=20, color=ft.colors.WHITE),
                ft.Text("开始屏幕取色", size=16, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            height=52, bgcolor=THEME_COLOR, border_radius=14,
            alignment=ft.alignment.center, on_click=start_picker, ink=True,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.colors.with_opacity(0.3, THEME_COLOR)),
        )
        copy_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.icons.COPY, size=18, color=ft.colors.WHITE),
                ft.Text("复制颜色", size=15, weight=ft.FontWeight.W_600, color=ft.colors.WHITE)],
                alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            height=46, bgcolor=ft.colors.GREEN, border_radius=12,
            alignment=ft.alignment.center, on_click=copy_picked, ink=True,
        )

        self._feature_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(height=16),
                ft.Container(content=picked_preview, alignment=ft.alignment.center),
                ft.Container(height=12),
                ft.Container(content=picked_hex, alignment=ft.alignment.center),
                ft.Container(height=4),
                ft.Container(content=picked_rgb, alignment=ft.alignment.center),
                ft.Container(height=6),
                ft.Container(content=status_text, alignment=ft.alignment.center),
                ft.Container(height=20),
                start_btn,
                ft.Container(height=10),
                copy_btn,
                ft.Container(height=20),
                ft.Text("历史颜色（点击复制）", size=14, weight=ft.FontWeight.W_600, color=self.clr_text),
                ft.Container(height=8),
                history_row,
                ft.Container(height=20),
                ft.Container(content=ft.Column([
                    ft.Text("使用说明", size=13, weight=ft.FontWeight.W_600, color=self.clr_text),
                    ft.Container(height=6),
                    ft.Text('1. 点击开始屏幕取色按钮', size=12, color=self.clr_text2),
                    ft.Text("2. 屏幕变半透明，鼠标变成十字", size=12, color=self.clr_text2),
                    ft.Text("3. 左键点击要取色的位置", size=12, color=self.clr_text2),
                    ft.Text("4. 右键或ESC取消取色", size=12, color=self.clr_text2),
                ], spacing=0), padding=12, bgcolor=self.clr_card, border_radius=12),
                ft.Container(height=20),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=16),
        ))
        self.page.update()

    def render_cloud_drive_page(self):
        """网盘页面 - 远程文件存储与管理（先渲染UI，再后台异步获取数据）"""
        self._show_navbar()  # 主页面显示导航栏
        self.content.controls.clear()
        self.content.scroll = None  # 外层不滚动，用内层Stack

        # 内层内容Column（可滚动）
        inner_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 顶部标题
        inner_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Text("网盘", size=28, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 50, 12, 10), bgcolor=self.clr_bg,
        ))
        inner_content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        # 我的网盘进度条卡片（先用默认值，后面异步更新）
        self._cloud_used_text = ft.Text("0.0 MB / 5 GB", size=12, color=self.clr_text2)
        self._cloud_pct_text = ft.Text("已使用 0.0%，剩余 5120 MB", size=11, color=self.clr_text2)
        self._cloud_progress = ft.ProgressBar(value=0, width=None, color=THEME_COLOR,
            bgcolor=ft.colors.with_opacity(0.15, THEME_COLOR), border_radius=4)
        inner_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.CLOUD, size=20, color=THEME_COLOR),
                    ft.Container(width=8),
                    ft.Text("我的网盘", size=16, weight=ft.FontWeight.W_600, color=self.clr_text, expand=True),
                    self._cloud_used_text,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=10),
                self._cloud_progress,
                ft.Container(height=6),
                self._cloud_pct_text,
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14, padding=ft.padding.all(16), margin=ft.padding.only(16, 12, 16, 0),
        ))

        # 快捷入口小卡片（一行两个）
        inner_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CLOUD_OUTLINED, size=28, color=THEME_COLOR),
                        ft.Container(height=8),
                        ft.Text("我的资源", size=13, weight=ft.FontWeight.W_600, color=self.clr_text),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center, on_click=lambda e: self._show_my_resources(),
                    ink=True,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.HOURGLASS_EMPTY_OUTLINED, size=28, color=ft.colors.GREY_400),
                        ft.Container(height=8),
                        ft.Text("暂存", size=13, weight=ft.FontWeight.W_600, color=self.clr_text2),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center, on_click=lambda e: self._show_toast("功能暂存中"),
                    ink=True,
                ),
            ], spacing=0),
            margin=ft.padding.only(16, 12, 16, 0),
        ))

        # 数据统计标题
        inner_content.controls.append(ft.Container(
            content=ft.Text("数据统计", size=14, weight=ft.FontWeight.W_600, color=self.clr_text2),
            padding=ft.padding.only(16, 16, 16, 8),
        ))

        # 数据统计四个卡片（2x2，跟"我的资源"卡片一样大）
        self._cloud_stats_view = ft.Column([], spacing=0)
        self._stats_view_count = ft.Text("0", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text)
        self._stats_download_count = ft.Text("0", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text)
        # 第一行
        self._cloud_stats_view.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.VISIBILITY_OUTLINED, size=26, color=ft.colors.BLUE),
                        ft.Container(height=6),
                        ft.Text("浏览人数", size=12, color=self.clr_text2),
                        self._stats_view_count,
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center, on_click=lambda e: self._show_cloud_stats_detail("浏览人数"), ink=True,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.DOWNLOAD_OUTLINED, size=26, color=ft.colors.GREEN),
                        ft.Container(height=6),
                        ft.Text("下载次数", size=12, color=self.clr_text2),
                        self._stats_download_count,
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center, on_click=lambda e: self._show_cloud_stats_detail("下载次数"), ink=True,
                ),
            ], spacing=0),
            margin=ft.padding.only(16, 0, 16, 0),
        ))
        self._cloud_stats_view.controls.append(ft.Container(height=12))
        # 第二行
        self._cloud_stats_view.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ADD_OUTLINED, size=26, color=self.clr_text2),
                        ft.Container(height=6),
                        ft.Text("待添加", size=12, color=self.clr_text2),
                        ft.Text("-", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text2),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ADD_OUTLINED, size=26, color=self.clr_text2),
                        ft.Container(height=6),
                        ft.Text("待添加", size=12, color=self.clr_text2),
                        ft.Text("-", size=16, weight=ft.FontWeight.BOLD, color=self.clr_text2),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, height=90, bgcolor=self.clr_card, border_radius=12,
                    alignment=ft.alignment.center,
                ),
            ], spacing=0),
            margin=ft.padding.only(16, 0, 16, 0),
        ))
        inner_content.controls.append(self._cloud_stats_view)
        inner_content.controls.append(ft.Container(height=80))

        # 网盘主页不显示加号，加号在「我的资源」页面显示
        self.content.controls.append(inner_content)

        # 立即更新UI（先显示出来）
        try:
            self.page.update()
        except Exception as e:
            print(f"网盘页面UI更新失败: {e}")

        # ===== 第二步：后台异步获取远程数据，获取完成后更新UI =====
        def _load_cloud_data_async():
            try:
                # 1. 获取已用空间
                try:
                    total_gb = 5.0
                    used_mb = self._get_cloud_used_mb()
                    used_pct = min(100, used_mb / (total_gb * 1024) * 100)
                    self._cloud_used_text.value = f"{used_mb:.1f} MB / {total_gb:.0f} GB"
                    self._cloud_pct_text.value = f"已使用 {used_pct:.1f}%，剩余 {(total_gb*1024-used_mb):.0f} MB"
                    self._cloud_progress.value = used_pct / 100
                except Exception as e:
                    print(f"获取网盘空间失败: {e}")

                # 2. 获取网盘统计数据（自己计算：把所有网盘的浏览/下载次数加起来，跟详情页口径一致）
                try:
                    total_view = 0
                    total_download = 0
                    if self.current_user:
                        user_id = self.current_user.get("id", "")
                        ok, result = self._remote_api_request("GET", "user-folders", params={"user_id": user_id, "parent_id": 0})
                        if ok and result:
                            folders = result.get("folders", [])
                            for folder in folders:
                                total_view += folder.get("view_count", 0)
                                total_download += folder.get("download_count", 0)
                    self._stats_view_count.value = str(total_view)
                    self._stats_download_count.value = str(total_download)
                except Exception as e:
                    print(f"获取网盘统计失败: {e}")

                try:
                    self.page.update()
                except Exception as e:
                    print(f"网盘页面异步更新失败: {e}")
            except Exception as e:
                print(f"网盘数据异步加载失败: {e}")

        try:
            import threading
            threading.Thread(target=_load_cloud_data_async, daemon=True).start()
        except Exception as e:
            print(f"启动网盘数据加载线程失败: {e}")


    def _show_my_resources(self, folder_id=0, folder_name="我的资源"):
        """显示我的资源页面"""
        self.current_folder_id = folder_id
        self.content.controls.clear()
        self.content.scroll = None  # 顶部标题固定
        self._hide_navbar()
        is_root = folder_id == 0
        title_text = folder_name if not is_root else "我的资源"
        back_action = lambda e: self._back_to_parent_folder() if not is_root else self._back_to_cloud_drive()
        
        # 标题栏（包含路径）
        title_row = [
            ft.IconButton(ft.icons.ARROW_BACK, icon_size=24, icon_color=self.clr_text, on_click=back_action),
            ft.Container(width=8),
        ]
        # 标题+路径（垂直排列）
        title_col_items = [ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=self.clr_text)]
        if not is_root and self.folder_path:
            path_text = " / ".join([f[1] for f in self.folder_path])
            title_col_items.append(ft.Text(path_text, size=11, color=self.clr_text2))
        title_row.append(ft.Column(title_col_items, spacing=2, expand=True))
        title_row.append(ft.IconButton(ft.icons.ADD_CIRCLE, icon_size=28, icon_color=THEME_COLOR, on_click=lambda e: self._show_cloud_upload_menu()))
        
        self.content.controls.append(ft.Container(
            content=ft.Row(title_row, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(12, 50, 12, 10), bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))
        
        content_area = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.content.controls.append(content_area)
        self.page.floating_action_button = None
        self.page.update()
        
        # 先用缓存快速显示（如果有缓存）
        cached_files = None
        try:
            if is_root and hasattr(self, '_cached_cloud_files') and self._cached_cloud_files:
                cached_files = self._cached_cloud_files
        except:
            pass
        
        if cached_files:
            # 有缓存，直接显示缓存
            def render_cached():
                content_area.controls.clear()
                for f in cached_files:
                    is_folder = f.get("type") == "folder"
                    if is_root and is_folder:
                        icon_color = ft.colors.BLUE
                        icon = ft.icons.CLOUD_OUTLINED
                        info_text = f.get("info", "网盘").replace("文件夹", "网盘")
                        raw_name = f.get("name", "未命名")
                        display_name = raw_name if raw_name.startswith("我的云盘") else f"我的云盘-{raw_name}"
                    else:
                        icon_color = ft.colors.BLUE if is_folder else ft.colors.ORANGE
                        icon = ft.icons.FOLDER if is_folder else ft.icons.INSERT_DRIVE_FILE_OUTLINED
                        info_text = f.get("info", "")
                        display_name = f.get("name", "未命名")
                    on_click = None
                    if is_folder:
                        on_click = lambda e, fi=f: self._open_folder(fi)
                    content_area.controls.append(ft.Container(
                        content=ft.Row([
                            ft.Container(content=ft.Icon(icon, size=22, color=ft.colors.WHITE), width=40, height=40, bgcolor=icon_color, border_radius=10, alignment=ft.alignment.center),
                            ft.Container(width=10),
                            ft.Column([
                                ft.Text(display_name, size=14, weight=ft.FontWeight.W_500, color=self.clr_text, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Container(height=2),
                                ft.Text(info_text, size=11, color=self.clr_text2),
                            ], spacing=0, expand=True),
                            ft.PopupMenuButton(items=self._build_cloud_menu_items(f, is_root), icon_color=self.clr_text2),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.clr_card, border_radius=12, padding=ft.padding.all(12), margin=ft.padding.only(16, 4, 16, 4),
                        on_click=on_click, ink=True,
                    ))
                self.page.update()
            try:
                render_cached()
            except:
                pass
        else:
            # 没有缓存，显示加载中
            loading_box = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, color=THEME_COLOR),
                    ft.Container(height=12),
                    ft.Text("加载中...", size=14, color=self.clr_text2),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(top=150), alignment=ft.alignment.center,
            )
            content_area.controls.append(loading_box)
            self.page.update()
        
        # 后台获取最新数据
        def load_files():
            try:
                files = self._get_cloud_files(folder_id=folder_id, use_cache=False)
                def update_ui():
                    content_area.controls.clear()
                    if not files:
                        empty_icon = ft.icons.CLOUD_OUTLINED if is_root else ft.icons.FOLDER_OFF_OUTLINED
                        empty_text = "暂无网盘" if is_root else "暂无文件"
                        empty_hint = "点击右上角加号创建我的网盘" if is_root else "点击右上角加号上传文件或创建文件夹"
                        content_area.controls.append(ft.Container(
                            content=ft.Column([
                                ft.Icon(empty_icon, size=64, color=self.clr_text2),
                                ft.Container(height=12),
                                ft.Text(empty_text, size=16, color=self.clr_text2, weight=ft.FontWeight.W_500),
                                ft.Container(height=6),
                                ft.Text(empty_hint, size=13, color=self.clr_text2),
                            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.only(top=120), alignment=ft.alignment.center,
                        ))
                    else:
                        for f in files:
                            is_folder = f.get("type") == "folder"
                            if is_root and is_folder:
                                icon_color = ft.colors.BLUE
                                icon = ft.icons.CLOUD_OUTLINED
                                info_text = f.get("info", "网盘").replace("文件夹", "网盘")
                                raw_name = f.get("name", "未命名")
                                display_name = raw_name if raw_name.startswith("我的云盘") else f"我的云盘-{raw_name}"
                            else:
                                icon_color = ft.colors.BLUE if is_folder else ft.colors.ORANGE
                                icon = ft.icons.FOLDER if is_folder else ft.icons.INSERT_DRIVE_FILE_OUTLINED
                                info_text = f.get("info", "")
                                display_name = f.get("name", "未命名")
                            on_click = None
                            if is_folder:
                                on_click = lambda e, fi=f: self._open_folder(fi)
                            content_area.controls.append(ft.Container(
                                content=ft.Row([
                                    ft.Container(content=ft.Icon(icon, size=22, color=ft.colors.WHITE), width=40, height=40, bgcolor=icon_color, border_radius=10, alignment=ft.alignment.center),
                                    ft.Container(width=10),
                                    ft.Column([
                                        ft.Text(display_name, size=14, weight=ft.FontWeight.W_500, color=self.clr_text, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Container(height=2),
                                        ft.Text(info_text, size=11, color=self.clr_text2),
                                    ], spacing=0, expand=True),
                                    ft.PopupMenuButton(items=self._build_cloud_menu_items(f, is_root), icon_color=self.clr_text2),
                                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                bgcolor=self.clr_card, border_radius=12, padding=ft.padding.all(12), margin=ft.padding.only(16, 4, 16, 4),
                                on_click=on_click, ink=True,
                            ))
                    self.page.update()
                try:
                    update_ui()
                except:
                    self.page.run_thread(update_ui)
            except Exception as e:
                print(f"加载失败: {e}")
        threading.Thread(target=load_files, daemon=True).start()


    def _show_cloud_stats(self, stat_type):
        """显示网盘统计详情（UI，API待对接）"""
        try:
            dlg = ft.AlertDialog(
                title=ft.Text(f"{stat_type}详情", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.BAR_CHART_OUTLINED, size=48, color=self.clr_text2),
                        ft.Container(height=12),
                        ft.Text(f"暂无{stat_type}数据", size=14, color=self.clr_text2),
                        ft.Container(height=6),
                        ft.Text("API待对接", size=12, color=self.clr_text2),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=250, height=180, alignment=ft.alignment.center,
                ),
                actions=[ft.TextButton("关闭", on_click=lambda e: self._close_dialog(dlg))],
            )
            self.page.dialog = dlg
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            self._show_toast("显示统计失败：" + str(e))

    def _menu_action(self, action_func):
        """菜单项点击后延迟执行，解决PopupMenu第一次点击不生效的问题"""
        import threading, time
        def run():
            time.sleep(0.15)  # 等待菜单关闭动画完成
            try:
                self.page.run_thread(action_func)
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()

    def _build_cloud_menu_items(self, fi, is_root):
        """构建网盘/文件的菜单项"""
        items = [
            ft.PopupMenuItem(icon=ft.icons.SHARE_OUTLINED, text="分享链接", on_click=lambda e, item=fi: self._menu_action(lambda: self._share_cloud_file(item))),
        ]
        # 根目录的网盘（文件夹）添加设置公告选项
        if is_root and fi.get("type") == "folder":
            items.append(ft.PopupMenuItem(icon=ft.icons.LINK, text="链接设置", on_click=lambda e, item=fi: self._menu_action(lambda: self._set_cloud_notice(item))))
        items.append(ft.PopupMenuItem(icon=ft.icons.DELETE_OUTLINE, text="删除", on_click=lambda e, item=fi: self._menu_action(lambda: self._delete_cloud_file(item))))
        return items

    def _set_cloud_notice(self, fi):
        """链接设置（网盘名字+公告+提取码）"""
        try:
            folder_name = fi.get("name", "网盘")
            folder_id = fi.get("id", "")
            share_code = fi.get("share_code", fi.get("code", ""))
            
            # 网盘名字输入框
            name_field = ft.TextField(label="网盘名称", width=280, border_radius=8,
                value=folder_name, hint_text="正在获取...")
            # 公告内容输入框
            notice_field = ft.TextField(label="公告内容", width=280, border_radius=8, multiline=True, min_lines=3, max_lines=5,
                hint_text="正在获取...")
            # 提取码输入框（四位，留空则不设置）
            code_field = ft.TextField(label="提取码（留空则不设置）", width=280, border_radius=8,
                hint_text="输入4位提取码", max_length=4,
                counter_text="0/4")
            
            def on_save(e):
                new_name = name_field.value.strip()
                notice_text = notice_field.value.strip()
                extract_code = code_field.value.strip() if code_field.value else ""
                if not new_name:
                    self._show_toast("网盘名称不能为空")
                    return
                if extract_code and len(extract_code) != 4:
                    self._show_toast("提取码必须是4位")
                    return
                if not self.current_user:
                    self._show_toast("请先登录")
                    return
                # 关闭弹窗，显示保存中
                self._close_dialog(dlg)
                self._show_toast("正在保存...")
                # 后台保存
                def do_save():
                    try:
                        try:
                            user_id = int(self.current_user.get("id", 0))
                        except (ValueError, TypeError):
                            user_id = self.current_user.get("id", "")
                        # 调用设置下载页信息API
                        ok, result = self._remote_api_request("PUT", f"download-page/{share_code}",
                            body={"user_id": user_id, "name": new_name, "notice": notice_text, "extract_code": extract_code})
                        if ok and result and result.get("ok"):
                            # 保存成功，清除缓存，刷新当前页面
                            self._cached_cloud_files = None
                            import threading
                            threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
                            # 刷新当前我的资源页面
                            try:
                                self._show_my_resources(folder_id=self.current_folder_id,
                                    folder_name=self.folder_path[-1][1] if self.folder_path else "我的资源")
                            except:
                                pass
                            self._show_toast("保存成功")
                        else:
                            error_msg = result.get("msg", "保存失败") if isinstance(result, dict) else "保存失败"
                            self._show_toast("保存失败：" + str(error_msg))
                    except Exception as ex:
                        self._show_toast("保存失败：" + str(ex)[:20])
                import threading
                threading.Thread(target=do_save, daemon=True).start()
            
            dlg = ft.AlertDialog(
                title=ft.Text("链接设置", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Column([
                    name_field,
                    ft.Container(height=10),
                    notice_field,
                    ft.Container(height=10),
                    code_field,
                ], spacing=0, tight=True, width=280),
                actions=[
                    ft.TextButton("取消", on_click=lambda e: self._close_dialog(dlg)),
                    ft.TextButton("保存", on_click=on_save),
                ],
            )
            # 可靠地显示对话框：先清空旧dialog，再设置新的
            try:
                if self.page.dialog:
                    self.page.dialog.open = False
                self.page.dialog = None
                self.page.update()
            except:
                pass
            import time as _t
            _t.sleep(0.05)
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
            
            # 后台获取当前名字和公告
            def load_current_info():
                try:
                    info = self._get_folder_download_page_info(share_code)
                    def update_fields():
                        if info:
                            if info.get("notice"):
                                notice_field.value = info["notice"]
                                notice_field.hint_text = "输入公告内容"
                            else:
                                notice_field.hint_text = "输入公告内容（当前无公告）"
                            if info.get("extract_code"):
                                code_field.value = info["extract_code"]
                                code_field.hint_text = "已设置提取码"
                                code_field.counter_text = f"{len(info['extract_code'])}/4"
                            else:
                                code_field.hint_text = "输入4位提取码（留空则不设置）"
                                code_field.counter_text = "0/4"
                        else:
                            notice_field.hint_text = "输入公告内容"
                            code_field.hint_text = "输入4位提取码（留空则不设置）"
                        name_field.hint_text = "输入网盘名称"
                        self.page.update()
                    self.page.run_thread(update_fields)
                except Exception as e:
                    print(f"获取下载页信息失败: {e}")
                    def update_hint():
                        name_field.hint_text = "输入网盘名称"
                        notice_field.hint_text = "输入公告内容"
                        self.page.update()
                    self.page.run_thread(update_hint)
            
            import threading
            threading.Thread(target=load_current_info, daemon=True).start()
        except Exception as e:
            self._show_toast("链接设置失败：" + str(e))

    def _open_folder(self, folder_info):
        """打开文件夹，进入子目录"""
        folder_id = folder_info.get("id")
        folder_name = folder_info.get("name", "文件夹")
        if folder_id:
            # 记录路径
            self.folder_path.append((folder_id, folder_name))
            self._show_my_resources(folder_id=folder_id, folder_name=folder_name)

    def _back_to_parent_folder(self):
        """返回上级文件夹"""
        if self.folder_path:
            self.folder_path.pop()
        if self.folder_path:
            parent_id, parent_name = self.folder_path[-1]
            self._show_my_resources(folder_id=parent_id, folder_name=parent_name)
        else:
            self._show_my_resources(folder_id=0, folder_name="我的资源")


    def _back_to_cloud_drive(self):
        """返回网盘主页"""
        self.folder_path = []
        self.current_folder_id = 0
        self._show_navbar()
        self.render_cloud_drive_page()

    def _hide_navbar(self):
        """隐藏底部导航栏（进入子页面时调用）"""
        if hasattr(self, '_navbar_area') and self._navbar_area:
            self._navbar_area.visible = False
        self.page.floating_action_button = None

    def _show_navbar(self):
        """显示底部导航栏（从子页面返回时调用）"""
        if hasattr(self, '_navbar_area') and self._navbar_area:
            self._navbar_area.visible = True
        self.page.floating_action_button = None


    def _share_cloud_file(self, fi):
        """分享文件或文件夹（调用远程API获取分享链接）"""
        if not self.current_user:
            return
        try:
            user_id = int(self.current_user.get("id", 0))
        except (ValueError, TypeError):
            user_id = self.current_user.get("id", "")
        item_id = fi.get("id")
        item_type = fi.get("type", "file")
        if not item_id:
            self._show_toast("分享失败：缺少ID")
            return
        try:
            if item_type == "folder":
                ok, result = self._remote_api_request("POST", f"user-folders/{item_id}/share", body={"user_id": user_id})
            else:
                ok, result = self._remote_api_request("POST", f"user-files/{item_id}/share", body={"user_id": user_id})
            if ok and result:
                data = result.get("data", result)
                share_url = data.get("share_url", "")
                share_code = data.get("share_code", "")
                # 如果没有完整URL，用分享码拼接
                if not share_url and share_code:
                    base_url = APP_CONFIG.get("remote_api_base", "")
                    share_url = f"{base_url}/s/{share_code}"
                # 清理链接，去掉前后空格和换行
                share_url = share_url.strip()
                if share_url:
                    # 确保链接有http前缀
                    if not share_url.startswith("http"):
                        share_url = "https://" + share_url.lstrip("/")
                    # 严格清理链接：去掉所有非打印字符、BOM、前后空格换行
                    import re
                    share_url = re.sub(r'[\x00-\x1f\x7f-\x9f\ufeff]', '', share_url)
                    share_url = share_url.strip()
                    # 用PowerShell Set-Clipboard复制（最可靠，纯文本无隐藏字符）
                    copy_success = False
                    try:
                        import subprocess
                        ps_cmd = f"Set-Clipboard -Value '{share_url}'"
                        subprocess.run(["powershell", "-Command", ps_cmd], 
                            check=False, capture_output=True, timeout=5)
                        copy_success = True
                    except:
                        pass
                    # 备用1：Flet原生剪贴板
                    if not copy_success:
                        try:
                            self.page.set_clipboard(share_url)
                            copy_success = True
                        except:
                            pass
                    # 备用2：Windows clip命令（用UTF-8无BOM）
                    if not copy_success:
                        try:
                            import subprocess
                            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
                            p.communicate(input=share_url.encode("utf-8"))
                            copy_success = True
                        except:
                            pass
                    if copy_success:
                        self._show_toast("分享链接已复制")
                    else:
                        self._show_toast("复制失败，请手动复制")
                else:
                    self._show_toast("获取分享链接失败")
            else:
                error_msg = result.get("msg", "未知错误") if isinstance(result, dict) else str(result)
                self._show_toast("分享失败：" + str(error_msg))
        except Exception as e:
            self._show_toast(f"分享失败: {e}")

    def _show_cloud_upload_menu(self):
        """显示网盘操作菜单
        根目录（我的资源）：只显示创建网盘
        子目录（网盘内）：显示上传文件和创建文件夹
        """
        try:
            is_root = (not hasattr(self, 'current_folder_id')) or self.current_folder_id == 0
            
            def upload_file(e):
                self._close_dialog(dlg)
                self._upload_cloud_file()
            def create_folder(e):
                self._close_dialog(dlg)
                self._create_cloud_folder()
            
            menu_items = []
            if not is_root:
                # 网盘内：上传文件
                menu_items.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.UPLOAD_FILE, size=24, color=THEME_COLOR),
                        ft.Container(width=12),
                        ft.Text("上传文件", size=15, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=upload_file, padding=ft.padding.all(12), border_radius=8,
                ))
                menu_items.append(ft.Container(height=4))
                # 网盘内：创建文件夹
                menu_items.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.CREATE_NEW_FOLDER, size=24, color=THEME_COLOR),
                        ft.Container(width=12),
                        ft.Text("创建文件夹", size=15, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=create_folder, padding=ft.padding.all(12), border_radius=8,
                ))
            else:
                # 根目录：只创建网盘
                menu_items.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.WEB, size=24, color=THEME_COLOR),
                        ft.Container(width=12),
                        ft.Text("创建网盘", size=15, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=create_folder, padding=ft.padding.all(12), border_radius=8,
                ))
            
            title_text = "网盘操作" if not is_root else "我的资源"
            dlg = ft.AlertDialog(
                title=ft.Text(title_text, size=18, weight=ft.FontWeight.BOLD),
                content=ft.Column(menu_items, spacing=0, tight=True, width=280),
                actions=[ft.TextButton("取消", on_click=lambda e: self._close_dialog(dlg))],
            )
            self.page.dialog = dlg
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            self._show_toast("打开菜单失败：" + str(e))

    def _fetch_cloud_stats_from_remote(self):
        """从远程API获取网盘统计信息"""
        if not self.current_user:
            return None
        try:
            user_id = self.current_user.get("id", "")
            ok, result = self._remote_api_request("GET", "user-fm-stats", params={"user_id": user_id})
            if ok and result:
                return result
        except Exception as e:
            print(f"获取网盘统计失败: {e}")
        return None

    def _get_folder_download_page_info(self, share_code):
        """通过下载页API获取文件夹的公告、提取码、浏览次数、下载次数"""
        if not share_code:
            return None
        try:
            ok, result = self._remote_api_request("GET", f"download-page/{share_code}")
            if ok and result and result.get("ok"):
                if result.get("type") == "folder":
                    folder = result.get("folder", {})
                    return {
                        "notice": folder.get("notice", ""),
                        "extract_code": folder.get("extract_code", result.get("extract_code", "")),
                        "view_count": folder.get("view_count", 0),
                        "download_count": folder.get("download_count", 0),
                    }
        except Exception as e:
            print(f"获取下载页信息失败: {e}")
        return None

    def _show_cloud_stats_detail(self, stat_type):
        """显示网盘统计详情（直接用文件夹列表返回的view_count/download_count，无需额外API）"""
        try:
            # 先显示弹窗（加载中）
            loading_content = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=30, height=30, color=THEME_COLOR),
                    ft.Container(height=10),
                    ft.Text("正在加载...", size=13, color=self.clr_text2),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(top=80),
            )
            
            title_with_hint = ft.Column([
                ft.Text(f"{stat_type}详情", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("各网盘分享页统计（文件浏览不计入）", size=11, color=self.clr_text2),
            ], spacing=2)
            
            dlg = ft.AlertDialog(
                title=title_with_hint,
                content=ft.Container(content=loading_content, width=300, height=350),
                actions=[ft.TextButton("关闭", on_click=lambda e: self._close_dialog(dlg))],
            )
            self.page.dialog = dlg
            self.page.dialog.open = True
            self.page.update()
            
            # 后台获取文件夹列表（列表里已经带view_count和download_count）
            def load_folders():
                try:
                    folders = []
                    try:
                        if self.current_user:
                            user_id = self.current_user.get("id", "")
                            ok, result = self._remote_api_request("GET", "user-folders", params={"user_id": user_id, "parent_id": 0})
                            if ok and result:
                                folders = result.get("folders", [])
                    except:
                        pass
                    
                    def show_list():
                        detail_items = []
                        if not folders:
                            detail_items.append(ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.icons.FOLDER_OFF_OUTLINED, size=48, color=self.clr_text2),
                                    ft.Container(height=12),
                                    ft.Text("暂无网盘数据", size=14, color=self.clr_text2),
                                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=ft.padding.all(20),
                            ))
                        else:
                            for folder in folders:
                                folder_name = folder.get("name", "未命名")
                                raw_name = folder_name if folder_name.startswith("我的云盘") else f"我的云盘-{folder_name}"
                                # 直接用文件夹列表返回的统计字段
                                if stat_type == "浏览人数":
                                    count = folder.get("view_count", 0)
                                    color = ft.colors.BLUE
                                else:
                                    count = folder.get("download_count", 0)
                                    color = ft.colors.GREEN
                                detail_items.append(ft.Container(
                                    content=ft.Row([
                                        ft.Container(content=ft.Icon(ft.icons.CLOUD_OUTLINED, size=20, color=ft.colors.WHITE),
                                            width=36, height=36, bgcolor=ft.colors.BLUE, border_radius=8, alignment=ft.alignment.center),
                                        ft.Container(width=10),
                                        ft.Text(raw_name, size=14, weight=ft.FontWeight.W_500, color=self.clr_text, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(str(count), size=14, weight=ft.FontWeight.W_600, color=color),
                                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    bgcolor=self.clr_card, border_radius=10, padding=ft.padding.all(10),
                                    margin=ft.padding.only(0, 3, 0, 3),
                                ))
                        dlg.content = ft.Container(
                            content=ft.Column(detail_items, spacing=0, scroll=ft.ScrollMode.AUTO),
                            width=300, height=350,
                        )
                        self.page.update()
                    self.page.run_thread(show_list)
                except Exception as e:
                    print(f"加载统计详情失败: {e}")
                    self.page.run_thread(lambda: self._show_toast("加载失败"))
            
            import threading
            threading.Thread(target=load_folders, daemon=True).start()
        except Exception as e:
            self._show_toast("显示统计详情失败：" + str(e))

    def _render_cloud_files(self):
        if not hasattr(self, '_cloud_file_list') or not self._cloud_file_list:
            return
        self._cloud_file_list.controls.clear()
        files = self._get_cloud_files()
        if not files:
            self._cloud_file_list.controls.append(ft.Container(
                content=ft.Column([
                    ft.Container(height=40),
                    ft.Icon(ft.icons.CLOUD_OFF_OUTLINED, size=64, color=self.clr_text2),
                    ft.Container(height=12),
                    ft.Text("网盘是空的", size=16, color=self.clr_text2, weight=ft.FontWeight.W_500),
                    ft.Container(height=6),
                    ft.Text("点击右下角加号上传文件", size=13, color=self.clr_text2),
                    ft.Container(height=40),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True, alignment=ft.alignment.center,
            ))
            return
        for f in files:
            icon_color = ft.colors.BLUE if f.get("type") == "folder" else ft.colors.ORANGE
            icon = ft.icons.FOLDER if f.get("type") == "folder" else ft.icons.INSERT_DRIVE_FILE_OUTLINED
            self._cloud_file_list.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(icon, size=22, color=ft.colors.WHITE),
                        width=40, height=40, bgcolor=icon_color, border_radius=10, alignment=ft.alignment.center),
                    ft.Container(width=10),
                    ft.Column([
                        ft.Text(f.get("name", "未命名"), size=14, weight=ft.FontWeight.W_500, color=self.clr_text,
                            overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Container(height=2),
                        ft.Text(f.get("info", ""), size=11, color=self.clr_text2),
                    ], spacing=0, expand=True),
                    ft.PopupMenuButton(items=[
                        ft.PopupMenuItem(icon=ft.icons.DOWNLOAD_OUTLINED, text="下载", on_click=lambda e, fi=f: self._download_cloud_file(fi)),
                        ft.PopupMenuItem(icon=ft.icons.DELETE_OUTLINE, text="删除", on_click=lambda e, fi=f: self._delete_cloud_file(fi)),
                    ], icon=ft.Icon(ft.icons.MORE_VERT, size=20, color=self.clr_text2)),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.clr_card, border_radius=12, padding=ft.padding.symmetric(horizontal=12, vertical=10),
                margin=ft.padding.symmetric(horizontal=16), on_click=lambda e, fi=f: self._open_cloud_file(fi),
            ))
        self._cloud_file_list.controls.append(ft.Container(height=20))

    def _get_cloud_files(self, use_cache=True, folder_id=None):
        """获取用户网盘文件和文件夹列表
        use_cache=True时优先返回缓存，然后后台刷新
        folder_id: 指定文件夹ID，None表示使用当前文件夹
        """
        if folder_id is None:
            folder_id = self.current_folder_id
        # 只有根目录才用缓存，子目录实时获取
        if use_cache and folder_id == 0 and self._cached_cloud_files is not None:
            # 后台刷新缓存
            if not self._cloud_files_loading:
                threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
            return self._cached_cloud_files
        # 直接从远程API获取
        return self._fetch_cloud_files_from_remote(folder_id)

    def _fetch_cloud_files_from_remote(self, folder_id=0):
        """从远程API获取网盘文件列表
        folder_id: 文件夹ID，0表示根目录
        """
        if not self.current_user:
            return []
        try:
            user_id = int(self.current_user.get("id", 0))
        except (ValueError, TypeError):
            user_id = self.current_user.get("id", "")
        if not user_id:
            return []
        result = []
        try:
            # 获取文件夹列表
            ok, folders_data = self._remote_api_request("GET", "user-folders", params={"user_id": user_id, "parent_id": folder_id})
            if ok and folders_data:
                folders = folders_data.get("folders", [])
                for folder in folders:
                    result.append({
                        "id": folder.get("id"),
                        "name": folder.get("name", "未命名"),
                        "type": "folder",
                        "size_bytes": 0,
                        "info": f"文件夹 · {folder.get('file_count', 0)}个文件",
                        "share_code": folder.get("code", folder.get("share_code", "")),
                        "extract_code": folder.get("extract_code", ""),
                    })
            # 获取文件列表
            ok, files_data = self._remote_api_request("GET", "user-files", params={"user_id": user_id, "folder_id": folder_id})
            if ok and files_data:
                files = files_data.get("files", [])
                for f in files:
                    result.append({
                        "id": f.get("id"),
                        "name": f.get("name", "未命名"),
                        "type": "file",
                        "size_bytes": f.get("file_size", 0),
                        "info": f"{f.get('size', '未知')} · {f.get('created_at', '')}",
                        "share_code": f.get("share_code", ""),
                        "extract_code": f.get("extract_code", ""),
                    })
        except Exception as e:
            print(f"获取网盘文件失败: {e}")
        # 排序：文件夹在前，文件在后，各自按创建时间倒序（最新的在前面）
        folders = [f for f in result if f.get("type") == "folder"]
        files = [f for f in result if f.get("type") == "file"]
        # 文件按创建时间倒序（info中包含创建时间，简单按原始顺序即可，远程API应该已排序）
        return folders + files

    def _refresh_cloud_cache(self):
        """后台刷新网盘缓存"""
        if self._cloud_files_loading:
            return
        self._cloud_files_loading = True
        try:
            files = self._fetch_cloud_files_from_remote()
            self._cached_cloud_files = files
            # 同时刷新已用空间
            self._cached_cloud_used_mb = self._fetch_cloud_used_mb_from_remote()
            # 如果当前在网盘页面，刷新UI
            if hasattr(self, '_cloud_file_list') and self._cloud_file_list:
                try:
                    self._render_cloud_files()
                    self.page.update()
                except:
                    pass
        except Exception as e:
            print(f"刷新网盘缓存失败: {e}")
        finally:
            self._cloud_files_loading = False

    def _fetch_cloud_used_mb_from_remote(self):
        """从远程API获取网盘已用空间"""
        if not self.current_user:
            return 0
        user_id = self.current_user.get("id", "")
        try:
            ok, result = self._remote_api_request("GET", "user-fm-stats", params={"user_id": user_id})
            if ok and result:
                total_size = result.get("total_file_size", 0)
                return total_size / (1024 * 1024)
        except Exception as e:
            print(f"获取网盘统计失败: {e}")
        return 0

    def _save_cloud_files(self, files):
        try:
            cloud_dir = os.path.join(_base_dir, "user_data")
            os.makedirs(cloud_dir, exist_ok=True)
            with open(os.path.join(cloud_dir, "cloud_drive.json"), "w", encoding="utf-8") as f:
                json.dump(files, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _get_cloud_used_mb(self, use_cache=True):
        """获取用户网盘已用空间（优先缓存，后台刷新）"""
        if use_cache and self._cached_cloud_used_mb > 0:
            return self._cached_cloud_used_mb
        return self._fetch_cloud_used_mb_from_remote()

    def _upload_cloud_file(self):
        """上传文件到远程网盘（100MB以内用原方式，超过100MB分块上传）"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(title="选择要上传的文件")
            root.destroy()
            if not file_path or not os.path.exists(file_path) or not self.current_user:
                return
            try:
                user_id = int(self.current_user.get("id", 0))
            except (ValueError, TypeError):
                user_id = self.current_user.get("id", "")
            fname = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            # 超过100MB走分块上传
            if file_size > 100 * 1024 * 1024:
                # 显示上传中弹窗
                progress_ring = ft.ProgressRing(width=36, height=36, color=THEME_COLOR, stroke_width=3)
                upload_status = ft.Text(f"正在上传：{fname}", size=13, color=self.clr_text, text_align=ft.TextAlign.CENTER)
                upload_size_text = ft.Text(f"{file_size_mb:.1f} MB", size=11, color=self.clr_text2)
                progress_bar = ft.ProgressBar(width=240, height=8, color=THEME_COLOR, bgcolor=self.clr_border, value=0)
                progress_text = ft.Text("0%", size=12, color=self.clr_text2, text_align=ft.TextAlign.CENTER)
                upload_dlg = ft.AlertDialog(
                    content=ft.Container(
                        content=ft.Column([
                            progress_ring, ft.Container(height=10),
                            upload_status, ft.Container(height=2), upload_size_text,
                            ft.Container(height=12), progress_bar, ft.Container(height=4), progress_text,
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                        padding=ft.padding.all(20), width=280,
                    ),
                )
                self.page.dialog = upload_dlg
                self.page.dialog.open = True
                self.page.update()
                def do_chunked():
                    try:
                        self._chunked_upload(file_path, fname, file_size, user_id,
                            upload_dlg, progress_bar, progress_text, progress_ring, upload_status)
                    except Exception as e:
                        self._close_dialog(upload_dlg)
                        self._show_toast("上传失败：" + str(e)[:40])
                threading.Thread(target=do_chunked, daemon=True).start()
                return

            # 100MB以内用原方式（和之前完全一样）
            progress_ring = ft.ProgressRing(width=36, height=36, color=THEME_COLOR, stroke_width=3)
            upload_status = ft.Text(f"正在上传：{fname}", size=13, color=self.clr_text, text_align=ft.TextAlign.CENTER)
            upload_size_text = ft.Text(f"{file_size_mb:.1f} MB", size=11, color=self.clr_text2)
            progress_bar = ft.ProgressBar(width=240, height=8, color=THEME_COLOR, bgcolor=self.clr_border, value=0)
            progress_text = ft.Text("0%", size=12, color=self.clr_text2, text_align=ft.TextAlign.CENTER)
            upload_dlg = ft.AlertDialog(
                content=ft.Container(
                    content=ft.Column([
                        progress_ring, ft.Container(height=10),
                        upload_status, ft.Container(height=2), upload_size_text,
                        ft.Container(height=12), progress_bar, ft.Container(height=4), progress_text,
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                    padding=ft.padding.all(20), width=280,
                ),
            )
            self.page.dialog = upload_dlg
            self.page.dialog.open = True
            self.page.update()

            def do_upload():
                try:
                    import http.client
                    from urllib.parse import urlparse
                    base_url = APP_CONFIG.get("remote_api_base", "")
                    app_key = APP_CONFIG.get("remote_app_key", "")
                    if not base_url or not app_key:
                        self._close_dialog(upload_dlg)
                        self._show_toast("未配置远程API")
                        return
                    url = f"{base_url}/api/remote/{app_key}/user-files/upload"
                    parsed = urlparse(url)
                    is_https = parsed.scheme == "https"
                    boundary = "----YoXiBoundary" + str(int(time.time() * 1000))
                    current_fid = self.current_folder_id if hasattr(self, 'current_folder_id') else 0
                    user_id_part = (
                        f"--{boundary}\r\n"
                        f'Content-Disposition: form-data; name="user_id"\r\n\r\n'
                        f"{user_id}\r\n"
                    ).encode("utf-8")
                    folder_id_part = (
                        f"--{boundary}\r\n"
                        f'Content-Disposition: form-data; name="folder_id"\r\n\r\n'
                        f"{current_fid}\r\n"
                    ).encode("utf-8")
                    try:
                        fname.encode('ascii').decode('ascii')
                        file_header = (
                            f"--{boundary}\r\n"
                            f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
                            f"Content-Type: application/octet-stream\r\n\r\n"
                        ).encode("utf-8")
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        from urllib.parse import quote
                        fname_encoded = quote(fname)
                        file_header = (
                            f"--{boundary}\r\n"
                            f'Content-Disposition: form-data; name="file"; filename="file"; filename*=UTF-8\'\'{fname_encoded}\r\n'
                            f"Content-Type: application/octet-stream\r\n\r\n"
                        ).encode("utf-8")
                    end_boundary = f"\r\n--{boundary}--\r\n".encode("utf-8")
                    total_size = len(user_id_part) + len(folder_id_part) + len(file_header) + file_size + len(end_boundary)
                    sent_size = 0
                    if is_https:
                        conn = http.client.HTTPSConnection(parsed.netloc, timeout=120)
                    else:
                        conn = http.client.HTTPConnection(parsed.netloc, timeout=120)
                    conn.putrequest("POST", parsed.path + ("?" + parsed.query if parsed.query else ""))
                    conn.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
                    conn.putheader("Content-Length", str(total_size))
                    conn.putheader("User-Agent", "YoXiEmail/1.0")
                    conn.putheader("Accept", "application/json")
                    conn.endheaders()
                    conn.send(user_id_part)
                    sent_size += len(user_id_part)
                    conn.send(folder_id_part)
                    sent_size += len(folder_id_part)
                    conn.send(file_header)
                    sent_size += len(file_header)
                    chunk_size = 64 * 1024
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            conn.send(chunk)
                            sent_size += len(chunk)
                            pct = min(100, int(sent_size / total_size * 100))
                            def update_progress(p=pct):
                                progress_bar.value = p / 100
                                progress_text.value = f"{p}%"
                                self.page.update()
                            self.page.run_thread(update_progress)
                    conn.send(end_boundary)
                    resp = conn.getresponse()
                    resp_data = resp.read().decode("utf-8")
                    conn.close()
                    if resp.status == 200:
                        result = json.loads(resp_data)
                        if result.get("ok"):
                            self._close_dialog(upload_dlg)
                            self._show_toast("上传成功")
                            self._cached_cloud_files = None
                            threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
                            try:
                                self._show_my_resources(folder_id=self.current_folder_id,
                                    folder_name=self.folder_path[-1][1] if self.folder_path else "我的资源")
                            except:
                                pass
                        else:
                            error_msg = result.get("msg", "未知错误")
                            self._close_dialog(upload_dlg)
                            self._show_toast("上传失败：" + str(error_msg))
                    else:
                        error_detail = f"HTTP {resp.status}"
                        try:
                            err_result = json.loads(resp_data)
                            if err_result.get("msg"):
                                error_detail += ": " + err_result["msg"]
                        except:
                            if resp_data and len(resp_data) < 100:
                                error_detail += ": " + resp_data
                        self._close_dialog(upload_dlg)
                        self._show_toast("上传失败：" + error_detail)
                except Exception as e:
                    self._close_dialog(upload_dlg)
                    self._show_toast("上传失败：" + str(e)[:40])
            threading.Thread(target=do_upload, daemon=True).start()
        except Exception as e:
            self._show_toast("上传出错：" + str(e)[:30])

    def _chunked_upload(self, file_path, fname, file_size, user_id, upload_dlg, progress_bar, progress_text, progress_ring, upload_status):
        """大文件分块上传（init → chunk → complete）"""
        try:
            import http.client
            from urllib.parse import urlparse

            base_url = APP_CONFIG.get("remote_api_base", "")
            app_key = APP_CONFIG.get("remote_app_key", "")
            if not base_url or not app_key:
                self._close_dialog(upload_dlg)
                self._show_toast("未配置远程API")
                return

            CHUNK_SIZE = 5 * 1024 * 1024
            total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
            current_fid = self.current_folder_id if hasattr(self, 'current_folder_id') else 0

            def api_post(path, body_data=None, is_json=True):
                """发送POST请求"""
                url = f"{base_url}/api/remote/{app_key}/{path}"
                parsed = urlparse(url)
                if parsed.scheme == "https":
                    conn = http.client.HTTPSConnection(parsed.netloc, timeout=120)
                else:
                    conn = http.client.HTTPConnection(parsed.netloc, timeout=120)
                if is_json:
                    data = json.dumps(body_data).encode("utf-8")
                    conn.putrequest("POST", parsed.path)
                    conn.putheader("Content-Type", "application/json")
                    conn.putheader("Content-Length", str(len(data)))
                    conn.putheader("User-Agent", "YoXiEmail/1.0")
                    conn.endheaders()
                    conn.send(data)
                else:
                    conn.putrequest("POST", parsed.path)
                    conn.putheader("Content-Type", "application/octet-stream")
                    conn.putheader("Content-Length", str(len(body_data)))
                    conn.putheader("User-Agent", "YoXiEmail/1.0")
                    conn.endheaders()
                    conn.send(body_data)
                resp = conn.getresponse()
                resp_data = resp.read().decode("utf-8")
                conn.close()
                return resp.status, resp_data

            # 1. 初始化上传
            def update_status(text):
                upload_status.value = text
                self.page.update()

            update_status(f"初始化上传...")
            status, resp_data = api_post("user-files/upload/init", {
                "user_id": str(user_id),
                "filename": fname,
                "total_size": file_size,
                "folder_id": current_fid,
                "total_chunks": total_chunks,
            })
            if status != 200:
                self._close_dialog(upload_dlg)
                self._show_toast(f"上传初始化失败（HTTP {status}），大文件上传需要服务器支持分块接口")
                return
            init_result = json.loads(resp_data)
            if not init_result.get("ok"):
                self._close_dialog(upload_dlg)
                self._show_toast("初始化失败：" + init_result.get("msg", "未知错误"))
                return
            upload_id = init_result.get("upload_id") or init_result.get("data", {}).get("upload_id", "")
            if not upload_id:
                self._close_dialog(upload_dlg)
                self._show_toast("初始化失败：未返回upload_id")
                return

            # 2. 分块上传（带失败重试）
            with open(file_path, "rb") as f:
                for chunk_index in range(total_chunks):
                    chunk_data = f.read(CHUNK_SIZE)
                    if not chunk_data:
                        break
                    update_status(f"上传分块 {chunk_index + 1}/{total_chunks}")

                    # 每个分块最多重试3次
                    chunk_ok = False
                    for retry in range(3):
                        try:
                            # 发送分块（用multipart包含upload_id和chunk_index）
                            url = f"{base_url}/api/remote/{app_key}/user-files/upload/chunk"
                            parsed = urlparse(url)
                            boundary = "----YoXiChunk" + str(int(time.time() * 1000))
                            uid_part = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"upload_id\"\r\n\r\n{upload_id}\r\n").encode("utf-8")
                            idx_part = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"chunk_index\"\r\n\r\n{chunk_index}\r\n").encode("utf-8")
                            file_head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"chunk\"; filename=\"chunk_{chunk_index}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode("utf-8")
                            end_b = f"\r\n--{boundary}--\r\n".encode("utf-8")
                            total_chunk_size = len(uid_part) + len(idx_part) + len(file_head) + len(chunk_data) + len(end_b)

                            if parsed.scheme == "https":
                                conn = http.client.HTTPSConnection(parsed.netloc, timeout=120)
                            else:
                                conn = http.client.HTTPConnection(parsed.netloc, timeout=120)
                            conn.putrequest("POST", parsed.path)
                            conn.putheader("Content-Type", f"multipart/form-data; boundary={boundary}")
                            conn.putheader("Content-Length", str(total_chunk_size))
                            conn.putheader("User-Agent", "YoXiEmail/1.0")
                            conn.endheaders()
                            conn.send(uid_part)
                            conn.send(idx_part)
                            conn.send(file_head)
                            conn.send(chunk_data)
                            conn.send(end_b)
                            resp = conn.getresponse()
                            resp_body = resp.read().decode("utf-8")
                            conn.close()

                            # 检查分块上传是否成功
                            if resp.status == 200:
                                try:
                                    chunk_result = json.loads(resp_body)
                                    if chunk_result.get("ok"):
                                        chunk_ok = True
                                        break
                                except:
                                    chunk_ok = True
                                    break
                            if retry < 2:
                                time.sleep(1)  # 重试前等待1秒
                        except Exception:
                            if retry < 2:
                                time.sleep(1)
                            continue

                    if not chunk_ok:
                        self._close_dialog(upload_dlg)
                        self._show_toast(f"分块 {chunk_index + 1} 上传失败，请重试")
                        return

                    # 更新进度
                    pct = min(100, int((chunk_index + 1) / total_chunks * 100))
                    def update_progress(p=pct):
                        progress_bar.value = p / 100
                        progress_text.value = f"{p}%"
                        self.page.update()
                    self.page.run_thread(update_progress)

            # 3. 完成上传
            update_status("正在合并文件...")
            status, resp_data = api_post("user-files/upload/complete", {
                "upload_id": upload_id,
                "user_id": str(user_id),
            })
            self._handle_upload_response(status, resp_data, upload_dlg)
        except Exception as e:
            self._close_dialog(upload_dlg)
            self._show_toast("分块上传失败：" + str(e)[:40])

    def _handle_upload_response(self, status, resp_data, upload_dlg):
        """处理上传响应"""
        if status == 200:
            try:
                result = json.loads(resp_data)
                if result.get("ok"):
                    self._close_dialog(upload_dlg)
                    self._show_toast("上传成功")
                    self._cached_cloud_files = None
                    threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
                    try:
                        self._show_my_resources(folder_id=self.current_folder_id,
                            folder_name=self.folder_path[-1][1] if self.folder_path else "我的资源")
                    except:
                        pass
                else:
                    error_msg = result.get("msg", "未知错误")
                    self._close_dialog(upload_dlg)
                    self._show_toast("上传失败：" + str(error_msg))
            except:
                self._close_dialog(upload_dlg)
                self._show_toast("上传成功")
        elif status == 500:
            self._close_dialog(upload_dlg)
            self._show_toast("上传失败：服务器错误，文件可能过大，请用分块上传或联系管理员")
        else:
            error_detail = f"HTTP {status}"
            try:
                err_result = json.loads(resp_data)
                if err_result.get("msg"):
                    error_detail += ": " + err_result["msg"]
            except:
                if resp_data and len(resp_data) < 100:
                    error_detail += ": " + resp_data
            self._close_dialog(upload_dlg)
            self._show_toast("上传失败：" + error_detail)


    def _create_cloud_folder(self):
        try:
            # 根目录创建网盘时检查数量限制（最多5个）
            is_root = (not hasattr(self, 'current_folder_id')) or self.current_folder_id == 0
            if is_root:
                MAX_DRIVES = 5
                drive_count = self._get_current_cloud_drive_count()
                if drive_count >= MAX_DRIVES:
                    self.page.dialog = ft.AlertDialog(
                        title=ft.Row([
                            ft.Icon(ft.icons.LOCK, size=20, color=ft.colors.ORANGE),
                            ft.Container(width=8),
                            ft.Text("网盘数量已达上限", size=16, weight=ft.FontWeight.BOLD),
                        ]),
                        content=ft.Column([
                            ft.Text(f"最多可创建 {MAX_DRIVES} 个网盘，当前已创建 {drive_count} 个。", size=13, color=self.clr_text2),
                            ft.Container(height=6),
                            ft.Text("如需创建更多网盘，请联系管理员帮你创建。", size=13, color=self.clr_text2),
                        ], spacing=0, tight=True),
                        actions=[
                            ft.TextButton("我知道了", on_click=lambda ev: self._close_dialog()),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.dialog.open = True
                    self.page.update()
                    return

            creating = [False]  # 用列表实现闭包变量，防重复点击
            def on_submit(e):
                if creating[0]:
                    return  # 防止重复点击
                name = name_field.value.strip()
                if not name:
                    self._show_toast("请输入文件夹名称")
                    return
                if not self.current_user:
                    self._show_toast("请先登录")
                    return
                # 根目录创建网盘时检查重名
                if is_root:
                    try:
                        cached = getattr(self, '_cached_cloud_files', None)
                        if cached and isinstance(cached, list):
                            for f in cached:
                                if isinstance(f, dict) and f.get("type") == "folder" and f.get("name", "").strip() == name:
                                    self._show_toast("网盘名称已存在，请换一个名字")
                                    return
                    except:
                        pass
                creating[0] = True
                # 立即关闭对话框，显示创建中
                self._close_dialog(dlg)
                self._show_toast(f"正在创建：{name}")
                # 后台创建，不阻塞UI
                def do_create():
                    try:
                        try:
                            user_id = int(self.current_user.get("id", 0))
                        except (ValueError, TypeError):
                            user_id = self.current_user.get("id", "")
                        parent_id = self.current_folder_id if hasattr(self, 'current_folder_id') else 0
                        ok, result = self._remote_api_request("POST", "user-folders", body={"user_id": user_id, "name": name, "parent_id": parent_id})
                        if ok:
                            # 清除缓存，后台刷新
                            self._cached_cloud_files = None
                            threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
                            # 立即刷新当前页面
                            try:
                                self._show_my_resources(folder_id=self.current_folder_id, 
                                    folder_name=self.folder_path[-1][1] if self.folder_path else "我的资源")
                            except:
                                pass
                            self._show_toast(f"已创建：{name}")
                        else:
                            error_msg = result.get("msg", "") if isinstance(result, dict) else str(result)
                            error_msg = str(error_msg)
                            if not error_msg or "500" in error_msg or "Internal" in error_msg:
                                self._show_toast("服务器超时，请联系管理员或重试")
                            elif "exist" in error_msg.lower() or "已存在" in error_msg or "重复" in error_msg:
                                self._show_toast("名称已存在，请换一个名字")
                            elif "permission" in error_msg.lower() or "权限" in error_msg:
                                self._show_toast("没有权限，请联系管理员")
                            elif "limit" in error_msg.lower() or "上限" in error_msg or "超过" in error_msg:
                                self._show_toast("数量已达上限，请前往积分商城兑换")
                            else:
                                self._show_toast("创建失败：" + error_msg[:20])
                    except Exception as ex:
                        err_str = str(ex)
                        if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                            self._show_toast("网络超时，请检查网络后重试")
                        elif "500" in err_str or "Internal" in err_str:
                            self._show_toast("服务器超时，请联系管理员或重试")
                        elif "Connection" in err_str or "连接" in err_str:
                            self._show_toast("网络连接失败，请检查网络")
                        else:
                            self._show_toast("创建失败：" + err_str[:20])
                threading.Thread(target=do_create, daemon=True).start()
            dialog_title = "新建网盘" if is_root else "新建文件夹"
            field_label = "网盘名称" if is_root else "文件夹名称"
            name_field = ft.TextField(label=field_label, width=280, border_radius=8)
            dlg = ft.AlertDialog(title=ft.Text(dialog_title), content=name_field,
                actions=[ft.TextButton("取消", on_click=lambda e: self._close_dialog(dlg)),
                         ft.TextButton("创建", on_click=on_submit)])
            self.page.dialog = dlg
            self.page.dialog.open = True
            self.page.update()
        except Exception as e:
            self._show_toast("创建网盘出错：" + str(e))
    def _download_cloud_file(self, fi):
        self._show_toast("开始下载：" + fi.get("name", ""))

    def _copy_cloud_link(self, fi):
        self._show_toast("链接已复制")

    def _delete_cloud_file(self, fi):
        """删除文件或文件夹（后台删除，立即从UI移除）"""
        if not self.current_user:
            return
        item_id = fi.get("id")
        item_type = fi.get("type", "file")
        item_name = fi.get("name", "文件")
        if not item_id:
            self._show_toast("删除失败：缺少ID")
            return
        # 立即显示删除中
        self._show_toast(f"正在删除：{item_name}")
        # 后台删除，不阻塞UI
        def do_delete():
            try:
                try:
                    user_id = int(self.current_user.get("id", 0))
                except (ValueError, TypeError):
                    user_id = self.current_user.get("id", "")
                if item_type == "folder":
                    ok, result = self._remote_api_request("DELETE", f"user-folders/{item_id}", body={"user_id": user_id})
                else:
                    ok, result = self._remote_api_request("DELETE", f"user-files/{item_id}", body={"user_id": user_id})
                if ok:
                    # 清除缓存，后台刷新
                    self._cached_cloud_files = None
                    threading.Thread(target=self._refresh_cloud_cache, daemon=True).start()
                    # 立即刷新当前页面
                    try:
                        self._show_my_resources(folder_id=self.current_folder_id,
                            folder_name=self.folder_path[-1][1] if self.folder_path else "我的资源")
                    except:
                        pass
                    if item_type == "folder":
                        self._show_toast("文件夹已删除")
                    else:
                        self._show_toast("文件已删除")
                else:
                    self._show_toast("删除失败")
            except Exception as e:
                self._show_toast(f"删除失败: {e}")
        threading.Thread(target=do_delete, daemon=True).start()
    def _open_cloud_file(self, fi):
        if fi.get("type") == "folder":
            self._show_toast("打开文件夹：" + fi.get("name", ""))
        else:
            self._show_toast("打开文件：" + fi.get("name", ""))

    def render_me_page(self):
        self._show_navbar()  # 主页面显示导航栏
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
                            self._get_colored_name_widget(name or username or qq or "用户", size=18, weight=ft.FontWeight.BOLD),
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

        # ---- 统计卡片（2列）：网盘文件夹数量 + 文件数量 ----
        _cloud_stats = getattr(self, '_cached_cloud_stats', None) or {}
        folder_count = _cloud_stats.get("folder_count", 0)
        file_count = _cloud_stats.get("file_count", 0)
        # 未登录或无缓存时，后台加载网盘统计
        if self.current_user and not _cloud_stats:
            def _load_cloud_stats_for_me():
                try:
                    stats = self._fetch_cloud_stats_from_remote()
                    if stats:
                        self._cached_cloud_stats = stats
                        self.page.run_thread(self.render_me_page)
                except Exception as e:
                    print(f"[我的页面] 加载网盘统计失败: {e}")
            threading.Thread(target=_load_cloud_stats_for_me, daemon=True).start()
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Column([
                    ft.Text(str(folder_count), size=26, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Container(height=2),
                    ft.Text("文件夹", size=12, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    expand=True, alignment=ft.alignment.center, padding=14),
                ft.Container(width=1, bgcolor=self.clr_border, height=50),
                ft.Container(content=ft.Column([
                    ft.Text(str(file_count), size=26, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE),
                    ft.Container(height=2),
                    ft.Text("文件", size=12, color=self.clr_text2),
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

        # ---- 积分入口 ----
        # TODO: API接入后，积分数字从后端获取；未登录时点击应跳转登录
        _my_points_display = (getattr(self, "_points_cache", None) or {}).get("points", 0)
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.STARS, size=22, color=ft.colors.AMBER),
                    width=40, height=40, bgcolor=ft.colors.AMBER_50,
                    border_radius=12, alignment=ft.alignment.center),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("我的积分", size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                    ft.Container(height=2),
                    ft.Text("签到赚积分，查看排名", size=11, color=self.clr_text2),
                ], spacing=0, expand=True),
                ft.Row([
                    ft.Text(str(_my_points_display), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER),
                    ft.Container(width=2),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, size=18, color=self.clr_text3),
                ], spacing=0),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 6, 16, 6),
            on_click=lambda e: self._open_points_page(),
        ))


        # ---- 修改昵称颜色入口 ----
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

    # ========== 积分中心页面 ==========
    def _load_points_data_silent(self):
        """静默加载积分数据到缓存（加载页预加载用，只存缓存不刷新页面）"""
        try:
            if not self.current_user:
                return
            user_id = self.current_user.get("id", "")
            if not user_id:
                return
            points_data = {"_loaded": True}
            # 获取积分概览+签到记录
            try:
                ok1, result1 = self._remote_api_request("GET", "user-points",
                    params={"user_id": user_id})
                if ok1 and isinstance(result1, dict) and result1.get("ok"):
                    d = result1.get("data", {})
                    points_data["points"] = d.get("points", 0)
                    points_data["rank"] = d.get("rank", 0)
                    points_data["checked_in_today"] = d.get("checked_in_today", False)
                    points_data["continuous_days"] = d.get("continuous_days", 0)
                    points_data["total_users"] = d.get("total_users", 0)
                    points_data["checkin_records"] = d.get("checkin_records", [])
            except Exception:
                pass
            # 获取排行榜
            try:
                ok2, result2 = self._remote_api_request("GET", "points-rank",
                    params={"user_id": user_id, "limit": 50, "period": "week"})
                if ok2 and isinstance(result2, dict) and result2.get("ok"):
                    d = result2.get("data", {})
                    points_data["rank_list"] = d.get("rank_list", [])
                    points_data["my_rank"] = d.get("my_rank")
            except Exception:
                pass
            self._points_cache = points_data
            # 加载用户已购商品
            try:
                ok3, result3 = self._remote_api_request("GET", "user-purchases",
                    params={"user_id": user_id})
                if ok3 and isinstance(result3, dict) and result3.get("ok"):
                    self._purchases_cache = result3.get("data", result3)
            except Exception:
                pass
        except Exception:
            pass

    def _load_points_data(self):
        """后台加载积分数据和排行榜（API对接版）"""
        try:
            if not self.current_user:
                self._points_cache = {
                    "_loaded": True, "points": 0, "rank": 0,
                    "checked_in_today": False, "continuous_days": 0,
                    "checkin_records": [], "rank_list": [], "my_rank": None,
                    "_not_logged_in": True,
                }
                self.page.run_thread(self.render_points_page)
                return

            user_id = self.current_user.get("id", "")
            if not user_id:
                self._points_cache = {
                    "_loaded": True, "points": 0, "rank": 0,
                    "checked_in_today": False, "continuous_days": 0,
                    "checkin_records": [], "rank_list": [], "my_rank": None,
                }
                self.page.run_thread(self.render_points_page)
                return

            # 并行获取：积分概览（含签到记录）+ 排行榜
            points_data = {"_loaded": True}

            # 1. 获取我的积分 + 签到记录
            try:
                ok1, result1 = self._remote_api_request("GET", "user-points",
                    params={"user_id": user_id})
                if ok1 and isinstance(result1, dict) and result1.get("ok"):
                    d = result1.get("data", {})
                    points_data["points"] = d.get("points", 0)
                    points_data["rank"] = d.get("rank", 0)
                    points_data["checked_in_today"] = d.get("checked_in_today", False)
                    points_data["continuous_days"] = d.get("continuous_days", 0)
                    points_data["total_users"] = d.get("total_users", 0)
                    points_data["checkin_records"] = d.get("checkin_records", [])
                else:
                    points_data["points"] = 0
                    points_data["rank"] = 0
                    points_data["checked_in_today"] = False
                    points_data["continuous_days"] = 0
                    points_data["checkin_records"] = []
            except Exception as e:
                print(f"[积分] 获取积分失败: {e}")
                points_data["points"] = 0
                points_data["rank"] = 0
                points_data["checked_in_today"] = False
                points_data["continuous_days"] = 0
                points_data["checkin_records"] = []

            # 2. 获取排行榜
            try:
                ok2, result2 = self._remote_api_request("GET", "points-rank",
                    params={"user_id": user_id, "limit": 50, "period": "week"})
                if ok2 and isinstance(result2, dict) and result2.get("ok"):
                    d = result2.get("data", {})
                    points_data["rank_list"] = d.get("rank_list", [])
                    points_data["my_rank"] = d.get("my_rank")
                    # 从排行榜中找到当前用户的真实排名，覆盖user-points返回的rank
                    for item in points_data["rank_list"]:
                        if isinstance(item, dict) and str(item.get("user_id")) == str(user_id):
                            points_data["rank"] = item.get("rank", points_data.get("rank", 0))
                            break
                else:
                    points_data["rank_list"] = []
                    points_data["my_rank"] = None
            except Exception as e:
                print(f"[积分] 获取排行榜失败: {e}")
                points_data["rank_list"] = []
                points_data["my_rank"] = None

            self._points_cache = points_data

            # 3. 加载用户已购商品
            try:
                ok3, result3 = self._remote_api_request("GET", "user-purchases",
                    params={"user_id": user_id})
                if ok3 and isinstance(result3, dict) and result3.get("ok"):
                    self._purchases_cache = result3.get("data", result3)
                else:
                    self._purchases_cache = None
            except Exception as e:
                print(f"[积分] 获取购买记录失败: {e}")
                self._purchases_cache = None

            self.page.run_thread(self.render_points_page)
        except Exception as e:
            print(f"[积分] 加载数据异常: {e}")
            self._points_cache = {
                "_loaded": True, "points": 0, "rank": 0,
                "checked_in_today": False, "continuous_days": 0,
                "checkin_records": [], "rank_list": [], "my_rank": None,
            }
            self.page.run_thread(self.render_points_page)

    def _open_points_page(self):
        """打开积分中心（有缓存则不重新加载，签到后才刷新）"""
        # 如果缓存已加载，直接显示，不重新请求API
        cached = getattr(self, '_points_cache', None)
        if cached and isinstance(cached, dict) and cached.get("_loaded"):
            self.render_points_page()
        else:
            # 没有缓存时才加载
            self._points_cache = None
            self._purchases_cache = None
            self.render_points_page()

    def render_points_page(self):
        """积分中心页面（API对接版）"""
        # 停止之前的倒计时线程
        self._checkin_countdown_running = False
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None

        # ---- 顶部固定栏 ----
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_me_page()),
                ft.Text("积分中心", size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 未登录提示
        if not self.current_user:
            scroll_content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Icon(ft.icons.LOCK_OUTLINE, size=48, color=ft.colors.GREY_400),
                        alignment=ft.alignment.center),
                    ft.Container(height=12),
                    ft.Text("登录后查看积分和排名", size=15, color=self.clr_text2),
                    ft.Container(height=16),
                    ft.ElevatedButton("去登录", expand=True, height=44,
                        style=ft.ButtonStyle(bgcolor=THEME_COLOR, color=ft.colors.WHITE),
                        on_click=lambda e: self.show_fullscreen_login()),
                ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=60),
            ))
            self.content.controls.append(scroll_content)
            self.page.update()
            return

        # 数据未加载时显示加载中，并启动后台加载
        _cache = getattr(self, "_points_cache", None)
        if not _cache or not _cache.get("_loaded"):
            scroll_content.controls.append(ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=36, height=36, color=THEME_COLOR, stroke_width=3),
                    ft.Container(height=12),
                    ft.Text("加载中...", size=14, color=self.clr_text2),
                ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=80),
            ))
            self.content.controls.append(scroll_content)
            self.page.update()
            threading.Thread(target=self._load_points_data, daemon=True).start()
            return

        pc = self._points_cache
        my_points = self._get_display_points()
        checked_in_today = pc.get("checked_in_today", False)
        continuous_days = pc.get("continuous_days", 0)
        checkin_records = pc.get("checkin_records", [])
        rank_list = pc.get("rank_list", [])
        my_rank_info = pc.get("my_rank")

        # 先过滤+按签到天数排序，得到真实排名
        filtered_rank = []
        for item in rank_list:
            if isinstance(item, dict):
                name = item.get("name", "") or ""
                if name and name.strip() and name.strip() != "匿名用户":
                    filtered_rank.append(item)
        sorted_rank = sorted(filtered_rank, key=lambda x: x.get("checkin_days", 0) if isinstance(x, dict) else 0, reverse=True)
        for idx, item in enumerate(sorted_rank):
            if isinstance(item, dict):
                item["rank"] = idx + 1

        # 从排序后的列表中找当前用户的真实排名
        my_rank = 0
        if self.current_user:
            cur_uid = str(self.current_user.get("id", ""))
            for item in sorted_rank:
                if isinstance(item, dict) and str(item.get("user_id", "")) == cur_uid:
                    my_rank = item.get("rank", 0)
                    break
        if not my_rank and my_rank_info and isinstance(my_rank_info, dict):
            my_rank = my_rank_info.get("rank", 0)

        # ---- 积分头部卡片（金色） ----
        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.STARS, size=28, color=ft.colors.WHITE),
                        width=52, height=52, bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                        border_radius=26, alignment=ft.alignment.center),
                    ft.Container(width=14),
                    ft.Column([
                        ft.Text("我的积分", size=13, color=ft.colors.WHITE70),
                        ft.Container(height=2),
                        ft.Text(str(my_points), size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ], spacing=0, expand=True),
                    ft.Column([
                        ft.Text("当前排名", size=13, color=ft.colors.WHITE70),
                        ft.Container(height=2),
                        ft.Text(f"第 {my_rank} 名" if my_rank else "未上榜", size=20,
                            weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=12),
                ft.Container(height=1, bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE)),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.icons.LOCAL_FIRE_DEPARTMENT, size=14, color=ft.colors.WHITE),
                    ft.Container(width=4),
                    ft.Text(f"连续签到 {continuous_days} 天", size=12, color=ft.colors.WHITE),
                    ft.Container(width=16),
                    ft.Icon(ft.icons.CALENDAR_TODAY, size=14, color=ft.colors.WHITE),
                    ft.Container(width=4),
                    ft.Text("每日签到 +10 积分", size=12, color=ft.colors.WHITE),
                ], spacing=0),
            ], spacing=0),
            bgcolor=ft.colors.AMBER, border_radius=16, padding=20,
            margin=ft.margin.only(16, 12, 16, 6),
        ))

        # ---- 签到按钮 + 距下次签到剩余时间（实时更新） ----
        if checked_in_today:
            checkin_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=18, color=ft.colors.WHITE),
                    ft.Container(width=6),
                    ft.Text("今日已签到", size=15, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                height=48, bgcolor=ft.colors.GREY_400, border_radius=12,
            )
            remain_text = ft.Text("距下次签到：计算中...", size=11,
                color=self.clr_text2, text_align=ft.TextAlign.CENTER)
            checkin_area = ft.Column([
                checkin_btn,
                ft.Container(height=6),
                remain_text,
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            # 启动倒计时实时更新线程
            self._checkin_countdown_running = False
            if hasattr(self, "_checkin_countdown_thread") and self._checkin_countdown_thread:
                self._checkin_countdown_running = False
            self._checkin_countdown_running = True
            def _update_countdown():
                while getattr(self, "_checkin_countdown_running", False):
                    try:
                        _now_ts = time.time()
                        _tomorrow_str = time.strftime("%Y-%m-%d", time.localtime(_now_ts + 86400)) + " 00:00:00"
                        _tomorrow_ts = time.mktime(time.strptime(_tomorrow_str, "%Y-%m-%d %H:%M:%S"))
                        _remain = int(max(0, _tomorrow_ts - _now_ts))
                        _rh = _remain // 3600
                        _rm = (_remain % 3600) // 60
                        _rs = _remain % 60
                        remain_text.value = f"距下次签到：{_rh}小时{_rm}分{_rs}秒"
                        self.page.update()
                    except Exception:
                        pass
                    time.sleep(1)
            self._checkin_countdown_thread = threading.Thread(target=_update_countdown, daemon=True)
            self._checkin_countdown_thread.start()
        else:
            checkin_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.EVENT_AVAILABLE, size=18, color=ft.colors.WHITE),
                    ft.Container(width=6),
                    ft.Text("立即签到 +10积分", size=15, weight=ft.FontWeight.W_600, color=ft.colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                height=48, bgcolor=ft.colors.AMBER, border_radius=12,
                on_click=lambda e: self._do_check_in(),
                ink=True,
            )
            checkin_area = checkin_btn
        scroll_content.controls.append(ft.Container(
            content=checkin_area,
            padding=ft.padding.symmetric(horizontal=16),
            margin=ft.margin.only(0, 6, 0, 6),
        ))

        # ---- 签到日历（固定周一到周日排列） ----
        weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]
        today_str = time.strftime("%Y-%m-%d")
        # 构建日期->签到状态映射
        record_map = {}
        for r in checkin_records:
            if isinstance(r, dict) and r.get("date"):
                record_map[r["date"]] = r.get("checked", False)
        # 计算本周一的日期
        today_ts = time.mktime(time.strptime(today_str, "%Y-%m-%d"))
        today_wday = time.localtime(today_ts).tm_wday  # 周一=0
        monday_ts = today_ts - today_wday * 86400
        day_cells = []
        for i in range(7):
            day_ts = monday_ts + i * 86400
            day_date = time.strftime("%Y-%m-%d", time.localtime(day_ts))
            day_label = weekday_labels[i]
            is_today = (day_date == today_str)
            checked = record_map.get(day_date, False)
            cell_bg = ft.colors.AMBER if checked else (
                ft.colors.AMBER_50 if is_today else self.clr_input_bg)
            cell_text_color = ft.colors.WHITE if checked else (
                ft.colors.AMBER if is_today else self.clr_text2)
            icon = ft.icons.CHECK if checked else (ft.icons.TODAY if is_today else ft.icons.CIRCLE)
            icon_size = 16 if checked else 14
            day_cells.append(ft.Container(
                content=ft.Column([
                    ft.Text(day_label, size=10, color=cell_text_color),
                    ft.Container(height=4),
                    ft.Container(content=ft.Icon(icon, size=icon_size, color=cell_text_color),
                        width=28, height=28,
                        bgcolor=ft.colors.with_opacity(0.15, cell_bg) if not checked else ft.colors.TRANSPARENT,
                        border_radius=14, alignment=ft.alignment.center),
                ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True, padding=ft.padding.symmetric(vertical=8),
            ))
        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Text("签到记录", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                ft.Row(day_cells, spacing=4),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 6, 16, 6),
        ))

        # ---- 积分商城入口 ----
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.STORE, size=22, color=ft.colors.WHITE),
                    width=42, height=42, bgcolor=ft.colors.PURPLE, border_radius=12,
                    alignment=ft.alignment.center),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("积分商城", size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                    ft.Container(height=2),
                    ft.Text("用积分兑换网盘权限等好礼", size=11, color=self.clr_text2),
                ], spacing=0, expand=True),
                ft.Icon(ft.icons.CHEVRON_RIGHT, size=18, color=self.clr_text3),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 6, 16, 6),
            on_click=lambda e: self.render_points_shop(),
            ink=True,
        ))

        # ---- 签到排行榜 ----
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.AMBER, border_radius=2),
                ft.Container(width=6),
                ft.Text("签到排行榜", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
                ft.Container(width=8),
                ft.Text("按签到天数", size=11, color=self.clr_text3),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 12, 20, 6),
        ))

        # sorted_rank 已在页面顶部计算（过滤+按签到天数排序）

        if not sorted_rank:
            scroll_content.controls.append(ft.Container(
                content=ft.Text("暂无排行数据", size=13, color=self.clr_text2,
                    text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=20),
            ))
        else:
            for item in sorted_rank:
                rank_num = item.get("rank", 0)
                item_name = item.get("name", "匿名用户") or "匿名用户"
                item_points = item.get("points", 0)
                item_checkin_days = item.get("checkin_days", 0)
                item_qq = item.get("qq", "") or ""

                # 前三名特殊颜色
                if rank_num == 1:
                    rank_icon = ft.icons.LOOKS_ONE
                    rank_color = ft.colors.AMBER
                    rank_bg = ft.colors.AMBER_50
                elif rank_num == 2:
                    rank_icon = ft.icons.LOOKS_TWO
                    rank_color = ft.colors.GREY_500
                    rank_bg = ft.colors.GREY_100
                elif rank_num == 3:
                    rank_icon = ft.icons.LOOKS_3
                    rank_color = ft.colors.ORANGE_400
                    rank_bg = ft.colors.ORANGE_50
                else:
                    rank_icon = None
                    rank_color = self.clr_text2
                    rank_bg = self.clr_input_bg

                # 排名显示
                if rank_icon:
                    rank_widget = ft.Container(content=ft.Icon(rank_icon, size=20, color=rank_color),
                        width=32, height=32, alignment=ft.alignment.center)
                else:
                    rank_widget = ft.Container(content=ft.Text(str(rank_num), size=14,
                        weight=ft.FontWeight.W_600, color=rank_color),
                        width=32, height=32, alignment=ft.alignment.center)

                # 头像（有QQ显示QQ头像，加载失败或无QQ显示名字首字母）
                avatar_text = item_name[0].upper() if item_name else "U"
                if item_qq:
                    avatar_widget = ft.Container(
                        content=ft.Image(src=f"https://q1.qlogo.cn/g?b=qq&nk={item_qq}&s=100",
                            width=36, height=36, fit=ft.ImageFit.COVER, border_radius=18,
                            error_content=ft.Container(
                                content=ft.Text(avatar_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                width=36, height=36, bgcolor=THEME_COLOR, border_radius=18,
                                alignment=ft.alignment.center)),
                        width=36, height=36, border_radius=18, clip_behavior=ft.ClipBehavior.ANTI_ALIAS)
                else:
                    avatar_widget = ft.Container(
                        content=ft.Text(avatar_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        width=36, height=36, bgcolor=THEME_COLOR, border_radius=18,
                        alignment=ft.alignment.center)

                # 判断是否是当前用户自己（只有自己显示彩色名字）
                is_current_user = self.current_user and str(item.get("user_id", "")) == str(self.current_user.get("id", ""))
                if is_current_user:
                    name_widget = self._get_colored_name_widget(item_name, size=14, weight=ft.FontWeight.W_500)
                else:
                    name_widget = ft.Text(item_name, size=14, weight=ft.FontWeight.W_500,
                        color=self.clr_text, overflow=ft.TextOverflow.ELLIPSIS)

                # 名字+积分区域（可伸缩，超长省略），签到天数固定在右边
                name_points_area = ft.Container(
                    content=ft.Row([
                        ft.Container(content=name_widget, expand=True),
                        ft.Text(str(item_points), size=13, weight=ft.FontWeight.W_600, color=ft.colors.AMBER),
                        ft.Container(width=1),
                        ft.Icon(ft.icons.STARS, size=12, color=ft.colors.AMBER),
                    ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                )
                # 签到天数（固定宽度，不被挤压）
                checkin_badge = ft.Container(content=ft.Row([
                    ft.Text(str(item_checkin_days), size=13, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Container(width=1),
                    ft.Icon(ft.icons.EVENT_AVAILABLE, size=12, color=THEME_COLOR),
                ], spacing=0), bgcolor=ft.colors.with_opacity(0.1, THEME_COLOR),
                    border_radius=8, padding=ft.padding.symmetric(horizontal=6, vertical=3))

                scroll_content.controls.append(ft.Container(
                    content=ft.Row([
                        rank_widget,
                        ft.Container(width=8),
                        avatar_widget,
                        ft.Container(width=10),
                        name_points_area,
                        ft.Container(width=8),
                        checkin_badge,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=12, padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    margin=ft.margin.only(16, 2, 16, 2),
                ))

        # 我的排名（如果不在前N名，底部高亮显示）
        if my_rank_info and isinstance(my_rank_info, dict):
            my_rank_num = my_rank_info.get("rank", 0)
            my_name_display = my_rank_info.get("name", "我") or "我"
            my_points_display = my_rank_info.get("points", my_points)
            my_checkin_days = my_rank_info.get("checkin_days", pc.get("continuous_days", 0))
            my_qq_display = my_rank_info.get("qq", "") or ""
            # 检查是否已经在 sorted_rank 中
            already_in_list = any(
                item.get("user_id") == self.current_user.get("id")
                for item in sorted_rank if isinstance(item, dict)
            )
            if not already_in_list and my_rank_num:
                scroll_content.controls.append(ft.Container(height=6))
                my_avatar_text = my_name_display[0].upper() if my_name_display else "U"
                if my_qq_display:
                    my_avatar = ft.Container(
                        content=ft.Image(src=f"https://q1.qlogo.cn/g?b=qq&nk={my_qq_display}&s=100",
                            width=36, height=36, fit=ft.ImageFit.COVER, border_radius=18,
                            error_content=ft.Container(
                                content=ft.Text(my_avatar_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                width=36, height=36, bgcolor=THEME_COLOR, border_radius=18,
                                alignment=ft.alignment.center)),
                        width=36, height=36, border_radius=18, clip_behavior=ft.ClipBehavior.ANTI_ALIAS)
                else:
                    my_avatar = ft.Container(
                        content=ft.Text(my_avatar_text, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        width=36, height=36, bgcolor=THEME_COLOR, border_radius=18,
                        alignment=ft.alignment.center)
                # 我的排名行（当前用户，显示彩色名字）
                my_name_widget = self._get_colored_name_widget(my_name_display, size=14, weight=ft.FontWeight.W_600)
                my_name_points = ft.Container(
                    content=ft.Row([
                        ft.Container(content=my_name_widget, expand=True),
                        ft.Text(str(my_points_display), size=13, weight=ft.FontWeight.W_600, color=THEME_COLOR),
                        ft.Container(width=1),
                        ft.Icon(ft.icons.STARS, size=12, color=THEME_COLOR),
                    ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                )
                my_checkin_badge = ft.Container(content=ft.Row([
                    ft.Text(str(my_checkin_days), size=13, weight=ft.FontWeight.BOLD, color=THEME_COLOR),
                    ft.Container(width=1),
                    ft.Icon(ft.icons.EVENT_AVAILABLE, size=12, color=THEME_COLOR),
                ], spacing=0), bgcolor=ft.colors.with_opacity(0.15, THEME_COLOR),
                    border_radius=8, padding=ft.padding.symmetric(horizontal=6, vertical=3))
                scroll_content.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Text(str(my_rank_num), size=14, weight=ft.FontWeight.W_600,
                            color=THEME_COLOR), width=32, height=32, alignment=ft.alignment.center),
                        ft.Container(width=8),
                        my_avatar,
                        ft.Container(width=10),
                        my_name_points,
                        ft.Container(width=8),
                        my_checkin_badge,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.colors.BLUE_50, border_radius=12,
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    margin=ft.margin.only(16, 2, 16, 2),
                    border=ft.border.all(1.5, THEME_COLOR),
                ))

        scroll_content.controls.append(ft.Container(height=20))
        self.content.controls.append(scroll_content)
        self.page.update()

    def _do_check_in(self):
        """执行签到（弹小窗显示状态，成功后后台刷新数据）"""
        if not self.current_user:
            self._show_toast("请先登录后再签到", "warning")
            return

        user_id = self.current_user.get("id", "")
        if not user_id:
            self._show_toast("用户信息异常，请重新登录", "error")
            return

        # 弹出签到中对话框（不隐藏当前页面）
        checkin_icon = ft.ProgressRing(width=36, height=36, color=THEME_COLOR, stroke_width=3)
        checkin_text = ft.Text("签到中...", size=15, color=self.clr_text, weight=ft.FontWeight.W_600)
        checkin_sub = ft.Text("请稍候", size=12, color=self.clr_text2)
        checkin_dlg = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    checkin_icon,
                    ft.Container(height=12),
                    checkin_text,
                    ft.Container(height=4),
                    checkin_sub,
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                padding=ft.padding.all(24),
                width=200,
            ),
        )
        self.page.dialog = checkin_dlg
        checkin_dlg.open = True
        self.page.update()

        def checkin_thread():
            try:
                ok, result = self._remote_api_request("POST", "daily-checkin",
                    body={"user_id": user_id})
                if ok and isinstance(result, dict) and result.get("ok"):
                    d = result.get("data", {})
                    earned = d.get("points_earned", 10)
                    total_points = d.get("total_points", 0)
                    new_continuous = d.get("continuous_days", 0)

                    # 更新对话框为签到成功
                    def show_success():
                        checkin_icon = ft.Icon(ft.icons.CHECK_CIRCLE, size=40, color=ft.colors.GREEN)
                        checkin_text.value = f"签到成功！+{earned} 积分"
                        checkin_text.color = ft.colors.GREEN
                        checkin_sub.value = f"连续签到 {new_continuous} 天"
                        # 替换进度环为成功图标
                        checkin_dlg.content.content.controls[0] = checkin_icon
                        self.page.update()
                    self.page.run_thread(show_success)

                    # 后台刷新积分数据（排行榜等），不隐藏当前页面
                    def refresh_and_close():
                        try:
                            # 先更新本地缓存的基本信息
                            if isinstance(getattr(self, "_points_cache", None), dict):
                                self._points_cache["points"] = total_points
                                self._points_cache["checked_in_today"] = True
                                self._points_cache["continuous_days"] = new_continuous
                                records = self._points_cache.get("checkin_records", [])
                                if records and isinstance(records[-1], dict):
                                    records[-1]["checked"] = True
                                    records[-1]["points_earned"] = earned
                            # 后台重新加载完整数据（含排行榜）
                            self._load_points_data_silent()
                            time.sleep(0.5)
                        except:
                            pass
                        # 关闭对话框并刷新页面
                        def finish():
                            self._close_dialog(checkin_dlg)
                            self.render_points_page()
                        self.page.run_thread(finish)

                    threading.Thread(target=refresh_and_close, daemon=True).start()
                else:
                    msg = "签到失败"
                    if isinstance(result, dict):
                        msg = result.get("msg", "签到失败")
                    def show_fail():
                        self._close_dialog(checkin_dlg)
                        self._show_toast(msg, "error")
                    self.page.run_thread(show_fail)
            except Exception as e:
                print(f"[签到] 异常: {e}")
                def show_except():
                    self._close_dialog(checkin_dlg)
                    self._show_toast(f"签到失败: {str(e)[:20]}", "error")
                self.page.run_thread(show_except)

        threading.Thread(target=checkin_thread, daemon=True).start()

    # ========== 积分商城 ==========
    def _get_consumed_points(self):
        """获取本地已消费但未同步到服务器的积分（兼容旧数据）"""
        consumed = self.settings.get("consumed_points", 0)
        try:
            return int(consumed)
        except:
            return 0

    def _add_consumed_points(self, points):
        """记录本地消费积分（兼容旧数据）"""
        consumed = self._get_consumed_points() + points
        self.settings["consumed_points"] = consumed
        save_settings(self.settings)

    def _get_display_points(self):
        """获取显示用积分（优先API真实积分，减去本地未同步消费）"""
        api_points = 0
        try:
            pc = getattr(self, '_points_cache', {})
            if pc and isinstance(pc, dict):
                api_points = pc.get("points", 0)
        except:
            pass
        return max(0, api_points - self._get_consumed_points())

    def _load_purchases(self):
        """从API加载用户已购商品"""
        if not self.current_user:
            return
        try:
            user_id = self.current_user.get("id", "")
            ok, result = self._remote_api_request("GET", "user-purchases",
                params={"user_id": str(user_id)})
            if ok and isinstance(result, dict):
                data = result.get("data", result)
                self._purchases_cache = data
        except Exception as e:
            print(f"加载购买记录失败: {e}")


    # ========== 昵称颜色相关 ==========
    def _get_purchased_name_colors(self):
        """获取已购买的昵称颜色列表"""
        return self.data.get("purchased_name_colors", [])

    def _get_active_name_color(self):
        """获取当前激活的昵称颜色key"""
        return self.data.get("active_name_color", None)

    def _set_active_name_color(self, color_key):
        """设置激活的昵称颜色"""
        self.data["active_name_color"] = color_key
        save_data(self.data)

    def _add_purchased_name_color(self, color_key):
        """添加已购买的昵称颜色"""
        purchased = self._get_purchased_name_colors()
        if color_key not in purchased:
            purchased.append(color_key)
            self.data["purchased_name_colors"] = purchased
            save_data(self.data)

    def _get_colored_name_widget(self, name, size=14, weight=None):
        """获取带颜色的昵称Text控件（彩色名字用多字符渐变）"""
        if not name:
            return ft.Text("", size=size)
        active = self._get_active_name_color()
        if not active or active not in self.NAME_COLORS:
            return ft.Text(name, size=size, weight=weight, color=self.clr_text)
        color_cfg = self.NAME_COLORS[active]
        if color_cfg["color"] == "rainbow":
            # 彩色：每个字不同颜色
            chars = []
            for i, ch in enumerate(name):
                c = self.RAINBOW_COLORS[i % len(self.RAINBOW_COLORS)]
                chars.append(ft.Text(ch, size=size, weight=weight, color=c))
            return ft.Row(chars, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            return ft.Text(name, size=size, weight=weight, color=color_cfg["color"])

    def _get_cloud_drive_limit(self):
        """获取用户可创建的网盘数量（默认1个，每购买一次+1）"""
        # 优先从API缓存获取
        try:
            pc = getattr(self, '_purchases_cache', None)
            if pc and isinstance(pc, dict):
                slots = pc.get("cloud_drive_slots", 0)
                return 1 + int(slots)
        except:
            pass
        # 兜底用本地存储
        purchased = self.settings.get("purchased_drive_slots", 0)
        try:
            purchased = int(purchased)
        except:
            purchased = 0
        return 1 + purchased

    def _get_current_cloud_drive_count(self):
        """统计当前已创建的网盘数量（根目录下的文件夹）"""
        try:
            cached = getattr(self, '_cached_cloud_files', None)
            if cached and isinstance(cached, list):
                count = 0
                for f in cached:
                    if isinstance(f, dict) and f.get("type") == "folder":
                        count += 1
                return count
        except:
            pass
        return 0

    def render_points_shop(self):
        """积分商城页面"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None  # 顶部标题固定，只有内容区滚动
        self.page.floating_action_button = None

        # 顶部标题栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_points_page()),
                ft.Text("积分商城", size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 后台加载购买记录（如果未加载）
        if not getattr(self, '_purchases_cache', None):
            threading.Thread(target=self._load_purchases, daemon=True).start()

        # 当前积分
        my_points = self._get_display_points()

        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.STARS, size=24, color=ft.colors.WHITE),
                    width=48, height=48, bgcolor=ft.colors.AMBER, border_radius=14,
                    alignment=ft.alignment.center),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("我的积分", size=12, color=ft.colors.WHITE70),
                    ft.Text(str(my_points), size=26, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ], spacing=2, expand=True),
                ft.Container(content=ft.Text("签到赚积分", size=11, color=ft.colors.WHITE),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                    border_radius=10, padding=ft.padding.symmetric(horizontal=10, vertical=5)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.with_opacity(0.9, THEME_COLOR),
            border_radius=16, padding=16,
            margin=ft.margin.only(16, 12, 16, 6),
        ))

        # 商品列表标题
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.PURPLE, border_radius=2),
                ft.Container(width=6),
                ft.Text("兑换商品", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        # 网盘权限商品
        drive_limit = self._get_cloud_drive_limit()
        drive_count = self._get_current_cloud_drive_count()
        can_buy = my_points >= 50

        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.CLOUD_CIRCLE, size=28, color=ft.colors.WHITE),
                        width=52, height=52, bgcolor=ft.colors.BLUE, border_radius=14,
                        alignment=ft.alignment.center),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text("网盘创建权限", size=16, weight=ft.FontWeight.W_600, color=self.clr_text),
                        ft.Container(height=2),
                        ft.Text(f"当前可创建 {drive_limit} 个网盘，已创建 {drive_count} 个", size=11, color=self.clr_text2),
                    ], spacing=0, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=12),
                ft.Row([
                    ft.Container(content=ft.Row([
                        ft.Icon(ft.icons.STARS, size=14, color=ft.colors.AMBER),
                        ft.Container(width=2),
                        ft.Text("50", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER),
                    ], spacing=0), expand=True),
                    ft.Container(
                        content=ft.Text("立即兑换", size=14, weight=ft.FontWeight.W_600,
                            color=ft.colors.WHITE if can_buy else ft.colors.GREY_400),
                        bgcolor=THEME_COLOR if can_buy else ft.colors.GREY_300,
                        border_radius=10, padding=ft.padding.symmetric(horizontal=20, vertical=8),
                        on_click=lambda e: self._purchase_cloud_drive_slot() if can_buy else None,
                        ink=True if can_buy else False,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 2, 16, 6),
        ))


        # 昵称颜色商品
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.PINK, border_radius=2),
                ft.Container(width=6),
                ft.Text("昵称颜色", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        for color_key, color_cfg in self.NAME_COLORS.items():
            purchased = color_key in self._get_purchased_name_colors()
            can_buy = (not purchased) and my_points >= color_cfg["points"]
            is_active = self._get_active_name_color() == color_key

            # 颜色预览
            if color_cfg["color"] == "rainbow":
                preview_chars = []
                for i, ch in enumerate("彩色"):
                    c = self.RAINBOW_COLORS[i % len(self.RAINBOW_COLORS)]
                    preview_chars.append(ft.Text(ch, size=16, weight=ft.FontWeight.BOLD, color=c))
                color_preview = ft.Row(preview_chars, spacing=0)
            else:
                color_preview = ft.Text("昵称", size=16, weight=ft.FontWeight.BOLD, color=color_cfg["color"])

            # 按钮状态
            if purchased and is_active:
                btn_text = "使用中"
                btn_bg = ft.colors.GREEN
                btn_click = None
            elif purchased:
                btn_text = "使用"
                btn_bg = THEME_COLOR
                btn_click = lambda e, k=color_key: self._activate_name_color(k)
            else:
                btn_text = "立即兑换"
                btn_bg = THEME_COLOR if can_buy else ft.colors.GREY_300
                btn_click = lambda e, k=color_key: self._purchase_name_color(k) if can_buy else None

            scroll_content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=ft.Icon(color_cfg["icon"], size=24, color=ft.colors.WHITE),
                            width=44, height=44,
                            bgcolor=color_cfg["color"] if color_cfg["color"] != "rainbow" else ft.colors.PURPLE,
                            border_radius=12, alignment=ft.alignment.center),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(color_cfg["name"], size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Container(height=2),
                            color_preview,
                        ], spacing=0, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Container(content=ft.Row([
                            ft.Icon(ft.icons.STARS, size=14, color=ft.colors.AMBER),
                            ft.Container(width=2),
                            ft.Text(str(color_cfg["points"]), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER),
                        ], spacing=0), expand=True),
                        ft.Container(
                            content=ft.Text(btn_text, size=13, weight=ft.FontWeight.W_600,
                                color=ft.colors.WHITE if (can_buy or purchased) else ft.colors.GREY_400),
                            bgcolor=btn_bg,
                            border_radius=10, padding=ft.padding.symmetric(horizontal=16, vertical=7),
                            on_click=btn_click,
                            ink=True if (can_buy or purchased) else False,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=0),
                bgcolor=self.clr_card, border_radius=14, padding=14,
                margin=ft.margin.only(16, 2, 16, 6),
            ))

        # 说明
        scroll_content.controls.append(ft.Container(
            content=ft.Text("兑换后立即到账，积分不可退还", size=11,
                color=self.clr_text3, text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=16),
        ))

        self.content.controls.append(scroll_content)
        self.page.update()

    def _purchase_cloud_drive_slot(self):
        """购买网盘创建权限（50积分）"""
        if not self.current_user:
            self._show_toast("请先登录", "warning")
            return
        my_points = self._get_display_points()
        if my_points < 50:
            self._show_toast("积分不足，需要50积分", "error")
            return

        self._show_toast("正在兑换...", "info")

        def purchase_thread():
            try:
                user_id = self.current_user.get("id", "")
                # 调用购买API（自动校验积分并扣除）
                ok, result = self._remote_api_request("POST", "points-purchase",
                    body={"user_id": str(user_id), "item": "cloud_drive_slot",
                          "item_name": "网盘创建权限", "points": 50})
                if ok and isinstance(result, dict) and result.get("ok"):
                    # 购买成功：直接从缓存扣减积分（避免清空缓存导致显示0）
                    if isinstance(self._points_cache, dict) and "points" in self._points_cache:
                        self._points_cache["points"] = max(0, self._points_cache["points"] - 50)
                    self._purchases_cache = None
                    # 后台重新加载购买记录
                    threading.Thread(target=self._load_purchases, daemon=True).start()
                    def on_success():
                        self._show_toast("兑换成功！网盘权限+1", "success")
                        self.render_points_shop()
                    self.page.run_thread(on_success)
                else:
                    msg = "兑换失败"
                    if isinstance(result, dict):
                        msg = result.get("msg", "兑换失败")
                    self.page.run_thread(lambda: self._show_toast(msg, "error"))
            except Exception as e:
                self.page.run_thread(lambda: self._show_toast("兑换失败: " + str(e)[:15], "error"))

        threading.Thread(target=purchase_thread, daemon=True).start()


    def _purchase_name_color(self, color_key):
        """购买昵称颜色"""
        if not self.current_user:
            self._show_toast("请先登录", "warning")
            return
        if color_key not in self.NAME_COLORS:
            return
        color_cfg = self.NAME_COLORS[color_key]
        my_points = self._get_display_points()
        if my_points < color_cfg["points"]:
            self._show_toast(f"积分不足，需要{color_cfg['points']}积分", "error")
            return

        self._show_toast("正在兑换...", "info")

        def purchase_thread():
            try:
                user_id = self.current_user.get("id", "")
                ok, result = self._remote_api_request("POST", "points-purchase",
                    body={"user_id": str(user_id), "item": f"name_color_{color_key}",
                          "item_name": color_cfg["name"], "points": color_cfg["points"]})
                if ok and isinstance(result, dict) and result.get("ok"):
                    # 购买成功：直接从缓存扣减积分（避免清空缓存导致显示0）
                    if isinstance(self._points_cache, dict) and "points" in self._points_cache:
                        self._points_cache["points"] = max(0, self._points_cache["points"] - color_cfg["points"])
                    self._purchases_cache = None
                    self._add_purchased_name_color(color_key)
                    self._set_active_name_color(color_key)
                    threading.Thread(target=self._load_purchases, daemon=True).start()
                    def on_success():
                        self._show_toast(f"兑换成功！{color_cfg['name']}已激活", "success")
                        self.render_points_shop()
                    self.page.run_thread(on_success)
                else:
                    msg = "兑换失败"
                    if isinstance(result, dict):
                        msg = result.get("msg", "兑换失败")
                    self.page.run_thread(lambda: self._show_toast(msg, "error"))
            except Exception as e:
                self.page.run_thread(lambda: self._show_toast("兑换失败: " + str(e)[:15], "error"))

        threading.Thread(target=purchase_thread, daemon=True).start()

    def _activate_name_color(self, color_key):
        """激活已购买的昵称颜色（None表示恢复默认颜色）"""
        if color_key is not None and color_key not in self._get_purchased_name_colors():
            self._show_toast("请先兑换该颜色", "warning")
            return
        self._set_active_name_color(color_key)
        self._show_toast("昵称颜色已切换", "success")
        # 刷新当前页面
        if hasattr(self, '_name_color_page_active') and self._name_color_page_active:
            self.render_name_color_page()

    def render_name_color_page(self):
        """昵称颜色设置页面"""
        self._name_color_page_active = True
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None  # 顶部标题固定，只有内容区滚动
        self.page.floating_action_button = None

        # 顶部标题栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self._close_name_color_page()),
                ft.Text("修改昵称颜色", size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 当前昵称预览
        if self.current_user:
            username = self.current_user.get("username", "")
            name = self.current_user.get("name", username)
            preview_widget = self._get_colored_name_widget(name, size=22, weight=ft.FontWeight.BOLD)
            scroll_content.controls.append(ft.Container(
                content=ft.Column([
                    ft.Text("当前昵称预览", size=12, color=self.clr_text2),
                    ft.Container(height=8),
                    ft.Row([preview_widget], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=self.clr_card, border_radius=14, padding=16,
                margin=ft.margin.only(16, 12, 16, 6),
                alignment=ft.alignment.center,
            ))

        # 颜色列表标题
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.PINK, border_radius=2),
                ft.Container(width=6),
                ft.Text("选择颜色", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        # 默认颜色
        active = self._get_active_name_color()
        default_active = active is None
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.icons.TEXT_FIELDS, size=22, color=ft.colors.WHITE),
                    width=44, height=44, bgcolor=ft.colors.GREY_600, border_radius=12,
                    alignment=ft.alignment.center),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("默认颜色", size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                    ft.Container(height=2),
                    ft.Text("恢复原始昵称颜色", size=11, color=self.clr_text2),
                ], spacing=0, expand=True),
                ft.TextButton("使用中" if default_active else "使用",
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN if default_active else THEME_COLOR,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=16, vertical=7),
                    ),
                    on_click=lambda e: self._activate_name_color(None) if not default_active else None,
                    disabled=default_active,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 2, 16, 6),
        ))

        # 已购买的颜色
        for color_key, color_cfg in self.NAME_COLORS.items():
            purchased = color_key in self._get_purchased_name_colors()
            is_active = active == color_key

            if color_cfg["color"] == "rainbow":
                preview_chars = []
                for i, ch in enumerate("彩色昵称"):
                    c = self.RAINBOW_COLORS[i % len(self.RAINBOW_COLORS)]
                    preview_chars.append(ft.Text(ch, size=14, weight=ft.FontWeight.BOLD, color=c))
                color_preview = ft.Row(preview_chars, spacing=0)
            else:
                color_preview = ft.Text("彩色昵称", size=14, weight=ft.FontWeight.BOLD, color=color_cfg["color"])

            if not purchased:
                # 未购买：灰色显示，提示去积分商城
                scroll_content.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(color_cfg["icon"], size=22, color=ft.colors.GREY_400),
                            width=44, height=44, bgcolor=ft.colors.GREY_200, border_radius=12,
                            alignment=ft.alignment.center),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(color_cfg["name"], size=15, weight=ft.FontWeight.W_600, color=ft.colors.GREY_500),
                            ft.Container(height=2),
                            ft.Text(f"需{color_cfg['points']}积分兑换", size=11, color=ft.colors.GREY_400),
                        ], spacing=0, expand=True),
                        ft.Container(
                            content=ft.Text("去兑换", size=13, weight=ft.FontWeight.W_600, color=THEME_COLOR),
                            on_click=lambda e: self.render_points_shop(),
                            ink=True,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=14, padding=14,
                    margin=ft.margin.only(16, 2, 16, 6),
                    opacity=0.6,
                ))
            else:
                scroll_content.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(color_cfg["icon"], size=22, color=ft.colors.WHITE),
                            width=44, height=44,
                            bgcolor=color_cfg["color"] if color_cfg["color"] != "rainbow" else ft.colors.PURPLE,
                            border_radius=12, alignment=ft.alignment.center),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(color_cfg["name"], size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Container(height=2),
                            color_preview,
                        ], spacing=0, expand=True),
                        ft.TextButton("使用中" if is_active else "使用",
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.GREEN if is_active else THEME_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.padding.symmetric(horizontal=16, vertical=7),
                            ),
                            on_click=lambda e, k=color_key: self._activate_name_color(k) if not is_active else None,
                            disabled=is_active,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=14, padding=14,
                    margin=ft.margin.only(16, 2, 16, 6),
                ))

        scroll_content.controls.append(ft.Container(height=20))
        self.content.controls.append(scroll_content)
        self.page.update()

    def _close_name_color_page(self):
        """关闭昵称颜色页面，返回个人主页"""
        self._name_color_page_active = False
        self.show_user_profile()

    # ========== 设置页面 ==========
    def render_settings_page(self):
        self._hide_navbar()  # 进入设置页面隐藏导航栏
        self.content.controls.clear()
        self.content.scroll = None  # 关闭整体滚动，标题固定

        # ---- 顶部固定栏 ----
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_me_page()),
                ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW, icon_size=20, icon_color=self.clr_text,
                    on_click=self._back_to_features, visible=getattr(self, "_show_back_to_features", False)),
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

        # 登录设备（点击查看当前设备和历史登录记录）
        scroll_content.controls.append(self._build_menu_item(
            icon=ft.icons.DEVICES, icon_color=ft.colors.CYAN,
            label="登录设备", on_click=lambda e: self._show_device_page(),
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
                ft.Text(f"YoXi网盘 v{_app_ver}", size=12, color=self.clr_text2,
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
        # 本地图标路径（尝试多种路径确保移动端兼容）
        def _find_asset_path(filename):
            candidate_paths = [
                os.path.join(_base_dir, "assets", filename),
                os.path.join(os.getcwd(), "assets", filename),
                "assets/" + filename,
                filename,
            ]
            for p in candidate_paths:
                if os.path.exists(p):
                    return p
            return candidate_paths[0]
        
        local_icon_path = _find_asset_path("default_icon.png")
        qq_icon_path = _find_asset_path("qq_email_icon.png")
        netease_icon_path = _find_asset_path("netease_email_icon.png")
        gmail_icon_path = _find_asset_path("gmail_icon.png")
        custom_icon_1 = _find_asset_path("custom_icon_1.png")
        custom_icon_2 = _find_asset_path("custom_icon_2.png")
        custom_icon_3 = _find_asset_path("custom_icon_3.png")
        custom_icon_4 = _find_asset_path("custom_icon_4.png")
        custom_icon_5 = _find_asset_path("custom_icon_5.png")
        custom_icon_6 = _find_asset_path("custom_icon_6.png")
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
                    content=ft.Image(src=icon_info["image_path"], width=56, height=56, fit=ft.ImageFit.COVER),
                    width=56, height=56,
                    border_radius=16,
                    alignment=ft.alignment.center,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
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
            current_icon_widget = ft.Container(
                content=ft.Image(src=current_icon, width=32, height=32, fit=ft.ImageFit.COVER),
                width=32, height=32, border_radius=9,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.alignment.center,
            )
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
        self._show_toast("应用图标已更新，重启应用后生效")
        self.render_settings_page()

    def _pick_custom_icon(self):
        """打开文件选择器，让用户选择自定义图标（支持移动端相册）"""
        try:
            # 使用Flet原生文件选择器，支持移动端相册
            def on_file_picked(e):
                try:
                    if e.files and len(e.files) > 0:
                        file_path = e.files[0].path
                        if file_path:
                            # 复制用户选择的图片到assets目录
                            import shutil
                            custom_icon_path = os.path.join(_base_dir, "assets", "user_custom_icon.png")
                            # 确保assets目录存在
                            os.makedirs(os.path.dirname(custom_icon_path), exist_ok=True)
                            shutil.copy(file_path, custom_icon_path)
                            # 保存自定义图标
                            self.settings["app_icon"] = custom_icon_path
                            self.settings["app_icon_type"] = "custom"
                            save_settings(self.settings)
                            self._show_toast("自定义图标已设置，重启应用后生效")
                            # 刷新设置页面
                            self.render_settings_page()
                    else:
                        self._show_toast("未选择图片")
                except Exception as ex:
                    self._show_toast(f"选择图片失败: {str(ex)}")
            
            # 创建文件选择器
            file_picker = ft.FilePicker(on_result=on_file_picked)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            # 打开文件选择器，只允许选择图片
            file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["png", "jpg", "jpeg", "gif", "bmp", "webp"],
                dialog_title="选择应用图标"
            )
        except Exception as e:
            self._show_toast(f"打开相册失败: {str(e)}")
    
    def _get_current_app_icon(self):
        """获取当前应用图标（支持图片和emoji）"""
        icon_type = self.settings.get("app_icon_type", "image")
        if icon_type == "image":
            # 图片图标，返回图片路径（尝试多种路径，确保移动端兼容）
            user_icon = self.settings.get("app_icon", "")
            if user_icon and os.path.exists(user_icon):
                return user_icon
            # 尝试多种默认图标路径
            candidate_paths = [
                os.path.join(_base_dir, "assets", "default_icon.png"),
                os.path.join(os.getcwd(), "assets", "default_icon.png"),
                "assets/default_icon.png",
            ]
            for path in candidate_paths:
                if os.path.exists(path):
                    return path
            # 如果都不存在，返回第一个候选路径
            return candidate_paths[0]
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
            filename = "empty_email_icon_dark.png"
        else:
            # 白天模式或跟随系统（默认白天）：白色背景，黑色邮箱
            filename = "empty_email_icon.png"
        # 尝试多种路径
        candidate_paths = [
            os.path.join(_base_dir, "assets", filename),
            os.path.join(os.getcwd(), "assets", filename),
            "assets/" + filename,
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                return path
        return candidate_paths[0]

    def _build_app_icon_widget(self, size=28):
        """构建应用图标组件（支持图片、emoji和自定义）"""
        icon_type = self._get_current_app_icon_type()
        icon_value = self._get_current_app_icon()
        if icon_type in ("image", "custom"):
            # 图片图标和自定义图标都用圆角正方形显示
            return ft.Container(
                content=ft.Image(src=icon_value, width=size, height=size, fit=ft.ImageFit.COVER),
                width=size, height=size, border_radius=size//4,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.alignment.center,
            )
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

    def _show_device_page(self):
        """登录设备页面：当前设备信息 + 历史登录记录"""
        self._hide_navbar()
        self.content.controls.clear()
        self.content.scroll = None  # 顶部标题固定
        self.page.floating_action_button = None

        # 顶部标题栏
        self.content.controls.append(ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, icon_size=22,
                    on_click=lambda e: self.render_settings_page()),
                ft.Text("登录设备", size=20, weight=ft.FontWeight.BOLD, expand=True, color=self.clr_text),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(8, 45, 12, 8),
            bgcolor=self.clr_bg,
        ))
        self.content.controls.append(ft.Container(height=1, bgcolor=self.clr_border))

        scroll_content = ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # 当前设备卡片
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.GREEN, border_radius=2),
                ft.Container(width=6),
                ft.Text("当前设备", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 14, 20, 6),
        ))

        self._cur_device_ip = ft.Text("获取中...", size=14, color=self.clr_text)
        self._cur_device_model = ft.Text("获取中...", size=14, color=self.clr_text)
        self._cur_device_time = ft.Text("刚刚", size=12, color=self.clr_text3)

        scroll_content.controls.append(ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.DEVICES, size=22, color=ft.colors.WHITE),
                        width=44, height=44, bgcolor=ft.colors.CYAN, border_radius=12,
                        alignment=ft.alignment.center),
                    ft.Container(width=12),
                    ft.Column([
                        self._cur_device_model,
                        ft.Container(height=2),
                        self._cur_device_ip,
                    ], spacing=0, expand=True),
                    ft.Container(content=ft.Text("在线", size=11, color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN, border_radius=10,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3)),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Row([
                    ft.Icon(ft.icons.ACCESS_TIME, size=12, color=self.clr_text3),
                    ft.Container(width=4),
                    self._cur_device_time,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0),
            bgcolor=self.clr_card, border_radius=14, padding=14,
            margin=ft.margin.only(16, 2, 16, 6),
        ))

        # 历史登录记录
        scroll_content.controls.append(ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=ft.colors.GREY, border_radius=2),
                ft.Container(width=6),
                ft.Text("历史登录", size=13, color=self.clr_text2, weight=ft.FontWeight.W_600),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(20, 10, 20, 6),
        ))

        self._device_history_list = ft.Column([], spacing=0)
        scroll_content.controls.append(self._device_history_list)

        # 初始显示加载中
        self._device_history_list.controls.append(ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=28, height=28, color=THEME_COLOR, stroke_width=2),
                ft.Container(height=8),
                ft.Text("加载中...", size=13, color=self.clr_text2),
            ], alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=40),
        ))

        self.content.controls.append(scroll_content)
        self.page.update()

        # 后台获取当前设备信息和历史记录
        threading.Thread(target=self._load_device_data, daemon=True).start()

    def _load_device_data(self):
        """加载当前设备信息和历史登录记录（对接网站API）"""
        import platform
        import socket
        import time

        user_id = self.current_user.get("id", "") if self.current_user else ""
        if not user_id:
            def update_no_login():
                if hasattr(self, '_cur_device_ip'):
                    self._cur_device_ip.value = "未登录"
                if hasattr(self, '_cur_device_model'):
                    self._cur_device_model.value = "请先登录"
                if hasattr(self, '_device_history_list'):
                    self._device_history_list.controls.clear()
                    self._device_history_list.controls.append(ft.Container(
                        content=ft.Text("登录后查看历史记录", size=13, color=self.clr_text2,
                            text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(vertical=30),
                    ))
                self.page.update()
            self.page.run_thread(update_no_login)
            return

        # 获取本地设备信息
        dev = self._get_device_info()
        device_model = f"{dev['device_model']} ({dev['os_version']})"
        device_ip = "获取中..."
        try:
            import urllib.request
            req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                device_ip = resp.read().decode("utf-8").strip()
        except:
            try:
                device_ip = socket.gethostbyname(socket.gethostname())
            except:
                device_ip = "未知"

        # 从API获取历史登录记录
        records = []
        try:
            ok, result = self._remote_api_request("GET", "user-login-devices",
                params={"user_id": str(user_id), "limit": "20"})
            if ok and isinstance(result, dict) and result.get("ok"):
                records = result.get("records", [])
        except Exception as e:
            print(f"[设备记录] 获取失败: {e}")

        login_time = time.strftime("%Y-%m-%d %H:%M:%S")

        def update_ui():
            # 当前设备
            if hasattr(self, '_cur_device_ip'):
                self._cur_device_ip.value = f"IP: {device_ip}"
            if hasattr(self, '_cur_device_model'):
                self._cur_device_model.value = device_model
            if hasattr(self, '_cur_device_time'):
                # 用最新一条记录的时间，如果没有则用当前时间
                if records and isinstance(records[0], dict):
                    self._cur_device_time.value = f"登录时间：{records[0].get('login_time', login_time)}"
                else:
                    self._cur_device_time.value = f"登录时间：{login_time}"
            # 历史记录
            if hasattr(self, '_device_history_list'):
                self._device_history_list.controls.clear()
                if not records:
                    self._device_history_list.controls.append(ft.Container(
                        content=ft.Text("暂无历史登录记录", size=13, color=self.clr_text2,
                            text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(vertical=30),
                    ))
                else:
                    for rec in records:
                        if not isinstance(rec, dict):
                            continue
                        rec_device = rec.get("device", "未知设备")
                        rec_ip = rec.get("ip_address", "未知")
                        rec_time = rec.get("login_time", "")
                        rec_status = rec.get("status", "success")
                        status_color = ft.colors.GREEN if rec_status == "success" else ft.colors.RED
                        status_text = "成功" if rec_status == "success" else "失败"
                        self._device_history_list.controls.append(ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(content=ft.Icon(ft.icons.DEVICES, size=16, color=ft.colors.WHITE),
                                        width=32, height=32, bgcolor=ft.colors.CYAN, border_radius=8,
                                        alignment=ft.alignment.center),
                                    ft.Container(width=10),
                                    ft.Column([
                                        ft.Text(rec_device, size=13, weight=ft.FontWeight.W_500, color=self.clr_text,
                                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Container(height=2),
                                        ft.Text(f"IP: {rec_ip}", size=11, color=self.clr_text2),
                                    ], spacing=0, expand=True),
                                    ft.Container(content=ft.Text(status_text, size=10, color=ft.colors.WHITE),
                                        bgcolor=status_color, border_radius=8,
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2)),
                                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Container(height=4),
                                ft.Row([
                                    ft.Icon(ft.icons.ACCESS_TIME, size=11, color=self.clr_text3),
                                    ft.Container(width=4),
                                    ft.Text(rec_time, size=11, color=self.clr_text3),
                                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ], spacing=0),
                            bgcolor=self.clr_card, border_radius=12, padding=12,
                            margin=ft.margin.only(16, 2, 16, 2),
                        ))
                self.page.update()
        self.page.run_thread(update_ui)

    def _fetch_device_info(self):
        """获取设备登录IP和型号（先本地获取，后面对接网站API）"""
        try:
            import platform
            import socket
            # 获取设备型号（电脑名+系统）
            device_model = f"{platform.node()} ({platform.system()} {platform.release()})"
            # 获取公网IP
            device_ip = "未知"
            try:
                import urllib.request
                req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    device_ip = resp.read().decode("utf-8").strip()
            except:
                try:
                    device_ip = socket.gethostbyname(socket.gethostname())
                except:
                    device_ip = "获取失败"
            def update_ui():
                if hasattr(self, '_device_ip_text'):
                    self._device_ip_text.value = device_ip
                    self._device_ip_text.color = self.clr_text
                if hasattr(self, '_device_model_text'):
                    self._device_model_text.value = device_model
                    self._device_model_text.color = self.clr_text
                self.page.update()
            self.page.run_thread(update_ui)
        except Exception as e:
            print(f"[设备信息] 获取失败: {e}")

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
        # 网盘数据缓存（加载页预加载，避免每次进入都重新请求）
        self._cached_cloud_files = None
        self._cached_cloud_used_mb = 0
        self._cloud_files_loading = False
        self.current_folder_id = 0  # 当前所在文件夹ID，0表示根目录
        self.folder_path = []  # 文件夹路径栈，用于返回上级

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
        # 重新渲染当前页面以应用新颜色（4标签：0网盘/1功能/2频道/3主页）
        try:
            if self.current_tab == 0:
                self.render_cloud_drive_page()
            elif self.current_tab == 1:
                self.render_features_page()
            elif self.current_tab == 2:
                self.render_channel_page()
            elif self.current_tab == 3:
                self.render_me_page()
        except:
            pass
        # 强制刷新页面背景和顶部
        try:
            self.page.update()
        except:
            pass

    # ========== 个人主页详情 ==========
    def show_user_profile(self, e=None):
        """显示个人主页详细信息"""
        if not self.current_user:
            return
        self._hide_navbar()  # 进入个人主页隐藏导航栏
        self.content.controls.clear()
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
                    self._get_colored_name_widget(name or username or "用户", size=20, weight=ft.FontWeight.BOLD),
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

        # 修改昵称颜色（账户信息里昵称下面）
        if self.current_user:
            active_color = self._get_active_name_color()
            if active_color and active_color in self.NAME_COLORS:
                color_cfg = self.NAME_COLORS[active_color]
                if color_cfg["color"] == "rainbow":
                    color_label = "彩色"
                    color_icon_bg = ft.colors.PURPLE
                else:
                    color_label = color_cfg["name"].replace("名字", "")
                    color_icon_bg = color_cfg["color"]
            else:
                color_label = "默认"
                color_icon_bg = ft.colors.GREY_600
            scroll_content.controls.append(ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(ft.icons.COLOR_LENS, size=20, color=ft.colors.WHITE),
                        width=36, height=36, bgcolor=color_icon_bg,
                        border_radius=10, alignment=ft.alignment.center),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text("修改昵称颜色", size=14, weight=ft.FontWeight.W_600, color=self.clr_text),
                        ft.Container(height=1),
                        ft.Text("当前：" + color_label, size=11, color=self.clr_text2),
                    ], spacing=0, expand=True),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, size=18, color=self.clr_text3),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.clr_card, border_radius=12, padding=14,
                margin=ft.margin.only(16, 2, 16, 2),
                on_click=lambda e: self.render_name_color_page(),
                ink=True,
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

    def _close_dialog(self, dlg=None):
        """通用关闭对话框方法，支持传入dlg或不传（关闭当前对话框）"""
        try:
            if dlg:
                dlg.open = False
            else:
                # 没有传入dlg，直接关闭当前对话框
                if self.page.dialog:
                    try:
                        self.page.dialog.open = False
                    except:
                        pass
            self.page.update()
        except:
            try:
                self.page.dialog = None
                self.page.update()
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
        """检查更新（实时调用API）"""
        current_version = APP_CONFIG.get("app_version", "1.0.0")
        self._show_toast("正在检查更新...", "info")

        def check_thread():
            try:
                ok, result = self._remote_api_request("GET", "status")
                if ok and isinstance(result, dict):
                    need_update = result.get("need_update", False)
                    target_version = result.get("target_version", "")
                    download_url = result.get("download_url", "")
                    force_update = result.get("force_update", False)
                    # 缓存最新状态
                    self._remote_config = result
                    # 判断是否需要更新
                    has_update = need_update and target_version and target_version != current_version
                    if has_update:
                        content_text = f"发现新版本 {target_version}\n当前版本 {current_version}\n\n点击确定前往下载"
                    else:
                        content_text = f"当前已是最新版本\n版本号: {current_version}"

                    def go_update(ev):
                        self._close_dialog()
                        url = download_url or APP_CONFIG.get("update_url", "")
                        if url:
                            try:
                                self.page.launch_url(url)
                            except:
                                try:
                                    import webbrowser
                                    webbrowser.open(url)
                                except:
                                    pass

                    actions = [ft.TextButton("关闭", on_click=lambda ev: self._close_dialog())]
                    if has_update:
                        actions.append(ft.TextButton("去更新", on_click=go_update))

                    def show_dialog():
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
                    self.page.run_thread(show_dialog)
                else:
                    self.page.run_thread(lambda: self._show_toast("检查更新失败，请稍后重试", "error"))
            except Exception as ex:
                self.page.run_thread(lambda: self._show_toast("检查更新失败: " + str(ex)[:20], "error"))

        threading.Thread(target=check_thread, daemon=True).start()

    def _clear_cache(self, e=None):
        """弹出清除选项：清除缓存 / 清除登录设备历史记录"""
        def do_clear_cache(ev):
            self._close_dialog()
            self._do_clear_cache()

        def do_clear_login_history(ev):
            self._close_dialog()
            self._clear_login_history()

        self.page.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.CLEANING_SERVICES, size=22, color=ft.colors.GREEN),
                ft.Container(width=8),
                ft.Text("清除数据", size=18, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.icons.DELETE_SWEEP, size=18, color=ft.colors.BLUE),
                            width=36, height=36, bgcolor=ft.colors.BLUE_50,
                            border_radius=10, alignment=ft.alignment.center),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text("清除缓存", size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Text("清除邮箱、频道等本地缓存数据", size=11, color=self.clr_text2),
                        ], spacing=2, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=12, padding=12,
                    on_click=do_clear_cache, ink=True,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.icons.HISTORY_TOGGLE_OFF, size=18, color=ft.colors.RED),
                            width=36, height=36, bgcolor=ft.colors.RED_50,
                            border_radius=10, alignment=ft.alignment.center),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text("清除登录设备记录", size=15, weight=ft.FontWeight.W_600, color=self.clr_text),
                            ft.Text("删除网站上保存的登录历史记录", size=11, color=self.clr_text2),
                        ], spacing=2, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.clr_card, border_radius=12, padding=12,
                    on_click=do_clear_login_history, ink=True,
                ),
            ], spacing=0, tight=True),
            actions=[
                ft.TextButton("取消", on_click=lambda ev: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _do_clear_cache(self):
        """实际执行清除缓存"""
        try:
            self._cloud_emails_cache = []
            self._msg_counts = {}
            self._last_email_sync_time = 0
            self._points_cache = None
            self._cached_cloud_files = None
            if hasattr(self, '_cached_channel_messages'):
                self._cached_channel_messages = []
            if hasattr(self, '_last_channel_msg_load_time'):
                self._last_channel_msg_load_time = 0

            self._show_toast("缓存已清理，正在重新同步...", "success")

            def reload_background():
                time.sleep(0.3)
                try:
                    self._sync_emails_from_cloud()
                except:
                    pass
            threading.Thread(target=reload_background, daemon=True).start()
        except Exception as ex:
            self._show_toast("清理缓存失败: " + str(ex)[:20], "error")

    def _clear_login_history(self):
        """清除登录设备历史记录（调用网站API）"""
        if not self.current_user:
            self._show_toast("请先登录", "warning")
            return
        user_id = self.current_user.get("id", "")
        if not user_id:
            self._show_toast("用户信息异常", "error")
            return
        self._show_toast("正在清除登录记录...", "info")

        def clear_thread():
            try:
                ok, result = self._remote_api_request("DELETE", "user-login-devices",
                    params={"user_id": str(user_id)})
                if ok and isinstance(result, dict) and result.get("ok"):
                    self.page.run_thread(lambda: self._show_toast("登录记录已清除", "success"))
                else:
                    msg = "网站暂未开放清除登录记录功能"
                    if isinstance(result, dict) and result.get("msg"):
                        msg = result.get("msg")
                    self.page.run_thread(lambda: self._show_toast(msg, "error"))
            except Exception as ex:
                err_str = str(ex)
                if "404" in err_str or "405" in err_str:
                    self.page.run_thread(lambda: self._show_toast("网站暂未开放此功能，请在后台添加接口", "error"))
                else:
                    self.page.run_thread(lambda: self._show_toast("清除失败: " + err_str[:15], "error"))

        threading.Thread(target=clear_thread, daemon=True).start()

    def _join_qq_group(self, e=None):
        """加入QQ群（浏览器打开QQ群网页）"""
        try:
            qq_group_number = "1093927643"
            # 浏览器打开QQ群网页链接
            qq_group_url = f"https://qm.qq.com/cgi-bin/qm/qr?k={qq_group_number}&jump_from=webapi"
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
            app_name = APP_CONFIG.get("app_name", "YoXi网盘")
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
            self._points_cache = None
            self._purchases_cache = None
            self._cached_cloud_files = None
            self._cached_cloud_used_mb = 0
            self._cloud_emails_cache = []
            # 清除本地消费记录（切换账号后不继承）
            if "consumed_points" in self.settings:
                self.settings["consumed_points"] = 0
            if "purchased_drive_slots" in self.settings:
                self.settings["purchased_drive_slots"] = 0
            # 重置默认有效期为1小时（切换账号后不继承上一个账号的设置）
            self.settings["default_duration_hours"] = 1
            save_settings(self.settings)
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
        win_title = APP_CONFIG.get("app_name", "YoXi网盘")
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

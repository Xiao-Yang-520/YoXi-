# -*- coding: utf-8 -*-
"""
临时邮箱 App —— 纯 Python (Kivy) 实现
无限创建一次性邮箱，每个有效期1小时，自动接收邮件
基于 mail.tm 免费 API
支持 iOS / Android / Windows / macOS / Linux
"""

import json
import os
import random
import re
import string
import sys
import threading
import time
from datetime import datetime

# ── 加载配置文件（config.json）──
DEFAULT_CONFIG = {
    "app_name": "临时邮箱",
    "app_version": "1.0.0",
    "remote_config_url": "",
    "email_lifetime_seconds": 3600,
    "auto_refresh_seconds": 3,
    "window_width": 375,
    "window_height": 812,
    "theme_color": "#007AFF",
    "enable_phone_tab": True,
    "phone_numbers": [
        {"country": "美国", "number": "+1 201-351-6280"},
        {"country": "英国", "number": "+44 7862-012-345"},
    ],
}

# 远程控制配置默认值
REMOTE_CONFIG_DEFAULT = {
    "enabled": "是",
    "maintenance": "否",
    "maintenance_message": "系统维护中，请稍后再试",
    "latest_version": "1.0.0",
    "update_url": "",
    "update_message": "",
    "notice": "",
    "force_update": "否",
    "disabled_message": "应用已停用，请联系开发者",
}

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    cfg = dict(DEFAULT_CONFIG)
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg.update(user_cfg)
    except Exception:
        pass
    return cfg

APP_CONFIG = load_config()

# ── 中文字体设置（必须在导入其他 kivy 模块之前）──
from kivy.config import Config

def _find_chinese_font():
    candidates = []
    if sys.platform == "win32":
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

_chinese_font = _find_chinese_font()
if _chinese_font:
    Config.set("kivy", "default_font", ["ChineseFont", _chinese_font])

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

# ─────────────────────── 全局配置 ───────────────────────

Window.size = (APP_CONFIG["window_width"], APP_CONFIG["window_height"])
Window.clearcolor = get_color_from_hex("#F2F2F7")

# iOS 配色（主题色从配置读取）
IOS_BLUE = get_color_from_hex(APP_CONFIG["theme_color"])
IOS_GRAY = get_color_from_hex("#F2F2F7")
IOS_GRAY2 = get_color_from_hex("#E5E5EA")
IOS_DARK = get_color_from_hex("#1C1C1E")
IOS_LABEL = get_color_from_hex("#3C3C43")
IOS_SECONDARY = get_color_from_hex("#8E8E93")
IOS_RED = get_color_from_hex("#FF3B30")
IOS_GREEN = get_color_from_hex("#34C759")
IOS_ORANGE = get_color_from_hex("#FF9500")
WHITE = get_color_from_hex("#FFFFFF")

# mail.tm API
API_BASE = "https://api.mail.tm"
EMAIL_LIFETIME = APP_CONFIG["email_lifetime_seconds"]


# ─────────────────────── 数据存储 ───────────────────────

class EmailStore:
    def __init__(self):
        if os.path.exists("/Documents"):
            data_dir = "/Documents"
        else:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.store = JsonStore(os.path.join(data_dir, "tempmail.json"))
        if not self.store.exists("emails"):
            self.store.put("emails", items=[])

    def load(self):
        return self.store.get("emails")["items"]

    def save(self, emails):
        self.store.put("emails", items=emails)


# ─────────────────────── API 调用（后台线程）───

def api_create_email(callback):
    """创建 mail.tm 邮箱：获取域名 → 创建账户 → 获取 token"""
    def worker():
        try:
            # 1. 获取可用域名
            r = requests.get(f"{API_BASE}/domains", timeout=15)
            r.raise_for_status()
            domains = r.json().get("hydra:member", [])
            if not domains:
                raise Exception("没有可用域名")
            domain = domains[0]["domain"]

            # 2. 生成随机地址和密码
            name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
            address = f"{name}@{domain}"
            password = "".join(random.choices(string.ascii_letters + string.digits, k=20))

            # 3. 创建账户
            r = requests.post(f"{API_BASE}/accounts", json={
                "address": address,
                "password": password,
            }, timeout=15)
            r.raise_for_status()

            # 4. 获取 token
            r = requests.post(f"{API_BASE}/token", json={
                "address": address,
                "password": password,
            }, timeout=15)
            r.raise_for_status()
            token = r.json().get("token")
            if not token:
                raise Exception("获取 token 失败")

            email_data = {
                "address": address,
                "domain": domain,
                "password": password,
                "token": token,
            }
            Clock.schedule_once(lambda dt: callback(True, email_data))
        except Exception as e:
            err_msg = str(e)
            Clock.schedule_once(lambda dt: callback(False, err_msg))
    threading.Thread(target=worker, daemon=True).start()


def api_login(address, password, callback):
    """用邮箱地址和密码重新获取 token"""
    def worker():
        try:
            r = requests.post(f"{API_BASE}/token", json={
                "address": address,
                "password": password,
            }, timeout=15)
            r.raise_for_status()
            token = r.json().get("token")
            if not token:
                raise Exception("获取 token 失败")
            Clock.schedule_once(lambda dt: callback(True, token))
        except Exception as e:
            err_msg = str(e)
            Clock.schedule_once(lambda dt: callback(False, err_msg))
    threading.Thread(target=worker, daemon=True).start()


def api_check_inbox(token, callback):
    """检查收件箱"""
    def worker():
        try:
            r = requests.get(f"{API_BASE}/messages", headers={
                "Authorization": f"Bearer {token}",
            }, timeout=15)
            r.raise_for_status()
            messages = r.json().get("hydra:member", [])
            Clock.schedule_once(lambda dt: callback(True, messages))
        except Exception as e:
            err_msg = str(e)
            Clock.schedule_once(lambda dt: callback(False, err_msg))
    threading.Thread(target=worker, daemon=True).start()


def api_read_message(token, msg_id, callback):
    """读取邮件详情"""
    def worker():
        try:
            r = requests.get(f"{API_BASE}/messages/{msg_id}", headers={
                "Authorization": f"Bearer {token}",
            }, timeout=15)
            r.raise_for_status()
            msg = r.json()
            Clock.schedule_once(lambda dt: callback(True, msg))
        except Exception as e:
            err_msg = str(e)
            Clock.schedule_once(lambda dt: callback(False, err_msg))
    threading.Thread(target=worker, daemon=True).start()


# ─────────────────────── 工具函数 ───────────────────────

def api_fetch_remote_config(url, callback):
    """拉取远程控制配置"""
    def worker():
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            cfg = r.json()
            merged = dict(REMOTE_CONFIG_DEFAULT)
            merged.update(cfg)
            Clock.schedule_once(lambda dt: callback(True, merged))
        except Exception as e:
            err_msg = str(e)
            Clock.schedule_once(lambda dt: callback(False, err_msg))
    threading.Thread(target=worker, daemon=True).start()


def strip_html(html):
    """去除 HTML 标签，返回纯文本"""
    if not html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    text = re.sub(r'<p\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def format_time_remaining(seconds):
    """格式化剩余时间"""
    if seconds <= 0:
        return "已过期"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}时{m}分"
    return f"{m}分{s}秒"


def format_date(date_str):
    """格式化邮件日期（支持 ISO 8601 和普通格式）"""
    if not date_str:
        return ""
    try:
        # mail.tm ISO 8601: 2024-01-01T12:00:00+00:00
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%m-%d %H:%M")
    except:
        pass
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%m-%d %H:%M")
    except:
        return date_str[:16]


def get_sender(msg):
    """从邮件数据中提取发件人地址"""
    sender = msg.get("from", "")
    if isinstance(sender, dict):
        return sender.get("address", sender.get("name", "未知"))
    return str(sender)


def get_email_provider(email):
    """根据邮箱地址返回服务商信息 (颜色, 文字)"""
    email = email.lower().strip()
    if "@" in email:
        domain = email.split("@")[1]
    else:
        domain = email

    if domain in ("qq.com", "vip.qq.com", "foxmail.com"):
        return (get_color_from_hex("#12B7F5"), "QQ")
    if domain in ("163.com", "126.com", "yeah.net"):
        return (get_color_from_hex("#E60012"), "163")
    if domain == "gmail.com":
        return (get_color_from_hex("#EA4335"), "G")
    if domain in ("outlook.com", "hotmail.com", "live.com", "msn.com"):
        return (get_color_from_hex("#0078D4"), "O")
    if domain in ("sina.com", "sina.cn"):
        return (get_color_from_hex("#E6162D"), "S")
    if domain == "sohu.com":
        return (get_color_from_hex("#FF6600"), "S")
    if domain == "aliyun.com":
        return (get_color_from_hex("#FF6A00"), "A")
    if domain in ("139.com", "189.cn", "wo.cn"):
        return (get_color_from_hex("#00A0E9"), "M")
    # 企业邮箱/其他
    first = email[0].upper() if email and email[0].isalnum() else "?"
    return (get_color_from_hex("#8E8E93"), first)


# ─────────────────────── 自定义控件 ───────────────────────

class RoundedButton(Button):
    def __init__(self, bg_color=IOS_BLUE, text_color=WHITE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        with self.canvas.before:
            self._color = Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_bg(self, color):
        self._color.rgba = color


class EmailCard(BoxLayout):
    """邮箱卡片"""
    def __init__(self, email_data, on_open, on_delete, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(104)
        self.padding = [dp(18), dp(14), dp(18), dp(14)]
        self.spacing = dp(8)
        self.email_data = email_data
        self.on_open = on_open
        self.on_delete = on_delete
        self._touch_start = None

        with self.canvas.before:
            Color(0, 0, 0, 0.06)
            self._shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(3)),
                size=(self.width - dp(4), self.height),
                radius=[dp(16)]
            )
            Color(*WHITE)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
        self.addr_label = Label(
            text=email_data["address"],
            color=IOS_DARK, font_size=sp(17), bold=True,
            halign="left", valign="center",
        )
        self.addr_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        self.del_btn = Button(
            text="删除", size_hint=(None, None), size=(dp(56), dp(30)),
            background_normal="", background_color=(0, 0, 0, 0),
            color=IOS_RED, font_size=sp(13), bold=True,
        )
        with self.del_btn.canvas.before:
            Color(1, 0.23, 0.19, 0.1)
            self._del_bg = RoundedRectangle(pos=self.del_btn.pos, size=self.del_btn.size, radius=[dp(8)])
        self.del_btn.bind(pos=self._update_del_bg, size=self._update_del_bg)
        self.del_btn.bind(on_release=lambda x: on_delete(email_data["id"]))
        row1.add_widget(self.addr_label)
        row1.add_widget(self.del_btn)

        row2 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        self.time_label = Label(
            text="", color=IOS_SECONDARY, font_size=sp(13),
            halign="left", valign="center",
        )
        self.time_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        self.unread_label = Label(
            text="", color=IOS_BLUE, font_size=sp(13), bold=True,
            halign="right", valign="center",
        )
        row2.add_widget(self.time_label)
        row2.add_widget(self.unread_label)

        self.add_widget(row1)
        self.add_widget(row2)

    def _update_bg(self, *args):
        self._shadow.pos = (self.x + dp(2), self.y - dp(3))
        self._shadow.size = (self.width - dp(4), self.height)
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_del_bg(self, *args):
        self._del_bg.pos = self.del_btn.pos
        self._del_bg.size = self.del_btn.size

    def update_time(self, remaining):
        self.time_label.text = f"剩余: {format_time_remaining(remaining)}"
        if remaining <= 0:
            self.time_label.color = IOS_RED
        elif remaining < 300:
            self.time_label.color = IOS_ORANGE
        else:
            self.time_label.color = IOS_SECONDARY

    def update_unread(self, count):
        if count > 0:
            self.unread_label.text = f"{count} 封未读"
        else:
            self.unread_label.text = "暂无邮件"

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.del_btn.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            self._touch_start = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_start and self.collide_point(*touch.pos):
            self._touch_start = None
            self.on_open(self.email_data["id"])
            return True
        self._touch_start = None
        return super().on_touch_up(touch)


class Separator(Widget):
    """分割线"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas.before:
            Color(*IOS_GRAY2)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = (self.width, 1)


class TabButton(BoxLayout):
    """底部导航按钮，上层emoji图标+下层文字，带选中指示条"""
    def __init__(self, emoji_text, label_text, on_release, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(1)
        self.padding = [dp(0), dp(4), dp(0), dp(4)]
        self._on_release = on_release
        self._touch_down = False

        self.emoji_label = Label(
            text=emoji_text, font_size=sp(20), bold=True,
            halign="center", valign="center", size_hint_y=0.6,
            color=IOS_DARK,
        )

        self.text_label = Label(
            text=label_text, font_size=sp(11), bold=True,
            halign="center", valign="center", size_hint_y=0.4,
            color=IOS_SECONDARY,
        )

        self.add_widget(self.emoji_label)
        self.add_widget(self.text_label)

        with self.canvas.after:
            self._indicator_color = Color(0, 0, 0, 0)
            self._indicator = Rectangle(pos=self.pos, size=(self.width, dp(3)))
        self.bind(pos=self._update_indicator, size=self._update_indicator)

    def _update_indicator(self, *args):
        self._indicator.pos = (self.x, self.y)
        self._indicator.size = (self.width, dp(3))

    def set_active(self, active):
        if active:
            self._indicator_color.rgba = IOS_BLUE
            self.text_label.color = IOS_BLUE
        else:
            self._indicator_color.rgba = (0, 0, 0, 0)
            self.text_label.color = IOS_SECONDARY

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_down = True
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_down and self.collide_point(*touch.pos):
            self._touch_down = False
            if self._on_release:
                self._on_release(self)
            return True
        self._touch_down = False
        return super().on_touch_up(touch)


class MessageItem(BoxLayout):
    """邮件列表项"""
    def __init__(self, msg, on_open, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(76)
        self.padding = [dp(14), dp(10), dp(16), dp(10)]
        self.spacing = dp(12)
        self.msg = msg
        self.on_open = on_open
        self._touch = False

        with self.canvas.before:
            Color(*WHITE)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        is_unread = not msg.get("seen", False)
        sender = get_sender(msg)

        # 左边：邮箱服务商图标
        icon_color, icon_text = get_email_provider(sender)
        icon_box = BoxLayout(size_hint=(None, None), size=(dp(40), dp(40)))
        with icon_box.canvas.before:
            Color(*icon_color)
            self._icon_bg = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=self._update_icon, size=self._update_icon)
        icon_label = Label(
            text=icon_text, color=WHITE, font_size=sp(12), bold=True,
            halign="center", valign="center",
        )
        icon_box.add_widget(icon_label)

        # 右边：邮件内容
        content = BoxLayout(orientation="vertical", spacing=dp(3))
        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
        from_label = Label(
            text=sender, color=IOS_DARK if is_unread else IOS_SECONDARY,
            font_size=sp(14), bold=is_unread,
            halign="left", valign="center",
        )
        from_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0] * 0.65, None)))
        date_label = Label(
            text=format_date(msg.get("createdAt", "")),
            color=IOS_SECONDARY, font_size=sp(12),
            halign="right", valign="center", size_hint_x=0.35,
        )
        row1.add_widget(from_label)
        row1.add_widget(date_label)

        subject_label = Label(
            text=msg.get("subject", "(无主题)"),
            color=IOS_LABEL if is_unread else IOS_SECONDARY,
            font_size=sp(13), halign="left", valign="center",
        )
        subject_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))

        content.add_widget(row1)
        content.add_widget(subject_label)

        self.add_widget(icon_box)
        self.add_widget(content)

    def _update_icon(self, *args):
        self._icon_bg.pos = args[0].pos
        self._icon_bg.size = args[0].size

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch = True
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch and self.collide_point(*touch.pos):
            self._touch = False
            self.on_open(self.msg)
            return True
        self._touch = False
        return super().on_touch_up(touch)


# ─────────────────────── 主应用 ───────────────────────

class TempMailApp(App):
    def build(self):
        self.icon = "icon.png"
        self.store = EmailStore()
        self.emails = self.store.load()
        self.current_email_id = None
        self.current_email = None
        self.current_messages = []
        self.view = "list"
        self._refresh_event = None
        self.current_tab = "email"
        self.remote_config = dict(REMOTE_CONFIG_DEFAULT)
        self._main_initialized = False
        self._remote_poll_event = None

        self.root = BoxLayout(orientation="vertical")
        self._show_loading()

        # 拉取远程控制配置
        url = APP_CONFIG.get("remote_config_url", "")
        if url:
            api_fetch_remote_config(url, self._on_remote_config_loaded)
        else:
            Clock.schedule_once(lambda dt: self._start_main_app(), 0.3)

        Clock.schedule_interval(self._tick, 1.0)
        return self.root

    # ─────────────────────── 远程控制 ───────────────────────

    def _on_remote_config_loaded(self, success, result):
        if success:
            self.remote_config = result
        self._process_remote_config()

    def _process_remote_config(self):
        cfg = self.remote_config
        if str(cfg.get("enabled", "是")).strip() == "否":
            self._show_disabled(cfg.get("disabled_message", "应用已停用，请联系开发者"))
            return
        if str(cfg.get("maintenance", "否")).strip() == "是":
            self._show_maintenance(cfg.get("maintenance_message", "系统维护中，请稍后再试"))
            return
        self._start_main_app()
        notice = cfg.get("notice", "")
        if notice:
            Clock.schedule_once(lambda dt: self._show_notice(notice), 0.5)
        latest = cfg.get("latest_version", "")
        if latest and self._version_newer(latest, APP_CONFIG.get("app_version", "1.0.0")):
            Clock.schedule_once(lambda dt: self._show_update_prompt(cfg), 1.0)

    def _version_newer(self, latest, current):
        try:
            l = [int(x) for x in latest.split(".")]
            c = [int(x) for x in current.split(".")]
            return l > c
        except:
            return False

    def _show_loading(self):
        self.root.clear_widgets()
        layout = BoxLayout(orientation="vertical", spacing=dp(16))
        label = Label(text="正在加载...", color=IOS_DARK, font_size=sp(18))
        layout.add_widget(label)
        self.root.add_widget(layout)

    def _show_disabled(self, message):
        self.root.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(20))
        title = Label(text="应用已停用", color=IOS_RED, font_size=sp(28), bold=True)
        msg = Label(text=message, color=IOS_LABEL, font_size=sp(16), halign="center")
        msg.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        layout.add_widget(title)
        layout.add_widget(msg)
        self.root.add_widget(layout)

    def _show_maintenance(self, message):
        self.root.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(20))
        title = Label(text="系统维护中", color=IOS_ORANGE, font_size=sp(28), bold=True)
        msg = Label(text=message, color=IOS_LABEL, font_size=sp(16), halign="center")
        msg.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        layout.add_widget(title)
        layout.add_widget(msg)
        self.root.add_widget(layout)

    def _start_main_app(self):
        self._main_initialized = True
        self.root.clear_widgets()
        self.content_area = BoxLayout(orientation="vertical")
        self.root.add_widget(self.content_area)
        self._build_tab_bar()
        self._switch_tab("email")
        self._start_remote_polling()

    def _start_remote_polling(self):
        self._stop_remote_polling()
        url = APP_CONFIG.get("remote_config_url", "")
        if not url:
            return
        self._remote_poll_event = Clock.schedule_interval(lambda dt: self._poll_remote_config(), 10)

    def _stop_remote_polling(self):
        if hasattr(self, '_remote_poll_event') and self._remote_poll_event:
            self._remote_poll_event.cancel()
            self._remote_poll_event = None

    def _poll_remote_config(self):
        url = APP_CONFIG.get("remote_config_url", "")
        if not url:
            return

        def on_result(success, result):
            if not success:
                return
            self.remote_config = result
            enabled = str(result.get("enabled", "是")).strip()
            maintenance = str(result.get("maintenance", "否")).strip()

            if enabled == "否":
                if self.view != "disabled":
                    self.view = "disabled"
                    self._show_disabled(result.get("disabled_message", "应用已停用，请联系开发者"))
                return

            if maintenance == "是":
                if self.view != "maintenance":
                    self.view = "maintenance"
                    self._show_maintenance(result.get("maintenance_message", "系统维护中，请稍后再试"))
                return

            if self.view in ("disabled", "maintenance"):
                self.view = "list"
                self._start_main_app()

        api_fetch_remote_config(url, on_result)

    def _show_notice(self, notice):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
        msg = Label(text=notice, color=IOS_DARK, font_size=sp(15), halign="center")
        msg.bind(size=lambda i, v: setattr(i, "text_size", (v[0] - dp(20), None)))
        btn = RoundedButton(text="知道了", font_size=sp(15), size_hint_y=None, height=dp(44))
        content.add_widget(msg)
        content.add_widget(btn)
        popup = Popup(title="公告", content=content, size_hint=(0.85, None), height=dp(220),
                      background="", background_color=WHITE, title_color=IOS_DARK, title_size=sp(17),
                      separator_color=IOS_GRAY2, auto_dismiss=False)
        btn.bind(on_release=lambda x: popup.dismiss())
        popup.open()

    def _show_update_prompt(self, cfg):
        latest = cfg.get("latest_version", "")
        message = cfg.get("update_message", f"发现新版本 v{latest}")
        update_url = cfg.get("update_url", "")
        force = str(cfg.get("force_update", "否")).strip() == "是"

        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
        title = Label(text=f"发现新版本 v{latest}", color=IOS_BLUE, font_size=sp(18), bold=True)
        msg = Label(text=message, color=IOS_DARK, font_size=sp(14), halign="center")
        msg.bind(size=lambda i, v: setattr(i, "text_size", (v[0] - dp(20), None)))
        content.add_widget(title)
        content.add_widget(msg)

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        if not force:
            later = RoundedButton(text="稍后", bg_color=IOS_GRAY2, text_color=IOS_DARK, font_size=sp(15))
            btns.add_widget(later)
        update_btn = RoundedButton(text="立即更新", font_size=sp(15), bold=True)
        btns.add_widget(update_btn)
        content.add_widget(btns)

        popup = Popup(title="", content=content, size_hint=(0.85, None), height=dp(240),
                      background="", background_color=WHITE, separator_color=(0, 0, 0, 0),
                      auto_dismiss=not force)
        if not force:
            later.bind(on_release=lambda x: popup.dismiss())
        update_btn.bind(on_release=lambda x: self._open_update_url(update_url, popup))
        popup.open()

    def _open_update_url(self, url, popup):
        if url:
            import webbrowser
            webbrowser.open(url)
        popup.dismiss()

    # ─────────────────────── 底部导航栏 ───────────────────────

    def _build_tab_bar(self):
        self.tab_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[dp(0), dp(6), dp(0), dp(4)],
        )
        with self.tab_bar.canvas.before:
            Color(*WHITE)
            self._tab_bg = RoundedRectangle(pos=self.tab_bar.pos, size=self.tab_bar.size)
        self.tab_bar.bind(pos=self._update_tab_bg, size=self._update_tab_bg)

        self.tab_buttons = {}
        tabs = [("email", "✉", "邮箱")]
        if APP_CONFIG.get("enable_phone_tab", True):
            tabs.append(("phone", "☎", "号码"))
        tabs.append(("me", "☺", "我的"))
        for key, emoji, label in tabs:
            btn = TabButton(
                emoji_text=emoji,
                label_text=label,
                on_release=lambda x, k=key: self._switch_tab(k),
            )
            self.tab_buttons[key] = btn
            self.tab_bar.add_widget(btn)
        self.root.add_widget(self.tab_bar)

    def _update_tab_bg(self, *args):
        self._tab_bg.pos = args[0].pos
        self._tab_bg.size = args[0].size

    def _switch_tab(self, tab):
        self.current_tab = tab
        for key, btn in self.tab_buttons.items():
            btn.set_active(key == tab)
        self.content_area.clear_widgets()
        if self._refresh_event:
            self._refresh_event.cancel()
            self._refresh_event = None
        if tab == "email":
            self._build_email_list_view()
        elif tab == "phone":
            self._build_phone_view()
        elif tab == "me":
            self._build_me_view()

    # ─────────────────────── 号码页面 ───────────────────────

    def _build_phone_view(self):
        self.content_area.clear_widgets()

        # 顶部导航
        nav = BoxLayout(size_hint_y=None, height=dp(96), padding=[dp(20), dp(40), dp(20), dp(10)])
        with nav.canvas.before:
            Color(*WHITE)
            bg = RoundedRectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                 size=lambda i, v: setattr(bg, 'size', v))
        title = Label(text="临时号码", color=IOS_DARK, font_size=sp(28), bold=True,
                      halign="left", valign="center")
        title.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        nav.add_widget(title)

        # 提示
        tip = Label(
            text="公开免费接码号码，所有人可见短信，请勿用于重要账号",
            color=IOS_SECONDARY, font_size=sp(12),
            size_hint_y=None, height=dp(36), halign="center",
        )
        tip.bind(size=lambda i, v: setattr(i, "text_size", (v[0] - dp(32), None)))

        # 号码列表
        phone_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10),
                                     padding=[dp(16), dp(8), dp(16), dp(8)])
        phone_container.bind(minimum_height=phone_container.setter("height"))

        # 从配置文件读取号码列表
        phones = APP_CONFIG["phone_numbers"]
        for item in phones:
            country = item["country"]
            number = item["number"]
            card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(76),
                              padding=[dp(18), dp(14), dp(18), dp(14)])
            with card.canvas.before:
                Color(0, 0, 0, 0.05)
                card_shadow = RoundedRectangle(
                    pos=(card.x + dp(2), card.y - dp(2)),
                    size=(card.width - dp(4), card.height),
                    radius=[dp(14)]
                )
                Color(*WHITE)
                card_bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
            card.bind(pos=lambda i, v: (setattr(card_bg, 'pos', v), setattr(card_bg, 'size', v),
                                          setattr(card_shadow, 'pos', (i.x + dp(2), i.y - dp(2))),
                                          setattr(card_shadow, 'size', (i.width - dp(4), i.height))),
                      size=lambda i, v: (setattr(card_bg, 'pos', i.pos), setattr(card_bg, 'size', v),
                                          setattr(card_shadow, 'pos', (i.x + dp(2), i.y - dp(2))),
                                          setattr(card_shadow, 'size', (i.width - dp(4), i.height))))

            info = BoxLayout(orientation="vertical", spacing=dp(2))
            country_label = Label(text=country, color=IOS_SECONDARY, font_size=sp(12),
                                  halign="left", valign="center", size_hint_y=None, height=dp(16))
            country_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
            num_label = Label(text=number, color=IOS_DARK, font_size=sp(17), bold=True,
                              halign="left", valign="center")
            num_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
            info.add_widget(country_label)
            info.add_widget(num_label)

            copy_btn = Button(
                text="复制", size_hint=(None, None), size=(dp(56), dp(32)),
                background_normal="", background_color=(0, 0, 0, 0),
                color=IOS_BLUE, font_size=sp(13), bold=True,
            )
            with copy_btn.canvas.before:
                Color(0, 0.478, 1, 0.1)
                btn_bg = RoundedRectangle(pos=copy_btn.pos, size=copy_btn.size, radius=[dp(10)])
            copy_btn.bind(pos=lambda i, v: setattr(btn_bg, 'pos', v),
                          size=lambda i, v: setattr(btn_bg, 'size', v))
            copy_btn.bind(on_release=lambda x, n=number: self._copy_text(n))

            card.add_widget(info)
            card.add_widget(copy_btn)
            phone_container.add_widget(card)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll.add_widget(phone_container)

        self.content_area.add_widget(nav)
        self.content_area.add_widget(tip)
        self.content_area.add_widget(scroll)

    def _copy_text(self, text):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self._show_toast("已复制到剪贴板")
        except:
            self._show_toast("复制失败")

    # ─────────────────────── 我的页面 ───────────────────────

    def _build_me_view(self):
        self.content_area.clear_widgets()

        # 顶部
        nav = BoxLayout(size_hint_y=None, height=dp(96), padding=[dp(20), dp(40), dp(20), dp(10)])
        with nav.canvas.before:
            Color(*WHITE)
            bg = RoundedRectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                 size=lambda i, v: setattr(bg, 'size', v))
        title = Label(text="我的", color=IOS_DARK, font_size=sp(28), bold=True,
                      halign="left", valign="center")
        title.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        nav.add_widget(title)

        # 用户卡片
        user_card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(100),
                              padding=[dp(20), dp(16), dp(20), dp(16)], spacing=dp(6))
        with user_card.canvas.before:
            Color(*WHITE)
            uc_bg = RoundedRectangle(pos=user_card.pos, size=user_card.size, radius=[dp(14)])
        user_card.bind(pos=lambda i, v: setattr(uc_bg, 'pos', v),
                        size=lambda i, v: setattr(uc_bg, 'size', v))

        app_name = Label(text=APP_CONFIG["app_name"], color=IOS_DARK, font_size=sp(20), bold=True,
                         halign="left", valign="center")
        app_name.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        version = Label(text="版本 1.0.0", color=IOS_SECONDARY, font_size=sp(13),
                        halign="left", valign="center")
        version.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        user_card.add_widget(app_name)
        user_card.add_widget(version)

        # 统计卡片
        email_count = len(self.emails)
        total_msgs = sum(e.get("unread", 0) for e in self.emails)
        stats_card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(80),
                               padding=[dp(16), dp(12), dp(16), dp(12)])
        with stats_card.canvas.before:
            Color(*WHITE)
            sc_bg = RoundedRectangle(pos=stats_card.pos, size=stats_card.size, radius=[dp(14)])
        stats_card.bind(pos=lambda i, v: setattr(sc_bg, 'pos', v),
                         size=lambda i, v: setattr(sc_bg, 'size', v))

        stat1 = BoxLayout(orientation="vertical")
        stat1.add_widget(Label(text=str(email_count), color=IOS_BLUE, font_size=sp(24), bold=True))
        stat1.add_widget(Label(text="邮箱数量", color=IOS_SECONDARY, font_size=sp(12)))
        stat2 = BoxLayout(orientation="vertical")
        stat2.add_widget(Label(text=str(total_msgs), color=IOS_GREEN, font_size=sp(24), bold=True))
        stat2.add_widget(Label(text="未读邮件", color=IOS_SECONDARY, font_size=sp(12)))
        stats_card.add_widget(stat1)
        stats_card.add_widget(stat2)

        # 设置列表
        settings = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(1),
                             padding=[dp(16), dp(0), dp(16), dp(0)])
        with settings.canvas.before:
            Color(*WHITE)
        settings_items = [
            ("邮箱有效期", f"{APP_CONFIG['email_lifetime_seconds'] / 3600:.1f}小时"),
            ("自动刷新", f"{APP_CONFIG['auto_refresh_seconds']}秒"),
            ("主题色", APP_CONFIG["theme_color"]),
            ("数据存储", "本地保存"),
            ("关于", f"{APP_CONFIG['app_name']} v1.0"),
        ]
        for label, value in settings_items:
            item = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52),
                             padding=[dp(16), dp(0), dp(16), dp(0)])
            with item.canvas.before:
                Color(*WHITE)
                item_bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(0)])
            item.bind(pos=lambda i, v: setattr(item_bg, 'pos', v),
                      size=lambda i, v: setattr(item_bg, 'size', v))
            l = Label(text=label, color=IOS_DARK, font_size=sp(15), halign="left", valign="center")
            l.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
            r = Label(text=value, color=IOS_SECONDARY, font_size=sp(14), halign="right", valign="center")
            item.add_widget(l)
            item.add_widget(r)
            settings.add_widget(item)

        # 清除数据按钮
        clear_btn = RoundedButton(text="清除所有数据", bg_color=IOS_RED, font_size=sp(15), bold=True,
                                   size_hint=(0.9, None), height=dp(48), pos_hint={"center_x": 0.5})
        clear_btn.bind(on_release=self._clear_all_data)

        # 底部留白
        spacer = Widget(size_hint_y=None, height=dp(20))

        scroll_content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12),
                                    padding=[dp(0), dp(12), dp(0), dp(12)])
        scroll_content.bind(minimum_height=scroll_content.setter("height"))
        scroll_content.add_widget(user_card)
        scroll_content.add_widget(stats_card)
        scroll_content.add_widget(settings)
        scroll_content.add_widget(spacer)
        scroll_content.add_widget(clear_btn)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll.add_widget(scroll_content)

        self.content_area.add_widget(nav)
        self.content_area.add_widget(scroll)

    def _clear_all_data(self, instance):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
        msg = Label(text="确定要清除所有邮箱数据吗？\n此操作不可恢复。",
                    color=IOS_DARK, font_size=sp(15), halign="center")
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        cancel = RoundedButton(text="取消", bg_color=IOS_GRAY2, text_color=IOS_DARK, font_size=sp(15))
        confirm = RoundedButton(text="清除", bg_color=IOS_RED, font_size=sp(15), bold=True)
        btns.add_widget(cancel)
        btns.add_widget(confirm)
        content.add_widget(msg)
        content.add_widget(btns)
        popup = Popup(title="", content=content, size_hint=(0.8, None), height=dp(180),
                      background="", background_color=WHITE, separator_color=(0, 0, 0, 0))
        cancel.bind(on_release=lambda x: popup.dismiss())
        confirm.bind(on_release=lambda x: self._do_clear(popup))
        popup.open()

    def _do_clear(self, popup):
        popup.dismiss()
        self.emails = []
        self._save_emails()
        self._show_toast("数据已清除")
        self._build_me_view()

    def _save_emails(self):
        self.store.save(self.emails)

    def _tick(self, dt):
        if not getattr(self, '_main_initialized', False):
            return
        if self.view in ("disabled", "maintenance"):
            return
        now = time.time()
        changed = False
        for e in self.emails:
            remaining = e["expires_at"] - now
            if remaining <= 0 and not e.get("expired", False):
                e["expired"] = True
                changed = True
        if changed:
            self._save_emails()
        if self.view == "list":
            self._update_list_times()
        elif self.view == "inbox":
            self._update_inbox_timer()

    # ─────────────────────── 邮箱列表视图 ───────────────────────

    def _build_email_list_view(self):
        self.view = "list"
        if self._refresh_event:
            self._refresh_event.cancel()
            self._refresh_event = None
        self.content_area.clear_widgets()

        nav = BoxLayout(size_hint_y=None, height=dp(96), padding=[dp(20), dp(40), dp(20), dp(10)])
        with nav.canvas.before:
            Color(*WHITE)
            self._nav_bg = RoundedRectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=self._update_nav_bg, size=self._update_nav_bg)
        title = Label(
            text=APP_CONFIG["app_name"], color=IOS_DARK, font_size=sp(28), bold=True,
            halign="left", valign="center",
        )
        title.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        nav.add_widget(title)

        self.list_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.list_container.bind(minimum_height=self.list_container.setter("height"))
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.scroll.add_widget(self.list_container)

        bottom = BoxLayout(size_hint_y=None, height=dp(100), padding=[dp(20), dp(10), dp(20), dp(30)])
        with bottom.canvas.before:
            Color(*WHITE)
            self._bottom_bg = RoundedRectangle(pos=bottom.pos, size=bottom.size)
        bottom.bind(pos=self._update_bottom_bg, size=self._update_bottom_bg)
        self.create_btn = RoundedButton(text="+  创建新邮箱", font_size=sp(17), bold=True)
        self.create_btn.bind(on_release=self._create_email)
        bottom.add_widget(self.create_btn)

        self.content_area.add_widget(nav)
        self.content_area.add_widget(self.scroll)
        self.content_area.add_widget(bottom)
        self._refresh_list()

    def _update_nav_bg(self, *args):
        self._nav_bg.pos = args[0].pos
        self._nav_bg.size = args[0].size

    def _update_bottom_bg(self, *args):
        self._bottom_bg.pos = args[0].pos
        self._bottom_bg.size = args[0].size

    def _refresh_list(self):
        self.list_container.clear_widgets()
        if not self.emails:
            empty = Label(
                text="还没有邮箱\n点击下方按钮创建",
                color=IOS_SECONDARY, font_size=sp(15),
                size_hint_y=None, height=dp(200), halign="center",
            )
            self.list_container.add_widget(empty)
            return
        now = time.time()
        for e in self.emails:
            remaining = e["expires_at"] - now
            card = EmailCard(
                email_data=e, on_open=self._open_inbox, on_delete=self._delete_email,
            )
            card.update_time(remaining)
            card.update_unread(e.get("unread", 0))
            self.list_container.add_widget(card)

    def _update_list_times(self):
        if not hasattr(self, 'list_container'):
            return
        now = time.time()
        for child in self.list_container.children:
            if isinstance(child, EmailCard):
                remaining = child.email_data["expires_at"] - now
                child.update_time(remaining)

    # ── 创建邮箱 ──
    def _create_email(self, instance):
        if hasattr(self, 'create_btn') and self.create_btn.disabled:
            return
        if hasattr(self, 'create_btn'):
            self.create_btn.disabled = True
            self.create_btn.text = "创建中..."
        self._loading_popup = Popup(
            title="", content=Label(text="正在创建邮箱...", color=IOS_DARK, font_size=sp(16)),
            size_hint=(0.6, None), height=dp(120),
            background="", background_color=WHITE,
            separator_color=(0, 0, 0, 0), auto_dismiss=False,
        )
        self._loading_popup.open()
        api_create_email(self._on_email_created)

    def _on_email_created(self, success, result):
        if hasattr(self, '_loading_popup'):
            self._loading_popup.dismiss()
        self._start_create_cooldown()
        if not success:
            self._show_error("创建失败", f"无法创建邮箱：{result}")
            return
        email_data = {
            "id": str(int(time.time() * 1000)),
            "address": result["address"],
            "domain": result["domain"],
            "password": result["password"],
            "token": result["token"],
            "created_at": time.time(),
            "expires_at": time.time() + EMAIL_LIFETIME,
            "expired": False,
            "unread": 0,
            "messages": [],
        }
        self.emails.insert(0, email_data)
        self._save_emails()
        self._refresh_list()

    def _start_create_cooldown(self):
        if not hasattr(self, 'create_btn'):
            return
        self._cooldown_remaining = 5
        self.create_btn.disabled = True
        self.create_btn.text = f"请等待 {self._cooldown_remaining} 秒"

        def tick(dt):
            self._cooldown_remaining -= 1
            if self._cooldown_remaining <= 0:
                self.create_btn.disabled = False
                self.create_btn.text = "+  创建新邮箱"
                return False
            self.create_btn.text = f"请等待 {self._cooldown_remaining} 秒"
            return True

        Clock.schedule_interval(tick, 1)

    # ── 删除邮箱 ──
    def _delete_email(self, email_id):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
        msg = Label(text="确定要删除这个邮箱吗？", color=IOS_DARK, font_size=sp(16), halign="center")
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        cancel = RoundedButton(text="取消", bg_color=IOS_GRAY2, text_color=IOS_DARK, font_size=sp(15))
        confirm = RoundedButton(text="删除", bg_color=IOS_RED, font_size=sp(15), bold=True)
        btns.add_widget(cancel)
        btns.add_widget(confirm)
        content.add_widget(msg)
        content.add_widget(btns)
        popup = Popup(
            title="", content=content,
            size_hint=(0.8, None), height=dp(160),
            background="", background_color=WHITE,
            separator_color=(0, 0, 0, 0),
        )
        cancel.bind(on_release=lambda x: popup.dismiss())
        confirm.bind(on_release=lambda x: self._do_delete(email_id, popup))
        popup.open()

    def _do_delete(self, email_id, popup):
        popup.dismiss()
        self.emails = [e for e in self.emails if e["id"] != email_id]
        self._save_emails()
        self._refresh_list()

    # ─────────────────────── 收件箱视图 ───────────────────────

    def _open_inbox(self, email_id):
        email = next((e for e in self.emails if e["id"] == email_id), None)
        if not email:
            return
        if email.get("expired", False) or email["expires_at"] <= time.time():
            self._show_error("邮箱已过期", "该邮箱已超过1小时有效期，请创建新邮箱。")
            return

        self.current_email_id = email_id
        self.current_email = email
        self.view = "inbox"
        self.content_area.clear_widgets()

        nav = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120),
                        padding=[dp(16), dp(40), dp(16), dp(10)], spacing=dp(6))
        with nav.canvas.before:
            Color(*WHITE)
            self._inav_bg = RoundedRectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=self._update_inav_bg, size=self._update_inav_bg)

        top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        back_btn = Button(
            text="< 返回", size_hint=(None, None), size=(dp(70), dp(36)),
            background_normal="", background_color=(0, 0, 0, 0),
            color=IOS_BLUE, font_size=sp(16),
        )
        back_btn.bind(on_release=lambda x: self._back_to_list())
        self.addr_title = Label(
            text=email["address"], color=IOS_DARK, font_size=sp(15), bold=True,
            halign="center", valign="center",
        )
        copy_btn = Button(
            text="复制", size_hint=(None, None), size=(dp(50), dp(36)),
            background_normal="", background_color=(0, 0, 0, 0),
            color=IOS_BLUE, font_size=sp(14),
        )
        copy_btn.bind(on_release=lambda x: self._copy_address(email["address"]))
        top_row.add_widget(back_btn)
        top_row.add_widget(self.addr_title)
        top_row.add_widget(copy_btn)

        info_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
        self.inbox_timer = Label(
            text="", color=IOS_SECONDARY, font_size=sp(13),
            halign="left", valign="center",
        )
        self.inbox_timer.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        refresh_btn = Button(
            text="刷新", size_hint=(None, None), size=(dp(50), dp(28)),
            background_normal="", background_color=(0, 0, 0, 0),
            color=IOS_BLUE, font_size=sp(13),
        )
        refresh_btn.bind(on_release=lambda x: self._refresh_inbox())
        info_row.add_widget(self.inbox_timer)
        info_row.add_widget(refresh_btn)

        nav.add_widget(top_row)
        nav.add_widget(info_row)

        self.msg_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.msg_container.bind(minimum_height=self.msg_container.setter("height"))
        self.msg_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.msg_scroll.add_widget(self.msg_container)

        self.content_area.add_widget(nav)
        self.content_area.add_widget(self.msg_scroll)

        self._update_inbox_timer()
        self._refresh_inbox()

        if self._refresh_event:
            self._refresh_event.cancel()
        self._refresh_event = Clock.schedule_interval(lambda dt: self._refresh_inbox(silent=True), APP_CONFIG["auto_refresh_seconds"])

    def _update_inav_bg(self, *args):
        self._inav_bg.pos = args[0].pos
        self._inav_bg.size = args[0].size

    def _update_inbox_timer(self):
        if not hasattr(self, 'inbox_timer') or not self.current_email:
            return
        remaining = self.current_email["expires_at"] - time.time()
        self.inbox_timer.text = f"有效期剩余: {format_time_remaining(remaining)}"
        if remaining <= 0:
            self.inbox_timer.color = IOS_RED
        elif remaining < 300:
            self.inbox_timer.color = IOS_ORANGE
        else:
            self.inbox_timer.color = IOS_SECONDARY

    def _copy_address(self, address):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(address)
            self._show_toast("已复制到剪贴板")
        except:
            self._show_toast("复制失败，请手动复制")

    def _show_toast(self, text):
        popup = Popup(
            title="", content=Label(text=text, color=WHITE, font_size=sp(14)),
            size_hint=(0.5, None), height=dp(50),
            background="", background_color=(0, 0, 0, 0.7),
            separator_color=(0, 0, 0, 0), auto_dismiss=True,
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def _refresh_inbox(self, silent=False):
        email = self.current_email
        if not email or email.get("expired", False):
            return

        # 先自动登录刷新 token，确保有效
        def on_logged_in(success, token_or_err):
            if not success:
                if not silent:
                    self._show_error("登录失败", str(token_or_err))
                return
            email["token"] = token_or_err
            self._save_emails()

            def on_result(success2, messages):
                if not success2:
                    if not silent:
                        self._show_error("刷新失败", str(messages))
                    return
                self.current_messages = messages
                unread = sum(1 for m in messages if not m.get("seen", False))
                email["unread"] = unread
                self._save_emails()
                self._render_messages()

            api_check_inbox(token_or_err, on_result)

        api_login(email["address"], email["password"], on_logged_in)

    def _render_messages(self):
        self.msg_container.clear_widgets()
        if not self.current_messages:
            empty = Label(
                text="收件箱为空\n等待接收邮件...",
                color=IOS_SECONDARY, font_size=sp(15),
                size_hint_y=None, height=dp(200), halign="center",
            )
            self.msg_container.add_widget(empty)
            return
        for msg in self.current_messages:
            item = MessageItem(msg=msg, on_open=self._open_message)
            self.msg_container.add_widget(item)

    def _back_to_list(self):
        if self._refresh_event:
            self._refresh_event.cancel()
            self._refresh_event = None
        self._build_email_list_view()

    # ─────────────────────── 邮件详情视图 ───────────────────────

    def _open_message(self, msg):
        self.view = "detail"
        email = self.current_email
        msg_id = msg["id"]

        # 标记已读
        if not msg.get("seen", False):
            msg["seen"] = True
            if email["unread"] > 0:
                email["unread"] -= 1
            self._save_emails()

        self.content_area.clear_widgets()

        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(80),
                        padding=[dp(16), dp(40), dp(16), dp(10)])
        with nav.canvas.before:
            Color(*WHITE)
            self._dnav_bg = RoundedRectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda i, v: setattr(self._dnav_bg, 'pos', v),
                 size=lambda i, v: setattr(self._dnav_bg, 'size', v))
        back_btn = Button(
            text="< 收件箱", size_hint=(None, None), size=(dp(90), dp(36)),
            background_normal="", background_color=(0, 0, 0, 0),
            color=IOS_BLUE, font_size=sp(16),
        )
        back_btn.bind(on_release=lambda x: self._back_to_inbox())
        title = Label(text="邮件详情", color=IOS_DARK, font_size=sp(17), bold=True, halign="center")
        spacer = Widget(size_hint_x=0.25)
        nav.add_widget(back_btn)
        nav.add_widget(title)
        nav.add_widget(spacer)

        self.detail_content = BoxLayout(orientation="vertical", size_hint_y=None,
                                         padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))
        self.detail_content.bind(minimum_height=self.detail_content.setter("height"))
        self.detail_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.detail_scroll.add_widget(self.detail_content)

        loading = Label(text="加载中...", color=IOS_SECONDARY, font_size=sp(15),
                        size_hint_y=None, height=dp(100))
        self.detail_content.add_widget(loading)

        self.content_area.add_widget(nav)
        self.content_area.add_widget(self.detail_scroll)

        # 先自动登录刷新 token，再读取邮件
        def on_logged_in(success, token_or_err):
            if not success:
                self.detail_content.clear_widgets()
                err = Label(text=f"加载失败: {token_or_err}", color=IOS_RED,
                            font_size=sp(14), size_hint_y=None, height=dp(100), halign="center")
                self.detail_content.add_widget(err)
                return
            email["token"] = token_or_err
            self._save_emails()
            api_read_message(token_or_err, msg_id, self._on_message_loaded)

        api_login(email["address"], email["password"], on_logged_in)

    def _on_message_loaded(self, success, msg):
        self.detail_content.clear_widgets()
        if not success:
            err = Label(text=f"加载失败: {msg}", color=IOS_RED, font_size=sp(14),
                        size_hint_y=None, height=dp(100), halign="center")
            self.detail_content.add_widget(err)
            return

        subject = Label(
            text=msg.get("subject", "(无主题)"),
            color=IOS_DARK, font_size=sp(20), bold=True,
            size_hint_y=None, halign="left",
        )
        subject.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)),
                      texture_size=lambda i, v: setattr(i, "height", v[1] + dp(8)))
        self.detail_content.add_widget(subject)

        sender = get_sender(msg)
        from_label = Label(
            text=f"来自: {sender}",
            color=IOS_LABEL, font_size=sp(14),
            size_hint_y=None, height=dp(24), halign="left",
        )
        from_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        self.detail_content.add_widget(from_label)

        date_label = Label(
            text=f"时间: {format_date(msg.get("createdAt", ""))}",
            color=IOS_SECONDARY, font_size=sp(13),
            size_hint_y=None, height=dp(20), halign="left",
        )
        date_label.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        self.detail_content.add_widget(date_label)

        sep = Separator()
        self.detail_content.add_widget(sep)

        body_text = msg.get("text", "") or strip_html(msg.get("html", ""))
        if not body_text:
            body_text = "(无正文内容)"

        body = Label(
            text=body_text, color=IOS_DARK, font_size=sp(15),
            size_hint_y=None, halign="left", valign="top", line_height=1.5,
        )
        body.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)),
                   texture_size=lambda i, v: setattr(i, "height", max(v[1] + dp(16), dp(100))))
        self.detail_content.add_widget(body)

        attachments = msg.get("attachments", [])
        if attachments:
            att_label = Label(
                text=f"附件 ({len(attachments)}):",
                color=IOS_LABEL, font_size=sp(14), bold=True,
                size_hint_y=None, height=dp(24), halign="left",
            )
            self.detail_content.add_widget(att_label)
            for att in attachments:
                att_name = att.get("filename", "未知文件")
                att_size = att.get("size", 0)
                att_item = Label(
                    text=f"  {att_name} ({att_size} bytes)",
                    color=IOS_BLUE, font_size=sp(13),
                    size_hint_y=None, height=dp(22), halign="left",
                )
                att_item.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
                self.detail_content.add_widget(att_item)

    def _back_to_inbox(self):
        self.view = "inbox"
        self._open_inbox(self.current_email_id)

    # ── 错误弹窗 ──
    def _show_error(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
        msg = Label(text=message, color=IOS_DARK, font_size=sp(15), halign="center")
        btn = RoundedButton(text="知道了", font_size=sp(15), size_hint_y=None, height=dp(44))
        content.add_widget(msg)
        content.add_widget(btn)
        popup = Popup(
            title=title, content=content,
            size_hint=(0.8, None), height=dp(180),
            background="", background_color=WHITE,
            title_color=IOS_DARK, title_size=sp(17),
            separator_color=IOS_GRAY2,
        )
        btn.bind(on_release=lambda x: popup.dismiss())
        popup.open()


# ─────────────────────── 入口 ───────────────────────

if __name__ == "__main__":
    TempMailApp().run()

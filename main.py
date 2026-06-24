# -*- coding: utf-8 -*-
# ──────────────────────────────────────────────────────────
# stdlib импорты ПЕРВЫМИ — ловим краши до инициализации kivy
# Android 16 (API 36) / One UI 8.0 / Samsung A35 5G ready
# ──────────────────────────────────────────────────────────
import sys
import traceback
import os
import datetime
import threading
import urllib.request
import urllib.error
import csv
import io
import base64
import time



# ══ Crash Log ════════════════════════════════════════════════

def get_crash_log_path():
    """
    Путь для лога без КАКИХ-ЛИБО разрешений.
    Android 16 / SELinux Enforcing / Knox 3.12:
      getExternalFilesDir() — не требует разрешений вообще.
    Файл: /storage/emulated/0/Android/data/org.nevpn/files/NEVPN_crash_log.txt
    Читать: USB MTP  →  Этот ПК / Samsung A35 / Internal / Android/data/org.nevpn/files/
    """
    is_android = (
        os.path.exists("/system/build.prop")
        or os.path.exists("/system/framework")
    )
    if not is_android:
        try:
            from kivy.utils import platform as _p
            is_android = (_p == "android")
        except Exception:
            pass

    if is_android:
        # 1) getExternalFilesDir — никаких разрешений, Android 4.4+
        try:
            from jnius import autoclass
            ctx = autoclass("org.kivy.android.PythonActivity").mActivity
            d = ctx.getExternalFilesDir(None)
            if d is not None:
                path = d.getAbsolutePath()
                os.makedirs(path, exist_ok=True)
                t = os.path.join(path, ".wtest")
                open(t, "w").close()
                os.remove(t)
                return os.path.join(path, "NEVPN_crash_log.txt")
        except Exception:
            pass

        # 2) getCacheDir — всегда доступен
        try:
            from jnius import autoclass
            ctx = autoclass("org.kivy.android.PythonActivity").mActivity
            path = ctx.getCacheDir().getAbsolutePath()
            os.makedirs(path, exist_ok=True)
            return os.path.join(path, "NEVPN_crash_log.txt")
        except Exception:
            pass

        # 3) getFilesDir — внутренняя память
        try:
            from jnius import autoclass
            ctx = autoclass("org.kivy.android.PythonActivity").mActivity
            path = ctx.getFilesDir().getAbsolutePath()
            os.makedirs(path, exist_ok=True)
            return os.path.join(path, "NEVPN_crash_log.txt")
        except Exception:
            pass

        # 4) Жёсткие пути с проверкой записи
        for base in [
            "/storage/emulated/0/Android/data/org.nevpn/files",
            "/data/data/org.nevpn/cache",
            "/data/data/org.nevpn/files",
        ]:
            try:
                os.makedirs(base, exist_ok=True)
                t = os.path.join(base, ".wtest")
                open(t, "w").close()
                os.remove(t)
                return os.path.join(base, "NEVPN_crash_log.txt")
            except Exception:
                continue

        return "/data/local/tmp/NEVPN_crash_log.txt"
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")


def write_crash_log(exc_type, exc_value, exc_tb):
    """Пишет лог — никогда не бросает исключений."""
    try:
        path = get_crash_log_path()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "=" * 60,
            "CRASH  " + now,
            "=" * 60,
            "Platform: " + sys.platform,
            "Python: " + sys.version,
            "",
            "--- Traceback ---",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
            "",
        ]
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass


def handle_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    write_crash_log(exc_type, exc_value, exc_tb)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = handle_exception

_orig_thread_hook = threading.excepthook
def _thread_exception_handler(args):
    if args.exc_type and not issubclass(args.exc_type, SystemExit):
        write_crash_log(args.exc_type, args.exc_value, args.exc_traceback)
    _orig_thread_hook(args)
threading.excepthook = _thread_exception_handler


# ══ Kivy — после crash handler ═══════════════════════════════
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import platform

try:
    if platform != "android":
        Window.size = (360, 640)
except Exception:
    pass



KV = '''
#:import dp kivy.metrics.dp

<NeomorphButton@MDCard>:
    size_hint_y: None
    height: "52dp"
    radius: [26]
    md_bg_color: 0.95, 0.95, 0.98, 1
    elevation: 3
    ripple_behavior: True
    orientation: 'horizontal'
    padding: [16, 0, 16, 0]
    spacing: 12

<ServerListItem>:
    size_hint_y: None
    height: "60dp"
    radius: [16]
    md_bg_color: 0.95, 0.95, 0.98, 1
    elevation: 2
    ripple_behavior: True
    padding: [16, 0]
    on_release: app.root.get_screen('servers').select_server(root.server_name)
    MDBoxLayout:
        spacing: 14
        MDBoxLayout:
            size_hint: None, None
            size: "38dp", "38dp"
            pos_hint: {"center_y": .5}
            AnchorLayout:
                Image:
                    source: root.flag_source
                    size_hint: None, None
                    size: "30dp", "22dp"
                    pos_hint: {"center_x": .5, "center_y": .5}
        MDLabel:
            text: root.server_name
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            valign: "middle"
            size_hint_x: 1
        MDBoxLayout:
            size_hint: None, None
            size: "38dp", "38dp"
            pos_hint: {"center_y": .5}
            AnchorLayout:
                MDIcon:
                    icon: "chevron-right"
                    size_hint: None, None
                    size: "22dp", "22dp"
                    pos_hint: {"center_x": .5, "center_y": .5}
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_size: "20sp"

WindowManager:
    MainScreen:
    SettingsScreen:
    ServersScreen:
    AboutScreen:
    ProtocolScreen:
    SubscriptionScreen:

# ─── MAIN SCREEN ────────────────────────────────────────────────────
<MainScreen>:
    name: 'main'
    selected_server: "Нидерланды"
    is_connected: False
    traffic_up: "0 B"
    traffic_down: "0 B"

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        # ── Top bar ──
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"
            spacing: 0

            Widget:
                size_hint_x: None
                width: "48dp"

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"

                MDCard:
                    adaptive_size: True
                    radius: [14]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    padding: [12, 6, 14, 6]
                    elevation: 1

                    MDBoxLayout:
                        adaptive_size: True
                        spacing: 6
                        orientation: "horizontal"

                        Image:
                            source: 'images/logo_icon.png'
                            size_hint: None, None
                            size: "22dp", "22dp"
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "NEVPN"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                            pos_hint: {"center_y": .5}

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "cog"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.5, 1
                        on_release: root.manager.current = 'settings'

        Widget:
            size_hint_y: None
            height: "18dp"

        # ── Server selector ──
        NeomorphButton:
            on_release: root.manager.current = 'servers'

            MDBoxLayout:
                size_hint: None, None
                size: "36dp", "36dp"
                pos_hint: {"center_y": .5}
                AnchorLayout:
                    MDIcon:
                        icon: "swap-horizontal"
                        size_hint: None, None
                        size: "22dp", "22dp"
                        pos_hint: {"center_x": .5, "center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.35, 0.35, 0.45, 1

            MDLabel:
                text: root.selected_server
                size_hint_x: 1
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
                halign: "left"
                valign: "middle"
                bold: True

            MDBoxLayout:
                size_hint: None, None
                size: "36dp", "36dp"
                pos_hint: {"center_y": .5}
                AnchorLayout:
                    MDIcon:
                        icon: "chevron-right"
                        size_hint: None, None
                        size: "22dp", "22dp"
                        pos_hint: {"center_x": .5, "center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.75, 0.75, 0.75, 1

        Widget:
            size_hint_y: None
            height: "24dp"

        # ── Connect button ──
        AnchorLayout:
            size_hint_y: None
            height: "260dp"

            MDCard:
                id: connect_card
                size_hint: None, None
                size: "240dp", "240dp"
                radius: [60]
                md_bg_color: 0.93, 0.94, 0.98, 1
                elevation: 8
                shadow_color: 0.75, 0.75, 0.85, 0.6

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: 14
                    padding: [0, 24, 0, 20]

                    MDLabel:
                        id: status_label
                        text: app.lang_connect
                        halign: "center"
                        valign: "top"
                        font_style: "H5"
                        theme_text_color: "Custom"
                        text_color: 0.55, 0.55, 0.68, 1
                        bold: True
                        size_hint_y: None
                        height: "40dp"

                    AnchorLayout:
                        MDCard:
                            id: power_button
                            size_hint: None, None
                            size: "100dp", "100dp"
                            radius: [50]
                            md_bg_color: 0.2, 0.4, 0.9, 1
                            elevation: 6
                            ripple_behavior: True
                            on_release: root.on_power_press(self)

                            AnchorLayout:
                                MDIcon:
                                    id: power_icon
                                    icon: "power-plug-outline"
                                    font_size: "46sp"
                                    theme_text_color: "Custom"
                                    text_color: 1, 1, 1, 1
                                    pos_hint: {"center_x": .5, "center_y": .5}

        Widget:
            size_hint_y: None
            height: "20dp"

        # ── Traffic stats ──
        AnchorLayout:
            size_hint_y: None
            height: "44dp"

            MDCard:
                size_hint: None, None
                size: "200dp", "36dp"
                radius: [18]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                padding: [18, 0]

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: 20

                    MDBoxLayout:
                        spacing: 4
                        MDIcon:
                            icon: "arrow-up"
                            size_hint: None, None
                            size: "16dp", "16dp"
                            pos_hint: {"center_y": .5}
                            theme_text_color: "Custom"
                            text_color: 0.3, 0.7, 0.4, 1
                            font_size: "14sp"
                        MDLabel:
                            id: traffic_up_label
                            text: root.traffic_up
                            adaptive_size: True
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.2, 0.2, 0.2, 1
                            pos_hint: {"center_y": .5}

                    MDBoxLayout:
                        spacing: 4
                        MDIcon:
                            icon: "arrow-down"
                            size_hint: None, None
                            size: "16dp", "16dp"
                            pos_hint: {"center_y": .5}
                            theme_text_color: "Custom"
                            text_color: 0.25, 0.5, 0.95, 1
                            font_size: "14sp"
                        MDLabel:
                            id: traffic_down_label
                            text: root.traffic_down
                            adaptive_size: True
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.2, 0.2, 0.2, 1
                            pos_hint: {"center_y": .5}

        Widget:

# ─── SETTINGS SCREEN ────────────────────────────────────────────────
<SettingsScreen>:
    name: 'settings'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        # ── Top bar ──
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "arrow-left"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        on_release: root.manager.current = 'main'

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDCard:
                    adaptive_size: True
                    radius: [14]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    padding: [12, 6, 14, 6]
                    elevation: 1
                    MDBoxLayout:
                        adaptive_size: True
                        spacing: 6
                        Image:
                            source: 'images/logo_icon.png'
                            size_hint: None, None
                            size: "22dp", "22dp"
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "NEVPN"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                            pos_hint: {"center_y": .5}

            Widget:
                size_hint_x: None
                width: "48dp"

        Widget:
            size_hint_y: None
            height: "20dp"

        # ── Title ──
        NeomorphButton:
            ripple_behavior: False
            MDLabel:
                text: "Настройки"
                bold: True
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.1, 0.1, 0.1, 1
                halign: "center"
                valign: "middle"
                size_hint: 1, 1

        Widget:
            size_hint_y: None
            height: "20dp"

        # ── Settings list — статичный, не скроллится, карточки отдельные ──
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "10dp"
            size_hint_y: None
            height: self.minimum_height

            # Язык
            MDCard:
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: app.toggle_language()
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "translate"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.25, 0.45, 0.9, 1
                                font_size: "22sp"
                    MDLabel:
                        id: settings_lang_title
                        text: app.lang_settings
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "44dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDLabel:
                                id: lang_badge
                                text: app.lang_code
                                font_style: "Caption"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0.25, 0.45, 0.9, 1
                                halign: "center"
                                adaptive_size: True
                                pos_hint: {"center_x": .5, "center_y": .5}

            # Протокол
            MDCard:
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: root.manager.current = 'protocol'
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "shield-lock-outline"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.25, 0.45, 0.9, 1
                                font_size: "22sp"
                    MDLabel:
                        text: app.lang_protocol
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "chevron-right"
                                size_hint: None, None
                                size: "22dp", "22dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.7, 0.7, 0.7, 1
                                font_size: "20sp"

            # Автоподключение
            MDCard:
                id: autoconnect_card
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: root.toggle_autoconnect(self)
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                id: autoconnect_icon
                                icon: "wifi-check"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.25, 0.45, 0.9, 1
                                font_size: "22sp"
                    MDLabel:
                        id: autoconnect_label
                        text: "Автоподключение"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "32dp", "32dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                id: autoconnect_check
                                icon: "check-circle-outline"
                                size_hint: None, None
                                size: "22dp", "22dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.75, 0.75, 0.75, 1
                                font_size: "20sp"

            # Kill Switch
            MDCard:
                id: killswitch_card
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: root.toggle_killswitch(self)
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                id: killswitch_icon
                                icon: "close-network-outline"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.9, 0.3, 0.3, 1
                                font_size: "22sp"
                    MDLabel:
                        id: killswitch_label
                        text: "Kill Switch"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "32dp", "32dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                id: killswitch_check
                                icon: "check-circle-outline"
                                size_hint: None, None
                                size: "22dp", "22dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.75, 0.75, 0.75, 1
                                font_size: "20sp"

            # Подписка
            MDCard:
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: root.manager.current = 'subscription'
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "crown-outline"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.85, 0.65, 0.1, 1
                                font_size: "22sp"
                    MDLabel:
                        text: app.lang_subscription
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "chevron-right"
                                size_hint: None, None
                                size: "22dp", "22dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.7, 0.7, 0.7, 1
                                font_size: "20sp"

            # О приложении
            MDCard:
                size_hint_y: None
                height: "60dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                ripple_behavior: True
                padding: [16, 0, 16, 0]
                on_release: root.manager.current = 'about'
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "information-outline"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.25, 0.45, 0.9, 1
                                font_size: "22sp"
                    MDLabel:
                        text: "О приложении"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"
                        size_hint_x: 1
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "chevron-right"
                                size_hint: None, None
                                size: "22dp", "22dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.7, 0.7, 0.7, 1
                                font_size: "20sp"

        Widget:

# ─── SERVERS SCREEN ─────────────────────────────────────────────────
<ServersScreen>:
    name: 'servers'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        MDBoxLayout:
            size_hint_y: None
            height: "48dp"

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "arrow-left"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        on_release: root.manager.current = 'main'

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDCard:
                    adaptive_size: True
                    radius: [14]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    padding: [12, 6, 14, 6]
                    elevation: 1
                    MDBoxLayout:
                        adaptive_size: True
                        spacing: 6
                        Image:
                            source: 'images/logo_icon.png'
                            size_hint: None, None
                            size: "22dp", "22dp"
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "NEVPN"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                            pos_hint: {"center_y": .5}

            Widget:
                size_hint_x: None
                width: "48dp"

        Widget:
            size_hint_y: None
            height: "16dp"

        MDLabel:
            text: "Серверы VPN Gate"
            bold: True
            font_style: "H6"
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            halign: "center"
            size_hint_y: None
            height: "40dp"

        # ── Статус загрузки ──
        AnchorLayout:
            size_hint_y: None
            height: "38dp"
            MDCard:
                adaptive_size: True
                radius: [12]
                md_bg_color: 0.93, 0.95, 1.0, 1
                padding: [14, 6]
                elevation: 1
                MDBoxLayout:
                    spacing: 6
                    adaptive_size: True
                    MDIcon:
                        id: loading_icon
                        icon: "cloud-download-outline"
                        size_hint: None, None
                        size: "18dp", "18dp"
                        pos_hint: {"center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.25, 0.45, 0.9, 1
                        font_size: "16sp"
                    MDLabel:
                        id: loading_label
                        text: "Загрузка серверов..."
                        adaptive_size: True
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.3, 0.3, 0.5, 1
                        pos_hint: {"center_y": .5}

        Widget:
            size_hint_y: None
            height: "8dp"

        # ── Кнопка обновить ──
        AnchorLayout:
            size_hint_y: None
            height: "32dp"
            MDCard:
                adaptive_size: True
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 1
                ripple_behavior: True
                padding: [12, 5]
                on_release: root.refresh_servers()
                MDBoxLayout:
                    spacing: 5
                    adaptive_size: True
                    MDIcon:
                        icon: "refresh"
                        size_hint: None, None
                        size: "16dp", "16dp"
                        pos_hint: {"center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.55, 1
                        font_size: "14sp"
                    MDLabel:
                        text: "Обновить"
                        adaptive_size: True
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.4, 0.4, 0.55, 1
                        pos_hint: {"center_y": .5}

        Widget:
            size_hint_y: None
            height: "10dp"

        # ── Динамический список серверов ──
        ScrollView:
            do_scroll_x: False
            MDBoxLayout:
                id: servers_list
                orientation: 'vertical'
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                padding: [0, 0, 0, 16]

        Widget:

# ─── ABOUT SCREEN ───────────────────────────────────────────────────
<AboutScreen>:
    name: 'about'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        MDBoxLayout:
            size_hint_y: None
            height: "48dp"

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "arrow-left"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        on_release: root.manager.current = 'settings'

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDLabel:
                    text: "О приложении"
                    bold: True
                    halign: "center"
                    font_style: "H6"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.1, 0.1, 1
                    adaptive_size: True

            Widget:
                size_hint_x: None
                width: "48dp"

        Widget:
            size_hint_y: None
            height: "40dp"

        AnchorLayout:
            size_hint_y: None
            height: "100dp"
            MDCard:
                size_hint: None, None
                size: "80dp", "80dp"
                radius: [24]
                md_bg_color: 0.2, 0.4, 0.9, 1
                elevation: 6
                AnchorLayout:
                    Image:
                        source: 'images/logo_icon.png'
                        size_hint: None, None
                        size: "48dp", "48dp"
                        pos_hint: {"center_x": .5, "center_y": .5}

        Widget:
            size_hint_y: None
            height: "20dp"

        MDLabel:
            text: "NEVPN"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: "40dp"

        MDLabel:
            text: "Версия 1.0.0"
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1
            size_hint_y: None
            height: "24dp"

        Widget:
            size_hint_y: None
            height: "30dp"

        MDCard:
            size_hint_y: None
            height: "100dp"
            radius: [16]
            md_bg_color: 0.95, 0.95, 0.98, 1
            elevation: 2
            padding: [20, 12]
            MDLabel:
                text: "Неоморфный VPN-клиент с открытым кодом.\\nРазработано с использованием KivyMD.\\nВсе права защищены © 2025 NEVPN."
                halign: "center"
                valign: "middle"
                theme_text_color: "Custom"
                text_color: 0.4, 0.4, 0.4, 1

        Widget:

# ─── PROTOCOL SCREEN ────────────────────────────────────────────────
<ProtocolScreen>:
    name: 'protocol'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        # Top bar
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "arrow-left"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        on_release: root.manager.current = 'settings'

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDLabel:
                    text: app.lang_protocol
                    bold: True
                    halign: "center"
                    font_style: "H6"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.1, 0.1, 1
                    adaptive_size: True

            Widget:
                size_hint_x: None
                width: "48dp"

        Widget:
            size_hint_y: None
            height: "24dp"

        # Иконка щита
        AnchorLayout:
            size_hint_y: None
            height: "110dp"
            MDCard:
                size_hint: None, None
                size: "88dp", "88dp"
                radius: [28]
                md_bg_color: 0.2, 0.4, 0.9, 1
                elevation: 6
                AnchorLayout:
                    MDIcon:
                        icon: "shield-lock"
                        size_hint: None, None
                        size: "48dp", "48dp"
                        pos_hint: {"center_x": .5, "center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_size: "44sp"

        Widget:
            size_hint_y: None
            height: "10dp"

        MDLabel:
            text: "OpenVPN"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: "40dp"

        MDLabel:
            text: app.lang_protocol_sub
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.55, 0.55, 0.65, 1
            size_hint_y: None
            height: "22dp"

        Widget:
            size_hint_y: None
            height: "20dp"

        # Карточки с фактами
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "10dp"
            size_hint_y: None
            height: self.minimum_height

            MDCard:
                size_hint_y: None
                height: "64dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                padding: [16, 0]
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "lock"
                                size_hint: None, None
                                size: "24dp", "24dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.2, 0.4, 0.9, 1
                                font_size: "22sp"
                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_x: 1
                        spacing: 2
                        MDLabel:
                            text: app.lang_proto_enc
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                        MDLabel:
                            text: "AES-256-GCM"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.5, 0.5, 0.6, 1
                            adaptive_size: True

            MDCard:
                size_hint_y: None
                height: "64dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                padding: [16, 0]
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "key-variant"
                                size_hint: None, None
                                size: "24dp", "24dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.2, 0.4, 0.9, 1
                                font_size: "22sp"
                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_x: 1
                        spacing: 2
                        MDLabel:
                            text: app.lang_proto_auth
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                        MDLabel:
                            text: "TLS 1.3 + RSA-2048"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.5, 0.5, 0.6, 1
                            adaptive_size: True

            MDCard:
                size_hint_y: None
                height: "64dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                padding: [16, 0]
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "eye-off-outline"
                                size_hint: None, None
                                size: "24dp", "24dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.2, 0.4, 0.9, 1
                                font_size: "22sp"
                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_x: 1
                        spacing: 2
                        MDLabel:
                            text: app.lang_proto_anon
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                        MDLabel:
                            text: app.lang_proto_anon_sub
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.5, 0.5, 0.6, 1
                            adaptive_size: True

            MDCard:
                size_hint_y: None
                height: "64dp"
                radius: [16]
                md_bg_color: 0.95, 0.95, 0.98, 1
                elevation: 2
                padding: [16, 0]
                MDBoxLayout:
                    spacing: 14
                    MDBoxLayout:
                        size_hint: None, None
                        size: "38dp", "38dp"
                        pos_hint: {"center_y": .5}
                        AnchorLayout:
                            MDIcon:
                                icon: "access-point"
                                size_hint: None, None
                                size: "24dp", "24dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 0.2, 0.4, 0.9, 1
                                font_size: "22sp"
                    MDBoxLayout:
                        orientation: "vertical"
                        size_hint_x: 1
                        spacing: 2
                        MDLabel:
                            text: app.lang_proto_port
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            adaptive_size: True
                        MDLabel:
                            text: "UDP 1194 / TCP 443"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.5, 0.5, 0.6, 1
                            adaptive_size: True

        Widget:

# ─── SUBSCRIPTION SCREEN ────────────────────────────────────────────
<SubscriptionScreen>:
    name: 'subscription'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        padding: [20, 14, 20, 20]
        spacing: 0

        # Top bar
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"

            MDBoxLayout:
                size_hint_x: None
                width: "48dp"
                AnchorLayout:
                    anchor_x: "center"
                    anchor_y: "center"
                    MDIconButton:
                        icon: "arrow-left"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        on_release: root.manager.current = 'settings'

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "center"
                MDLabel:
                    text: app.lang_subscription
                    bold: True
                    halign: "center"
                    font_style: "H6"
                    theme_text_color: "Custom"
                    text_color: 0.1, 0.1, 0.1, 1
                    adaptive_size: True

            Widget:
                size_hint_x: None
                width: "48dp"

        Widget:
            size_hint_y: None
            height: "20dp"

        # Корона
        AnchorLayout:
            size_hint_y: None
            height: "100dp"
            MDCard:
                size_hint: None, None
                size: "80dp", "80dp"
                radius: [24]
                md_bg_color: 0.98, 0.93, 0.72, 1
                elevation: 5
                AnchorLayout:
                    MDIcon:
                        icon: "crown"
                        size_hint: None, None
                        size: "44dp", "44dp"
                        pos_hint: {"center_x": .5, "center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.85, 0.58, 0.05, 1
                        font_size: "40sp"

        Widget:
            size_hint_y: None
            height: "8dp"

        MDLabel:
            text: "NEVPN Premium"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: "38dp"

        MDLabel:
            text: app.lang_sub_desc
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.55, 0.55, 0.65, 1
            size_hint_y: None
            height: "22dp"

        Widget:
            size_hint_y: None
            height: "18dp"

        # Карточка тарифа
        MDCard:
            size_hint_y: None
            height: "100dp"
            radius: [20]
            md_bg_color: 0.95, 0.95, 0.98, 1
            elevation: 3
            padding: [20, 0]
            MDBoxLayout:
                spacing: 12
                AnchorLayout:
                    size_hint: None, None
                    size: "48dp", "48dp"
                    pos_hint: {"center_y": .5}
                    MDCard:
                        size_hint: None, None
                        size: "48dp", "48dp"
                        radius: [14]
                        md_bg_color: 0.2, 0.4, 0.9, 1
                        elevation: 2
                        AnchorLayout:
                            MDIcon:
                                icon: "calendar-month"
                                size_hint: None, None
                                size: "26dp", "26dp"
                                pos_hint: {"center_x": .5, "center_y": .5}
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                                font_size: "24sp"
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_x: 1
                    spacing: 4
                    MDLabel:
                        text: app.lang_sub_plan
                        bold: True
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        adaptive_size: True
                    MDLabel:
                        text: app.lang_sub_features
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.6, 1
                        adaptive_size: True
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint: None, None
                    size: "70dp", "60dp"
                    pos_hint: {"center_y": .5}
                    spacing: 0
                    MDLabel:
                        text: "500 ₽"
                        bold: True
                        font_style: "H6"
                        theme_text_color: "Custom"
                        text_color: 0.2, 0.4, 0.9, 1
                        halign: "right"
                        size_hint_y: None
                        height: "36dp"
                    MDLabel:
                        text: app.lang_sub_period
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.6, 0.6, 0.7, 1
                        halign: "right"
                        size_hint_y: None
                        height: "18dp"

        Widget:
            size_hint_y: None
            height: "14dp"

        # Что включено
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "8dp"
            size_hint_y: None
            height: self.minimum_height

            MDCard:
                size_hint_y: None
                height: "44dp"
                radius: [12]
                md_bg_color: 0.93, 0.98, 0.93, 1
                elevation: 0
                padding: [14, 0]
                MDBoxLayout:
                    spacing: 10
                    MDIcon:
                        icon: "check-circle"
                        size_hint: None, None
                        size: "20dp", "20dp"
                        pos_hint: {"center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.72, 0.35, 1
                        font_size: "18sp"
                    MDLabel:
                        text: app.lang_sub_f1
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"

            MDCard:
                size_hint_y: None
                height: "44dp"
                radius: [12]
                md_bg_color: 0.93, 0.98, 0.93, 1
                elevation: 0
                padding: [14, 0]
                MDBoxLayout:
                    spacing: 10
                    MDIcon:
                        icon: "check-circle"
                        size_hint: None, None
                        size: "20dp", "20dp"
                        pos_hint: {"center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.72, 0.35, 1
                        font_size: "18sp"
                    MDLabel:
                        text: app.lang_sub_f2
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"

            MDCard:
                size_hint_y: None
                height: "44dp"
                radius: [12]
                md_bg_color: 0.93, 0.98, 0.93, 1
                elevation: 0
                padding: [14, 0]
                MDBoxLayout:
                    spacing: 10
                    MDIcon:
                        icon: "check-circle"
                        size_hint: None, None
                        size: "20dp", "20dp"
                        pos_hint: {"center_y": .5}
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.72, 0.35, 1
                        font_size: "18sp"
                    MDLabel:
                        text: app.lang_sub_f3
                        theme_text_color: "Custom"
                        text_color: 0.1, 0.1, 0.1, 1
                        valign: "middle"

        Widget:
            size_hint_y: None
            height: "18dp"

        # Кнопка купить
        MDCard:
            size_hint_y: None
            height: "52dp"
            radius: [26]
            md_bg_color: 0.2, 0.4, 0.9, 1
            elevation: 5
            ripple_behavior: True
            on_release: print("[Sub] Купить нажато")
            AnchorLayout:
                MDLabel:
                    text: app.lang_buy
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    font_style: "Button"
                    adaptive_size: True
                    pos_hint: {"center_x": .5, "center_y": .5}

        Widget:
'''



class ServerListItem(MDCard):
    server_name = StringProperty()
    flag_source = StringProperty()


class MainScreen(Screen):
    selected_server = StringProperty("Выберите сервер")
    is_connected = BooleanProperty(False)
    traffic_up = StringProperty("0 B")
    traffic_down = StringProperty("0 B")

    # Хранит dict текущего сервера VPN Gate
    _current_server = None
    # Путь к временному .ovpn файлу
    _ovpn_path = None

    # ── Кнопка питания ───────────────────────────────────────────────

    def on_power_press(self, instance):
        anim = (Animation(size=(dp(90), dp(90)), duration=0.08) +
                Animation(size=(dp(100), dp(100)), duration=0.08))
        anim.start(instance)

        if self.is_connected:
            self._disconnect_vpn()
        else:
            if self._current_server:
                self.connect_vpngate(self._current_server)
            else:
                # Нет сервера — переход на экран выбора
                self.manager.current = 'servers'

    # ── Подключение через ics-openvpn ────────────────────────────────

    def connect_vpngate(self, srv):
        """
        Декодирует .ovpn конфиг из base64, сохраняет в файл,
        запускает ics-openvpn (de.blinkt.openvpn) через Intent.
        Работает на Android; на десктопе — имитация.
        """
        self._current_server = srv
        self._set_status_connecting()

        try:
            ovpn_data = base64.b64decode(srv["ovpn_b64"]).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[VPN] base64 decode error: {e}")
            self._set_status_error()
            return

        # Сохраняем .ovpn во временный файл
        ovpn_path = self._save_ovpn(ovpn_data, srv.get("country", "XX"))
        if not ovpn_path:
            self._set_status_error()
            return
        self._ovpn_path = ovpn_path

        if platform == "android":
            self._launch_openvpn_android(ovpn_path, srv["name"])
        else:
            # Десктоп: имитация для разработки
            print(f"[VPN-DEV] Would launch OpenVPN with: {ovpn_path}")
            Clock.schedule_once(lambda dt: self._on_connected(), 1.5)

    def _save_ovpn(self, ovpn_data, country_code):
        """Сохраняет .ovpn в кэш-директорию приложения."""
        try:
            if platform == "android":
                from jnius import autoclass
                ctx = autoclass("org.kivy.android.PythonActivity").mActivity
                cache_dir = ctx.getCacheDir().getAbsolutePath()
            else:
                cache_dir = os.path.dirname(os.path.abspath(__file__))

            os.makedirs(cache_dir, exist_ok=True)
            path = os.path.join(cache_dir, f"nevpn_{country_code}.ovpn")
            with open(path, "w", encoding="utf-8") as f:
                f.write(ovpn_data)
            print(f"[VPN] .ovpn сохранён: {path}")
            return path
        except Exception as e:
            print(f"[VPN] Ошибка сохранения .ovpn: {e}")
            return None

    def _launch_openvpn_android(self, ovpn_path, server_name):
        """
        Запускает ics-openvpn (пакет de.blinkt.openvpn) через Android Intent.
        ics-openvpn должен быть установлен отдельно.
        Скачать: https://f-droid.org/packages/de.blinkt.openvpn/
        """
        try:
            from jnius import autoclass, cast
            from android import activity  # type: ignore

            Intent          = autoclass("android.content.Intent")
            Uri             = autoclass("android.net.Uri")
            PythonActivity  = autoclass("org.kivy.android.PythonActivity")
            File            = autoclass("java.io.File")
            FileProvider    = autoclass("androidx.core.content.FileProvider")

            ctx = PythonActivity.mActivity

            # Формируем URI через FileProvider (Android 7+)
            java_file = File(ovpn_path)
            authority = ctx.getPackageName() + ".fileprovider"

            try:
                uri = FileProvider.getUriForFile(ctx, authority, java_file)
            except Exception:
                # Фолбэк: прямой file:// URI (работает до Android 7)
                uri = Uri.fromFile(java_file)

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "application/x-openvpn-profile")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

            # Если ics-openvpn установлен — откроется он напрямую
            intent.setPackage("de.blinkt.openvpn")

            ctx.startActivity(intent)
            print(f"[VPN] Intent отправлен: {server_name}")

            # Помечаем как "подключается" — ics-openvpn сам управляет соединением
            Clock.schedule_once(lambda dt: self._on_connecting_intent_sent(), 0.5)

        except Exception as e:
            write_crash_log(type(e), e, e.__traceback__)
            print(f"[VPN] Intent error: {e}")
            # ics-openvpn не установлен — предложим установить
            Clock.schedule_once(lambda dt: self._prompt_install_openvpn(), 0)

    def _prompt_install_openvpn(self):
        """Открывает F-Droid / Play страницу ics-openvpn для установки."""
        self._set_status_error()
        try:
            from jnius import autoclass
            Intent         = autoclass("android.content.Intent")
            Uri            = autoclass("android.net.Uri")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ctx = PythonActivity.mActivity

            # Пробуем F-Droid, потом Play Store
            for url in [
                "market://details?id=de.blinkt.openvpn",
                "https://f-droid.org/packages/de.blinkt.openvpn/",
            ]:
                try:
                    i = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    ctx.startActivity(i)
                    break
                except Exception:
                    continue
        except Exception as e:
            print(f"[VPN] Не удалось открыть магазин: {e}")

        # Обновляем UI
        try:
            self.ids.status_label.text = "Установите\nics-openvpn"
            self.ids.status_label.text_color = (0.9, 0.4, 0.1, 1)
        except Exception:
            pass

    def _disconnect_vpn(self):
        """Отключение: посылает STOP Intent в ics-openvpn."""
        if platform == "android":
            try:
                from jnius import autoclass
                Intent         = autoclass("android.content.Intent")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                ctx = PythonActivity.mActivity

                intent = Intent("de.blinkt.openvpn.DISCONNECT_VPN")
                intent.setPackage("de.blinkt.openvpn")
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                ctx.startActivity(intent)
            except Exception as e:
                print(f"[VPN] Disconnect error: {e}")

        self.is_connected = False
        self.traffic_up = "0 B"
        self.traffic_down = "0 B"
        self.update_ui()

    # ── Состояния UI ─────────────────────────────────────────────────

    def _on_connected(self):
        self.is_connected = True
        self.traffic_up = "↑ Активно"
        self.traffic_down = "↓ Активно"
        self.update_ui()

    def _on_connecting_intent_sent(self):
        """После отправки Intent — показываем промежуточный статус."""
        try:
            self.ids.status_label.text = "Запуск VPN..."
            self.ids.status_label.text_color = (0.8, 0.6, 0.1, 1)
            self.ids.power_icon.icon = "loading"
            self.ids.power_button.md_bg_color = (0.8, 0.6, 0.1, 1)
        except Exception:
            pass

    def _set_status_connecting(self):
        try:
            self.ids.status_label.text = "Подключение..."
            self.ids.status_label.text_color = (0.75, 0.55, 0.1, 1)
            self.ids.power_icon.icon = "power-plug-outline"
            self.ids.power_button.md_bg_color = (0.75, 0.55, 0.1, 1)
        except Exception:
            pass

    def _set_status_error(self):
        try:
            self.ids.status_label.text = "Ошибка"
            self.ids.status_label.text_color = (0.85, 0.2, 0.2, 1)
            self.ids.power_icon.icon = "power-plug-off-outline"
            self.ids.power_button.md_bg_color = (0.85, 0.2, 0.2, 1)
        except Exception:
            pass

    def on_is_connected(self, instance, value):
        self.update_ui()

    def update_ui(self):
        try:
            status_label = self.ids.status_label
            power_button = self.ids.power_button
            power_icon = self.ids.power_icon

            if self.is_connected:
                status_label.text = "Подключено"
                status_label.text_color = (0.2, 0.7, 0.35, 1)
                power_icon.icon = "power-plug"
                power_button.md_bg_color = (0.15, 0.72, 0.35, 1)
            else:
                status_label.text = "Connect"
                status_label.text_color = (0.55, 0.55, 0.68, 1)
                power_icon.icon = "power-plug-outline"
                power_button.md_bg_color = (0.2, 0.4, 0.9, 1)
        except Exception:
            pass

    def on_kv_post(self, base_widget):
        try:
            self.update_ui()
        except Exception:
            pass


class SettingsScreen(Screen):
    _autoconnect_on = False
    _killswitch_on = False

    def toggle_autoconnect(self, instance):
        from kivy.animation import Animation
        self._autoconnect_on = not self._autoconnect_on
        if self._autoconnect_on:
            anim = Animation(md_bg_color=(0.78, 0.96, 0.82, 1), duration=0.25)
            self.ids.autoconnect_icon.text_color = (0.15, 0.65, 0.3, 1)
            self.ids.autoconnect_label.text_color = (0.05, 0.45, 0.15, 1)
            self.ids.autoconnect_check.icon = "check-circle"
            self.ids.autoconnect_check.text_color = (0.15, 0.72, 0.35, 1)
        else:
            anim = Animation(md_bg_color=(0.95, 0.95, 0.98, 1), duration=0.25)
            self.ids.autoconnect_icon.text_color = (0.25, 0.45, 0.9, 1)
            self.ids.autoconnect_label.text_color = (0.1, 0.1, 0.1, 1)
            self.ids.autoconnect_check.icon = "check-circle-outline"
            self.ids.autoconnect_check.text_color = (0.75, 0.75, 0.75, 1)
        anim.start(instance)

    def toggle_killswitch(self, instance):
        from kivy.animation import Animation
        self._killswitch_on = not self._killswitch_on
        if self._killswitch_on:
            anim = Animation(md_bg_color=(0.78, 0.96, 0.82, 1), duration=0.25)
            self.ids.killswitch_icon.text_color = (0.15, 0.65, 0.3, 1)
            self.ids.killswitch_label.text_color = (0.05, 0.45, 0.15, 1)
            self.ids.killswitch_check.icon = "check-circle"
            self.ids.killswitch_check.text_color = (0.15, 0.72, 0.35, 1)
        else:
            anim = Animation(md_bg_color=(0.95, 0.95, 0.98, 1), duration=0.25)
            self.ids.killswitch_icon.text_color = (0.9, 0.3, 0.3, 1)
            self.ids.killswitch_label.text_color = (0.1, 0.1, 0.1, 1)
            self.ids.killswitch_check.icon = "check-circle-outline"
            self.ids.killswitch_check.text_color = (0.75, 0.75, 0.75, 1)
        anim.start(instance)


class ServersScreen(Screen):
    """
    Загружает серверы с VPN Gate API, показывает список.
    При выборе — сохраняет .ovpn в кэш и запускает ics-openvpn через Intent.
    """

    # ── VPN Gate API ──────────────────────────────────────────────────
    VPNGATE_URL = "https://www.vpngate.net/api/iphone/"

    # Флаги стран: ISO-код → emoji
    FLAGS = {
        "JP": "🇯🇵", "US": "🇺🇸", "KR": "🇰🇷", "DE": "🇩🇪",
        "NL": "🇳🇱", "FR": "🇫🇷", "GB": "🇬🇧", "CA": "🇨🇦",
        "SG": "🇸🇬", "RU": "🇷🇺", "IN": "🇮🇳", "AU": "🇦🇺",
        "TH": "🇹🇭", "UA": "🇺🇦", "BR": "🇧🇷", "SE": "🇸🇪",
        "CH": "🇨🇭", "IT": "🇮🇹", "PL": "🇵🇱", "CZ": "🇨🇿",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._servers = []       # список dict: {name, ip, speed, score, ovpn_b64, country}
        self._loading = False

    def on_enter(self):
        """Вызывается каждый раз при переходе на экран."""
        if not self._servers:
            self.refresh_servers()

    def refresh_servers(self):
        if self._loading:
            return
        self._loading = True
        self._set_status("⏳  Загрузка серверов VPN Gate...", (0.3, 0.3, 0.5, 1))
        # Очистить список
        Clock.schedule_once(lambda dt: self._clear_list(), 0)
        # Загрузить в фоне
        t = threading.Thread(target=self._fetch_servers, daemon=True)
        t.start()

    def _fetch_servers(self):
        """Фоновый поток: скачивает CSV от VPN Gate."""
        try:
            req = urllib.request.Request(
                self.VPNGATE_URL,
                headers={"User-Agent": "NEVPN/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            msg = f"❌  Ошибка сети: {e}\nПроверьте интернет"
            Clock.schedule_once(
                lambda dt, m=msg: self._set_status(m, (0.8, 0.2, 0.2, 1)), 0
            )
            self._loading = False
            return

        try:
            servers = self._parse_vpngate_csv(raw)
        except Exception as e:
            msg = f"❌  Ошибка парсинга: {e}"
            Clock.schedule_once(
                lambda dt, m=msg: self._set_status(m, (0.8, 0.2, 0.2, 1)), 0
            )
            self._loading = False
            return

        self._servers = servers
        self._loading = False
        Clock.schedule_once(lambda dt: self._populate_list(servers), 0)

    def _parse_vpngate_csv(self, raw_text):
        """Парсит CSV VPN Gate. Возвращает топ-20 серверов по скорости."""
        # VPN Gate CSV начинается с '*vpn_servers\r\n', заканчивается '*\r\n'
        lines = raw_text.splitlines()
        # убрать первую и последнюю строки-маркеры
        csv_lines = [l for l in lines if not l.startswith("*")]
        csv_text = "\n".join(csv_lines)

        reader = csv.DictReader(io.StringIO(csv_text))
        servers = []
        for row in reader:
            try:
                ovpn_b64 = row.get("OpenVPN_ConfigData_Base64", "").strip()
                if not ovpn_b64:
                    continue
                country_code = row.get("CountryShort", "??").strip().upper()
                country_long = row.get("CountryLong", "Unknown").strip()
                ip = row.get("IP", "").strip()
                speed_str = row.get("Speed", "0").strip()
                score_str = row.get("Score", "0").strip()
                speed = int(speed_str) if speed_str.isdigit() else 0
                score = int(score_str) if score_str.isdigit() else 0
                sessions_str = row.get("NumVpnSessions", "0").strip()
                sessions = int(sessions_str) if sessions_str.isdigit() else 0

                flag = self.FLAGS.get(country_code, "🌐")
                speed_mbps = speed / 1_000_000
                display_name = f"{flag} {country_long}"

                servers.append({
                    "name": display_name,
                    "country": country_code,
                    "ip": ip,
                    "speed": speed,
                    "speed_mbps": speed_mbps,
                    "score": score,
                    "sessions": sessions,
                    "ovpn_b64": ovpn_b64,
                })
            except Exception:
                continue

        # Сортировка: по скорости убывает, берём топ-25
        servers.sort(key=lambda s: s["speed"], reverse=True)
        return servers[:25]

    def _clear_list(self):
        try:
            self.ids.servers_list.clear_widgets()
        except Exception:
            pass

    def _set_status(self, text, color=(0.3, 0.3, 0.5, 1)):
        try:
            self.ids.loading_label.text = text
            self.ids.loading_label.text_color = color
            icon = "check-circle-outline" if "✅" in text else (
                "alert-circle-outline" if "❌" in text else "cloud-download-outline"
            )
            self.ids.loading_icon.icon = icon
        except Exception:
            pass

    def _populate_list(self, servers):
        """Добавляет карточки серверов в ScrollView."""
        if not servers:
            self._set_status("❌  Серверы не найдены", (0.8, 0.2, 0.2, 1))
            return

        self._set_status(
            f"✅  Найдено серверов: {len(servers)}",
            (0.15, 0.65, 0.3, 1)
        )
        self._clear_list()

        from kivymd.uix.card import MDCard
        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.label import MDLabel
        from kivy.metrics import dp as _dp

        box = self.ids.servers_list

        for srv in servers:
            speed_text = f"{srv['speed_mbps']:.1f} Mbps"
            sessions_text = f"{srv['sessions']} польз."

            # Создаём карточку через Builder для совместимости со стилями
            from kivy.lang import Builder as _B
            card_kv = f"""
MDCard:
    size_hint_y: None
    height: "68dp"
    radius: [16]
    md_bg_color: 0.95, 0.95, 0.98, 1
    elevation: 2
    ripple_behavior: True
    padding: [14, 0]
    MDBoxLayout:
        spacing: 10
        MDLabel:
            text: "{srv['name']}"
            size_hint_x: 1
            theme_text_color: "Custom"
            text_color: 0.1, 0.1, 0.1, 1
            valign: "middle"
            bold: True
            font_size: "14sp"
        MDBoxLayout:
            orientation: "vertical"
            size_hint: None, None
            size: "80dp", "48dp"
            pos_hint: {{"center_y": .5}}
            spacing: 2
            MDLabel:
                text: "{speed_text}"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.2, 0.55, 0.85, 1
                halign: "right"
                adaptive_size: True
            MDLabel:
                text: "{sessions_text}"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.55, 0.55, 0.65, 1
                halign: "right"
                adaptive_size: True
        MDBoxLayout:
            size_hint: None, None
            size: "28dp", "28dp"
            pos_hint: {{"center_y": .5}}
            AnchorLayout:
                MDIcon:
                    icon: "chevron-right"
                    size_hint: None, None
                    size: "20dp", "20dp"
                    pos_hint: {{"center_x": .5, "center_y": .5}}
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_size: "18sp"
"""
            try:
                card = _B.load_string(card_kv)
                # Биндим нажатие — передаём srv как замыкание
                def make_handler(s):
                    def handler(instance):
                        self.select_server(s)
                    return handler
                card.bind(on_release=make_handler(srv))
                box.add_widget(card)
            except Exception as e:
                print(f"[Servers] Card error: {e}")

    # ── Выбор и подключение ──────────────────────────────────────────

    def select_server(self, srv):
        """Сохраняет .ovpn и запускает ics-openvpn."""
        if isinstance(srv, str):
            # Старый вызов из KV (на всякий случай)
            main_screen = self.manager.get_screen('main')
            main_screen.selected_server = srv
            self.manager.current = 'main'
            return

        main_screen = self.manager.get_screen('main')
        main_screen.selected_server = srv["name"]
        main_screen._current_server = srv

        print(f"[Servers] Выбран: {srv['name']} / {srv['ip']}")
        self.manager.current = 'main'

        # Запускаем подключение
        Clock.schedule_once(lambda dt: main_screen.connect_vpngate(srv), 0.3)



class ProtocolScreen(Screen):
    pass


class SubscriptionScreen(Screen):
    pass


class AboutScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


# ══ Словари переводов ══════════════════════════════════════════
TRANSLATIONS = {
    'ru': {
        'connect':         'Connect',
        'connected':       'Подключено',
        'settings':        'Настройки',
        'lang_settings':   'Язык',
        'lang_code':       'RU',
        'protocol':        'Протокол',
        'protocol_sub':    'Открытый стандарт · надёжный и быстрый',
        'subscription':    'Подписка',
        'sub_desc':        'Разблокируй все возможности NEVPN',
        'sub_plan':        'Premium · 1 месяц',
        'sub_features':    'Все серверы · Kill Switch · без рекламы',
        'sub_period':      '/ месяц',
        'sub_f1':          'Доступ ко всем серверам',
        'sub_f2':          'Kill Switch — защита при обрыве',
        'sub_f3':          'Без рекламы и ограничений',
        'buy':             'Купить — 500 ₽',
        'proto_enc':       'Шифрование',
        'proto_auth':      'Аутентификация',
        'proto_anon':      'Анонимность',
        'proto_anon_sub':  'Нет логов · нет утечек DNS',
        'proto_port':      'Порты',
    },
    'en': {
        'connect':         'Connect',
        'connected':       'Connected',
        'settings':        'Settings',
        'lang_settings':   'Language',
        'lang_code':       'EN',
        'protocol':        'Protocol',
        'protocol_sub':    'Open standard · reliable and fast',
        'subscription':    'Subscription',
        'sub_desc':        'Unlock all NEVPN features',
        'sub_plan':        'Premium · 1 month',
        'sub_features':    'All servers · Kill Switch · no ads',
        'sub_period':      '/ month',
        'sub_f1':          'Access to all servers',
        'sub_f2':          'Kill Switch — protection on disconnect',
        'sub_f3':          'No ads or limits',
        'buy':             'Buy — 500 ₽',
        'proto_enc':       'Encryption',
        'proto_auth':      'Authentication',
        'proto_anon':      'Anonymity',
        'proto_anon_sub':  'No logs · no DNS leaks',
        'proto_port':      'Ports',
    },
}


class NEVPNApp(MDApp):
    lang_code        = StringProperty('RU')
    lang_connect     = StringProperty('Connect')
    lang_connected   = StringProperty('Подключено')
    lang_settings    = StringProperty('Язык')
    lang_protocol    = StringProperty('Протокол')
    lang_protocol_sub = StringProperty('Открытый стандарт · надёжный и быстрый')
    lang_subscription = StringProperty('Подписка')
    lang_sub_desc    = StringProperty('Разблокируй все возможности NEVPN')
    lang_sub_plan    = StringProperty('Premium · 1 месяц')
    lang_sub_features = StringProperty('Все серверы · Kill Switch · без рекламы')
    lang_sub_period  = StringProperty('/ месяц')
    lang_sub_f1      = StringProperty('Доступ ко всем серверам')
    lang_sub_f2      = StringProperty('Kill Switch — защита при обрыве')
    lang_sub_f3      = StringProperty('Без рекламы и ограничений')
    lang_buy         = StringProperty('Купить — 500 ₽')
    lang_proto_enc   = StringProperty('Шифрование')
    lang_proto_auth  = StringProperty('Аутентификация')
    lang_proto_anon  = StringProperty('Анонимность')
    lang_proto_anon_sub = StringProperty('Нет логов · нет утечек DNS')
    lang_proto_port  = StringProperty('Порты')

    _current_lang = 'ru'

    def toggle_language(self):
        self._current_lang = 'en' if self._current_lang == 'ru' else 'ru'
        t = TRANSLATIONS[self._current_lang]
        self.lang_code         = t['lang_code']
        self.lang_settings     = t['lang_settings']
        self.lang_connect      = t['connect']
        self.lang_connected    = t['connected']
        self.lang_protocol     = t['protocol']
        self.lang_protocol_sub = t['protocol_sub']
        self.lang_subscription = t['subscription']
        self.lang_sub_desc     = t['sub_desc']
        self.lang_sub_plan     = t['sub_plan']
        self.lang_sub_features = t['sub_features']
        self.lang_sub_period   = t['sub_period']
        self.lang_sub_f1       = t['sub_f1']
        self.lang_sub_f2       = t['sub_f2']
        self.lang_sub_f3       = t['sub_f3']
        self.lang_buy          = t['buy']
        self.lang_proto_enc    = t['proto_enc']
        self.lang_proto_auth   = t['proto_auth']
        self.lang_proto_anon   = t['proto_anon']
        self.lang_proto_anon_sub = t['proto_anon_sub']
        self.lang_proto_port   = t['proto_port']
        # обновить статус на главном экране
        try:
            ms = self.root.get_screen('main')
            if ms.is_connected:
                ms.ids.status_label.text = t['connected']
            else:
                ms.ids.status_label.text = t['connect']
        except Exception:
            pass

    def build(self):
        try:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Blue"
            return Builder.load_string(KV)
        except Exception as e:
            Logger.exception("NEVPN: build() failed")
            write_crash_log(type(e), e, e.__traceback__)
            raise


if __name__ == '__main__':
    try:
        NEVPNApp().run()
    except Exception as e:
        write_crash_log(type(e), e, e.__traceback__)
        raise
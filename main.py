# -*- coding: utf-8 -*-
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation

from kivy.utils import platform
try:
    if platform != 'android':
        Window.size = (360, 640)
except Exception:
    pass

import sys
import traceback
import os
import datetime
import threading

def get_crash_log_path():
    """Определяем путь для crash_log.txt — работает и на Android, и на ПК"""
    from kivy.utils import platform
    if platform == 'android':
        try:
            from android.storage import primary_external_storage_path
            ext = primary_external_storage_path()
            if ext:
                return os.path.join(ext, 'NEVPN_crash_log.txt')
        except Exception:
            pass
        # Запасной путь — внутреннее хранилище приложения
        return '/sdcard/NEVPN_crash_log.txt'
    else:
        # На ПК — рядом с main.py
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash_log.txt')

def write_crash_log(exc_type, exc_value, exc_tb):
    """Записывает crash в txt файл"""
    try:
        log_path = get_crash_log_path()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "=" * 60,
            f"CRASH — {now}",
            "=" * 60,
            f"Platform: {sys.platform}",
            f"Python: {sys.version}",
            "",
            "--- Traceback ---",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
            "",
        ]
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("\n".join(lines))
        Logger.error(f"NEVPN: Crash log saved to: {log_path}")
    except Exception as write_err:
        Logger.error(f"NEVPN: Could not write crash log: {write_err}")

def handle_exception(exc_type, exc_value, exc_tb):
    # Игнорируем KeyboardInterrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    try:
        Logger.error("NEVPN: " + "".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        write_crash_log(exc_type, exc_value, exc_tb)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = handle_exception

# Ловим крэши и в потоках (Thread)
_original_threading_excepthook = threading.excepthook
def thread_exception_handler(args):
    if args.exc_type and not issubclass(args.exc_type, SystemExit):
        handle_exception(args.exc_type, args.exc_value, args.exc_traceback)
    _original_threading_excepthook(args)
threading.excepthook = thread_exception_handler



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
                        text: "Connect"
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

        # ── Settings list ──
        ScrollView:
            MDList:
                spacing: "10dp"
                padding: [0, 0, 0, 10]

                # Language
                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
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
                                    size: "30dp", "30dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                                    theme_text_color: "Custom"
                                    text_color: 0.25, 0.45, 0.9, 1
                                    font_size: "22sp"
                        MDLabel:
                            text: "Язык"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            valign: "middle"
                            size_hint_x: 1
                        MDBoxLayout:
                            size_hint: None, None
                            size: "38dp", "38dp"
                            pos_hint: {"center_y": .5}
                            AnchorLayout:
                                MDLabel:
                                    text: "RU"
                                    font_style: "Caption"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 0.5, 0.5, 0.6, 1
                                    halign: "center"
                                    adaptive_size: True
                                    pos_hint: {"center_x": .5, "center_y": .5}

                # Protocol
                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
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
                            text: "Протокол"
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

                # Auto connect
                MDCard:
                    size_hint_y: None
                    height: "60dp"
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
                                    icon: "wifi-check"
                                    size_hint: None, None
                                    size: "26dp", "26dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                                    theme_text_color: "Custom"
                                    text_color: 0.25, 0.45, 0.9, 1
                                    font_size: "22sp"
                        MDLabel:
                            text: "Автоподключение"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            valign: "middle"
                            size_hint_x: 1
                        MDSwitch:
                            size_hint: None, None
                            size: "50dp", "30dp"
                            pos_hint: {"center_y": .5}

                # Kill switch
                MDCard:
                    size_hint_y: None
                    height: "60dp"
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
                                    icon: "close-network-outline"
                                    size_hint: None, None
                                    size: "26dp", "26dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                                    theme_text_color: "Custom"
                                    text_color: 0.9, 0.3, 0.3, 1
                                    font_size: "22sp"
                        MDLabel:
                            text: "Kill Switch"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            valign: "middle"
                            size_hint_x: 1
                        MDSwitch:
                            size_hint: None, None
                            size: "50dp", "30dp"
                            pos_hint: {"center_y": .5}

                # Subscription
                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
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
                            text: "Подписка"
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

                # About
                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
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
            height: "20dp"

        NeomorphButton:
            ripple_behavior: False
            MDLabel:
                text: "Доступные серверы"
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

        ScrollView:
            MDList:
                id: server_list
                spacing: "10dp"
                padding: [0, 0, 0, 10]

                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
                    on_release: app.root.get_screen('servers').select_server("Нидерланды")
                    MDBoxLayout:
                        spacing: 14
                        MDBoxLayout:
                            size_hint: None, None
                            size: "38dp", "38dp"
                            pos_hint: {"center_y": .5}
                            AnchorLayout:
                                Image:
                                    source: "images/flag_nl.png"
                                    size_hint: None, None
                                    size: "30dp", "22dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                        MDLabel:
                            text: "Нидерланды"
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

                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
                    on_release: app.root.get_screen('servers').select_server("США")
                    MDBoxLayout:
                        spacing: 14
                        MDBoxLayout:
                            size_hint: None, None
                            size: "38dp", "38dp"
                            pos_hint: {"center_y": .5}
                            AnchorLayout:
                                Image:
                                    source: "images/flag_us.png"
                                    size_hint: None, None
                                    size: "30dp", "22dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                        MDLabel:
                            text: "США"
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

                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
                    on_release: app.root.get_screen('servers').select_server("Япония")
                    MDBoxLayout:
                        spacing: 14
                        MDBoxLayout:
                            size_hint: None, None
                            size: "38dp", "38dp"
                            pos_hint: {"center_y": .5}
                            AnchorLayout:
                                Image:
                                    source: "images/flag_jp.png"
                                    size_hint: None, None
                                    size: "30dp", "22dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                        MDLabel:
                            text: "Япония"
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

                MDCard:
                    size_hint_y: None
                    height: "60dp"
                    radius: [16]
                    md_bg_color: 0.95, 0.95, 0.98, 1
                    elevation: 2
                    ripple_behavior: True
                    padding: [16, 0]
                    on_release: app.root.get_screen('servers').select_server("Германия")
                    MDBoxLayout:
                        spacing: 14
                        MDBoxLayout:
                            size_hint: None, None
                            size: "38dp", "38dp"
                            pos_hint: {"center_y": .5}
                            AnchorLayout:
                                Image:
                                    source: "images/flag_de.png"
                                    size_hint: None, None
                                    size: "30dp", "22dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                        MDLabel:
                            text: "Германия"
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
'''


class ServerListItem(MDCard):
    server_name = StringProperty()
    flag_source = StringProperty()


class MainScreen(Screen):
    selected_server = StringProperty("Нидерланды")
    is_connected = BooleanProperty(False)
    traffic_up = StringProperty("0 B")
    traffic_down = StringProperty("0 B")

    def on_power_press(self, instance):
        anim = (Animation(size=(dp(90), dp(90)), duration=0.08) +
                Animation(size=(dp(100), dp(100)), duration=0.08))
        anim.start(instance)
        self.is_connected = not self.is_connected
        if self.is_connected:
            print(f"[VPN] Подключено к серверу: {self.selected_server}")
            self.traffic_up = "1.2 KB"
            self.traffic_down = "3.4 KB"
        else:
            print("[VPN] Отключено")
            self.traffic_up = "0 B"
            self.traffic_down = "0 B"
        self.update_ui()

    def on_is_connected(self, instance, value):
        self.update_ui()

    def update_ui(self):
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

    def on_kv_post(self, base_widget):
        try:
            self.update_ui()
        except Exception:
            pass


class SettingsScreen(Screen):
    pass


class ServersScreen(Screen):
    def select_server(self, server_name):
        main_screen = self.manager.get_screen('main')
        main_screen.selected_server = server_name
        print(f"[Servers] Выбран сервер: {server_name}")
        self.manager.current = 'main'


class AboutScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class NEVPNApp(MDApp):
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
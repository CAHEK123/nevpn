# -*- coding: utf-8 -*-
import sys
import types
import os

# ╔══════════════════════════════════════════════════════════════╗
# ║  ПАТЧ v2: полная заглушка для KivyMD 1.2.0 на Android       ║
# ║  Подменяем material_resources ДО любого импорта KivyMD.     ║
# ║  Также фиксим theming.py который тоже лезет в Window.       ║
# ╚══════════════════════════════════════════════════════════════╝

# --- material_resources заглушка ---
_mat_mod = types.ModuleType('kivymd.material_resources')
_mat_mod.__all__ = ('DEVICE_TYPE',)
_mat_mod.DEVICE_TYPE = 'mobile'
sys.modules['kivymd.material_resources'] = _mat_mod

# --- Заглушка Window до инициализации ---
# Нужна чтобы theming.py не упал при импорте
import kivy  # noqa: E402
kivy.require('2.0.0')

# Устанавливаем платформу ДО Window
os.environ.setdefault('KIVY_NO_ENV_CONFIG', '1')

from kivy.utils import platform  # noqa: E402

# На Android Window может быть None при импорте —
# подменяем временно чтобы KivyMD не падал
if platform == 'android':
    import kivy.core.window as _kw_module
    if _kw_module.Window is None:
        class _FakeWindow:
            width = 1080
            height = 1920
            size = (1080, 1920)
            dpi = 420
        _kw_module.Window = _FakeWindow()

from kivy.core.window import Window  # noqa: E402

if platform != 'android':
    Window.size = (360, 640)

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, ImageLeftWidget
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation

# Логгер крашей на телефоне
import traceback as _tb

def _crash_hook(exc_type, exc_value, exc_tb):
    try:
        with open('/sdcard/nevpn_crash.txt', 'a') as f:
            import datetime
            f.write(f'\n{"="*60}\n')
            f.write(f'CRASH  {datetime.datetime.now()}\n')
            f.write(f'Platform: {platform}\n')
            f.write(f'Python: {sys.version}\n\n')
            f.write('--- Traceback ---\n')
            _tb.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _crash_hook

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

WindowManager:
    MainScreen:
    SettingsScreen:
    ServersScreen:
    AboutScreen:

# ─── MAIN ───────────────────────────────────────────────
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

        # Топбар
        MDBoxLayout:
            size_hint_y: None
            height: "48dp"
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
                        Image:
                            source: 'image/logo_icon.png'
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

        # Выбор сервера
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

        # Кнопка подключения
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
                            on_touch_down:
                                if self.collide_point(*args[1].pos): root.on_power_press(self)
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

        # Трафик
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
                            text: root.traffic_down
                            adaptive_size: True
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.2, 0.2, 0.2, 1
                            pos_hint: {"center_y": .5}
        Widget:

# ─── SETTINGS ───────────────────────────────────────────
<SettingsScreen>:
    name: 'settings'
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
                            source: 'image/logo_icon.png'
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

        ScrollView:
            MDList:
                spacing: "10dp"
                padding: [0, 0, 0, 10]

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
                                    icon: "shield-lock-outline"
                                    size_hint: None, None
                                    size: "26dp", "26dp"
                                    pos_hint: {"center_x": .5, "center_y": .5}
                                    theme_text_color: "Custom"
                                    text_color: 0.25, 0.45, 0.9, 1
                                    font_size: "22sp"
                        MDLabel:
                            text: "Протокол: WireGuard"
                            theme_text_color: "Custom"
                            text_color: 0.1, 0.1, 0.1, 1
                            valign: "middle"
                            size_hint_x: 1

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

# ─── SERVERS ────────────────────────────────────────────
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
                            source: 'image/logo_icon.png'
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
                                    source: "image/flag_nl.png"
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
                                    source: "image/flag_us.png"
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
                                    source: "image/flag_jp.png"
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
                                    source: "image/flag_de.png"
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

# ─── ABOUT ──────────────────────────────────────────────
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
                        source: 'image/logo_icon.png'
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
                text: "Неоморфный VPN-клиент.\\nРазработано с использованием KivyMD.\\nAndroid 16 / Samsung A35 5G"
                halign: "center"
                valign: "middle"
                theme_text_color: "Custom"
                text_color: 0.4, 0.4, 0.4, 1

        Widget:
'''


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
            self.traffic_up = "1.2 KB"
            self.traffic_down = "3.4 KB"
        else:
            self.traffic_up = "0 B"
            self.traffic_down = "0 B"
        self.update_ui()

    def on_is_connected(self, instance, value):
        self.update_ui()

    def update_ui(self):
        if self.is_connected:
            self.ids.status_label.text = "Подключено"
            self.ids.status_label.text_color = (0.2, 0.7, 0.35, 1)
            self.ids.power_icon.icon = "power-plug"
            self.ids.power_button.md_bg_color = (0.15, 0.72, 0.35, 1)
        else:
            self.ids.status_label.text = "Connect"
            self.ids.status_label.text_color = (0.55, 0.55, 0.68, 1)
            self.ids.power_icon.icon = "power-plug-outline"
            self.ids.power_button.md_bg_color = (0.2, 0.4, 0.9, 1)

    def on_kv_post(self, base_widget):
        self.update_ui()


class SettingsScreen(Screen):
    pass


class ServersScreen(Screen):
    def select_server(self, server_name):
        self.manager.get_screen('main').selected_server = server_name
        self.manager.current = 'main'


class AboutScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class NEVPNApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)


if __name__ == '__main__':
    NEVPNApp().run()
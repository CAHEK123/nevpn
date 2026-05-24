[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# ── ИСПРАВЛЕНИЕ КРАША ──────────────────────────────────────
# Ошибка: AttributeError: 'NoneType' object has no attribute 'width'
# в kivymd/material_resources.py
# Причина: kivy==master несовместим с kivymd==1.2.0
# Решение: используем kivy==2.3.0 — стабильная версия под kivymd 1.2.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = images/logo_icon.png

# Samsung A35 5G — Android 16 (API 36), One UI 8.0
android.permissions = INTERNET

android.minapi = 26
android.api = 36
android.ndk = 25b
android.sdk = 36
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

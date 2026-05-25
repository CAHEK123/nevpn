[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# python3==3.11.9 фиксирует hostpython3 — в 3.14 нет модуля cgi
# p4a.branch = develop — ветка где cgi-проблема уже исправлена
# kivy==2.2.1 + kivymd==1.1.1 — рабочая пара под NDK r25b
requirements = python3==3.11.9,kivy==2.2.1,kivymd==1.1.1,pillow,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = images/logo_icon.png

android.permissions = INTERNET

android.minapi = 26
android.api = 33
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

# Используем develop-ветку p4a — там исправлена совместимость с Python 3.14
p4a.branch = develop

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

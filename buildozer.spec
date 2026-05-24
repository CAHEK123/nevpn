[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = image/*.png,image/*.jpg,image/*.jpeg

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = image/logo_icon.png

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.minapi = 26
android.api = 34
android.ndk = 25b
android.sdk = 34
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

# Используем стабильный тег p4a с Python 3.11 + NDK 25b
# 2024.09.02 — последний официальный релиз, проверен с Kivy 2.3.0
p4a.branch = 2024.09.02

[buildozer]
log_level = 2
warn_on_root = 1

[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg,image/*.png,image/*.jpg

version = 1.0.0

# kivy master + kivymd master — совместимы между собой
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = image/logo_icon.png

android.permissions = INTERNET
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

# Логкэт для отладки
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

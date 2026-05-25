[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# Рабочая комбинация без cgi-проблем:
# - p4a.branch = master (hostpython3 = 3.11.x, там cgi ещё есть)
# - python3 без версии (согласуется с hostpython3 = 3.11.x)
# - kivy==2.3.0 + kivymd==1.2.0 совместимы с NDK r23b + Python 3.11
hostpython3 = python3==3.11.9
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,pillow,pyjnius

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

# master ветка p4a — hostpython3 = 3.11.x, cgi ещё присутствует
p4a.branch = master

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

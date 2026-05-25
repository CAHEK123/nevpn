[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg

version = 1.0.0

# НЕ указываем p4a.version / p4a.branch — p4a устанавливается вручную в yml
# через pip install git+https://...@<коммит> чтобы зафиксировать Python 3.11

requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.2.0,pillow,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = images/logo_icon.png

android.permissions = INTERNET

android.minapi = 26
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.enable_androidx = True

android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1

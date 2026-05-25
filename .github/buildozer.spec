[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = image/*.png,image/*.jpg,image/*.jpeg

version = 1.0.0

# ВАЖНО: kivy и kivymd — БЕЗ ==версии.
# p4a использует встроенные рецепты, а не pip.
# Если указать ==версию — p4a пытается поставить через pip и падает.
requirements = python3,kivy,kivymd,pillow

orientation = portrait
fullscreen = 0

icon.filename = image/logo_icon.png

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.minapi = 26
android.api = 34
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

# Тег p4a нужно указывать С префиксом v — именно так называются теги в git.
# v2024.01.21 содержит рецепты: kivy 2.3.0, kivymd 1.2.0, python 3.11
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1

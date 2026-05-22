[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = image/*.png,image/*.jpg

version = 1.0.0

requirements = python3,kivy==master,kivymd==1.2.0,pillow

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

# Переменная окружения для фикса бага с Window
android.add_java_options = -DKIVY_NO_ENV_CONFIG=1

[buildozer]
log_level = 2
warn_on_root = 1

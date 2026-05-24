[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = image/*.png,image/*.jpg

version = 1.0.0

# kivy==master работает с NDK r25b (проверено первой успешной сборкой)
# kivymd==1.2.0 — патч в main.py фиксит краш с Window
requirements = python3,kivy==master,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = image/logo_icon.png

android.permissions = INTERNET
android.minapi = 26
android.api = 34
android.ndk = 25b
android.sdk = 34
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1

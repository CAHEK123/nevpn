[app]

title = NEVPN
package.name = nevpn
package.domain = org.nevpn
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
source.include_patterns = images/*.png,images/*.jpg,image/*.png,image/*.jpg

version = 1.0.0

# kivy master исправляет баг с NDK r25b (glVertexAttribPointer)
requirements = python3,kivy==master,kivymd==1.2.0,pillow

orientation = portrait
fullscreen = 0

# Иконка — используем ту папку что есть в репо
icon.filename = image/logo_icon.png

android.permissions = INTERNET
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# Только arm64 — быстрее собирается, покрывает 95% устройств
android.archs = arm64-v8a

android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 1
